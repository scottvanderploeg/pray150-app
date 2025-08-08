#!/usr/bin/env python3

from database import get_supabase_client

def check_tables():
    """Check what tables exist in our database"""
    try:
        supabase = get_supabase_client()
        
        # List all tables by trying to access them
        tables_to_check = ['users', 'user_profiles', 'psalms', 'journal_entries', 'prayers', 'psalm_progress']
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"✓ Table '{table}' exists ({len(result.data)} rows checked)")
            except Exception as e:
                print(f"✗ Table '{table}' missing: {e}")
                
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    check_tables()