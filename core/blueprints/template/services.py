from pymysql import Error
from pymysql.cursors import DictCursor as RealDictCursor

from core.db import get_db_connection
from core.errors import ApiError


def get_template_task_options():
    """Get combobox options for process tasks."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, name, location_id FROM templates ORDER BY name ASC")
        templates = cursor.fetchall()
        cursor.execute("SELECT id, name FROM functions ORDER BY name ASC")
        functions = cursor.fetchall()
        cursor.execute(
            "SELECT id, name, subject FROM email_templates ORDER BY name ASC"
        )
        email_templates = cursor.fetchall()
        return {
            "success": True,
            "templates": [dict(item) for item in templates],
            "functions": [dict(item) for item in functions],
            "email_templates": [dict(item) for item in email_templates],
        }
    except Error as error:
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_template_tasks(args):
    """Get sorted and paginated process tasks with resolved names."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    sort_columns = {
        "id": "template_tasks.id",
        "step": "template_tasks.step",
        "template_id": "templates.name",
        "title": "template_tasks.title",
        "description": "template_tasks.description",
        "due_offset_days": "template_tasks.due_offset_days",
        "responsible_function_id": "functions.name",
        "email_template_id": "email_templates.name",
        "mandatory": "template_tasks.mandatory",
    }
    sort_column = sort_columns.get(args.get("sort", "id"), "template_tasks.id")
    direction = "DESC" if args.get("direction", "asc").lower() == "desc" else "ASC"
    try:
        page = max(1, int(args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    page_size = 800
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        joins = """
            FROM template_tasks
            LEFT JOIN templates ON templates.id = template_tasks.template_id
            LEFT JOIN functions ON functions.id = template_tasks.responsible_function_id
            LEFT JOIN email_templates ON email_templates.id = template_tasks.email_template_id
        """
        template_id = args.get("template_id", type=int)
        filter_sql = " WHERE template_tasks.template_id = %s" if template_id else ""
        filter_values = (template_id,) if template_id else ()
        template_context = None
        if template_id:
            cursor.execute(
                """
                SELECT templates.id, templates.name,
                       process_types.name AS process_type_name,
                       locations.name AS location_name,
                       jobs.name AS job_name
                FROM templates
                LEFT JOIN process_types ON process_types.id = templates.process_type_id
                LEFT JOIN locations ON locations.id = templates.location_id
                LEFT JOIN jobs ON jobs.id = templates.job_id
                WHERE templates.id = %s
            """,
                (template_id,),
            )
            template_context = cursor.fetchone()
        cursor.execute(f"SELECT COUNT(*) AS total {joins}{filter_sql}", filter_values)
        total = cursor.fetchone()["total"]
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = min(page, total_pages)
        cursor.execute(
            f"""
            SELECT template_tasks.id, template_tasks.step, template_tasks.template_id,
                   templates.name AS template_name, template_tasks.title,
                   template_tasks.description, template_tasks.due_offset_days,
                   template_tasks.responsible_function_id,
                   COALESCE(functions.name, '') AS responsible_name,
                   template_tasks.email_template_id,
                   email_templates.name AS email_template_name,
                   template_tasks.mandatory
            {joins}
            {filter_sql}
            ORDER BY {sort_column} {direction}, template_tasks.id ASC
            LIMIT %s OFFSET %s
        """,
            filter_values + (page_size, (page - 1) * page_size),
        )
        tasks = [dict(item) for item in cursor.fetchall()]
        return {
            "success": True,
            "template_tasks": tasks,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "template_context": dict(template_context) if template_context else None,
        }
    except Error as error:
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def _template_task_values(data):
    """Validate and normalize template task input."""
    required_ids = ("template_id", "responsible_function_id")
    if any(data.get(field) in (None, "") for field in required_ids):
        raise ValueError("Referenz fehlt.")
    title = str(data.get("title", "")).strip()
    if not title:
        raise ValueError("Titel fehlt.")
    return (
        int(data.get("step", 0)),
        int(data["template_id"]),
        title,
        str(data.get("description", "")),
        int(data.get("due_offset_days", 0)),
        int(data["responsible_function_id"]),
        int(data["email_template_id"]) if data.get("email_template_id") else None,
        bool(data.get("mandatory", False)),
    )


def create_template_task(data):
    """Create a process task."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        task = _template_task_values(data)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO template_tasks
                (step, template_id, title, description, due_offset_days,
                 responsible_function_id, email_template_id, mandatory)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            task,
        )
        keys = (
            "step",
            "template_id",
            "title",
            "description",
            "due_offset_days",
            "responsible_function_id",
            "email_template_id",
            "mandatory",
        )
        result = dict(zip(keys, task))
        result["id"] = cursor.lastrowid
        connection.commit()
        return {"success": True, "template_task": result}
    except (TypeError, ValueError) as error:
        connection.rollback()
        raise ApiError("Ungültige Werte für Prozessaufgabe.", 400) from error
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_template_task(task_id, data):
    """Update a process task."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        task = _template_task_values(data)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE template_tasks
            SET step = %s, template_id = %s, title = %s, description = %s,
                due_offset_days = %s, responsible_function_id = %s,
                email_template_id = %s, mandatory = %s
            WHERE id = %s
        """,
            task + (task_id,),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Prozessaufgabe nicht gefunden.", 404)
        keys = (
            "step",
            "template_id",
            "title",
            "description",
            "due_offset_days",
            "responsible_function_id",
            "email_template_id",
            "mandatory",
        )
        result = dict(zip(keys, task))
        result["id"] = task_id
        connection.commit()
        return {"success": True, "template_task": result}
    except ApiError:
        raise
    except (TypeError, ValueError) as error:
        connection.rollback()
        raise ApiError("Ungültige Werte für Prozessaufgabe.", 400) from error
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def delete_template_task(task_id):
    """Delete a process task and its generated employee tasks."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE template_task_id = %s", (task_id,))
        deleted_tasks = cursor.rowcount
        cursor.execute("DELETE FROM template_tasks WHERE id = %s", (task_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Prozessaufgabe nicht gefunden.", 404)
        connection.commit()
        return {"success": True, "deleted_tasks": deleted_tasks}
    except ApiError:
        raise
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_template_options():
    """Get combobox options for templates."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, name FROM process_types ORDER BY name ASC")
        process_types = cursor.fetchall()
        cursor.execute("SELECT id, name FROM locations ORDER BY name ASC")
        locations = cursor.fetchall()
        cursor.execute("SELECT id, location_id, name FROM jobs ORDER BY name ASC")
        jobs = cursor.fetchall()
        return {
            "success": True,
            "process_types": [dict(item) for item in process_types],
            "locations": [dict(item) for item in locations],
            "jobs": [dict(item) for item in jobs],
        }
    except Error as error:
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_templates(args):
    """Get filtered, sorted templates with resolved foreign-key names."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    sort_columns = {
        "id": "templates.id",
        "process_type_id": "process_types.name",
        "location_id": "locations.name",
        "job_id": "jobs.name",
        "name": "templates.name",
        "active": "templates.active",
    }
    sort_column = sort_columns.get(args.get("sort", "id"), "templates.id")
    direction = "DESC" if args.get("direction", "asc").lower() == "desc" else "ASC"
    filters = {
        "process_type_id": args.get("process_type_id", "").strip(),
        "location_id": args.get("location_id", "").strip(),
        "job_id": args.get("job_id", "").strip(),
        "name": args.get("name", "").strip(),
    }
    try:
        page = max(1, int(args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    page_size = 800

    try:
        where_parts = []
        values = []
        for column in ("process_type_id", "location_id", "job_id"):
            if filters[column].isdigit():
                where_parts.append(f"templates.{column} = %s")
                values.append(int(filters[column]))
        if len(filters["name"]) >= 3:
            where_parts.append("templates.name LIKE %s")
            values.append(f"%{filters['name']}%")
        where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM templates
            LEFT JOIN process_types ON process_types.id = templates.process_type_id
            LEFT JOIN locations ON locations.id = templates.location_id
            LEFT JOIN jobs ON jobs.id = templates.job_id
            {where_sql}
        """,
            values,
        )
        total = cursor.fetchone()["total"]
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = min(page, total_pages)
        cursor.execute(
            f"""
            SELECT templates.id, templates.process_type_id, process_types.name AS process_type_name,
                   templates.location_id, locations.name AS location_name,
                   templates.job_id, jobs.name AS job_name,
                   templates.name,
                   (SELECT COUNT(*) FROM template_tasks
                    WHERE template_tasks.template_id = templates.id) AS task_count,
                   templates.active
            FROM templates
            LEFT JOIN process_types ON process_types.id = templates.process_type_id
            LEFT JOIN locations ON locations.id = templates.location_id
            LEFT JOIN jobs ON jobs.id = templates.job_id
            {where_sql}
            ORDER BY {sort_column} {direction}, templates.id ASC
            LIMIT %s OFFSET %s
        """,
            values + [page_size, (page - 1) * page_size],
        )
        templates = [dict(item) for item in cursor.fetchall()]
        return {
            "success": True,
            "templates": templates,
            "total": total,
            "page": page,
            "total_pages": total_pages,
        }
    except Error as error:
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def copy_template_tasks(template_id, data):
    """Copy all process tasks from one template to an empty template."""
    try:
        target_template_id = int(data.get("target_template_id"))
    except (TypeError, ValueError):
        raise ApiError("Ziel-Template ist erforderlich.", 400)
    if target_template_id == template_id:
        raise ApiError("Quell- und Ziel-Template müssen verschieden sein.", 400)

    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id FROM templates WHERE id IN (%s, %s)",
            (template_id, target_template_id),
        )
        if len(cursor.fetchall()) != 2:
            raise ApiError("Quell- oder Ziel-Template nicht gefunden.", 404)
        cursor.execute(
            "SELECT COUNT(*) AS total FROM template_tasks WHERE template_id = %s",
            (template_id,),
        )
        source_count = cursor.fetchone()["total"]
        if source_count == 0:
            raise ApiError("Das Quell-Template enthält keine Prozessaufgaben.", 400)
        cursor.execute(
            "SELECT COUNT(*) AS total FROM template_tasks WHERE template_id = %s",
            (target_template_id,),
        )
        if cursor.fetchone()["total"] != 0:
            raise ApiError("Das Ziel-Template enthält bereits Prozessaufgaben.", 409)
        cursor.execute(
            """
            INSERT INTO template_tasks
                (step, template_id, title, description, due_offset_days,
                 responsible_function_id, email_template_id, mandatory)
            SELECT step, %s, title, description, due_offset_days,
                   responsible_function_id, email_template_id, mandatory
            FROM template_tasks
            WHERE template_id = %s
            ORDER BY step, id
        """,
            (target_template_id, template_id),
        )
        connection.commit()
        return {"success": True, "copied": cursor.rowcount}
    except ApiError:
        connection.rollback()
        raise
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_template_copy_options(source_template_id):
    """Return templates that do not contain process tasks."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        exclude_sql = "AND templates.id <> %s" if source_template_id else ""
        values = (source_template_id,) if source_template_id else ()
        cursor.execute(
            """
            SELECT templates.id, templates.name, 0 AS task_count,
                   process_types.name AS process_type_name,
                   locations.name AS location_name,
                   jobs.name AS job_name
            FROM templates
            LEFT JOIN process_types ON process_types.id = templates.process_type_id
            LEFT JOIN locations ON locations.id = templates.location_id
            LEFT JOIN jobs ON jobs.id = templates.job_id
            WHERE NOT EXISTS (
                SELECT 1 FROM template_tasks
                WHERE template_tasks.template_id = templates.id
            )
            """
            + exclude_sql
            + """
            ORDER BY templates.name ASC
        """,
            values,
        )
        return {
            "success": True,
            "templates": [dict(item) for item in cursor.fetchall()],
        }
    except Error as error:
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_template_suggestions(field, query):
    """Return up to ten matching template filter suggestions."""
    field_map = {
        "process_type_id": ("process_types.id", "process_types.name"),
        "location_id": ("locations.id", "locations.name"),
        "job_id": ("jobs.id", "jobs.name"),
        "name": ("templates.id", "templates.name"),
    }
    if field not in field_map or len(query) < 3:
        return {"success": True, "templates": []}
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        id_column, display_column = field_map[field]
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            f"""
            SELECT DISTINCT {id_column} AS value, {display_column} AS label
            FROM templates
            LEFT JOIN process_types ON process_types.id = templates.process_type_id
            LEFT JOIN locations ON locations.id = templates.location_id
            LEFT JOIN jobs ON jobs.id = templates.job_id
            WHERE {display_column} LIKE %s
            ORDER BY label ASC
            LIMIT 10
        """,
            (f"%{query}%",),
        )
        return {
            "success": True,
            "templates": [dict(item) for item in cursor.fetchall()],
        }
    except Error as error:
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def create_template(data):
    """Create a template."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        name = str(data.get("name", "")).strip()
        process_type_id = data.get("process_type_id")
        location_id = data.get("location_id")
        job_id = data.get("job_id")
        active = bool(data.get("active", True))
        if not name or None in (process_type_id, location_id, job_id):
            raise ApiError("Prozess, Location, Job und Name sind erforderlich.", 400)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO templates (process_type_id, location_id, job_id, name, active)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (int(process_type_id), int(location_id), int(job_id), name, active),
        )
        template = {
            "id": cursor.lastrowid,
            "process_type_id": int(process_type_id),
            "location_id": int(location_id),
            "job_id": int(job_id),
            "name": name,
            "active": active,
        }
        connection.commit()
        return {"success": True, "template": template}
    except ApiError:
        connection.rollback()
        raise
    except (TypeError, ValueError) as error:
        connection.rollback()
        raise ApiError(
            "Ungültige Auswahl für Prozess, Location oder Job.", 400
        ) from error
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_template(template_id, data):
    """Update a template."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        name = str(data.get("name", "")).strip()
        process_type_id = data.get("process_type_id")
        location_id = data.get("location_id")
        job_id = data.get("job_id")
        if not name or None in (process_type_id, location_id, job_id):
            raise ApiError("Prozess, Location, Job und Name sind erforderlich.", 400)
        active = bool(data.get("active", True))
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE templates
            SET process_type_id = %s, location_id = %s, job_id = %s, name = %s, active = %s
            WHERE id = %s
        """,
            (
                int(process_type_id),
                int(location_id),
                int(job_id),
                name,
                active,
                template_id,
            ),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Template nicht gefunden.", 404)
        template = {
            "id": template_id,
            "process_type_id": int(process_type_id),
            "location_id": int(location_id),
            "job_id": int(job_id),
            "name": name,
            "active": active,
        }
        connection.commit()
        return {"success": True, "template": template}
    except ApiError:
        connection.rollback()
        raise
    except (TypeError, ValueError) as error:
        connection.rollback()
        raise ApiError(
            "Ungültige Auswahl für Prozess, Location oder Job.", 400
        ) from error
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def delete_template(template_id):
    """Delete a template."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM templates WHERE id = %s", (template_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Template nicht gefunden.", 404)
        connection.commit()
        return {"success": True}
    except ApiError:
        raise
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()
