#!/usr/bin/env python3
"""
Script to create all database tables and admin user
Run this from the backend directory: python create_tables_and_admin.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import raw_material, food_item, order, user
from app.models.user import User, UserRole
from app.services.user_service import UserService
from app.schemas.user import UserCreate

def create_all_tables():
    """Create all database tables"""
    print("🗄️ Creating database tables...")
    
    try:
        # Create all tables
        raw_material.Base.metadata.create_all(bind=engine)
        food_item.Base.metadata.create_all(bind=engine)
        order.Base.metadata.create_all(bind=engine)
        user.Base.metadata.create_all(bind=engine)
        
        print("✅ All database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_admin_user():
    """Create the default admin user"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("\n🔐 Creating default admin user...")
        
        # Check if admin already exists
        existing_admin = UserService.get_user_by_username(db, "admin")
        if existing_admin:
            print("✅ Admin user already exists!")
            print(f"   Username: admin")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            return existing_admin
        
        # Create admin user
        admin_data = UserCreate(
            username="admin",
            email="admin@foodinventory.com",
            password="admin123",  # Shorter password
            full_name="System Administrator",
            role=UserRole.ADMIN
        )
        
        admin_user = UserService.create_user(db, admin_data)
        
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@foodinventory.com")
        print(f"   Role: admin")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def verify_admin_login():
    """Verify that admin can login"""
    db = next(get_db())
    
    try:
        print("\n🔍 Verifying admin login...")
        user = UserService.authenticate_user(db, "admin", "admin123")
        
        if user:
            print("✅ Admin login verification successful!")
            return True
        else:
            print("❌ Admin login verification failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying admin login: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Food Inventory Database Setup")
    print("=" * 50)
    
    # Create tables
    if create_all_tables():
        # Create admin user
        admin_user = create_admin_user()
        
        if admin_user:
            # Verify login works
            if verify_admin_login():
                print("\n🎉 Setup completed successfully!")
                print("\n🎯 Next steps:")
                print("1. Go to http://localhost:3000/login")
                print("2. Login with username: admin, password: admin123")
                print("3. Start using the system!")
            else:
                print("\n❌ Setup completed but login verification failed.")
        else:
            print("\n❌ Failed to create admin user.")
    else:
        print("\n❌ Failed to create database tables.")