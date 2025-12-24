#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to PostgreSQL
Run this after setting up PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.raw_material import RawMaterial
from app.models.food_item import FoodItem, FoodItemIngredient
from app.models.order import Order, OrderItem
from app.database import Base

def migrate_data(sqlite_url: str, postgresql_url: str):
    """Migrate data from SQLite to PostgreSQL"""
    
    print("🔄 Starting data migration from SQLite to PostgreSQL...")
    
    # Create engines
    sqlite_engine = create_engine(sqlite_url)
    postgresql_engine = create_engine(postgresql_url)
    
    # Create sessions
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgresql_engine)
    
    sqlite_session = SqliteSession()
    postgres_session = PostgresSession()
    
    try:
        # Create tables in PostgreSQL
        print("📋 Creating tables in PostgreSQL...")
        Base.metadata.create_all(bind=postgresql_engine)
        
        # Migrate Raw Materials
        print("📦 Migrating raw materials...")
        raw_materials = sqlite_session.query(RawMaterial).all()
        for material in raw_materials:
            new_material = RawMaterial(
                name=material.name,
                unit=material.unit,
                quantity_available=material.quantity_available,
                minimum_threshold=material.minimum_threshold,
                created_at=material.created_at
            )
            postgres_session.add(new_material)
        postgres_session.commit()
        print(f"✅ Migrated {len(raw_materials)} raw materials")
        
        # Migrate Food Items
        print("🍕 Migrating food items...")
        food_items = sqlite_session.query(FoodItem).all()
        for item in food_items:
            new_item = FoodItem(
                name=item.name,
                price=item.price,
                is_available=item.is_available,
                created_at=item.created_at
            )
            postgres_session.add(new_item)
        postgres_session.commit()
        print(f"✅ Migrated {len(food_items)} food items")
        
        # Migrate Food Item Ingredients
        print("🥘 Migrating recipes...")
        ingredients = sqlite_session.query(FoodItemIngredient).all()
        for ingredient in ingredients:
            new_ingredient = FoodItemIngredient(
                food_item_id=ingredient.food_item_id,
                raw_material_id=ingredient.raw_material_id,
                quantity_required_per_unit=ingredient.quantity_required_per_unit
            )
            postgres_session.add(new_ingredient)
        postgres_session.commit()
        print(f"✅ Migrated {len(ingredients)} recipe ingredients")
        
        # Migrate Orders
        print("📋 Migrating orders...")
        orders = sqlite_session.query(Order).all()
        for order in orders:
            new_order = Order(
                total_price=order.total_price,
                status=order.status,
                created_at=order.created_at
            )
            postgres_session.add(new_order)
        postgres_session.commit()
        print(f"✅ Migrated {len(orders)} orders")
        
        # Migrate Order Items
        print("🛒 Migrating order items...")
        order_items = sqlite_session.query(OrderItem).all()
        for item in order_items:
            new_item = OrderItem(
                order_id=item.order_id,
                food_item_id=item.food_item_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal
            )
            postgres_session.add(new_item)
        postgres_session.commit()
        print(f"✅ Migrated {len(order_items)} order items")
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        postgres_session.rollback()
        raise
    finally:
        sqlite_session.close()
        postgres_session.close()

def main():
    """Main migration function"""
    if len(sys.argv) != 2:
        print("Usage: python migrate_to_postgresql.py <postgresql_url>")
        print("Example: python migrate_to_postgresql.py postgresql://user:password@localhost/food_inventory")
        sys.exit(1)
    
    postgresql_url = sys.argv[1]
    sqlite_url = "sqlite:///./food_inventory.db"
    
    if not os.path.exists("food_inventory.db"):
        print("❌ SQLite database not found. Please ensure food_inventory.db exists.")
        sys.exit(1)
    
    print(f"📊 Source: {sqlite_url}")
    print(f"📊 Target: {postgresql_url}")
    
    confirm = input("Continue with migration? (y/N): ")
    if confirm.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    migrate_data(sqlite_url, postgresql_url)

if __name__ == "__main__":
    main()