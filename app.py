import streamlit as st
from pathlib import Path
import base64
import requests
import pandas as pd
import altair as alt
from datetime import date, datetime, timedelta
import random

# -------------------
# CONFIG
# -------------------
BACKEND_URL = "https://ai-life-balance-planner.onrender.com"

ASSETS_DIR = Path("assets")

st.set_page_config(page_title="AI LifeBalance", page_icon="🌿", layout="wide")

# -------------------
# Helpers
# -------------------
def asset_path(name: str) -> Path:
    return ASSETS_DIR / name

def exists(name: str) -> bool:
    return asset_path(name).exists()

def embed_image_base64(path: Path) -> str:
    try:
        b = path.read_bytes()
        ext = path.suffix.lower().lstrip(".")
        mime = f"image/{'png' if ext=='png' else ext}"
        encoded = base64.b64encode(b).decode()
        return f"data:{mime};base64,{encoded}"
    except Exception:
        return ""

# -------------------
# CSS Styling
# -------------------
def load_css(dark=False):
    bg_css = ""
    if exists("bg_pattern.png"):
        bg_data = embed_image_base64(asset_path("bg_pattern.png"))
        if bg_data:
            bg_css = f"background-image: url('{bg_data}'); background-size: cover; background-attachment: fixed;"
    primary_color = "#2E7D32" if not dark else "#81C784"
    text_color = "#000" if not dark else "#fff"
    bg_color = "rgba(255,255,255,0.96)" if not dark else "rgba(30,30,30,0.9)"
    st.markdown(f"""
    <style>
    .stApp {{
        {bg_css};
        color:{text_color};
    }}
    main .block-container {{
        max-width: 1100px;
        margin: 1.2rem auto;
        padding-left: 1.6rem;
        padding-right: 1.6rem;
    }}
    .content-card {{
        background: {bg_color};
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0 12px 30px rgba(14,30,37,0.08);
        border: 1px solid rgba(30,60,80,0.05);
        margin-bottom: 18px;
    }}
    .big-title {{
        font-size:28px !important;
        font-weight:700;
        color:{primary_color};
        margin-bottom: 15px;
        text-align:center;
    }}
    .page-quote {{
        font-size:18px;
        font-style:italic;
        color:#444;
        text-align:center;
        margin-bottom:20px;
    }}
    .task-card {{
        background: {bg_color};
        padding: 14px;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(16,24,40,0.06);
        margin-bottom: 12px;
        border-left: 6px solid {primary_color};
        transition: all 0.3s;
    }}
    .task-card:hover {{
        transform: scale(1.02);
        box-shadow: 0 8px 22px rgba(16,24,40,0.1);
    }}
    .plan-card {{
        background: {bg_color};
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(16,24,40,0.04);
        margin-bottom: 10px;
    }}
    .label {{ font-size:13px; color:#5c6b73; }}
    div.stButton > button:first-child {{
        background-color: {primary_color};
        color: #fff;
        border-radius: 8px;
        height: 2.6em;
        font-weight: 600;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #346e2e;
    }}
    </style>
    """, unsafe_allow_html=True)

# -------------------
# Session State Defaults
# -------------------
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = []
if 'generated_advice' not in st.session_state:
    st.session_state.generated_advice = ""
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'username' not in st.session_state:
    st.session_state.username = "Guest"

