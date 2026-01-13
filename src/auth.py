import sqlite3
import os
import hashlib
import random
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "catms.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def create_user_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT,
            profile_image BLOB
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, email, password):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def authenticate_user(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    return row[0] if row else None


def get_user_profile(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, email, profile_image FROM users WHERE id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    return row


def update_profile_image(user_id, image_bytes):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET profile_image=? WHERE id=?",
        (image_bytes, user_id)
    )
    conn.commit()
    conn.close()

    
# ---------- EMAIL OTP AUTH ----------

# ================= CONFIG =================
EMAIL_SENDER = "youremail@gmail.com"   
EMAIL_PASSWORD = "Enter Your Password " 

# In-memory OTP store (same logic as before)
OTP_STORE = {}

# ================= OTP GENERATION =================
def generate_otp():
    return str(random.randint(100000, 999999))


# ================= SEND OTP EMAIL =================
def send_otp_email(receiver_email):
    otp = generate_otp()
    expiry = datetime.now() + timedelta(minutes=5)

    OTP_STORE[receiver_email] = {
        "otp": otp,
        "expiry": expiry
    }

    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = receiver_email
    msg["Subject"] = "CATMS Email Verification OTP"
    msg.set_content(
        f"""
Your OTP for CATMS registration is: {otp}

This OTP is valid for 5 minutes.
Do not share this OTP with anyone.

– CATMS Team
        """
    )

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

    return True


# ================= VERIFY OTP =================
def verify_otp(email, user_otp):
    if email not in OTP_STORE:
        return False, "OTP not requested"

    data = OTP_STORE[email]

    if datetime.now() > data["expiry"]:
        OTP_STORE.pop(email)
        return False, "OTP expired"

    if data["otp"] != user_otp:
        return False, "Invalid OTP"

    OTP_STORE.pop(email)
    return True, "OTP verified"


print("OTP functions loaded")