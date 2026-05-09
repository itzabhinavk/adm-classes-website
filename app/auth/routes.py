"""
Authentication Routes
Handles user login, logout, and registration
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.db import get_user_by_email, create_user, user_exists

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
        try:
            user = get_user_by_email(email)
        except Exception as err:
            flash('Database connection failed. Please try again later. some time wait plzz', 'error')
            return redirect(url_for('auth.login'))
        
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
    Student/Teacher registration route
    """
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        name = f"{first_name} {last_name}".strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', 'student').strip()
        agree_terms = request.form.get('agree_terms')

        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All required fields must be filled', 'error')
            return redirect(url_for('auth.register'))

        if not agree_terms:
            flash('You must agree to the terms and conditions', 'error')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return redirect(url_for('auth.register'))

        # Check if email already exists
        try:
            if user_exists(email):
                flash('Email already registered', 'error')
                return redirect(url_for('auth.register'))
        except Exception as err:
            flash('Database connection failed. Please try again later.', 'error')
            return redirect(url_for('auth.register'))

        # Create user
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            create_user(name, email, hashed_password, role, phone)
            flash(f'Registration successful as {role}! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as err:
            flash(f'An error occurred during registration: {err}', 'error')
            return redirect(url_for('auth.register'))

    return render_template('register.html')
def teacher_register():
    """
    Teacher registration route - goes to pending approval
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        subjects = request.form.getlist('subjects')
        experience = request.form.get('experience', '').strip()
        agree_terms = request.form.get('agree_terms')

        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All required fields must be filled', 'error')
            return redirect(url_for('auth.teacher_register'))

        if not subjects:
            flash('Please select at least one subject you can teach', 'error')
            return redirect(url_for('auth.teacher_register'))

        if not agree_terms:
            flash('You must agree to the Terms & Conditions', 'error')
            return redirect(url_for('auth.teacher_register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.teacher_register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return redirect(url_for('auth.teacher_register'))

        # Check if email already exists in users or pending
        try:
            from app.utils.db import execute_query
            existing_user = execute_query("SELECT id FROM users WHERE email=%s", (email,), fetch_one=True)
            existing_pending = execute_query("SELECT id FROM teacher_pending WHERE email=%s", (email,), fetch_one=True)

            if existing_user or existing_pending:
                flash('Email already registered', 'error')
                return redirect(url_for('auth.teacher_register'))
        except Exception as err:
            flash('Database connection failed. Please try again later.', 'error')
            return redirect(url_for('auth.teacher_register'))

        # Create pending teacher registration
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            subjects_str = ','.join(subjects)

            execute_query(
                "INSERT INTO teacher_pending (name, email, password, phone, requested_subjects) VALUES (%s, %s, %s, %s, %s)",
                (name, email, hashed_password, phone, subjects_str)
            )

            flash('Registration submitted! Your application will be reviewed by admin within 24 hours.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as err:
            flash('An error occurred during registration. Please try again later.', 'error')
            return redirect(url_for('auth.teacher_register'))

    return render_template('auth/teacher_register.html')

@auth_bp.route('/logout')
def logout():
    """
    User logout route
    """
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

# ==================== OAuth Routes ====================

@auth_bp.route('/google')
def google_login():
    """
    Google OAuth login - redirects to Google consent screen
    """
    from config import OAUTH_CONFIG
    
    google_config = OAUTH_CONFIG.get('google', {})
    client_id = google_config.get('client_id', '')
    redirect_uri = google_config.get('redirect_uri', '')
    
    if not client_id:
        flash('Google OAuth is not configured. Please contact administrator.', 'error')
        return redirect(url_for('auth.login'))
    
    # Google OAuth URL
    google_auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?'
    google_auth_url += f'client_id={client_id}'
    google_auth_url += f'&redirect_uri={request.host_url}{redirect_uri[1:]}'
    google_auth_url += '&response_type=code'
    google_auth_url += '&scope=email profile'
    google_auth_url += '&access_type=online'
    
    return redirect(google_auth_url)

@auth_bp.route('/google/callback')
def google_callback():
    """
    Google OAuth callback - handles the authorization code
    """
    from config import OAUTH_CONFIG
    import requests
    
    code = request.args.get('code')
    if not code:
        flash('Google login failed. No authorization code received.', 'error')
        return redirect(url_for('auth.login'))
    
    google_config = OAUTH_CONFIG.get('google', {})
    client_id = google_config.get('client_id', '')
    client_secret = google_config.get('client_secret', '')
    redirect_uri = google_config.get('redirect_uri', '')
    
    # Exchange code for token
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': request.host_url + redirect_uri[1:],
        'grant_type': 'authorization_code'
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            flash('Google login failed. Could not get access token.', 'error')
            return redirect(url_for('auth.login'))
        
        # Get user info from Google
        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {token_json["access_token"]}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()
        
        if 'email' not in userinfo:
            flash('Google login failed. Could not get user info.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user exists or create new one
        email = userinfo['email']
        name = userinfo.get('name', email.split('@')[0])
        
        # Check if user exists
        existing_user = get_user_by_email(email)
        
        if existing_user:
            # User exists, log them in
            session['user_id'] = existing_user['id']
            session['user_name'] = existing_user.get('name', name)
            session['email'] = existing_user['email']
            session['role'] = existing_user['role']
            session['oauth_provider'] = 'google'
        else:
            # Create new user (student by default for OAuth)
            new_user = create_user(
                name=name,
                email=email,
                password=generate_password_hash(f'google_{email}_{os.urandom(16).hex()}'),
                role='student',
                phone=''
            )
            
            if new_user:
                session['user_id'] = new_user['id']
                session['user_name'] = name
                session['email'] = email
                session['role'] = 'student'
                session['oauth_provider'] = 'google'
                flash('Account created successfully via Google!', 'success')
            else:
                flash('Failed to create account via Google.', 'error')
                return redirect(url_for('auth.login'))
        
        # Redirect to appropriate dashboard
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif session.get('role') == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
            
    except Exception as e:
        flash(f'Google login error: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/github')
def github_login():
    """
    GitHub OAuth login - redirects to GitHub consent screen
    """
    from config import OAUTH_CONFIG
    
    github_config = OAUTH_CONFIG.get('github', {})
    client_id = github_config.get('client_id', '')
    redirect_uri = github_config.get('redirect_uri', '')
    
    if not client_id:
        flash('GitHub OAuth is not configured. Please contact administrator.', 'error')
        return redirect(url_for('auth.login'))
    
    # GitHub OAuth URL
    github_auth_url = 'https://github.com/login/oauth/authorize?'
    github_auth_url += f'client_id={client_id}'
    github_auth_url += f'&redirect_uri={request.host_url}{redirect_uri[1:]}'
    github_auth_url += '&scope=user:email'
    
    return redirect(github_auth_url)

@auth_bp.route('/github/callback')
def github_callback():
    """
    GitHub OAuth callback - handles the authorization code
    """
    from config import OAUTH_CONFIG
    import requests
    
    code = request.args.get('code')
    if not code:
        flash('GitHub login failed. No authorization code received.', 'error')
        return redirect(url_for('auth.login'))
    
    github_config = OAUTH_CONFIG.get('github', {})
    client_id = github_config.get('client_id', '')
    client_secret = github_config.get('client_secret', '')
    redirect_uri = github_config.get('redirect_uri', '')
    
    # Exchange code for token
    token_url = 'https://github.com/login/oauth/access_token'
    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': request.host_url + redirect_uri[1:]
    }
    headers = {'Accept': 'application/json'}
    
    try:
        token_response = requests.post(token_url, json=token_data, headers=headers)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            flash('GitHub login failed. Could not get access token.', 'error')
            return redirect(url_for('auth.login'))
        
        # Get user info from GitHub
        userinfo_url = 'https://api.github.com/user'
        headers = {'Authorization': f'token {token_json["access_token"]}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()
        
        if 'login' not in userinfo:
            flash('GitHub login failed. Could not get user info.', 'error')
            return redirect(url_for('auth.login'))
        
        # Get email if not public
        email = userinfo.get('email')
        if not email:
            emails_response = requests.get('https://api.github.com/user/emails', headers=headers)
            emails = emails_response.json()
            if emails:
                email = emails[0].get('email', f"{userinfo['login']}@github.com")
        
        if not email:
            email = f"{userinfo['login']}@github.com"
        
        name = userinfo.get('name', userinfo['login'])
        
        # Check if user exists or create new one
        existing_user = get_user_by_email(email)
        
        if existing_user:
            # User exists, log them in
            session['user_id'] = existing_user['id']
            session['user_name'] = existing_user.get('name', name)
            session['email'] = existing_user['email']
            session['role'] = existing_user['role']
            session['oauth_provider'] = 'github'
        else:
            # Create new user (student by default for OAuth)
            new_user = create_user(
                name=name,
                email=email,
                password=generate_password_hash(f'github_{email}_{os.urandom(16).hex()}'),
                role='student',
                phone=''
            )
            
            if new_user:
                session['user_id'] = new_user['id']
                session['user_name'] = name
                session['email'] = email
                session['role'] = 'student'
                session['oauth_provider'] = 'github'
                flash('Account created successfully via GitHub!', 'success')
            else:
                flash('Failed to create account via GitHub.', 'error')
                return redirect(url_for('auth.login'))
        
        # Redirect to appropriate dashboard
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif session.get('role') == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
            
    except Exception as e:
        flash(f'GitHub login error: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/')
def index():
    """
    Auth index route - redirects to login
    """
    return redirect(url_for('auth.login'))
