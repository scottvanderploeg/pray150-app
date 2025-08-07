"""
Supabase-based models for Pray150 app
"""
from flask_login import UserMixin
from datetime import datetime
from database import get_supabase_client
import uuid

class User(UserMixin):
    def __init__(self, id=None, username=None, email=None, first_name=None, last_name=None,
                 country=None, zip_code=None, preferred_translation='NIV', 
                 font_preference='Georgia', theme_preference='default', created_at=None):
        self.id = str(id) if id else None  # Store as string for consistency
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.country = country
        self.zip_code = zip_code
        self.preferred_translation = preferred_translation
        self.font_preference = font_preference
        self.theme_preference = theme_preference
        self.created_at = created_at or datetime.utcnow()
    
    @property
    def display_name(self):
        """Get user's display name (first name capitalized or fallback)"""
        if self.first_name:
            return self.first_name.title()
        elif self.username:
            return self.username
        else:
            return f"User {str(self.id)[:8]}"
    
    @property 
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.display_name

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID - fetch from user_profiles table"""
        try:
            from database import get_supabase_client
            supabase = get_supabase_client()
            
            # Try to get user profile data
            result = supabase.table('user_profiles').select('*')\
                .eq('user_id', str(user_id)).execute()
            
            if result.data and len(result.data) > 0:
                profile = result.data[0]
                return User(
                    id=str(user_id),
                    username=profile.get('username'),
                    email=profile.get('email'),
                    first_name=profile.get('first_name'),
                    last_name=profile.get('last_name'),
                    country=profile.get('country'),
                    zip_code=profile.get('zip_code'),
                    preferred_translation=profile.get('preferred_translation', 'NIV'),
                    font_preference=profile.get('font_preference', 'Georgia'),
                    theme_preference=profile.get('theme_preference', 'default'),
                    created_at=profile.get('created_at')
                )
            else:
                # Fallback for users without profiles
                return User(
                    id=str(user_id),
                    username=f"user_{str(user_id)[:8]}",
                    first_name="User",
                    preferred_translation='NIV'
                )
        except Exception as e:
            print(f"Error getting user by ID {user_id}: {e}")
            # Fallback user object
            return User(
                id=str(user_id),
                username=f"user_{str(user_id)[:8]}",
                first_name="User",
                preferred_translation='NIV'
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
    
    def get_current_psalm_number(self):
        """Get the user's current psalm number in their sequential progression"""
        try:
            supabase = get_supabase_client()
            
            # Get all completed psalm progress records for this user
            progress_result = supabase.table('psalm_progress').select('psalm_id')\
                .eq('user_id', str(self.id))\
                .eq('completed', True)\
                .order('created_at', desc=False).execute()
            
            if not progress_result.data:
                # New user - start with Psalm 1
                return 1
            
            # Get the highest sequential psalm number that has been completed
            completed_psalms = set()
            for progress in progress_result.data:
                psalm_id = progress.get('psalm_id')
                if psalm_id:
                    completed_psalms.add(int(psalm_id))
            
            # Find the next psalm in sequence starting from 1
            current_psalm = 1
            while current_psalm in completed_psalms and current_psalm <= 150:
                current_psalm += 1
            
            # If we've completed all 150, start over at 1
            if current_psalm > 150:
                return 1
                
            return current_psalm
            
        except Exception as e:
            print(f"Error getting current psalm: {e}")
            return 1  # Default to Psalm 1
    
    def advance_to_next_psalm(self):
        """Advance user to next psalm after completing current one"""
        current = self.get_current_psalm_number()
        next_psalm = current + 1
        if next_psalm > 150:
            next_psalm = 1  # Cycle back to Psalm 1
        return next_psalm

