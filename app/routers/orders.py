from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, InventoryCheckResult

router = APIRouter(prefix="/api/orders", tags=["orders"])


def convert_order_to_response(order) -> dict:
    """Convert order model to response dict"""
    return {
        "id": order.id,
        "total_price": order.total_price,
        "status": order.status.value if hasattr(order.status, 'value') else order.status,
        "created_at": order.created_at,
        "order_items": [
            {
                "id": item.id,
                "food_item_id": item.food_item_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal,
                "food_item_name": item.food_item.name if item.food_item else f"Deleted Item (ID: {item.food_item_id})"
            }
            for item in order.order_items
        ]
    }


@router.post("/check-inventory")
def check_inventory_availability(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """Check if order can be fulfilled with current inventory"""
    result = OrderService.check_inventory_availability(db, order_data)
    return {
        "can_fulfill": result.can_fulfill,
        "missing_ingredients": result.missing_ingredients,
        "total_price": result.total_price
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    Create order with automatic inventory deduction.
    This is the CRITICAL endpoint that handles inventory deduction atomically.
    """
    try:
        result = OrderService.create_order(db, order_data)
        return convert_order_to_response(result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/")
def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all orders with pagination"""
    orders = OrderService.get_orders(db, skip=skip, limit=limit)
    return [convert_order_to_response(order) for order in orders]


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get order by ID"""
    order = OrderService.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return convert_order_to_response(order)


@router.patch("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Cancel order"""
    try:
        order = OrderService.cancel_order(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return {"message": "Order cancelled successfully", "status": order.status}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{order_id}/complete")
def complete_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Mark order as completed"""
    try:
        order = OrderService.complete_order(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return {"message": "Order completed successfully", "status": order.status}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )