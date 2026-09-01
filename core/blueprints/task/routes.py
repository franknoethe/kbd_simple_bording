from flask import jsonify, render_template, request, session

from core.blueprints.task import task_bp
from core.blueprints.task import services
from core.errors import ApiError
from core.utils import current_user_role


def _is_manager():
    return current_user_role().casefold() in {"admin", "manager"}


@task_bp.route("/tasks")
def tasks_page():
    return render_template("tasks.html")


@task_bp.route("/favicon.ico")
def favicon():
    return "", 204


@task_bp.route("/api/task-options")
def task_options():
    try:
        return jsonify(services.get_task_options())
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@task_bp.route("/api/tasks")
def get_tasks():
    try:
        return jsonify(
            services.get_tasks(request.args, _is_manager(), session["user"]["id"])
        )
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@task_bp.route("/api/tasks/suggestions")
def task_suggestions():
    field = request.args.get("field", "")
    query = request.args.get("q", "").strip()
    try:
        return jsonify(services.get_task_suggestions(field, query))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@task_bp.route("/api/tasks", methods=["POST"])
def assign_tasks():
    if not _is_manager():
        return jsonify({"success": False, "message": "Keine Berechtigung."}), 403
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.assign_tasks(data)), 201
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@task_bp.route("/api/tasks/single", methods=["POST"])
def create_single_task():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(services.create_single_task(data)), 201
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@task_bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    if not _is_manager():
        return jsonify({"success": False, "message": "Keine Berechtigung."}), 403
    try:
        return jsonify(services.delete_task(task_id))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@task_bp.route("/api/tasks/<int:task_id>/email-preview")
def task_email_preview(task_id):
    try:
        return jsonify(
            services.get_task_email_preview(
                task_id, _is_manager(), session["user"]["id"]
            )
        )
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@task_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(
            services.update_task(task_id, data, _is_manager(), session["user"]["id"])
        )
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code
