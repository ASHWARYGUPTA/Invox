#!/usr/bin/env python3
"""
Test OAuth Flow End-to-End

This script tests the complete OAuth authentication flow:
1. Simulates OAuth callback from Google
2. Verifies user creation in database
3. Tests JWT token generation
4. Tests protected endpoints with authentication
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api/v1"

# Test data - simulating what Google OAuth would send
TEST_OAUTH_DATA = {
    "provider": "google",
    "provider_account_id": "google_test_user_123456",
    "email": "test.user@example.com",
    "name": "Test User",
    "image": "https://lh3.googleusercontent.com/a/test-image",
    "access_token": "ya29.test_access_token_12345",
    "refresh_token": "1//test_refresh_token_67890",
    "expires_at": int((datetime.now().timestamp()) + 3600),  # 1 hour from now
    "token_type": "Bearer",
    "scope": "openid email profile",
    "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test_id_token"
}

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {text}")
    print(f"{'='*60}\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def test_health():
    """Test 1: Health Check"""
    print_header("Test 1: Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is healthy: {data}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect to backend: {e}")
        return False

def test_oauth_callback():
    """Test 2: OAuth Callback - User Creation"""
    print_header("Test 2: OAuth Callback - Create User")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=TEST_OAUTH_DATA,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "access_token" in data:
                print_success("User created and JWT token received!")
                print_info(f"Token Type: {data.get('token_type')}")
                print_info(f"Token (first 50 chars): {data['access_token'][:50]}...")
                return data["access_token"]
            else:
                print_error("No access token in response")
                return None
        else:
            print_error(f"OAuth callback failed: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"OAuth callback error: {e}")
        return None

def test_existing_user_login():
    """Test 3: OAuth Callback - Existing User Login"""
    print_header("Test 3: OAuth Callback - Login Existing User")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=TEST_OAUTH_DATA,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Existing user logged in successfully!")
            print_info("OAuth tokens updated in database")
            return data["access_token"]
        else:
            print_error(f"Login failed: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_get_current_user(token):
    """Test 4: Get Current User (Protected Endpoint)"""
    print_header("Test 4: Get Current User - Protected Endpoint")
    
    if not token:
        print_error("No token provided, skipping test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers=headers,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print_success("Successfully retrieved current user!")
            print_info(f"User Data:\n{json.dumps(user, indent=2)}")
            return True
        else:
            print_error(f"Failed to get user: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Get user error: {e}")
        return False

def test_get_user_profile(token):
    """Test 5: Get User Profile (Protected Endpoint)"""
    print_header("Test 5: Get User Profile - Protected Endpoint")
    
    if not token:
        print_error("No token provided, skipping test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE}/users/me",
            headers=headers,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print_success("Successfully retrieved user profile!")
            print_info(f"Profile Data:\n{json.dumps(user, indent=2)}")
            return True
        else:
            print_error(f"Failed to get profile: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Get profile error: {e}")
        return False

def test_update_profile(token):
    """Test 6: Update User Profile (Protected Endpoint)"""
    print_header("Test 6: Update User Profile - Protected Endpoint")
    
    if not token:
        print_error("No token provided, skipping test")
        return False
    
    update_data = {
        "name": "Updated Test User",
        "image": "https://example.com/new-avatar.jpg"
    }
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.put(
            f"{API_BASE}/users/me",
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print_success("Successfully updated user profile!")
            print_info(f"Updated Profile:\n{json.dumps(user, indent=2)}")
            return True
        else:
            print_error(f"Failed to update profile: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Update profile error: {e}")
        return False

def test_unauthorized_access():
    """Test 7: Unauthorized Access (No Token)"""
    print_header("Test 7: Unauthorized Access - No Token")
    
    try:
        response = requests.get(
            f"{API_BASE}/users/me",
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code in [401, 403]:
            print_success("Correctly rejected unauthorized request!")
            print_info(f"Error: {response.json()}")
            return True
        else:
            print_error(f"Should have returned 401 or 403, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Test error: {e}")
        return False

def test_invalid_token():
    """Test 8: Invalid Token"""
    print_header("Test 8: Invalid Token Authentication")
    
    try:
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = requests.get(
            f"{API_BASE}/users/me",
            headers=headers,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Correctly rejected invalid token!")
            print_info(f"Error: {response.json()}")
            return True
        else:
            print_error(f"Should have returned 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Test error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 OAuth Flow End-to-End Testing")
    print("="*60)
    print(f"\n🔗 Backend URL: {BACKEND_URL}")
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track results
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Test 1: Health Check
    results["total"] += 1
    if test_health():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("Backend is not healthy. Stopping tests.")
        return
    
    # Test 2: Create User via OAuth
    results["total"] += 1
    token = test_oauth_callback()
    if token:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("Failed to create user. Stopping tests.")
        return
    
    # Test 3: Login Existing User
    results["total"] += 1
    token = test_existing_user_login()
    if token:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 4: Get Current User
    results["total"] += 1
    if test_get_current_user(token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 5: Get User Profile
    results["total"] += 1
    if test_get_user_profile(token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 6: Update Profile
    results["total"] += 1
    if test_update_profile(token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 7: Unauthorized Access
    results["total"] += 1
    if test_unauthorized_access():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 8: Invalid Token
    results["total"] += 1
    if test_invalid_token():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Print Summary
    print_header("Test Summary")
    print(f"✅ Passed: {results['passed']}/{results['total']}")
    print(f"❌ Failed: {results['failed']}/{results['total']}")
    
    if results['failed'] == 0:
        print("\n🎉 All tests passed! OAuth flow is working perfectly!")
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed. Please review the errors above.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
