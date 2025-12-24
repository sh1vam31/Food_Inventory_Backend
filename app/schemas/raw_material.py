from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class RawMaterialBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    unit: str = Field(..., pattern="^(kg|gram|liter|piece)$")
    quantity_available: float = Field(..., ge=0)
    minimum_threshold: float = Field(..., ge=0)


class RawMaterialCreate(RawMaterialBase):
    pass


class RawMaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    unit: Optional[str] = Field(None, pattern="^(kg|gram|liter|piece)$")
    quantity_available: Optional[float] = Field(None, ge=0)
    minimum_threshold: Optional[float] = Field(None, ge=0)


class RawMaterialResponse(RawMaterialBase):
    id: int
    created_at: Optional[datetime] = None
    is_low_stock: bool

    class Config:
        from_attributes = True


class RawMaterialWithUsageResponse(RawMaterialResponse):
    is_used_in_recipes: bool
    food_items: List[str]
    usage_count: int