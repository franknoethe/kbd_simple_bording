from flask import Flask, jsonify, render_template, request
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# PostgreSQL Database Configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'postgres',
    'password': 'root',
    'database': 'kbd_hr_boarding',
    'port': 5432
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

EMPLOYEES = [
    {
        "id": 1,
        "name": "Maya Schneider",
        "department": "IT",
        "role": "Junior Developer",
        "status": "in_progress",
        "progress": 72,
        "start_date": "2026-08-20",
        "location": "Berlin",
    },
    {
        "id": 2,
        "name": "Luca Meyer",
        "department": "HR",
        "role": "HR Specialist",
        "status": "approved",
        "progress": 100,
        "start_date": "2026-08-15",
        "location": "Hamburg",
    },
    {
        "id": 3,
        "name": "Nora Patel",
        "department": "Finance",
        "role": "Finance Analyst",
        "status": "pending",
        "progress": 36,
        "start_date": "2026-08-27",
        "location": "Munich",
    },
    {
        "id": 4,
        "name": "Felix Mueller",
        "department": "Operations",
        "role": "Operations Lead",
        "status": "review",
        "progress": 81,
        "start_date": "2026-09-02",
        "location": "Cologne",
    },
]

STATUS_LABELS = {
    "approved": "Approved",
    "in_progress": "In Progress",
    "pending": "Pending",
    "review": "In Review",
}


def compute_stats():
    total = len(EMPLOYEES)
    approved = sum(1 for item in EMPLOYEES if item["status"] == "approved")
    in_progress = sum(1 for item in EMPLOYEES if item["status"] == "in_progress")
    pending = sum(1 for item in EMPLOYEES if item["status"] == "pending")
    avg_progress = round(sum(item["progress"] for item in EMPLOYEES) / total, 1)
    return {
        "total": total,
        "approved": approved,
        "in_progress": in_progress,
        "pending": pending,
        "avg_progress": avg_progress,
    }


@app.route("/")
def index():
    return render_template(
        "index.html",
        employees=EMPLOYEES,
        status_labels=STATUS_LABELS,
        stats=compute_stats(),
    )


@app.route("/employees")
def employees_page():
    """Render employees CRUD page"""
    return render_template("employees.html")


@app.route("/locations")
def locations_page():
    """Render locations CRUD page."""
    return render_template("locations.html")


@app.route("/functions")
def functions_page():
    """Render functions CRUD page."""
    return render_template("functions.html")


@app.route("/jobs")
def jobs_page():
    """Render jobs CRUD page."""
    return render_template("jobs.html")


@app.route("/api/jobs", methods=['GET'])
def get_jobs():
    """Get all jobs with their location names."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            SELECT jobs.id, jobs.location_id, jobs.name,
                   locations.name AS location_name
            FROM jobs
            LEFT JOIN locations ON locations.id = jobs.location_id
            ORDER BY jobs.name ASC
        ''')
        jobs = cursor.fetchall()
        return jsonify({'success': True, 'jobs': [dict(item) for item in jobs]})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/job-options", methods=['GET'])
def get_job_options():
    """Get active locations for the jobs location combobox."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, name FROM locations WHERE active = TRUE ORDER BY name ASC')
        locations = cursor.fetchall()
        return jsonify({'success': True, 'locations': [dict(item) for item in locations]})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/jobs", methods=['POST'])
def create_job():
    """Create a job."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        location_id = data.get('location_id')
        if not name or location_id in (None, ''):
            return jsonify({'success': False, 'message': 'Name und Standort sind erforderlich.'}), 400

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            INSERT INTO jobs (location_id, name)
            VALUES (%s, %s)
            RETURNING id, location_id, name
        ''', (int(location_id), name))
        job = cursor.fetchone()
        connection.commit()
        return jsonify({'success': True, 'job': dict(job)}), 201
    except (ValueError, TypeError):
        connection.rollback()
        return jsonify({'success': False, 'message': 'Ungültiger Standort.'}), 400
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/jobs/<int:job_id>", methods=['PUT'])
def update_job(job_id):
    """Update a job."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        location_id = data.get('location_id')
        if not name or location_id in (None, ''):
            return jsonify({'success': False, 'message': 'Name und Standort sind erforderlich.'}), 400

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            UPDATE jobs
            SET location_id = %s, name = %s
            WHERE id = %s
            RETURNING id, location_id, name
        ''', (int(location_id), name, job_id))
        job = cursor.fetchone()
        if job is None:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Job nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True, 'job': dict(job)})
    except (ValueError, TypeError):
        connection.rollback()
        return jsonify({'success': False, 'message': 'Ungültiger Standort.'}), 400
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/jobs/<int:job_id>", methods=['DELETE'])
def delete_job(job_id):
    """Delete a job."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM jobs WHERE id = %s', (job_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Job nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/functions", methods=['GET'])
def get_functions():
    """Get all functions from PostgreSQL."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, name FROM functions ORDER BY name ASC')
        functions = cursor.fetchall()
        return jsonify({'success': True, 'functions': [dict(item) for item in functions]})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/functions", methods=['POST'])
def create_function():
    """Create a function."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        if not name:
            return jsonify({'success': False, 'message': 'Name darf nicht leer sein.'}), 400

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            INSERT INTO functions (name)
            VALUES (%s)
            RETURNING id, name
        ''', (name,))
        function = cursor.fetchone()
        connection.commit()
        return jsonify({'success': True, 'function': dict(function)}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/functions/<int:function_id>", methods=['PUT'])
def update_function(function_id):
    """Update a function."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        if not name:
            return jsonify({'success': False, 'message': 'Name darf nicht leer sein.'}), 400

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            UPDATE functions
            SET name = %s
            WHERE id = %s
            RETURNING id, name
        ''', (name, function_id))
        function = cursor.fetchone()
        if function is None:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Funktion nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True, 'function': dict(function)})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/functions/<int:function_id>", methods=['DELETE'])
def delete_function(function_id):
    """Delete a function."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM functions WHERE id = %s', (function_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Funktion nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/locations", methods=['GET'])
