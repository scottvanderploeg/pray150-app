"""
API.Bible Integration for NIV 2011 and Additional Translations
This provides access to properly licensed Bible translations including NIV 2011
"""

import requests
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ApiBibleClient:
    """Client for API.Bible service with proper licensing for copyrighted translations"""
    
    BASE_URL = "https://api.scripture.api.bible/v1"
    
    # Bible IDs for API.Bible - NIV 2011 is not available in free tier
    # de4e12af7f28f599-02 is actually KJV, not NIV 2011
    BIBLE_IDS = {
        'ESV': 'f421fe261da7624f-01',        # English Standard Version
        'NLT': 'fd37d8a28e95d3be-01',       # New Living Translation  
        'CSB': 'c315fa9f71d4af3a-01',       # Christian Standard Bible
        'NASB': '1588f89b43ad0f51-01',      # New American Standard Bible
        'KJV': 'de4e12af7f28f599-02'        # King James Version (what we were calling NIV2011)
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize with API key from environment or parameter
        
        Args:
            api_key: API.Bible API key (get from environment if not provided)
        """
        self.api_key = api_key or os.environ.get('API_BIBLE_KEY')
        if not self.api_key:
            logger.warning("No API.Bible API key provided. Some translations may not be available.")
        
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'api-key': self.api_key,
                'accept': 'application/json'
            })
    
    def get_available_bibles(self) -> List[Dict]:
        """Get list of all available Bible translations"""
        if not self.api_key:
            return []
            
        try:
            response = self.session.get(f"{self.BASE_URL}/bibles")
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Error fetching available bibles: {e}")
            return []
    
    def get_psalm(self, psalm_number: int, translation: str = 'ESV') -> Optional[Dict]:
        """
        Fetch psalm from API.Bible with proper verse parsing
        
        Args:
            psalm_number: Psalm number (1-150)
            translation: Translation code (NIV2011, ESV, etc.)
            
        Returns:
            Dictionary with psalm data or None if not found
        """
        if not self.api_key:
            logger.warning("API.Bible requires API key for access")
            return None
            
        bible_id = self.BIBLE_IDS.get(translation)
        if not bible_id:
            logger.error(f"Unknown translation: {translation}")
            return None
            
        # API.Bible uses book.chapter format
        # Psalms is book PSA
        chapter_id = f"PSA.{psalm_number}"
        
        try:
            # First get the verses for this chapter
            url = f"{self.BASE_URL}/bibles/{bible_id}/chapters/{chapter_id}/verses"
            response = self.session.get(url)
            response.raise_for_status()
            
            verses_data = response.json().get('data', [])
            
            if not verses_data:
                logger.warning(f"No verses found for Psalm {psalm_number} in {translation}")
                return None
            
            # Now get the content for each verse
            verses = []
            for verse_data in verses_data:
                verse_id = verse_data.get('id', '')
                verse_url = f"{self.BASE_URL}/bibles/{bible_id}/verses/{verse_id}"
                verse_response = self.session.get(verse_url, params={'content-type': 'text'})
                verse_response.raise_for_status()
                
                verse_content = verse_response.json().get('data', {})
                verse_text = verse_content.get('content', '').strip()
                
                # Extract verse number from the verse reference (e.g., "PSA.1.1" -> 1)
                verse_reference = verse_content.get('reference', '')
                verse_num = verse_reference.split('.')[-1] if '.' in verse_reference else len(verses) + 1
                
                # Clean up the verse text (remove HTML tags, verse numbers, and superscriptions)
                import re
                verse_text = re.sub(r'<[^>]+>', '', verse_text)  # Remove HTML tags
                verse_text = re.sub(r'^\s*\[\d+\]\s*', '', verse_text)  # Remove verse numbers like [1]
                verse_text = re.sub(r'\s+', ' ', verse_text).strip()  # Normalize whitespace
                
                # Skip verses that are superscriptions or contain psalm titles
                verse_reference = verse_content.get('reference', '')
                
                # Skip verse 0 or very short verses (likely superscriptions)
                if '.0' in verse_reference or len(verse_text) < 10:
                    continue
                
                # Remove superscription text that appears at the beginning of verse 1
                if verse_num == '1' and ('psalm of' in verse_text.lower() or 'a song of' in verse_text.lower()):
                    # Find where the actual verse starts (usually after the title and verse number)
                    import re
                    # Look for patterns like "A Psalm of David..." followed by actual verse
                    superscript_match = re.search(r'^[^\.]+\.\s*', verse_text)
                    if superscript_match:
                        verse_text = verse_text[superscript_match.end():].strip()
                    
                    # If still starts with title-like text, try to find the verse content
                    if any(phrase in verse_text.lower() for phrase in ['psalm of', 'song of', 'prayer of', 'maskil of']):
                        # Try to find where verse actually starts (after title and verse marker)
                        parts = verse_text.split('. ')
                        if len(parts) > 1:
                            verse_text = '. '.join(parts[1:])
                
                # Final cleanup - remove any remaining verse numbers in square brackets
                verse_text = re.sub(r'^\s*\[\d+\]\s*', '', verse_text)
                
                verses.append({
                    'verse_number': int(verse_num) if str(verse_num).isdigit() else len(verses) + 1,
                    'text': verse_text,
                    'verse_id': verse_id
                })
            
            return {
                'psalm_number': psalm_number,
                'translation': translation,
                'translation_name': f"{translation} (API.Bible)",
                'verse_count': len(verses),
                'verses': verses,
                'source': 'api.bible'
            }
            
        except Exception as e:
            logger.error(f"Error fetching psalm {psalm_number} ({translation}): {e}")
            return None

def test_api_bible():
    """Test function to check API.Bible access"""
    client = ApiBibleClient()
    
    # Test getting available bibles
    bibles = client.get_available_bibles()
    print(f"Found {len(bibles)} available bibles")
    
    # Look for NIV 2011
    niv_bibles = [b for b in bibles if 'NIV' in b.get('name', '')]
    if niv_bibles:
        print("NIV translations found:")
        for bible in niv_bibles:
            print(f"  - {bible.get('name')}: {bible.get('id')}")
    else:
        print("No NIV translations found")
    
    return bibles

if __name__ == "__main__":
    test_api_bible()