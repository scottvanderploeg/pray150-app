#!/usr/bin/env python3

from database import get_supabase_client

def fix_journal_entry():
    """Fix the journal entry to correct psalm number"""
    try:
        supabase = get_supabase_client()
        
        # Find the journal entry with psalm_id = 19
        result = supabase.table('journal_entries').select('*')\
            .eq('user_id', '57564e6b-3adc-4613-abaa-dc61d56b6d4a')\
            .eq('psalm_id', 19).execute()
        
        if result.data:
            entry = result.data[0]
            print(f"Found journal entry with ID {entry['id']} for Psalm 19")
            
            # Update it to be for Psalm 1 (only psalm_id field exists)
            update_result = supabase.table('journal_entries')\
                .update({'psalm_id': 1})\
                .eq('id', entry['id']).execute()
            
            print(f"Updated journal entry to Psalm 1: {update_result}")
            
            # Verify the update
            verify_result = supabase.table('journal_entries').select('*')\
                .eq('user_id', '57564e6b-3adc-4613-abaa-dc61d56b6d4a').execute()
            
            print("Updated journal entries:")
            for entry in verify_result.data:
                print(f"  - Psalm {entry.get('psalm_number', entry.get('psalm_id'))}: {entry.get('created_at')}")
        else:
            print("No journal entry found for Psalm 19")
            
    except Exception as e:
        print(f"Error fixing journal entry: {e}")

if __name__ == "__main__":
    fix_journal_entry()