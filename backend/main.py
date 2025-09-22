# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

# Load ENV (GEMINI_API_KEY etc.)
load_dotenv()

# local imports
from backend import models, schemas
from models import Task as TaskModel  # If running from backend folder, adjust import path; we rely on project root run
# To avoid confusion, import SessionLocal from backend.models:
from backend.models import SessionLocal, init_db

# Planner & advisor from project root (reuse your files)
from planner import generate_day_plan
from advisor import generate_advice

app = FastAPI(title="AI LifeBalance Backend")

# Allow calls from Streamlit (running on localhost:8501)
origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize DB
@app.on_event("startup")
def startup_event():
    init_db()

# CRUD endpoints
@app.post("/tasks", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskModel(
        name=task.name,
        category=task.category,
        duration=task.duration,
        energy_required=task.energy_required,
        priority=task.priority,
        deadline=task.deadline,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=list[schemas.TaskOut])
def read_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).filter(TaskModel.completed == False).all()

@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"status": "deleted"}

# Schedule endpoint: gathers pending tasks and returns plan + AI advice
@app.post("/schedule")
def make_schedule(req: schemas.ScheduleRequest, db: Session = Depends(get_db)):
    # fetch pending tasks
    rows = db.query(TaskModel).filter(TaskModel.completed == False).all()
    tasks = []
    for r in rows:
        tasks.append({
            "id": r.id,
            "name": r.name,
            "duration": r.duration,
            "energy_required": r.energy_required,
            "priority": r.priority,
            "deadline": r.deadline,
            "category": r.category
        })
    # transform slots format to list of tuples expected by planner (["09:00-12:00"] -> [("09:00","12:00")])
    slots = []
    for s in req.slots:
        try:
            start, end = s.split("-")
            slots.append((start.strip(), end.strip()))
        except:
            continue
    plan = generate_day_plan(tasks, slots, req.energy_level)
    user_profile = "Student, 4th year engineering"
    advice = generate_advice(user_profile, plan, req.energy_level)
    return {"plan": plan, "advice": advice}

# Health endpoint (simple store)
@app.post("/health")
def add_health_entry(h: schemas.HealthIn, db: Session = Depends(get_db)):
    from backend.models import Health
    entry = Health(type=h.type, value=h.value)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"status": "ok", "entry_id": entry.id}