def get_locations():
    """Get all locations from PostgreSQL."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, name, active FROM locations ORDER BY name ASC')
        locations = cursor.fetchall()
        return jsonify({'success': True, 'locations': [dict(item) for item in locations]})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/locations", methods=['POST'])
def create_location():
    """Create a location."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        active = bool(data.get('active', True))

        if not name:
            return jsonify({'success': False, 'message': 'Name darf nicht leer sein.'}), 400

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            INSERT INTO locations (name, active)
            VALUES (%s, %s)
            RETURNING id, name, active
        ''', (name, active))
        location = cursor.fetchone()
        connection.commit()
        return jsonify({'success': True, 'location': dict(location)}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/locations/<int:location_id>", methods=['PUT'])
def update_location(location_id):
    """Update a location."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        active = bool(data.get('active', True))

        if not name:
            return jsonify({'success': False, 'message': 'Name darf nicht leer sein.'}), 400

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            UPDATE locations
            SET name = %s, active = %s
            WHERE id = %s
            RETURNING id, name, active
        ''', (name, active, location_id))
        location = cursor.fetchone()

        if location is None:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Standort nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True, 'location': dict(location)})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/locations/<int:location_id>", methods=['DELETE'])
def delete_location(location_id):
    """Delete a location."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM locations WHERE id = %s', (location_id,))

        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Standort nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/employees", methods=['GET'])
def get_employees():
    """Get all employees from database"""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
             SELECT id, first_name, last_name, email_business AS email,
                 NULLIF(BTRIM(department), '') AS department, username, location_id, job_id,
                 role_id, function_id
            FROM employees ORDER BY last_name asc
        ''')
        employees = cursor.fetchall()
        return jsonify({'success': True, 'employees': [dict(emp) for emp in employees]})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()
        connection.close()


@app.route("/api/employee-options", methods=['GET'])
def get_employee_options():
    """Get display names for employee foreign-key fields."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, name FROM locations WHERE active = TRUE ORDER BY name ASC')
        locations = cursor.fetchall()
        cursor.execute('SELECT id, name FROM jobs ORDER BY name ASC')
        jobs = cursor.fetchall()
        cursor.execute('SELECT id, name FROM roles ORDER BY name ASC')
        roles = cursor.fetchall()
        cursor.execute('SELECT id, name FROM functions ORDER BY name ASC')
        functions = cursor.fetchall()

        return jsonify({
            'success': True,
            'locations': [dict(item) for item in locations],
            'jobs': [dict(item) for item in jobs],
            'roles': [dict(item) for item in roles],
            'functions': [dict(item) for item in functions],
        })
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/employees", methods=['POST'])
def create_employee():
    """Create a new employee"""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        data = request.get_json()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            INSERT INTO employees
            (first_name, last_name, email_business, department, username, password_hash,
             location_id, job_id, role_id, function_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, first_name, last_name, email_business AS email,
                      department, username, location_id, job_id, role_id,
                      function_id
        ''', (
            data.get('first_name', ''),
            data.get('last_name', ''),
            data.get('email', ''),
            data.get('department', ''),
            data.get('username', ''),
            data.get('password', ''),
            data.get('location_id', 0),
            data.get('job_id', 0),
            data.get('role_id', 0),
            data.get('function_id', 0)
        ))
        
        employee = cursor.fetchone()
        connection.commit()
        
        return jsonify({'success': True, 'employee': dict(employee), 'id': employee['id']}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()
        connection.close()


@app.route("/api/employees/<int:employee_id>", methods=['PUT'])
def update_employee(employee_id):
    """Update an existing employee"""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        data = request.get_json()
        cursor = connection.cursor()
        
        cursor.execute('''
            UPDATE employees 
            SET first_name = %s, last_name = %s, email_business = %s,
                department = %s,
                username = %s, password_hash = %s, location_id = %s,
                job_id = %s, role_id = %s, function_id = %s
            WHERE id = %s
        ''', (
            data.get('first_name', ''),
            data.get('last_name', ''),
            data.get('email', ''),
            data.get('department', ''),
            data.get('username', ''),
            data.get('password', ''),
            data.get('location_id', 0),
            data.get('job_id', 0),
            data.get('role_id', 0),
            data.get('function_id', 0),
            employee_id
        ))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Employee not found'}), 404
        
        return jsonify({'success': True, 'id': employee_id})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()
        connection.close()


@app.route("/api/employees/<int:employee_id>", methods=['DELETE'])
def delete_employee(employee_id):
    """Delete an employee"""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM employees WHERE id = %s', (employee_id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Employee not found'}), 404
        
        return jsonify({'success': True})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
