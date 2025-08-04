from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from database import get_supabase_client
from models import User
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')
        
        try:
            # Use Supabase Auth for login
            supabase = get_supabase_client()
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Create user object for Flask-Login (simplified)
                user = User.get_by_id(auth_response.user.id)
                login_user(user, remember=True)
                flash('Welcome back!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                flash('Invalid email or password. Please try again.', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        country = request.form.get('country')
        zip_code = request.form.get('zip_code')
        
        if not first_name or not last_name or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        try:
            # Use Supabase Auth for registration
            supabase = get_supabase_client()
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                try:
                    # Create user profile record
                    profile_data = {
                        'user_id': auth_response.user.id,
                        'username': f"{first_name.lower()}.{last_name.lower()}",
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'country': country or None,
                        'zip_code': zip_code or None,
                        'preferred_translation': 'NIV',
                        'font_preference': 'Georgia',
                        'theme_preference': 'default'
                    }
                    
                    # Save profile to user_profiles table
                    profile_result = supabase.table('user_profiles').insert(profile_data).execute()
                    print(f"Profile created: {profile_result}")
                    
                except Exception as profile_error:
                    print(f"Profile creation error: {profile_error}")
                    # Continue with registration even if profile creation fails
                
                # Create user object for Flask-Login
                user = User(
                    id=auth_response.user.id,
                    username=f"{first_name.lower()}.{last_name.lower()}",
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    country=country,
                    zip_code=zip_code
                )
                
                login_user(user, remember=True)
                flash('Registration successful! Welcome to Pray150. Please check your email to confirm your account.', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Registration failed. Please try again.', 'error')
                
        except Exception as e:
            print(f"Registration error: {e}")
            error_msg = str(e)
            if "rate limit" in error_msg.lower():
                flash('Too many registration attempts. Please wait a moment and try again.', 'error')
            elif "email" in error_msg.lower():
                flash('This email is already registered or invalid. Please try a different email.', 'error')
            else:
                flash('Registration failed. Please try again in a few moments.', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    try:
        # Sign out from Supabase
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Supabase logout error: {e}")
    
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    """Display the forgot password form"""
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password', methods=['GET']) 
def reset_password():
    """Display the simple password reset form"""
    return render_template('simple_reset.html')
