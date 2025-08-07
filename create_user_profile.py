#!/usr/bin/env python3
"""
Create missing user profile for existing user
"""
from database import get_supabase_client
import sys

def create_user_profile():
    # Get the current user ID from the logs (2e6b777c-732d-48f6-83e8-e7adc70c8434)
    user_id = "2e6b777c-732d-48f6-83e8-e7adc70c8434"
    
    # Ask for user details
    first_name = input("Enter your first name: ").strip()
    last_name = input("Enter your last name: ").strip()
    email = input("Enter your email: ").strip()
    
    if not first_name or not last_name or not email:
        print("Error: All fields are required")
        return False
        
    try:
        supabase = get_supabase_client()
        
        # Create profile data
        profile_data = {
            'user_id': user_id,
            'username': f"{first_name.lower()}.{last_name.lower()}",
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'country': None,
            'zip_code': None,
            'preferred_translation': 'NIV',
            'font_preference': 'Georgia',
            'theme_preference': 'default'
        }
        
        # Insert the profile
        result = supabase.table('user_profiles').insert(profile_data).execute()
        
        if result.data:
            print(f"✓ Successfully created profile for {first_name} {last_name}")
            print(f"✓ User ID: {user_id}")
            print(f"✓ Email: {email}")
            return True
        else:
            print("❌ Failed to create profile")
            return False
            
    except Exception as e:
        print(f"❌ Error creating profile: {e}")
        return False

if __name__ == "__main__":
    print("Creating user profile for existing user...")
    success = create_user_profile()
    if success:
        print("\n🎉 Profile created successfully!")
        print("Please refresh your dashboard to see your name displayed correctly.")
    else:
        print("\n❌ Profile creation failed. Please check the error messages above.")