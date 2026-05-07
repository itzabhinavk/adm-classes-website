-- Add course_id column to lectures table if not exists
ALTER TABLE lectures ADD COLUMN course_id INT NULL;
ALTER TABLE lectures ADD FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL;

-- Verify the column was added
SHOW COLUMNS FROM lectures LIKE 'course_id';