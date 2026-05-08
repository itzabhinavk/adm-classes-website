"""
Application Configuration
"""
import os

# Database Configuration
# Use environment variables so the app can connect to MySQL with a password.
db_config = {
    "host": os.environ.get('DB_HOST', 'localhost'),      # MySQL server host
    "user": os.environ.get('DB_USER', 'root'),           # MySQL username
    "password": os.environ.get('DB_PASSWORD', ''),       # MySQL password
    "database": os.environ.get('DB_NAME', 'railway'),         # Database name
    "port": int(os.environ.get('DB_PORT', '3306')),        # MySQL port

}

# OAuth Configuration (Google & GitHub)
# Get these from Google Cloud Console and GitHub Developer Settings
OAUTH_CONFIG = {
    "google": {
        "client_id": os.environ.get('GOOGLE_CLIENT_ID', '1004428945612-8lcivej5uvumv5dfunh37madur7jgug6.apps.googleusercontent.com'),
        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET', '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'),
        "redirect_uri": os.environ.get('GOOGLE_REDIRECT_URI', '/auth/google/callback')
    },
    "github": {
        "client_id": os.environ.get('GITHUB_CLIENT_ID', 'Ov23li60etrfZQ7iwI3d'),
        "client_secret": os.environ.get('GITHUB_CLIENT_SECRET', '1608b431a4c9aad3690f300a83ca6329b3a10e70'),
        "redirect_uri": os.environ.get('GITHUB_REDIRECT_URI', '/auth/github/callback')
    }
}

class Config:
    """
    Base configuration for Flask application
    """
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey-change-in-production'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Database configuration
    DATABASE_CONFIG = db_config
    
    # Flask configuration
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """
    Development configuration
    """
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """
    Testing configuration
    """
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    """
    Production configuration
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
