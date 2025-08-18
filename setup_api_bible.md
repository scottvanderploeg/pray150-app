# Setting up NIV 2011 and API.Bible Integration

## Overview

Pray150 now supports NIV 2011 and other premium Bible translations through API.Bible integration. This provides access to properly licensed translations while respecting copyright requirements.

## What's Available Now

### Free Translations (Rob Keplin's API)
- ✅ **ESV** - English Standard Version
- ✅ **NIV** - New International Version (1984)
- ✅ **NLT** - New Living Translation
- ✅ **KJV** - King James Version
- ✅ **ASV** - American Standard Version
- ✅ **BBE** - Bible in Basic English
- ✅ **DARBY** - Darby English Bible
- ✅ **WEB** - World English Bible
- ✅ **YLT** - Young's Literal Translation
- ✅ **WLC** - Hebrew (Westminster Leningrad Codex)
- ✅ **LXX** - Greek (Septuagint)

### Premium Translations (API.Bible - Requires API Key)
- 🔑 **NIV2011** - New International Version (2011)
- 🔑 **CSB** - Christian Standard Bible
- 🔑 **NASB** - New American Standard Bible

## How to Enable NIV 2011

### Step 1: Get API.Bible Account
1. Visit https://scripture.api.bible/
2. Sign up for a free account
3. Get your API key from the dashboard

### Step 2: Add API Key to Your Project
Add your API key as an environment variable:
```bash
API_BIBLE_KEY=your_api_key_here
```

### Step 3: Test the Integration
Run the test script to verify everything works:
```bash
python test_niv2011_api.py
```

## Copyright and Licensing

### Important Notes
- **NIV 2011** is copyrighted by Biblica, Inc.
- Free tier allows limited use for non-commercial purposes
- Commercial use requires additional licensing
- Always include proper attribution when using copyrighted translations

### Required Attribution for NIV 2011
```
Scripture quotations taken from The Holy Bible, New International Version® NIV® 
Copyright © 1973, 1978, 1984, 2011 by Biblica, Inc. Used with permission. 
All rights reserved worldwide.
```

## Technical Implementation

### API Integration
- Uses Rob Keplin's API for free translations
- Falls back to API.Bible for premium translations
- Graceful degradation when API keys are not available
- Consistent data format across all sources

### Files Modified
- `bible_api.py` - Added NIV2011 support and API.Bible integration
- `api_bible_integration.py` - New API.Bible client
- `templates/psalm.html` - Updated translation selector
- `test_niv2011_api.py` - Test script for validation

## Usage in the App

### User Experience
- NIV 2011 appears in translation dropdown with asterisk (*)
- Shows "(Requires API Key)" when not configured
- Seamless switching between free and premium translations
- Falls back gracefully if premium translations are unavailable

### Developer Notes
- API.Bible integration is optional - app works without it
- Environment variable `API_BIBLE_KEY` enables premium features
- All translation requests go through the unified `BibleAPI.get_psalm()` method
- Proper error handling and logging throughout

## Future Enhancements

1. **Verse-by-Verse Parsing** - Currently API.Bible returns full chapter text, could be parsed into individual verses
2. **More Translations** - API.Bible supports 200+ translations in various languages
3. **Caching** - Could implement caching for API.Bible responses to reduce API calls
4. **User Preferences** - Save user's preferred translation in their profile

## Support

If you encounter issues:
1. Check your API.Bible account is active
2. Verify the API key is correctly set
3. Review server logs for detailed error messages
4. Use the test script to diagnose problems