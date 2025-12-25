#!/usr/bin/env python3
"""
Script to create sample order maintainer users
Run this from the backend directory: python create_order_maintainers.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import UserRole
from app.services.user_service import UserService
from app.schemas.user import UserCreate

def create_order_maintainers():
    """Create sample order maintainer users"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("👥 Creating Order Maintainer Users...")
        print("=" * 50)
        
        # Sample order maintainer users
        order_maintainers = [
            {
                "username": "manager",
                "email": "manager@restaurant.com",
                "password": "manager123",
                "full_name": "Restaurant Manager",
                "role": UserRole.ORDER_MAINTAINER
            },
            {
                "username": "chef",
                "email": "chef@restaurant.com",
                "password": "chef123",
                "full_name": "Head Chef",
                "role": UserRole.ORDER_MAINTAINER
            },
            {
                "username": "staff",
                "email": "staff@restaurant.com",
                "password": "staff123",
                "full_name": "Kitchen Staff",
                "role": UserRole.ORDER_MAINTAINER
            }
        ]
        
        created_users = []
        
        for user_data in order_maintainers:
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
                print(f"   Role: Order Maintainer")
                print(f"   Password: {user_data['password']}")
                print()
                
            except Exception as e:
                print(f"❌ Error creating user '{user_data['username']}': {e}")
                print()
        
        print("🎉 Order Maintainer creation completed!")
        print(f"Created {len(created_users)} new users.")
        
        if created_users:
            print("\n📋 Order Maintainer Login Credentials:")
            print("=" * 50)
            for user_data in order_maintainers:
                if any(u.username == user_data["username"] for u in created_users):
                    print(f"Username: {user_data['username']}")
                    print(f"Password: {user_data['password']}")
                    print(f"Role: Order Maintainer")
                    print(f"Access: Dashboard, Menu (view), Orders")
                    print("-" * 30)
        
        print("\n🔒 What Order Maintainers CAN do:")
        print("• View and access Dashboard")
        print("• View Menu items")
        print("• Place and manage Orders")
        print("• View inventory (read-only)")
        print()
        print("❌ What Order Maintainers CANNOT do:")
        print("• Modify inventory (add/edit/delete raw materials)")
        print("• Create new users")
        print("• Access admin functions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_order_maintainers()