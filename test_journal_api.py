#!/usr/bin/env python3
"""
Test script for the journal API endpoint
"""
import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_journal_endpoint():
    """Test the journal endpoint functionality"""
    
    # Sample journal entry data
    journal_data = {
        "psalm_id": 1,
        "prompt_responses": {
            "Lord, where is my heart/soul today?": "My heart feels peaceful today, grateful for God's presence.",
            "LOOK! Lord, help me discover new truth from your Word today.": "I discovered that God's love is steadfast even in difficult times.",
            "LISTEN! Lord, what is your thought for me today from your Word?": "God is reminding me to trust in His timing and provision.",
            "RESPOND: Lord, what do I need to talk to you about? What are you calling me to do?": "I need to pray for patience and trust. God is calling me to serve others with love."
        }
    }
    
    print("=== Journal API Test ===")
    print(f"URL: {BASE_URL}/journal")
    print(f"Data: {json.dumps(journal_data, indent=2)}")
    
    # Test without authentication (should fail)
    print("\n1. Testing without JWT token (should fail with 401):")
    response = requests.post(f"{BASE_URL}/journal", json=journal_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test with invalid JWT token (should fail)
    print("\n2. Testing with invalid JWT token (should fail with 422):")
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.post(f"{BASE_URL}/journal", json=journal_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test with missing data
    print("\n3. Testing with missing psalm_id (should fail with 400):")
    invalid_data = {"prompt_responses": journal_data["prompt_responses"]}
    response = requests.post(f"{BASE_URL}/journal", json=invalid_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test with missing prompt responses
    print("\n4. Testing with incomplete prompt_responses (should fail with 400):")
    incomplete_data = {
        "psalm_id": 1,
        "prompt_responses": {
            "Lord, where is my heart/soul today?": "Test response"
        }
    }
    response = requests.post(f"{BASE_URL}/journal", json=incomplete_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    print("\n=== To test with valid JWT token: ===")
    print("1. Register a user: POST /api/register")
    print("2. Confirm email via Supabase dashboard or email")
    print("3. Login: POST /api/login")
    print("4. Use the returned access_token in Authorization header")
    print("5. Make journal entry: POST /api/journal")

if __name__ == "__main__":
    test_journal_endpoint()