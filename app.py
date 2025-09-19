# app.py
import streamlit as st
from datetime import date
from planner import generate_day_plan
from advisor import generate_advice

st.set_page_config(page_title="AI LifeBalance", layout="wide")
st.title("🌿 AI LifeBalance — Planner for Study, Work & Well-being")

# Session-state for tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.sidebar.header("➕ Add a Task")
name = st.sidebar.text_input("Task name")
category = st.sidebar.selectbox("Category", ["study","work","chore","health"])
duration = st.sidebar.number_input("Duration (minutes)", min_value=5, max_value=480, value=60, step=5)
energy_req = st.sidebar.selectbox("Energy required", ["high","medium","low"])
priority = st.sidebar.slider("Priority (1 low - 5 high)", 1, 5, 3)
deadline = st.sidebar.date_input("Deadline (optional)", value=date.today())

if st.sidebar.button("Add Task"):
    st.session_state.tasks.append({
        "name": name,
        "category": category,
        "duration": int(duration),
        "energy_required": energy_req,
        "priority": int(priority),
        "deadline": deadline.isoformat()
    })
    st.sidebar.success("Task added!")

st.header("📝 Current Tasks")
if st.session_state.tasks:
    for i, t in enumerate(st.session_state.tasks):
        st.write(f"**{i+1}. {t['name']}** — {t['category']} — {t['duration']} min — energy: {t['energy_required']} — priority: {t['priority']} — due: {t['deadline']}")
else:
    st.info("Add tasks from the sidebar.")

st.markdown("---")
st.header("⚡ Today's Inputs / Generate Plan")
energy_level = st.radio("How energetic are you today?", ["high","medium","low"], index=1)
slots_text = st.text_area("Availability slots (one per line, format HH:MM-HH:MM)", value="09:00-12:00\n15:00-18:00")
slots = []
for line in slots_text.splitlines():
    if "-" in line:
        s,e = line.strip().split("-")
        slots.append((s.strip(), e.strip()))

if st.button("Generate Today's Plan"):
    if not st.session_state.tasks:
        st.warning("Please add at least one task.")
    else:
        plan = generate_day_plan(st.session_state.tasks, slots, energy_level)
        st.subheader("📅 Generated Plan")
        st.table(plan)
        # AI advice
        user_profile = "4th year engineering student, busy schedule"
        advice = generate_advice(user_profile, plan, energy_level)
        st.subheader("🤖 AI Advisor")
        st.write(advice)

st.markdown("---")
st.header("⚙️ Controls")
if st.button("Clear all tasks"):
    st.session_state.tasks = []
    st.success("Tasks cleared.")
