from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict
from collections import defaultdict
from app.models.order import Order, OrderItem, OrderStatus
from app.models.food_item import FoodItem, FoodItemIngredient
from app.models.raw_material import RawMaterial
from app.schemas.order import OrderCreate, InventoryCheckResult
from app.services.food_item_service import FoodItemService


class OrderService:
    @staticmethod
    def check_inventory_availability(db: Session, order_data: OrderCreate) -> InventoryCheckResult:
        """
        Check if all items in the order can be fulfilled with current inventory.
        This is the CRITICAL inventory validation logic.
        """
        # Collect all required raw materials across all order items
        total_required_materials = defaultdict(float)
        total_price = 0.0
        
        # Calculate total requirements for each raw material
        for item in order_data.items:
            food_item = db.query(FoodItem).options(
                joinedload(FoodItem.ingredients).joinedload(FoodItemIngredient.raw_material)
            ).filter(FoodItem.id == item.food_item_id).first()
            
            if not food_item:
                return InventoryCheckResult(
                    can_fulfill=False,
                    missing_ingredients=[{"error": f"Food item {item.food_item_id} not found"}]
                )
            
            if not food_item.is_available:
                return InventoryCheckResult(
                    can_fulfill=False,
                    missing_ingredients=[{"error": f"Food item '{food_item.name}' is not available"}]
                )
            
            # Add to total price
            total_price += food_item.price * item.quantity
            
            # Calculate required raw materials for this food item
            for ingredient in food_item.ingredients:
                total_required = ingredient.quantity_required_per_unit * item.quantity
                total_required_materials[ingredient.raw_material_id] += total_required

        # Check availability for each required raw material
        missing_ingredients = []
        for raw_material_id, required_quantity in total_required_materials.items():
            raw_material = db.query(RawMaterial).filter(RawMaterial.id == raw_material_id).first()
            
            if not raw_material:
                missing_ingredients.append({
                    "raw_material_id": raw_material_id,
                    "error": "Raw material not found"
                })
                continue
            
            if raw_material.quantity_available < required_quantity:
                missing_ingredients.append({
                    "raw_material_id": raw_material_id,
                    "raw_material_name": raw_material.name,
                    "required": required_quantity,
                    "available": raw_material.quantity_available,
                    "unit": raw_material.unit,
                    "shortage": required_quantity - raw_material.quantity_available
                })

        return InventoryCheckResult(
            can_fulfill=len(missing_ingredients) == 0,
            missing_ingredients=missing_ingredients,
            total_price=total_price
        )

    @staticmethod
    def create_order(db: Session, order_data: OrderCreate) -> Order:
        """
        Create order with ATOMIC inventory deduction.
        This is the MOST CRITICAL function - handles inventory deduction with transactions.
        """
        try:
            # Start transaction
            db.begin()
            
            # Step 1: Check inventory availability
            inventory_check = OrderService.check_inventory_availability(db, order_data)
            if not inventory_check.can_fulfill:
                db.rollback()
                raise ValueError(f"Cannot fulfill order: {inventory_check.missing_ingredients}")

            # Step 2: Create order
            db_order = Order(
                total_price=inventory_check.total_price,
                status=OrderStatus.PLACED
            )
            db.add(db_order)
            db.flush()  # Get order ID

            # Step 3: Create order items and calculate total required materials
            total_required_materials = defaultdict(float)
            
            for item_data in order_data.items:
                food_item = db.query(FoodItem).options(
                    joinedload(FoodItem.ingredients).joinedload(FoodItemIngredient.raw_material)
                ).filter(FoodItem.id == item_data.food_item_id).first()

                # Create order item
                order_item = OrderItem(
                    order_id=db_order.id,
                    food_item_id=item_data.food_item_id,
                    quantity=item_data.quantity,
                    unit_price=food_item.price,
                    subtotal=food_item.price * item_data.quantity
                )
                db.add(order_item)

                # Calculate required materials for this order item
                for ingredient in food_item.ingredients:
                    total_required = ingredient.quantity_required_per_unit * item_data.quantity
                    total_required_materials[ingredient.raw_material_id] += total_required

            # Step 4: ATOMIC INVENTORY DEDUCTION
            # Deduct all required raw materials in a single transaction
            for raw_material_id, required_quantity in total_required_materials.items():
                raw_material = db.query(RawMaterial).filter(
                    RawMaterial.id == raw_material_id
                ).with_for_update().first()  # Lock row for update
                
                if raw_material.quantity_available < required_quantity:
                    # This should not happen due to pre-check, but safety measure
                    db.rollback()
                    raise ValueError(
                        f"Insufficient {raw_material.name}: "
                        f"required {required_quantity}, available {raw_material.quantity_available}"
                    )
                
                # Deduct inventory
                raw_material.quantity_available = round(raw_material.quantity_available - required_quantity, 2)

            # Step 5: Commit transaction
            db.commit()
            
            # Reload the order with all relationships
            db.refresh(db_order)
            return OrderService.get_order(db, db_order.id)

        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"Database error during order creation: {str(e)}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error creating order: {str(e)}")

    @staticmethod
    def get_order(db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID with all related data"""
        return db.query(Order).options(
            joinedload(Order.order_items).joinedload(OrderItem.food_item)
        ).filter(Order.id == order_id).first()

    @staticmethod
    def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders with pagination"""
        return db.query(Order).options(
            joinedload(Order.order_items).joinedload(OrderItem.food_item)
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def cancel_order(db: Session, order_id: int) -> Optional[Order]:
        """Cancel order (does not restore inventory - business decision)"""
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return None
        
        if db_order.status != OrderStatus.PLACED:
            raise ValueError(f"Cannot cancel order with status {db_order.status}")
        
        db_order.status = OrderStatus.CANCELLED
        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def complete_order(db: Session, order_id: int) -> Optional[Order]:
        """Mark order as completed"""
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return None
        
        if db_order.status != OrderStatus.PLACED:
            raise ValueError(f"Cannot complete order with status {db_order.status}")
        
        db_order.status = OrderStatus.COMPLETED
        db.commit()
        db.refresh(db_order)
        return db_order