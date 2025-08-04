from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Text, Boolean, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User preferences
    preferred_translation = db.Column(db.String(10), default='NIV')
    font_preference = db.Column(db.String(50), default='Georgia')
    theme_preference = db.Column(db.String(50), default='default')
    
    # Relationships
    journal_entries = relationship('JournalEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    psalm_markups = relationship('PsalmMarkup', backref='user', lazy=True, cascade='all, delete-orphan')
    prayers = relationship('Prayer', backref='user', lazy=True, cascade='all, delete-orphan')
    progress_records = relationship('PsalmProgress', backref='user', lazy=True, cascade='all, delete-orphan')

class Psalm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(200))
    
    # Psalm texts in different translations
    text_niv = db.Column(db.Text)
    text_esv = db.Column(db.Text)
    text_nlt = db.Column(db.Text)
    text_nkjv = db.Column(db.Text)
    text_nrsv = db.Column(db.Text)
    
    # YouTube music URL
    youtube_url = db.Column(db.String(500))
    
    # Devotional prompts
    prompt_1 = db.Column(db.Text)
    prompt_2 = db.Column(db.Text)
    prompt_3 = db.Column(db.Text)
    prompt_4 = db.Column(db.Text)
    
    # Relationships
    journal_entries = relationship('JournalEntry', backref='psalm', lazy=True)
    markups = relationship('PsalmMarkup', backref='psalm', lazy=True)
    progress_records = relationship('PsalmProgress', backref='psalm', lazy=True)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    psalm_id = db.Column(db.Integer, ForeignKey('psalm.id'), nullable=False)
    prompt_number = db.Column(db.Integer, nullable=False)  # 1-4
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_shared = db.Column(db.Boolean, default=False)

class PsalmMarkup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    psalm_id = db.Column(db.Integer, ForeignKey('psalm.id'), nullable=False)
    translation = db.Column(db.String(10), nullable=False)
    start_position = db.Column(db.Integer)
    end_position = db.Column(db.Integer)
    markup_type = db.Column(db.String(20))  # 'highlight', 'note'
    color = db.Column(db.String(20), default='yellow')
    note_text = db.Column(db.Text)
    is_visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # 'family', 'healing', 'salvation', 'personal'
    is_answered = db.Column(db.Boolean, default=False)
    answered_date = db.Column(db.DateTime)
    answered_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PsalmProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    psalm_id = db.Column(db.Integer, ForeignKey('psalm.id'), nullable=False)
    completed_date = db.Column(db.DateTime, default=datetime.utcnow)
    reading_time_minutes = db.Column(db.Integer)
    journal_completed = db.Column(db.Boolean, default=False)
    music_listened = db.Column(db.Boolean, default=False)
