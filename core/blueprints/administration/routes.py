from flask import jsonify, render_template, request

from core.blueprints.administration import administration_bp
from core.blueprints.administration import services
from core.errors import ApiError


def _error(error):
    return jsonify({"success": False, "message": error.message}), error.status_code


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


@administration_bp.route("/locations")
def locations_page():
    """Render locations CRUD page."""
    return render_template("locations.html")


@administration_bp.route("/functions")
def functions_page():
    """Render functions CRUD page."""
    return render_template("functions.html")


@administration_bp.route("/jobs")
def jobs_page():
    """Render jobs CRUD page."""
    return render_template("jobs.html")


@administration_bp.route("/process-types")
def process_types_page():
    """Render process types CRUD page."""
    return render_template("process_types.html")


@administration_bp.route("/roles")
def roles_page():
    """Render roles CRUD page."""
    return render_template("roles.html")


@administration_bp.route("/email-templates")
def email_templates_page():
    """Render email templates CRUD page."""
    return render_template("email_templates.html")


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------


@administration_bp.route("/api/email-templates", methods=["GET"])
def get_email_templates():
    try:
        return jsonify(services.get_email_templates(request.args))
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/email-templates", methods=["POST"])
def create_email_template():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.create_email_template(data)), 201
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/email-templates/suggestions", methods=["GET"])
def get_email_template_suggestions():
    field = request.args.get("field", "")
    query = request.args.get("q", "").strip()
    try:
        return jsonify(services.get_email_template_suggestions(field, query))
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/email-templates/<int:template_id>", methods=["PUT"])
def update_email_template(template_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.update_email_template(template_id, data))
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/email-templates/<int:template_id>", methods=["DELETE"])
def delete_email_template(template_id):
    try:
        return jsonify(services.delete_email_template(template_id))
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/email-templates/import-preview", methods=["POST"])
def preview_email_template_import():
    """Parse an uploaded Outlook template without writing to the database."""
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename.lower().endswith(".oft"):
        return (
            jsonify({"success": False, "message": "Bitte eine .oft-Datei auswählen."}),
            400,
        )
    try:
        return jsonify(
            {"success": True, "email_template": services.parse_oft_file(uploaded_file)}
        )
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------


@administration_bp.route("/api/roles", methods=["GET"])
def get_roles():
    try:
        return jsonify(services.get_roles())
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/roles", methods=["POST"])
def create_role():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.create_role(data)), 201
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/roles/<int:role_id>", methods=["PUT"])
def update_role(role_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.update_role(role_id, data))
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/roles/<int:role_id>", methods=["DELETE"])
def delete_role(role_id):
    try:
        return jsonify(services.delete_role(role_id))
    except ApiError as error:
        return _error(error)


# ---------------------------------------------------------------------------
# Process types
# ---------------------------------------------------------------------------


@administration_bp.route("/api/process-types", methods=["GET"])
def get_process_types():
    try:
        return jsonify(services.get_process_types())
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/process-types", methods=["POST"])
def create_process_type():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.create_process_type(data)), 201
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/process-types/<int:process_type_id>", methods=["PUT"])
def update_process_type(process_type_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.update_process_type(process_type_id, data))
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/process-types/<int:process_type_id>", methods=["DELETE"])
def delete_process_type(process_type_id):
    try:
        return jsonify(services.delete_process_type(process_type_id))
    except ApiError as error:
        return _error(error)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------


@administration_bp.route("/api/jobs", methods=["GET"])
def get_jobs():
    try:
        return jsonify(services.get_jobs())
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/job-options", methods=["GET"])
def get_job_options():
    try:
        return jsonify(services.get_job_options())
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/jobs", methods=["POST"])
def create_job():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.create_job(data)), 201
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.update_job(job_id, data))
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    try:
        return jsonify(services.delete_job(job_id))
    except ApiError as error:
        return _error(error)


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


@administration_bp.route("/api/functions", methods=["GET"])
def get_functions():
    try:
        return jsonify(services.get_functions())
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/functions", methods=["POST"])
def create_function():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.create_function(data)), 201
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/functions/<int:function_id>", methods=["PUT"])
def update_function(function_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.update_function(function_id, data))
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/functions/<int:function_id>", methods=["DELETE"])
def delete_function(function_id):
    try:
        return jsonify(services.delete_function(function_id))
    except ApiError as error:
        return _error(error)


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------


@administration_bp.route("/api/locations", methods=["GET"])
def get_locations():
    try:
        return jsonify(services.get_locations())
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/locations", methods=["POST"])
def create_location():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.create_location(data)), 201
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/locations/<int:location_id>", methods=["PUT"])
def update_location(location_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.update_location(location_id, data))
    except ApiError as error:
        return _error(error)


@administration_bp.route("/api/locations/<int:location_id>", methods=["DELETE"])
def delete_location(location_id):
    try:
        return jsonify(services.delete_location(location_id))
    except ApiError as error:
        return _error(error)
