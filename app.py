from flask import Flask, jsonify, render_template, request
from pathlib import Path
from io import BytesIO
from base64 import b64encode
import re
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
import olefile

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
    page_size = 800
    try:
        current_page = max(1, int(request.args.get('page', 1)))
    except (TypeError, ValueError):
        current_page = 1

    total_employees = len(EMPLOYEES)
    total_pages = max(1, (total_employees + page_size - 1) // page_size)
    current_page = min(current_page, total_pages)
    start_index = (current_page - 1) * page_size
    page_employees = EMPLOYEES[start_index:start_index + page_size]

    return render_template(
        "index.html",
        employees=page_employees,
        status_labels=STATUS_LABELS,
        stats=compute_stats(),
        current_page=current_page,
        total_pages=total_pages,
        total_employees=total_employees,
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


@app.route("/process-types")
def process_types_page():
    """Render process types CRUD page."""
    return render_template("process_types.html")


@app.route("/roles")
def roles_page():
    """Render roles CRUD page."""
    return render_template("roles.html")


@app.route("/email-templates")
def email_templates_page():
    """Render email templates CRUD page."""
    return render_template("email_templates.html")


def read_oft_property(ole, property_id):
    """Read a common MAPI string property from an Outlook OLE file."""
    for data_type in ("001F", "001E", "001A"):
        stream_name = f"__substg1.0_{property_id}{data_type}"
        if ole.exists(stream_name):
            raw = ole.openstream(stream_name).read()
            if data_type == "001F":
                return raw.decode("utf-16-le", errors="replace").rstrip("\x00")
            return raw.decode("utf-8", errors="replace").rstrip("\x00")
    return ""


def read_oft_body_html(ole):
    """Read the HTML body property stored by Outlook."""
    for data_type in ("0102", "001F", "001E", "001A"):
        stream_name = f"__substg1.0_1013{data_type}"
        if ole.exists(stream_name):
            raw = ole.openstream(stream_name).read()
            if data_type == "0102":
                for encoding in ("utf-8", "utf-16-le", "cp1252"):
                    try:
                        decoded = raw.decode(encoding)
                        if "<" in decoded or "html" in decoded.lower():
                            return decoded.rstrip("\x00")
                    except UnicodeDecodeError:
                        continue
                return raw.decode("utf-8", errors="replace").rstrip("\x00")
            if data_type == "001F":
                return raw.decode("utf-16-le", errors="replace").rstrip("\x00")
            return raw.decode("cp1252", errors="replace").rstrip("\x00")
    return ""


def read_oft_stream(ole, directory, stream_name):
    """Read a stream from an Outlook attachment storage directory."""
    full_path = list(directory) + [stream_name]
    if not ole.exists(full_path):
        return b""
    return ole.openstream(full_path).read()


def read_oft_attachment_property(ole, directory, property_id):
    """Read a string attachment property from an OFT storage directory."""
    for data_type, encoding in (("001F", "utf-16-le"), ("001E", "cp1252"), ("001A", "cp1252")):
        raw = read_oft_stream(ole, directory, f"__substg1.0_{property_id}{data_type}")
        if raw:
            return raw.decode(encoding, errors="replace").rstrip("\x00")
    return ""


def read_oft_attachment_binary(ole, directory):
    """Read the binary payload of an Outlook attachment."""
    for stream_parts in ole.listdir(streams=True, storages=False):
        stream_path = tuple(stream_parts)
        if tuple(stream_path[:-1]) != tuple(directory):
            continue
        stream_name = stream_path[-1].lower()
        if stream_name.endswith("37010102"):
            return ole.openstream(stream_path).read()
    return b""


def embed_oft_inline_images(ole, body_html):
    """Replace cid image references with embedded data URLs from OFT attachments."""
    if not body_html or "cid:" not in body_html:
        return body_html

    cid_data = {}
    image_data = []
    for directory_parts in ole.listdir(storages=True, streams=False):
        directory = tuple(directory_parts)
        if not any(part.lower().startswith("__attach") for part in directory):
            continue
        content_id = read_oft_attachment_property(ole, directory, "3712")
        content_location = read_oft_attachment_property(ole, directory, "3713")
        attachment_data = read_oft_attachment_binary(ole, directory)
        mime_type = read_oft_attachment_property(ole, directory, "370e") or "application/octet-stream"
        if attachment_data and mime_type.lower().startswith("image/"):
            data_url = f"data:{mime_type};base64,{b64encode(attachment_data).decode('ascii')}"
            image_data.append((len(attachment_data), data_url))
        if content_id and attachment_data:
            normalized_id = content_id.strip().strip("<>")
            data_url = f"data:{mime_type};base64,{b64encode(attachment_data).decode('ascii')}"
            cid_data[normalized_id.lower()] = data_url
            if content_location:
                cid_data[content_location.strip().lower()] = data_url

    largest_image = max(image_data, default=(0, ""), key=lambda item: item[0])[1]

    def replace_cid(match):
        content_id = match.group(1).strip().strip("<>").lower()
        data_url = cid_data.get(content_id, "")
        if data_url.startswith("data:image/"):
            encoded_payload = data_url.split(",", 1)[-1]
            if len(encoded_payload) <= 256 and largest_image:
                data_url = largest_image
        return data_url or match.group(0)

    return re.sub(r"cid:([^\"'\s>]+)", replace_cid, body_html, flags=re.IGNORECASE)


def parse_oft_file(file_storage):
    """Extract subject, HTML and plain text from an Outlook .oft file."""
    file_bytes = file_storage.read()
    if not file_bytes:
        raise ValueError("Die Outlookvorlage ist leer.")

    try:
        ole = olefile.OleFileIO(BytesIO(file_bytes))
    except (OSError, ValueError, olefile.olefile.OleFileError) as error:
        raise ValueError("Die Datei ist keine gültige Outlookvorlage.") from error

    with ole:
        subject = read_oft_property(ole, "0037")
        body_text = read_oft_property(ole, "1000")
        body_html = read_oft_body_html(ole)
        body_html = embed_oft_inline_images(ole, body_html)

    name = Path(file_storage.filename or "Vorlage.oft").stem
    return {
        "name": name,
        "subject": subject or name,
        "body_html": body_html,
        "body_text": body_text if not body_html else "",
        "active": True,
    }


@app.route("/api/email-templates", methods=['GET'])
def get_email_templates():
    """Get a filtered, sorted page of email templates."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    sort_columns = {'name': 'name', 'subject': 'subject'}
    sort_key = request.args.get('sort', 'name')
    direction = 'DESC' if request.args.get('direction', 'asc').lower() == 'desc' else 'ASC'
    sort_column = sort_columns.get(sort_key, 'name')
    filters = {
        'name': request.args.get('name', '').strip(),
        'subject': request.args.get('subject', '').strip(),
        'body_html': request.args.get('body_html', '').strip(),
        'body_text': request.args.get('body_text', '').strip(),
    }
    try:
        page = max(1, int(request.args.get('page', 1)))
    except (TypeError, ValueError):
        page = 1
    page_size = 800

    try:
        where_parts = []
        values = []
        for column, value in filters.items():
            if len(value) >= 3:
                where_parts.append(f"COALESCE({column}, '') ILIKE %s")
                values.append(f"%{value}%")
        where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ''
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SELECT COUNT(*) AS total FROM email_templates {where_sql}", values)
        total = cursor.fetchone()['total']
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = min(page, total_pages)
        cursor.execute(f'''
            SELECT id, name, subject, body_html, body_text, active
            FROM email_templates {where_sql}
            ORDER BY {sort_column} {direction} NULLS LAST, id ASC
            LIMIT %s OFFSET %s
        ''', values + [page_size, (page - 1) * page_size])
        templates = [dict(item) for item in cursor.fetchall()]
        return jsonify({'success': True, 'email_templates': templates,
                        'total': total, 'page': page, 'total_pages': total_pages})
    except Error as error:
        return jsonify({'success': False, 'message': f'Database error: {str(error)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/email-templates", methods=['POST'])
def create_email_template():
    """Create an email template."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        subject = str(data.get('subject', '')).strip()
        body_html = str(data.get('body_html', ''))
        body_text = str(data.get('body_text', ''))
        active = bool(data.get('active', True))
        if not name or not subject:
            return jsonify({'success': False, 'message': 'Name und Betreff sind erforderlich.'}), 400
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            INSERT INTO email_templates (name, subject, body_html, body_text, active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, subject, body_html, body_text, active
        ''', (name, subject, body_html, body_text, active))
        template = dict(cursor.fetchone())
        connection.commit()
        return jsonify({'success': True, 'email_template': template}), 201
    except Error as error:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(error)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/email-templates/suggestions", methods=['GET'])
def get_email_template_suggestions():
    """Return up to ten matching values for a template filter."""
    field_map = {'name': 'name', 'subject': 'subject', 'body_html': 'body_html', 'body_text': 'body_text'}
    field = request.args.get('field', '')
    query = request.args.get('q', '').strip()
    if field not in field_map or len(query) < 3:
        return jsonify({'success': True, 'email_templates': []})
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    try:
        column = field_map[field]
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f'''
            SELECT id, name, subject, body_html, body_text
            FROM email_templates
            WHERE COALESCE({column}, '') ILIKE %s
            ORDER BY {column} ASC NULLS LAST, id ASC
            LIMIT 10
        ''', (f'%{query}%',))
        return jsonify({'success': True, 'email_templates': [dict(item) for item in cursor.fetchall()]})
    except Error as error:
        return jsonify({'success': False, 'message': f'Database error: {str(error)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/email-templates/<int:template_id>", methods=['PUT'])
def update_email_template(template_id):
    """Update an email template."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        subject = str(data.get('subject', '')).strip()
        if not name or not subject:
            return jsonify({'success': False, 'message': 'Name und Betreff sind erforderlich.'}), 400
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            UPDATE email_templates
            SET name = %s, subject = %s, body_html = %s, body_text = %s, active = %s
            WHERE id = %s
            RETURNING id, name, subject, body_html, body_text, active
        ''', (name, subject, str(data.get('body_html', '')), str(data.get('body_text', '')),
              bool(data.get('active', True)), template_id))
        template = cursor.fetchone()
        if template is None:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Vorlage nicht gefunden.'}), 404
        connection.commit()
        return jsonify({'success': True, 'email_template': dict(template)})
    except Error as error:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(error)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/email-templates/<int:template_id>", methods=['DELETE'])
def delete_email_template(template_id):
    """Delete an email template."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM email_templates WHERE id = %s', (template_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Vorlage nicht gefunden.'}), 404
        connection.commit()
        return jsonify({'success': True})
    except Error as error:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(error)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/email-templates/import-preview", methods=['POST'])
def preview_email_template_import():
    """Parse an uploaded Outlook template without writing to the database."""
    uploaded_file = request.files.get('file')
    if not uploaded_file or not uploaded_file.filename.lower().endswith('.oft'):
        return jsonify({'success': False, 'message': 'Bitte eine .oft-Datei auswählen.'}), 400
    try:
        return jsonify({'success': True, 'email_template': parse_oft_file(uploaded_file)})
    except ValueError as error:
        return jsonify({'success': False, 'message': str(error)}), 400


@app.route("/api/roles", methods=['GET'])
def get_roles():
    """Get all roles from PostgreSQL."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, name FROM roles ORDER BY name ASC')
        roles = cursor.fetchall()
        return jsonify({'success': True, 'roles': [dict(item) for item in roles]})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/roles", methods=['POST'])
def create_role():
    """Create a role."""
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
            INSERT INTO roles (name)
            VALUES (%s)
            RETURNING id, name
        ''', (name,))
        role = cursor.fetchone()
        connection.commit()
        return jsonify({'success': True, 'role': dict(role)}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/roles/<int:role_id>", methods=['PUT'])
def update_role(role_id):
    """Update a role."""
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
            UPDATE roles
            SET name = %s
            WHERE id = %s
            RETURNING id, name
        ''', (name, role_id))
        role = cursor.fetchone()
        if role is None:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Rolle nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True, 'role': dict(role)})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/roles/<int:role_id>", methods=['DELETE'])
