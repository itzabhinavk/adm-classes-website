"""
Student Routes
Handles student dashboard and student-facing pages.
"""
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.utils.decorators import student_required
from app.utils.db import get_courses, get_student_courses, get_course_by_id, student_is_enrolled, enroll_student_in_course

student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('/')
@student_required
def index():
    """Student home - redirect to dashboard."""
    return redirect(url_for('student.dashboard'))


@student_bp.route('/dashboard')
@student_required
def dashboard():
    """Student dashboard."""
    try:
        courses = get_courses()
        enrolled_courses = get_student_courses(session.get('user_id'))
        enrolled_ids = [course['id'] for course in enrolled_courses]
    except Exception:
        courses = []
        enrolled_courses = []
        enrolled_ids = []
    return render_template(
        'student/index.html',
        user_name=session.get('user_name'),
        courses=courses,
        enrolled_courses=enrolled_courses,
        enrolled_ids=enrolled_ids
    )


@student_bp.route('/courses')
@student_required
def courses():
    """Student courses page."""
    try:
        courses = get_courses()
        enrolled_courses = get_student_courses(session.get('user_id'))
        enrolled_ids = [course['id'] for course in enrolled_courses if course['status'] == 'approved']
    except Exception:
        courses = []
        enrolled_courses = []
        enrolled_ids = []

    return render_template(
        'student/courses.html',
        courses=courses,
        enrolled_courses=enrolled_courses,
        enrolled_ids=enrolled_ids,
        user_name=session.get('user_name')
    )


@student_bp.route('/request/<int:course_id>', methods=['POST'])
@student_required
def request_course(course_id):
    """Request enrollment in a course (admin approval required)."""
    student_id = session.get('user_id')
    try:
        from app.utils.db import execute_query, execute_insert_update_delete

        course = execute_query("SELECT * FROM courses WHERE id=%s", (course_id,), fetch_one=True)
        if not course:
            flash('Course not found.', 'error')
            return redirect(url_for('student.courses'))

        # Check if already requested or enrolled
        existing = execute_query(
            "SELECT status FROM student_courses WHERE student_id=%s AND course_id=%s",
            (student_id, course_id),
            fetch_one=True
        )

        if existing:
            if existing['status'] == 'pending':
                flash('You have already requested this course. Waiting for admin approval.', 'info')
            elif existing['status'] == 'approved':
                flash('You are already enrolled in this course.', 'info')
            elif existing['status'] == 'rejected':
                flash('Your previous request was rejected. You can request again.', 'warning')
                # Allow re-request by updating status
                execute_insert_update_delete(
                    "UPDATE student_courses SET status='pending', purchased_at=NOW() WHERE student_id=%s AND course_id=%s",
                    (student_id, course_id)
                )
                flash('Course request submitted again!', 'success')
            return redirect(url_for('student.courses'))

        # Create new request
        execute_insert_update_delete(
            "INSERT INTO student_courses (student_id, course_id, price, status) VALUES (%s, %s, %s, 'pending')",
            (student_id, course_id, course['price'])
        )
        flash('Course request submitted! Waiting for admin approval.', 'success')
    except Exception as err:
        flash(f'Error requesting course: {err}', 'error')

    return redirect(url_for('student.courses'))

@student_bp.route('/my-requests')
@student_required
def my_requests():
    """View my course requests."""
    student_id = session.get('user_id')
    try:
        from app.utils.db import execute_query

        requests = execute_query("""
            SELECT sc.id, sc.status, sc.purchased_at,
                   c.title, c.category, c.level, c.price
            FROM student_courses sc
            JOIN courses c ON sc.course_id = c.id
            WHERE sc.student_id = %s
            ORDER BY sc.purchased_at DESC
        """, (student_id,))
    except Exception as e:
        flash(f'Error loading requests: {str(e)}', 'error')
        requests = []

    return render_template('student/my_requests.html', requests=requests, user_name=session.get('user_name'))


@student_bp.route('/my-courses')
@student_required
def my_courses():
    """Student approved courses page."""
    student_id = session.get('user_id')
    try:
        from app.utils.db import execute_query

        courses = execute_query("""
            SELECT c.id, c.title, c.description, c.category, c.level, c.price,
                   u.name AS teacher_name, sc.purchased_at
            FROM student_courses sc
            JOIN courses c ON sc.course_id = c.id
            LEFT JOIN teacher_courses tc ON c.id = tc.course_id
            LEFT JOIN users u ON tc.teacher_id = u.id
            WHERE sc.student_id = %s AND sc.status = 'approved'
            ORDER BY sc.purchased_at DESC
        """, (student_id,))
    except Exception as e:
        flash(f'Error loading my courses: {str(e)}', 'error')
        courses = []

    return render_template('student/my_courses.html', courses=courses, user_name=session.get('user_name'))


