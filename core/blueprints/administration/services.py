from pymysql import Error
from pymysql.cursors import DictCursor as RealDictCursor

from core.blueprints.administration.oft_import import parse_oft_file
from core.db import get_db_connection
from core.errors import ApiError

__all__ = ["parse_oft_file"]


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------


def get_email_templates(args):
    """Get a filtered, sorted page of email templates."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    sort_columns = {"name": "name", "subject": "subject"}
    sort_key = args.get("sort", "name")
    direction = "DESC" if args.get("direction", "asc").lower() == "desc" else "ASC"
    sort_column = sort_columns.get(sort_key, "name")
    filters = {
        "name": args.get("name", "").strip(),
        "subject": args.get("subject", "").strip(),
        "body_html": args.get("body_html", "").strip(),
        "body_text": args.get("body_text", "").strip(),
    }
    try:
        page = max(1, int(args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    page_size = 800

    try:
        where_parts = []
        values = []
        for column, value in filters.items():
            if len(value) >= 3:
                where_parts.append(f"COALESCE({column}, '') LIKE %s")
                values.append(f"%{value}%")
        where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            f"SELECT COUNT(*) AS total FROM email_templates {where_sql}", values
        )
        total = cursor.fetchone()["total"]
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = min(page, total_pages)
        cursor.execute(
            f"""
            SELECT id, name, subject, body_html, body_text, active
            FROM email_templates {where_sql}
            ORDER BY {sort_column} {direction}, id ASC
            LIMIT %s OFFSET %s
        """,
            values + [page_size, (page - 1) * page_size],
        )
        templates = [dict(item) for item in cursor.fetchall()]
        return {
            "success": True,
            "email_templates": templates,
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


def create_email_template(data):
    """Create an email template."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        name = str(data.get("name", "")).strip()
        subject = str(data.get("subject", "")).strip()
        body_html = str(data.get("body_html", ""))
        body_text = str(data.get("body_text", ""))
        active = bool(data.get("active", True))
        if not name or not subject:
            raise ApiError("Name und Betreff sind erforderlich.", 400)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO email_templates (name, subject, body_html, body_text, active)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (name, subject, body_html, body_text, active),
        )
        template = {
            "id": cursor.lastrowid,
            "name": name,
            "subject": subject,
            "body_html": body_html,
            "body_text": body_text,
            "active": active,
        }
        connection.commit()
        return {"success": True, "email_template": template}
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


def get_email_template_suggestions(field, query):
    """Return up to ten matching values for a template filter."""
    field_map = {
        "name": "name",
        "subject": "subject",
        "body_html": "body_html",
        "body_text": "body_text",
    }
    if field not in field_map or len(query) < 3:
        return {"success": True, "email_templates": []}
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        column = field_map[field]
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            f"""
            SELECT id, name, subject, body_html, body_text
            FROM email_templates
            WHERE COALESCE({column}, '') LIKE %s
            ORDER BY {column} ASC, id ASC
            LIMIT 10
        """,
            (f"%{query}%",),
        )
        return {
            "success": True,
            "email_templates": [dict(item) for item in cursor.fetchall()],
        }
    except Error as error:
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_email_template(template_id, data):
    """Update an email template."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        name = str(data.get("name", "")).strip()
        subject = str(data.get("subject", "")).strip()
        if not name or not subject:
            raise ApiError("Name und Betreff sind erforderlich.", 400)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE email_templates
            SET name = %s, subject = %s, body_html = %s, body_text = %s, active = %s
            WHERE id = %s
        """,
            (
                name,
                subject,
                str(data.get("body_html", "")),
                str(data.get("body_text", "")),
                bool(data.get("active", True)),
                template_id,
            ),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Vorlage nicht gefunden.", 404)
        template = {
            "id": template_id,
            "name": name,
            "subject": subject,
            "body_html": str(data.get("body_html", "")),
            "body_text": str(data.get("body_text", "")),
            "active": bool(data.get("active", True)),
        }
        connection.commit()
        return {"success": True, "email_template": template}
    except ApiError:
        raise
    except Error as error:
        connection.rollback()
        raise ApiError(f"Database error: {str(error)}", 500) from error
    finally:
        if cursor:
            cursor.close()
        connection.close()


