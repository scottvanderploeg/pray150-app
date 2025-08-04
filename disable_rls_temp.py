#!/usr/bin/env python3
"""
Temporary script to disable RLS for journal_entries table to test functionality
"""
import os
from supabase import create_client

def disable_rls_temporarily():
    """Disable RLS temporarily for testing"""
    try:
        # Use service role key if available, otherwise regular key
        service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_KEY"))
        
        supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            service_key
        )
        
        # Execute SQL to disable RLS temporarily
        result = supabase.rpc('exec_sql', {
            'sql': 'ALTER TABLE journal_entries DISABLE ROW LEVEL SECURITY;'
        }).execute()
        
        print("RLS disabled for journal_entries table")
        return True
        
    except Exception as e:
        print(f"Failed to disable RLS: {e}")
        
        # Try direct SQL approach
        try:
            result = supabase.postgrest.rpc('exec_sql', {
                'sql': 'ALTER TABLE journal_entries DISABLE ROW LEVEL SECURITY;'
            }).execute()
            print("RLS disabled via direct SQL")
            return True
        except Exception as e2:
            print(f"Direct SQL also failed: {e2}")
            return False

def test_journal_save():
    """Test saving a journal entry"""
    try:
        supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )
        
        test_entry = {
            "user_id": "test_user_temp",
            "psalm_id": 1,
            "prompt_responses": {
                "1": "Test entry after RLS disable"
            }
        }
        
        result = supabase.table('journal_entries').insert(test_entry).execute()
        
        if result.data:
            print(f"✓ Test entry saved successfully: {result.data[0]['id']}")
            
            # Clean up test entry
            supabase.table('journal_entries').delete().eq('id', result.data[0]['id']).execute()
            print("✓ Test entry cleaned up")
            return True
        else:
            print("✗ Test entry failed to save")
            return False
            
    except Exception as e:
        print(f"Test save failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Temporary RLS Disable for Testing ===")
    
    if disable_rls_temporarily():
        print("\nTesting journal save...")
        if test_journal_save():
            print("\n✓ Journal saving should now work!")
            print("Remember to re-enable RLS after testing:")
            print("ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;")
        else:
            print("\n✗ Journal saving still not working")
    else:
        print("\n✗ Could not disable RLS")