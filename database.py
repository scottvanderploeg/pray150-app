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
        
        # Create users table (extends Supabase auth.users)
        create_users_table = """
        CREATE TABLE IF NOT EXISTS public.users (
            id UUID REFERENCES auth.users(id) PRIMARY KEY,
            username VARCHAR(64) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            preferred_translation VARCHAR(10) DEFAULT 'NIV',
            font_preference VARCHAR(50) DEFAULT 'Georgia',
            theme_preference VARCHAR(50) DEFAULT 'default',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create psalms table
        create_psalms_table = """
        CREATE TABLE IF NOT EXISTS public.psalms (
            id SERIAL PRIMARY KEY,
            psalm_number INTEGER UNIQUE NOT NULL,
            title VARCHAR(200),
            text_niv TEXT,
            text_esv TEXT,
            text_nlt TEXT,
            text_nkjv TEXT,
            text_nrsv TEXT,
            music_url VARCHAR(500),
            prompt_1 TEXT,
            prompt_2 TEXT,
            prompt_3 TEXT,
            prompt_4 TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create journal_entries table
        create_journal_entries_table = """
        CREATE TABLE IF NOT EXISTS public.journal_entries (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
            psalm_id INTEGER REFERENCES public.psalms(id),
            prompt_number INTEGER NOT NULL,
            content TEXT,
            is_shared BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create markups table
        create_markups_table = """
        CREATE TABLE IF NOT EXISTS public.markups (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
            psalm_id INTEGER REFERENCES public.psalms(id),
            translation VARCHAR(10) NOT NULL,
            start_position INTEGER,
            end_position INTEGER,
            markup_type VARCHAR(20),
            color VARCHAR(20) DEFAULT 'yellow',
            note_text TEXT,
            is_visible BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create prayer_lists table
        create_prayer_lists_table = """
        CREATE TABLE IF NOT EXISTS public.prayer_lists (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(50) NOT NULL,
            is_answered BOOLEAN DEFAULT FALSE,
            answered_date TIMESTAMP WITH TIME ZONE,
            answered_note TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create progress table
        create_progress_table = """
        CREATE TABLE IF NOT EXISTS public.progress (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
            psalm_id INTEGER REFERENCES public.psalms(id),
            completed_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            reading_time_minutes INTEGER,
            journal_completed BOOLEAN DEFAULT FALSE,
            music_listened BOOLEAN DEFAULT FALSE
        );
        """
        
        # Execute table creation (this would typically be done via Supabase dashboard or migrations)
        print("Database tables schema defined. Please create these tables in your Supabase dashboard:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to 'SQL Editor'")
        print("3. Execute the table creation scripts provided in database.py")
        print("4. Or use the Table Editor to create the tables manually")
        
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# SQL scripts for manual execution in Supabase dashboard
SUPABASE_SQL_SCRIPTS = {
    'users': """
    CREATE TABLE IF NOT EXISTS public.users (
        id UUID REFERENCES auth.users(id) PRIMARY KEY,
        username VARCHAR(64) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        preferred_translation VARCHAR(10) DEFAULT 'NIV',
        font_preference VARCHAR(50) DEFAULT 'Georgia',
        theme_preference VARCHAR(50) DEFAULT 'default',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
    
    -- Create policy for users to only access their own data
    CREATE POLICY "Users can view their own profile" ON public.users
        FOR SELECT USING (auth.uid() = id);
    
    CREATE POLICY "Users can update their own profile" ON public.users
        FOR UPDATE USING (auth.uid() = id);
    """,
    
    'psalms': """
    CREATE TABLE IF NOT EXISTS public.psalms (
        id SERIAL PRIMARY KEY,
        psalm_number INTEGER UNIQUE NOT NULL,
        title VARCHAR(200),
        text_niv TEXT,
        text_esv TEXT,
        text_nlt TEXT,
        text_nkjv TEXT,
        text_nrsv TEXT,
        music_url VARCHAR(500),
        prompt_1 TEXT,
        prompt_2 TEXT,
        prompt_3 TEXT,
        prompt_4 TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.psalms ENABLE ROW LEVEL SECURITY;
    
    -- Allow all authenticated users to read psalms
    CREATE POLICY "Anyone can view psalms" ON public.psalms
        FOR SELECT USING (true);
    """,
    
    'journal_entries': """
    CREATE TABLE IF NOT EXISTS public.journal_entries (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
        psalm_id INTEGER REFERENCES public.psalms(id),
        prompt_number INTEGER NOT NULL,
        content TEXT,
        is_shared BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.journal_entries ENABLE ROW LEVEL SECURITY;
    
    -- Users can only access their own journal entries
    CREATE POLICY "Users can manage their own journal entries" ON public.journal_entries
        USING (auth.uid() = user_id);
    """,
    
    'markups': """
    CREATE TABLE IF NOT EXISTS public.markups (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
        psalm_id INTEGER REFERENCES public.psalms(id),
        translation VARCHAR(10) NOT NULL,
        start_position INTEGER,
        end_position INTEGER,
        markup_type VARCHAR(20),
        color VARCHAR(20) DEFAULT 'yellow',
        note_text TEXT,
        is_visible BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.markups ENABLE ROW LEVEL SECURITY;
    
    -- Users can only access their own markups
    CREATE POLICY "Users can manage their own markups" ON public.markups
        USING (auth.uid() = user_id);
    """,
    
    'prayer_lists': """
    CREATE TABLE IF NOT EXISTS public.prayer_lists (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        category VARCHAR(50) NOT NULL,
        is_answered BOOLEAN DEFAULT FALSE,
        answered_date TIMESTAMP WITH TIME ZONE,
        answered_note TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.prayer_lists ENABLE ROW LEVEL SECURITY;
    
    -- Users can only access their own prayers
    CREATE POLICY "Users can manage their own prayers" ON public.prayer_lists
        USING (auth.uid() = user_id);
    """,
    
    'progress': """
    CREATE TABLE IF NOT EXISTS public.progress (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
        psalm_id INTEGER REFERENCES public.psalms(id),
        completed_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        reading_time_minutes INTEGER,
        journal_completed BOOLEAN DEFAULT FALSE,
        music_listened BOOLEAN DEFAULT FALSE
    );
    
    -- Enable Row Level Security
    ALTER TABLE public.progress ENABLE ROW LEVEL SECURITY;
    
    -- Users can only access their own progress
    CREATE POLICY "Users can manage their own progress" ON public.progress
        USING (auth.uid() = user_id);
    """
}