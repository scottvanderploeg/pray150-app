# Pray150 - Scripture-Fed Prayer Application

## Overview

Pray150 is a devotional web application designed to teach people how to pray by immersing them in the Psalms. The application provides a structured approach to Scripture-fed, Spirit-led, worship-based prayer through daily Psalm readings, guided journaling, music integration, and prayer tracking. Built with Flask, the app serves users ranging from new believers learning to pray to mature believers seeking deeper prayer lives.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask** as the primary web framework with modular blueprint structure
- **SQLAlchemy** with DeclarativeBase for ORM and database management
- **Flask-Login** for user session management and authentication
- Modular design with separate blueprints for authentication (`auth.py`) and main functionality (`routes.py`)

### Database Design
- **SQLite** as default database with configurable DATABASE_URL for production scaling
- Five core models: User, Psalm, JournalEntry, Prayer, PsalmProgress, and PsalmMarkup
- User-centric data model with cascading relationships for data integrity
- User preference storage for translations, fonts, and themes
- Progress tracking with timestamps for completion analytics

### Authentication & Security
- **Werkzeug** password hashing for secure credential storage
- Session-based authentication with configurable secret keys
- User data isolation through foreign key relationships
- Remember-me functionality for persistent sessions

### Frontend Architecture
- **Bootstrap 5** for responsive UI components and grid system
- **Font Awesome** icons for consistent visual language
- Custom CSS with CSS variables for theme customization
- JavaScript enhancement for form validation, tooltips, and interactive features
- Mobile-first responsive design for future mobile app development

### Content Management
- Static Psalm data initialization system in `psalm_data.py`
- Multiple Bible translation support (NIV, ESV, NLT, NKJV, NRSV)
- YouTube embed integration for worship music accompaniment
- Four devotional prompts per Psalm for guided reflection

### User Experience Features
- Daily Psalm calculation using day-of-year modulo for consistent cycling
- Dashboard with progress summaries and recent activity
- Text highlighting and note-taking with toggle visibility
- Prayer categorization (family, healing, salvation, personal) with answered prayer archiving
- Customizable reading preferences (font, theme, translation)

## External Dependencies

### Core Libraries
- **Flask** (web framework)
- **Flask-SQLAlchemy** (database ORM)
- **Flask-Login** (authentication management)
- **Werkzeug** (security utilities)

### Frontend Resources
- **Bootstrap 5** (CSS framework via CDN)
- **Font Awesome 6** (icon library via CDN)
- **Google Fonts** (typography - Georgia, Merriweather)

### Media Integration
- **YouTube** embed API for Psalm music integration
- Plans for future MP3 conversion for mobile applications

### Development Tools
- **SQLite** for development database (configurable for production)
- Environment variable configuration for deployment flexibility
- ProxyFix middleware for production deployment compatibility

### Planned Integrations
- **Supabase** mentioned in project notes for future database and authentication migration
- Social sharing capabilities for prayer milestones and journal entries
- Future iOS/Android mobile app development path