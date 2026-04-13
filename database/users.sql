CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','teacher','student') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    description VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    level VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO courses (title, description, category, level) VALUES
('Class 8th - Science', 'Foundation science course for class 8 students.', 'Science', '8th'),
('Class 9th - Science', 'Complete science overview with practice questions.', 'Science', '9th'),
('Class 10th - Science', 'Exam-ready science course for class 10.', 'Science', '10th'),
('Class 11th - Physics', 'Physics concepts for first-year science students.', 'Physics', '11th'),
('Class 12th - Chemistry', 'Class 12 chemistry course with theory and examples.', 'Chemistry', '12th');