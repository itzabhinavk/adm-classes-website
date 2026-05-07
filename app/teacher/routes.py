"""
Teacher Routes
Handles teacher dashboard, courses, and content management
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.decorators import teacher_required, login_required
from app.utils.db import (
    execute_query,
    execute_insert_update_delete,
    get_user_by_id,
    get_teacher_courses,
)

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/')
@teacher_required
def index():
    """Teacher home - redirect to dashboard"""
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    """
    Teacher dashboard - shows courses and statistics
    """
    try:
        teacher_id = session.get('user_id')

        # Get assigned courses (from teacher_courses table)
        assigned_courses = execute_query(
            "SELECT c.id, c.title, c.category "
            "FROM teacher_courses tc "
            "JOIN courses c ON tc.course_id = c.id "
            "WHERE tc.teacher_id = %s ORDER BY c.title",
            (teacher_id,)
        )

        # Get lecture stats
        lecture_stats = execute_query(
            "SELECT COUNT(*) as total_lectures FROM lectures WHERE teacher_id=%s",
            (teacher_id,),
            fetch_one=True
        )

        # Get student count (students enrolled in teacher's courses)
        student_count = execute_query(
            "SELECT COUNT(DISTINCT sc.student_id) AS count "
            "FROM student_courses sc "
            "JOIN teacher_courses tc ON sc.course_id = tc.course_id "
            "WHERE tc.teacher_id = %s AND sc.status='approved'",
            (teacher_id,),
            fetch_one=True
        )

        stats = {
            'subjects': len(assigned_courses),
            'lectures': lecture_stats['total_lectures'] if lecture_stats else 0,
            'students': student_count['count'] if student_count else 0
        }

        return render_template('teacher/dashboard.html',
                             stats=stats,
                             assigned_subjects=assigned_courses,
                             user_name=session.get('user_name'))
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('teacher/dashboard.html', stats={}, assigned_subjects=[], user_name=session.get('user_name'))

@teacher_bp.route('/courses')
@teacher_required
def courses():
    """
    List teacher's courses
    """
    try:
        courses = get_teacher_courses(session.get('user_id'))
    except Exception:
        courses = []
    return render_template('teacher/my-courses.html', courses=courses, user_name=session.get('user_name'))

@teacher_bp.route('/add-content', methods=['GET', 'POST'])
@teacher_required
def add_content():
    """
    Add course content
    """
    teacher_id = session.get('user_id')

    # Get assigned courses for dropdown (from teacher_courses table)
    assigned_courses = execute_query(
        "SELECT c.id, c.title, c.category "
        "FROM teacher_courses tc "
        "JOIN courses c ON tc.course_id = c.id "
        "WHERE tc.teacher_id = %s ORDER BY c.title",
        (teacher_id,)
    )

    if request.method == 'POST':
        course_id = request.form.get('course_id', '').strip()
        class_mode = request.form.get('class_mode', '').strip()
        class_title = request.form.get('class_title', '').strip()
        start_date = request.form.get('start_date', '').strip()
        start_time = request.form.get('start_time', '').strip()
        duration = request.form.get('duration', '').strip()
        description = request.form.get('description', '').strip()
        stream_link = request.form.get('stream_link', '').strip()
        video_link = request.form.get('video_link', '').strip()

        if not all([course_id, class_mode, class_title]):
            flash('Course, class mode, and title are required', 'error')
            return redirect(url_for('teacher.add_content'))

        # Verify course is assigned to teacher
        course_check = execute_query(
            "SELECT id FROM teacher_courses WHERE teacher_id=%s AND course_id=%s",
            (teacher_id, course_id),
            fetch_one=True
        )

        if not course_check:
            flash('You are not authorized to add content for this course', 'error')
            return redirect(url_for('teacher.add_content'))

        if class_mode == 'live' and not stream_link:
            flash('Live class requires a meeting link', 'error')
            return redirect(url_for('teacher.add_content'))

        if class_mode == 'link' and not video_link:
            flash('Video link is required for link classes', 'error')
            return redirect(url_for('teacher.add_content'))

        try:
            # Get course title from course_id
            course = execute_query(
                "SELECT title, category FROM courses WHERE id=%s",
                (course_id,),
                fetch_one=True
            )
            
            # Create lecture
            lecture_result = execute_insert_update_delete(
                "INSERT INTO lectures (teacher_id, course_id, subject_name, class_mode, title, description, start_date, start_time, duration, stream_link, video_link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (teacher_id, course_id, course['category'] if course else '', class_mode, class_title, description, start_date or None, start_time or None, duration or None, stream_link or None, video_link or None)
            )

            lecture_id = lecture_result['last_id']
            flash(f'Lecture "{class_title}" created successfully! You can now upload notes.', 'success')

            # Redirect to upload notes page for this lecture
            return redirect(url_for('teacher.upload_notes', lecture_id=lecture_id))

        except Exception as e:
            flash(f'Error creating lecture: {str(e)}', 'error')
            return redirect(url_for('teacher.add_content'))

    return render_template('teacher/add-content.html', assigned_subjects=assigned_courses, user_name=session.get('user_name'))

@teacher_bp.route('/profile')
@teacher_required
def profile():
    """
    Teacher profile
    """
    teacher = get_user_by_id(session.get('user_id'))
    return render_template('teacher/profile.html', teacher=teacher, user_name=session.get('user_name'))

@teacher_bp.route('/profile/update', methods=['POST'])
@teacher_required
def update_profile():
    """
    Update teacher profile
    """
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    
    if not name or not email:
        flash('Name and email are required', 'error')
        return redirect(url_for('teacher.profile'))
    
    try:
        execute_insert_update_delete(
            "UPDATE users SET name=%s, email=%s WHERE id=%s",
            (name, email, session.get('user_id'))
        )
        session['user_name'] = name
        session['email'] = email
        flash('Profile updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'error')
    
    return redirect(url_for('teacher.profile'))

@teacher_bp.route('/settings')
@teacher_required
def settings():
    """
    Teacher settings
    """
    teacher = get_user_by_id(session.get('user_id'))
    return render_template('teacher/setting.html', teacher=teacher, user_name=session.get('user_name'))

@teacher_bp.route('/upload-notes/<int:lecture_id>', methods=['GET', 'POST'])
@teacher_required
def upload_notes(lecture_id):
    """
    Upload notes for a lecture
    """
    teacher_id = session.get('user_id')

    # Verify lecture belongs to teacher
    lecture = execute_query(
        "SELECT * FROM lectures WHERE id=%s AND teacher_id=%s",
        (lecture_id, teacher_id),
        fetch_one=True
    )

    if not lecture:
        flash('Lecture not found or access denied', 'error')
        return redirect(url_for('teacher.my_lectures'))

    if request.method == 'POST':
        if 'notes_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)

        file = request.files['notes_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        if file:
            # Save file to uploads directory
            import os
            from werkzeug.utils import secure_filename

            upload_dir = os.path.join('static', 'uploads', 'notes')
            os.makedirs(upload_dir, exist_ok=True)

            filename = secure_filename(f"lecture_{lecture_id}_{file.filename}")
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            try:
                # Save to database
                execute_insert_update_delete(
                    "INSERT INTO lecture_notes (lecture_id, file_name, file_path) VALUES (%s, %s, %s)",
                    (lecture_id, file.filename, file_path)
                )

                flash('Notes uploaded successfully!', 'success')
                return redirect(url_for('teacher.my_lectures'))

            except Exception as e:
                flash(f'Error uploading notes: {str(e)}', 'error')
                return redirect(request.url)

    return render_template('teacher/upload_notes.html', lecture=lecture, user_name=session.get('user_name'))

@teacher_bp.route('/my-lectures')
@teacher_required
def my_lectures():
    """
    View teacher's lectures
    """
    teacher_id = session.get('user_id')

    try:
        lectures = execute_query(
            "SELECT l.*, COUNT(ln.id) as notes_count, CASE WHEN COUNT(ln.id) > 0 THEN 1 ELSE 0 END as notes_uploaded FROM lectures l LEFT JOIN lecture_notes ln ON l.id = ln.lecture_id WHERE l.teacher_id=%s GROUP BY l.id ORDER BY l.created_at DESC",
            (teacher_id,)
        )

        # Calculate stats
        total_lectures = len(lectures)
        live_lectures = sum(1 for l in lectures if l['class_mode'] == 'live')
        uploaded_lectures = sum(1 for l in lectures if l['class_mode'] == 'upload')
        notes_count = sum(1 for l in lectures if l['notes_uploaded'])

    except Exception as e:
        flash(f'Error loading lectures: {str(e)}', 'error')
        lectures = []
        total_lectures = live_lectures = uploaded_lectures = notes_count = 0

    return render_template('teacher/my-courses.html',
                         lectures=lectures,
                         total_lectures=total_lectures,
                         live_lectures=live_lectures,
                         uploaded_lectures=uploaded_lectures,
                         notes_count=notes_count,
                         user_name=session.get('user_name'))

@teacher_bp.route('/students')
@teacher_required
def students():
    """
    View students enrolled in teacher's courses
    """
    try:
        teacher_id = session.get('user_id')
        students = execute_query(
            "SELECT DISTINCT u.id, u.name, u.email, u.phone, sc.purchased_at, sc.status "
            "FROM student_courses sc "
            "JOIN users u ON sc.student_id = u.id "
            "JOIN teacher_courses tc ON sc.course_id = tc.course_id "
            "WHERE tc.teacher_id = %s "
            "ORDER BY sc.purchased_at DESC",
            (teacher_id,)
        )
    except Exception as e:
        flash(f'Error loading students: {str(e)}', 'error')
        students = []
    return render_template('teacher/student.html', students=students, user_name=session.get('user_name'))
