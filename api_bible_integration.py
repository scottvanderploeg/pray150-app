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
    
    # Bible IDs for API.Bible (these need to be obtained from their service)
    BIBLE_IDS = {
        'NIV2011': 'de4e12af7f28f599-02',  # NIV 2011 (requires licensing)
        'ESV': 'f421fe261da7624f-01',        # English Standard Version
        'NLT': 'fd37d8a28e95d3be-01',       # New Living Translation  
        'CSB': 'c315fa9f71d4af3a-01',       # Christian Standard Bible
        'NASB': '1588f89b43ad0f51-01'       # New American Standard Bible
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
        Fetch psalm from API.Bible
        
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
            url = f"{self.BASE_URL}/bibles/{bible_id}/chapters/{chapter_id}"
            response = self.session.get(url, params={'content-type': 'text'})
            response.raise_for_status()
            
            data = response.json().get('data', {})
            
            # Parse the content to extract verses
            content = data.get('content', '')
            
            return {
                'psalm_number': psalm_number,
                'translation': translation,
                'translation_name': f"{translation} (API.Bible)",
                'content': content,
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