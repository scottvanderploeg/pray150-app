#!/usr/bin/env python3

"""
Test script to validate NIV 2011 API integration
"""

import os
import sys
sys.path.append('.')

from bible_api import BibleAPI

def test_niv2011_integration():
    """Test NIV 2011 integration without requiring actual API key"""
    
    print("=== Testing NIV 2011 API Integration ===")
    
    # Initialize Bible API
    api = BibleAPI()
    
    # Check available translations
    print("\nAvailable translations:")
    translations = api.get_available_translations()
    for code, name in translations.items():
        print(f"  {code}: {name}")
    
    # Test current NIV (1984) - should work
    print("\n--- Testing NIV 1984 (current) ---")
    psalm_niv = api.get_psalm(1, 'NIV')
    if psalm_niv:
        print(f"✓ NIV 1984 working: {len(psalm_niv['verses'])} verses")
        print(f"  First verse: {psalm_niv['verses'][0]['text'][:80]}...")
    else:
        print("✗ NIV 1984 failed")
    
    # Test NIV 2011 - will show what happens without API key
    print("\n--- Testing NIV 2011 (requires API.Bible) ---")
    psalm_niv2011 = api.get_psalm(1, 'NIV2011')
    if psalm_niv2011:
        print(f"✓ NIV 2011 working: {psalm_niv2011.get('verse_count', 'unknown')} verses")
        if psalm_niv2011.get('verses'):
            print(f"  First verse: {psalm_niv2011['verses'][0]['text'][:80]}...")
    else:
        print("✗ NIV 2011 not available (likely needs API.Bible key)")
    
    # Test other new translations
    print("\n--- Testing additional translations ---")
    for translation in ['CSB', 'NASB']:
        psalm_data = api.get_psalm(1, translation)
        if psalm_data:
            print(f"✓ {translation} working")
        else:
            print(f"✗ {translation} not available")
    
    print("\n=== Summary ===")
    print("To enable NIV 2011, you need:")
    print("1. Sign up at https://scripture.api.bible/")
    print("2. Get a free API key")
    print("3. Set API_BIBLE_KEY environment variable")
    print("4. Note: NIV 2011 may require commercial licensing for production use")
    
    return True

if __name__ == "__main__":
    test_niv2011_integration()