#!/usr/bin/env python3
"""
Test database configuration
"""

import os
import sys

def test_config():
    """Test database configuration"""
    print("🔍 Testing Database Configuration")
    print("=" * 40)
    
    # Check environment variables
    database_url = os.getenv("DATABASE_URL")
    environment = os.getenv("ENVIRONMENT", "development")
    
    print(f"Environment: {environment}")
    print(f"DATABASE_URL set: {'Yes' if database_url else 'No'}")
    
    if database_url:
        print(f"DATABASE_URL starts with: {database_url[:30]}...")
        
        # Check URL format
        if database_url.startswith(("postgresql://", "postgres://")):
            print("✅ PostgreSQL URL detected")
        elif database_url.startswith("sqlite:"):
            print("✅ SQLite URL detected")
        else:
            print("❌ Unknown database URL format")
            return False
    else:
        print("⚠️  DATABASE_URL not set, will use SQLite default")
    
    # Test imports
    try:
        print("\n🧪 Testing imports...")
        from app.core.config import settings
        print("✅ Config imported successfully")
        
        print(f"Settings environment: {settings.environment}")
        print(f"Settings is_postgresql: {settings.is_postgresql}")
        print(f"Settings database_url starts with: {settings.database_url[:30]}...")
        
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    # Test database connection
    try:
        print("\n🔌 Testing database engine creation...")
        from app.database import engine
        print("✅ Database engine created successfully")
        
        # Test connection
        with engine.connect() as conn:
            if settings.is_postgresql:
                result = conn.execute("SELECT version()")
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL connection successful: {version[:50]}...")
            else:
                result = conn.execute("SELECT sqlite_version()")
                version = result.fetchone()[0]
                print(f"✅ SQLite connection successful: {version}")
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)