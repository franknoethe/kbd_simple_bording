"""Send due-task reminders. Run this script once per day from cron/Task Scheduler."""
import os
import smtplib
from email.message import EmailMessage
from datetime import date

from app import get_db_connection
from pymysql import Error
from pymysql.cursors import DictCursor


def send_reminders():
    connection = get_db_connection()
    if not connection:
        raise RuntimeError('Database connection error')
    cursor = None
    sent = 0
    try:
        cursor = connection.cursor(cursor=DictCursor)
        cursor.execute('''
            SELECT t.id, t.title, t.description, e.email,
                   et.subject, et.body_html, et.body_text
            FROM tasks t
            JOIN employees e ON e.id = t.employee_id
            JOIN template_tasks tt ON tt.id = t.template_task_id
            LEFT JOIN email_templates et ON et.id = tt.email_template_id
            WHERE t.due_date <= %s AND t.status <> 'completed'
              AND t.reminder_sent_at IS NULL AND e.email IS NOT NULL
        ''', (date.today(),))
        due_tasks = cursor.fetchall()
        smtp_host = os.environ.get('KBD_SMTP_HOST')
        if not smtp_host:
            raise RuntimeError('KBD_SMTP_HOST ist nicht gesetzt.')
        smtp_port = int(os.environ.get('KBD_SMTP_PORT', '587'))
        sender = os.environ.get('KBD_SMTP_FROM', 'boarding@localhost')
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            if os.environ.get('KBD_SMTP_TLS', '1') == '1':
                smtp.starttls()
            username = os.environ.get('KBD_SMTP_USER')
            if username:
                smtp.login(username, os.environ.get('KBD_SMTP_PASSWORD', ''))
            for task in due_tasks:
                message = EmailMessage()
                message['Subject'] = task['subject'] or task['title']
                message['From'] = sender
                message['To'] = task['email']
                message.set_content(task['body_text'] or task['description'] or task['title'])
                if task['body_html']:
                    message.add_alternative(task['body_html'], subtype='html')
                smtp.send_message(message)
                cursor.execute('UPDATE tasks SET reminder_sent_at = CURRENT_TIMESTAMP WHERE id = %s', (task['id'],))
                sent += 1
        connection.commit()
        return sent
    except Error:
        connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        connection.close()


if __name__ == '__main__':
    print(f'{send_reminders()} Erinnerungen versendet.')