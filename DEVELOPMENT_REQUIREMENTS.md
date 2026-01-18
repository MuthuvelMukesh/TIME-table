# DEVELOPMENT REQUIREMENTS - Timetable Generator System

## Overview
This document outlines the requirements for implementing a login system with user authentication, multi-department support, staff entry, and course entry functionalities for the MKCE Timetable Generator application.

---

## 1. Login Page with User Authentication

### 1.1 User Model (Database Schema)

Create a new `User` table in the database with the following fields:

```python
class User(SQLModel, table=True):
    id: Optional[int] = Primary Key
    username: str (unique, indexed)
    email: str (unique, indexed)
    password_hash: str (hashed password using bcrypt/passlib)
    full_name: str
    role: str (values: "ADMIN", "HOD", "FACULTY", "STAFF")
    department_id: Optional[int] (Foreign Key to Department)
    is_active: bool (default: True)
    is_verified: bool (default: False)
    created_at: datetime
    last_login: Optional[datetime]
```

### 1.2 Login Page UI Components

**Location**: `timetable_generator/login.py` (new Streamlit page)

**Features Required**:
- Login form with:
  - Username/Email field
  - Password field (masked input)
  - "Remember Me" checkbox
  - "Login" button
  - "Forgot Password?" link
  
- User Registration form:
  - Full name
  - Email
  - Username
  - Password (with confirmation)
  - Department selection dropdown
  - Role selection (for admin use)
  
- Session Management:
  - Use Streamlit session state to store logged-in user info
  - Implement auto-logout after inactivity (30 minutes)
  - Display logged-in user name in sidebar

### 1.3 Authentication Backend API

**New Endpoints to Create in `backend.py`**:

```python
POST /api/auth/register
  - Create new user account
  - Hash password using bcrypt
  - Send verification email (optional)
  
POST /api/auth/login
  - Validate username/password
  - Return JWT token or session ID
  - Update last_login timestamp
  
POST /api/auth/logout
  - Invalidate session/token
  - Clear user session data
  
GET /api/auth/me
  - Get current logged-in user details
  - Requires authentication token
  
POST /api/auth/change-password
  - Allow users to change their password
  - Require old password verification
```

### 1.4 Authentication Middleware

Implement middleware to protect API endpoints:
- Verify JWT token or session ID
- Check user permissions based on role
- Return 401 Unauthorized for invalid tokens
- Return 403 Forbidden for insufficient permissions

---

## 2. Multi-Department Connections

### 2.1 Department Model (Database Schema)

Create a new `Department` table:

```python
class Department(SQLModel, table=True):
    id: Optional[int] = Primary Key
    code: str (unique, e.g., "IT", "CSE", "ECE", "MECH")
    name: str (e.g., "Information Technology")
    hod_user_id: Optional[int] (Foreign Key to User)
    building: Optional[str]
    num_sections: int (default: 2)
    active: bool (default: True)
    created_at: datetime
```

### 2.2 Update Existing Models

**Faculty Model Updates**:
```python
# Add to Faculty model
department_id: int (Foreign Key to Department)
user_id: Optional[int] (Foreign Key to User - link faculty to login account)
```

**Course Model Updates**:
```python
# Add to Course model
department_id: int (Foreign Key to Department)
shared_departments: List[int] (JSON - list of dept IDs for shared courses)
```

**Section Model Updates**:
```python
# Add to Section model
department_id: int (Foreign Key to Department)
```

### 2.3 Multi-Department Features

**Department Dashboard**:
- View statistics per department
- Show faculty count, course count, sections per department
- Filter timetables by department
- Allow HOD to manage their department's data

**Cross-Department Courses**:
- Mark courses as "shared" between departments
- Example: Mathematics shared between IT, CSE, ECE
- Handle faculty availability across departments
- Generate department-specific timetables with shared courses

---

## 3. Staff Entry Form

### 3.1 Enhanced Staff/Faculty Entry UI

**Location**: Update `app.py` Faculty Management tab

**Form Fields Required**:

1. **Personal Information**:
   - Full Name (text input)
   - Email (email input)
   - Phone Number (text input)
   - Employee ID (text input, unique)

2. **Department Information**:
   - Select Department (dropdown from Department table)
   - Specialization (text input)
   - Is External Faculty? (checkbox)

3. **Account Linking**:
   - Link to User Account (dropdown - optional)
   - Or create new user account (checkbox)

4. **Availability Schedule**:
   - Visual calendar grid for selecting available slots
   - Days: Monday to Friday
   - Periods: 1-7 with checkboxes
   - "Select All" and "Clear All" buttons for each day

5. **Additional Details**:
   - Office Location (text input)
   - Qualification (dropdown: PhD, M.Tech, M.E., B.Tech)
   - Years of Experience (number input)

### 3.2 Staff Entry Backend API

**Enhanced Endpoint**:
```python
POST /api/faculty
  - Accept all fields from form
  - Validate department_id exists
  - Create linked user account if requested
  - Return created faculty with ID
  
GET /api/faculty?department_id=<id>
  - Filter faculty by department
  
PUT /api/faculty/{id}
  - Update faculty details
  - Allow department transfer
```