load_css(st.session_state.dark_mode)
# -------------------
# Login Page (Name + Email + Password)
# -------------------
import re
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# Read stored credentials from .env
VALID_EMAIL = os.getenv("SENDER_EMAIL", "").strip().strip('"')
VALID_PASSWORD = os.getenv("SENDER_PASSWORD", "").strip().strip('"')

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# Show login page only if not logged in
if not st.session_state.logged_in:
    st.title("🔐 Login to AI LifeBalance")
    st.write("Please enter your details to continue")

    with st.form("login_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            # ✅ Name validation: allow letters, numbers, spaces, underscores; must start with a letter
            name_pattern = r'^[A-Za-z][A-Za-z0-9_ ]{2,}$'
            if not re.match(name_pattern, name):
                st.error("❌ Invalid name. Start with a letter, only letters/numbers/spaces/underscores allowed, min 3 characters.")
            elif not email.strip() or not password.strip():
                st.error("❌ Email and password cannot be empty.")
            elif email.strip() != VALID_EMAIL or password.strip() != VALID_PASSWORD:
                st.error("❌ Invalid credentials. Please check your email or password.")
            else:
                # ✅ Successful login
                st.session_state.user_name = name.strip()
                st.session_state.user_email = email.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()


# -------------------
# Sidebar
# -------------------
icons = {
    "Home": "home_icon.png",
    "Add Task": "add_task_icon.png",
    "View Tasks": "view_tasks_icon.png",
    "Generate Plan": "plan_icon.png",
    "Analytics": "analytics_icon.png"
}

st.sidebar.markdown("## ⚡ AI LifeBalance")
st.sidebar.markdown("---")

# 👤 Display logged-in user name instead of login box
st.sidebar.markdown(f"### 👤 Logged in as: **{st.session_state.user_name}**")


# Theme toggle
if st.sidebar.checkbox("Dark Mode", value=st.session_state.dark_mode):
    st.session_state.dark_mode = True
else:
    st.session_state.dark_mode = False
load_css(st.session_state.dark_mode)

for key, icon_file in icons.items():
    col1, col2 = st.sidebar.columns([1, 5])
    with col1:
        if exists(icon_file):
            st.image(asset_path(icon_file), width=24)
    with col2:
        if st.sidebar.button(key):
            st.session_state.page = key

st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ • Keep slots in HH:MM-HH:MM format")

page = st.session_state.page

# -------------------
# Backend Helpers
# -------------------
def fetch_tasks():
    try:
        r = requests.get(f"{BACKEND_URL}/tasks", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"❌ Could not fetch tasks from backend: {e}")
        return []

def post_task(payload):
    try:
        r = requests.post(f"{BACKEND_URL}/tasks", json=payload, timeout=5)
        r.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)

def put_task_done(task_id, completed=True):
    try:
        payload = {"completed": completed}
        r = requests.put(f"{BACKEND_URL}/tasks/{task_id}", json=payload, timeout=5)
        r.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)

def delete_task(task_id):
    try:
        r = requests.delete(f"{BACKEND_URL}/tasks/{task_id}", timeout=5)
        r.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)

def call_schedule(slots, energy):
    try:
        payload = {"slots": slots, "energy_level": energy}
        r = requests.post(f"{BACKEND_URL}/schedule", json=payload, timeout=15)
        
        # Handle validation error from backend
        if r.status_code == 400:
            try:
                detail = r.json().get("detail", "Invalid input")
            except Exception:
                detail = "Invalid input"
            return {"error": detail}
        
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Could not reach backend: {e}"}
    except Exception as e:
        return {"error": str(e)}


# -------------------
# UI Components
# -------------------
CATEGORY_COLORS = {
    "study": "#42a5f5",
    "work": "#66bb6a",
    "personal": "#ec407a",
    "health": "#ef5350",
    "wellbeing": "#ab47bc"
}

