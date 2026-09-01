from flask import jsonify, redirect, render_template, request, session, url_for

from core.constants import MANAGEMENT_PATHS, MASTER_DATA_PATHS
from core.utils import current_user_role, is_api_request


def register_security(app):
    """Register the before_request access-control hook (unchanged from the
    original monolithic app.py, only endpoint names now carry the blueprint
    prefix)."""

    @app.before_request
    def protect_application():
        if request.endpoint in {"auth.login", "auth.logout", "static"}:
            return None

        if "user" not in session:
            if is_api_request():
                return (
                    jsonify({"success": False, "message": "Anmeldung erforderlich."}),
                    401,
                )
            return redirect(
                url_for(
                    "auth.login",
                    next=request.full_path if request.query_string else request.path,
                )
            )

        is_management_path = request.path in MANAGEMENT_PATHS or any(
            request.path.startswith(path + "/") for path in MANAGEMENT_PATHS
        )
        is_master_data_path = request.path in MASTER_DATA_PATHS or any(
            request.path.startswith(path + "/") for path in MASTER_DATA_PATHS
        )
        role = current_user_role().casefold()
        if (is_management_path and role not in {"admin", "manager"}) or (
            is_master_data_path and role != "admin"
        ):
            if is_api_request():
                return (
                    jsonify({"success": False, "message": "Keine Berechtigung."}),
                    403,
                )
            return render_template("403.html"), 403

        return None
