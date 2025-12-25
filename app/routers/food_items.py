from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.food_item_service import FoodItemService
from app.schemas.food_item import FoodItemCreate, FoodItemResponse
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/food-items", tags=["food-items"])


def convert_to_response(food_item) -> dict:
    """Convert food item model to response dict"""
    return {
        "id": food_item.id,
        "name": food_item.name,
        "price": food_item.price,
        "is_available": food_item.is_available,
        "created_at": food_item.created_at,
        "ingredients": [
            {
                "id": ingredient.id,
                "raw_material_id": ingredient.raw_material_id,
                "quantity_required_per_unit": ingredient.quantity_required_per_unit,
                "raw_material_name": ingredient.raw_material.name,
                "raw_material_unit": ingredient.raw_material.unit
            }
            for ingredient in food_item.ingredients
        ]
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_food_item(
    food_item: FoodItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Require authentication
):
    """Create a new food item with ingredients (recipe)"""
    try:
        result = FoodItemService.create_food_item(db, food_item)
        return convert_to_response(result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/")
def get_food_items(
    skip: int = 0,
    limit: int = 100,
    available_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all food items or only available ones"""
    if available_only:
        food_items = FoodItemService.get_available_food_items(db)
    else:
        food_items = FoodItemService.get_food_items(db, skip=skip, limit=limit)
    
    return [convert_to_response(item) for item in food_items]


@router.get("/{food_item_id}")
def get_food_item(
    food_item_id: int,
    db: Session = Depends(get_db)
):
    """Get food item by ID with ingredients"""
    food_item = FoodItemService.get_food_item(db, food_item_id)
    if not food_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food item not found"
        )
    return convert_to_response(food_item)


@router.put("/{food_item_id}")
def update_food_item(
    food_item_id: int,
    food_item: FoodItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Require authentication
):
    """Update food item and its ingredients"""
    try:
        updated_item = FoodItemService.update_food_item(db, food_item_id, food_item)
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item not found"
            )
        return convert_to_response(updated_item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{food_item_id}/availability")
def update_food_item_availability(
    food_item_id: int,
    is_available: bool,
    delete_ingredients: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Require authentication
):
    """Update food item availability with optional ingredient deletion"""
    try:
        result = FoodItemService.update_food_item_availability_with_inventory(
            db, food_item_id, is_available, delete_ingredients
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item not found"
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{food_item_id}/availability-check")
def check_food_item_availability(
    food_item_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    """Check if food item can be prepared with current inventory"""
    result = FoodItemService.check_food_item_availability(db, food_item_id, quantity)
    return result


@router.delete("/{food_item_id}")
def delete_food_item(
    food_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Require authentication
):
    """Delete food item (requires authentication)"""
    try:
        success = FoodItemService.delete_food_item(db, food_item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item not found"
            )
        return {"message": "Food item deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting food item: {str(e)}"
        )