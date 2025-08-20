from app import app
from admin import admin_bp

# Register admin blueprint
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
