# Supabase Database Setup for Pray150

## Step 1: Create Tables in Supabase Dashboard

Your Flask app is now connected to Supabase, but you need to create the database tables manually in your Supabase dashboard. Here's how:

### Go to Supabase SQL Editor

1. Open your Supabase project dashboard
2. Click on "SQL Editor" in the left sidebar
3. Click "New Query" 
4. Copy and paste each script below, then run them one by one

### Script 1: Create Users Table

```sql
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

CREATE POLICY "Users can insert their own profile" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);
```

### Script 2: Create Psalms Table

```sql
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

-- Allow service role to insert psalms (for initialization)
CREATE POLICY "Service role can insert psalms" ON public.psalms
    FOR INSERT USING (true);
```

### Script 3: Create Journal Entries Table

```sql
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
```

### Script 4: Create Markups Table

```sql
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
```

### Script 5: Create Prayer Lists Table

```sql
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
```

### Script 6: Create Progress Table

```sql
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
```

## Step 2: Enable Email Authentication

1. In your Supabase dashboard, go to "Authentication" → "Settings" 
2. Make sure "Enable email confirmations" is turned ON if you want email verification
3. Or turn it OFF if you want to allow immediate registration without email confirmation

## Step 3: Test the Application

Once you've run all the SQL scripts above:

1. Your Flask app should be running at the provided URL
2. Try registering a new account
3. The app will automatically create sample Psalm data when you first visit the dashboard
4. You can start using the journaling and prayer features immediately

## Important Notes

- **Row Level Security (RLS)** is enabled on all tables to ensure users can only access their own data
- The **psalms** table can be read by all authenticated users but only modified by service roles
- All user-specific data (journal entries, prayers, progress) is automatically filtered by user ID
- The app uses Supabase Auth for user registration and login, with your custom users table for additional profile data

## Troubleshooting

If you encounter any issues:

1. **Authentication errors**: Check that your SUPABASE_URL, SUPABASE_KEY, and SUPABASE_JWT_SECRET are correctly set
2. **Database errors**: Verify all tables were created successfully in the Supabase dashboard
3. **Permission errors**: Make sure RLS policies are properly created for each table

The application should now be fully functional with your Supabase database!