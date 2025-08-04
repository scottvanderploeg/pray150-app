from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Psalm, JournalEntry, Prayer, PsalmProgress, User
from psalm_data import initialize_psalms
from datetime import datetime, timedelta

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
    
    # Get today's psalm (using modulo to cycle through available psalms)
    day_of_year = datetime.now().timetuple().tm_yday
    todays_psalm_number = ((day_of_year - 1) % psalm_count) + 1 if psalm_count > 0 else 1
    todays_psalm = Psalm.get_by_number(todays_psalm_number)
    
    # Get recent journal entries
    recent_entries = JournalEntry.get_recent_by_user(current_user.id, limit=3)
    
    # Get active prayers
    active_prayers = Prayer.get_active_by_user(current_user.id, limit=5)
    
    # Get progress summary
    total_psalms_read = PsalmProgress.get_count_by_user(current_user.id)
    psalms_this_week = PsalmProgress.get_week_count_by_user(current_user.id)
    
    return render_template('dashboard.html',
                         todays_psalm=todays_psalm,
                         recent_entries=recent_entries,
                         active_prayers=active_prayers,
                         total_psalms_read=total_psalms_read,
                         psalms_this_week=psalms_this_week)

@main_bp.route('/psalm/<int:psalm_number>')
@login_required
def psalm(psalm_number):
    psalm = Psalm.get_by_number(psalm_number)
    if not psalm:
        flash('Psalm not found.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get user's journal entries for this psalm
    journal_entries = JournalEntry.get_by_user_and_psalm(current_user.id, psalm.id)
    
    # Convert to dict for easy template access
    entries_dict = {entry.prompt_number: entry for entry in journal_entries}
    
    # Get user's markups for this psalm (placeholder for now)
    markups = []
    
    return render_template('psalm.html', 
                         psalm=psalm, 
                         entries_dict=entries_dict,
                         markups=markups)

@main_bp.route('/save_journal', methods=['POST'])
@login_required
def save_journal():
    psalm_id = request.form.get('psalm_id')
    prompt_number = request.form.get('prompt_number')
    content = request.form.get('content')
    
    if not psalm_id or not prompt_number:
        flash('Invalid journal entry data.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Find existing entry or create new one
    existing_entries = JournalEntry.get_by_user_and_psalm(current_user.id, psalm_id)
    existing_entry = None
    for entry in existing_entries:
        if entry.prompt_number == int(prompt_number):
            existing_entry = entry
            break
    
    if existing_entry:
        # Update existing entry's prompt responses
        existing_entry.prompt_responses[str(prompt_number)] = content
        entry = existing_entry
    else:
        # Create new entry with prompt responses
        prompt_responses = {str(prompt_number): content}
        entry = JournalEntry(
            user_id=current_user.id,
            psalm_id=int(psalm_id),
            prompt_responses=prompt_responses
        )
    
    if entry.save():
        flash('Journal entry saved successfully!', 'success')
    else:
        flash('Error saving journal entry. Please try again.', 'error')
    
    # Get psalm number for redirect
    psalm = Psalm.get_by_number(1)  # Default fallback
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
        prayer_text=f"{title}: {description}" if description else title
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
                prayer_text=prayer_data.get('prayer_text'),
                is_answered=True,
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
