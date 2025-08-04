# Manual Supabase Table Setup

Since the automatic table creation is not working through the API, please create the `user_profiles` table manually in your Supabase dashboard:

## Steps:

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `cqxngpjnwdrpctnbizqc`
3. Go to "SQL Editor" in the left sidebar
4. Run this SQL command:

```sql
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
```

5. Click "Run" to execute the SQL

After creating the table, registration should work properly and display user's first names instead of UUIDs.

## Why this is needed:

The registration form now collects:
- First Name (required)
- Last Name (required) 
- Email (required)
- Password (required)
- Country (optional)
- Zip Code (optional)

This information gets stored in the `user_profiles` table and linked to the Supabase Auth user via the `user_id` field.