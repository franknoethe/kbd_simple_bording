import os

SECRET_KEY = os.environ.get("KBD_SECRET_KEY", "kbd-simple-boarding-development-key")

# MariaDB Database Configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "kbd_hr_boarding",
    "port": 3306,
}
