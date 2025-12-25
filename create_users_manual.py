#!/usr/bin/env python3
"""
Manual script to create users directly in the database
Run this from the backend directory: python create_users_manual.py
"""

from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models.user import User, UserRole
from app.core.auth import get_password_hash
from app.services.user_service import UserService
from app.schemas.user import UserCreate

def create_sample_users():
    """Create sample users for testing"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🔐 Creating sample users...")
        print("=" * 50)
        
        # Sample users to create
        sample_users = [
            {
                "username": "restaurant_manager",
                "email": "manager@restaurant.com",
                "password": "manager123",
                "full_name": "Restaurant Manager",
                "role": UserRole.ORDER_MAINTAINER
            },
            {
                "username": "head_chef",
                "email": "chef@restaurant.com", 
                "password": "chef123",
                "full_name": "Head Chef",
                "role": UserRole.ORDER_MAINTAINER
            },
            {
                "username": "owner_admin",
                "email": "owner@restaurant.com",
                "password": "owner123",
                "full_name": "Restaurant Owner",
                "role": UserRole.ADMIN
            },
            {
                "username": "inventory_staff",
                "email": "inventory@restaurant.com",
                "password": "inventory123", 
                "full_name": "Inventory Staff",
                "role": UserRole.ORDER_MAINTAINER
            }
        ]
        
        created_users = []
        
        for user_data in sample_users:
            try:
                # Check if user already exists
                existing_user = UserService.get_user_by_username(db, user_data["username"])
                if existing_user:
                    print(f"⚠️  User '{user_data['username']}' already exists, skipping...")
                    continue
                
                # Create user
                user_create = UserCreate(**user_data)
                new_user = UserService.create_user(db, user_create)
                created_users.append(new_user)
                
                print(f"✅ Created user: {user_data['username']}")
                print(f"   Email: {user_data['email']}")
                print(f"   Role: {user_data['role']}")
                print(f"   Password: {user_data['password']}")
                print()
                
            except Exception as e:
                print(f"❌ Error creating user '{user_data['username']}': {e}")
                print()
        
        print("🎉 User creation completed!")
        print(f"Created {len(created_users)} new users.")
        
        if created_users:
            print("\n📋 Login Credentials Summary:")
            print("=" * 50)
            for user_data in sample_users:
                if any(u.username == user_data["username"] for u in created_users):
                    print(f"Username: {user_data['username']}")
                    print(f"Password: {user_data['password']}")
                    print(f"Role: {user_data['role']}")
                    print(f"Email: {user_data['email']}")
                    print("-" * 30)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_users()