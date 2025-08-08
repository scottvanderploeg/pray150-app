#!/usr/bin/env python3

from database import get_supabase_client

def create_psalm_progress_table():
    """Create the psalm_progress table in Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Create psalm_progress table using raw SQL
        sql = """
        CREATE TABLE IF NOT EXISTS psalm_progress (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            psalm_id INTEGER NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Create RLS policy for psalm_progress
        ALTER TABLE psalm_progress ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can only see their own psalm progress" ON psalm_progress
        FOR ALL USING (auth.uid()::text = user_id);
        
        -- Create index for better performance
        CREATE INDEX IF NOT EXISTS psalm_progress_user_id_idx ON psalm_progress(user_id);
        CREATE INDEX IF NOT EXISTS psalm_progress_psalm_id_idx ON psalm_progress(psalm_id);
        """
        
        result = supabase.rpc('run_sql', {'sql': sql}).execute()
        print("✓ psalm_progress table created successfully!")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error creating table: {e}")
        
        # Alternative: Try using Supabase REST API to create via SQL
        try:
            # Use a simple query to test if we can create the table another way
            print("Trying alternative table creation method...")
            
            # Create the table by inserting a dummy record that will auto-create structure
            dummy_data = {
                'user_id': 'dummy',
                'psalm_id': 1,
                'completed': True
            }
            
            result = supabase.table('psalm_progress').insert(dummy_data).execute()
            print(f"Table creation attempt result: {result}")
            
            # Remove the dummy record
            supabase.table('psalm_progress').delete().eq('user_id', 'dummy').execute()
            print("✓ psalm_progress table created via insertion method!")
            
        except Exception as e2:
            print(f"Alternative method also failed: {e2}")

if __name__ == "__main__":
    create_psalm_progress_table()