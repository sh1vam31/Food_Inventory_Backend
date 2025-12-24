from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class RawMaterial(Base):
    __tablename__ = "raw_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    unit = Column(String, nullable=False)  # kg, gram, liter, piece
    quantity_available = Column(Float, nullable=False, default=0.0)
    minimum_threshold = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    food_item_ingredients = relationship("FoodItemIngredient", back_populates="raw_material")

    def __repr__(self):
        return f"<RawMaterial(name='{self.name}', quantity={self.quantity_available} {self.unit})>"

    @property
    def is_low_stock(self) -> bool:
        """Check if current stock is below minimum threshold"""
        return self.quantity_available <= self.minimum_threshold