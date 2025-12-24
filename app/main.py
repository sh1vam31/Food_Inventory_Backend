import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import raw_materials_router, food_items_router, orders_router
from app.database import engine
from app.models import raw_material, food_item, order
from app.core.config import settings

# Create database tables
raw_material.Base.metadata.create_all(bind=engine)
food_item.Base.metadata.create_all(bind=engine)
order.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Food Order & Inventory Management System",
    description="A complete system for managing food orders with automatic inventory deduction",
    version="1.0.0"
)

# CORS middleware - Configure for production
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://your-app-name.vercel.app",  # Replace with your actual Vercel domain
]

# In production, you might want to be more restrictive
if settings.is_production:
    # Add your production frontend URL here
    allowed_origins = [
        "https://your-app-name.vercel.app",  # Replace with your actual Vercel domain
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(raw_materials_router)
app.include_router(food_items_router)
app.include_router(orders_router)


@app.get("/")
def read_root():
    db_type = "PostgreSQL" if settings.is_postgresql else "SQLite"
    return {
        "message": "Food Order & Inventory Management System API",
        "version": "1.0.0",
        "environment": settings.environment,
        "database": db_type,
        "docs": "/docs",
        "features": [
            "Raw material management",
            "Food item & recipe builder",
            "Order processing with automatic inventory deduction",
            "Stock monitoring & alerts"
        ]
    }


@app.get("/health")
def health_check():
    db_type = "PostgreSQL" if settings.is_postgresql else "SQLite"
    return {
        "status": "healthy", 
        "message": "API is running",
        "database": db_type,
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)