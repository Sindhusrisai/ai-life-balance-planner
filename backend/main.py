from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.models import Task as TaskModel, SessionLocal, init_db
from planner import generate_day_plan
from advisor import generate_advice  # placeholder advice
from datetime import datetime
from backend.email_utils import send_email_notification
 # ✅ import the helper

app = FastAPI(title="AI LifeBalance Backend")
app = FastAPI()

@app.get("/send-test-email")
def send_test_email():
    send_email_notification(
        receiver_email="receiver@gmail.com",
        subject="Test Email",
        body="This is a test email from FastAPI!"
    )
    return {"message": "Email sent successfully!"}
# -------------------
# CORS
# -------------------
origins = ["http://localhost:8501", "http://127.0.0.1:8501"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# DB Dependency
# -------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------
# Initialize DB
# -------------------
@app.on_event("startup")
def startup_event():
    init_db()

# -------------------
# Root
# -------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to AI LifeBalance API"}

# -------------------
# CRUD endpoints for tasks
# -------------------
@app.post("/tasks", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskModel(
        name=task.name,
        category=task.category,
        duration=task.duration,
        energy_required=task.energy_required.lower(),
        priority=task.priority,
        deadline=task.deadline,
        completed=False
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # ✅ Optional: send email notification
    try:
        send_email(
            subject="🎯 New Task Added to AI LifeBalance",
            body=f"Task '{task.name}' has been successfully added to your planner.",
            to_email="your_email@gmail.com"   # or dynamic user email later
        )
    except Exception as e:
        print(f"Email sending failed: {e}")

    return db_task


@app.get("/tasks", response_model=list[schemas.TaskOut])
def read_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()

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

# -------------------
# Schedule endpoint
# -------------------
@app.post("/schedule")
def make_schedule(req: schemas.ScheduleRequest, db: Session = Depends(get_db)):
    rows = db.query(TaskModel).filter(TaskModel.completed == False).all()
    if not rows:
        return {"plan": [], "advice": "No tasks found"}

    # ✅ Collect tasks
    tasks = []
    for r in rows:
        tasks.append({
            "id": r.id,
            "name": r.name,
            "duration": r.duration,
            "energy_required": r.energy_required.lower(),
            "priority": r.priority,
            "deadline": str(r.deadline),
            "category": r.category
        })

    # ✅ Validate time slots
    slots = []
    invalid_slots = []

    for s in req.slots:
        try:
            start, end = s.split("-")
            start = start.strip()
            end = end.strip()

            # Check HH:MM format
            datetime.strptime(start, "%H:%M")
            datetime.strptime(end, "%H:%M")

            slots.append((start, end))
        except Exception:
            invalid_slots.append(s)

    # ❌ If any invalid slots exist → return 400 with proper error message
    if invalid_slots:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid time format in slots: {', '.join(invalid_slots)}. Please use HH:MM-HH:MM format."
        )

    # ✅ Generate plan
    plan = generate_day_plan(tasks, slots, req.energy_level)
    advice = "Focus on high-priority tasks first!" if req.energy_level == "high" else "Focus on small, easy tasks and recharge your energy."

    return {"plan": plan, "advice": advice}
