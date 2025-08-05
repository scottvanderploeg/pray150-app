"""
Bolls Bible API Integration for Hebrew and Greek Texts
Provides access to Westminster Leningrad Codex (Hebrew) and Septuagint (Greek)
"""

import requests
import logging
from typing import List, Dict, Optional
from functools import lru_cache
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BollsBibleAPI:
    """Bolls Bible API client for fetching Hebrew and Greek texts"""
    
    BASE_URL = "https://bolls.life"
    PSALMS_BOOK_ID = 19
    TIMEOUT = 30
    
    # Available translations from Bolls API for original languages
    ORIGINAL_LANGUAGE_TRANSLATIONS = {
        'WLC': 'Hebrew (Westminster Leningrad Codex)',
        'LXX': 'Greek (Septuagint)'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Pray150-DevotionalApp/1.0',
            'Accept': 'application/json'
        })
    
    def get_available_translations(self) -> Dict[str, str]:
        """Get all available original language translations"""
        return self.ORIGINAL_LANGUAGE_TRANSLATIONS.copy()
    
    @lru_cache(maxsize=300)
    def get_psalm_hebrew(self, psalm_number: int) -> Optional[Dict]:
        """
        Fetch a specific Psalm in Hebrew (Westminster Leningrad Codex)
        
        Args:
            psalm_number: Psalm number (1-150)
            
        Returns:
            Dictionary with psalm data and verses in Hebrew
        """
        return self._get_psalm('WLC', psalm_number)
    
    @lru_cache(maxsize=300) 
    def get_psalm_greek(self, psalm_number: int) -> Optional[Dict]:
        """
        Fetch a specific Psalm in Greek (Septuagint)
        
        Args:
            psalm_number: Psalm number (1-150)
            
        Returns:
            Dictionary with psalm data and verses in Greek
        """
        # Note: Septuagint psalm numbering can differ from Hebrew
        # Some psalms are combined or split differently
        return self._get_psalm('LXX', psalm_number)
    
    def _get_psalm(self, translation: str, psalm_number: int) -> Optional[Dict]:
        """
        Internal method to fetch a psalm in specified translation
        
        Args:
            translation: Translation code (WLC or LXX)
            psalm_number: Psalm number (1-150)
            
        Returns:
            Dictionary with psalm data and verses
        """
        if not (1 <= psalm_number <= 150):
            logger.error(f"Invalid psalm number: {psalm_number}. Must be 1-150.")
            return None
            
        if translation not in self.ORIGINAL_LANGUAGE_TRANSLATIONS:
            logger.error(f"Unknown translation: {translation}. Available: {list(self.ORIGINAL_LANGUAGE_TRANSLATIONS.keys())}")
            return None
        
        try:
            url = f"{self.BASE_URL}/get-text/{translation}/{self.PSALMS_BOOK_ID}/{psalm_number}/"
            
            logger.info(f"Fetching Psalm {psalm_number} ({translation}) from Bolls Bible API...")
            
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            verses_data = response.json()
            
            if not verses_data:
                logger.warning(f"No verses found for Psalm {psalm_number} in {translation}")
                return None
            
            # Format the response to match our standard structure
            psalm_data = {
                'psalm_number': psalm_number,
                'translation': translation,
                'translation_name': self.ORIGINAL_LANGUAGE_TRANSLATIONS[translation],
                'verse_count': len(verses_data),
                'verses': [],
                'language': 'hebrew' if translation == 'WLC' else 'greek',
                'source': 'bolls_bible_api'
            }
            
            for verse in verses_data:
                psalm_data['verses'].append({
                    'verse_number': verse['verse'],
                    'text': verse['text'].strip(),
                    'verse_id': verse['pk']
                })
            
            logger.info(f"Successfully fetched Psalm {psalm_number} ({translation}) with {len(verses_data)} verses")
            return psalm_data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching Psalm {psalm_number} ({translation})")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Psalm {psalm_number} ({translation}): {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching Psalm {psalm_number} ({translation}): {e}")
            return None
    
    def get_psalm_both_languages(self, psalm_number: int) -> Dict[str, Optional[Dict]]:
        """
        Fetch a Psalm in both Hebrew and Greek
        
        Args:
            psalm_number: Psalm number (1-150)
            
        Returns:
            Dictionary with Hebrew and Greek psalm data
        """
        results = {
            'hebrew': self.get_psalm_hebrew(psalm_number),
            'greek': self.get_psalm_greek(psalm_number)
        }
        
        return results

# Global instance
bolls_api = BollsBibleAPI()