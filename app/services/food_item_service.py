from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.models.food_item import FoodItem, FoodItemIngredient
from app.models.raw_material import RawMaterial
from app.schemas.food_item import FoodItemCreate


class FoodItemService:
    @staticmethod
    def create_food_item(db: Session, food_item: FoodItemCreate) -> FoodItem:
        """Create a new food item with ingredients"""
        # Create food item
        db_food_item = FoodItem(
            name=food_item.name,
            price=food_item.price,
            is_available=food_item.is_available
        )
        db.add(db_food_item)
        db.flush()  # Get the ID without committing

        # Add ingredients
        for ingredient in food_item.ingredients:
            # Verify raw material exists
            raw_material = db.query(RawMaterial).filter(
                RawMaterial.id == ingredient.raw_material_id
            ).first()
            if not raw_material:
                raise ValueError(f"Raw material with ID {ingredient.raw_material_id} not found")

            db_ingredient = FoodItemIngredient(
                food_item_id=db_food_item.id,
                raw_material_id=ingredient.raw_material_id,
                quantity_required_per_unit=ingredient.quantity_required_per_unit
            )
            db.add(db_ingredient)

        db.commit()
        
        # Reload with relationships
        db.refresh(db_food_item)
        return FoodItemService.get_food_item(db, db_food_item.id)

    @staticmethod
    def get_food_item(db: Session, food_item_id: int) -> Optional[FoodItem]:
        """Get food item by ID with ingredients"""
        return db.query(FoodItem).options(
            joinedload(FoodItem.ingredients).joinedload(FoodItemIngredient.raw_material)
        ).filter(FoodItem.id == food_item_id).first()

    @staticmethod
    def get_food_items(db: Session, skip: int = 0, limit: int = 100) -> List[FoodItem]:
        """Get all food items with ingredients"""
        return db.query(FoodItem).options(
            joinedload(FoodItem.ingredients).joinedload(FoodItemIngredient.raw_material)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_available_food_items(db: Session) -> List[FoodItem]:
        """Get only available food items"""
        return db.query(FoodItem).options(
            joinedload(FoodItem.ingredients).joinedload(FoodItemIngredient.raw_material)
        ).filter(FoodItem.is_available == True).all()

    @staticmethod
    def update_food_item(db: Session, food_item_id: int, food_item_data: FoodItemCreate) -> Optional[FoodItem]:
        """Update food item and its ingredients"""
        # Get existing food item
        db_food_item = db.query(FoodItem).filter(FoodItem.id == food_item_id).first()
        if not db_food_item:
            return None

        # Update basic info
        db_food_item.name = food_item_data.name
        db_food_item.price = food_item_data.price
        db_food_item.is_available = food_item_data.is_available

        # Delete existing ingredients
        db.query(FoodItemIngredient).filter(FoodItemIngredient.food_item_id == food_item_id).delete()

        # Add new ingredients
        for ingredient_data in food_item_data.ingredients:
            # Validate raw material exists
            raw_material = db.query(RawMaterial).filter(RawMaterial.id == ingredient_data.raw_material_id).first()
            if not raw_material:
                raise ValueError(f"Raw material with ID {ingredient_data.raw_material_id} not found")

            ingredient = FoodItemIngredient(
                food_item_id=db_food_item.id,
                raw_material_id=ingredient_data.raw_material_id,
                quantity_required_per_unit=ingredient_data.quantity_required_per_unit
            )
            db.add(ingredient)

        db.commit()
        
        # Reload with relationships
        return FoodItemService.get_food_item(db, db_food_item.id)

    @staticmethod
    def update_food_item_availability(db: Session, food_item_id: int, is_available: bool) -> Optional[FoodItem]:
        """Update food item availability"""
        db_food_item = db.query(FoodItem).filter(FoodItem.id == food_item_id).first()
        if not db_food_item:
            return None
        
        db_food_item.is_available = is_available
        db.commit()
        db.refresh(db_food_item)
        return db_food_item

    @staticmethod
    def update_food_item_availability_with_inventory(
        db: Session, 
        food_item_id: int, 
        is_available: bool, 
        delete_ingredients: bool = False
    ) -> Optional[dict]:
        """Update food item availability with optional ingredient deletion from inventory"""
        # Get the food item with ingredients
        food_item = FoodItemService.get_food_item(db, food_item_id)
        if not food_item:
            return None
        
        # Track deleted ingredients for response
        deleted_ingredients = []
        
        # If marking as unavailable and delete_ingredients is True, remove ingredients from inventory
        if not is_available and delete_ingredients:
            for ingredient in food_item.ingredients:
                raw_material = ingredient.raw_material
                if raw_material.quantity_available >= ingredient.quantity_required_per_unit:
                    # Reduce inventory by the required amount per unit
                    old_quantity = raw_material.quantity_available
                    raw_material.quantity_available -= ingredient.quantity_required_per_unit
                    
                    deleted_ingredients.append({
                        "raw_material_name": raw_material.name,
                        "quantity_removed": ingredient.quantity_required_per_unit,
                        "old_quantity": old_quantity,
                        "new_quantity": raw_material.quantity_available,
                        "unit": raw_material.unit
                    })
                else:
                    # Not enough inventory to remove
                    deleted_ingredients.append({
                        "raw_material_name": raw_material.name,
                        "quantity_removed": 0,
                        "old_quantity": raw_material.quantity_available,
                        "new_quantity": raw_material.quantity_available,
                        "unit": raw_material.unit,
                        "error": f"Insufficient inventory (available: {raw_material.quantity_available}, required: {ingredient.quantity_required_per_unit})"
                    })
        
        # Update food item availability
        food_item.is_available = is_available
        db.commit()
        db.refresh(food_item)
        
        response = {
            "message": "Food item availability updated",
            "is_available": food_item.is_available,
            "ingredients_deleted": delete_ingredients and not is_available,
            "deleted_ingredients": deleted_ingredients if deleted_ingredients else None
        }
        
        return response

    @staticmethod
    def delete_food_item(db: Session, food_item_id: int) -> bool:
        """Delete food item and its ingredients"""
        try:
            db_food_item = db.query(FoodItem).filter(FoodItem.id == food_item_id).first()
            if not db_food_item:
                return False
            
            # First delete all ingredients (foreign key references)
            db.query(FoodItemIngredient).filter(
                FoodItemIngredient.food_item_id == food_item_id
            ).delete()
            
            # Then delete the food item
            db.delete(db_food_item)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error deleting food item: {e}")
            return False

    @staticmethod
    def check_food_item_availability(db: Session, food_item_id: int, quantity: int) -> dict:
        """Check if food item can be prepared with current inventory"""
        food_item = FoodItemService.get_food_item(db, food_item_id)
        if not food_item:
            return {"available": False, "reason": "Food item not found"}
        
        if not food_item.is_available:
            return {"available": False, "reason": "Food item is not available"}

        missing_ingredients = []
        for ingredient in food_item.ingredients:
            required_quantity = ingredient.quantity_required_per_unit * quantity
            if ingredient.raw_material.quantity_available < required_quantity:
                missing_ingredients.append({
                    "raw_material": ingredient.raw_material.name,
                    "required": required_quantity,
                    "available": ingredient.raw_material.quantity_available,
                    "unit": ingredient.raw_material.unit
                })

        if missing_ingredients:
            return {
                "available": False, 
                "reason": "Insufficient ingredients",
                "missing_ingredients": missing_ingredients
            }

        return {"available": True}