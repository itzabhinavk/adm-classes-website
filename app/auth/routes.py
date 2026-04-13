"""
Authentication Routes
Handles user login, logout, and registration
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.db import get_user_by_email, create_user, user_exists
import mysql.connector

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route with role-based authentication
    """
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif session.get('role') == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif session.get('role') == 'student':
            return redirect(url_for('student.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'student').strip()
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('auth.login'))
        
        if role not in ['student', 'teacher', 'admin']:
            flash('Invalid role selected', 'error')
            return redirect(url_for('auth.login'))
        
        # Get user from database
        user = get_user_by_email(email)
        
        # Verify user exists, password is correct, and role matches (for security)
        if user and check_password_hash(user['password'], password) and user['role'] == role:
            # Set session
            session['user_id'] = user['id']
            session['user_name'] = user['name'] if 'name' in user else user.get('first_name', '') + ' ' + user.get('last_name', '')
            session['email'] = user['email']
            session['role'] = user['role']
            session.permanent = True
            
            # Redirect based on role
            if role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            elif role == 'student':
                return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email, password, or role', 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route with role selection
    """
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif session.get('role') == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif session.get('role') == 'student':
            return redirect(url_for('student.dashboard'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', 'student').strip()
        agree_terms = request.form.get('agree_terms')
        
        # Validation
        if not all([first_name, last_name, email, password, confirm_password]):
            flash('All required fields must be filled', 'error')
            return redirect(url_for('auth.register'))
        
        if not agree_terms:
            flash('You must agree to the Terms & Conditions', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return redirect(url_for('auth.register'))
        
        if role not in ['student', 'teacher']:
            flash('Invalid role selected', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        if user_exists(email):
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user with proper password hashing
        try:
            full_name = f"{first_name} {last_name}"
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            create_user(full_name, email, hashed_password, role)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except mysql.connector.Error as e:
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """
    User logout route
    """
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
def index():
    """
    Auth index route - redirects to login
    """
    return redirect(url_for('auth.login'))
