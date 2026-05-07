"""
Flask application factory.
Registers all blueprints and provides top-level auth route aliases.
"""

from flask import Flask
from config import Config



def create_app(config_class=Config):
    """
    Create and configure Flask application instance.
    """
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    from app.auth.routes import auth_bp, login as auth_login, register as auth_register, logout as auth_logout
    from app.admin.routes import admin_bp
    from app.teacher.routes import teacher_bp
    from app.student.routes import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    @app.route('/login', methods=['GET', 'POST'])
    def login_alias():
        return auth_login()

    @app.route('/register', methods=['GET', 'POST'])
    def register_alias():
        return auth_register()

    @app.route('/logout')
    def logout_alias():
        return auth_logout()

    return app
