from datetime import date, datetime

from flask import jsonify, request, session

from core.constants import TASK_STATUSES


def is_api_request():
    return request.path.startswith("/api/")


def current_user_role():
    return session.get("user", {}).get("role", "")


def task_connection_error():
    return jsonify({"success": False, "message": "Database connection error"}), 500


def task_payload(row):
    item = dict(row)
    if isinstance(item.get("due_date"), (date, datetime)):
        item["due_date"] = item["due_date"].isoformat()
    if isinstance(item.get("created_at"), (date, datetime)):
        item["created_at"] = item["created_at"].isoformat()[:10]
    item["status_label"] = TASK_STATUSES.get(item.get("status"), item.get("status", ""))
    return item
