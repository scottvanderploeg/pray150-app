#!/usr/bin/env python3

from database import get_supabase_client

def debug_psalm_progress():
    """Debug psalm progression for current user"""
    try:
        supabase = get_supabase_client()
        
        # Check current user's journal entries
        print("=== Journal Entries ===")
        journal_result = supabase.table('journal_entries').select('*')\
            .eq('user_id', '57564e6b-3adc-4613-abaa-dc61d56b6d4a')\
            .order('created_at', desc=False).execute()
        
        print(f"Found {len(journal_result.data)} journal entries:")
        for entry in journal_result.data:
            print(f"  - Psalm {entry.get('psalm_number', entry.get('psalm_id'))}: {entry.get('created_at')}")
        
        # Check psalm progress records
        print("\n=== Psalm Progress Records ===")
        progress_result = supabase.table('psalm_progress').select('*')\
            .eq('user_id', '57564e6b-3adc-4613-abaa-dc61d56b6d4a')\
            .order('created_at', desc=False).execute()
        
        print(f"Found {len(progress_result.data)} progress records:")
        for progress in progress_result.data:
            print(f"  - Psalm {progress.get('psalm_id')}: completed={progress.get('completed')} at {progress.get('created_at')}")
        
        # Test the progression logic using journal entries
        print("\n=== Testing Progression Logic (Using Journal Entries) ===")
        completed_psalms = set()
        for entry in journal_result.data:
            psalm_num = entry.get('psalm_number')
            if psalm_num:
                completed_psalms.add(int(psalm_num))
        
        print(f"Completed psalms (from journal entries): {sorted(completed_psalms)}")
        
        # Find next psalm
        current_psalm = 1
        while current_psalm in completed_psalms and current_psalm <= 150:
            current_psalm += 1
        
        if current_psalm > 150:
            current_psalm = 1
            
        print(f"Next psalm should be: {current_psalm}")
        
    except Exception as e:
        print(f"Error debugging: {e}")

if __name__ == "__main__":
    debug_psalm_progress()