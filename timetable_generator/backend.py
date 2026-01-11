"""
backend.py - FastAPI Backend for Timetable Generator
====================================================
Provides REST API endpoints for timetable generation and data management.
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
import json
from typing import List, Dict, Any, Optional
import pandas as pd

from database import (
    create_db_and_tables, get_session, engine,
    Faculty, Course, Section, Constraint, TimetableEntry, init_sample_data
)
from algorithm import generate_timetable, DAYS, SCHEDULABLE_PERIODS


# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Timetable Generator API",
    description="REST API for MKCE IT Department Timetable Generation",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    """Initialize database tables on app startup."""
    create_db_and_tables()
    # Uncomment to initialize with sample data on first run
    # init_sample_data()


# ============================================================================
# FACULTY ENDPOINTS
# ============================================================================

@app.post("/api/faculty", response_model=dict)
def create_faculty(
    faculty: Faculty,
    session: Session = Depends(get_session)
) -> dict:
    """Create a new faculty member."""
    try:
        session.add(faculty)
        session.commit()
        session.refresh(faculty)
        return {"status": "success", "id": faculty.id, "data": faculty}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/faculty", response_model=dict)
def list_faculty(session: Session = Depends(get_session)) -> dict:
    """Get all faculty members."""
    faculty_list = session.exec(select(Faculty)).all()
    return {
        "status": "success",
        "count": len(faculty_list),
        "data": faculty_list
    }


@app.get("/api/faculty/{faculty_id}", response_model=dict)
def get_faculty(faculty_id: int, session: Session = Depends(get_session)) -> dict:
    """Get a specific faculty member."""
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return {"status": "success", "data": faculty}


@app.put("/api/faculty/{faculty_id}", response_model=dict)
def update_faculty(
    faculty_id: int,
    faculty_update: Faculty,
    session: Session = Depends(get_session)
) -> dict:
    """Update faculty member details."""
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Update fields
    faculty_data = faculty_update.dict(exclude_unset=True)
    for key, value in faculty_data.items():
        setattr(faculty, key, value)
    
    session.add(faculty)
    session.commit()
    session.refresh(faculty)
    return {"status": "success", "data": faculty}


@app.delete("/api/faculty/{faculty_id}", response_model=dict)
def delete_faculty(faculty_id: int, session: Session = Depends(get_session)) -> dict:
    """Delete a faculty member."""
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    session.delete(faculty)
    session.commit()
    return {"status": "success", "message": "Faculty deleted"}


# ============================================================================
# COURSE ENDPOINTS
# ============================================================================

@app.post("/api/course", response_model=dict)
def create_course(
    course: Course,
    session: Session = Depends(get_session)
) -> dict:
    """Create a new course."""
    try:
        session.add(course)
        session.commit()
        session.refresh(course)
        return {"status": "success", "id": course.id, "data": course}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/course", response_model=dict)
def list_courses(session: Session = Depends(get_session)) -> dict:
    """Get all courses."""
    courses = session.exec(select(Course)).all()
    return {
        "status": "success",
        "count": len(courses),
        "data": courses
    }


@app.get("/api/course/{course_id}", response_model=dict)
def get_course(course_id: int, session: Session = Depends(get_session)) -> dict:
    """Get a specific course."""
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"status": "success", "data": course}


# ============================================================================
# SECTION ENDPOINTS
# ============================================================================

@app.post("/api/section", response_model=dict)
def create_section(
    section: Section,
    session: Session = Depends(get_session)
) -> dict:
    """Create a new section."""
    try:
        session.add(section)
        session.commit()
        session.refresh(section)
        return {"status": "success", "id": section.id, "data": section}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/section", response_model=dict)
def list_sections(session: Session = Depends(get_session)) -> dict:
    """Get all sections."""
    sections = session.exec(select(Section)).all()
    return {
        "status": "success",
        "count": len(sections),
        "data": sections
    }


# ============================================================================
# CONSTRAINT ENDPOINTS
# ============================================================================

@app.post("/api/constraint", response_model=dict)
def create_constraint(
    constraint: Constraint,
    session: Session = Depends(get_session)
) -> dict:
    """Create a new constraint."""
    try:
        session.add(constraint)
        session.commit()
        session.refresh(constraint)
        return {"status": "success", "id": constraint.id, "data": constraint}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/constraint", response_model=dict)
def list_constraints(session: Session = Depends(get_session)) -> dict:
    """Get all constraints."""
    constraints = session.exec(select(Constraint)).all()
    return {
        "status": "success",
        "count": len(constraints),
        "data": constraints
    }


# ============================================================================
# TIMETABLE GENERATION ENDPOINT
# ============================================================================

@app.post("/api/generate-timetable", response_model=dict)
def generate_timetable_endpoint(
    section_id: int,
    session: Session = Depends(get_session)
) -> dict:
    """
    Generate timetable for a specific section.
    
    Args:
        section_id: Section to generate timetable for
    
    Returns:
        JSON with generated timetable
    """
    try:
        # Fetch section
        section = session.get(Section, section_id)
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        
        # Prepare faculty data
        faculty_list = session.exec(select(Faculty)).all()
        faculty_data = {
            f.id: {
                "name": f.name,
                "available_slots": f.available_slots,
                "is_external": f.is_external,
                "department": f.department
            }
            for f in faculty_list
        }
        
        # Prepare course data
        course_list = session.exec(select(Course)).all()
        course_data = {
            c.id: {
                "code": c.code,
                "name": c.name,
                "type": c.course_type,
                "required_faculty_ids": c.required_faculty_ids,
                "block_size": 2 if c.course_type == "LAB" else 1,
                "section_id": section_id
            }
            for c in course_list
        }
        
        # Prepare constraints data
        constraint_list = session.exec(select(Constraint)).all()
        constraints_data = {
            c.id: {
                "course_id": c.course_id,
                "preferred_days": c.preferred_days,
                "block_size": c.block_size,
                "is_hard": c.is_hard
            }
            for c in constraint_list
        }
        
        # Generate timetable
        success, df, message = generate_timetable(
            faculty_data,
            course_data,
            constraints_data,
            section.name
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Convert dataframe to dict for JSON response
        timetable_dict = df.to_dict(orient="records")
        
        return {
            "status": "success",
            "message": message,
            "section": section.name,
            "timetable": timetable_dict,
            "html_table": df.to_html(escape=False, classes="dataframe")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating timetable: {str(e)}")


@app.post("/api/upload-config", response_model=dict)
def upload_config(file: UploadFile = File(...)) -> dict:
    """
    Upload JSON configuration file to populate database.
    
    Expected JSON format:
    {
        "faculty": [...],
        "courses": [...],
        "sections": [...],
        "constraints": [...]
    }
    """
    try:
        content = json.loads(file.file.read())
        
        # Validate structure
        required_keys = ["faculty", "courses", "sections", "constraints"]
        if not all(key in content for key in required_keys):
            raise ValueError(f"JSON must contain: {', '.join(required_keys)}")
        
        return {
            "status": "success",
            "message": "Config file parsed successfully",
            "preview": {
                "faculty_count": len(content.get("faculty", [])),
                "courses_count": len(content.get("courses", [])),
                "sections_count": len(content.get("sections", [])),
                "constraints_count": len(content.get("constraints", []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/api/health", response_model=dict)
def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Timetable Generator API is running"
    }


@app.get("/api/stats", response_model=dict)
def get_stats(session: Session = Depends(get_session)) -> dict:
    """Get database statistics."""
    faculty_count = len(session.exec(select(Faculty)).all())
    course_count = len(session.exec(select(Course)).all())
    section_count = len(session.exec(select(Section)).all())
    constraint_count = len(session.exec(select(Constraint)).all())
    
    return {
        "status": "success",
        "faculty": faculty_count,
        "courses": course_count,
        "sections": section_count,
        "constraints": constraint_count
    }


@app.post("/api/reset-db", response_model=dict)
def reset_database() -> dict:
    """
    Reset database and initialize with sample data.
    WARNING: This will delete all existing data!
    """
    try:
        # Drop all tables
        from sqlmodel import SQLModel
        SQLModel.metadata.drop_all(engine)
        
        # Create new tables and init sample data
        create_db_and_tables()
        init_sample_data()
        
        return {
            "status": "success",
            "message": "Database reset and initialized with sample data"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
