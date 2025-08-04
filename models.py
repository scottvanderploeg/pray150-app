"""
Supabase-based models for Pray150 app
"""
from flask_login import UserMixin
from datetime import datetime
from database import get_supabase_client
import uuid

class User(UserMixin):
    def __init__(self, id=None, username=None, email=None, preferred_translation='NIV', 
                 font_preference='Georgia', theme_preference='default', created_at=None):
        self.id = str(id) if id else None  # Store as string for consistency
        self.username = username
        self.email = email
        self.preferred_translation = preferred_translation
        self.font_preference = font_preference
        self.theme_preference = theme_preference
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID - simplified for text-based user_id"""
        # Since we're using Supabase Auth, we create a minimal user object
        return User(
            id=str(user_id),
            username=f"user_{str(user_id)[:8]}",  # Generate username from ID
            email="user@example.com",  # Placeholder - would come from Supabase Auth
            preferred_translation='NIV',
            font_preference='Georgia',
            theme_preference='default'
        )

    @staticmethod
    def get_by_email(email):
        """Get user by email - simplified"""
        # For now, return None as we'll handle auth through Supabase Auth directly
        return None

    def save(self):
        """Save user to Supabase - simplified"""
        return True  # User info is managed by Supabase Auth

    def update_preferences(self, translation=None, font=None, theme=None):
        """Update user preferences - simplified"""
        if translation:
            self.preferred_translation = translation
        if font:
            self.font_preference = font
        if theme:
            self.theme_preference = theme
        return True

class Psalm:
    def __init__(self, id=None, psalm_number=None, title=None, text_niv=None, text_esv=None,
                 text_nlt=None, text_nkjv=None, text_nrsv=None, music_url=None,
                 prompt_1=None, prompt_2=None, prompt_3=None, prompt_4=None):
        self.id = id
        self.number = psalm_number
        self.title = title
        self.text_niv = text_niv
        self.text_esv = text_esv
        self.text_nlt = text_nlt
        self.text_nkjv = text_nkjv
        self.text_nrsv = text_nrsv
        self.youtube_url = music_url  # Keep backward compatibility
        self.prompt_1 = prompt_1
        self.prompt_2 = prompt_2
        self.prompt_3 = prompt_3
        self.prompt_4 = prompt_4

    @staticmethod
    def get_by_number(psalm_number):
        """Get psalm by number from Supabase"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('psalms').select('*').eq('psalm_number', psalm_number).execute()
            if result.data:
                psalm_data = result.data[0]
                return Psalm(
                    id=psalm_data['id'],
                    psalm_number=psalm_data['psalm_number'],
                    title=psalm_data.get('title'),
                    text_niv=psalm_data.get('text_niv'),
                    text_esv=psalm_data.get('text_esv'),
                    text_nlt=psalm_data.get('text_nlt'),
                    text_nkjv=psalm_data.get('text_nkjv'),
                    text_nrsv=psalm_data.get('text_nrsv'),
                    music_url=psalm_data.get('music_url'),
                    prompt_1=psalm_data.get('prompt_1'),
                    prompt_2=psalm_data.get('prompt_2'),
                    prompt_3=psalm_data.get('prompt_3'),
                    prompt_4=psalm_data.get('prompt_4')
                )
            return None
        except Exception as e:
            print(f"Error getting psalm by number: {e}")
            return None

    @staticmethod
    def get_count():
        """Get total count of psalms"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('psalms').select('id', count='exact').execute()
            return result.count or 0
        except Exception as e:
            print(f"Error getting psalm count: {e}")
            return 0

    def save(self):
        """Save psalm to Supabase"""
        try:
            supabase = get_supabase_client()
            psalm_data = {
                'psalm_number': self.number,
                'title': self.title,
                'text_niv': self.text_niv,
                'text_esv': self.text_esv,
                'text_nlt': self.text_nlt,
                'text_nkjv': self.text_nkjv,
                'text_nrsv': self.text_nrsv,
                'music_url': self.youtube_url,
                'prompt_1': self.prompt_1,
                'prompt_2': self.prompt_2,
                'prompt_3': self.prompt_3,
                'prompt_4': self.prompt_4
            }
            result = supabase.table('psalms').insert(psalm_data).execute()
            if result.data:
                self.id = result.data[0]['id']
            return result.data
        except Exception as e:
            print(f"Error saving psalm: {e}")
            return None

class JournalEntry:
    def __init__(self, id=None, user_id=None, psalm_id=None, prompt_responses=None, 
                 created_at=None):
        self.id = id
        self.user_id = str(user_id) if user_id else None
        self.psalm_id = psalm_id
        self.prompt_responses = prompt_responses or {}  # JSONB field
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def get_by_user_and_psalm(user_id, psalm_id):
        """Get journal entries for a user and psalm"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('journal_entries').select('*')\
                .eq('user_id', str(user_id)).eq('psalm_id', psalm_id).execute()
            
            entries = []
            for entry_data in result.data:
                entries.append(JournalEntry(
                    id=entry_data['id'],
                    user_id=entry_data['user_id'],
                    psalm_id=entry_data['psalm_id'],
                    prompt_responses=entry_data.get('prompt_responses', {}),
                    created_at=entry_data.get('created_at')
                ))
            return entries
        except Exception as e:
            print(f"Error getting journal entries: {e}")
            return []

    @staticmethod
    def get_recent_by_user(user_id, limit=3):
        """Get recent journal entries for a user"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('journal_entries').select('*, psalms(psalm_number)')\
                .eq('user_id', str(user_id)).order('created_at', desc=True).limit(limit).execute()
            
            entries = []
            for entry_data in result.data:
                entry = JournalEntry(
                    id=entry_data['id'],
                    user_id=entry_data['user_id'],
                    psalm_id=entry_data['psalm_id'],
                    prompt_responses=entry_data.get('prompt_responses', {}),
                    created_at=entry_data.get('created_at')
                )
                # Add psalm reference for display
                if entry_data.get('psalms'):
                    entry.psalm = type('Psalm', (), {'number': entry_data['psalms']['psalm_number']})()
                entries.append(entry)
            return entries
        except Exception as e:
            print(f"Error getting recent journal entries: {e}")
            return []

    def save(self):
        """Save journal entry to Supabase"""
        try:
            supabase = get_supabase_client()
            entry_data = {
                'user_id': self.user_id,
                'psalm_id': self.psalm_id,
                'prompt_responses': self.prompt_responses
            }
            
            if self.id:
                # Update existing entry
                result = supabase.table('journal_entries').update(entry_data).eq('id', self.id).execute()
            else:
                # Create new entry
                result = supabase.table('journal_entries').insert(entry_data).execute()
                if result.data:
                    self.id = result.data[0]['id']
            
            return result.data
        except Exception as e:
            print(f"Error saving journal entry: {e}")
            return None

    # Helper methods for backward compatibility
    @property
    def prompt_number(self):
        """Backward compatibility - get first prompt number"""
        if self.prompt_responses:
            return min(int(k) for k in self.prompt_responses.keys() if k.isdigit())
        return 1

    @property
    def content(self):
        """Backward compatibility - get first prompt content"""
        if self.prompt_responses:
            first_key = str(self.prompt_number)
            return self.prompt_responses.get(first_key, '')
        return ''

class Prayer:
    def __init__(self, id=None, user_id=None, category=None, prayer_text=None,
                 is_answered=False, created_at=None):
        self.id = id
        self.user_id = str(user_id) if user_id else None
        self.category = category
        self.prayer_text = prayer_text
        self.is_answered = is_answered
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def get_active_by_user(user_id, limit=None):
        """Get active prayers for a user"""
        try:
            supabase = get_supabase_client()
            query = supabase.table('prayer_lists').select('*')\
                .eq('user_id', str(user_id)).eq('is_answered', False)\
                .order('created_at', desc=True)
            
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            
            prayers = []
            for prayer_data in result.data:
                prayers.append(Prayer(
                    id=prayer_data['id'],
                    user_id=prayer_data['user_id'],
                    category=prayer_data.get('category'),
                    prayer_text=prayer_data.get('prayer_text'),
                    is_answered=prayer_data.get('is_answered', False),
                    created_at=prayer_data.get('created_at')
                ))
            return prayers
        except Exception as e:
            print(f"Error getting active prayers: {e}")
            return []

    @staticmethod
    def get_answered_by_user(user_id, limit=10):
        """Get answered prayers for a user"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('prayer_lists').select('*')\
                .eq('user_id', str(user_id)).eq('is_answered', True)\
                .order('created_at', desc=True).limit(limit).execute()
            
            prayers = []
            for prayer_data in result.data:
                prayers.append(Prayer(
                    id=prayer_data['id'],
                    user_id=prayer_data['user_id'],
                    category=prayer_data.get('category'),
                    prayer_text=prayer_data.get('prayer_text'),
                    is_answered=prayer_data.get('is_answered', False),
                    created_at=prayer_data.get('created_at')
                ))
            return prayers
        except Exception as e:
            print(f"Error getting answered prayers: {e}")
            return []

    def save(self):
        """Save prayer to Supabase"""
        try:
            supabase = get_supabase_client()
            prayer_data = {
                'user_id': self.user_id,
                'category': self.category,
                'prayer_text': self.prayer_text,
                'is_answered': self.is_answered
            }
            
            if self.id:
                # Update existing prayer
                result = supabase.table('prayer_lists').update(prayer_data).eq('id', self.id).execute()
            else:
                # Create new prayer
                result = supabase.table('prayer_lists').insert(prayer_data).execute()
                if result.data:
                    self.id = result.data[0]['id']
            
            return result.data
        except Exception as e:
            print(f"Error saving prayer: {e}")
            return None

    # Backward compatibility properties
    @property
    def title(self):
        return self.prayer_text[:50] + "..." if self.prayer_text and len(self.prayer_text) > 50 else self.prayer_text
    
    @property
    def description(self):
        return self.prayer_text

