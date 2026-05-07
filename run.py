"""
ADM Classes - Main Application Entry Point
Flask-based educational management system
"""

from flask import Flask, redirect, url_for, session
from config import Config



from app import create_app

app = create_app(Config)

@app.route('/')
def index():
    """
    Root route - redirect to appropriate dashboard based on user role
    """
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif role == 'student':
            return redirect(url_for('student.dashboard'))
    
    return redirect(url_for('auth.login'))

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Page Not Found</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            h1 { color: #333; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>404 - Page Not Found</h1>
        <p>The page you are looking for does not exist.</p>
        <a href="/">Go Home</a>
    </body>
    </html>
    ''', 404

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Access Forbidden</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            h1 { color: #d9534f; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>403 - Access Forbidden</h1>
        <p>You do not have permission to access this resource.</p>
        <a href="/">Go Home</a>
    </body>
    </html>
    ''', 403

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Server Error</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            h1 { color: #d9534f; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>500 - Server Error</h1>
        <p>An unexpected error occurred. Please try again later.</p>
        <a href="/">Go Home</a>
    </body>
    </html>
    ''', 500

if __name__ == "__main__":
    # Run the Flask application
    # Debug mode: True (set to False in production)
    # Host: 0.0.0.0 (accessible from all network interfaces)
    # Port: 5000
    app.run(debug=True, host='0.0.0.0', port=5000)