#!/usr/bin/env python3
"""
Create a completely new prayer_lists table with correct structure
"""
import os
from supabase import create_client

def create_fresh_prayer_table():
    """Create prayer_lists table from scratch"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_service_key:
        print("Missing Supabase credentials")
        return
    
    supabase = create_client(supabase_url, supabase_service_key)
    
    # Try different approaches to create the table
    create_sql_commands = [
        # Option 1: Simple create with just required fields
        """
        CREATE TABLE IF NOT EXISTS public.prayer_lists_new (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            category TEXT,
            title TEXT,
            description TEXT,
            is_answered BOOLEAN DEFAULT FALSE,
            answered_note TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            answered_at TIMESTAMPTZ
        );
        """,
        
        # Copy any existing data
        """
        INSERT INTO public.prayer_lists_new (user_id, category, created_at)
        SELECT user_id, category, created_at 
        FROM public.prayer_lists
        WHERE user_id IS NOT NULL;
        """,
        
        # Drop old table and rename new one
        """
        DROP TABLE IF EXISTS public.prayer_lists_old;
        ALTER TABLE public.prayer_lists RENAME TO prayer_lists_old;
        ALTER TABLE public.prayer_lists_new RENAME TO prayer_lists;
        """
    ]
    
    print("SQL commands to run in Supabase SQL Editor:")
    print("="*50)
    for i, sql in enumerate(create_sql_commands, 1):
        print(f"-- Step {i}:")
        print(sql.strip())
        print()
    
    print("="*50)
    print("Alternative single command:")
    print("""
-- Create new table with correct structure
CREATE TABLE IF NOT EXISTS public.prayer_lists_correct (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    category TEXT,
    title TEXT,
    description TEXT,
    is_answered BOOLEAN DEFAULT FALSE,
    answered_note TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    answered_at TIMESTAMPTZ
);

-- Copy existing data if any
INSERT INTO public.prayer_lists_correct (user_id, category, created_at)
SELECT user_id, category, created_at 
FROM public.prayer_lists
WHERE EXISTS (SELECT 1 FROM public.prayer_lists LIMIT 1);

-- Replace old table
DROP TABLE IF EXISTS public.prayer_lists;
ALTER TABLE public.prayer_lists_correct RENAME TO prayer_lists;

-- Add RLS policies
ALTER TABLE public.prayer_lists ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own prayers" ON public.prayer_lists
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);
""")

if __name__ == "__main__":
    create_fresh_prayer_table()