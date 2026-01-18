"""
backend.py - FastAPI Backend for Timetable Generator
====================================================
Provides REST API endpoints for timetable generation and data management.
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from passlib.context import CryptContext
from jose import JWTError, jwt

from database import (
    create_db_and_tables, get_session, engine,
    Faculty, Course, Section, Constraint, TimetableEntry, init_sample_data,
    User, Department
)
from algorithm import generate_timetable, DAYS, SCHEDULABLE_PERIODS


# ============================================================================
# SECURITY SETUP
# ============================================================================

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"  # Change in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return payload."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_session)
) -> User:
    """Get current authenticated user."""
    username = token_payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    
    return user


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
# AUTHENTICATION ENDPOINTS
# ============================================================================

class LoginRequest(SQLModel):
    """Login request model."""
    username: str
    password: str


class RegisterRequest(SQLModel):
    """User registration request model."""
    username: str
    email: str
    password: str
    full_name: str
    role: str = "FACULTY"
    department_id: Optional[int] = None


@app.post("/api/auth/register", response_model=dict)
def register_user(
    request: RegisterRequest,
    session: Session = Depends(get_session)
) -> dict:
    """Register a new user."""
    # Check if username already exists
    existing_user = session.exec(select(User).where(User.username == request.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    existing_email = session.exec(select(User).where(User.email == request.email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=hashed_password,
        full_name=request.full_name,
        role=request.role,
        department_id=request.department_id,
        is_active=True,
        is_verified=False
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return {
        "status": "success",
        "message": "User registered successfully",
        "user_id": new_user.id
    }


@app.post("/api/auth/login", response_model=dict)
def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
) -> dict:
    """Authenticate user and return JWT token."""
    # Find user by username
    user = session.exec(select(User).where(User.username == request.username)).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    # Update last login
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department_id": user.department_id
        }
    }


@app.get("/api/auth/me", response_model=dict)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get current authenticated user information."""
    return {
        "status": "success",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "department_id": current_user.department_id,
            "last_login": current_user.last_login
        }
    }


@app.post("/api/auth/change-password", response_model=dict)
def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> dict:
    """Change user password."""
    # Verify old password
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    # Update password
    current_user.password_hash = get_password_hash(new_password)
    session.add(current_user)
    session.commit()
    
    return {
        "status": "success",
        "message": "Password changed successfully"
    }


# ============================================================================
# DEPARTMENT ENDPOINTS
# ============================================================================

@app.post("/api/department", response_model=dict)
def create_department(
    department: Department,
    session: Session = Depends(get_session)
) -> dict:
    """Create a new department."""
    try:
        session.add(department)
        session.commit()
        session.refresh(department)
        return {"status": "success", "id": department.id, "data": department}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/department", response_model=dict)
def list_departments(session: Session = Depends(get_session)) -> dict:
    """Get all departments."""
    departments = session.exec(select(Department)).all()
    return {
        "status": "success",
        "count": len(departments),
        "data": departments
    }


@app.get("/api/department/{department_id}", response_model=dict)
def get_department(
    department_id: int,
    session: Session = Depends(get_session)
) -> dict:
    """Get a specific department."""
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"status": "success", "data": department}


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
def list_faculty(
    department_id: Optional[int] = None,
    session: Session = Depends(get_session)
) -> dict:
    """Get all faculty members, optionally filtered by department."""
    query = select(Faculty)
    
    if department_id is not None:
        query = query.where(Faculty.department_id == department_id)
    
    faculty_list = session.exec(query).all()
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
def list_courses(
    department_id: Optional[int] = None,
    session: Session = Depends(get_session)
) -> dict:
    """Get all courses, optionally filtered by department."""
    query = select(Course)
    
    if department_id is not None:
        # Get courses for this department or shared with this department
        courses = session.exec(query).all()
        filtered_courses = [
            course for course in courses
            if course.department_id == department_id or 
               (course.shared_departments and department_id in course.shared_departments)
        ]
        return {
            "status": "success",
            "count": len(filtered_courses),
            "data": filtered_courses
        }
    
    courses = session.exec(query).all()
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
