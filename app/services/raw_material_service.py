from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.raw_material import RawMaterial
from app.schemas.raw_material import RawMaterialCreate, RawMaterialUpdate


class RawMaterialService:
    @staticmethod
    def create_raw_material(db: Session, raw_material: RawMaterialCreate) -> RawMaterial:
        """Create a new raw material"""
        db_raw_material = RawMaterial(**raw_material.dict())
        db.add(db_raw_material)
        db.commit()
        db.refresh(db_raw_material)
        return db_raw_material

    @staticmethod
    def get_raw_material(db: Session, raw_material_id: int) -> Optional[RawMaterial]:
        """Get raw material by ID"""
        return db.query(RawMaterial).filter(RawMaterial.id == raw_material_id).first()

    @staticmethod
    def get_raw_material_by_name(db: Session, name: str) -> Optional[RawMaterial]:
        """Get raw material by name"""
        return db.query(RawMaterial).filter(RawMaterial.name == name).first()

    @staticmethod
    def get_raw_materials(db: Session, skip: int = 0, limit: int = 100) -> List[RawMaterial]:
        """Get all raw materials with pagination"""
        return db.query(RawMaterial).offset(skip).limit(limit).all()

    @staticmethod
    def get_raw_materials_with_usage(db: Session, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all raw materials with usage information"""
        raw_materials = db.query(RawMaterial).offset(skip).limit(limit).all()
        
        result = []
        for material in raw_materials:
            food_items_using = RawMaterialService.get_food_items_using_raw_material(db, material.id)
            
            material_dict = {
                "id": material.id,
                "name": material.name,
                "unit": material.unit,
                "quantity_available": material.quantity_available,
                "minimum_threshold": material.minimum_threshold,
                "created_at": material.created_at,
                "is_low_stock": material.is_low_stock,
                "is_used_in_recipes": len(food_items_using) > 0,
                "food_items": food_items_using,
                "usage_count": len(food_items_using)
            }
            result.append(material_dict)
        
        return result

    @staticmethod
    def get_low_stock_materials(db: Session) -> List[RawMaterial]:
        """Get raw materials that are below minimum threshold"""
        return db.query(RawMaterial).filter(
            RawMaterial.quantity_available <= RawMaterial.minimum_threshold
        ).all()

    @staticmethod
    def update_raw_material(
        db: Session, 
        raw_material_id: int, 
        raw_material_update: RawMaterialUpdate
    ) -> Optional[RawMaterial]:
        """Update raw material"""
        db_raw_material = db.query(RawMaterial).filter(RawMaterial.id == raw_material_id).first()
        if not db_raw_material:
            return None
        
        update_data = raw_material_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_raw_material, field, value)
        
        db.commit()
        db.refresh(db_raw_material)
        return db_raw_material

    @staticmethod
    def update_stock(db: Session, raw_material_id: int, quantity_change: float) -> Optional[RawMaterial]:
        """Update stock quantity (can be positive or negative)"""
        db_raw_material = db.query(RawMaterial).filter(RawMaterial.id == raw_material_id).first()
        if not db_raw_material:
            return None
        
        new_quantity = db_raw_material.quantity_available + quantity_change
        if new_quantity < 0:
            raise ValueError(f"Insufficient stock. Available: {db_raw_material.quantity_available}, Required: {abs(quantity_change)}")
        
        # Round to 2 decimal places to avoid floating point precision issues
        db_raw_material.quantity_available = round(new_quantity, 2)
        db.commit()
        db.refresh(db_raw_material)
        return db_raw_material

    @staticmethod
    def get_food_items_using_raw_material(db: Session, raw_material_id: int) -> List[str]:
        """Get list of food item names that use this raw material"""
        from app.models.food_item import FoodItemIngredient, FoodItem
        
        food_items = db.query(FoodItem.name).join(
            FoodItemIngredient, FoodItem.id == FoodItemIngredient.food_item_id
        ).filter(
            FoodItemIngredient.raw_material_id == raw_material_id
        ).all()
        
        return [item.name for item in food_items]

    @staticmethod
    def delete_raw_material(db: Session, raw_material_id: int) -> bool:
        """Delete raw material"""
        from app.models.food_item import FoodItemIngredient
        
        db_raw_material = db.query(RawMaterial).filter(RawMaterial.id == raw_material_id).first()
        if not db_raw_material:
            return False
        
        # Check if raw material is used in any food items
        food_items_using = RawMaterialService.get_food_items_using_raw_material(db, raw_material_id)
        
        if food_items_using:
            food_items_list = ", ".join(food_items_using)
            raise ValueError(f"Cannot delete raw material '{db_raw_material.name}' because it is used in these food items: {food_items_list}. Please remove it from all recipes first.")
        
        db.delete(db_raw_material)
        db.commit()
        return True