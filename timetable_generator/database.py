"""
database.py - SQLModel Schema for Timetable Generator
========================================================
Defines database models for Faculty, Course, Section, and Constraints
using SQLModel (SQLAlchemy + Pydantic hybrid).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import JSON, Column
import json


# ============================================================================
# MODELS
# ============================================================================

class Faculty(SQLModel, table=True):
    """
    Faculty Model
    - id: Unique faculty identifier
    - name: Faculty member's name
    - department: Department affiliation
    - specialization: Subject specialization
    - available_slots: JSON dict with {day: [period_list]}
      e.g., {"Monday": [1, 2, 3, 5, 6], "Tuesday": [1, 3, 4, 5]}
      Periods 3 and 6 are after breaks (global constraints).
    - is_external: True for Math/Placement (shared with other depts)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    department: str
    specialization: str
    available_slots: Dict[str, List[int]] = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )
    is_external: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Dr. S. Geeitha",
                "department": "IT",
                "specialization": "AI/ML",
                "available_slots": {
                    "Monday": [1, 2, 3, 5, 6, 7],
                    "Tuesday": [1, 2, 3, 5, 6, 7]
                },
                "is_external": False
            }
        }


class Course(SQLModel, table=True):
    """
    Course Model
    - id: Unique course identifier
    - code: Course code (e.g., "IT302")
    - name: Course name
    - course_type: "THEORY" or "LAB"
    - credits: Credit hours
    - weekly_hours: Hours per week
    - required_faculty_ids: List of faculty IDs required for this course
      For LABs: Must be 2 faculty members (multi-faculty constraint)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    name: str
    course_type: str = Field(default="THEORY")  # "THEORY" or "LAB"
    credits: int
    weekly_hours: int
    required_faculty_ids: List[int] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "code": "IT301",
                "name": "Machine Learning",
                "course_type": "LAB",
                "credits": 4,
                "weekly_hours": 2,
                "required_faculty_ids": [1, 2]  # Dr. Geeitha + Ms. Anitha
            }
        }


class Section(SQLModel, table=True):
    """
    Section Model - Represents a class section
    - id: Section identifier
    - name: Section name (e.g., "II Year IT A")
    - year: Academic year
    - division: "A" or "B"
    - department: Department code
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    year: int
    division: str
    department: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "II Year IT A",
                "year": 2,
                "division": "A",
                "department": "IT"
            }
        }


class Constraint(SQLModel, table=True):
    """
    Constraint Model - Defines scheduling constraints
    - id: Constraint identifier
    - course_id: Associated course
    - section_id: Associated section
    - block_size: Consecutive periods required (1 for theory, 2+ for labs)
    - preferred_days: Optional preferred days for scheduling
    - is_hard: True if must be satisfied, False if soft constraint
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id")
    section_id: int = Field(foreign_key="section.id")
    block_size: int = Field(default=1)  # 1 for THEORY, 2+ for LAB
    preferred_days: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )
    is_hard: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "course_id": 1,
                "section_id": 1,
                "block_size": 2,
                "preferred_days": ["Monday", "Wednesday"],
                "is_hard": True
            }
        }


class TimetableEntry(SQLModel, table=True):
    """
    TimetableEntry Model - Single scheduled slot
    - id: Entry identifier
    - section_id: Section for which this is scheduled
    - course_id: Course being taught
    - day: Day of week
    - period: Period number (1-7)
    - faculty_id: Primary faculty member
    - secondary_faculty_id: For labs, secondary faculty member
    - room_number: Room/Lab location
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    section_id: int = Field(foreign_key="section.id")
    course_id: int = Field(foreign_key="course.id")
    day: str
    period: int
    faculty_id: int = Field(foreign_key="faculty.id")
    secondary_faculty_id: Optional[int] = Field(default=None, foreign_key="faculty.id")
    room_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = "sqlite:///timetable.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL logging
)


def create_db_and_tables():
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for getting database session in FastAPI."""
    with Session(engine) as session:
        yield session


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_sample_data():
    """
    Initialize database with sample data for testing.
    Call this once during development/testing.
    """
    create_db_and_tables()
    
    with Session(engine) as session:
        # Create Faculty
        faculty_data = [
            Faculty(
                name="Dr. S. Geeitha",
                department="IT",
                specialization="AI/ML",
                available_slots={
                    "Monday": [1, 2, 3, 5, 6, 7],
                    "Tuesday": [1, 2, 3, 5, 6, 7],
                    "Wednesday": [1, 2, 3, 5, 6, 7],
                    "Thursday": [1, 2, 3, 5, 6, 7],
                    "Friday": [1, 2, 3, 5, 6, 7],
                },
                is_external=False
            ),
            Faculty(
                name="Ms. K. Anitha",
                department="IT",
                specialization="OS/Systems",
                available_slots={
                    "Monday": [1, 2, 3, 5, 6, 7],
                    "Tuesday": [1, 2, 3, 5, 6, 7],
                    "Wednesday": [1, 2, 5, 6, 7],
                    "Thursday": [1, 2, 3, 5, 6, 7],
                    "Friday": [1, 2, 3, 5, 6, 7],
                },
                is_external=False
            ),
            Faculty(
                name="Dr. Mathematics",
                department="MATH",
                specialization="Mathematics",
                available_slots={
                    "Monday": [1, 2, 5, 6],
                    "Tuesday": [1, 2, 5, 6],
                    "Wednesday": [1, 2, 5, 6],
                    "Thursday": [1, 2, 5, 6],
                    "Friday": [1, 2, 5, 6],
                },
                is_external=True
            ),
        ]
        
        for faculty in faculty_data:
            session.add(faculty)
        session.commit()
        
        # Create Sections
        sections = [
            Section(name="II Year IT A", year=2, division="A", department="IT"),
            Section(name="II Year IT B", year=2, division="B", department="IT"),
        ]
        
        for section in sections:
            session.add(section)
        session.commit()
        
        # Create Courses
        courses = [
            Course(
                code="IT301",
                name="Machine Learning Lab",
                course_type="LAB",
                credits=4,
                weekly_hours=2,
                required_faculty_ids=[1, 2]  # Dr. Geeitha + Ms. Anitha
            ),
            Course(
                code="IT302",
                name="Operating Systems",
                course_type="THEORY",
                credits=3,
                weekly_hours=3,
                required_faculty_ids=[2]  # Ms. Anitha
            ),
            Course(
                code="IT303",
                name="Mathematics",
                course_type="THEORY",
                credits=3,
                weekly_hours=3,
                required_faculty_ids=[3]  # Dr. Mathematics (external)
            ),
        ]
        
        for course in courses:
            session.add(course)
        session.commit()
        
        # Create Constraints
        constraints = [
            Constraint(
                course_id=1,  # ML Lab
                section_id=1,  # IT A
                block_size=2,
                preferred_days=["Monday", "Wednesday"],
                is_hard=True
            ),
            Constraint(
                course_id=2,  # OS Theory
                section_id=1,  # IT A
                block_size=1,
                preferred_days=["Tuesday", "Thursday"],
                is_hard=True
            ),
            Constraint(
                course_id=3,  # Math
                section_id=1,  # IT A
                block_size=1,
                preferred_days=["Friday"],
                is_hard=True
            ),
        ]
        
        for constraint in constraints:
            session.add(constraint)
        session.commit()
        
        print("✓ Sample data initialized successfully!")


if __name__ == "__main__":
    init_sample_data()
