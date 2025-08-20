#!/usr/bin/env python3
"""
Script to set admin privileges for users in the Pray150 app.
Run this script to grant admin access to specific email addresses.

Usage:
    python set_admin.py your-email@example.com

This will add the email to the ADMIN_EMAILS environment variable.
"""

import os
import sys

def set_admin_emails(email_to_add=None):
    """Set or update admin emails in environment"""
    
    current_admins = os.environ.get('ADMIN_EMAILS', '')
    admin_list = [email.strip() for email in current_admins.split(',') if email.strip()]
    
    if email_to_add:
        if email_to_add not in admin_list:
            admin_list.append(email_to_add)
            print(f"✓ Added {email_to_add} to admin list")
        else:
            print(f"✓ {email_to_add} is already an admin")
    
    # Show current admin list
    if admin_list:
        print(f"\nCurrent admin emails:")
        for i, email in enumerate(admin_list, 1):
            print(f"  {i}. {email}")
    else:
        print("\nNo admin emails currently set.")
    
    # Instructions for setting in Replit
    print(f"\n" + "="*60)
    print("To set these admin emails in Replit:")
    print("="*60)
    print("1. Go to your Replit project")
    print("2. Click on 'Secrets' tab (lock icon in sidebar)")
    print("3. Add or update the secret:")
    print(f"   Key: ADMIN_EMAILS")
    print(f"   Value: {','.join(admin_list)}")
    print("4. Restart your application")
    print("="*60)
    
    return admin_list

if __name__ == '__main__':
    if len(sys.argv) > 1:
        email = sys.argv[1]
        if '@' not in email:
            print("Error: Please provide a valid email address")
            sys.exit(1)
        set_admin_emails(email)
    else:
        print("Usage: python set_admin.py <email@example.com>")
        print("\nThis script helps you set admin privileges for the Pray150 admin panel.")
        set_admin_emails()  # Show current status