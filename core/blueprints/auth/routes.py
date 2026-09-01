import hmac

from flask import redirect, render_template, request, session, url_for
from pymysql import Error
from pymysql.cursors import DictCursor as RealDictCursor
from werkzeug.security import check_password_hash

from core.blueprints.auth import auth_bp
from core.db import get_db_connection


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("employee.index"))

    error = None
    username = request.form.get("username", "").strip()
    if request.method == "POST":
        password = request.form.get("password", "")
        connection = get_db_connection()
        cursor = None
        if not connection:
            error = "Die Datenbank ist momentan nicht erreichbar."
        else:
            try:
                cursor = connection.cursor(cursor_factory=RealDictCursor)
                cursor.execute(
                    """
                    SELECT e.id, e.first_name, e.last_name, e.username,
                           e.password_hash, COALESCE(r.name, '') AS role
                    FROM employees e
                    LEFT JOIN roles r ON r.id = e.role_id
                    WHERE LOWER(e.username) = LOWER(%s)
                """,
                    (username,),
                )
                employee = cursor.fetchone()
                stored_password = employee.get("password_hash") if employee else None
                password_matches = False
                if stored_password:
                    stored_password = str(stored_password)
                    if "$" in stored_password:
                        try:
                            password_matches = check_password_hash(
                                stored_password, password
                            )
                        except ValueError:
                            password_matches = False
                    else:
                        password_matches = hmac.compare_digest(
                            stored_password, password
                        )

                if employee and password_matches:
                    session.clear()
                    session["user"] = {
                        "id": employee["id"],
                        "name": f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip(),
                        "username": employee["username"],
                        "role": employee.get("role", ""),
                    }
                    next_url = request.args.get("next", "")
                    if not next_url.startswith("/") or next_url.startswith("//"):
                        next_url = url_for("employee.index")
                    return redirect(next_url)
                error = "Benutzername oder Passwort ist nicht korrekt."
            except Error:
                error = "Die Anmeldung konnte nicht geprüft werden."
            finally:
                if cursor:
                    cursor.close()
                connection.close()

    return render_template("login.html", error=error, username=username)


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
