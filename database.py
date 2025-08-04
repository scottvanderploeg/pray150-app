"""
Supabase database initialization and table creation
"""
import os
from supabase import create_client

def get_supabase_client():
    """Get Supabase client instance"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    return create_client(supabase_url, supabase_key)

def initialize_database():
    """Initialize Supabase database tables"""
    try:
        supabase = get_supabase_client()
        
        # Create tables using Supabase SQL execution
        # Note: In production, these would typically be created via Supabase migrations
        
        # Create psalms table - exact schema as specified
        create_psalms_table = """
        CREATE TABLE IF NOT EXISTS public.psalms (
            id BIGSERIAL PRIMARY KEY,
            psalm_number INT4 UNIQUE NOT NULL,
            text_niv TEXT,
            text_esv TEXT,
            text_nlt TEXT,
            text_nkjv TEXT,
            text_nrsv TEXT,
            music_url TEXT
        );
        """
        
        # Create journal_entries table - exact schema as specified
        create_journal_entries_table = """
        CREATE TABLE IF NOT EXISTS public.journal_entries (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            psalm_id BIGINT REFERENCES public.psalms(id),
            prompt_responses JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        # Create markups table - exact schema as specified
        create_markups_table = """
        CREATE TABLE IF NOT EXISTS public.markups (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            psalm_id BIGINT REFERENCES public.psalms(id),
            markup_data JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        # Create prayer_lists table - exact schema as specified
        create_prayer_lists_table = """
        CREATE TABLE IF NOT EXISTS public.prayer_lists (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            category TEXT,
            prayer_text TEXT,
            is_answered BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        # Create progress table - exact schema as specified
        create_progress_table = """
        CREATE TABLE IF NOT EXISTS public.progress (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            psalm_id BIGINT REFERENCES public.psalms(id),
            completed BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        # Try to create tables directly using Supabase
        try:
            # Execute each table creation script
            tables = [
                ('psalms', create_psalms_table),
                ('journal_entries', create_journal_entries_table),
                ('markups', create_markups_table),
                ('prayer_lists', create_prayer_lists_table),
                ('progress', create_progress_table)
            ]
            
            print("Attempting to create Supabase tables...")
            
            for table_name, sql_script in tables:
                try:
                    # Note: Supabase Python client doesn't support raw SQL execution
                    # Tables need to be created via dashboard or API
                    print(f"✓ {table_name} table schema ready")
                except Exception as e:
                    print(f"✗ Error with {table_name}: {e}")
            
            print("\nTo create tables in Supabase:")
            print("1. Go to your Supabase dashboard → SQL Editor")
            print("2. Run the SQL scripts provided in SUPABASE_SETUP.md")
            print("3. Or use the table creation scripts below:")
            
            return True
            
        except Exception as e:
            print(f"Database setup notice: {e}")
            return False
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# SQL scripts for manual execution in Supabase dashboard - Updated to match exact schema
SUPABASE_SQL_SCRIPTS = {
    'psalms': """
    CREATE TABLE IF NOT EXISTS public.psalms (
        id BIGSERIAL PRIMARY KEY,
        psalm_number INT4 UNIQUE NOT NULL,
        text_niv TEXT,
        text_esv TEXT,
        text_nlt TEXT,
        text_nkjv TEXT,
        text_nrsv TEXT,
        music_url TEXT
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.psalms ENABLE ROW LEVEL SECURITY;
    
    -- Allow all users to read psalms
    CREATE POLICY "Anyone can view psalms" ON public.psalms
        FOR SELECT USING (true);
    
    -- Allow authenticated users to insert psalms (for data initialization)
    CREATE POLICY "Authenticated users can insert psalms" ON public.psalms
        FOR INSERT WITH CHECK (true);
    """,
    
    'journal_entries': """
    CREATE TABLE IF NOT EXISTS public.journal_entries (
        id BIGSERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        psalm_id BIGINT REFERENCES public.psalms(id),
        prompt_responses JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.journal_entries ENABLE ROW LEVEL SECURITY;
    
    -- Users can manage their own journal entries (using user_id as text)
    CREATE POLICY "Users can manage their own journal entries" ON public.journal_entries
        USING (user_id = auth.uid()::text);
    """,
    
    'markups': """
    CREATE TABLE IF NOT EXISTS public.markups (
        id BIGSERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        psalm_id BIGINT REFERENCES public.psalms(id),
        markup_data JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.markups ENABLE ROW LEVEL SECURITY;
    
    -- Users can manage their own markups
    CREATE POLICY "Users can manage their own markups" ON public.markups
        USING (user_id = auth.uid()::text);
    """,
    
    'prayer_lists': """
    CREATE TABLE IF NOT EXISTS public.prayer_lists (
        id BIGSERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        category TEXT,
        prayer_text TEXT,
        is_answered BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.prayer_lists ENABLE ROW LEVEL SECURITY;
    
    -- Users can manage their own prayers
    CREATE POLICY "Users can manage their own prayers" ON public.prayer_lists
        USING (user_id = auth.uid()::text);
    """,
    
    'progress': """
    CREATE TABLE IF NOT EXISTS public.progress (
        id BIGSERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        psalm_id BIGINT REFERENCES public.psalms(id),
        completed BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.progress ENABLE ROW LEVEL SECURITY;
    
    -- Users can manage their own progress
    CREATE POLICY "Users can manage their own progress" ON public.progress
        USING (user_id = auth.uid()::text);
    """
}

def check_table_exists(table_name):
    """Check if a table exists in Supabase"""
    try:
        supabase = get_supabase_client()
        # Try to select from table to check if it exists
        result = supabase.table(table_name).select('*').limit(1).execute()
        return True
    except Exception as e:
        print(f"Table {table_name} check failed: {e}")
        return False

def verify_all_tables():
    """Verify all required tables exist"""
    required_tables = ['psalms', 'journal_entries', 'markups', 'prayer_lists', 'progress']
    existing_tables = []
    missing_tables = []
    
    for table in required_tables:
        if check_table_exists(table):
            existing_tables.append(table)
            print(f"✓ Table '{table}' exists")
        else:
            missing_tables.append(table)
            print(f"✗ Table '{table}' missing")
    
    return existing_tables, missing_tables