### 3.3 Staff Management Features

- **View All Staff**: Table showing all faculty with filters
- **Search**: Search by name, department, specialization
- **Bulk Import**: Upload CSV file with faculty data
- **Export**: Download faculty list as CSV/Excel
- **Deactivate/Activate**: Soft delete functionality

---

## 4. Course Entry Form

### 4.1 Enhanced Course Entry UI

**Location**: Update `app.py` Course Management tab

**Form Fields Required**:

1. **Basic Information**:
   - Course Code (text input, unique, e.g., "IT301")
   - Course Name (text input, e.g., "Machine Learning")
   - Course Type (dropdown: THEORY, LAB, TUTORIAL)
   - Credits (number input, 1-6)
   - Weekly Hours (number input, 1-8)

2. **Department Association**:
   - Primary Department (dropdown from Department table)
   - Shared with Departments (multi-select dropdown)

3. **Faculty Assignment**:
   - For THEORY courses:
     - Select 1 Primary Faculty (dropdown filtered by department)
   - For LAB courses:
     - Select 2 Faculty Members (multi-select, requires exactly 2)
     - Faculty must be from same or shared departments

4. **Scheduling Preferences**:
   - Preferred Days (multi-select: Mon-Fri)
   - Avoid Days (multi-select: Mon-Fri)
   - Preferred Time Slots (morning/afternoon)
   - Lab requires consecutive periods (auto-handled)

5. **Prerequisites**:
   - Prerequisite Courses (multi-select from existing courses)
   - Co-requisite Courses (multi-select)

### 4.2 Course Entry Backend API

**Enhanced Endpoint**:
```python
POST /api/course
  - Validate course code is unique
  - Validate department_id exists
  - Validate faculty assignments:
    - THEORY: 1 faculty
    - LAB: exactly 2 faculty
  - Create associated constraint automatically
  
GET /api/course?department_id=<id>
  - Filter courses by department
  - Include shared courses
  
PUT /api/course/{id}
  - Update course details
  - Validate faculty assignments on update
  
DELETE /api/course/{id}
  - Soft delete or prevent if used in timetable
```

### 4.3 Course Management Features

- **View All Courses**: Table with filters by department, type
- **Search**: Search by course code or name
- **Duplicate Course**: Copy course for different section
- **Bulk Import**: Upload CSV with course data
- **Export**: Download course catalog as CSV/Excel
- **Course Dependencies**: View prerequisite chains

---

## 5. Database Migration Plan

### 5.1 New Tables to Create

1. **User** - Authentication and authorization
2. **Department** - Department information
3. **UserSession** - Active user sessions (optional)
4. **AuditLog** - Track changes for accountability (optional)

### 5.2 Schema Changes to Existing Tables

**Faculty table**:
- Add `department_id` column (Foreign Key)
- Add `user_id` column (Foreign Key, nullable)
- Add `employee_id` column (unique)
- Add `qualification` column
- Add `office_location` column

**Course table**:
- Add `department_id` column (Foreign Key)
- Add `shared_departments` column (JSON array)

**Section table**:
- Add `department_id` column (Foreign Key)

### 5.3 Migration Script

Create `migrations/001_add_auth_and_departments.py`:
```python
# Script to:
# 1. Create new tables (User, Department)
# 2. Add new columns to existing tables
# 3. Migrate existing data (assign to default department)
# 4. Create admin user account
```

---

## 6. Security Requirements

### 6.1 Password Security
- Use bcrypt or passlib for password hashing
- Minimum password length: 8 characters
- Require: uppercase, lowercase, number, special character
- Implement password reset via email

### 6.2 API Security
- Use JWT tokens with 24-hour expiry
- Implement refresh tokens
- Rate limiting on login endpoint (5 attempts per minute)
- HTTPS required in production

### 6.3 Role-Based Access Control (RBAC)

**ADMIN Role**:
- Full access to all departments
- Create/delete departments
- Manage user accounts
- System configuration

**HOD Role**:
- Full access to their department
- Add/edit faculty in their department
- Add/edit courses in their department
- Generate timetables for their sections

**FACULTY Role**:
- View their own timetable
- Update their availability
- View their department's timetable
- No edit access to courses/sections

**STAFF Role**:
- View-only access
- Generate reports
- Export timetables

---

## 7. Implementation Phases

### Phase 1: Database and Models (Week 1)
- [ ] Create User model in `database.py`
- [ ] Create Department model in `database.py`
- [ ] Update existing models with new relationships
- [ ] Create database migration script
- [ ] Test database schema changes

### Phase 2: Backend Authentication API (Week 2)
- [ ] Implement authentication endpoints in `backend.py`
- [ ] Add JWT token generation/validation
- [ ] Create authentication middleware
- [ ] Add role-based access control decorators
- [ ] Write API tests for authentication

