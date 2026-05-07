"""Seed the ADM database with sample users, courses, teacher assignments, and student enrollments."""
from werkzeug.security import generate_password_hash
from app.utils.db import (
    create_user,
    user_exists,
    get_user_by_email,
    create_course,
    get_course_by_title,
    assign_teacher_to_course,
    enroll_student_in_course,
    student_is_enrolled,
    get_courses,
    execute_query,
)


def ensure_user(name, email, password, role, phone=None):
    if user_exists(email):
        print(f"User already exists: {email}")
        return get_user_by_email(email)
    hashed = generate_password_hash(password, method='pbkdf2:sha256')
    result = create_user(name, email, hashed, role, phone)
    print(f"Created user {email} ({role})")
    return get_user_by_email(email)


def ensure_course(title, description, category, level, price):
    course = get_course_by_title(title)
    if course:
        print(f"Course already exists: {title}")
        return course
    result = create_course(title, description, category, level, price)
    print(f"Created course: {title}")
    return get_course_by_title(title)


def ensure_teacher_assignment(teacher_id, course_id):
    existing = execute_query(
        "SELECT id FROM teacher_courses WHERE teacher_id=%s AND course_id=%s",
        (teacher_id, course_id),
        fetch_one=True
    )
    if existing:
        print(f"Teacher {teacher_id} already assigned to course {course_id}")
        return existing
    return assign_teacher_to_course(teacher_id, course_id)


def ensure_student_enrollment(student_id, course_id, price):
    if student_is_enrolled(student_id, course_id):
        print(f"Student {student_id} already enrolled in course {course_id}")
        return None
    return enroll_student_in_course(student_id, course_id, price, 'active')


def main():
    # Sample users
    admin = ensure_user('Admin User', 'admin@adm.com', 'Admin123!', 'admin', '9000000001')
    teacher_one = ensure_user('Teacher One', 'teacher1@adm.com', 'Teacher123!', 'teacher', '9000000002')
    teacher_two = ensure_user('Teacher Two', 'teacher2@adm.com', 'Teacher123!', 'teacher', '9000000003')
    student_one = ensure_user('Student One', 'student1@adm.com', 'Student123!', 'student', '9000000004')
    student_two = ensure_user('Student Two', 'student2@adm.com', 'Student123!', 'student', '9000000005')
    student_three = ensure_user('Student Three', 'student3@adm.com', 'Student123!', 'student', '9000000006')

    # Sample courses
    course_a = ensure_course('Class 8th - Science', 'Foundation science course for class 8 students.', 'Science', '8th', 499.00)
    course_b = ensure_course('Class 9th - Science', 'Complete science overview with practice questions.', 'Science', '9th', 599.00)
    course_c = ensure_course('Class 10th - Science', 'Exam-ready science course for class 10.', 'Science', '10th', 699.00)
    course_d = ensure_course('Class 11th - Physics', 'Physics concepts for first-year science students.', 'Physics', '11th', 799.00)
    course_e = ensure_course('Class 12th - Chemistry', 'Class 12 chemistry course with theory and examples.', 'Chemistry', '12th', 899.00)

    # Assign teachers to courses
    ensure_teacher_assignment(teacher_one['id'], course_a['id'])
    ensure_teacher_assignment(teacher_one['id'], course_b['id'])
    ensure_teacher_assignment(teacher_two['id'], course_c['id'])
    ensure_teacher_assignment(teacher_two['id'], course_d['id'])
    ensure_teacher_assignment(teacher_two['id'], course_e['id'])

    # Enroll students into courses
    ensure_student_enrollment(student_one['id'], course_a['id'], course_a['price'])
    ensure_student_enrollment(student_one['id'], course_c['id'], course_c['price'])
    ensure_student_enrollment(student_two['id'], course_b['id'], course_b['price'])
    ensure_student_enrollment(student_two['id'], course_e['id'], course_e['price'])
    ensure_student_enrollment(student_three['id'], course_d['id'], course_d['price'])

    print('\nSample data seeding completed.')
    print('Login as admin@adm.com / Admin123!')
    print('Login as teacher1@adm.com / Teacher123!')
    print('Login as student1@adm.com / Student123!')


if __name__ == '__main__':
    main()
