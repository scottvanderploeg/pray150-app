#!/usr/bin/env python3
"""
Check the current structure of prayer_lists table
"""
import os
from supabase import create_client

def check_table_structure():
    """Check what columns exist in prayer_lists table"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_service_key:
        print("Missing Supabase credentials")
        return
    
    supabase = create_client(supabase_url, supabase_service_key)
    
    try:
        # Try to insert a minimal record to see what columns are expected
        test_data = {'user_id': 'test', 'category': 'test'}
        result = supabase.table('prayer_lists').insert(test_data).execute()
        print(f"Basic insert worked: {result}")
        
        # Clean up
        if result.data:
            test_id = result.data[0]['id']
            supabase.table('prayer_lists').delete().eq('id', test_id).execute()
            
    except Exception as e:
        print(f"Error with basic insert: {e}")
        
    try:
        # Try with more fields
        test_data2 = {
            'user_id': 'test', 
            'category': 'test',
            'prayer_request': 'test prayer',
            'request_text': 'test text'
        }
        result2 = supabase.table('prayer_lists').insert(test_data2).execute()
        print(f"Extended insert worked: {result2}")
        
        # Clean up
        if result2.data:
            test_id = result2.data[0]['id']
            supabase.table('prayer_lists').delete().eq('id', test_id).execute()
            
    except Exception as e:
        print(f"Error with extended insert: {e}")

if __name__ == "__main__":
    check_table_structure()