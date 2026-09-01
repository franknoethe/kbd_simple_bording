"""Thin Flask entrypoint. All routes now live in the ``core`` package as blueprints
(auth, employee, task, template, administration); see core/__init__.py for the
application factory and core/blueprints/*/routes.py + services.py for the
individual endpoints.

``get_db_connection`` is re-exported here for backward compatibility with
send_task_reminders.py, which imports it via ``from app import get_db_connection``.
"""

from core import create_app, get_db_connection  # noqa: F401

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
