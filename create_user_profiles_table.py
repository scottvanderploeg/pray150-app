#!/usr/bin/env python3
"""
Create user_profiles table in Supabase
"""
import os
from supabase import create_client

def create_user_profiles_table():
    """Create the user_profiles table using SQL execution"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Create table SQL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS public.user_profiles (
        id BIGSERIAL PRIMARY KEY,
        user_id TEXT NOT NULL UNIQUE,
        username TEXT,
        email TEXT,
        first_name TEXT,
        last_name TEXT,
        country TEXT,
        zip_code TEXT,
        preferred_translation TEXT DEFAULT 'NIV',
        font_preference TEXT DEFAULT 'Georgia',
        theme_preference TEXT DEFAULT 'default',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    try:
        # Try to execute the SQL directly using the REST API
        import requests
        
        response = requests.post(
            f"{supabase_url}/rest/v1/rpc",
            headers={
                "Authorization": f"Bearer {supabase_key}",
                "apikey": supabase_key,
                "Content-Type": "application/json"
            },
            json={"sql": create_table_sql}
        )
        
        if response.status_code == 200:
            print("✓ user_profiles table created successfully")
            return True
        else:
            print(f"Failed to create table: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

if __name__ == "__main__":
    create_user_profiles_table()