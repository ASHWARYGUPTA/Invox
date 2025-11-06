"""
System Health Check Script
Tests all components of the invoice processing system
"""
import sys
import os
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_backend():
    """Check if backend is running"""
    print("\n🔍 Checking Backend Server...")
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"   ❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend. Is it running?")
        print("   Run: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_database():
    """Check database connection and data"""
    print("\n🔍 Checking Database...")
    try:
        from app.db.session import SessionLocal
        from app.models.user import User
        from app.models.invoice import Invoice
        
        db = SessionLocal()
        
        # Check connection
        user_count = db.query(User).count()
        invoice_count = db.query(Invoice).count()
        
        print(f"   ✅ Database connected")
        print(f"   Users: {user_count}")
        print(f"   Invoices: {invoice_count}")
        
        # Check if user ID 1 exists (needed for email poller)
        user_1 = db.query(User).filter(User.id == 1).first()
        if user_1:
            print(f"   ✅ Default user exists: {user_1.email}")
        else:
            print(f"   ⚠️  No user with ID 1 (email poller needs this)")
            print(f"   Run: python create_default_user.py")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n🔍 Checking Environment Variables...")
    
    required_vars = [
        "GOOGLE_API_KEY",
        "DATABASE_URL",
        "SECRET_KEY",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET"
    ]
    
    from app.core.config import settings
    
    all_ok = True
    for var in required_vars:
        value = getattr(settings, var, None)
        if value and value != "":
            print(f"   ✅ {var}: {'*' * 10} (set)")
        else:
            print(f"   ❌ {var}: NOT SET")
            all_ok = False
    
    return all_ok

def check_google_apis():
    """Check if Google APIs are working"""
    print("\n🔍 Checking Google APIs...")
    
    try:
        from app.services.processing_service import client
        
        if client is None:
            print("   ❌ Gemini API client not initialized")
            print("   Check GOOGLE_API_KEY in .env")
            return False
        else:
            print("   ✅ Gemini API client initialized")
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_email_poller_config():
    """Check email poller configuration"""
    print("\n🔍 Checking Email Poller Configuration...")
    
    credentials_file = os.path.join("app", "worker", "credentials.json")
    token_file = os.path.join("app", "worker", "token.json")
    
    if os.path.exists(credentials_file):
        print(f"   ✅ credentials.json exists")
    else:
        print(f"   ❌ credentials.json NOT FOUND")
        print(f"   Download from Google Cloud Console")
        return False
    
    if os.path.exists(token_file):
        print(f"   ✅ token.json exists (Gmail authorized)")
    else:
        print(f"   ⚠️  token.json not found (need to authorize)")
        print(f"   Run: python -m app.worker.email_poller")
    
    return True

def main():
    """Run all checks"""
    print("=" * 70)
    print("  🏥 Invoice Processing System - Health Check")
    print("=" * 70)
    
    results = {
        "Backend": check_backend(),
        "Database": check_database(),
        "Environment": check_environment(),
        "Google APIs": check_google_apis(),
        "Email Poller": check_email_poller_config()
    }
    
    print("\n" + "=" * 70)
    print("  📊 Summary")
    print("=" * 70)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {component}")
    
    all_ok = all(results.values())
    
    print("\n" + "=" * 70)
    if all_ok:
        print("  ✅ All systems operational!")
    else:
        print("  ⚠️  Some issues detected. Review above for details.")
    print("=" * 70)
    
    return all_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCheck cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
