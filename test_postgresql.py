#!/usr/bin/env python3
"""
Test PostgreSQL connection and setup
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def test_postgresql_connection(database_url: str):
    """Test PostgreSQL connection"""
    print(f"🔍 Testing PostgreSQL connection...")
    print(f"📊 URL: {database_url.split('@')[0]}@***")
    
    try:
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"📋 PostgreSQL version: {version}")
            
            # Test database operations
            conn.execute(text("SELECT 1"))
            print("✅ Basic queries work")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
    else:
        database_url = input("Enter PostgreSQL URL: ")
    
    if not database_url.startswith(("postgresql://", "postgres://")):
        print("❌ Invalid PostgreSQL URL format")
        print("Expected: postgresql://user:password@host:port/database")
        sys.exit(1)
    
    success = test_postgresql_connection(database_url)
    
    if success:
        print("\n🎉 PostgreSQL is ready for deployment!")
        print("💡 To use this database:")
        print(f"   1. Set DATABASE_URL={database_url}")
        print("   2. Set ENVIRONMENT=production")
        print("   3. Run your application")
    else:
        print("\n❌ PostgreSQL connection failed")
        print("Please check your connection details and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()