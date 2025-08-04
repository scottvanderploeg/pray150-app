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
        self.id = id
        self.username = username
        self.email = email
        self.preferred_translation = preferred_translation
        self.font_preference = font_preference
        self.theme_preference = theme_preference
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID from Supabase"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('users').select('*').eq('id', user_id).execute()
            if result.data:
                user_data = result.data[0]
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    preferred_translation=user_data.get('preferred_translation', 'NIV'),
                    font_preference=user_data.get('font_preference', 'Georgia'),
                    theme_preference=user_data.get('theme_preference', 'default'),
                    created_at=user_data.get('created_at')
                )
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None

    @staticmethod
    def get_by_email(email):
        """Get user by email from Supabase"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('users').select('*').eq('email', email).execute()
            if result.data:
                user_data = result.data[0]
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    preferred_translation=user_data.get('preferred_translation', 'NIV'),
                    font_preference=user_data.get('font_preference', 'Georgia'),
                    theme_preference=user_data.get('theme_preference', 'default'),
                    created_at=user_data.get('created_at')
                )
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def save(self):
        """Save user to Supabase"""
        try:
            supabase = get_supabase_client()
            user_data = {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'preferred_translation': self.preferred_translation,
                'font_preference': self.font_preference,
                'theme_preference': self.theme_preference
            }
            result = supabase.table('users').upsert(user_data).execute()
            return result.data
        except Exception as e:
            print(f"Error saving user: {e}")
            return None

    def update_preferences(self, translation=None, font=None, theme=None):
        """Update user preferences"""
        try:
            supabase = get_supabase_client()
            updates = {}
            if translation:
                updates['preferred_translation'] = translation
                self.preferred_translation = translation
            if font:
                updates['font_preference'] = font
                self.font_preference = font
            if theme:
                updates['theme_preference'] = theme
                self.theme_preference = theme
            
            if updates:
                result = supabase.table('users').update(updates).eq('id', self.id).execute()
                return result.data
            return True
        except Exception as e:
            print(f"Error updating preferences: {e}")
            return False

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
    def __init__(self, id=None, user_id=None, psalm_id=None, prompt_number=None,
                 content=None, is_shared=False, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.psalm_id = psalm_id
        self.prompt_number = prompt_number
        self.content = content
        self.is_shared = is_shared
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @staticmethod
    def get_by_user_and_psalm(user_id, psalm_id):
        """Get journal entries for a user and psalm"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('journal_entries').select('*')\
                .eq('user_id', user_id).eq('psalm_id', psalm_id).execute()
            
            entries = []
            for entry_data in result.data:
                entries.append(JournalEntry(
                    id=entry_data['id'],
                    user_id=entry_data['user_id'],
                    psalm_id=entry_data['psalm_id'],
                    prompt_number=entry_data['prompt_number'],
                    content=entry_data['content'],
                    is_shared=entry_data.get('is_shared', False),
                    created_at=entry_data.get('created_at'),
                    updated_at=entry_data.get('updated_at')
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
                .eq('user_id', user_id).order('updated_at', desc=True).limit(limit).execute()
            
            entries = []
            for entry_data in result.data:
                entry = JournalEntry(
                    id=entry_data['id'],
                    user_id=entry_data['user_id'],
                    psalm_id=entry_data['psalm_id'],
                    prompt_number=entry_data['prompt_number'],
                    content=entry_data['content'],
                    is_shared=entry_data.get('is_shared', False),
                    created_at=entry_data.get('created_at'),
                    updated_at=entry_data.get('updated_at')
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
                'prompt_number': self.prompt_number,
                'content': self.content,
                'is_shared': self.is_shared,
                'updated_at': datetime.utcnow().isoformat()
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

class Prayer:
    def __init__(self, id=None, user_id=None, title=None, description=None, category=None,
                 is_answered=False, answered_date=None, answered_note=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.category = category
        self.is_answered = is_answered
        self.answered_date = answered_date
        self.answered_note = answered_note
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @staticmethod
    def get_active_by_user(user_id, limit=None):
        """Get active prayers for a user"""
        try:
            supabase = get_supabase_client()
            query = supabase.table('prayer_lists').select('*')\
                .eq('user_id', user_id).eq('is_answered', False)\
                .order('created_at', desc=True)
            
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            
            prayers = []
            for prayer_data in result.data:
                prayers.append(Prayer(
                    id=prayer_data['id'],
                    user_id=prayer_data['user_id'],
                    title=prayer_data['title'],
                    description=prayer_data.get('description'),
                    category=prayer_data['category'],
                    is_answered=prayer_data['is_answered'],
                    answered_date=prayer_data.get('answered_date'),
                    answered_note=prayer_data.get('answered_note'),
                    created_at=prayer_data.get('created_at'),
                    updated_at=prayer_data.get('updated_at')
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
                .eq('user_id', user_id).eq('is_answered', True)\
                .order('answered_date', desc=True).limit(limit).execute()
            
            prayers = []
            for prayer_data in result.data:
                prayers.append(Prayer(
                    id=prayer_data['id'],
                    user_id=prayer_data['user_id'],
                    title=prayer_data['title'],
                    description=prayer_data.get('description'),
                    category=prayer_data['category'],
                    is_answered=prayer_data['is_answered'],
                    answered_date=prayer_data.get('answered_date'),
                    answered_note=prayer_data.get('answered_note'),
                    created_at=prayer_data.get('created_at'),
                    updated_at=prayer_data.get('updated_at')
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
                'title': self.title,
                'description': self.description,
                'category': self.category,
                'is_answered': self.is_answered,
                'answered_date': self.answered_date.isoformat() if self.answered_date else None,
                'answered_note': self.answered_note,
                'updated_at': datetime.utcnow().isoformat()
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

class PsalmProgress:
    def __init__(self, id=None, user_id=None, psalm_id=None, completed_date=None,
                 reading_time_minutes=None, journal_completed=False, music_listened=False):
        self.id = id
        self.user_id = user_id
        self.psalm_id = psalm_id
        self.completed_date = completed_date or datetime.utcnow()
        self.reading_time_minutes = reading_time_minutes
        self.journal_completed = journal_completed
        self.music_listened = music_listened

    @staticmethod
    def get_count_by_user(user_id):
        """Get total count of completed psalms for a user"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('progress').select('id', count='exact')\
                .eq('user_id', user_id).execute()
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
                .eq('user_id', user_id).gte('completed_date', week_ago).execute()
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
                'completed_date': self.completed_date.isoformat(),
                'reading_time_minutes': self.reading_time_minutes,
                'journal_completed': self.journal_completed,
                'music_listened': self.music_listened
            }
            
            result = supabase.table('progress').insert(progress_data).execute()
            if result.data:
                self.id = result.data[0]['id']
            return result.data
        except Exception as e:
            print(f"Error saving progress: {e}")
            return None
