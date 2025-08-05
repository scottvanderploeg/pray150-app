from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Psalm, JournalEntry, Prayer, PsalmProgress, User
from psalm_data import initialize_psalms
from datetime import datetime, timedelta
from database import get_supabase_client
from bible_api import bible_api, get_psalm, get_daily_psalm, get_available_translations

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Initialize psalms if needed
    psalm_count = Psalm.get_count()
    if psalm_count == 0:
        initialize_psalms()
        psalm_count = Psalm.get_count()
    
    # Calculate today's psalm based on day of year (cycles through all 150 Psalms)
    today = datetime.now()
    day_of_year = today.timetuple().tm_yday
    todays_psalm_number = ((day_of_year - 1) % 150) + 1
    
    # Get user's preferred translation
    user_translation = current_user.preferred_translation if hasattr(current_user, 'preferred_translation') else 'ESV'
    
    # Fetch today's psalm from Bible API
    todays_psalm_api = get_daily_psalm(day_of_year, user_translation)
    
    # Get local psalm data for backward compatibility
    todays_psalm = Psalm.get_by_number(todays_psalm_number)
    
    # Get recent journal entries
    recent_entries = JournalEntry.get_recent_by_user(current_user.id, limit=3)
    
    # Get active prayers
    active_prayers = Prayer.get_active_by_user(current_user.id, limit=5)
    
    # Get progress summary
    total_psalms_read = PsalmProgress.get_count_by_user(current_user.id)
    psalms_this_week = PsalmProgress.get_week_count_by_user(current_user.id)
    total_journal_entries = JournalEntry.get_count_by_user(current_user.id)
    print(f"DEBUG: Dashboard - total_journal_entries = {total_journal_entries}")
    
    # Get dates with journal entries for calendar highlighting
    journal_dates = JournalEntry.get_entry_dates_by_user(current_user.id)
    
    return render_template('dashboard.html',
                         todays_psalm=todays_psalm,
                         todays_psalm_api=todays_psalm_api,
                         todays_psalm_number=todays_psalm_number,
                         user_translation=user_translation,
                         recent_entries=recent_entries,
                         active_prayers=active_prayers,
                         total_psalms_read=total_psalms_read,
                         psalms_this_week=psalms_this_week,
                         total_journal_entries=total_journal_entries,
                         journal_dates=journal_dates)

@main_bp.route('/journal-history')
@login_required
def journal_history():
    """Display all journal entries with search and filter capabilities"""
    # Get search parameters
    search_psalm = request.args.get('psalm', type=int)
    search_date = request.args.get('date')
    search_text = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 12  # entries per page
    
    # Get all journal entries for the user
    all_entries = JournalEntry.get_all_by_user(current_user.id)
    print(f"DEBUG: Journal history - found {len(all_entries)} total entries for user {current_user.id}")
    
    # Apply filters
    filtered_entries = all_entries
    
    # Filter by psalm number
    if search_psalm:
        filtered_entries = [entry for entry in filtered_entries if entry.psalm_id == search_psalm]
    
    # Filter by date
    if search_date:
        try:
            filter_date = datetime.strptime(search_date, '%Y-%m-%d').date()
            filtered_entries = [entry for entry in filtered_entries 
                              if entry.created_at and 
                              datetime.fromisoformat(entry.created_at.replace('Z', '+00:00')).date() == filter_date]
        except (ValueError, AttributeError):
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
    
    # Filter by text content
    if search_text:
        search_lower = search_text.lower()
        filtered_entries = [entry for entry in filtered_entries 
                          if any(search_lower in str(response).lower() 
                                for response in entry.prompt_responses.values())]
    
    # Sort by creation date (newest first) - handle string dates from Supabase
    def get_sort_date(entry):
        try:
            if isinstance(entry.created_at, str):
                return datetime.fromisoformat(entry.created_at.replace('Z', '+00:00'))
            return entry.created_at or datetime.min
        except:
            return datetime.min
    
    filtered_entries.sort(key=get_sort_date, reverse=True)
    
    # Calculate pagination
    total = len(filtered_entries)
    start = (page - 1) * per_page
    end = start + per_page
    entries = filtered_entries[start:end]
    
    # Calculate pagination info
    has_prev = page > 1
    has_next = end < total
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    
    # Get dates with journal entries for calendar highlighting
    journal_dates = JournalEntry.get_entry_dates_by_user(current_user.id)
    
    return render_template('journal_history.html', 
                         entries=entries,
                         total=total,
                         page=page,
                         per_page=per_page,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_num=prev_num,
                         next_num=next_num,
                         search_psalm=search_psalm,
                         search_date=search_date,
                         search_text=search_text,
                         journal_dates=journal_dates)