def delete_role(role_id):
    """Delete a role."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM roles WHERE id = %s', (role_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Rolle nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/process-types", methods=['GET'])
def get_process_types():
    """Get all process types from PostgreSQL."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, name FROM process_types ORDER BY name ASC')
        process_types = cursor.fetchall()
        return jsonify({'success': True, 'process_types': [dict(item) for item in process_types]})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/process-types", methods=['POST'])
def create_process_type():
    """Create a process type."""
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
            INSERT INTO process_types (name)
            VALUES (%s)
            RETURNING id, name
        ''', (name,))
        process_type = cursor.fetchone()
        connection.commit()
        return jsonify({'success': True, 'process_type': dict(process_type)}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/process-types/<int:process_type_id>", methods=['PUT'])
def update_process_type(process_type_id):
    """Update a process type."""
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
            UPDATE process_types
            SET name = %s
            WHERE id = %s
            RETURNING id, name
        ''', (name, process_type_id))
        process_type = cursor.fetchone()
        if process_type is None:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Prozessart nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True, 'process_type': dict(process_type)})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


@app.route("/api/process-types/<int:process_type_id>", methods=['DELETE'])
def delete_process_type(process_type_id):
    """Delete a process type."""
    connection = get_db_connection()
    cursor = None
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM process_types WHERE id = %s', (process_type_id,))
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({'success': False, 'message': 'Prozessart nicht gefunden.'}), 404

        connection.commit()
        return jsonify({'success': True})
    except Error as e:
        connection.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


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
        cursor.execute('SELECT id, location_id, name FROM jobs ORDER BY name ASC')
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
