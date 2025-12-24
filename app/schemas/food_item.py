from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class FoodItemIngredientCreate(BaseModel):
    raw_material_id: int
    quantity_required_per_unit: float = Field(..., gt=0)


class FoodItemIngredientResponse(BaseModel):
    id: int
    raw_material_id: int
    quantity_required_per_unit: float
    raw_material_name: str
    raw_material_unit: str

    class Config:
        from_attributes = True


class FoodItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    is_available: bool = True


class FoodItemCreate(FoodItemBase):
    ingredients: List[FoodItemIngredientCreate] = []


class FoodItemResponse(FoodItemBase):
    id: int
    created_at: Optional[datetime] = None
    ingredients: List[FoodItemIngredientResponse] = []

    class Config:
        from_attributes = True