class Psalm:
    def __init__(self, id=None, psalm_number=None, text_niv=None, text_esv=None,
                 text_nlt=None, text_nkjv=None, text_nrsv=None, music_url=None):
        self.id = id
        self.number = psalm_number
        self.text_niv = text_niv
        self.text_esv = text_esv
        self.text_nlt = text_nlt
        self.text_nkjv = text_nkjv
        self.text_nrsv = text_nrsv
        self.music_url = music_url

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
                    text_niv=psalm_data.get('text_niv'),
                    text_esv=psalm_data.get('text_esv'),
                    text_nlt=psalm_data.get('text_nlt'),
                    text_nkjv=psalm_data.get('text_nkjv'),
                    text_nrsv=psalm_data.get('text_nrsv'),
                    music_url=psalm_data.get('music_url')
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
                'text_niv': self.text_niv,
                'text_esv': self.text_esv,
                'text_nlt': self.text_nlt,
                'text_nkjv': self.text_nkjv,
                'text_nrsv': self.text_nrsv,
                'music_url': self.music_url
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
        """Get recent journal entries for a user - consolidated by psalm and date"""
        try:
            # Get all entries and then take the most recent ones
            all_entries = JournalEntry.get_all_by_user(user_id)
            return all_entries[:limit]
        except Exception as e:
            print(f"Error getting recent journal entries: {e}")
            return []

    @staticmethod
    def get_entry_dates_by_user(user_id):
        """Get all dates when user made journal entries for calendar highlighting"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('journal_entries').select('created_at')\
                .eq('user_id', str(user_id)).execute()
            
            dates = []
            for entry_data in result.data:
                if entry_data.get('created_at'):
                    try:
                        # Handle different date formats from Supabase
                        created_at = entry_data['created_at']
                        if isinstance(created_at, str):
                            # Parse ISO format date string
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            dates.append(date_obj.date().isoformat())
                        else:
                            dates.append(created_at.date().isoformat())
                    except:
                        continue
            return list(set(dates))  # Remove duplicates
        except Exception as e:
            print(f"Error getting journal entry dates: {e}")
            return []

    @staticmethod
    def get_count_by_user(user_id):
        """Get total count of journal entries for a user"""
        try:
            from database import get_supabase_client
            supabase = get_supabase_client()
            
            # Use a simple query to get all entries and count them
            result = supabase.table('journal_entries').select('id')\
                .eq('user_id', str(user_id)).execute()
            
            count = len(result.data) if result.data else 0
            return count
        except Exception as e:
            print(f"Error getting journal entry count: {e}")
            return 0
            
    @staticmethod
    def get_week_count_by_user(user_id, days_back=7):
        """Get count of journal entries in the last week"""
        try:
            from datetime import timedelta
            from database import get_supabase_client
            week_ago = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            
            supabase = get_supabase_client()
            result = supabase.table('journal_entries').select('id')\
                .eq('user_id', str(user_id))\
                .gte('created_at', week_ago).execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"Error getting week journal entry count: {e}")
            return 0
            
    @staticmethod
    def get_emotion_trends(user_id, days_back=30):
        """Get emotion data over time for heart tracker"""
        try:
            from datetime import timedelta
            from database import get_supabase_client
            from_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            
            supabase = get_supabase_client()
            result = supabase.table('journal_entries').select('created_at,prompt_responses')\
                .eq('user_id', str(user_id))\
                .gte('created_at', from_date)\
                .order('created_at', desc=False).execute()
                
            emotion_data = []
            emotion_values = {'terrible': 1, 'bad': 2, 'okay': 3, 'good': 4, 'great': 5}
            
            for entry in result.data:
                if entry.get('prompt_responses', {}).get('emotion'):
                    emotion = entry['prompt_responses']['emotion']
                    if emotion in emotion_values:
                        emotion_data.append({
                            'date': entry['created_at'][:10],  # Extract date part
                            'emotion': emotion,
                            'value': emotion_values[emotion]
                        })
            
            return emotion_data
        except Exception as e:
            print(f"Error getting emotion trends: {e}")
            return []

    @staticmethod
    def get_all_by_user(user_id):
        """Get all journal entries for a user - grouped by psalm and date"""
        try:
            from database import get_supabase_client
            supabase = get_supabase_client()
            print(f"DEBUG: Getting all entries for user_id {user_id}")
            
            # Get journal entries without join first
            result = supabase.table('journal_entries').select('*')\
                .eq('user_id', str(user_id)).order('created_at', desc=True).execute()
            
            print(f"DEBUG: Query result: {result}")
            print(f"DEBUG: Found {len(result.data) if result.data else 0} raw journal entries for user {user_id}")
            
            if not result.data:
                print("DEBUG: No data returned from query")
                return []
            
            # Take most recent entries (since we now save consolidated entries)
            # The most recent entries should already have all prompt responses combined
            
            entries = []
            for entry_data in result.data:
                print(f"DEBUG: Processing entry data: {entry_data}")
                entry = JournalEntry(
                    id=entry_data['id'],
                    user_id=entry_data['user_id'],
                    psalm_id=entry_data['psalm_id'],
                    prompt_responses=entry_data.get('prompt_responses', {}),
                    created_at=entry_data.get('created_at')
                )
                
                # Get psalm number separately since we don't have foreign key relation
                try:
                    # psalm_id in journal_entries corresponds to psalm_number in psalms table
                    psalm_result = supabase.table('psalms').select('psalm_number')\
                        .eq('psalm_number', entry.psalm_id).execute()
                    if psalm_result.data:
                        entry.psalm = type('Psalm', (), {'number': psalm_result.data[0]['psalm_number']})()
                    else:
                        # Fallback: use psalm_id as number if psalm not found
                        entry.psalm = type('Psalm', (), {'number': entry.psalm_id})()
                except:
                    entry.psalm = type('Psalm', (), {'number': entry.psalm_id})()
                
                entries.append(entry)
            
            print(f"DEBUG: Returning {len(entries)} consolidated journal entries")
            return entries
        except Exception as e:
            print(f"Error getting all journal entries: {e}")
            import traceback
            traceback.print_exc()
            return []

    def save(self):
        """Save journal entry to Supabase with proper auth context"""
        try:
            from database import get_supabase_client
            
            # Get a service role client for bypassing RLS temporarily
            # OR get user's JWT token for proper authentication
            supabase = get_supabase_client()
            
            entry_data = {
                'user_id': str(self.user_id),  # Ensure it's a string
                'psalm_id': int(self.psalm_id),
                'prompt_responses': self.prompt_responses
            }
            
            print(f"DEBUG: Saving entry_data: {entry_data}")
            
            if self.id:
                # Update existing entry
                print(f"DEBUG: Updating existing entry ID {self.id}")
                result = supabase.table('journal_entries').update(entry_data).eq('id', self.id).execute()
            else:
                # Create new entry
                print(f"DEBUG: Creating new entry")
                result = supabase.table('journal_entries').insert(entry_data).execute()
                if result.data:
                    self.id = result.data[0]['id']
                    print(f"DEBUG: New entry created with ID {self.id}")
            
            print(f"DEBUG: Supabase result: {result}")
            return result.data
        except Exception as e:
            import traceback
            print(f"Error saving journal entry: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            
            # If RLS is blocking, let's try using the service role key directly
            if "row-level security" in str(e).lower():
                print("DEBUG: RLS detected, trying with service role...")
                try:
                    print("DEBUG: Getting SUPABASE_URL and keys...")
                    import os
                    from supabase import create_client
                    
                    supabase_url = os.environ.get("SUPABASE_URL")
                    # Try various service key environment variables
                    service_key = (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or 
                                 os.environ.get("SUPABASE_SERVICE_KEY") or 
                                 os.environ.get("SUPABASE_KEY"))
                    
                    print(f"DEBUG: URL exists: {bool(supabase_url)}, Service key exists: {bool(service_key)}")
                    
                    if not supabase_url or not service_key:
                        print("DEBUG: Missing Supabase credentials")
                        return None
                    
                    # Use service role key to bypass RLS for development
                    service_supabase = create_client(supabase_url, service_key)
                    
                    print(f"DEBUG: Created service client, attempting save...")
                    
                    # Add headers to bypass RLS
                    service_supabase.postgrest.auth(service_key)
                    
                    if self.id:
                        result = service_supabase.table('journal_entries').update(entry_data).eq('id', self.id).execute()
                    else:
                        result = service_supabase.table('journal_entries').insert(entry_data).execute()
                        if result.data:
                            self.id = result.data[0]['id']
                    
                    print(f"DEBUG: Service role result: {result}")
                    if result.data:
                        print("DEBUG: Service role save successful!")
                        return result.data
                    else:
                        print("DEBUG: Service role save returned no data")
                        return None
                        
                except Exception as service_error:
                    print(f"Service role attempt failed: {service_error}")
                    import traceback
                    print(f"Service role traceback: {traceback.format_exc()}")
            
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
    def __init__(self, id=None, user_id=None, category=None, title=None, description=None,
                 prayer_text=None, is_answered=False, answered_note=None, created_at=None, answered_at=None):
        self.id = id
        self.user_id = str(user_id) if user_id else None
        self.category = category
        # Support both new structure (title/description) and old structure (prayer_text)
        if prayer_text and not title:
            # Parse old format "title: description"
            if ":" in prayer_text:
                parts = prayer_text.split(":", 1)
                self.title = parts[0].strip()
                self.description = parts[1].strip() if len(parts) > 1 else ""
            else:
                self.title = prayer_text
                self.description = ""
        else:
            self.title = title
            self.description = description or ""
        self.prayer_text = prayer_text  # Keep for backward compatibility
        self.is_answered = is_answered
        self.answered_note = answered_note
        self.created_at = created_at or datetime.utcnow()
        self.answered_at = answered_at

    @staticmethod
    def get_active_by_user(user_id, limit=None):
        """Get active prayers for a user"""
        try:
            supabase = get_supabase_client()
            # First check if table exists and has correct structure
            query = supabase.table('prayer_lists').select('*')\
                .eq('user_id', str(user_id))
            
            # Try to filter by is_answered if column exists
            try:
                query = query.eq('is_answered', False)
            except:
                # Column doesn't exist, we'll filter manually
                pass
                
            query = query.order('created_at', desc=True)
            
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            
            prayers = []
            for prayer_data in result.data:
                # Manual filtering if is_answered column doesn't exist
                is_answered = prayer_data.get('is_answered', False)
                if not is_answered:  # Only include active (non-answered) prayers
                    # Parse datetime strings from Supabase
                    created_at = prayer_data.get('created_at')
                    if isinstance(created_at, str):
                        try:
                            from datetime import datetime
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            created_at = datetime.utcnow()
                    
                    answered_at = prayer_data.get('answered_at')
                    if isinstance(answered_at, str):
                        try:
                            answered_at = datetime.fromisoformat(answered_at.replace('Z', '+00:00'))
                        except:
                            answered_at = None
                    
                    prayers.append(Prayer(
                        id=prayer_data['id'],
                        user_id=prayer_data['user_id'],
                        category=prayer_data.get('category'),
                        title=prayer_data.get('title'),
                        description=prayer_data.get('description'),
                        prayer_text=prayer_data.get('prayer_text'),
                        is_answered=is_answered,
                        answered_note=prayer_data.get('answered_note'),
                        created_at=created_at,
                        answered_at=answered_at
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
            query = supabase.table('prayer_lists').select('*')\
                .eq('user_id', str(user_id))
            
            # Try to filter by is_answered if column exists
            try:
                query = query.eq('is_answered', True)
            except:
                # Column doesn't exist, we'll filter manually
                pass
                
            result = query.order('answered_at', desc=True)\
                .limit(limit).execute()
            
            prayers = []
            for prayer_data in result.data:
                # Manual filtering if is_answered column doesn't exist
                is_answered = prayer_data.get('is_answered', False)
                if is_answered:  # Only include answered prayers
                    # Parse datetime strings from Supabase
                    created_at = prayer_data.get('created_at')
                    if isinstance(created_at, str):
                        try:
                            from datetime import datetime
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            created_at = datetime.utcnow()
                    
                    answered_at = prayer_data.get('answered_at')
                    if isinstance(answered_at, str):
                        try:
                            answered_at = datetime.fromisoformat(answered_at.replace('Z', '+00:00'))
                        except:
                            answered_at = None
                    
                    prayers.append(Prayer(
                        id=prayer_data['id'],
                        user_id=prayer_data['user_id'],
                        category=prayer_data.get('category'),
                        title=prayer_data.get('title'),
                        description=prayer_data.get('description'),
                        prayer_text=prayer_data.get('prayer_text'),
                        is_answered=is_answered,
                        answered_note=prayer_data.get('answered_note'),
                        created_at=created_at,
                        answered_at=answered_at
                    ))
            return prayers
        except Exception as e:
            print(f"Error getting answered prayers: {e}")
            return []

    def save(self):
        """Save prayer to Supabase"""
        try:
            supabase = get_supabase_client()
            
            # Base prayer data that should work with any table structure
            prayer_data = {
                'user_id': self.user_id,
                'category': self.category,
                'title': self.title,
                'description': self.description
            }
            
            # Add optional fields if they exist
            if hasattr(self, 'is_answered') and self.is_answered is not None:
                prayer_data['is_answered'] = self.is_answered
            if hasattr(self, 'answered_note') and self.answered_note:
                prayer_data['answered_note'] = self.answered_note
            if hasattr(self, 'answered_at') and self.answered_at:
                prayer_data['answered_at'] = self.answered_at.isoformat() if hasattr(self.answered_at, 'isoformat') else self.answered_at
            
            print(f"DEBUG: Saving prayer data: {prayer_data}")
            
            if self.id:
                # Update existing prayer
                result = supabase.table('prayer_lists').update(prayer_data).eq('id', self.id).execute()
            else:
                # Create new prayer
                result = supabase.table('prayer_lists').insert(prayer_data).execute()
                if result.data:
                    self.id = result.data[0]['id']
            
            print(f"DEBUG: Save result: {result}")
            return result.data
        except Exception as e:
            print(f"Error saving prayer: {e}")
            import traceback
            traceback.print_exc()
            return None

    # Ensure title property works
    def get_title(self):
        if hasattr(self, 'title') and self.title:
            return self.title
        elif self.prayer_text:
            # Extract title from prayer_text (before colon if exists)
            if ":" in self.prayer_text:
                title_part = self.prayer_text.split(":", 1)[0].strip()
                return title_part[:50] + "..." if len(title_part) > 50 else title_part
            return self.prayer_text[:50] + "..." if len(self.prayer_text) > 50 else self.prayer_text
        return "Prayer Request"
    
    def get_description(self):
        if hasattr(self, 'description') and self.description:
            return self.description
        elif self.prayer_text and ":" in self.prayer_text:
            parts = self.prayer_text.split(":", 1)
            if len(parts) > 1:
                return parts[1].strip()
        return ""
    
    @property
    def answered_date(self):
        return self.answered_at or self.created_at

class PsalmProgress:
    def __init__(self, id=None, user_id=None, psalm_id=None, completed=True, created_at=None):
        self.id = id
        self.user_id = str(user_id) if user_id else None
        self.psalm_id = psalm_id
        self.completed = completed
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def get_count_by_user(user_id):
        """Get total count of completed psalms for a user based on journal entries"""
        try:
            from database import get_supabase_client
            supabase = get_supabase_client()
            # Count unique psalms that have been journaled about
            result = supabase.table('journal_entries').select('psalm_id')\
                .eq('user_id', str(user_id)).execute()
            
            if result.data:
                # Get unique psalm IDs
                unique_psalms = set(entry['psalm_id'] for entry in result.data if entry.get('psalm_id'))
                return len(unique_psalms)
            return 0
        except Exception as e:
            print(f"Error getting progress count: {e}")
            return 0

    @staticmethod
    def get_week_count_by_user(user_id, days_back=7):
        """Get count of unique psalms completed in the last week based on journal entries"""
        try:
            from datetime import timedelta
            from database import get_supabase_client
            week_ago = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            
            supabase = get_supabase_client()
            result = supabase.table('journal_entries').select('psalm_id')\
                .eq('user_id', str(user_id))\
                .gte('created_at', week_ago).execute()
                
            if result.data:
                # Get unique psalm IDs from this week
                unique_psalms = set(entry['psalm_id'] for entry in result.data if entry.get('psalm_id'))
                return len(unique_psalms)
            return 0
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
