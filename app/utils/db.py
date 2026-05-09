"""
Database utility functions
"""
import os
import pymysql
from config import db_config
from flask import current_app

def get_db_connection():
    """
    Get a new database connection
    """
    try:
        
        return pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenvt('DB_PASSWORD', ),
            database=os.getenv('DB_NAME', ),
            port=int(os.getenv('DB_PORT', )),
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4',
            autocommit=False,
        )
    except Exception as err:
        raise ConnectionError(f"MySQL connection failed: {err}")

def execute_query(query, params=None, fetch_one=False):
    """
    Execute a SELECT query and return results
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or list)
        fetch_one: If True, return single row; otherwise return all rows
    
    Returns:
        Single row (dict) if fetch_one=True, list of rows otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params or ())
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()

def execute_insert_update_delete(query, params=None):
    """
    Execute an INSERT, UPDATE, or DELETE query
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or list)
    
    Returns:
        Number of affected rows, or last insert id for INSERT
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params or ())
        conn.commit()
        affected = cursor.rowcount
        last_id = cursor.lastrowid
        return {'affected': affected, 'last_id': last_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def user_exists(email):
    """
    Check if user exists by email
    """
    result = execute_query(
        "SELECT id FROM users WHERE email=%s",
        (email,),
        fetch_one=True
    )
    return result is not None

def get_user_by_email(email):
    """
    Get user by email
    """
    return execute_query(
        "SELECT * FROM users WHERE email=%s",
        (email,),
        fetch_one=True
    )

def get_user_by_id(user_id):
    """
    Get user by ID
    """
    return execute_query(
        "SELECT * FROM users WHERE id=%s",
        (user_id,),
        fetch_one=True
    )

def create_user(name, email, password, role='student', phone=None):
    """
    Create a new user
    """
    return execute_insert_update_delete(
        "INSERT INTO users (name, email, password, role, phone) VALUES (%s, %s, %s, %s, %s)",
        (name, email, password, role, phone)
    )


def get_courses():
    """
    Get available courses
    """
    return execute_query(
        "SELECT id, title, description, category, level, price FROM courses ORDER BY id"
    )


def get_course_by_id(course_id):
    """
    Get a single course by ID
    """
    return execute_query(
        "SELECT id, title, description, category, level, price FROM courses WHERE id=%s",
        (course_id,),
        fetch_one=True
    )


def get_course_by_title(title):
    """
    Get a single course by title
    """
    return execute_query(
        "SELECT id, title, description, category, level, price FROM courses WHERE title=%s",
        (title,),
        fetch_one=True
    )


def get_courses_with_teachers():
    """
    Get all courses with assigned teacher names
    """
    return execute_query(
        "SELECT c.id, c.title, c.description, c.category, c.level, c.price, u.id AS teacher_id, u.name AS teacher_name "
        "FROM courses c "
        "LEFT JOIN teacher_courses tc ON c.id = tc.course_id "
        "LEFT JOIN users u ON tc.teacher_id = u.id "
        "ORDER BY c.id"
    )


def create_course(title, description, category, level, price=0.00):
    """
    Create a new course
    """
    return execute_insert_update_delete(
        "INSERT INTO courses (title, description, category, level, price) VALUES (%s, %s, %s, %s, %s)",
        (title, description, category, level, price)
    )


def assign_teacher_to_course(teacher_id, course_id):
    """
    Assign a teacher to a course
    """
    return execute_insert_update_delete(
        "INSERT INTO teacher_courses (teacher_id, course_id) VALUES (%s, %s)",
        (teacher_id, course_id)
    )


def get_teacher_courses(teacher_id):
    """
    Get all courses assigned to a teacher
    """
    return execute_query(
        "SELECT c.id, c.title, c.description, c.category, c.level, c.price, tc.assigned_at "
        "FROM teacher_courses tc "
        "JOIN courses c ON tc.course_id = c.id "
        "WHERE tc.teacher_id = %s ORDER BY c.id",
        (teacher_id,)
    )


def enroll_student_in_course(student_id, course_id, price=0.00, status='active'):
    """
    Enroll a student (purchase a course)
    """
    return execute_insert_update_delete(
        "INSERT INTO student_courses (student_id, course_id, price, status) VALUES (%s, %s, %s, %s)",
        (student_id, course_id, price, status)
    )


def get_student_courses(student_id):
    """
    Get a student's enrolled courses
    """
    return execute_query(
        "SELECT c.id, c.title, c.description, c.category, c.level, c.price, sc.purchased_at, sc.status "
        "FROM student_courses sc "
        "JOIN courses c ON sc.course_id = c.id "
        "WHERE sc.student_id = %s ORDER BY sc.purchased_at DESC",
        (student_id,)
    )


def get_course_students(course_id):
    """
    Get all students enrolled in a specific course
    """
    return execute_query(
        "SELECT u.id, u.name, u.email, u.phone, sc.purchased_at, sc.status "
        "FROM student_courses sc "
        "JOIN users u ON sc.student_id = u.id "
        "WHERE sc.course_id = %s ORDER BY sc.purchased_at DESC",
        (course_id,)
    )


def student_is_enrolled(student_id, course_id):
    """
    Check whether a student is already enrolled in a course
    """
    return execute_query(
        "SELECT id FROM student_courses WHERE student_id=%s AND course_id=%s",
        (student_id, course_id),
        fetch_one=True
    ) is not None


def get_teachers():
    """
    Get all teacher users
    """
    return execute_query(
        "SELECT id, name, email, phone, created_at FROM users WHERE role='teacher' ORDER BY name"
    )


def get_students():
    """
    Get all student users
    """
    return execute_query(
        "SELECT id, name, email, phone, created_at FROM users WHERE role='student' ORDER BY name"
    )


def update_user(user_id, **kwargs):
    """
    Update user information
    
    Args:
        user_id: User ID to update
        **kwargs: Fields to update (name, email, password, role, phone)
    """
    allowed_fields = {'name', 'email', 'password', 'role', 'phone'}
    update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not update_fields:
        return {'affected': 0, 'last_id': None}
    
    set_clause = ', '.join([f"{k}=%s" for k in update_fields.keys()])
    values = list(update_fields.values())
    values.append(user_id)
    
    query = f"UPDATE users SET {set_clause} WHERE id=%s"
    return execute_insert_update_delete(query, values)
