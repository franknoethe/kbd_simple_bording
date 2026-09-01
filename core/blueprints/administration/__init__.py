from flask import Blueprint

administration_bp = Blueprint("administration", __name__)

from core.blueprints.administration import routes  # noqa: E402,F401
