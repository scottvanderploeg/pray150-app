#!/usr/bin/env python3
"""
Fix prayer_lists table by adding missing columns
"""
import os
from supabase import create_client

def fix_prayer_table():
    """Add missing columns to prayer_lists table"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_service_key:
        print("Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_service_key)
    
    try:
        # Add the missing columns using direct SQL
        sql_commands = [
            "ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS title TEXT;",
            "ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS description TEXT;",
            "ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS is_answered BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS answered_note TEXT;",
            "ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS answered_at TIMESTAMPTZ;"
        ]
        
        for sql in sql_commands:
            print(f"Running: {sql}")
            result = supabase.rpc('execute_sql', {'sql': sql}).execute()
            print(f"Result: {result}")
        
        print("✓ Successfully added missing columns!")
        
        # Test inserting a prayer
        test_prayer = {
            'user_id': '82045853-62d6-41be-a3f9-681ee74dd38d',
            'category': 'family',
            'title': 'Test Prayer',
            'description': 'Please bless my family with health and peace',
            'is_answered': False
        }
        
        insert_result = supabase.table('prayer_lists').insert(test_prayer).execute()
        print(f"✓ Test prayer inserted successfully: {insert_result.data}")
        
        # Clean up test prayer
        if insert_result.data:
            test_id = insert_result.data[0]['id']
            delete_result = supabase.table('prayer_lists').delete().eq('id', test_id).execute()
            print(f"✓ Test prayer cleaned up: {delete_result}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        print("Manual SQL needed - please run these commands in Supabase SQL Editor:")
        print()
        print("ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS title TEXT;")
        print("ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS description TEXT;")
        print("ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS is_answered BOOLEAN DEFAULT FALSE;")
        print("ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS answered_note TEXT;")
        print("ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS answered_at TIMESTAMPTZ;")
        return False

if __name__ == "__main__":
    fix_prayer_table()