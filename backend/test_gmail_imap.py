#!/usr/bin/env python3
"""
Quick IMAP Connection Tester
Tests Gmail IMAP connection to debug authentication issues
"""
import imaplib
import sys

def test_gmail_imap():
    print("=" * 60)
    print("Gmail IMAP Connection Tester")
    print("=" * 60)
    print()
    
    # Get credentials
    email = input("📧 Enter your Gmail address: ").strip()
    password = input("🔑 Enter your Gmail App Password (16 chars, no spaces): ").strip()
    
    # Remove spaces if user included them
    password = password.replace(" ", "")
    
    print()
    print("Testing connection...")
    print(f"  Email: {email}")
    print(f"  Server: imap.gmail.com")
    print(f"  Port: 993")
    print(f"  SSL: Yes")
    print()
    
    try:
        # Connect to Gmail IMAP
        print("⏳ Connecting to imap.gmail.com:993...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        print("✓ SSL connection established")
        
        # Attempt login
        print(f"⏳ Logging in as {email}...")
        mail.login(email, password)
        print("✓ Login successful!")
        
        # Get mailbox info
        print()
        print("📊 Mailbox Information:")
        print("-" * 60)
        
        # List folders
        status, folders = mail.list()
        print(f"\n📁 Available folders ({len(folders)}):")
        for folder in folders[:10]:  # Show first 10
            print(f"  • {folder.decode()}")
        if len(folders) > 10:
            print(f"  ... and {len(folders) - 10} more")
        
        # Select inbox and get stats
        mail.select("INBOX")
        
        # Count unread emails
        status, unread = mail.search(None, 'UNSEEN')
        unread_count = len(unread[0].split()) if unread[0] else 0
        
        # Count total emails
        status, total = mail.search(None, 'ALL')
        total_count = len(total[0].split()) if total[0] else 0
        
        print()
        print("📧 INBOX Statistics:")
        print(f"  Total emails: {total_count}")
        print(f"  Unread emails: {unread_count}")
        
        # Logout
        mail.logout()
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! Your Gmail IMAP connection works perfectly!")
        print("=" * 60)
        print()
        print("✓ You can use these credentials in the Invox email config")
        print("✓ Make sure to enter the password WITHOUT spaces")
        print()
        return True
        
    except imaplib.IMAP4.error as e:
        print()
        print("=" * 60)
        print("❌ IMAP Authentication Error")
        print("=" * 60)
        print(f"\nError: {e}")
        print()
        print("🔍 Common Causes:")
        print()
        print("1. ❌ Using regular Gmail password instead of App Password")
        print("   → You MUST use an App Password, not your regular password")
        print("   → Generate one at: https://myaccount.google.com/apppasswords")
        print()
        print("2. ❌ 2-Step Verification not enabled")
        print("   → App Passwords require 2FA to be enabled")
        print("   → Enable at: https://myaccount.google.com/security")
        print()
        print("3. ❌ App Password has spaces")
        print("   → Remove all spaces from the 16-character password")
        print("   → Example: abcdefghijklmnop (not abcd efgh ijkl mnop)")
        print()
        print("4. ❌ Old/revoked App Password")
        print("   → Generate a fresh App Password")
        print("   → Revoke old ones at: https://myaccount.google.com/apppasswords")
        print()
        print("5. ❌ IMAP disabled in Gmail settings")
        print("   → Enable at: Gmail → Settings → Forwarding and POP/IMAP")
        print()
        return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Connection Error")
        print("=" * 60)
        print(f"\nError: {e}")
        print()
        print("🔍 Possible Issues:")
        print()
        print("1. ❌ No internet connection")
        print("   → Check your network connection")
        print()
        print("2. ❌ Firewall blocking port 993")
        print("   → Check firewall settings")
        print()
        print("3. ❌ Gmail IMAP servers down (rare)")
        print("   → Check https://www.google.com/appsstatus")
        print()
        return False

if __name__ == "__main__":
    print()
    success = test_gmail_imap()
    print()
    
    if not success:
        print("📚 Quick Setup Guide:")
        print()
        print("Step 1: Enable 2-Step Verification")
        print("  → https://myaccount.google.com/signinoptions/two-step-verification")
        print()
        print("Step 2: Generate App Password")
        print("  → https://myaccount.google.com/apppasswords")
        print("  → Select 'Mail' and 'Other (Custom name)'")
        print("  → Copy the 16-character password (remove spaces!)")
        print()
        print("Step 3: Enable IMAP in Gmail")
        print("  → Gmail → Settings (gear icon) → See all settings")
        print("  → Forwarding and POP/IMAP tab")
        print("  → Enable IMAP → Save Changes")
        print()
        print("Step 4: Run this test again")
        print()
        sys.exit(1)
    
    sys.exit(0)
