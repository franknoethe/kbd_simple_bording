from flask import Blueprint

employee_bp = Blueprint("employee", __name__)

from core.blueprints.employee import routes  # noqa: E402,F401