def task_card(task):
    color = CATEGORY_COLORS.get(task['category'], "#888")
    st.markdown(f"""
    <div class="task-card" style="border-left: 6px solid {color};">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-weight:700; font-size:16px;">{task['name']}</div>
          <div class="label">{task['category']} • {task['duration']} min • Priority {task['priority']}</div>
          <div class="label">Deadline: {task.get('deadline') or '—'}</div>
        </div>
        <div style="text-align:right;">
          <div class="label">Energy: {task.get('energy_required','')}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def plan_card(item):
    color = CATEGORY_COLORS.get(item.get('category',''), "#888")
    st.markdown(f"""
    <div class="plan-card" style="border-left: 6px solid {color};">
      <div style="font-weight:700;">{item['task']}</div>
      <div class="label">Slot: {item['slot']} • Category: {item.get('category','')}</div>
    </div>
    """, unsafe_allow_html=True)

def show_category_chart(tasks):
    if not tasks:
        return
    df = pd.DataFrame(tasks)
    if df.empty or 'category' not in df:
        return
    agg = df.groupby('category').size().reset_index(name='count')
    chart = alt.Chart(agg).mark_bar().encode(
        x='category',
        y='count',
        tooltip=['category','count']
    ).properties(height=250, width=500)
    st.altair_chart(chart, use_container_width=True)

def show_completion_chart(tasks):
    if not tasks:
        return
    df = pd.DataFrame(tasks)
    if df.empty:
        return
    df['completed'] = df.get('completed', False)
    done = df['completed'].sum()
    total = len(df)
    st.progress(done/total if total else 0)

# -------------------
# Dynamic Quotes / Banners
# -------------------
BANNERS = [
    "🌱 Balance your tasks, balance your life.",
    "💡 Stay consistent, stay productive.",
    "⚡ Prioritize what matters today.",
    "✨ Small steps every day lead to big results."
]

def random_banner():
    return random.choice(BANNERS)

# -------------------
# Pages
# -------------------
if page == "Home":
    # Display username
    user_name = st.session_state.get('user_name', 'Guest')
    st.markdown(f"<div class='big-title'>🌿 Welcome back,  <b>{user_name}</b>!!</div>", unsafe_allow_html=True)


    # Banner
    if exists("banner.png"):
        st.image(str(asset_path("banner.png")), use_container_width=True)

    # Random motivational quote
    st.markdown(f"<div class='page-quote'>{random_banner()}</div>", unsafe_allow_html=True)

    # Dashboard Stats
    tasks = fetch_tasks()
    pending = sum(1 for t in tasks if not t.get('completed'))
    completed = sum(1 for t in tasks if t.get('completed'))
    today_deadline = sum(1 for t in tasks if t.get('deadline') == str(date.today()))
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pending Tasks", pending)
    col2.metric("Completed Tasks", completed)
    col3.metric("Deadlines Today", today_deadline)
    col4.metric("Productivity Streak", st.session_state.streak)

    # Completion progress bar
    show_completion_chart(tasks)

    # Tip of the day
    tips = [
        "Break work into 25-min sessions!",
        "Focus on high-priority tasks first.",
        "Take short breaks every hour.",
        "Plan your day the night before."
    ]
    st.markdown(f"<div class='content-card'><strong>Tip of the Day:</strong> {random.choice(tips)}</div>", unsafe_allow_html=True)

elif page == "Add Task":
    st.markdown("<div class='big-title'>➕ Add Task</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-quote'>{random_banner()}</div>", unsafe_allow_html=True)
    with st.form("add_task_form"):
        name = st.text_input("Task name")
        category = st.selectbox("Category", ["study", "work", "personal", "health", "wellbeing"])
        duration = st.number_input("Duration (minutes)", min_value=1, value=60)
        energy_required = st.selectbox("Energy required", ["high", "medium", "low"])
        priority = st.slider("Priority (1 low - 5 high)", 1, 5, 4)
        deadline = st.date_input("Deadline", value=date.today())
        submitted = st.form_submit_button("Add Task")
        if submitted:
            if not name.strip():
                st.warning("Please enter a task name")
            else:
                payload = {
                    "name": name.strip(),
                    "category": category,
                    "duration": int(duration),
                    "energy_required": energy_required,
                    "priority": int(priority),
                    "deadline": str(deadline)
                }
                ok, err = post_task(payload)
                if ok:
                    st.success("Task added ✅")
                    st.session_state.streak += 1
                else:
                    st.error(f"Could not add task: {err}")

elif page == "View Tasks":
    st.markdown("<div class='big-title'>📝 Tasks</div>", unsafe_allow_html=True)
    tasks = fetch_tasks()
    if not tasks:
        st.info("No tasks found")
    else:
        for t in tasks:
            # Determine style for completed tasks
            name_style = f"<s>{t['name']}</s>" if t.get('completed') else t['name']
            category_style = f"<s>{t['category']} • {t['duration']} min • Priority {t['priority']}</s>" if t.get('completed') else f"{t['category']} • {t['duration']} min • Priority {t['priority']}"
            deadline_style = f"<s>{t.get('deadline') or '—'}</s>" if t.get('completed') else t.get('deadline') or '—'
            energy_style = f"<s>{t.get('energy_required','')}</s>" if t.get('completed') else t.get('energy_required','')

            # Category color
            color = CATEGORY_COLORS.get(t['category'], "#2E7D32")  # fallback green

            # Render card with category color
            st.markdown(f"""
            <div class="task-card" style="border-left: 6px solid {color};">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div style="font-weight:700; font-size:16px;">{name_style}</div>
                  <div class="label">{category_style}</div>
                  <div class="label">Deadline: {deadline_style}</div>
                </div>
                <div style="text-align:right;">
                  <div class="label">Energy: {energy_style}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Action buttons
            c1, c2 = st.columns([1,1])
            with c1:
                if not t.get('completed'):  # Only show mark done if not already completed
                    if st.button(f"Mark done ✓", key=f"done-{t['id']}"):
                        payload = {
                            "name": t['name'],
                            "category": t['category'],
                            "duration": t['duration'],
                            "priority": t['priority'],
                            "energy_required": t.get('energy_required','medium'),
                            "deadline": t.get('deadline', str(date.today())),
                            "completed": True
                        }
                        try:
                            r = requests.put(f"{BACKEND_URL}/tasks/{t['id']}", json=payload, timeout=5)
                            r.raise_for_status()
                            st.success(f"Task '{t['name']}' marked done ✅")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Could not mark done: {e}")
            with c2:
                if st.button(f"Delete ❌", key=f"del-{t['id']}"):
                    ok, err = delete_task(t['id'])
                    if ok: st.experimental_rerun()
                    else: st.error(err)



elif page == "Generate Plan":
    st.markdown("<div class='big-title'>🗓️ Generate Plan</div>", unsafe_allow_html=True)
    with st.form("generate_plan_form"):
        slots = st.text_area(
            "Enter your available time slots (HH:MM-HH:MM, one per line)", 
            placeholder="09:00-10:30\n11:00-12:00"
        )
        energy = st.selectbox("Your current energy level", ["high", "medium", "low"])
        submitted = st.form_submit_button("Generate Schedule")
    if submitted:
        result = call_schedule(slots.splitlines(), energy)
        if "error" in result:
            st.error(result["error"])
        else:
            st.session_state.generated_advice = result.get("advice", "")
            st.session_state.generated_plan = result.get("plan", [])
    if st.session_state.generated_advice:
        st.markdown(
            f"<div class='content-card'><strong>Coach Advice:</strong><br>{st.session_state.generated_advice}</div>", 
            unsafe_allow_html=True
        )
    for item in st.session_state.generated_plan:
        plan_card(item)
        # -------------------
    # Email the Generated Schedule
    # -------------------
    if st.session_state.generated_plan and st.session_state.user_email:
        import textwrap
        from backend.email_utils import send_email_notification
  # if email_utils.py is outside backend

        # Format the plan nicely for email body
        schedule_lines = []
        for item in st.session_state.generated_plan:
            line = f"{item['slot']} - {item['task']} ({item.get('category','')})"
            schedule_lines.append(line)
        schedule_text = "\n".join(schedule_lines)

        if st.button("📧 Send Schedule to My Email"):
            try:
                send_email_notification(
                    receiver_email=st.session_state.user_email,
                    subject="Your AI LifeBalance Schedule",
                    body=schedule_text
                )
                st.success(f"✅ Schedule sent to {st.session_state.user_email}")
            except Exception as e:
                st.error(f"Failed to send email: {e}")

elif page == "Analytics":
    st.markdown("<div class='big-title'>📊 Analytics</div>", unsafe_allow_html=True)
    tasks = fetch_tasks()
    show_category_chart(tasks)
    show_completion_chart(tasks)
