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
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        try:
            # Check if username is already taken
            existing_user = User.get_by_email(email)
            if existing_user:
                flash('Email already registered. Please use a different email.', 'error')
                return render_template('register.html')
            
            # Use Supabase Auth for registration
            supabase = get_supabase_client()
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Create user object for Flask-Login (simplified)
                user = User(
                    id=auth_response.user.id,
                    username=username,
                    email=email
                )
                
                login_user(user, remember=True)
                flash('Registration successful! Welcome to Pray150.', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Registration failed. Please try again.', 'error')
                
        except Exception as e:
            print(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
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
    """Display the reset password form"""
    return render_template('reset_password_manual.html')