### Phase 3: Login UI (Week 3)
- [ ] Create login page in Streamlit
- [ ] Implement session management
- [ ] Add user registration form
- [ ] Add password reset functionality
- [ ] Test login flow end-to-end

### Phase 4: Multi-Department Support (Week 4)
- [ ] Create department management UI
- [ ] Update faculty form with department selection
- [ ] Update course form with department selection
- [ ] Implement department filtering in all views
- [ ] Test cross-department scenarios

### Phase 5: Enhanced Forms (Week 5)
- [ ] Enhance staff entry form with all new fields
- [ ] Enhance course entry form with all new fields
- [ ] Add form validation on frontend and backend
- [ ] Add bulk import/export functionality
- [ ] Test form submissions and data integrity

### Phase 6: Testing and Documentation (Week 6)
- [ ] Write unit tests for new models
- [ ] Write integration tests for authentication
- [ ] Update user documentation
- [ ] Create admin guide
- [ ] Perform security audit

---

## 8. Sample Data for Testing

### 8.1 Departments
```json
[
  {"code": "IT", "name": "Information Technology", "num_sections": 2},
  {"code": "CSE", "name": "Computer Science", "num_sections": 3},
  {"code": "ECE", "name": "Electronics and Communication", "num_sections": 2},
  {"code": "MECH", "name": "Mechanical Engineering", "num_sections": 2}
]
```

### 8.2 Users
```json
[
  {
    "username": "admin",
    "email": "admin@mkce.ac.in",
    "full_name": "System Administrator",
    "role": "ADMIN",
    "password": "admin123"
  },
  {
    "username": "it_hod",
    "email": "hod.it@mkce.ac.in",
    "full_name": "Dr. IT HOD",
    "role": "HOD",
    "department": "IT",
    "password": "hod123"
  }
]
```

---

## 9. API Documentation Updates

Update the API documentation to include:
- Authentication flow diagrams
- Request/response examples for new endpoints
- Role permission matrix
- Error codes and messages

---

## 10. Testing Checklist

### Unit Tests
- [ ] User model CRUD operations
- [ ] Department model CRUD operations
- [ ] Password hashing and verification
- [ ] JWT token generation and validation

### Integration Tests
- [ ] Login flow (success and failure cases)
- [ ] Role-based access control
- [ ] Multi-department faculty assignment
- [ ] Timetable generation with multi-department courses

### UI Tests
- [ ] Login form validation
- [ ] Staff entry form with all fields
- [ ] Course entry form with department selection
- [ ] Department filtering in all views

### Security Tests
- [ ] SQL injection attempts
- [ ] XSS attempts
- [ ] Brute force login attempts
- [ ] Unauthorized API access

---

## 11. Future Enhancements (Optional)

- Email notifications for timetable changes
- Mobile app for faculty to view timetables
- Integration with college ERP system
- Automatic conflict detection and resolution
- Academic calendar integration
- Room allocation optimization
- Student timetable generation

---

## 12. Team Responsibilities

### Backend Developer
- Implement User and Department models
- Create authentication API endpoints
- Add middleware for role-based access control
- Write backend tests

### Frontend Developer
- Design and implement login page
- Enhance staff and course entry forms
- Add department filtering to all views
- Ensure responsive design

### Database Administrator
- Review and optimize database schema
- Create migration scripts
- Set up database backups
- Monitor query performance

### QA/Testing
- Write test cases for all new features
- Perform security testing
- Conduct user acceptance testing
- Document bugs and issues

---

## 13. Configuration Files

### Update `config_sample.json`
```json
{
  "database": {
    "url": "sqlite:///timetable.db",
    "echo": false
  },
  "auth": {
    "jwt_secret": "your-secret-key-here",
    "jwt_algorithm": "HS256",
    "jwt_expiry_hours": 24,
    "refresh_token_expiry_days": 7
  },
  "security": {
    "password_min_length": 8,
    "require_special_char": true,
    "max_login_attempts": 5,
    "lockout_duration_minutes": 15
  },
  "email": {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "noreply@mkce.ac.in"
  }
}
```

---

## 14. Dependencies to Add

Update `requirements.txt`:
```
# Existing dependencies...

# Authentication and Security
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.6

# Email
python-email-validator==2.1.0
aiosmtplib==3.0.1

# Additional utilities
pydantic[email]==2.5.3
```

---

## 15. Documentation Files to Update

- [ ] README.md - Add authentication setup instructions
- [ ] SETUP.md - Add initial admin user creation steps
- [ ] QUICK_START.md - Add login instructions
- [ ] IMPLEMENTATION_SUMMARY.md - Update with new features

---

## Contact Information

For questions or clarifications on these requirements, contact:

- **Project Lead**: [@MuthuvelMukesh](https://github.com/MuthuvelMukesh)
- **Team Members**: 
  - [@Sairam19062006](https://github.com/Sairam19062006)
  - [@tharun27102006](https://github.com/tharun27102006)

---

**Document Version**: 1.0  
**Last Updated**: January 18, 2026  
**Status**: Ready for Implementation