@student_bp.route('/notes')
@student_required
def notes():
    """Student notes page - only for approved courses."""
    student_id = session.get('user_id')
    try:
        from app.utils.db import execute_query
        
        # Get notes only for approved courses
        notes = execute_query("""
            SELECT l.id, l.title, l.description, c.title as course_title, 
                   l.created_at, u.name as teacher_name
            FROM lectures l
            JOIN courses c ON l.course_id = c.id
            JOIN student_courses sc ON c.id = sc.course_id
            LEFT JOIN users u ON l.teacher_id = u.id
            WHERE sc.student_id = %s AND sc.status = 'approved'
            AND l.notes_content IS NOT NULL AND l.notes_content != ''
            ORDER BY l.created_at DESC
        """, (student_id,))
    except Exception as e:
        notes = []
    
    return render_template('student/notes.html', notes=notes, user_name=session.get('user_name'))


@student_bp.route('/<int:note_id>')
@student_required
def view_note(note_id):
    """View a specific note - only if student has access to that course."""
    student_id = session.get('user_id')
    try:
        from app.utils.db import execute_query
        
        # Check if student has access to this note's course
        note = execute_query("""
            SELECT l.id, l.title, l.notes_content, c.title as course_title,
                   u.name as teacher_name, l.created_at
            FROM lectures l
            JOIN courses c ON l.course_id = c.id
            JOIN student_courses sc ON c.id = sc.course_id
            LEFT JOIN users u ON l.teacher_id = u.id
            WHERE l.id = %s AND sc.student_id = %s AND sc.status = 'approved'
        """, (note_id, student_id), fetch_one=True)
        
        if not note:
            flash('You do not have access to this note or note not found.', 'error')
            return redirect(url_for('student.notes'))
    except Exception as e:
        flash(f'Error loading note: {str(e)}', 'error')
        return redirect(url_for('student.notes'))
    
    return render_template('student/note.html', note=note, user_name=session.get('user_name'))


@student_bp.route('/videos')
@student_required
def videos():
    """Student videos page - only for approved courses."""
    student_id = session.get('user_id')
    try:
        from app.utils.db import execute_query
        
        # Get videos only for approved courses
        videos = execute_query("""
            SELECT l.id, l.title, l.description, c.title as course_title,
                   l.video_url, l.created_at, u.name as teacher_name
            FROM lectures l
            JOIN courses c ON l.course_id = c.id
            JOIN student_courses sc ON c.id = sc.course_id
            LEFT JOIN users u ON l.teacher_id = u.id
            WHERE sc.student_id = %s AND sc.status = 'approved'
            AND l.video_url IS NOT NULL AND l.video_url != ''
            ORDER BY l.created_at DESC
        """, (student_id,))
    except Exception as e:
        videos = []
    
    return render_template('student/videos.html', videos=videos, user_name=session.get('user_name'))


@student_bp.route('/quiz')
@student_required
def quiz():
    """Student quiz page - only for approved courses."""
    student_id = session.get('user_id')
    try:
        from app.utils.db import execute_query
        
        # Get quiz info for approved courses
        quizzes = execute_query("""
            SELECT DISTINCT c.id, c.title, c.category
            FROM courses c
            JOIN student_courses sc ON c.id = sc.course_id
            WHERE sc.student_id = %s AND sc.status = 'approved'
            ORDER BY c.title
        """, (student_id,))
    except Exception as e:
        quizzes = []
    
    return render_template('student/quiz.html', quizzes=quizzes, user_name=session.get('user_name'))


@student_bp.route('/<int:quiz_id>')
@student_required
def take_quiz(quiz_id):
    """Take a specific quiz - only if student has access."""
    student_id = session.get('user_id')
    try:
        from app.utils.db import execute_query
        
        # Check if student has access to this course
        course = execute_query("""
            SELECT c.id, c.title FROM courses c
            JOIN student_courses sc ON c.id = sc.course_id
            WHERE sc.student_id = %s AND sc.status = 'approved' AND c.id = %s
        """, (student_id, quiz_id), fetch_one=True)
        
        if not course:
            flash('You do not have access to this quiz.', 'error')
            return redirect(url_for('student.quiz'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('student.quiz'))
    
    return render_template('student/quiz.html', quiz_id=quiz_id, course=course, user_name=session.get('user_name'))


@student_bp.route('/about')
@student_required
def about():
    """About page - always accessible."""
    return render_template('student/about.html', user_name=session.get('user_name'))


@student_bp.route('/contact')
@student_required
def contact():
    """Contact page - always accessible with teacher info."""
    try:
        from app.utils.db import execute_query
        
        # Get all teachers for contact info
        teachers = execute_query("""
            SELECT id, name, email, phone, specialization
            FROM users WHERE role = 'teacher'
            ORDER BY name
        """)
    except Exception as e:
        teachers = []
    
    return render_template('student/contact.html', teachers=teachers, user_name=session.get('user_name'))
