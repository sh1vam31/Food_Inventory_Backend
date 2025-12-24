from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    food_item_id: int
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: int
    food_item_id: int
    quantity: int
    unit_price: float
    subtotal: float
    food_item_name: str

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderResponse(BaseModel):
    id: int
    total_price: float
    status: OrderStatus
    created_at: Optional[datetime] = None
    order_items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class InventoryCheckResult(BaseModel):
    """Response for inventory availability check"""
    can_fulfill: bool
    missing_ingredients: List[dict] = []
    total_price: float = 0.0