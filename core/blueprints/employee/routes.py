from flask import jsonify, render_template, request

from core.blueprints.employee import employee_bp
from core.blueprints.employee import services
from core.errors import ApiError


@employee_bp.route("/")
def index():
    try:
        current_page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        current_page = 1

    data = services.get_dashboard_data(current_page)
    return render_template("index.html", **data)


@employee_bp.route("/employees")
def employees_page():
    """Render employees CRUD page"""
    return render_template("employees.html")


@employee_bp.route("/api/employees", methods=["GET"])
def get_employees():
    try:
        return jsonify(services.list_employees())
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@employee_bp.route("/api/employee-options", methods=["GET"])
def get_employee_options():
    try:
        return jsonify(services.get_employee_options())
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@employee_bp.route("/api/employees", methods=["POST"])
def create_employee():
    data = request.get_json()
    try:
        return jsonify(services.create_employee(data)), 201
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@employee_bp.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    data = request.get_json()
    try:
        return jsonify(services.update_employee(employee_id, data))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code


@employee_bp.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    try:
        return jsonify(services.delete_employee(employee_id))
    except ApiError as error:
        return jsonify({"success": False, "message": error.message}), error.status_code
