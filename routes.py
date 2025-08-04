from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from models import Psalm, JournalEntry, Prayer, PsalmProgress, PsalmMarkup, User
from psalm_data import initialize_psalms
from datetime import datetime, timedelta
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Initialize psalms if needed
    if Psalm.query.count() == 0:
        initialize_psalms()
    
    # Get today's psalm (using modulo to cycle through available psalms)
    psalm_count = Psalm.query.count()
    day_of_year = datetime.now().timetuple().tm_yday
    todays_psalm_number = ((day_of_year - 1) % psalm_count) + 1
    todays_psalm = Psalm.query.filter_by(number=todays_psalm_number).first()
    
    # Get recent journal entries
    recent_entries = JournalEntry.query.filter_by(user_id=current_user.id)\
        .order_by(desc(JournalEntry.updated_at)).limit(3).all()
    
    # Get active prayers
    active_prayers = Prayer.query.filter_by(user_id=current_user.id, is_answered=False)\
        .order_by(desc(Prayer.created_at)).limit(5).all()
    
    # Get progress summary
    total_psalms_read = PsalmProgress.query.filter_by(user_id=current_user.id).count()
    this_week = datetime.now() - timedelta(days=7)
    psalms_this_week = PsalmProgress.query.filter_by(user_id=current_user.id)\
        .filter(PsalmProgress.completed_date >= this_week).count()
    
    return render_template('dashboard.html',
                         todays_psalm=todays_psalm,
                         recent_entries=recent_entries,
                         active_prayers=active_prayers,
                         total_psalms_read=total_psalms_read,
                         psalms_this_week=psalms_this_week)

@main_bp.route('/psalm/<int:psalm_number>')
@login_required
def psalm(psalm_number):
    psalm = Psalm.query.filter_by(number=psalm_number).first()
    if not psalm:
        flash('Psalm not found.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get user's journal entries for this psalm
    journal_entries = JournalEntry.query.filter_by(
        user_id=current_user.id, 
        psalm_id=psalm.id
    ).all()
    
    # Convert to dict for easy template access
    entries_dict = {entry.prompt_number: entry for entry in journal_entries}
    
    # Get user's markups for this psalm
    markups = PsalmMarkup.query.filter_by(
        user_id=current_user.id,
        psalm_id=psalm.id,
        translation=current_user.preferred_translation
    ).all()
    
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
    
    # Find existing entry or create new one
    entry = JournalEntry.query.filter_by(
        user_id=current_user.id,
        psalm_id=psalm_id,
        prompt_number=prompt_number
    ).first()
    
    if entry:
        entry.content = content
        entry.updated_at = datetime.utcnow()
    else:
        entry = JournalEntry(
            user_id=current_user.id,
            psalm_id=psalm_id,
            prompt_number=prompt_number,
            content=content
        )
        db.session.add(entry)
    
    try:
        db.session.commit()
        flash('Journal entry saved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error saving journal entry. Please try again.', 'error')
    
    return redirect(url_for('main.psalm', psalm_number=Psalm.query.get(psalm_id).number))

@main_bp.route('/complete_psalm', methods=['POST'])
@login_required
def complete_psalm():
    psalm_id = request.form.get('psalm_id')
    reading_time = request.form.get('reading_time', 0)
    music_listened = request.form.get('music_listened') == 'true'
    
    # Check if already completed today
    today = datetime.now().date()
    existing_progress = PsalmProgress.query.filter_by(
        user_id=current_user.id,
        psalm_id=psalm_id
    ).filter(PsalmProgress.completed_date >= today).first()
    
    if not existing_progress:
        # Check if journal is completed (at least one entry)
        journal_completed = JournalEntry.query.filter_by(
            user_id=current_user.id,
            psalm_id=psalm_id
        ).first() is not None
        
        progress = PsalmProgress(
            user_id=current_user.id,
            psalm_id=psalm_id,
            reading_time_minutes=reading_time,
            journal_completed=journal_completed,
            music_listened=music_listened
        )
        
        db.session.add(progress)
        db.session.commit()
        flash('Psalm completion recorded!', 'success')
    
    return redirect(url_for('main.psalm', psalm_number=Psalm.query.get(psalm_id).number))

@main_bp.route('/prayers')
@login_required
def prayers():
    active_prayers = Prayer.query.filter_by(
        user_id=current_user.id, 
        is_answered=False
    ).order_by(desc(Prayer.created_at)).all()
    
    answered_prayers = Prayer.query.filter_by(
        user_id=current_user.id, 
        is_answered=True
    ).order_by(desc(Prayer.answered_date)).limit(10).all()
    
    return render_template('prayers.html', 
                         active_prayers=active_prayers,
                         answered_prayers=answered_prayers)

@main_bp.route('/add_prayer', methods=['POST'])
@login_required
def add_prayer():
    title = request.form.get('title')
    description = request.form.get('description')
    category = request.form.get('category')
    
    prayer = Prayer(
        user_id=current_user.id,
        title=title,
        description=description,
        category=category
    )
    
    try:
        db.session.add(prayer)
        db.session.commit()
        flash('Prayer added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding prayer. Please try again.', 'error')
    
    return redirect(url_for('main.prayers'))

@main_bp.route('/answer_prayer', methods=['POST'])
@login_required
def answer_prayer():
    prayer_id = request.form.get('prayer_id')
    answered_note = request.form.get('answered_note')
    
    prayer = Prayer.query.filter_by(
        id=prayer_id, 
        user_id=current_user.id
    ).first()
    
    if prayer:
        prayer.is_answered = True
        prayer.answered_date = datetime.utcnow()
        prayer.answered_note = answered_note
        
        try:
            db.session.commit()
            flash('Prayer marked as answered! Praise God!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating prayer. Please try again.', 'error')
    
    return redirect(url_for('main.prayers'))

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main_bp.route('/update_preferences', methods=['POST'])
@login_required
def update_preferences():
    current_user.preferred_translation = request.form.get('translation')
    current_user.font_preference = request.form.get('font')
    current_user.theme_preference = request.form.get('theme')
    
    try:
        db.session.commit()
        flash('Preferences updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating preferences. Please try again.', 'error')
    
    return redirect(url_for('main.profile'))
