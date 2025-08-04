#!/usr/bin/env python3
"""
Verify Supabase connection and table status for Pray150 app
"""
import os
from database import get_supabase_client, verify_all_tables
from models import Psalm

def main():
    print("🔍 Verifying Supabase Connection for Pray150...")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Environment Variables:")
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY') 
    supabase_jwt = os.environ.get('SUPABASE_JWT_SECRET')
    
    print(f"   SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    print(f"   SUPABASE_KEY: {'✅ Set' if supabase_key else '❌ Missing'}")
    print(f"   SUPABASE_JWT_SECRET: {'✅ Set' if supabase_jwt else '❌ Missing'}")
    
    if supabase_url:
        print(f"   URL: {supabase_url}")
    
    # Test connection
    print("\n2. Connection Test:")
    try:
        supabase = get_supabase_client()
        print("   ✅ Supabase client created successfully")
    except Exception as e:
        print(f"   ❌ Failed to create client: {e}")
        return
    
    # Check tables
    print("\n3. Table Status:")
    existing_tables, missing_tables = verify_all_tables()
    
    for table in ['psalms', 'journal_entries', 'markups', 'prayer_lists', 'progress']:
        if table in existing_tables:
            print(f"   ✅ {table}")
        else:
            print(f"   ❌ {table} - Missing")
    
    # Check psalm data
    print("\n4. Sample Data:")
    try:
        psalm_count = Psalm.get_count()
        print(f"   Psalms in database: {psalm_count}")
        
        if psalm_count > 0:
            psalm_1 = Psalm.get_by_number(1)
            if psalm_1:
                print(f"   ✅ Sample psalm found: Psalm {psalm_1.number}")
            else:
                print("   ⚠️  No sample psalm found")
        else:
            print("   ⚠️  No psalms in database")
            
    except Exception as e:
        print(f"   ❌ Error checking psalms: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    if not missing_tables:
        print("🎉 SUCCESS: All tables exist and connection is working!")
        print("   Your Flask app should be fully functional.")
    else:
        print("⚠️  ACTION NEEDED: Missing tables detected")
        print(f"   Missing: {', '.join(missing_tables)}")
        print("   Please run the SQL scripts from SUPABASE_SETUP.md")
    print("=" * 50)

if __name__ == "__main__":
    main()