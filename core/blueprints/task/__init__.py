from flask import Blueprint

task_bp = Blueprint("task", __name__)

from core.blueprints.task import routes  # noqa: E402,F401
