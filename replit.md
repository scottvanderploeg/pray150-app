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
- **Supabase** as primary database with PostgreSQL backend 
- Five core models: User, Psalm, JournalEntry, Prayer, PsalmProgress, and PsalmMarkup
- Simplified schema with user_id as TEXT for Supabase Auth compatibility
- JSONB fields for flexible data storage (prompt_responses, markup_data)
- BIGINT primary keys and optimized timestamp handling
- Row Level Security (RLS) policies for user data isolation

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

### Current Integrations (Updated August 2025)
- **Supabase** successfully integrated as primary database and authentication provider
- Direct Supabase Auth integration with REST API endpoints
- **Flask-JWT-Extended** for JWT token management and API authentication
- Environment-based configuration with SUPABASE_URL, SUPABASE_KEY, SUPABASE_JWT_SECRET
- 4 out of 5 database tables created and verified (journal_entries table pending user creation)

### Authentication API Endpoints (August 2025)
- **POST /api/register**: User registration with Supabase Auth (requires email confirmation)
- **POST /api/login**: User login returning JWT access tokens
- **GET /api/verify**: JWT token verification and user information retrieval
- **POST /api/forgot-password**: Password reset email via Supabase Auth
- **POST /api/reset-password**: Password update using email-provided tokens
- **POST /api/journal**: Save journal entries with devotional prompts (requires JWT authentication)
- **GET /forgot-password**: Web interface for password reset requests
- **GET /reset-password**: Web interface for password reset completion
- Integration with existing Flask-Login session management for web interface
- Comprehensive error handling with proper HTTP status codes
- Email confirmation requirement through Supabase (configurable in Supabase dashboard)
- Complete password recovery flow with secure token-based verification
- Journal entries stored in Supabase journal_entries table with JSONB prompt responses

### Planned Integrations
- Social sharing capabilities for prayer milestones and journal entries
- Future iOS/Android mobile app development path