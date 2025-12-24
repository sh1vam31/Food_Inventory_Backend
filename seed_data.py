"""
Seed script to populate the database with sample data for testing.
Run this after setting up the database to get started quickly.
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.raw_material import RawMaterial
from app.models.food_item import FoodItem, FoodItemIngredient
from app.database import Base

# Create tables
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    
    try:
        # Clear existing data (for development)
        db.query(FoodItemIngredient).delete()
        db.query(FoodItem).delete()
        db.query(RawMaterial).delete()
        db.commit()
        
        # Seed raw materials
        raw_materials = [
            RawMaterial(name="Flour", unit="kg", quantity_available=50.0, minimum_threshold=10.0),
            RawMaterial(name="Sugar", unit="kg", quantity_available=25.0, minimum_threshold=5.0),
            RawMaterial(name="Eggs", unit="piece", quantity_available=100.0, minimum_threshold=20.0),
            RawMaterial(name="Milk", unit="liter", quantity_available=30.0, minimum_threshold=5.0),
            RawMaterial(name="Butter", unit="kg", quantity_available=15.0, minimum_threshold=3.0),
            RawMaterial(name="Tomato", unit="kg", quantity_available=20.0, minimum_threshold=5.0),
            RawMaterial(name="Cheese", unit="kg", quantity_available=12.0, minimum_threshold=2.0),
            RawMaterial(name="Chicken", unit="kg", quantity_available=25.0, minimum_threshold=5.0),
            RawMaterial(name="Bread", unit="piece", quantity_available=50.0, minimum_threshold=10.0),
            RawMaterial(name="Lettuce", unit="kg", quantity_available=8.0, minimum_threshold=2.0),
        ]
        
        for material in raw_materials:
            db.add(material)
        db.commit()
        
        # Refresh to get IDs
        for material in raw_materials:
            db.refresh(material)
        
        # Create a mapping for easy reference
        materials_map = {material.name: material for material in raw_materials}
        
        # Seed food items with recipes
        food_items_data = [
            {
                "name": "Margherita Pizza",
                "price": 12.99,
                "ingredients": [
                    {"material": "Flour", "quantity": 0.3},  # 300g flour per pizza
                    {"material": "Tomato", "quantity": 0.2},  # 200g tomato
                    {"material": "Cheese", "quantity": 0.15}, # 150g cheese
                ]
            },
            {
                "name": "Chicken Sandwich",
                "price": 8.99,
                "ingredients": [
                    {"material": "Bread", "quantity": 2},     # 2 pieces of bread
                    {"material": "Chicken", "quantity": 0.15}, # 150g chicken
                    {"material": "Lettuce", "quantity": 0.05}, # 50g lettuce
                    {"material": "Cheese", "quantity": 0.05},  # 50g cheese
                ]
            },
            {
                "name": "Chocolate Cake",
                "price": 15.99,
                "ingredients": [
                    {"material": "Flour", "quantity": 0.4},   # 400g flour
                    {"material": "Sugar", "quantity": 0.3},   # 300g sugar
                    {"material": "Eggs", "quantity": 3},      # 3 eggs
                    {"material": "Milk", "quantity": 0.25},   # 250ml milk
                    {"material": "Butter", "quantity": 0.2},  # 200g butter
                ]
            },
            {
                "name": "Cheese Omelette",
                "price": 6.99,
                "ingredients": [
                    {"material": "Eggs", "quantity": 3},      # 3 eggs
                    {"material": "Cheese", "quantity": 0.08}, # 80g cheese
                    {"material": "Milk", "quantity": 0.05},   # 50ml milk
                    {"material": "Butter", "quantity": 0.02}, # 20g butter
                ]
            }
        ]
        
        for item_data in food_items_data:
            # Create food item
            food_item = FoodItem(
                name=item_data["name"],
                price=item_data["price"],
                is_available=True
            )
            db.add(food_item)
            db.flush()  # Get ID
            
            # Add ingredients
            for ingredient_data in item_data["ingredients"]:
                material = materials_map[ingredient_data["material"]]
                ingredient = FoodItemIngredient(
                    food_item_id=food_item.id,
                    raw_material_id=material.id,
                    quantity_required_per_unit=ingredient_data["quantity"]
                )
                db.add(ingredient)
        
        db.commit()
        print("✅ Database seeded successfully!")
        print("\n📊 Sample Data Created:")
        print(f"   • {len(raw_materials)} raw materials")
        print(f"   • {len(food_items_data)} food items with recipes")
        print("\n🚀 You can now:")
        print("   • View inventory at /api/raw-materials")
        print("   • See menu items at /api/food-items")
        print("   • Place orders at /api/orders")
        print("   • Check API docs at http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()