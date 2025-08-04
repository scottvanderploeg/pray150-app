# Supabase Database Setup for Pray150 - Updated Schema

## Step 1: Create Tables in Supabase Dashboard

Your Flask app is connected to Supabase with the exact schema you specified. Create these tables in your Supabase dashboard:

### Go to Supabase SQL Editor

1. Open your Supabase project dashboard
2. Click on "SQL Editor" in the left sidebar
3. Click "New Query" 
4. Copy and paste each script below, then run them one by one

### Script 1: Create Psalms Table

```sql
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
```

### Script 2: Create Journal Entries Table

```sql
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
```

### Script 3: Create Markups Table

```sql
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
```

### Script 4: Create Prayer Lists Table

```sql
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
```

### Script 5: Create Progress Table

```sql
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
```

## Step 2: Verification Status 

✅ **Connection Status**: Your app is successfully connected to Supabase
✅ **Existing Tables**: 4 out of 5 tables already exist (psalms, markups, prayer_lists, progress)
❌ **Missing**: Only the `journal_entries` table needs to be created

**IMPORTANT**: You only need to run Script 2 above to complete the setup.

## Step 3: Enable Email Authentication (Optional)

1. In your Supabase dashboard, go to "Authentication" → "Settings" 
2. Make sure "Enable email confirmations" is turned ON if you want email verification
3. Or turn it OFF if you want to allow immediate registration without email confirmation

## Step 4: Test the Application

Once you've created the missing `journal_entries` table:

1. Your Flask app should be running at the provided URL
2. Try registering a new account
3. The app will automatically create sample Psalm data when you first visit the dashboard
4. You can start using the journaling and prayer features immediately

## Current Status Summary

✅ **Supabase Connection**: Working
✅ **Environment Variables**: All set correctly  
✅ **Required Dependencies**: supabase-py and flask-jwt-extended installed
✅ **Tables Created**: 4/5 tables exist (psalms, markups, prayer_lists, progress)
❌ **Action Needed**: Create journal_entries table using Script 2 above

## Troubleshooting

If you encounter any issues:

1. **Authentication errors**: Check that your SUPABASE_URL, SUPABASE_KEY, and SUPABASE_JWT_SECRET are correctly set
2. **Database errors**: Verify the journal_entries table was created successfully
3. **Permission errors**: Make sure RLS policies are properly created for the journal_entries table

The application should be fully functional once the journal_entries table is created!