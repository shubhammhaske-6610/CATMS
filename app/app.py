import sys, os
import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import streamlit.components.v1 as components 
import base64
import threading

def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode()


# ---------- PATH ----------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from src.task_reminder import run_scheduler 

# ---------- DATABASE PATH (FIX) ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "catms.db")


# ---------- INTERNAL IMPORTS ----------
from src.task_reminder import run_scheduler


from src.auth import (
    create_user_table,
    register_user,
    authenticate_user,
    get_user_profile,
    update_profile_image,
    send_otp_email,
    verify_otp
)

from src.task_storage import (
    create_table,
    add_task,
    get_tasks,
    mark_completed,
    delete_task,
    create_streak_table,
    update_streak,
    snooze_task,
            
)

# ---------- CONFIG ----------
st.set_page_config("CATMS", "🧠", layout="wide")
st.markdown("""
<style>
.profile-card {
    background: linear-gradient(135deg, #0a2540, #102a43);
    border-radius: 16px;
    padding: 16px;
    color: white;
    box-shadow: 0 6px 18px rgba(0,0,0,0.35);
    margin-bottom: 12px;
}
.profile-name {
    font-size: 16px;
    font-weight: 600;
}
.profile-email {
    font-size: 12px;
    opacity: 0.8;
}
.profile-badge {
    margin-top: 10px;
    background: rgba(255,255,255,0.12);
    padding: 6px;
    border-radius: 8px;
    font-size: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

create_user_table()
create_table()
create_streak_table()



# ---------- PDF EXPORT ----------
def generate_pdf(df, username):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, h - 40, "Cognitive Assistive Task Management System")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, h - 60, f"User: {username}")
    pdf.drawString(40, h - 75, f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}")

    y = h - 110
    pdf.setFont("Helvetica-Bold", 9)
    for i, col in enumerate(df.columns):
        pdf.drawString(40 + i * 70, y, col)

    y -= 15
    pdf.setFont("Helvetica", 9)
    for _, row in df.iterrows():
        for i, val in enumerate(row):
            pdf.drawString(40 + i * 70, y, str(val))
        y -= 14
        if y < 40:
            pdf.showPage()
            y = h - 50

    pdf.save()
    buffer.seek(0)
    return buffer

# ---------- LOGIN ----------
if "user_id" not in st.session_state:
    st.title("🧠 Cognitive Assistive Task Management System")

    t1, t2 = st.tabs(["Login", "Register"])

    with t1:
        u = st.text_input("Username or Email")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            uid = authenticate_user(u, p)

            if uid:
                st.session_state.user_id = uid
                st.session_state.username = u

                # ===== START TASK REMINDER THREAD (ADD THIS) =====
                if "reminder_started" not in st.session_state:
                    t = threading.Thread(
                        target=run_scheduler,
                        args=(st.session_state.user_id,),
                        daemon=True
                    )
                    t.start()
                    st.session_state.reminder_started = True
                # ===== END TASK REMINDER THREAD =====

                st.rerun()
            else:
                st.error("Invalid credentials")


    with t2:
        ru = st.text_input("Username", key="ru")
        re = st.text_input("Email", key="re")
        rp = st.text_input("Password", type="password", key="rp")
        if "otp_sent" not in st.session_state:
            st.session_state.otp_sent = False

        if not st.session_state.otp_sent:
            if st.button("Send OTP"):
                send_otp_email(re)
                st.session_state.otp_sent = True
                st.success("📧 OTP sent to your email")

        else:
            otp_input = st.text_input("Enter OTP")

            if st.button("Verify & Register"):
                ok, msg = verify_otp(re, otp_input)
                if ok:
                    if register_user(ru, re, rp):
                        st.success("✅ Registered successfully")
                        st.session_state.otp_sent = False
                    else:
                        st.error("Username already exists")
                else:
                    st.error(msg)

    st.stop()

# ---------- PROFILE ----------
user = get_user_profile(st.session_state.user_id)
_, username, email, profile_image = user

# Initialize session state for showing uploader
if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False

with st.sidebar:
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    st.markdown('<div class="profile-row">', unsafe_allow_html=True)

    # ---- Avatar with pencil icon ----
    if profile_image:
        img_base64 = image_to_base64(profile_image)
        img_src = f"data:image/png;base64,{img_base64}"
    else:
        img_src = "https://via.placeholder.com/96"

    # Pencil icon click toggles uploader visibility
    click_code = """
        <script>
        const checkbox = window.parent.document.getElementById('toggle_uploader_btn');
        checkbox.click();
        </script>
    """

    st.markdown(
        f"""
        <div style="position:relative; width:75px; height:75px;">
            <img src="{img_src}"
                 style="
                    width:75px;
                    height:75px;
                    border-radius:50%;
                    object-fit:cover;
                    border:2px solid rgba(255,255,255,0.7);
                 ">
            <button id="toggle_uploader_btn" style="
                position:absolute;
                bottom:-2px;
                right:-2px;
                width:22px;
                height:22px;
                border-radius:50%;
                background:#2563eb;
                color:white;
                font-size:12px;
                display:flex;
                align-items:center;
                justify-content:center;
                cursor:pointer;
                border:none;
            " onclick="document.dispatchEvent(new CustomEvent('toggleUploader'))">
                ✏️
            </button>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Listen for toggle event
    if st.button("Change Profile", key="toggle_uploader", help="Click pencil to change profile"):
        st.session_state.show_uploader = not st.session_state.show_uploader

    # ---- Lazy uploader ----
    if st.session_state.show_uploader:
        uploaded = st.file_uploader(
            "Select new profile image",
            type=["png", "jpg", "jpeg"],
            key="profileUpload"
        )
        if uploaded:
            update_profile_image(
                st.session_state.user_id,
                uploaded.read()
            )
            st.success("Profile updated")
            st.session_state.show_uploader = False  # hide uploader after update
            st.rerun()

    # ---- Username + email ----
    st.markdown(
        f"""
        <div>
            <div class="profile-name">{username}</div>
            <div class="profile-email">{email}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- GREETING CARD ----------
hour = datetime.now().hour

if hour < 12:
    greet = "Good Morning"
elif hour < 17:
    greet = "Good Afternoon"
else:
    greet = "Good Evening"

st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.35);
        color: white;
        margin-bottom: 20px;
    ">
        <div style="font-size:18px; font-weight:600;">
            👋 {greet}, {username}
        </div>
        <div style="font-size:13px; opacity:0.85; margin-top:4px;">
            Focus gently. One meaningful task at a time.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- STREAK ----------
conn = sqlite3.connect(DB_PATH)
row = conn.execute(
    "SELECT streak_count FROM streaks WHERE user_id=?",
    (st.session_state.user_id,),
).fetchone()
conn.close()

st.sidebar.markdown("---")
st.sidebar.subheader("🔥 Daily Streak")
st.sidebar.success(f"{row[0]} day streak" if row else "Start today 🚀")

# ---------- NAV ----------
st.sidebar.markdown("""
<style>
/* Make the selected radio button circle green */
div[role="radiogroup"] input[type="radio"] {
    accent-color: #22c55e; /* bright green */
}

/* Keep label text white and circle in front of text, add spacing */
div[role="radiogroup"] label {
    color: #f8fafc;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer; /* make label clickable */
    padding: 6px 12px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 8px; /* space between circle and text */
    background: linear-gradient(135deg, #1e293b, #0f172a); /* button color */
    transition: all 0.2s ease;
    margin-bottom: 6px; /* added spacing between buttons */
}

/* Optional hover effect */
div[role="radiogroup"] label:hover {
    background: linear-gradient(135deg, #2c3a4a, #16202a);
    transform: translateX(1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.sidebar.subheader("📌 Navigation")

page = st.sidebar.radio(
    "Navigation",  # non-empty label
    ["Tasks", "Add Task","History", "Analytics","Export CSV", "Logout"],
    key="nav",
    label_visibility="collapsed"  # hides the label in the sidebar
)

# ---------- DATA ----------
tasks = get_tasks(st.session_state.user_id)
df = pd.DataFrame(
    tasks,
    columns=[
        "ID", "Title", "Category", "Priority",
        "Due Date", "Start Time", "End Time",
        "Status", "Completed At"
    ]
)

# ---------- TASKS ----------
if page == "Tasks":
    st.header("🕒 Pending Tasks")

    now = datetime.now().time()
    pending = df[df["Status"] == "Pending"]

    # ----------- LAYOUT ----------
    left, right = st.columns([3, 1])

    # ================= LEFT : TASK LIST =================
    with left:
        if pending.empty:
            st.success("🎉 No pending tasks")
        else:
            for _, r in pending.iterrows():
                with st.container(border=True):
                    st.subheader(r["Title"])
                    st.write(f"📂 {r['Category']} | ⚡ {r['Priority']}")
                    st.write(f"📅 {r['Due Date']}")
                    st.write(f"⏰ {r['Start Time']} – {r['End Time']}")

                    # ----- TIME STATUS -----
                    try:
                        task_date = datetime.strptime(r["Due Date"], "%Y-%m-%d").date()

                        stt = datetime.strptime(r["Start Time"], "%I:%M %p").time()
                        ett = datetime.strptime(r["End Time"], "%I:%M %p").time()

                        now_dt = datetime.now()
                        start_dt = datetime.combine(task_date, stt)
                        end_dt = datetime.combine(task_date, ett)

                        if task_date < now_dt.date():
                            st.error("⚠ Task Delayed")

                        elif task_date == now_dt.date():
                            if now_dt < start_dt:
                                st.info("⏳ Upcoming")
                            elif start_dt <= now_dt <= end_dt:
                                st.success("🔥 Ongoing")
                            else:
                                st.error("⚠ Task Delayed")

                        else:
                            st.info("⏳ Upcoming")

                    except:
                        st.warning("Invalid time format")


                    c1, c2, c3 = st.columns(3)
                    if c1.button("✅ Complete", key=f"c{r['ID']}"):
                        mark_completed(r["ID"])
                        update_streak(st.session_state.user_id)
                        st.rerun()

                    if c2.button("🗑 Delete", key=f"d{r['ID']}"):
                        delete_task(r["ID"])
                        st.rerun()
                    
                    if c3.button("💤 Snooze 10m", key=f"s{r['ID']}"):
                        snooze_task(r["ID"])
                        st.success("⏰ Task snoozed by 10 minutes")
                        st.rerun()
                    
                  
        # ================= RIGHT : AI RECOMMENDATION =================
    with right:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #1f2937, #111827);
                border-radius: 14px;
                padding: 18px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.4);
            ">
                <h3 style="margin-top:0; color:#f9fafb;">🧠 Cognitive AI Assistant</h3>
                <p style="color:#d1d5db; font-size:14px;">
                    Gentle guidance for focus & memory
                </p>
                <hr style="border:0.5px solid #374151;">
            """,
            unsafe_allow_html=True
        )

        # ---- AI METRICS ----
        total_pending = len(pending)
        delayed = 0
        high_priority = 0

        for _, r in pending.iterrows():
            try:
                ett = datetime.strptime(r["End Time"], "%I:%M %p").time()
                if now > ett:
                    delayed += 1
            except:
                pass

            if r["Priority"] == "High":
                high_priority += 1

        st.markdown(
            f"""
            <p>📋 <b>Pending Tasks:</b> {total_pending}</p>
            <p>⚠ <b>Delayed:</b> {delayed}</p>
            <p>🔥 <b>High Priority:</b> {high_priority}</p>
            <hr style="border:0.5px solid #374151;">
            """,
            unsafe_allow_html=True
        )

        # ---- AI MESSAGE ----
        if total_pending == 0:
            msg = "🎉 You're all caught up! Take a break."
        elif delayed > 0:
            msg = "⚠ Focus on delayed tasks first. Try one task at a time."
        elif high_priority > 0:
            msg = "🔥 High-priority task detected. Start with that."
        else:
            msg = "✅ Maintain momentum. Short focused sessions help."

        st.markdown(
            f"""
            <div style="
                background:#111827;
                padding:12px;
                border-radius:10px;
                color:#e5e7eb;
                font-size:14px;
            ">
                {msg}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ---------- ADD TASK ----------
elif page == "Add Task":
    st.header("➕ Add Task")

    if "manual_task" not in st.session_state:
        st.session_state.manual_task = ""

    # ---------- STYLING ----------
    st.markdown(
        """
        <style>
        .input-label {
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 6px;
        }
        .stTextInput>div>div>input, 
        .stSelectbox>div>div>div>select, 
        .stDateInput>div>div>input {
            background-color: #0f172a;
            color: #f8fafc;
            border-radius: 8px;
            padding: 8px;
        }
        .time-window {
            background: #111827;
            padding: 14px;
            border-radius: 12px;
            margin-top: 10px;
        }
        .add-button {
            background-color: #2563eb;
            color: white;
            font-weight: 600;
            border-radius: 12px;
            padding: 10px 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---------- TASK INPUTS ----------
    c1, c2 = st.columns(2)
    with c1:
        pick = st.selectbox(
            "Select Task Title",
            ["", "Study", "Workout", "Medicine", "Meeting", "Project", "Personal"]
        )
    with c2:
        manual = st.text_input("Or enter manually", key="manual_task")

    # ✅ TITLE MUST BE DEFINED HERE
    title = manual.strip() if manual.strip() else pick.strip()

    category = st.selectbox("Category", ["Study", "Health", "Work", "Meals", "Personal", "Other"])
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    due_date = st.date_input("Due Date", min_value=date.today())


    # ---------- TIME WINDOW ----------
    with st.expander("⏰ Task Time Window", expanded=True):
        st.markdown('<div class="time-window">', unsafe_allow_html=True)
        sh, sm, sap = st.columns(3)
        eh, em, eap = st.columns(3)

        minutes = [f"{i:02d}" for i in range(60)]

        start_hour = sh.selectbox("Start Hour", list(range(1, 13)), key="sh")
        start_min = sm.selectbox("Start Minute", minutes, key="sm")
        start_ampm = sap.selectbox("AM/PM", ["AM", "PM"], key="sap")

        end_hour = eh.selectbox("End Hour", list(range(1, 13)), key="eh")
        end_min = em.selectbox("End Minute", minutes, key="em")
        end_ampm = eap.selectbox("AM/PM", ["AM", "PM"], key="eap")

        start_time = f"{start_hour}:{start_min} {start_ampm}"
        end_time = f"{end_hour}:{end_min} {end_ampm}"
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- ADD TASK BUTTON ----------
    if st.button("Add Task", key="add_task_btn"):
        if not title:
            st.error("Task title required")
            st.stop()

        # ---------- REAL-TIME VALIDATION ----------
        task_start_time = datetime.strptime(start_time, "%I:%M %p").time()
        task_end_time = datetime.strptime(end_time, "%I:%M %p").time()
        # round current time to minutes 
        now_dt = datetime.now().replace(second=0, microsecond=0)

        # basic sanity check
        if task_start_time >= task_end_time:
            st.error("⛔ Start time must be before end time")
            st.stop()

        # real-time check for today
        if due_date == date.today():
            if task_start_time < now_dt.time():
                st.error("⛔ Start time cannot be in the past")
                st.stop()

            if task_end_time <= now_dt.time():
                st.error("⛔ End time cannot be in the past")
                st.stop()

        add_task(
            st.session_state.user_id,
            title, category, priority,
            due_date.isoformat(),
            start_time, end_time
        )

        st.session_state.show_task_added = True
        st.session_state.pop("manual_task", None)
        st.rerun()


    # ---------- SUCCESS MESSAGE ----------
    if "show_task_added" in st.session_state and st.session_state.show_task_added:
        st.success("✅ Task added successfully!")
        st.session_state.show_task_added = False  # reset flag



# ---------- HISTORY ----------
elif page == "History":
    st.header("📜 Completed Tasks")

    completed = df[df["Status"] == "Completed"]

    if completed.empty:
        st.info("No completed tasks yet")
        st.stop()

    # ---------- STYLING ----------
    st.markdown(
        """
        <style>
        .history-table {
            border-collapse: collapse;
            width: 100%;
            font-family: 'Arial', sans-serif;
            color: #f8fafc;
        }
        .history-table th {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: #f9fafb;
            font-weight: 600;
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }
        .history-table td {
            padding: 10px;
            border-bottom: 1px solid #334155;
        }
        .history-table tr:hover {
            background: rgba(255, 255, 255, 0.05);
            transition: background 0.3s;
        }
        .history-card {
            background: linear-gradient(135deg, #1e293b, #111827);
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35);
            margin-bottom: 24px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---------- DISPLAY TABLE ----------
    st.markdown('<div class="history-card">', unsafe_allow_html=True)

    # Convert dataframe to HTML with custom class
    st.markdown(
        completed.drop(columns=["Completed At"]).to_html(
            index=False,
            classes="history-table",
            justify="left"
        ),
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- ANALYTICS ----------
elif page == "Analytics":
    st.header("📊 Analytics Dashboard")

    if df.empty:
        st.info("No data available for analytics")
        st.stop()

    # ---------- PREPROCESS ----------
    now = datetime.now()

    df["Delayed"] = False
    try:
        end_times = pd.to_datetime(
            df["Due Date"] + " " + df["End Time"],
            format="%Y-%m-%d %I:%M %p",
            errors="coerce"
        )
        df.loc[
            (df["Status"] == "Pending") & (end_times < now),
            "Delayed"
        ] = True
    except:
        pass

    total_tasks = len(df)
    completed_tasks = len(df[df["Status"] == "Completed"])
    pending_tasks = len(df[df["Status"] == "Pending"])
    delayed_tasks = len(df[df["Delayed"] == True])

    completion_rate = round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0

    # ---------- KPI CARDS ----------
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📝 Total Tasks", total_tasks)
    k2.metric("✅ Completed", completed_tasks)
    k3.metric("⏳ Pending", pending_tasks)
    k4.metric("⚠ Delayed", delayed_tasks)

    st.markdown("---")

    # ---------- DONUT + PRIORITY ----------
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📌 Task Status Distribution")
        status_counts = df["Status"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(
            status_counts,
            labels=status_counts.index,
            autopct="%1.1f%%",
            startangle=90
        )
        centre = plt.Circle((0, 0), 0.65, fc="white")
        fig1.gca().add_artist(centre)
        ax1.axis("equal")
        st.pyplot(fig1)

    with c2:
        st.subheader("⚡ Priority Distribution")
        priority_counts = df["Priority"].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.bar(priority_counts.index, priority_counts.values)
        ax2.set_ylabel("Task Count")
        st.pyplot(fig2)

    st.markdown("---")

    # ---------- TIME PRODUCTIVITY ----------
    st.subheader("⏰ Productivity by Time of Day")

    try:
        df["Start Hour"] = pd.to_datetime(
            df["Start Time"],
            format="%I:%M %p",
            errors="coerce"
        ).dt.hour

        time_productivity = (
            df[df["Status"] == "Completed"]
            .groupby("Start Hour")
            .size()
        )

        if not time_productivity.empty:
            st.line_chart(time_productivity)
        else:
            st.info("Not enough completed tasks for time analysis")
    except:
        st.warning("Time analysis not available")

    st.markdown("---")

    # ---------- CATEGORY PERFORMANCE ----------
    st.subheader("📂 Category Performance")

    category_stats = df.groupby("Category").agg(
        Total=("ID", "count"),
        Completed=("Status", lambda x: (x == "Completed").sum()),
        Delayed=("Delayed", "sum")
    )

    category_stats["Completion %"] = (
        category_stats["Completed"] / category_stats["Total"] * 100
    ).round(1)

    st.dataframe(category_stats, width="stretch")

    st.markdown("---")

    # ---------- SMART INSIGHTS ----------
    st.subheader("🧠 Smart Insights")

    insights = []

    if completion_rate >= 70:
        insights.append("🔥 Excellent productivity level")
    elif completion_rate >= 40:
        insights.append("⚡ Average productivity – consistency can improve")
    else:
        insights.append("🚨 Low productivity – reduce daily task load")

    if delayed_tasks > 0:
        insights.append("⏰ You often miss task deadlines")

    most_common_category = category_stats["Total"].idxmax()
    insights.append(f"📌 Most active category: {most_common_category}")

    if not time_productivity.empty:
        peak_hour = time_productivity.idxmax()
        insights.append(f"⏱ Most productive hour: {peak_hour}:00")

    for i in insights:
        st.markdown(f"- {i}")


# ---------- EXPORT ----------
elif page == "Export CSV":
    st.header("📤 Export Tasks")

    choice = st.radio("Select", ["All", "Pending", "Completed"])
    export_df = df if choice == "All" else df[df["Status"] == choice]

    st.dataframe(export_df, width="stretch")

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button("⬇ Download CSV", export_df.to_csv(index=False), f"tasks_{ts}.csv")
    st.download_button("📄 Download PDF", generate_pdf(export_df, username), f"tasks_{ts}.pdf")

# ---------- LOGOUT ----------
elif page == "Logout":
    st.session_state.clear()
    st.rerun()