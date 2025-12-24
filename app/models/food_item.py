from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ingredients = relationship("FoodItemIngredient", back_populates="food_item", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="food_item")

    def __repr__(self):
        return f"<FoodItem(name='{self.name}', price={self.price})>"


class FoodItemIngredient(Base):
    """Recipe table - maps food items to required raw materials"""
    __tablename__ = "food_item_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    raw_material_id = Column(Integer, ForeignKey("raw_materials.id"), nullable=False)
    quantity_required_per_unit = Column(Float, nullable=False)  # Amount needed per 1 food item

    # Relationships
    food_item = relationship("FoodItem", back_populates="ingredients")
    raw_material = relationship("RawMaterial", back_populates="food_item_ingredients")

    def __repr__(self):
        return f"<FoodItemIngredient(food_item_id={self.food_item_id}, raw_material_id={self.raw_material_id}, qty={self.quantity_required_per_unit})>"