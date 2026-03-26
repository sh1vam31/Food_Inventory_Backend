#!/usr/bin/env python3
"""
Script to create the default admin user
Run this from the backend directory: python create_admin.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models.user import User, UserRole
from app.services.user_service import UserService
from app.schemas.user import UserCreate

def create_admin_user():
    """Create the default admin user"""
    from app.database import Base
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🔐 Creating default admin user...")
        print("=" * 50)
        
        # Check if admin already exists
        existing_admin = UserService.get_user_by_username(db, "admin")
        if existing_admin:
            print("✅ Admin user already exists!")
            print(f"   Username: admin")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            print(f"   Active: {existing_admin.is_active}")
            return existing_admin
        
        # Create admin user
        admin_data = UserCreate(
            username="admin",
            email="admin@foodinventory.com",
            password="admin123",
            full_name="System Administrator",
            role=UserRole.ADMIN
        )
        
        admin_user = UserService.create_user(db, admin_data)
        
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@foodinventory.com")
        print(f"   Role: admin")
        print()
        print("🎉 You can now login with these credentials!")
        
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
            print(f"   User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
        else:
            print("❌ Admin login verification failed!")
            print("   The user exists but authentication failed.")
            
        return user is not None
        
    except Exception as e:
        print(f"❌ Error verifying admin login: {e}")
        return False
    finally:
        db.close()

def list_all_users():
    """List all users in the database"""
    db = next(get_db())
    
    try:
        print("\n👥 All users in database:")
        print("=" * 50)
        
        users = UserService.get_users(db)
        
        if not users:
            print("No users found in database.")
            return
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Full Name: {user.full_name}")
            print(f"Role: {user.role}")
            print(f"Active: {user.is_active}")
            print(f"Created: {user.created_at}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Food Inventory Admin Setup")
    print("=" * 50)
    
    # Create admin user
    admin_user = create_admin_user()
    
    if admin_user:
        # Verify login works
        verify_admin_login()
        
        # List all users
        list_all_users()
        
        print("\n🎯 Next steps:")
        print("1. Go to http://localhost:3000/login")
        print("2. Login with username: admin, password: admin123")
        print("3. Start using the system!")
    else:
        print("\n❌ Failed to create admin user. Please check the error messages above.")