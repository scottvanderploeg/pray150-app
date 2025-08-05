#!/usr/bin/env python3
"""
Setup prayer_lists table in Supabase
"""
import os
from supabase import create_client

def setup_prayer_table():
    """Create/verify the prayer_lists table structure"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # First, check current table structure
        result = supabase.table('prayer_lists').select('*').limit(1).execute()
        print(f"Current table query result: {result}")
        
        # Test inserting a sample prayer to see the structure
        test_prayer = {
            'user_id': 'test-user-123',
            'category': 'family',
            'prayer_text': 'Test prayer text',
            'is_answered': False
        }
        
        insert_result = supabase.table('prayer_lists').insert(test_prayer).execute()
        print(f"Test insert result: {insert_result}")
        
        # Clean up test data
        if insert_result.data:
            test_id = insert_result.data[0]['id']
            delete_result = supabase.table('prayer_lists').delete().eq('id', test_id).execute()
            print(f"Cleanup result: {delete_result}")
        
        return True
        
    except Exception as e:
        print(f"Prayer table test error: {e}")
        return False

if __name__ == "__main__":
    setup_prayer_table()