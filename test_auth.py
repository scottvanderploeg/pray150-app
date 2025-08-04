#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_auth_endpoints():
    """Test the authentication endpoints"""
    print("🧪 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test data
    test_email = "authtest@example.org" 
    test_password = "secure123"
    
    print(f"📧 Test Email: {test_email}")
    print(f"🔑 Test Password: {test_password}")
    print()
    
    # Test registration
    print("1️⃣  Testing Registration...")
    register_data = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            user_id = response.json().get("user_id")
            print(f"👤 User ID: {user_id}")
        elif response.status_code == 409:
            print("⚠️  User already exists, continuing with login test...")
        else:
            print("❌ Registration failed")
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    print()
    
    # Test login
    print("2️⃣  Testing Login...")
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            access_token = response.json().get("access_token")
            print(f"🎫 Access Token: {access_token[:50]}...")
            
            # Test token verification
            print()
            print("3️⃣  Testing Token Verification...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            verify_response = requests.get(
                f"{BASE_URL}/api/verify",
                headers=headers
            )
            
            print(f"Status Code: {verify_response.status_code}")
            print(f"Response: {verify_response.json()}")
            
            if verify_response.status_code == 200:
                print("✅ Token verification successful!")
            else:
                print("❌ Token verification failed")
        else:
            print("❌ Login failed")
            error_msg = response.json().get("error", "Unknown error")
            if "Email not confirmed" in error_msg:
                print("⚠️  Note: Supabase requires email confirmation for new users")
                print("📧 Check the email inbox and confirm the registration")
                
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    print()
    print("🏁 Authentication test completed!")

if __name__ == "__main__":
    test_auth_endpoints()