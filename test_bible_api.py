"""
Test script for Bible API integration
"""

from bible_api import bible_api, get_psalm, get_daily_psalm, get_available_translations
import datetime

def test_bible_api():
    print("Testing Bible API Integration for Pray150\n")
    
    # Test available translations
    print("1. Available Translations:")
    translations = get_available_translations()
    for code, name in translations.items():
        print(f"   {code}: {name}")
    print()
    
    # Test single psalm fetch
    print("2. Fetching Psalm 23 (ESV):")
    psalm_23 = get_psalm(23, 'ESV')
    if psalm_23:
        print(f"   Psalm {psalm_23['psalm_number']} ({psalm_23['translation_name']})")
        print(f"   Verses: {psalm_23['verse_count']}")
        for verse in psalm_23['verses'][:3]:  # Show first 3 verses
            print(f"   {verse['verse_number']}: {verse['text']}")
        print("   ...")
    print()
    
    # Test different translation
    print("3. Fetching Psalm 1 (NIV):")
    psalm_1 = get_psalm(1, 'NIV')
    if psalm_1:
        print(f"   Psalm {psalm_1['psalm_number']} ({psalm_1['translation_name']})")
        print(f"   Verse 1: {psalm_1['verses'][0]['text']}")
    print()
    
    # Test daily psalm
    print("4. Today's Psalm:")
    today = datetime.datetime.now()
    day_of_year = today.timetuple().tm_yday
    daily_psalm = get_daily_psalm(day_of_year, 'ESV')
    if daily_psalm:
        print(f"   Day {day_of_year} → Psalm {daily_psalm['psalm_number']}")
        print(f"   First verse: {daily_psalm['verses'][0]['text']}")
    print()
    
    # Test multiple translations
    print("5. Psalm 150 in multiple translations:")
    psalm_150_multi = bible_api.get_psalm_multiple_translations(150, ['ESV', 'NIV', 'KJV'])
    for translation, data in psalm_150_multi.items():
        print(f"   {translation}: {data['verses'][0]['text']}")
    print()
    
    # Test search
    print("6. Searching for 'shepherd':")
    search_results = bible_api.search_psalms('shepherd', limit=3)
    for result in search_results:
        print(f"   Psalm {result['psalm_number']}:{result['verse_number']} - {result['text'][:100]}...")
    print()
    
    print("Bible API integration test completed successfully!")

if __name__ == "__main__":
    test_bible_api()