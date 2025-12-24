from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.raw_material_service import RawMaterialService
from app.schemas.raw_material import RawMaterialCreate, RawMaterialUpdate, RawMaterialResponse, RawMaterialWithUsageResponse

router = APIRouter(prefix="/api/raw-materials", tags=["raw-materials"])


@router.post("/", response_model=RawMaterialResponse, status_code=status.HTTP_201_CREATED)
def create_raw_material(
    raw_material: RawMaterialCreate,
    db: Session = Depends(get_db)
):
    """Create a new raw material"""
    # Check if raw material with same name already exists
    existing = RawMaterialService.get_raw_material_by_name(db, raw_material.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Raw material with name '{raw_material.name}' already exists"
        )
    
    return RawMaterialService.create_raw_material(db, raw_material)


@router.get("/", response_model=List[RawMaterialResponse])
def get_raw_materials(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all raw materials"""
    return RawMaterialService.get_raw_materials(db, skip=skip, limit=limit)


@router.get("/with-usage", response_model=List[RawMaterialWithUsageResponse])
def get_raw_materials_with_usage(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all raw materials with usage information"""
    return RawMaterialService.get_raw_materials_with_usage(db, skip=skip, limit=limit)


@router.get("/low-stock", response_model=List[RawMaterialResponse])
def get_low_stock_materials(db: Session = Depends(get_db)):
    """Get raw materials that are below minimum threshold"""
    return RawMaterialService.get_low_stock_materials(db)


@router.get("/{raw_material_id}/usage", response_model=dict)
def get_raw_material_usage(
    raw_material_id: int,
    db: Session = Depends(get_db)
):
    """Get information about which food items use this raw material"""
    raw_material = RawMaterialService.get_raw_material(db, raw_material_id)
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw material not found"
        )
    
    food_items_using = RawMaterialService.get_food_items_using_raw_material(db, raw_material_id)
    
    return {
        "raw_material_name": raw_material.name,
        "is_used_in_recipes": len(food_items_using) > 0,
        "food_items": food_items_using,
        "usage_count": len(food_items_using)
    }


@router.get("/{raw_material_id}", response_model=RawMaterialResponse)
def get_raw_material(
    raw_material_id: int,
    db: Session = Depends(get_db)
):
    """Get raw material by ID"""
    raw_material = RawMaterialService.get_raw_material(db, raw_material_id)
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw material not found"
        )
    return raw_material


@router.put("/{raw_material_id}", response_model=RawMaterialResponse)
def update_raw_material(
    raw_material_id: int,
    raw_material_update: RawMaterialUpdate,
    db: Session = Depends(get_db)
):
    """Update raw material"""
    raw_material = RawMaterialService.update_raw_material(db, raw_material_id, raw_material_update)
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw material not found"
        )
    return raw_material


@router.patch("/{raw_material_id}/stock")
def update_stock(
    raw_material_id: int,
    quantity_change: float,
    db: Session = Depends(get_db)
):
    """Update stock quantity (positive to add, negative to subtract)"""
    try:
        raw_material = RawMaterialService.update_stock(db, raw_material_id, quantity_change)
        if not raw_material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raw material not found"
            )
        return {"message": "Stock updated successfully", "new_quantity": raw_material.quantity_available}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{raw_material_id}")
def delete_raw_material(
    raw_material_id: int,
    db: Session = Depends(get_db)
):
    """Delete raw material"""
    try:
        success = RawMaterialService.delete_raw_material(db, raw_material_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raw material not found"
            )
        return {"message": "Raw material deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )