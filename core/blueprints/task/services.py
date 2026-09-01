from datetime import date, timedelta

from pymysql import Error
from pymysql.cursors import DictCursor as RealDictCursor

from core.constants import TASK_STATUSES
from core.db import get_db_connection
from core.errors import ApiError
from core.utils import task_payload


def get_task_options():
    connection = get_db_connection()
    if not connection:
        raise ApiError("Database connection error", 500)
    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT employees.id, CONCAT_WS(' ', employees.first_name, employees.last_name) AS name
            FROM employees
            JOIN functions ON functions.id = employees.function_id
            WHERE functions.name = 'Newbie'
            ORDER BY employees.last_name, employees.first_name
        """)
        employees = cursor.fetchall()
        cursor.execute(
            "SELECT id, name FROM templates WHERE active = TRUE ORDER BY name"
        )
        templates = cursor.fetchall()
        cursor.execute(
            "SELECT id, name FROM email_templates WHERE active = TRUE ORDER BY name"
        )
        email_templates = cursor.fetchall()
        cursor.execute("""
            SELECT id, CONCAT_WS(' ', first_name, last_name) AS name
            FROM employees
            ORDER BY last_name, first_name
        """)
        all_employees = cursor.fetchall()
        cursor.execute(
            "SELECT id, name FROM locations WHERE active = TRUE ORDER BY name"
        )
        locations = cursor.fetchall()
        return {
            "success": True,
            "employees": [dict(row) for row in employees],
            "templates": [dict(row) for row in templates],
            "email_templates": [dict(row) for row in email_templates],
            "all_employees": [dict(row) for row in all_employees],
            "locations": [dict(row) for row in locations],
            "statuses": TASK_STATUSES,
        }
    except Error as error:
        raise ApiError(f"Database error: {error}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_tasks(args, is_manager, session_user_id):
    connection = get_db_connection()
    if not connection:
        raise ApiError("Database connection error", 500)
    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        employee_id = args.get("employee_id", type=int)
        if not is_manager:
            employee_id = session_user_id
        filters = {
            "theme": args.get("theme", "").strip(),
            "term": args.get("term", "").strip(),
            "employee": args.get("employee", "").strip(),
            "template": args.get("template", "").strip(),
            "due_date": args.get("due_date", "").strip(),
            "created_at": args.get("created_at", "").strip(),
        }
        where_parts = []
        values = []
        if employee_id:
            where_parts.append("t.employee_id = %s")
            values.append(employee_id)
        if filters["theme"]:
            where_parts.append("t.theme LIKE %s")
            values.append(f"%{filters['theme']}%")
        if filters["term"]:
            where_parts.append("t.term LIKE %s")
            values.append(f"%{filters['term']}%")
        if filters["employee"]:
            try:
                where_parts.append("t.employee_id = %s")
                values.append(int(filters["employee"]))
            except ValueError:
                where_parts.append("1 = 0")
        if len(filters["template"]) >= 3:
            where_parts.append("tt.title LIKE %s")
            values.append(f"%{filters['template']}%")
        if filters["due_date"]:
            where_parts.append("CAST(t.due_date AS CHAR) LIKE %s")
            values.append(f"%{filters['due_date']}%")
        if filters["created_at"]:
            where_parts.append("CAST(t.created_at AS CHAR) LIKE %s")
            values.append(f"%{filters['created_at']}%")
        where = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
        sort_columns = {
            "theme": "t.theme",
            "id": "t.id",
            "term": "t.term",
            "employee": "employee_name",
            "title": "t.title",
            "due_date": "t.due_date",
            "status": "t.status",
            "created_at": "t.created_at",
        }
        sort_column = sort_columns.get(args.get("sort", "due_date"), "t.due_date")
        direction = "DESC" if args.get("direction", "asc").lower() == "desc" else "ASC"
        try:
            page = max(1, int(args.get("page", 1)))
        except (TypeError, ValueError):
            page = 1
        page_size = 800
        filter_values = tuple(values)
        cursor.execute(
            f"""SELECT COUNT(*) AS total
            FROM tasks t JOIN employees e ON e.id = t.employee_id
            LEFT JOIN template_tasks tt ON tt.id = t.template_task_id {where}""",
            filter_values,
        )
        total = cursor.fetchone()["total"]
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = min(page, total_pages)
        values.extend([page_size, (page - 1) * page_size])
        cursor.execute(
            f"""
                 SELECT t.id, t.theme, t.term, t.employee_id, t.template_task_id, t.email_template_id,
                     t.title, t.description,
                   t.due_date, t.status, t.created_at,
                   CONCAT_WS(' ', e.first_name, e.last_name) AS employee_name,
                   tt.title AS template_task_title
            FROM tasks t
            JOIN employees e ON e.id = t.employee_id
            LEFT JOIN template_tasks tt ON tt.id = t.template_task_id
            {where}
            ORDER BY {sort_column} {direction}, t.id ASC
            LIMIT %s OFFSET %s
        """,
            tuple(values),
        )
        return {
            "success": True,
            "tasks": [task_payload(row) for row in cursor.fetchall()],
            "total": total,
            "page": page,
            "total_pages": total_pages,
        }
    except Error as error:
        raise ApiError(f"Database error: {error}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_task_suggestions(field, query):
    if (
        field not in {"theme", "term", "employee", "template", "due_date", "created_at"}
        or len(query) < 3
    ):
        return {"success": True, "suggestions": []}
    connection = get_db_connection()
    if not connection:
        raise ApiError("Database connection error", 500)
    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        if field == "theme":
            sql = """SELECT DISTINCT t.theme AS value, t.theme AS label
                FROM tasks t WHERE t.theme LIKE %s ORDER BY label LIMIT 10"""
        elif field == "term":
            sql = """SELECT DISTINCT t.term AS value, t.term AS label
                FROM tasks t WHERE t.term LIKE %s ORDER BY label LIMIT 10"""
        elif field == "employee":
            sql = """SELECT DISTINCT e.id AS value,
                CONCAT_WS(' ', e.first_name, e.last_name) AS label
                FROM tasks t JOIN employees e ON e.id = t.employee_id
                WHERE CONCAT_WS(' ', e.first_name, e.last_name) LIKE %s
                ORDER BY label LIMIT 10"""
        elif field == "template":
            sql = """SELECT DISTINCT tt.id AS value, tt.title AS label
                FROM tasks t JOIN template_tasks tt ON tt.id = t.template_task_id
                WHERE tt.title LIKE %s ORDER BY label LIMIT 10"""
        else:
            column = "t.due_date" if field == "due_date" else "t.created_at"
            sql = f"SELECT DISTINCT CAST({column} AS CHAR) AS value, CAST({column} AS CHAR) AS label FROM tasks WHERE CAST({column} AS CHAR) LIKE %s ORDER BY value LIMIT 10"
        cursor.execute(sql, (f"%{query}%",))
        return {
            "success": True,
            "suggestions": [dict(row) for row in cursor.fetchall()],
        }
    except Error as error:
        raise ApiError(f"Database error: {error}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def assign_tasks(data):
    try:
        employee_id = int(data["employee_id"])
        template_id = int(data["template_id"])
        entry_date = date.fromisoformat(data["entry_date"])
    except (KeyError, TypeError, ValueError):
        raise ApiError(
            "Mitarbeiter, Eintrittsdatum und Vorlage sind erforderlich.", 400
        )

    connection = get_db_connection()
    if not connection:
        raise ApiError("Database connection error", 500)
    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT id, CONCAT_WS(' ', first_name, last_name) AS name, location_id
            FROM employees WHERE id = %s
        """,
            (employee_id,),
        )
        employee = cursor.fetchone()
        if not employee:
            raise ApiError("Mitarbeiter nicht gefunden.", 404)
        cursor.execute(
            """
            SELECT template_tasks.id, template_tasks.title, template_tasks.description,
                   template_tasks.due_offset_days, template_tasks.email_template_id,
                   template_tasks.responsible_function_id,
                   COALESCE(functions.name, '') AS responsible_name
            FROM template_tasks
            LEFT JOIN functions ON functions.id = template_tasks.responsible_function_id
            WHERE template_tasks.template_id = %s
            ORDER BY template_tasks.step, template_tasks.id
        """,
            (template_id,),
        )
        template_tasks = cursor.fetchall()
        if not template_tasks:
            raise ApiError("Die Vorlage enthält keine Aufgaben.", 400)
        if any(task["responsible_function_id"] is None for task in template_tasks):
            raise ApiError(
                "Alle Vorlagenaufgaben benötigen einen Verantwortlichen.", 400
            )

        function_ids = list(
            {
                task["responsible_function_id"]
                for task in template_tasks
                if (task["responsible_name"] or "").strip().casefold() != "newbie"
            }
        )
        responsible_employee_by_function = {}
        if function_ids:
            placeholders = ", ".join(["%s"] * len(function_ids))
            cursor.execute(
                f"""
                SELECT id, function_id
                FROM employees
                WHERE location_id = %s AND function_id IN ({placeholders})
            """,
                (employee["location_id"], *function_ids),
            )
            for row in cursor.fetchall():
                responsible_employee_by_function.setdefault(
                    row["function_id"], row["id"]
                )

        missing_functions = sorted(
            {
                task["responsible_name"] or str(task["responsible_function_id"])
                for task in template_tasks
                if (task["responsible_name"] or "").strip().casefold() != "newbie"
                and task["responsible_function_id"]
                not in responsible_employee_by_function
            }
        )
        if missing_functions:
            raise ApiError(
                f"Am Standort des Mitarbeiters fehlt ein Mitarbeiter mit folgender Funktion: {', '.join(missing_functions)}",
                400,
            )

        cursor.execute(
            """
            SELECT templates.name AS template_name, process_types.name AS process_type_name,
                   jobs.name AS job_name, locations.name AS location_name
            FROM templates
            LEFT JOIN process_types ON process_types.id = templates.process_type_id
            LEFT JOIN jobs ON jobs.id = templates.job_id
            LEFT JOIN locations ON locations.id = templates.location_id
            WHERE templates.id = %s
        """,
            (template_id,),
        )
        template_info = cursor.fetchone() or {}
        task_term = " | ".join(
            [
                template_info.get("process_type_name") or "",
                template_info.get("template_name") or "",
                employee["name"] or "",
            ]
        )
        placeholder_values = {
            "[NEWBIE]": employee["name"] or "",
            "[JOB]": template_info.get("job_name") or "",
            "[STARTDATE]": entry_date.isoformat(),
            "[STARTDATUM]": entry_date.isoformat(),
            "[LOCATION]": template_info.get("location_name") or "",
            "[STANDORT]": template_info.get("location_name") or "",
        }

        def _apply_placeholders(text):
            if not text:
                return text
            for keyword, value in placeholder_values.items():
                text = text.replace(keyword, value)
            return text

        for template_task in template_tasks:
            due_date = entry_date - timedelta(
                days=int(template_task["due_offset_days"] or 0)
            )
            if (template_task["responsible_name"] or "").strip().casefold() == "newbie":
                responsible_employee_id = employee_id
            else:
                responsible_employee_id = responsible_employee_by_function[
                    template_task["responsible_function_id"]
                ]
            cursor.execute(
                """
                                INSERT INTO tasks
                                    (term, theme, employee_id, template_task_id, title, description, due_date, status, email_template_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, 'open', %s)
                            """,
                (
                    task_term,
                    template_task["responsible_name"],
                    responsible_employee_id,
                    template_task["id"],
                    _apply_placeholders(template_task["title"]),
                    _apply_placeholders(template_task["description"]),
                    due_date,
                    template_task["email_template_id"],
                ),
            )
        connection.commit()
        return {"success": True, "created": len(template_tasks)}
    except ApiError:
        connection.rollback()
        raise
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {error}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def create_single_task(data):
    try:
        employee_id = int(data["employee_id"])
    except (KeyError, TypeError, ValueError):
        raise ApiError("Ein Mitarbeiter ist erforderlich.", 400)
    try:
        due_date = date.fromisoformat(data["due_date"])
    except (KeyError, TypeError, ValueError):
        raise ApiError("Ein gültiges Fälligkeitsdatum ist erforderlich.", 400)
    title = str(data.get("title", "")).strip()
    if not title:
        raise ApiError("Ein Titel ist erforderlich.", 400)
    if due_date < date.today():
        raise ApiError(
            "Das Fälligkeitsdatum darf nicht in der Vergangenheit liegen.", 400
        )
    try:
        email_template_id = (
            int(data["email_template_id"]) if data.get("email_template_id") else None
        )
    except (TypeError, ValueError):
        raise ApiError("Ungültige E-Mail-Vorlage.", 400)
    connection = get_db_connection()
    if not connection:
        raise ApiError("Database connection error", 500)
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM employees WHERE id = %s", (employee_id,))
        if not cursor.fetchone():
            raise ApiError("Mitarbeiter nicht gefunden.", 404)
        cursor.execute(
            """
                        INSERT INTO tasks (theme, employee_id, template_task_id, title, description, due_date, status, email_template_id)
                        VALUES (%s, %s, NULL, %s, %s, %s, 'open', %s)
                """,
            (
                str(data.get("theme", "")).strip(),
                employee_id,
                title,
                str(data.get("description", "")).strip(),
                due_date,
                email_template_id,
            ),
        )
        connection.commit()
        return {"success": True, "id": cursor.lastrowid}
    except ApiError:
        connection.rollback()
        raise
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {error}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def delete_task(task_id):
    connection = get_db_connection()
    if not connection:
        raise ApiError("Database connection error", 500)
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Aufgabe nicht gefunden.", 404)
        connection.commit()
        return {"success": True}
    except ApiError:
        raise
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {error}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_task_email_preview(task_id, is_manager, session_user_id):
    connection = get_db_connection()
    if not connection:
        raise ApiError("Database connection error", 500)
    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        owner_filter = "" if is_manager else " AND t.employee_id = %s"
        values = [task_id]
        if owner_filter:
            values.append(session_user_id)
        cursor.execute(
            f"""
            SELECT t.id, t.email_template_id, t.title AS task_title,
                   et.name, et.subject, et.body_html, et.body_text
            FROM tasks t
            LEFT JOIN email_templates et ON et.id = t.email_template_id
            WHERE t.id = %s{owner_filter}
        """,
            values,
        )
        task = cursor.fetchone()
        if not task:
            raise ApiError("Aufgabe nicht gefunden.", 404)
        if task["email_template_id"] is None:
            raise ApiError(
                "Für diese Aufgabe ist keine E-Mail-Vorlage hinterlegt.", 404
            )
        return {"success": True, "email_template": dict(task)}
    except ApiError:
        raise
    except Error as error:
        raise ApiError(f"Database error: {error}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_task(task_id, data, is_manager, session_user_id):
    status = data.get("status")
    if status not in TASK_STATUSES:
        raise ApiError("Ungültiger Status.", 400)
    try:
        due_date = date.fromisoformat(data.get("due_date", ""))
    except (TypeError, ValueError):
        raise ApiError("Ein gültiges Fälligkeitsdatum ist erforderlich.", 400)
    connection = get_db_connection()
    if not connection:
        raise ApiError("Database connection error", 500)
    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        allowed = "" if is_manager else " AND employee_id = %s"
        lookup_values = [task_id]
        if allowed:
            lookup_values.append(session_user_id)
        cursor.execute(
            f"SELECT due_date FROM tasks WHERE id = %s{allowed}", lookup_values
        )
        current_task = cursor.fetchone()
        if not current_task:
            raise ApiError("Aufgabe nicht gefunden oder nicht erlaubt.", 404)
        current_due_date = current_task["due_date"]
        if due_date < date.today() and due_date != current_due_date:
            raise ApiError(
                "Das Fälligkeitsdatum darf nicht in der Vergangenheit liegen.", 400
            )
        values = [
            data.get("title", "").strip(),
            data.get("description", "").strip(),
            due_date,
            status,
            task_id,
        ]
        if allowed:
            values.append(session_user_id)
        cursor.execute(
            f"""
            UPDATE tasks SET title = %s, description = %s, due_date = %s, status = %s
            WHERE id = %s{allowed}
        """,
            values,
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Aufgabe nicht gefunden oder nicht erlaubt.", 404)
        connection.commit()
        return {"success": True, "id": task_id}
    except ApiError:
        connection.rollback()
        raise
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {error}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()
