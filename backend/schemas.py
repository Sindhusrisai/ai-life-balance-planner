from pydantic import BaseModel
from datetime import date

class TaskBase(BaseModel):
    name: str
    category: str
    duration: int
    energy_required: str
    priority: int
    deadline: date | None = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: str | None
    category: str | None
    duration: int | None
    energy_required: str | None
    priority: int | None
    deadline: date | None
    completed: bool | None

class TaskOut(TaskBase):
    id: int
    completed: bool

    class Config:
        from_attributes = True

class ScheduleRequest(BaseModel):
    slots: list[str]
    energy_level: str

class HealthIn(BaseModel):
    type: str
    value: str
