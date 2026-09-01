from pymysql import Error
from pymysql.cursors import DictCursor as RealDictCursor

from core.constants import STATUS_LABELS
from core.db import get_db_connection
from core.errors import ApiError


def get_dashboard_data(current_page):
    """Return the paginated onboarding candidate list plus stats for the dashboard.

    Mirrors the original index() route body 1:1 (same SQL, same status derivation).
    """
    page_size = 800
    connection = get_db_connection()
    candidates = []
    stats = {
        "total": 0,
        "approved": 0,
        "in_progress": 0,
        "pending": 0,
        "avg_progress": 0,
    }
    if connection:
        cursor = None
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT e.id,
                       CONCAT_WS(' ', e.first_name, e.last_name) AS name,
                      COALESCE(NULLIF(TRIM(e.department), ''), '') AS department,
                       COALESCE(l.name, '') AS location,
                       COALESCE(j.name, '') AS role,
                       process_cases.start_date,
                       COALESCE(task_counts.total_tasks, 0) AS total_tasks,
                       COALESCE(task_counts.open_tasks, 0) AS open_tasks,
                       COALESCE(task_counts.in_progress_tasks, 0) AS in_progress_tasks,
                       COALESCE(task_counts.completed_tasks, 0) AS completed_tasks
                FROM employees e
                JOIN functions f ON f.id = e.function_id AND LOWER(f.name) = LOWER(%s)
                LEFT JOIN locations l ON l.id = e.location_id
                LEFT JOIN jobs j ON j.id = e.job_id
                LEFT JOIN (
                    SELECT employee_id, MIN(start_date) AS start_date
                    FROM process_cases
                    GROUP BY employee_id
                ) process_cases ON process_cases.employee_id = e.id
                LEFT JOIN (
                    SELECT employee_id,
                           COUNT(*) AS total_tasks,
                           SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open_tasks,
                           SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress_tasks,
                           SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks
                    FROM tasks
                    GROUP BY employee_id
                ) task_counts ON task_counts.employee_id = e.id
                ORDER BY e.last_name ASC, e.first_name ASC
            """,
                ("Newbie",),
            )
            for row in cursor.fetchall():
                total_tasks = int(row.get("total_tasks") or 0)
                open_tasks = int(row.get("open_tasks") or 0)
                in_progress_tasks = int(row.get("in_progress_tasks") or 0)
                completed_tasks = int(row.get("completed_tasks") or 0)
                if open_tasks > 0:
                    status = "pending"
                elif in_progress_tasks > 0:
                    status = "in_progress"
                else:
                    status = "approved"
                progress = (
                    round((completed_tasks / total_tasks) * 100) if total_tasks else 0
                )
                candidates.append(
                    {
                        "id": row["id"],
                        "name": row["name"].strip(),
                        "department": row.get("department") or "",
                        "role": row.get("role") or "",
                        "status": status,
                        "progress": progress,
                        "start_date": (
                            row["start_date"].isoformat()
                            if row.get("start_date")
                            else ""
                        ),
                        "location": row.get("location") or "",
                    }
                )
        finally:
            if cursor:
                cursor.close()
            connection.close()

    total_employees = len(candidates)
    if total_employees:
        stats = {
            "total": total_employees,
            "approved": sum(1 for item in candidates if item["status"] == "approved"),
            "in_progress": sum(
                1 for item in candidates if item["status"] == "in_progress"
            ),
            "pending": sum(1 for item in candidates if item["status"] == "pending"),
            "avg_progress": round(
                sum(item["progress"] for item in candidates) / total_employees, 1
            ),
        }
    total_pages = max(1, (total_employees + page_size - 1) // page_size)
    current_page = min(current_page, total_pages)
    start_index = (current_page - 1) * page_size
    page_employees = candidates[start_index : start_index + page_size]

    return {
        "employees": page_employees,
        "status_labels": STATUS_LABELS,
        "stats": stats,
        "current_page": current_page,
        "total_pages": total_pages,
        "total_employees": total_employees,
    }


def list_employees():
    """Get all employees from database"""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
             SELECT id, first_name, last_name, email_business AS email,
                 NULLIF(TRIM(department), '') AS department, username, location_id, job_id,
                 role_id, function_id
            FROM employees ORDER BY last_name asc
        """)
        employees = cursor.fetchall()
        return {"success": True, "employees": [dict(emp) for emp in employees]}
    except Error as e:
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        cursor.close()
        connection.close()


def get_employee_options():
    """Get display names for employee foreign-key fields."""
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
        cursor.execute("SELECT id, location_id, name FROM jobs ORDER BY name ASC")
        jobs = cursor.fetchall()
        cursor.execute("SELECT id, name FROM roles ORDER BY name ASC")
        roles = cursor.fetchall()
        cursor.execute("SELECT id, name FROM functions ORDER BY name ASC")
        functions = cursor.fetchall()

        return {
            "success": True,
            "locations": [dict(item) for item in locations],
            "jobs": [dict(item) for item in jobs],
            "roles": [dict(item) for item in roles],
            "functions": [dict(item) for item in functions],
        }
    except Error as e:
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        if cursor:
            cursor.close()
        connection.close()


def create_employee(data):
    """Create a new employee"""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            INSERT INTO employees
            (first_name, last_name, email_business, department, username, password_hash,
             location_id, job_id, role_id, function_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                data.get("first_name", ""),
                data.get("last_name", ""),
                data.get("email", ""),
                data.get("department", ""),
                data.get("username", ""),
                data.get("password", ""),
                data.get("location_id", 0),
                data.get("job_id", 0),
                data.get("role_id", 0),
                data.get("function_id", 0),
            ),
        )

        employee = {
            "id": cursor.lastrowid,
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "email": data.get("email", ""),
            "department": data.get("department", ""),
            "username": data.get("username", ""),
            "location_id": data.get("location_id", 0),
            "job_id": data.get("job_id", 0),
            "role_id": data.get("role_id", 0),
            "function_id": data.get("function_id", 0),
        }
        connection.commit()

        return {"success": True, "employee": employee, "id": employee["id"]}
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        cursor.close()
        connection.close()


def update_employee(employee_id, data):
    """Update an existing employee"""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE employees 
            SET first_name = %s, last_name = %s, email_business = %s,
                department = %s,
                username = %s, password_hash = %s, location_id = %s,
                job_id = %s, role_id = %s, function_id = %s
            WHERE id = %s
        """,
            (
                data.get("first_name", ""),
                data.get("last_name", ""),
                data.get("email", ""),
                data.get("department", ""),
                data.get("username", ""),
                data.get("password", ""),
                data.get("location_id", 0),
                data.get("job_id", 0),
                data.get("role_id", 0),
                data.get("function_id", 0),
                employee_id,
            ),
        )
        connection.commit()

        if cursor.rowcount == 0:
            raise ApiError("Employee not found", 404)

        return {"success": True, "id": employee_id}
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        cursor.close()
        connection.close()


def delete_employee(employee_id):
    """Delete an employee"""
    connection = get_db_connection()
    cursor = None
    if not connection:
        raise ApiError("Database connection error", 500)

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
        connection.commit()

        if cursor.rowcount == 0:
            raise ApiError("Employee not found", 404)

        return {"success": True}
    except Error as e:
        connection.rollback()
        raise ApiError(f"Database error: {str(e)}", 500) from e
    finally:
        cursor.close()
        connection.close()
