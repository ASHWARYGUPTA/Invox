"""
Quick database connection test script
Run this to verify your database connection is working
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine
from app.core.config import settings
from sqlalchemy import text

print("=" * 50)
print("Database Connection Test")
print("=" * 50)
print(f"\n📍 Database URL: {settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0].split('//')[1], '***')}")
print(f"📍 Project: {settings.PROJECT_NAME}\n")

try:
    print("🔄 Attempting to connect...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        
        print("✅ Connection successful!")
        print(f"✅ PostgreSQL version: {version[:50]}...")
        
        # Test if users table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
        """))
        table_exists = result.fetchone()[0]
        
        if table_exists:
            print("✅ 'users' table exists")
            
            # Count users
            result = conn.execute(text("SELECT COUNT(*) FROM users;"))
            user_count = result.fetchone()[0]
            print(f"✅ Found {user_count} user(s) in database")
        else:
            print("⚠️  'users' table does not exist")
            print("   Run: alembic upgrade head")
        
        print("\n🎉 Database is ready to use!")
        
except Exception as e:
    print(f"\n❌ Connection failed!")
    print(f"❌ Error: {str(e)}")
    print("\n💡 Troubleshooting tips:")
    print("   1. Check PostgreSQL is running")
    print("   2. Verify DATABASE_URL in .env file")
    print("   3. Check database exists: CREATE DATABASE invoice_db;")
    print("   4. Run migrations: alembic upgrade head")
    print("\n   See backend/DB_FIX.md for detailed solutions")
    sys.exit(1)

print("=" * 50)
