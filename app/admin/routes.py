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
            'courses': execute_query("SELECT COUNT(*) as count FROM courses", fetch_one=True)['count'],
            'quizzes': 0,
            'pending_requests': execute_query("SELECT COUNT(*) as count FROM student_courses WHERE status='pending'", fetch_one=True)['count']
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
    students = execute_query("SELECT id, name, email, phone, created_at FROM users WHERE role='student' ORDER BY created_at DESC")
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
    teachers = execute_query("SELECT id, name, email, phone, specialization, created_at FROM users WHERE role='teacher' ORDER BY created_at DESC")
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
    try:
        courses = execute_query("SELECT * FROM courses ORDER BY created_at DESC")
        return render_template('admin/courses.html', courses=courses, user_name=session.get('user_name'))
    except Exception as e:
        flash(f'Error loading courses: {str(e)}', 'error')
        return render_template('admin/courses.html', courses=[], user_name=session.get('user_name'))

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@admin_required
def add_course():
    """
    Add new course
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        level = request.form.get('level', '').strip()
        price = request.form.get('price', '0').strip()

        if not all([title, description, category, level]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin.add_course'))

        try:
            execute_insert_update_delete(
                "INSERT INTO courses (title, description, category, level, price) VALUES (%s, %s, %s, %s, %s)",
                (title, description, category, level, float(price) if price else 0.00)
            )
            flash('Course added successfully', 'success')
            return redirect(url_for('admin.courses'))
        except Exception as e:
            flash(f'Error adding course: {str(e)}', 'error')
            return redirect(url_for('admin.add_course'))

    return render_template('admin/add_course.html', user_name=session.get('user_name'))

@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_course(course_id):
    """
    Edit course
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        level = request.form.get('level', '').strip()
        price = request.form.get('price', '0').strip()

        if not all([title, description, category, level]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin.edit_course', course_id=course_id))

        try:
            execute_insert_update_delete(
                "UPDATE courses SET title=%s, description=%s, category=%s, level=%s, price=%s WHERE id=%s",
                (title, description, category, level, float(price) if price else 0.00, course_id)
            )
            flash('Course updated successfully', 'success')
            return redirect(url_for('admin.courses'))
        except Exception as e:
            flash(f'Error updating course: {str(e)}', 'error')
            return redirect(url_for('admin.edit_course', course_id=course_id))

    course = execute_query("SELECT * FROM courses WHERE id=%s", (course_id,), fetch_one=True)
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('admin.courses'))

    return render_template('admin/edit_course.html', course=course, user_name=session.get('user_name'))

@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@admin_required
def delete_course(course_id):
    """
    Delete course
    """
    try:
        result = execute_insert_update_delete("DELETE FROM courses WHERE id=%s", (course_id,))
        if result['affected'] > 0:
            flash('Course deleted successfully', 'success')
        else:
            flash('Course not found', 'error')
    except Exception as e:
        flash(f'Error deleting course: {str(e)}', 'error')

    return redirect(url_for('admin.courses'))

@admin_bp.route('/student-requests')
@admin_required
def student_requests():
    """
    View student course requests
    """
    try:
        requests = execute_query("""
            SELECT sc.id, sc.student_id, sc.course_id, sc.status, sc.purchased_at,
                   u.name as student_name, u.email as student_email,
                   c.title as course_title, c.category, c.level
            FROM student_courses sc
            JOIN users u ON sc.student_id = u.id
            JOIN courses c ON sc.course_id = c.id
            WHERE sc.status = 'pending'
            ORDER BY sc.purchased_at DESC
        """)
        return render_template('admin/student_requests.html', requests=requests, user_name=session.get('user_name'))
    except Exception as e:
        flash(f'Error loading student requests: {str(e)}', 'error')
        return render_template('admin/student_requests.html', requests=[], user_name=session.get('user_name'))

