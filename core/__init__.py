from pathlib import Path

from flask import Flask

from core.config import SECRET_KEY
from core.db import get_db_connection
from core.security import register_security

from core.blueprints.auth import auth_bp
from core.blueprints.employee import employee_bp
from core.blueprints.task import task_bp
from core.blueprints.template import template_bp
from core.blueprints.administration import administration_bp

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    """Application factory: builds the Flask app and registers all blueprints."""
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.secret_key = SECRET_KEY

    register_security(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(template_bp)
    app.register_blueprint(administration_bp)

    return app


__all__ = ["create_app", "get_db_connection"]
