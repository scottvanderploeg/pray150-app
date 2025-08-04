from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database import get_supabase_client
import os

auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api')

@auth_api_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with Supabase Auth"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
        
        # Use Supabase Auth for registration
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "email_redirect_to": None
            }
        })
        
        if auth_response.user:
            return jsonify({
                "message": "User registered",
                "user_id": auth_response.user.id
            }), 201
        else:
            return jsonify({"error": "Registration failed - user may already exist"}), 400
            
    except Exception as e:
        error_msg = str(e)
        print(f"Registration error: {error_msg}")
        if "already registered" in error_msg or "already been registered" in error_msg:
            return jsonify({"error": "User already exists"}), 409
        return jsonify({"error": f"Registration failed: {error_msg}"}), 500

@auth_api_bp.route('/login', methods=['POST'])
def login():
    """Login user with Supabase Auth and return JWT token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Use Supabase Auth for login
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # Create JWT access token using user ID
            access_token = create_access_token(identity=auth_response.user.id)
            
            return jsonify({
                "access_token": access_token
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
            
    except Exception as e:
        error_msg = str(e)
        print(f"Login error: {error_msg}")
        if "Invalid login credentials" in error_msg or "invalid_credentials" in error_msg:
            return jsonify({"error": "Invalid email or password"}), 401
        return jsonify({"error": f"Login failed: {error_msg}"}), 500

@auth_api_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token and return user info"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get user info from Supabase
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user()
        
        if user_response.user:
            return jsonify({
                "valid": True,
                "user_id": current_user_id,
                "email": user_response.user.email
            }), 200
        else:
            return jsonify({"error": "Invalid token"}), 401
            
    except Exception as e:
        print(f"Token verification error: {e}")
        return jsonify({"error": "Token verification failed"}), 401

@auth_api_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email via Supabase Auth"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Use Supabase Auth to send password reset email
        supabase = get_supabase_client()
        
        # Use the request's host URL, ensuring it works with Replit's domain
        base_url = request.host_url.rstrip('/')
        redirect_url = f"{base_url}/reset-password"
        
        auth_response = supabase.auth.reset_password_for_email(
            email,
            options={
                "redirect_to": redirect_url
            }
        )
        
        # Supabase always returns success for security reasons
        # (to prevent email enumeration attacks)
        return jsonify({
            "message": "If an account with this email exists, a password reset link has been sent."
        }), 200
            
    except Exception as e:
        print(f"Password reset error: {e}")
        return jsonify({"error": "Password reset request failed. Please try again."}), 500

@auth_api_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token from email"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        new_password = data.get('new_password')
        
        if not access_token or not refresh_token or not new_password:
            return jsonify({"error": "Access token, refresh token, and new password are required"}), 400
        
        if len(new_password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
        
        # Use Supabase Auth to update password
        supabase = get_supabase_client()
        
        # Set the session with the tokens from the reset email
        supabase.auth.set_session(access_token, refresh_token)
        
        # Update the password
        auth_response = supabase.auth.update_user({
            "password": new_password
        })
        
        if auth_response.user:
            return jsonify({
                "message": "Password updated successfully"
            }), 200
        else:
            return jsonify({"error": "Password reset failed"}), 400
            
    except Exception as e:
        print(f"Password reset error: {e}")
        return jsonify({"error": "Password reset failed. Please try again."}), 500

@auth_api_bp.route('/direct-reset-password', methods=['POST'])
def direct_reset_password():
    """Reset password directly by creating new account or updating existing one"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        email = data.get('email')
        new_password = data.get('new_password')
        
        if not email or not new_password:
            return jsonify({"error": "Email and new password are required"}), 400
        
        if len(new_password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
        
        # Use Supabase Auth to handle the password reset
        supabase = get_supabase_client()
        
        try:
            # First, try to sign in with the old credentials to check if user exists
            # This will fail if user doesn't exist or has wrong password, which is fine
            
            # Try to create a new user with the email and new password
            # If user already exists, this will fail with "User already registered"
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": new_password
            })
            
            if auth_response.user:
                return jsonify({
                    "message": "Account created successfully with new password. Please check your email for confirmation."
                }), 200
            else:
                return jsonify({"error": "Account creation failed"}), 400
                
        except Exception as supabase_error:
            error_msg = str(supabase_error).lower()
            
            if "user already registered" in error_msg or "already registered" in error_msg:
                # User exists, so we need to use the password reset flow
                try:
                    # Send password reset email
                    reset_response = supabase.auth.reset_password_for_email(email)
                    
                    return jsonify({
                        "message": "Account exists. A password reset email has been sent to your email address. Follow the instructions in the email to reset your password."
                    }), 200
                    
                except Exception as reset_error:
                    print(f"Password reset email error: {reset_error}")
                    return jsonify({
                        "error": "Unable to send password reset email. Please try again later."
                    }), 500
            else:
                print(f"Supabase direct reset error: {supabase_error}")
                return jsonify({
                    "error": "Password reset failed. Please try again."
                }), 500
            
    except Exception as e:
        print(f"Direct password reset error: {e}")
        return jsonify({"error": "Password reset failed. Please try again."}), 500

@auth_api_bp.route('/journal', methods=['POST'])
@jwt_required()
def save_journal_entry():
    """Save journal entry to Supabase journal_entries table"""
    try:
        # Get current user from JWT
        current_user_id = get_jwt_identity()
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        psalm_id = data.get('psalm_id')
        prompt_responses = data.get('prompt_responses')
        
        # Validate required fields
        if not psalm_id or not prompt_responses:
            return jsonify({"error": "psalm_id and prompt_responses are required"}), 400
        
        # Validate psalm_id is integer
        try:
            psalm_id = int(psalm_id)
        except (ValueError, TypeError):
            return jsonify({"error": "psalm_id must be a valid integer"}), 400
        
        # Validate prompt_responses structure
        required_prompts = [
            "Lord, where is my heart/soul today?",
            "LOOK! Lord, help me discover new truth from your Word today.",
            "LISTEN! Lord, what is your thought for me today from your Word?",
            "RESPOND: Lord, what do I need to talk to you about? What are you calling me to do?"
        ]
        
        if not isinstance(prompt_responses, dict):
            return jsonify({"error": "prompt_responses must be an object"}), 400
        
        # Check if all required prompts are present
        for prompt in required_prompts:
            if prompt not in prompt_responses:
                return jsonify({"error": f"Missing response for: {prompt}"}), 400
        
        # Save to Supabase journal_entries table
        supabase = get_supabase_client()
        
        from datetime import datetime
        journal_entry = {
            "user_id": current_user_id,
            "psalm_id": psalm_id,
            "prompt_responses": prompt_responses,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('journal_entries').insert(journal_entry).execute()
        
        if result.data:
            entry_id = result.data[0]['id']
            return jsonify({
                "message": "Journal entry saved",
                "entry_id": str(entry_id)
            }), 201
        else:
            return jsonify({"error": "Failed to save journal entry"}), 500
            
    except Exception as e:
        print(f"Journal entry save error: {e}")
        return jsonify({"error": "Failed to save journal entry. Please try again."}), 500