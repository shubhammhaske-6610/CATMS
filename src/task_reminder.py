import time
import sqlite3
import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, timedelta

# ---------- DB PATH ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "catms.db")

# ---------- EMAIL CONFIG (REMINDER ONLY) ----------
EMAIL_SENDER = "youremail@gmail.com"      
EMAIL_PASSWORD = "your_email_password"   

def send_task_reminder_email(to_email, task_title, start_time):
    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    msg["Subject"] = "⏰ Task Reminder – CATMS"

    msg.set_content(
        f"""
Hello 👋,

Your task is starting soon.

📌 Task: {task_title}
⏰ Start Time: {start_time}

This is a 5-minute reminder.

– CATMS
        """
    )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def run_scheduler(user_id):
    reminded = set()

    while True:
        now = datetime.now()

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT t.id, t.title, t.due_date, t.start_time, u.email
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE t.user_id = ?
              AND t.status = 'Pending'
        """, (user_id,))

        tasks = cur.fetchall()
        conn.close()

        for task_id, title, due_date, start_time, email in tasks:
            try:
                task_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                task_time = datetime.strptime(start_time, "%I:%M %p").time()
                task_start = datetime.combine(task_date, task_time)
                reminder_time = task_start - timedelta(minutes=5)

                if reminder_time <= now < reminder_time + timedelta(seconds=60):
                    if task_id not in reminded:
                        send_task_reminder_email(email, title, start_time)
                        reminded.add(task_id)

            except:
                pass

        time.sleep(30)
