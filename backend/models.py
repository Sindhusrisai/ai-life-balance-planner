# backend/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite DB stored at project root
DATABASE_URL = "sqlite:///./lifebalance.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, default="study")
    duration = Column(Integer, default=60)    # minutes
    energy_required = Column(String, default="medium")
    priority = Column(Integer, default=3)
    deadline = Column(String, nullable=True)  # ISO date string
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Health(Base):
    __tablename__ = "health"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)     # sleep, water, exercise
    value = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
