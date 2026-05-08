"""
Database Seeder Script
Creates admin, teachers, and students in the database
"""
import pymysql
from werkzeug.security import generate_password_hash

# Database connection
def get_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'turntable.proxy.rlwy.net'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', ''),
        port=int(os.environ.get('DB_PORT', 19211)),
        cursorclass=pymysql.cursors.DictCursor
    )
def create_users():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Password hash for "password123"
    password_hash = generate_password_hash('password123', method='pbkdf2:sha256')
    
    print("Creating Admin...")
    # Check if admin exists, if not create
    cursor.execute("SELECT id FROM users WHERE email='admin@adm.com'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (name, email, password, role) 
            VALUES (%s, %s, %s, %s)
        """, ('Admin', 'admin@adm.com', password_hash, 'admin'))
    else:
        print("  Admin already exists, skipping...")
    
    # Create 5 Teachers
    teachers = [
        ('Rajesh Kumar', 'rajesh@adm.com'),
        ('Priya Sharma', 'priya@adm.com'),
        ('Amit Singh', 'amit@adm.com'),
        ('Sunita Devi', 'sunita@adm.com'),
        ('Vikram Patel', 'vikram@adm.com')
    ]
    
    print("Creating Teachers...")
    for name, email in teachers:
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (name, email, password, role) 
                VALUES (%s, %s, %s, %s)
            """, (name, email, password_hash, 'teacher'))
            print(f"  Created: {name}")
        else:
            print(f"  Already exists: {name}")
    
    # Create 10 Students
    students = [
        ('Rahul Sharma', 'rahul@student.com'),
        ('Anjali Gupta', 'anjali@student.com'),
        ('Mohit Kumar', 'mohit@student.com'),
        ('Pooja Singh', 'pooja@student.com'),
        ('Ajay Patel', 'ajay@student.com'),
        ('Sneha Reddy', 'sneha@student.com'),
        ('Deepak Verma', 'deepak@student.com'),
        ('Kavita Joshi', 'kavita@student.com'),
        ('Saurabh Mishra', 'saurabh@student.com'),
        ('Neha Singh', 'neha@student.com')
    ]
    
    print("Creating Students...")
    for name, email in students:
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (name, email, password, role) 
                VALUES (%s, %s, %s, %s)
            """, (name, email, password_hash, 'student'))
            print(f"  Created: {name}")
        else:
            print(f"  Already exists: {name}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n" + "="*50)
    print("All users created successfully!")
    print("="*50)
    print("\nLOGIN CREDENTIALS:")
    print("-" * 50)
    print("ADMIN:")
    print("  Email: admin@adm.com")
    print("  Password: password123")
    print("-" * 50)
    print("TEACHERS (5):")
    for name, email in teachers:
        print(f"  Email: {email}")
    print("  Password: password123")
    print("-" * 50)
    print("STUDENTS (10):")
    for name, email in students:
        print(f"  Email: {email}")
    print("  Password: password123")
    print("-" * 50)

if __name__ == '__main__':
    try:
        create_users()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure MySQL is running and database 'adm' exists!")
