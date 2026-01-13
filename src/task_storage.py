import sqlite3
import os
from datetime import datetime, date, timedelta

# ---------- ABSOLUTE BASE PATH ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- DATABASE PATH (BACKEND ONLY) ----------
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "catms.db")

# ---------- DEBUG PRINT (OPTIONAL) ----------
print("Using DB at:", DB_PATH)

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def ensure_task_time_columns():
    conn = get_connection()
    cur = conn.cursor()

    # Get existing columns
    cur.execute("PRAGMA table_info(tasks)")
    existing_columns = [row[1] for row in cur.fetchall()]

    # Add start_time if missing
    if "start_time" not in existing_columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN start_time TEXT")

    # Add end_time if missing
    if "end_time" not in existing_columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN end_time TEXT")

    # Add completed_at if missing
    if "completed_at" not in existing_columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")

    conn.commit()
    conn.close()



# ---------- TASK TABLE ----------
def create_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            category TEXT,
            priority TEXT,
            due_date TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

    # ✅ NEW (safe schema upgrade)
    ensure_task_time_columns()


def add_task(user_id, title, category, priority, due_date, start_time, end_time):
    conn = get_connection()
    conn.execute("""
        INSERT INTO tasks 
        (user_id, title, category, priority, due_date, start_time, end_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')
    """, (user_id, title, category, priority, due_date, start_time, end_time))
    conn.commit()
    conn.close()


def get_tasks(user_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, title, category, priority, due_date,
               start_time, end_time, status, completed_at
        FROM tasks
        WHERE user_id=?
    """, (user_id,)).fetchall()
    conn.close()
    return rows


def mark_completed(task_id):
    conn = get_connection()
    conn.execute("""
        UPDATE tasks
        SET status='Completed', completed_at=?
        WHERE id=?
    """, (datetime.now().isoformat(), task_id))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def create_streak_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER PRIMARY KEY,
            streak_count INTEGER DEFAULT 0,
            last_completed_date TEXT
        )
    """)

    conn.commit()
    conn.close()
    

def update_streak(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    today = date.today().isoformat()

    # Ensure streak row exists
    cur.execute(
        "SELECT streak_count, last_completed_date FROM streaks WHERE user_id=?",
        (user_id,)
    )
    row = cur.fetchone()

    if row is None:
        # First-ever completion
        cur.execute(
            "INSERT INTO streaks (user_id, streak_count, last_completed_date) VALUES (?, ?, ?)",
            (user_id, 1, today)
        )

    else:
        streak_count, last_date = row

        # If already updated today → do nothing
        if last_date == today:
            conn.close()
            return

        yesterday = (date.today() - timedelta(days=1)).isoformat()

        if last_date == yesterday:
            # Continue streak
            cur.execute(
                "UPDATE streaks SET streak_count = streak_count + 1, last_completed_date=? WHERE user_id=?",
                (today, user_id)
            )
        else:
            # Missed one or more days → reset streak
            cur.execute(
                "UPDATE streaks SET streak_count = 1, last_completed_date=? WHERE user_id=?",
                (today, user_id)
            )

    conn.commit()
    conn.close()

def snooze_task(task_id, minutes=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get existing end time and due date
    cur.execute(
        "SELECT due_date, end_time FROM tasks WHERE id=?",
        (task_id,)
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        return

    due_date, end_time = row

    end_dt = datetime.strptime(
        f"{due_date} {end_time}",
        "%Y-%m-%d %I:%M %p"
    )

    new_end_dt = end_dt + timedelta(minutes=minutes)
    new_end_time = new_end_dt.strftime("%I:%M %p")

    cur.execute(
        "UPDATE tasks SET end_time=? WHERE id=?",
        (new_end_time, task_id)
    )

    conn.commit()
    conn.close()