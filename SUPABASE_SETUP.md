# Supabase Prayer Table Setup

The prayer_lists table needs to be created with the correct structure. Please run this SQL in your Supabase dashboard:

## SQL Commands to Run:

```sql
-- Create prayer_lists table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.prayer_lists (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    category TEXT,
    prayer_text TEXT,
    is_answered BOOLEAN DEFAULT FALSE,
    answered_note TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    answered_at TIMESTAMPTZ
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_prayer_lists_user_id ON public.prayer_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_prayer_lists_is_answered ON public.prayer_lists(is_answered);
```

## Alternative: If table exists but has wrong columns:

```sql
-- Check current structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'prayer_lists' AND table_schema = 'public';

-- Add missing columns if needed
ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS is_answered BOOLEAN DEFAULT FALSE;
ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS answered_note TEXT;
ALTER TABLE public.prayer_lists ADD COLUMN IF NOT EXISTS answered_at TIMESTAMPTZ;
```

## Row Level Security (Optional):

```sql
-- Enable RLS
ALTER TABLE public.prayer_lists ENABLE ROW LEVEL SECURITY;

-- Create policy for users to see only their own prayers
CREATE POLICY "Users can view own prayers" ON public.prayer_lists
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own prayers" ON public.prayer_lists
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own prayers" ON public.prayer_lists
    FOR UPDATE USING (auth.uid()::text = user_id);
```