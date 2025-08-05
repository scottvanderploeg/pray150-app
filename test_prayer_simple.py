#!/usr/bin/env python3
"""
Test the simplest prayer creation
"""
import os
from supabase import create_client

def test_simple_prayer():
    """Test adding a prayer with minimal data"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    supabase = create_client(supabase_url, supabase_service_key)
    
    # Test with minimal data first
    prayer_data = {
        'user_id': '82045853-62d6-41be-a3f9-681ee74dd38d',
        'category': 'family'
    }
    
    try:
        print("Testing minimal prayer...")
        result = supabase.table('prayer_lists').insert(prayer_data).execute()
        print(f"Success! Minimal prayer: {result.data}")
        
        if result.data:
            prayer_id = result.data[0]['id']
            
            # Now try to update with title and description
            update_data = {
                'title': 'Family Health',
                'description': 'Please bless my family with good health and safety'
            }
            
            print("Testing update with title/description...")
            update_result = supabase.table('prayer_lists').update(update_data).eq('id', prayer_id).execute()
            print(f"Update result: {update_result.data}")
            
            # Clean up
            delete_result = supabase.table('prayer_lists').delete().eq('id', prayer_id).execute()
            print(f"Cleanup: {delete_result}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_prayer()