"""
Bible API Integration for Pray150
Uses Rob Keplin's Bible API to fetch all 150 Psalms with multiple translations
Includes psalm superscripts/inscriptions for complete biblical context
"""

import requests
import logging
import os
from typing import List, Dict, Optional
from functools import lru_cache
import time
from psalm_superscripts import get_psalm_superscript
from bolls_bible_api import bolls_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BibleAPI:
    """Bible API client for fetching Psalms from Rob Keplin's API"""
    
    BASE_URL = "https://bible-go-api.rkeplin.com/v1"
    PSALMS_BOOK_ID = 19
    TIMEOUT = 30
    
    # Available translations from the API (ordered by preference)
    AVAILABLE_TRANSLATIONS = {
        'NIV': 'New International Version (1984)',
        'ESV': 'English Standard Version',
        'NLT': 'New Living Translation',
        'KJV': 'King James Version',
        'CSB': 'Christian Standard Bible',
        'NASB': 'New American Standard Bible',
        'ASV': 'American Standard-ASV1901',
        'BBE': 'Bible in Basic English',
        'DARBY': 'Darby English Bible',
        'WEB': 'World English Bible',
        'YLT': "Young's Literal Translation",
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
        """Get all available Bible translations"""
        return self.AVAILABLE_TRANSLATIONS.copy()
    
    @lru_cache(maxsize=1000)
    def get_psalm(self, psalm_number: int, translation: str = 'ESV') -> Optional[Dict]:
        """
        Fetch a specific Psalm with verses
        
        Args:
            psalm_number: Psalm number (1-150)
            translation: Bible translation code (ESV, NIV, etc.)
            
        Returns:
            Dictionary with psalm data and verses
        """
        if not (1 <= psalm_number <= 150):
            logger.error(f"Invalid psalm number: {psalm_number}. Must be 1-150.")
            return None
            
        if translation not in self.AVAILABLE_TRANSLATIONS:
            logger.warning(f"Unknown translation: {translation}. Using ESV as fallback.")
            translation = 'ESV'
        
        # Check if this is a Hebrew or Greek translation
        if translation in ['WLC', 'LXX']:
            return self._get_original_language_psalm(translation, psalm_number)
        
        # RapidAPI NIV service removed - was providing NIV 1984 text, not NIV 2011
        
        # Check if this is a translation that requires API.Bible access
        if translation in ['CSB', 'NASB']:
            return self._get_api_bible_psalm(translation, psalm_number)
        
        try:
            url = f"{self.BASE_URL}/books/{self.PSALMS_BOOK_ID}/chapters/{psalm_number}"
            params = {'translation': translation}
            
            logger.info(f"Fetching Psalm {psalm_number} ({translation}) from Bible API...")
            
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            verses_data = response.json()
            
            if not verses_data:
                logger.warning(f"No verses found for Psalm {psalm_number} in {translation}")
                return None
            
            # Add superscript/inscription if available
            superscript = get_psalm_superscript(psalm_number)
            
            # Format the response
            psalm_data = {
                'psalm_number': psalm_number,
                'translation': translation,
                'translation_name': self.AVAILABLE_TRANSLATIONS.get(translation, translation),
                'verse_count': len(verses_data),
                'verses': [],
                'superscript': superscript
            }
            
            for verse in verses_data:
                psalm_data['verses'].append({
                    'verse_number': verse['verseId'],
                    'text': verse['verse'].strip(),
                    'verse_id': verse['id']
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
    
    def _get_api_bible_psalm(self, translation: str, psalm_number: int) -> Optional[Dict]:
        """
        Get psalm from API.Bible for licensed translations like NIV 2011
        
        Args:
            translation: Translation code (NIV2011, CSB, NASB)
            psalm_number: Psalm number (1-150)
            
        Returns:
            Psalm data or None if not available
        """
        try:
            from api_bible_integration import ApiBibleClient
            
            client = ApiBibleClient()
            result = client.get_psalm(psalm_number, translation)
            
            if result:
                # API.Bible already returns properly parsed verses
                psalm_data = {
                    'psalm_number': psalm_number,
                    'translation': translation,
                    'translation_name': self.AVAILABLE_TRANSLATIONS.get(translation, translation),
                    'verse_count': result.get('verse_count', len(result.get('verses', []))),
                    'verses': result.get('verses', []),
                    'superscript': get_psalm_superscript(psalm_number),
                    'source': 'api.bible'
                }
                
                logger.info(f"Successfully fetched Psalm {psalm_number} ({translation}) from API.Bible")
                return psalm_data
            else:
                logger.warning(f"Could not fetch Psalm {psalm_number} ({translation}) from API.Bible")
                return None
                
        except ImportError:
            logger.error("API.Bible integration not available")
            return None
        except Exception as e:
            logger.error(f"Error fetching Psalm {psalm_number} ({translation}) from API.Bible: {e}")
            return None
    
    def _get_rapidapi_niv_psalm(self, psalm_number: int) -> Optional[Dict]:
        """
        Get psalm from RapidAPI NIV 2011 service
        
        Args:
            psalm_number: Psalm number (1-150)
            
        Returns:
            Psalm data or None if not available
        """
        try:
            rapidapi_key = os.environ.get('RAPIDAPI_NIV_KEY')
            if not rapidapi_key:
                logger.error("RAPIDAPI_NIV_KEY not found in environment variables")
                return None
            
            # RapidAPI NIV 2011 endpoint
            url = "https://niv-bible.p.rapidapi.com/row"
            headers = {
                'x-rapidapi-host': 'niv-bible.p.rapidapi.com',
                'x-rapidapi-key': rapidapi_key
            }
            
            # Get the entire psalm chapter
            # The API requires individual verse requests, so we'll fetch all verses for the psalm
            verses = []
            verse_number = 1
            max_verses = 200  # Safety limit
            consecutive_empty = 0  # Track consecutive empty responses
            
            while verse_number <= max_verses:
                params = {
                    'Book': 'Psalms',
                    'Chapter': str(psalm_number),
                    'Verse': str(verse_number)
                }
                
                response = self.session.get(url, params=params, headers=headers, timeout=self.TIMEOUT)
                
                if response.status_code == 404:
                    consecutive_empty += 1
                    if consecutive_empty >= 3:  # Stop after 3 consecutive 404s
                        break
                    verse_number += 1
                    continue
                elif response.status_code != 200:
                    logger.error(f"RapidAPI error {response.status_code} for Psalm {psalm_number}:{verse_number}")
                    consecutive_empty += 1
                    if consecutive_empty >= 3:
                        break
                    verse_number += 1
                    continue
                
                try:
                    data = response.json()
                    if data and 'Text' in data:
                        # Extract the verse text from the Text field
                        text_data = data['Text']
                        if isinstance(text_data, dict):
                            # Get the first (and likely only) value from the dict
                            verse_text = list(text_data.values())[0] if text_data else ""
                        else:
                            verse_text = str(text_data)
                        
                        if verse_text:
                            # Clean up special characters and formatting issues
                            cleaned_text = verse_text.strip()
                            
                            # Remove backslashes and number sequences that appear to be formatting artifacts
                            import re
                            cleaned_text = re.sub(r'\\+["\n]*\s*\d+,\d+,\d+,?', '', cleaned_text)
                            cleaned_text = re.sub(r'\\+["\n]*', '', cleaned_text)
                            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                            
                            # Only add if there's meaningful text after cleaning
                            if len(cleaned_text) > 10:  # Ensure it's not just artifacts
                                verses.append({
                                    'verse_number': verse_number,
                                    'text': cleaned_text,
                                    'verse_id': f"{psalm_number}:{verse_number}"
                                })
                                consecutive_empty = 0  # Reset counter on successful verse
                            verse_number += 1
                        else:
                            consecutive_empty += 1
                            if consecutive_empty >= 3:
                                break
                            verse_number += 1
                    else:
                        consecutive_empty += 1
                        if consecutive_empty >= 3:
                            break
                        verse_number += 1
                except (ValueError, KeyError) as e:
                    logger.error(f"Error parsing RapidAPI response for Psalm {psalm_number}:{verse_number}: {e}")
                    consecutive_empty += 1
                    if consecutive_empty >= 3:
                        break
                    verse_number += 1
            
            if not verses:
                logger.warning(f"No verses found for Psalm {psalm_number} in NIV 2011")
                return None
            
            # Format the response
            psalm_data = {
                'psalm_number': psalm_number,
                'translation': 'NIV2011',
                'translation_name': 'New International Version (2011)',
                'verse_count': len(verses),
                'verses': verses,
                'superscript': get_psalm_superscript(psalm_number),
                'source': 'rapidapi-niv'
            }
            
            logger.info(f"Successfully fetched Psalm {psalm_number} (NIV 2011) with {len(verses)} verses from RapidAPI")
            return psalm_data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching Psalm {psalm_number} (NIV 2011) from RapidAPI")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Psalm {psalm_number} (NIV 2011) from RapidAPI: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching Psalm {psalm_number} (NIV 2011) from RapidAPI: {e}")
            return None
    
    def _get_original_language_psalm(self, translation: str, psalm_number: int) -> Optional[Dict]:
        """
        Fetch a psalm in Hebrew or Greek using Bolls Bible API
        
        Args:
            translation: WLC (Hebrew) or LXX (Greek)
            psalm_number: Psalm number (1-150)
            
        Returns:
            Dictionary with psalm data from Bolls API
        """
        try:
            if translation == 'WLC':
                psalm_data = bolls_api.get_psalm_hebrew(psalm_number)
            elif translation == 'LXX':
                psalm_data = bolls_api.get_psalm_greek(psalm_number)
            else:
                return None
            
            if psalm_data:
                # Add superscript for consistency (only applies to Hebrew, but keeping structure consistent)
                superscript = get_psalm_superscript(psalm_number) if translation == 'WLC' else None
                psalm_data['superscript'] = superscript
                
                # Update translation name to match our format
                psalm_data['translation_name'] = self.AVAILABLE_TRANSLATIONS[translation]
                
            return psalm_data
            
        except Exception as e:
            logger.error(f"Error fetching original language psalm {psalm_number} ({translation}): {e}")
            return None
    
    def get_psalm_multiple_translations(self, psalm_number: int, translations: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Fetch a Psalm in multiple translations
        
        Args:
            psalm_number: Psalm number (1-150)
            translations: List of translation codes (default: ESV, NIV, NLT)
            
        Returns:
            Dictionary with translation codes as keys and psalm data as values
        """
        if translations is None:
            translations = ['ESV', 'NIV', 'NLT']
        
        results = {}
        for translation in translations:
            psalm_data = self.get_psalm(psalm_number, translation)
            if psalm_data:
                results[translation] = psalm_data
            else:
                logger.warning(f"Failed to fetch Psalm {psalm_number} in {translation}")
        
        return results
    
    def get_daily_psalm(self, day_of_year: int, translation: str = 'ESV') -> Optional[Dict]:
        """
        Get the daily Psalm based on day of year (cycles through all 150 Psalms)
        
        Args:
            day_of_year: Day of year (1-365/366)
            translation: Bible translation code
            
        Returns:
            Psalm data for the day
        """
        # Cycle through all 150 Psalms
        psalm_number = ((day_of_year - 1) % 150) + 1
        
        logger.info(f"Day {day_of_year} corresponds to Psalm {psalm_number}")
        return self.get_psalm(psalm_number, translation)
    
    def search_psalms(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for verses in Psalms containing specific text
        
        Args:
            query: Search term
            limit: Maximum number of results
            
        Returns:
            List of matching verses
        """
        try:
            url = f"{self.BASE_URL}/search"
            params = {
                'query': f"psalms {query}",
                'limit': limit
            }
            
            logger.info(f"Searching Psalms for: '{query}'")
            
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            search_results = response.json()
            
            # Filter results to only include Psalms (book id 19)
            psalm_results = []
            for result in search_results:
                # Handle both dict and object responses
                if isinstance(result, dict):
                    book_info = result.get('book', {})
                    book_id = book_info.get('id') if isinstance(book_info, dict) else getattr(book_info, 'id', None)
                else:
                    book_id = getattr(getattr(result, 'book', None), 'id', None)
                
                if book_id == self.PSALMS_BOOK_ID:
                    psalm_results.append({
                        'psalm_number': getattr(result, 'chapterId', result.get('chapterId')) if hasattr(result, 'chapterId') else result.get('chapterId'),
                        'verse_number': getattr(result, 'verseId', result.get('verseId')) if hasattr(result, 'verseId') else result.get('verseId'),
                        'text': ((getattr(result, 'verse', result.get('verse')) if hasattr(result, 'verse') else result.get('verse', '')) or '').strip(),
                        'verse_id': getattr(result, 'id', result.get('id')) if hasattr(result, 'id') else result.get('id')
                    })
            
            logger.info(f"Found {len(psalm_results)} matching verses in Psalms")
            return psalm_results
            
        except Exception as e:
            logger.error(f"Error searching Psalms: {e}")
            return []
    
    def validate_psalm_number(self, psalm_number: int) -> bool:
        """Validate if psalm number is within valid range"""
        return 1 <= psalm_number <= 150
    
    def get_psalm_range(self, start_psalm: int, end_psalm: int, translation: str = 'ESV') -> Dict[int, Dict]:
        """
        Fetch multiple consecutive Psalms
        
        Args:
            start_psalm: Starting Psalm number
            end_psalm: Ending Psalm number (inclusive)
            translation: Bible translation code
            
        Returns:
            Dictionary with psalm numbers as keys and psalm data as values
        """
        if not (1 <= start_psalm <= end_psalm <= 150):
            logger.error(f"Invalid psalm range: {start_psalm}-{end_psalm}")
            return {}
        
        results = {}
        for psalm_num in range(start_psalm, end_psalm + 1):
            psalm_data = self.get_psalm(psalm_num, translation)
            if psalm_data:
                results[psalm_num] = psalm_data
            # Add small delay to be respectful to the API
            time.sleep(0.1)
        
        return results


# Global Bible API instance for use across the application
bible_api = BibleAPI()


# Convenience functions for easy integration
def get_psalm(psalm_number: int, translation: str = 'ESV') -> Optional[Dict]:
    """Get a single Psalm"""
    return bible_api.get_psalm(psalm_number, translation)


def get_daily_psalm(day_of_year: int, translation: str = 'ESV') -> Optional[Dict]:
    """Get today's Psalm based on day of year"""
    return bible_api.get_daily_psalm(day_of_year, translation)


def get_available_translations() -> Dict[str, str]:
    """Get available Bible translations"""
    return bible_api.get_available_translations()


def search_psalms(query: str, limit: int = 10) -> List[Dict]:
    """Search Psalms for specific text"""
    return bible_api.search_psalms(query, limit)