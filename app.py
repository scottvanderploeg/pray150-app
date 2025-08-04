import os
import logging
from flask import Flask
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.environ.get('SUPABASE_JWT_SECRET')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
jwt = JWTManager(app)

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Initialize Flask-Login for session management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(user_id)

# Import and register blueprints
from auth import auth_bp
from routes import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

# Initialize database tables
from database import initialize_database
initialize_database()
