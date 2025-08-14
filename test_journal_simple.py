#!/usr/bin/env python3

import requests
import json

def test_journal_save():
    """Test journal save endpoint directly"""
    
    # Test data - simulating what would be sent from the browser
    test_data = {
        'psalm_id': 2,  # Trying to save entry for Psalm 2 (next psalm)
        'prompt_responses': {
            '1': 'Test response for prompt 1',
            '2': 'Test response for prompt 2',
            'emotion': 'great'
        }
    }
    
    try:
        # Make POST request to save journal endpoint
        response = requests.post(
            'http://localhost:5000/save_journal',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            cookies={'session': 'test'}  # This won't work without proper session, but let's see what happens
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error testing journal save: {e}")

if __name__ == "__main__":
    test_journal_save()