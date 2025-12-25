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