class PsalmProgress:
    def __init__(self, id=None, user_id=None, psalm_id=None, completed=True, created_at=None):
        self.id = id
        self.user_id = str(user_id) if user_id else None
        self.psalm_id = psalm_id
        self.completed = completed
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def get_count_by_user(user_id):
        """Get total count of completed psalms for a user"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('progress').select('id', count='exact')\
                .eq('user_id', str(user_id)).eq('completed', True).execute()
            return result.count or 0
        except Exception as e:
            print(f"Error getting progress count: {e}")
            return 0

    @staticmethod
    def get_week_count_by_user(user_id, days_back=7):
        """Get count of psalms completed in the last week"""
        try:
            from datetime import timedelta
            week_ago = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            
            supabase = get_supabase_client()
            result = supabase.table('progress').select('id', count='exact')\
                .eq('user_id', str(user_id)).eq('completed', True)\
                .gte('created_at', week_ago).execute()
            return result.count or 0
        except Exception as e:
            print(f"Error getting week progress count: {e}")
            return 0

    def save(self):
        """Save progress to Supabase"""
        try:
            supabase = get_supabase_client()
            progress_data = {
                'user_id': self.user_id,
                'psalm_id': self.psalm_id,
                'completed': self.completed
            }
            
            result = supabase.table('progress').insert(progress_data).execute()
            if result.data:
                self.id = result.data[0]['id']
            return result.data
        except Exception as e:
            print(f"Error saving progress: {e}")
            return None
