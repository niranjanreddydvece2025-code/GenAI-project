from datetime import date, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship

from app.core.db import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    grade = Column(String(40))
    location = Column(String(120))
    experience_years = Column(Float, default=0)
    skills = Column(ARRAY(String), default=list)
    certifications = Column(ARRAY(String), default=list)
    previous_projects = Column(JSONB, default=list)
    domain_experience = Column(ARRAY(String), default=list)
    current_allocation = Column(String(200), nullable=True)
    availability_date = Column(Date, default=date.today)
    resume_path = Column(String(400), nullable=True)
    resume_text = Column(Text, nullable=True)
    performance_rating = Column(Float, default=4.0)
    ai_summary = Column(Text, nullable=True)
    embedding_id = Column(Integer, nullable=True)  # position in FAISS index
    created_at = Column(DateTime, default=datetime.utcnow)

    allocations = relationship("Allocation", back_populates="employee")
    shortlists = relationship("Shortlist", back_populates="employee")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(200), nullable=False)
    required_skills = Column(ARRAY(String), default=list)
    location = Column(String(120))
    start_date = Column(Date, nullable=True)

    allocations = relationship("Allocation", back_populates="project")


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    allocation_status = Column(String(40), default="Bench")  # Bench | Allocated
    allocation_date = Column(Date, default=date.today)

    employee = relationship("Employee", back_populates="allocations")
    project = relationship("Project", back_populates="allocations")


class Shortlist(Base):
    __tablename__ = "shortlists"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    manager_email = Column(String(200))
    query_text = Column(Text, nullable=True)
    match_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="shortlists")
