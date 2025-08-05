#!/usr/bin/env python3
"""
Test adding a prayer directly
"""
import os
from models import Prayer

def test_prayer_add():
    """Test adding a prayer"""
    print("Testing prayer creation...")
    
    # Create a test prayer
    prayer = Prayer(
        user_id="82045853-62d6-41be-a3f9-681ee74dd38d",  # Your user ID
        category="family",
        prayer_text="Test Prayer: Please bless my family with health and peace"
    )
    
    print(f"Created prayer object: {prayer.__dict__}")
    
    # Try to save it
    result = prayer.save()
    print(f"Save result: {result}")
    
    if result:
        print("Prayer saved successfully!")
        print(f"Prayer ID: {prayer.id}")
    else:
        print("Failed to save prayer")

if __name__ == "__main__":
    test_prayer_add()