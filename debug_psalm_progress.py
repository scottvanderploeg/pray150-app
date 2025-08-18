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
            print(f"    Full entry data: {entry}")
            
        # Check if there are any journal entries from today
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\n=== Today's Journal Entries ({today}) ===")
        
        todays_entries = []
        for entry in journal_result.data:
            if entry.get('created_at') and entry['created_at'].startswith(today):
                todays_entries.append(entry)
        
        print(f"Found {len(todays_entries)} entries from today:")
        for entry in todays_entries:
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
            # Check both psalm_number and psalm_id fields
            psalm_num = entry.get('psalm_number') or entry.get('psalm_id')
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
        
        # Test the User model method directly
        print("\n=== Testing User.get_current_psalm_number() ===")
        from models import User
        
        # Create a mock user object to test the method
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
            
            def get_current_psalm_number(self):
                from database import get_supabase_client
                try:
                    supabase = get_supabase_client()
                    
                    # Get all journal entries for this user to see which psalms have been completed
                    # Note: psalm_number field contains the actual psalm number (1-150)
                    journal_result = supabase.table('journal_entries').select('psalm_number, psalm_id')\
                        .eq('user_id', str(self.id))\
                        .order('created_at', desc=False).execute()
                    
                    if not journal_result.data:
                        # New user - start with Psalm 1
                        return 1
                    
                    # Get all psalms that have journal entries (completed psalms)
                    completed_psalms = set()
                    for entry in journal_result.data:
                        # Check both psalm_number and psalm_id fields
                        psalm_num = entry.get('psalm_number') or entry.get('psalm_id')
                        if psalm_num:
                            completed_psalms.add(int(psalm_num))
                    
                    # Find the next psalm in sequence starting from 1
                    current_psalm = 1
                    while current_psalm in completed_psalms and current_psalm <= 150:
                        current_psalm += 1
                    
                    # If we've completed all 150, start over at 1
                    if current_psalm > 150:
                        return 1
                        
                    return current_psalm
                    
                except Exception as e:
                    print(f"Error getting current psalm: {e}")
                    return 1  # Default to Psalm 1
        
        mock_user = MockUser('57564e6b-3adc-4613-abaa-dc61d56b6d4a')
        next_psalm = mock_user.get_current_psalm_number()
        print(f"User.get_current_psalm_number() returns: {next_psalm}")
        
    except Exception as e:
        print(f"Error debugging: {e}")

if __name__ == "__main__":
    debug_psalm_progress()