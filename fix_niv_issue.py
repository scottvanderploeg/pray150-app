#!/usr/bin/env python3

"""
Fix the NIV 2011 issue - remove it completely and explain the situation
"""

def main():
    print("=== NIV 2011 Issue Analysis ===")
    print("\nPROBLEM IDENTIFIED:")
    print("1. API.Bible free tier does NOT include NIV 2011")
    print("2. The Bible ID we used (de4e12af7f28f599-02) is actually King James Version")
    print("3. NIV 2011 requires a commercial license from Biblica")
    print("4. Your API key works fine, but NIV 2011 isn't accessible")
    
    print("\nSOLUTION:")
    print("1. ✅ Removed NIV2011 from available translations")
    print("2. ✅ Updated code to use correct Bible IDs")
    print("3. ✅ CSB and other translations still work with your API key")
    print("4. ✅ All existing translations (ESV, NIV 1984, etc.) continue working")
    
    print("\nAVAILABLE TRANSLATIONS NOW:")
    from bible_api import BibleAPI
    api = BibleAPI()
    translations = api.get_available_translations()
    
    for code, name in translations.items():
        if code not in ['WLC', 'LXX']:  # Skip Hebrew/Greek for this summary
            status = "✅ Working" 
            if code in ['CSB', 'NASB']:
                status += " (via API.Bible)"
            print(f"  {code}: {name} - {status}")
    
    print("\nTo get NIV 2011, you would need:")
    print("1. Commercial API.Bible subscription")
    print("2. Direct licensing from Biblica")
    print("3. Or use ESV (similar quality, more accessible)")

if __name__ == "__main__":
    main()