@admin_bp.route('/student-requests/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_request(request_id):
    """
    Approve student course request
    """
    try:
        result = execute_insert_update_delete(
            "UPDATE student_courses SET status='approved' WHERE id=%s",
            (request_id,)
        )
        if result['affected'] > 0:
            flash('Student request approved successfully', 'success')
        else:
            flash('Request not found', 'error')
    except Exception as e:
        flash(f'Error approving request: {str(e)}', 'error')

    return redirect(url_for('admin.student_requests'))

@admin_bp.route('/student-requests/<int:request_id>/reject', methods=['POST'])
@admin_required
def reject_request(request_id):
    """
    Reject student course request
    """
    try:
        result = execute_insert_update_delete(
            "UPDATE student_courses SET status='rejected' WHERE id=%s",
            (request_id,)
        )
        if result['affected'] > 0:
            flash('Student request rejected', 'success')
        else:
            flash('Request not found', 'error')
    except Exception as e:
        flash(f'Error rejecting request: {str(e)}', 'error')

    return redirect(url_for('admin.student_requests'))

@admin_bp.route('/assign-teacher', methods=['GET', 'POST'])
@admin_required
def assign_teacher():
    """
    Assign teacher to courses
    """
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        course_ids = request.form.getlist('course_ids')

        if not teacher_id or not course_ids:
            flash('Please select teacher and courses', 'error')
            return redirect(url_for('admin.assign_teacher'))

        try:
            # Remove existing assignments for these courses
            for course_id in course_ids:
                execute_insert_update_delete(
                    "DELETE FROM teacher_courses WHERE course_id=%s",
                    (course_id,)
                )

            # Assign new teacher
            for course_id in course_ids:
                execute_insert_update_delete(
                    "INSERT INTO teacher_courses (teacher_id, course_id) VALUES (%s, %s)",
                    (teacher_id, course_id)
                )

            flash('Teacher assigned to courses successfully', 'success')
            return redirect(url_for('admin.assign_teacher'))
        except Exception as e:
            flash(f'Error assigning teacher: {str(e)}', 'error')
            return redirect(url_for('admin.assign_teacher'))

    try:
        teachers = execute_query("SELECT id, name FROM users WHERE role='teacher'")
        courses = execute_query("SELECT id, title, category FROM courses")
        assignments = execute_query("""
            SELECT tc.course_id, tc.teacher_id, u.name as teacher_name, c.title as course_title
            FROM teacher_courses tc
            JOIN users u ON tc.teacher_id = u.id
            JOIN courses c ON tc.course_id = c.id
        """)
        print(f"DEBUG - Teachers: {len(teachers)}, Courses: {len(courses)}, Assignments: {len(assignments)}")
        return render_template('admin/assign_teacher.html',
                             teachers=teachers,
                             courses=courses,
                             assignments=assignments,
                             user_name=session.get('user_name'))
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        flash(f'Error loading data: {str(e)}', 'error')
        return render_template('admin/assign_teacher.html',
                             teachers=[],
                             courses=[],
                             assignments=[],
                             user_name=session.get('user_name'))

@admin_bp.route('/settings')
@admin_required
def settings():
    """
    Admin settings
    """
    admin = get_user_by_id(session.get('user_id'))
    return render_template('admin/settings.html', admin=admin, user_name=session.get('user_name'))

@admin_bp.route('/pending-teachers')
@admin_required
def pending_teachers():
    """
    View pending teacher registrations
    """
    try:
        pending_teachers = execute_query("SELECT * FROM teacher_pending ORDER BY created_at DESC")
        return render_template('admin/pending_teachers.html', pending_teachers=pending_teachers, user_name=session.get('user_name'))
    except Exception as e:
        flash(f'Error loading pending teachers: {str(e)}', 'error')
        return render_template('admin/pending_teachers.html', pending_teachers=[], user_name=session.get('user_name'))

@admin_bp.route('/pending-teachers/<int:pending_id>/approve', methods=['GET', 'POST'])
@admin_required
def approve_teacher(pending_id):
    """
    Approve pending teacher and assign subjects
    """
    if request.method == 'POST':
        assigned_subjects = request.form.getlist('subjects')

        if not assigned_subjects:
            flash('Please assign at least one subject', 'error')
            return redirect(url_for('admin.approve_teacher', pending_id=pending_id))

        try:
            # Get pending teacher data
            pending_teacher = execute_query("SELECT * FROM teacher_pending WHERE id=%s", (pending_id,), fetch_one=True)

            if not pending_teacher:
                flash('Pending teacher not found', 'error')
                return redirect(url_for('admin.pending_teachers'))

            # Create user account
            user_result = execute_insert_update_delete(
                "INSERT INTO users (name, email, password, phone, role) VALUES (%s, %s, %s, %s, 'teacher')",
                (pending_teacher['name'], pending_teacher['email'], pending_teacher['password'], pending_teacher['phone'])
            )

            teacher_id = user_result['last_id']

            # Assign subjects
            for subject in assigned_subjects:
                execute_insert_update_delete(
                    "INSERT INTO teacher_subjects (teacher_id, subject_name) VALUES (%s, %s)",
                    (teacher_id, subject)
                )

            # Remove from pending
            execute_insert_update_delete("DELETE FROM teacher_pending WHERE id=%s", (pending_id,))

            flash(f'Teacher {pending_teacher["name"]} approved and subjects assigned successfully', 'success')
            return redirect(url_for('admin.pending_teachers'))

        except Exception as e:
            flash(f'Error approving teacher: {str(e)}', 'error')
            return redirect(url_for('admin.approve_teacher', pending_id=pending_id))

    # GET request - show approval form
    try:
        pending_teacher = execute_query("SELECT * FROM teacher_pending WHERE id=%s", (pending_id,), fetch_one=True)

        if not pending_teacher:
            flash('Pending teacher not found', 'error')
            return redirect(url_for('admin.pending_teachers'))

        requested_subjects = pending_teacher['requested_subjects'].split(',') if pending_teacher['requested_subjects'] else []

        return render_template('admin/approve_teacher.html',
                             pending_teacher=pending_teacher,
                             requested_subjects=requested_subjects,
                             user_name=session.get('user_name'))

    except Exception as e:
        flash(f'Error loading teacher details: {str(e)}', 'error')
        return redirect(url_for('admin.pending_teachers'))

@admin_bp.route('/pending-teachers/<int:pending_id>/reject', methods=['POST'])
@admin_required
def reject_teacher(pending_id):
    """
    Reject pending teacher application
    """
    try:
        result = execute_insert_update_delete("DELETE FROM teacher_pending WHERE id=%s", (pending_id,))
        if result['affected'] > 0:
            flash('Teacher application rejected', 'success')
        else:
            flash('Pending teacher not found', 'error')
    except Exception as e:
        flash(f'Error rejecting teacher: {str(e)}', 'error')

    return redirect(url_for('admin.pending_teachers'))

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