@main_bp.route('/api/psalms/<int:number>')
def api_get_psalm(number):
    """API endpoint to retrieve psalm data by number from Bible API"""
    try:
        # Get translation preference from query parameter
        translation = request.args.get('translation', 'ESV').upper()
        
        # Validate psalm number
        if not (1 <= number <= 150):
            return jsonify({
                'success': False,
                'error': 'Invalid psalm number. Must be between 1 and 150.'
            }), 400
        
        # Fetch from Bible API
        psalm_data = get_psalm(number, translation)
        
        if psalm_data:
            return jsonify({
                'success': True,
                'data': psalm_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Psalm not found or API error'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/psalms/<int:number>/multiple-translations')
def api_get_psalm_multiple_translations(number):
    """API endpoint to get psalm in multiple translations"""
    try:
        # Validate psalm number
        if not (1 <= number <= 150):
            return jsonify({
                'success': False,
                'error': 'Invalid psalm number. Must be between 1 and 150.'
            }), 400
        
        # Get requested translations from query param (default: ESV, NIV, NLT)
        translations_param = request.args.get('translations', 'ESV,NIV,NLT')
        translations = [t.strip().upper() for t in translations_param.split(',')]
        
        # Fetch psalm in multiple translations
        psalm_data = bible_api.get_psalm_multiple_translations(number, translations)
        
        if psalm_data:
            return jsonify({
                'success': True,
                'data': psalm_data,
                'psalm_number': number,
                'translations_count': len(psalm_data)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No psalm data found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/translations')
def api_get_translations():
    """API endpoint to get available Bible translations"""
    try:
        translations = get_available_translations()
        return jsonify({
            'success': True,
            'data': translations,
            'count': len(translations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/search/psalms')
def api_search_psalms():
    """API endpoint to search psalms"""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        results = bible_api.search_psalms(query, limit)
        
        return jsonify({
            'success': True,
            'data': results,
            'query': query,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/bible-api-demo')
def bible_api_demo():
    """Demo page to showcase Bible API integration"""
    return render_template('bible_api_demo.html',
                         available_translations=get_available_translations())

@main_bp.route('/psalm/<int:psalm_number>')
@login_required
def psalm(psalm_number):
    # Validate psalm number
    if not (1 <= psalm_number <= 150):
        flash('Invalid psalm number. Please choose a psalm between 1 and 150.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get user's preferred translation
    user_translation = current_user.preferred_translation if hasattr(current_user, 'preferred_translation') else 'ESV'
    
    # Fetch psalm from Bible API
    psalm_api_data = get_psalm(psalm_number, user_translation)
    
    # Get local psalm data for backward compatibility
    psalm = Psalm.get_by_number(psalm_number)
    
    if not psalm_api_data and not psalm:
        flash('Psalm not found.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get user's journal entries for this psalm
    journal_entries = JournalEntry.get_by_user_and_psalm(current_user.id, psalm.id if psalm else psalm_number)
    
    # Pass the entries directly since they now contain all prompts in one entry
    entries_dict = {entry.id: entry for entry in journal_entries} if journal_entries else {}
    
    # Get user's markups for this psalm (placeholder for now)
    markups = []
    
    # Get available translations for the translation selector
    available_translations = get_available_translations()
    
    return render_template('psalm.html', 
                         psalm=psalm,
                         psalm_api_data=psalm_api_data,
                         psalm_number=psalm_number,
                         user_translation=user_translation,
                         available_translations=available_translations,
                         entries_dict=entries_dict,
                         markups=markups)

@main_bp.route('/save_journal', methods=['POST'])
@login_required
def save_journal():
    try:
        # Handle JSON requests for auto-save
        if request.is_json:
            data = request.get_json()
            psalm_id = data.get('psalm_id')
            prompt_responses = data.get('prompt_responses', {})
        else:
            # Handle form data for backward compatibility
            psalm_id = request.form.get('psalm_id')
            prompt_number = request.form.get('prompt_number')
            content = request.form.get('content')
            prompt_responses = {prompt_number: content} if prompt_number and content else {}
        
        if not psalm_id:
            return jsonify({'success': False, 'error': 'Invalid journal entry data'}), 400
        
        print(f"DEBUG: Saving journal - user_id={current_user.id}, psalm_id={psalm_id}")
        print(f"DEBUG: Prompt responses: {prompt_responses}")
        
        # For consolidated saving, we need to check for today's entry
        today = datetime.now().strftime('%Y-%m-%d')
        existing_entries = JournalEntry.get_by_user_and_psalm(current_user.id, psalm_id)
        
        # Filter to today's entries only
        today_entry = None
        for entry in existing_entries:
            if entry.created_at and entry.created_at.startswith(today):
                today_entry = entry
                break
        
        if today_entry:
            # Update existing entry with consolidated responses
            print(f"DEBUG: Updating existing entry ID {today_entry.id}")
            today_entry.prompt_responses.update(prompt_responses)
            today_entry.save()
        else:
            # Create new consolidated entry
            print(f"DEBUG: Creating new consolidated entry")
            entry = JournalEntry(
                user_id=current_user.id,
                psalm_id=psalm_id,
                prompt_responses=prompt_responses
            )
            entry.save()
        
        return jsonify({'success': True, 'message': 'Journal entry saved successfully!'})
        
    except Exception as e:
        print(f"Error saving journal entry: {e}")
        return jsonify({'success': False, 'error': 'Error saving journal entry. Please try again.'}), 500
        
        # Since we store all prompts in one entry, get the first (and should be only) entry
        if existing_entries:
            entry = existing_entries[0]
            print(f"DEBUG: Updating existing entry ID {entry.id}")
            # Update the specific prompt response
            entry.prompt_responses[str(prompt_number)] = content or ""
            print(f"DEBUG: Updated prompt_responses: {entry.prompt_responses}")
        else:
            # Create new entry with this prompt response
            prompt_responses = {str(prompt_number): content or ""}
            print(f"DEBUG: Creating new entry with prompt_responses: {prompt_responses}")
            entry = JournalEntry(
                user_id=current_user.id,
                psalm_id=int(psalm_id),
                prompt_responses=prompt_responses
            )
        
        # Save the entry
        print(f"DEBUG: Attempting to save entry...")
        save_result = entry.save()
        print(f"DEBUG: Save result: {save_result}")
        
        if save_result:
            print(f"DEBUG: Save successful, entry ID: {entry.id}")
            # For AJAX requests, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
               'application/json' in request.headers.get('Accept', ''):
                return jsonify({'success': True, 'message': 'Journal entry saved successfully'})
            
            flash('Journal entry saved successfully!', 'success')
        else:
            print(f"DEBUG: Save failed")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
               'application/json' in request.headers.get('Accept', ''):
                return jsonify({'success': False, 'error': 'Error saving journal entry'}), 500
            
            flash('Error saving journal entry. Please try again.', 'error')
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in save_journal: {e}")
        print(f"Full traceback: {error_details}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
           'application/json' in request.headers.get('Accept', ''):
            return jsonify({'success': False, 'error': str(e), 'details': error_details}), 500
        
        flash('Error saving journal entry. Please try again.', 'error')
    
    # For regular form submissions, redirect back to psalm
    try:
        from database import get_supabase_client
        supabase = get_supabase_client()
        result = supabase.table('psalms').select('psalm_number').eq('id', psalm_id).execute()
        if result.data:
            psalm_number = result.data[0]['psalm_number']
            return redirect(url_for('main.psalm', psalm_number=psalm_number))
    except Exception as e:
        print(f"Error getting psalm number: {e}")
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/complete_psalm', methods=['POST'])
@login_required
def complete_psalm():
    psalm_id = request.form.get('psalm_id')
    reading_time = request.form.get('reading_time', 0)
    music_listened = request.form.get('music_listened') == 'true'
    
    if not psalm_id:
        flash('Invalid psalm data.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Check if journal is completed (at least one entry)
        journal_entries = JournalEntry.get_by_user_and_psalm(current_user.id, psalm_id)
        journal_completed = len(journal_entries) > 0
        
        progress = PsalmProgress(
            user_id=current_user.id,
            psalm_id=int(psalm_id),
            completed=True
        )
        
        if progress.save():
            flash('Psalm completion recorded!', 'success')
        else:
            flash('Error recording progress. Please try again.', 'error')
    except Exception as e:
        print(f"Error saving progress: {e}")
        flash('Error recording progress. Please try again.', 'error')
    
    # Get psalm number for redirect
    try:
        from database import get_supabase_client
        supabase = get_supabase_client()
        result = supabase.table('psalms').select('psalm_number').eq('id', psalm_id).execute()
        if result.data:
            psalm_number = result.data[0]['psalm_number']
            return redirect(url_for('main.psalm', psalm_number=psalm_number))
    except:
        pass
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/journal/<int:entry_id>')
@login_required
def view_journal_entry(entry_id):
    """View a specific journal entry"""
    try:
        # Get the specific journal entry
        supabase = get_supabase_client()
        result = supabase.table('journal_entries').select('*')\
            .eq('id', entry_id).eq('user_id', current_user.id).execute()
        
        if not result.data:
            flash('Journal entry not found.', 'error')
            return redirect(url_for('main.journal_history'))
        
        entry_data = result.data[0]
        entry = JournalEntry(
            id=entry_data['id'],
            user_id=entry_data['user_id'],
            psalm_id=entry_data['psalm_id'],
            prompt_responses=entry_data.get('prompt_responses', {}),
            created_at=entry_data.get('created_at')
        )
        
        # Get the psalm
        psalm = Psalm.get_by_number(entry.psalm_id)
        if not psalm:
            flash('Associated psalm not found.', 'error')
            return redirect(url_for('main.journal_history'))
        
        return render_template('journal_entry.html', entry=entry, psalm=psalm)
        
    except Exception as e:
        print(f"Error viewing journal entry: {e}")
        flash('Error loading journal entry.', 'error')
        return redirect(url_for('main.journal_history'))

@main_bp.route('/prayers')
@login_required
def prayers():
    active_prayers = Prayer.get_active_by_user(current_user.id)
    answered_prayers = Prayer.get_answered_by_user(current_user.id, limit=10)
    
    return render_template('prayers.html', 
                         active_prayers=active_prayers,
                         answered_prayers=answered_prayers)

@main_bp.route('/add_prayer', methods=['POST'])
@login_required
def add_prayer():
    title = request.form.get('title')
    description = request.form.get('description')
    category = request.form.get('category')
    
    if not title or not category:
        flash('Please fill in the required fields.', 'error')
        return redirect(url_for('main.prayers'))
    
    prayer = Prayer(
        user_id=current_user.id,
        category=category,
        title=title,
        description=description or ""
    )
    
    if prayer.save():
        flash('Prayer added successfully!', 'success')
    else:
        flash('Error adding prayer. Please try again.', 'error')
    
    return redirect(url_for('main.prayers'))

@main_bp.route('/answer_prayer', methods=['POST'])
@login_required
def answer_prayer():
    prayer_id = request.form.get('prayer_id')
    answered_note = request.form.get('answered_note')
    
    if not prayer_id:
        flash('Invalid prayer ID.', 'error')
        return redirect(url_for('main.prayers'))
    
    try:
        # Get the prayer and verify ownership
        from database import get_supabase_client
        supabase = get_supabase_client()
        result = supabase.table('prayer_lists').select('*').eq('id', prayer_id).eq('user_id', current_user.id).execute()
        
        if result.data:
            prayer_data = result.data[0]
            prayer = Prayer(
                id=prayer_data['id'],
                user_id=prayer_data['user_id'],
                category=prayer_data.get('category'),
                title=prayer_data.get('title'),
                description=prayer_data.get('description'),
                prayer_text=prayer_data.get('prayer_text'),
                is_answered=True,
                answered_note=answered_note,
                answered_at=datetime.utcnow(),
                created_at=prayer_data.get('created_at')
            )
            
            if prayer.save():
                flash('Prayer marked as answered! Praise God!', 'success')
            else:
                flash('Error updating prayer. Please try again.', 'error')
        else:
            flash('Prayer not found.', 'error')
    except Exception as e:
        print(f"Error answering prayer: {e}")
        flash('Error updating prayer. Please try again.', 'error')
    
    return redirect(url_for('main.prayers'))

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main_bp.route('/update_preferences', methods=['POST'])
@login_required
def update_preferences():
    translation = request.form.get('translation')
    font = request.form.get('font')
    theme = request.form.get('theme')
    
    if current_user.update_preferences(translation=translation, font=font, theme=theme):
        flash('Preferences updated successfully!', 'success')
    else:
        flash('Error updating preferences. Please try again.', 'error')
    
    return redirect(url_for('main.profile'))
