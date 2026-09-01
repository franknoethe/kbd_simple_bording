from flask import jsonify, render_template, request

from core.blueprints.template import template_bp
from core.blueprints.template import services
from core.errors import ApiError


@template_bp.route("/templates")
def templates_page():
    """Render templates CRUD page."""
    return render_template("templates.html")


@template_bp.route("/template-tasks")
def template_tasks_page():
    """Render process tasks CRUD page."""
    return render_template("template_tasks.html")


@template_bp.route("/api/template-tasks/options", methods=["GET"])
def get_template_task_options():
    try:
        return jsonify(services.get_template_task_options())
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/template-tasks", methods=["GET"])
def get_template_tasks():
    try:
        return jsonify(services.get_template_tasks(request.args))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/template-tasks", methods=["POST"])
def create_template_task():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.create_template_task(data)), 201
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/template-tasks/<int:task_id>", methods=["PUT"])
def update_template_task(task_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.update_template_task(task_id, data))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/template-tasks/<int:task_id>", methods=["DELETE"])
def delete_template_task(task_id):
    try:
        return jsonify(services.delete_template_task(task_id))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/templates/options", methods=["GET"])
def get_template_options():
    try:
        return jsonify(services.get_template_options())
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/templates", methods=["GET"])
def get_templates():
    try:
        return jsonify(services.get_templates(request.args))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/templates/<int:template_id>/copy-tasks", methods=["POST"])
def copy_template_tasks(template_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.copy_template_tasks(template_id, data)), 201
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/templates/copy-options", methods=["GET"])
def get_template_copy_options():
    source_template_id = request.args.get("exclude_id", type=int)
    try:
        return jsonify(services.get_template_copy_options(source_template_id))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/templates/suggestions", methods=["GET"])
def get_template_suggestions():
    field = request.args.get("field", "")
    query = request.args.get("q", "").strip()
    try:
        return jsonify(services.get_template_suggestions(field, query))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/templates", methods=["POST"])
def create_template():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.create_template(data)), 201
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/templates/<int:template_id>", methods=["PUT"])
def update_template(template_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.update_template(template_id, data))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@template_bp.route("/api/templates/<int:template_id>", methods=["DELETE"])
def delete_template(template_id):
    try:
        return jsonify(services.delete_template(template_id))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code
