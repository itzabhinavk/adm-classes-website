# ADM Education Website

## Clean project structure

This project now contains the essential files and folders for a simple education website with login/register functionality.

### Remaining folders

- `app/`
  - `__init__.py` - Flask application factory and blueprint registration
  - `auth/` - authentication blueprint for login, registration, logout
  - `admin/` - admin dashboard and management pages
  - `teacher/` - teacher dashboard and pages
  - `student/` - student dashboard and pages
  - `utils/` - database helpers and auth decorators

- `database/`
  - `users.sql` - database schema for `users` table

- `static/`
  - CSS, JS, images used by templates

- `templates/`
  - HTML templates for login, register, dashboards, and pages

### Remaining root files

- `app.py` - application entry point
- `config.py` - database and Flask configuration
- `requirements.txt` - Python dependencies

## What was removed

The following old or duplicate items were removed because they were not used by the current Flask app:

- Root-level duplicate folders: `auth/`, `admin/`, `students/`, `teacher/`
- Old PHP assets and pages: `index.php`, `includes/`, `unuses-folder/`
- Outdated SQL file: `dashboard.sql`
- Empty database helper file: `database/db.py`
- Python bytecode cache: `app/__pycache__/`

## Notes

- Your current login/register system is implemented in `app/auth/routes.py`.
- Database access is implemented in `app/utils/db.py`.
- Authentication decorators are implemented in `app/utils/decorators.py`.
- The templates are in `templates/` and should be rendered by Flask.

## Database setup

To create the MySQL database and import the schema, run the PowerShell script from the project root:

```powershell
.\setup_db.ps1
```

This script will:
- create the `adm` database if it does not exist
- import the schema and initial data from `database/users.sql`

If your MySQL root user has a password, the script will prompt you to enter it.

If you need to set database credentials manually, you can use environment variables before starting the app:

```powershell
$env:DB_HOST = 'localhost'
$env:DB_USER = 'root'
$env:DB_PASSWORD = 'your_root_password'
$env:DB_NAME = 'adm'
.\venv\Scripts\python.exe app.py
```

## Next step

If you want, I can now verify the login/register flow end-to-end and fix any small issues in templates or session handling.

## Seed sample data

A basic seed script is available to populate users, courses, teacher assignments, and student enrollments:

```powershell
.\venv\Scripts\python.exe seed_data.py
```

This will create sample admin, teachers, and students, assign teachers to courses, and enroll students in courses.
