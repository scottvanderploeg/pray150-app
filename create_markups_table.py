#!/usr/bin/env python3
"""
Create the markups table in Supabase for storing highlights and notes
"""

from database import get_supabase_client
import sys

def create_markups_table():
    """Create the markups table with proper schema"""
    try:
        supabase = get_supabase_client()
        
        # Test if table already exists
        try:
            result = supabase.table('markups').select('*').limit(1).execute()
            print("✓ Markups table already exists")
            return True
        except Exception as e:
            if 'does not exist' in str(e) or 'not found' in str(e):
                print("Table doesn't exist, need to create it manually in Supabase dashboard")
            else:
                print(f"Error checking table: {e}")
        
        # Try to create via manual insert (this will fail but show us the issue)
        test_data = {
            'user_id': 'test_user',
            'psalm_id': 1,
            'markup_data': {
                'markup_type': 'highlight',
                'text': 'test text',
                'color': 'yellow'
            }
        }
        
        result = supabase.table('markups').insert(test_data).execute()
        print("✓ Table created successfully or already exists")
        print("Test result:", result)
        
        # Clean up test data
        if result.data:
            supabase.table('markups').delete().eq('user_id', 'test_user').execute()
            print("✓ Cleaned up test data")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating markups table: {e}")
        print("\nPlease create the table manually in Supabase dashboard with this SQL:")
        print("""
CREATE TABLE IF NOT EXISTS markups (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id TEXT NOT NULL,
    psalm_id INTEGER NOT NULL,
    markup_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE markups ENABLE ROW LEVEL SECURITY;

-- Create policy for users to manage their own markups
CREATE POLICY "Users can manage their own markups" ON markups
FOR ALL USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');
        """)
        return False

if __name__ == '__main__':
    success = create_markups_table()
    sys.exit(0 if success else 1)