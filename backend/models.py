from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_lifebalance.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    energy_required = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    deadline = Column(Date, nullable=True)
    completed = Column(Boolean, default=False)

class Health(Base):
    __tablename__ = "health"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    value = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
