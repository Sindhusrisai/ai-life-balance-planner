# backend/schemas.py
from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    name: str
    category: Optional[str] = "study"
    duration: int
    energy_required: Optional[str] = "medium"
    priority: Optional[int] = 3
    deadline: Optional[str] = None

class TaskUpdate(BaseModel):
    name: Optional[str]
    category: Optional[str]
    duration: Optional[int]
    energy_required: Optional[str]
    priority: Optional[int]
    deadline: Optional[str]
    completed: Optional[bool]

class TaskOut(TaskCreate):
    id: int
    completed: bool
    created_at: Optional[str]

    class Config:
        orm_mode = True

class ScheduleRequest(BaseModel):
    energy_level: str
    slots: list[str]  # e.g. ["09:00-12:00","15:00-18:00"]

class HealthIn(BaseModel):
    type: str
    value: int
