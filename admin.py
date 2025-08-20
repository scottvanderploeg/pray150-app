from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from database import get_supabase_client
import os
import sys
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin authorization decorator
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Check if user is admin (you can customize this logic)
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            # For now, check if user email is in admin list
            admin_emails = os.environ.get('ADMIN_EMAILS', '').split(',')
            if current_user.email not in admin_emails:
                flash('Access denied. Admin privileges required.', 'error')
                return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with key statistics"""
    try:
        supabase = get_supabase_client()
        
        # Get current date ranges
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        year_ago = now - timedelta(days=365)
        
        # User statistics
        users_total = supabase.table('users').select('id').execute()
        users_week = supabase.table('users').select('id').gte('created_at', week_ago.isoformat()).execute()
        users_month = supabase.table('users').select('id').gte('created_at', month_ago.isoformat()).execute()
        
        # Prayer statistics
        prayers_total = supabase.table('prayers').select('id').execute()
        prayers_week = supabase.table('prayers').select('id').gte('created_at', week_ago.isoformat()).execute()
        prayers_month = supabase.table('prayers').select('id').gte('created_at', month_ago.isoformat()).execute()
        prayers_answered = supabase.table('prayers').select('id').eq('is_answered', True).execute()
        
        # Journal entries statistics
        journal_total = supabase.table('journal_entries').select('id').execute()
        journal_week = supabase.table('journal_entries').select('id').gte('created_at', week_ago.isoformat()).execute()
        journal_month = supabase.table('journal_entries').select('id').gte('created_at', month_ago.isoformat()).execute()
        
        # Markup statistics (highlights and notes)
        markups_total = supabase.table('markups').select('id').execute()
        markups_week = supabase.table('markups').select('id').gte('created_at', week_ago.isoformat()).execute()
        markups_month = supabase.table('markups').select('id').gte('created_at', month_ago.isoformat()).execute()
        
        stats = {
            'users': {
                'total': len(users_total.data) if users_total.data else 0,
                'week': len(users_week.data) if users_week.data else 0,
                'month': len(users_month.data) if users_month.data else 0
            },
            'prayers': {
                'total': len(prayers_total.data) if prayers_total.data else 0,
                'week': len(prayers_week.data) if prayers_week.data else 0,
                'month': len(prayers_month.data) if prayers_month.data else 0,
                'answered': len(prayers_answered.data) if prayers_answered.data else 0
            },
            'journals': {
                'total': len(journal_total.data) if journal_total.data else 0,
                'week': len(journal_week.data) if journal_week.data else 0,
                'month': len(journal_month.data) if journal_month.data else 0
            },
            'markups': {
                'total': len(markups_total.data) if markups_total.data else 0,
                'week': len(markups_week.data) if markups_week.data else 0,
                'month': len(markups_month.data) if markups_month.data else 0
            }
        }
        
        return render_template('admin/dashboard.html', stats=stats)
        
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        flash('Error loading admin dashboard', 'error')
        return redirect(url_for('main.dashboard'))

@admin_bp.route('/users')
@admin_required
def users():
    """User management page"""
    try:
        supabase = get_supabase_client()
        
        # Get all users with their profiles
        users_response = supabase.table('users').select('*').execute()
        profiles_response = supabase.table('user_profiles').select('*').execute()
        
        # Combine user data with profiles
        users_data = users_response.data or []
        profiles_data = {profile['user_id']: profile for profile in (profiles_response.data or [])}
        
        # Enhance user data with profile information
        for user in users_data:
            profile = profiles_data.get(user['id'], {})
            user['profile'] = profile
            user['full_name'] = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or 'Unknown'
            user['location'] = f"{profile.get('country', '')}, {profile.get('zip_code', '')}".strip(' ,') or 'Unknown'
        
        return render_template('admin/users.html', users=users_data)
        
    except Exception as e:
        print(f"Admin users error: {e}")
        flash('Error loading users', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Analytics page with detailed charts and trends"""
    try:
        supabase = get_supabase_client()
        
        # Get daily user registrations for the past 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        daily_users = supabase.table('users')\
            .select('created_at')\
            .gte('created_at', thirty_days_ago.isoformat())\
            .order('created_at')\
            .execute()
        
        # Get daily prayer requests for the past 30 days
        daily_prayers = supabase.table('prayers')\
            .select('created_at')\
            .gte('created_at', thirty_days_ago.isoformat())\
            .order('created_at')\
            .execute()
        
        # Get daily journal entries for the past 30 days
        daily_journals = supabase.table('journal_entries')\
            .select('created_at')\
            .gte('created_at', thirty_days_ago.isoformat())\
            .order('created_at')\
            .execute()
        
        # Process data for charts
        def process_daily_data(data, date_field='created_at'):
            daily_counts = {}
            for item in data.data or []:
                date_str = item[date_field][:10]  # Get YYYY-MM-DD part
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
            
            # Fill in missing days with 0
            result = []
            current_date = thirty_days_ago.date()
            end_date = datetime.now().date()
            
            while current_date <= end_date:
                date_str = current_date.isoformat()
                result.append({
                    'date': date_str,
                    'count': daily_counts.get(date_str, 0)
                })
                current_date += timedelta(days=1)
            
            return result
        
        analytics_data = {
            'daily_users': process_daily_data(daily_users),
            'daily_prayers': process_daily_data(daily_prayers),
            'daily_journals': process_daily_data(daily_journals)
        }
        
        return render_template('admin/analytics.html', analytics=analytics_data)
        
    except Exception as e:
        print(f"Admin analytics error: {e}")
        flash('Error loading analytics', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reset_password/<user_id>', methods=['POST'])
@admin_required
def reset_password(user_id):
    """Reset a user's password"""
    try:
        new_password = request.form.get('new_password')
        if not new_password or len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        supabase = get_supabase_client()
        
        # Use Supabase Admin API to reset password
        from supabase import create_client
        supabase_url = os.environ.get('SUPABASE_URL')
        service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not service_key:
            return jsonify({'error': 'Admin credentials not configured'}), 500
            
        admin_supabase = create_client(supabase_url, service_key)
        
        # Update user password using admin privileges
        response = admin_supabase.auth.admin.update_user_by_id(
            user_id, 
            {"password": new_password}
        )
        
        if response:
            return jsonify({'success': True, 'message': 'Password reset successfully'})
        else:
            return jsonify({'error': 'Failed to reset password'}), 500
            
    except Exception as e:
        print(f"Password reset error: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/system_info')
@admin_required
def system_info():
    """System information and health check"""
    try:
        # Test database connection
        supabase = get_supabase_client()
        db_test = supabase.table('users').select('id').limit(1).execute()
        db_status = 'Connected' if db_test.data is not None else 'Error'
        
        # Get environment info (be careful not to expose sensitive data)
        system_info = {
            'database_status': db_status,
            'supabase_url': os.environ.get('SUPABASE_URL', 'Not set')[:30] + '...',
            'environment': os.environ.get('ENVIRONMENT', 'development'),
            'python_version': sys.version,
            'replit_domain': os.environ.get('REPLIT_DOMAINS', 'Not set')
        }
        
        return render_template('admin/system.html', system_info=system_info)
        
    except Exception as e:
        print(f"System info error: {e}")
        flash('Error loading system information', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/export_data/<data_type>')
@admin_required 
def export_data(data_type):
    """Export data as JSON for backup/analysis"""
    try:
        supabase = get_supabase_client()
        
        if data_type == 'users':
            data = supabase.table('users').select('*').execute()
        elif data_type == 'prayers':
            data = supabase.table('prayers').select('*').execute()
        elif data_type == 'journals':
            data = supabase.table('journal_entries').select('*').execute()
        elif data_type == 'markups':
            data = supabase.table('markups').select('*').execute()
        else:
            return jsonify({'error': 'Invalid data type'}), 400
        
        return jsonify({
            'success': True,
            'data_type': data_type,
            'count': len(data.data or []),
            'data': data.data or []
        })
        
    except Exception as e:
        print(f"Export data error: {e}")
        return jsonify({'error': str(e)}), 500