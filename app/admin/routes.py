"""
Admin Routes
Handles admin dashboard, user management, and content management
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.utils.decorators import admin_required, login_required
from app.utils.db import execute_query, execute_insert_update_delete, get_user_by_id

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def index():
    """Admin home - redirect to dashboard"""
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Admin dashboard - shows statistics and overview
    """
    try:
        # Get statistics
        stats = {
            'students': execute_query("SELECT COUNT(*) as count FROM users WHERE role='student'", fetch_one=True)['count'],
            'teachers': execute_query("SELECT COUNT(*) as count FROM users WHERE role='teacher'", fetch_one=True)['count'],
            'courses': 0,  # You can add courses table later
            'quizzes': 0   # You can add quizzes table later
        }
        
        return render_template('admin/dashboard.html', stats=stats, user_name=session.get('user_name'))
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html', stats={}, user_name=session.get('user_name'))

@admin_bp.route('/students')
@admin_required
def students():
    """
    Manage students
    """
    students = execute_query("SELECT id, name, email, created_at FROM users WHERE role='student'")
    return render_template('admin/students.html', students=students, user_name=session.get('user_name'))

@admin_bp.route('/students/<int:student_id>/delete', methods=['POST'])
@admin_required
def delete_student(student_id):
    """
    Delete a student
    """
    try:
        result = execute_insert_update_delete("DELETE FROM users WHERE id=%s AND role='student'", (student_id,))
        if result['affected'] > 0:
            flash('Student deleted successfully', 'success')
        else:
            flash('Student not found', 'error')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'error')
    
    return redirect(url_for('admin.students'))

@admin_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    """
    Edit student information
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        
        if not name or not email:
            flash('Name and email are required', 'error')
            return redirect(url_for('admin.edit_student', student_id=student_id))
        
        try:
            execute_insert_update_delete(
                "UPDATE users SET name=%s, email=%s WHERE id=%s AND role='student'",
                (name, email, student_id)
            )
            flash('Student updated successfully', 'success')
            return redirect(url_for('admin.students'))
        except Exception as e:
            flash(f'Error updating student: {str(e)}', 'error')
            return redirect(url_for('admin.edit_student', student_id=student_id))
    
    student = execute_query("SELECT * FROM users WHERE id=%s AND role='student'", (student_id,), fetch_one=True)
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/edit_student.html', student=student, user_name=session.get('user_name'))

@admin_bp.route('/teachers')
@admin_required
def teachers():
    """
    Manage teachers
    """
    teachers = execute_query("SELECT id, name, email, created_at FROM users WHERE role='teacher'")
    return render_template('admin/teachers.html', teachers=teachers, user_name=session.get('user_name'))

@admin_bp.route('/teachers/<int:teacher_id>/delete', methods=['POST'])
@admin_required
def delete_teacher(teacher_id):
    """
    Delete a teacher
    """
    try:
        result = execute_insert_update_delete("DELETE FROM users WHERE id=%s AND role='teacher'", (teacher_id,))
        if result['affected'] > 0:
            flash('Teacher deleted successfully', 'success')
        else:
            flash('Teacher not found', 'error')
    except Exception as e:
        flash(f'Error deleting teacher: {str(e)}', 'error')
    
    return redirect(url_for('admin.teachers'))

@admin_bp.route('/courses')
@admin_required
def courses():
    """
    Manage courses
    """
    # This will be implemented once you have a courses table
    courses = []
    return render_template('admin/courses.html', courses=courses, user_name=session.get('user_name'))

@admin_bp.route('/settings')
@admin_required
def settings():
    """
    Admin settings
    """
    admin = get_user_by_id(session.get('user_id'))
    return render_template('admin/settings.html', admin=admin, user_name=session.get('user_name'))

@admin_bp.route('/settings/update', methods=['POST'])
@admin_required
def update_settings():
    """
    Update admin settings
    """
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    
    if not name or not email:
        flash('Name and email are required', 'error')
        return redirect(url_for('admin.settings'))
    
    try:
        execute_insert_update_delete(
            "UPDATE users SET name=%s, email=%s WHERE id=%s",
            (name, email, session.get('user_id'))
        )
        session['user_name'] = name
        session['email'] = email
        flash('Settings updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')
    
    return redirect(url_for('admin.settings'))
