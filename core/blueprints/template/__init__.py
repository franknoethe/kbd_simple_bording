from flask import Blueprint

template_bp = Blueprint("template", __name__)

from core.blueprints.template import routes  # noqa: E402,F401