def delete_email_template(template_id):
    """Delete an email template."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM email_templates WHERE id = %s", (template_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Vorlage nicht gefunden.", 404)
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


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------


def get_roles():
    """Get all roles from PostgreSQL."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, name FROM roles ORDER BY name ASC")
        roles = cursor.fetchall()
        return {"success": True, "roles": [dict(item) for item in roles]}
    except Error as e:
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def create_role(data):
    """Create a role."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ApiError("Name darf nicht leer sein.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("INSERT INTO roles (name) VALUES (%s)", (name,))
        role = {"id": cursor.lastrowid, "name": name}
        connection.commit()
        return {"success": True, "role": role}
    except ApiError:
        connection.rollback()
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_role(role_id, data):
    """Update a role."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ApiError("Name darf nicht leer sein.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("UPDATE roles SET name = %s WHERE id = %s", (name, role_id))
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Rolle nicht gefunden.", 404)

        connection.commit()
        return {"success": True, "role": {"id": role_id, "name": name}}
    except ApiError:
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def delete_role(role_id):
    """Delete a role."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Rolle nicht gefunden.", 404)

        connection.commit()
        return {"success": True}
    except ApiError:
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Process types
# ---------------------------------------------------------------------------


def get_process_types():
    """Get all process types from PostgreSQL."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, name FROM process_types ORDER BY name ASC")
        process_types = cursor.fetchall()
        return {
            "success": True,
            "process_types": [dict(item) for item in process_types],
        }
    except Error as e:
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def create_process_type(data):
    """Create a process type."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ApiError("Name darf nicht leer sein.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("INSERT INTO process_types (name) VALUES (%s)", (name,))
        process_type = {"id": cursor.lastrowid, "name": name}
        connection.commit()
        return {"success": True, "process_type": process_type}
    except ApiError:
        connection.rollback()
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_process_type(process_type_id, data):
    """Update a process type."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ApiError("Name darf nicht leer sein.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "UPDATE process_types SET name = %s WHERE id = %s", (name, process_type_id)
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Prozessart nicht gefunden.", 404)

        connection.commit()
        return {"success": True, "process_type": {"id": process_type_id, "name": name}}
    except ApiError:
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def delete_process_type(process_type_id):
    """Delete a process type."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM process_types WHERE id = %s", (process_type_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Prozessart nicht gefunden.", 404)

        connection.commit()
        return {"success": True}
    except ApiError:
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------


def get_jobs():
    """Get all jobs with their location names."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT jobs.id, jobs.location_id, jobs.name,
                   locations.name AS location_name
            FROM jobs
            LEFT JOIN locations ON locations.id = jobs.location_id
            ORDER BY jobs.name ASC
        """)
        jobs = cursor.fetchall()
        return {"success": True, "jobs": [dict(item) for item in jobs]}
    except Error as e:
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_job_options():
    """Get active locations for the jobs location combobox."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id, name FROM locations WHERE active = TRUE ORDER BY name ASC"
        )
        locations = cursor.fetchall()
        return {"success": True, "locations": [dict(item) for item in locations]}
    except Error as e:
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def create_job(data):
    """Create one job for each comma-separated name."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        names = [
            name.strip()
            for name in str(data.get("name", "")).split(",")
            if name.strip()
        ]
        location_id = data.get("location_id")
        if not names or location_id in (None, ""):
            raise ApiError("Name und Standort sind erforderlich.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        location_id = int(location_id)
        jobs = []
        for name in names:
            cursor.execute(
                """
                INSERT INTO jobs (location_id, name)
                VALUES (%s, %s)
            """,
                (location_id, name),
            )
            jobs.append(
                {"id": cursor.lastrowid, "location_id": location_id, "name": name}
            )
        connection.commit()
        return {"success": True, "jobs": jobs, "created": len(jobs)}
    except ApiError:
        connection.rollback()
        raise
    except (ValueError, TypeError) as error:
        connection.rollback()
        raise ApiError("Ungültiger Standort.", 400) from error
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_job(job_id, data):
    """Update a job."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        name = str(data.get("name", "")).strip()
        location_id = data.get("location_id")
        if not name or location_id in (None, ""):
            raise ApiError("Name und Standort sind erforderlich.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE jobs
            SET location_id = %s, name = %s
            WHERE id = %s
        """,
            (int(location_id), name, job_id),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Job nicht gefunden.", 404)

        connection.commit()
        return {
            "success": True,
            "job": {"id": job_id, "location_id": int(location_id), "name": name},
        }
    except ApiError:
        raise
    except (ValueError, TypeError) as error:
        connection.rollback()
        raise ApiError("Ungültiger Standort.", 400) from error
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def delete_job(job_id):
    """Delete a job."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Job nicht gefunden.", 404)

        connection.commit()
        return {"success": True}
    except ApiError:
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def get_functions():
    """Get all functions from PostgreSQL."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, name FROM functions ORDER BY name ASC")
        functions = cursor.fetchall()
        return {"success": True, "functions": [dict(item) for item in functions]}
    except Error as e:
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def create_function(data):
    """Create a function."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ApiError("Name darf nicht leer sein.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("INSERT INTO functions (name) VALUES (%s)", (name,))
        function = {"id": cursor.lastrowid, "name": name}
        connection.commit()
        return {"success": True, "function": function}
    except ApiError:
        connection.rollback()
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_function(function_id, data):
    """Update a function."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ApiError("Name darf nicht leer sein.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "UPDATE functions SET name = %s WHERE id = %s", (name, function_id)
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Funktion nicht gefunden.", 404)

        connection.commit()
        return {"success": True, "function": {"id": function_id, "name": name}}
    except ApiError:
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def delete_function(function_id):
    """Delete a function."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM functions WHERE id = %s", (function_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Funktion nicht gefunden.", 404)

        connection.commit()
        return {"success": True}
    except ApiError:
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------


def get_locations():
    """Get all locations from PostgreSQL."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, name, active FROM locations ORDER BY name ASC")
        locations = cursor.fetchall()
        return {"success": True, "locations": [dict(item) for item in locations]}
    except Error as e:
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def create_location(data):
    """Create a location."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        name = str(data.get("name", "")).strip()
        active = bool(data.get("active", True))

        if not name:
            raise ApiError("Name darf nicht leer sein.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO locations (name, active)
            VALUES (%s, %s)
        """,
            (name, active),
        )
        location = {"id": cursor.lastrowid, "name": name, "active": active}
        connection.commit()
        return {"success": True, "location": location}
    except ApiError:
        connection.rollback()
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_location(location_id, data):
    """Update a location."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        name = str(data.get("name", "")).strip()
        active = bool(data.get("active", True))

        if not name:
            raise ApiError("Name darf nicht leer sein.", 400)

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE locations
            SET name = %s, active = %s
            WHERE id = %s
        """,
            (name, active, location_id),
        )

        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Standort nicht gefunden.", 404)

        connection.commit()
        return {
            "success": True,
            "location": {"id": location_id, "name": name, "active": active},
        }
    except ApiError:
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def delete_location(location_id):
    """Delete a location."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM locations WHERE id = %s", (location_id,))

        if cursor.rowcount == 0:
            connection.rollback()
            raise ApiError("Standort nicht gefunden.", 404)

        connection.commit()
        return {"success": True}
    except ApiError:
        raise
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()
