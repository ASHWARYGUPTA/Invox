"""
Create default user for email poller
This script creates user ID 1 if it doesn't exist
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User

def create_default_user():
    """Create default user with ID 1 for email poller"""
    db = SessionLocal()
    
    try:
        # Check if user ID 1 exists
        user = db.query(User).filter(User.id == 1).first()
        
        if user:
            print(f"✅ User ID 1 already exists:")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.full_name}")
            print(f"   Active: {user.is_active}")
        else:
            # Create new user
            print("📝 Creating default user (ID 1) for email poller...")
            
            # Get email from user input
            email = input("Enter email address (default: admin@invoiceproject.com): ").strip()
            if not email:
                email = "admin@invoiceproject.com"
            
            full_name = input("Enter full name (default: Email Poller Admin): ").strip()
            if not full_name:
                full_name = "Email Poller Admin"
            
            user = User(
                email=email,
                full_name=full_name,
                is_active=True,
                google_sub=None  # Will be set when they log in via OAuth
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            print(f"\n✅ Successfully created user:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.full_name}")
            print(f"\n💡 This user will receive all invoices from the email poller.")
            print(f"   They can log in via Google OAuth to view invoices in the frontend.")
    
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  Create Default User for Email Poller")
    print("=" * 60)
    print()
    
    create_default_user()
    
    print()
    print("=" * 60)
    print("  Done!")
    print("=" * 60)
