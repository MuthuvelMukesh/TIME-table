# 📅 MKCE Timetable Generator - Complete Project Index

## 🎯 Project Overview

A full-stack Timetable Generator for M. Kumarasamy College of Engineering (MKCE) Department of Information Technology with:
- **Frontend**: Streamlit interactive UI
- **Backend**: FastAPI REST API  
- **Algorithm**: Constraint Satisfaction Problem (CSP) solver
- **Database**: SQLModel + SQLite (PostgreSQL ready)

---

## 📁 Project Files Guide

### 🔵 Core Application Files

#### 1. `timetable_generator/__init__.py`
- Package initialization
- Version info
- **When to use**: Part of package structure

#### 2. `timetable_generator/database.py` ⭐
- **Purpose**: Database schema & management
- **Key Classes**: Faculty, Course, Section, Constraint, TimetableEntry
- **What it does**:
  - Defines SQLModel schemas
  - Creates/manages database
  - Initializes sample data
  - Provides ORM layer
- **When to modify**: When adding new data models
- **Lines of code**: ~450

#### 3. `timetable_generator/algorithm.py` ⭐
- **Purpose**: Core CSP solver for timetable generation
- **Key Classes**: TimetableCSP, Period, ScheduleSlot
- **What it does**:
  - Defines constraint satisfaction problem
  - Implements lab block constraints
  - Validates faculty availability
  - Prevents faculty clashes
  - Generates timetable DataFrame
- **When to modify**: When changing scheduling logic
- **Lines of code**: ~600

#### 4. `timetable_generator/backend.py` ⭐
- **Purpose**: FastAPI REST API server
- **What it does**:
  - Provides REST endpoints for CRUD operations
  - Integrates with database & algorithm
  - Handles timetable generation requests
  - Provides Swagger/OpenAPI documentation
- **Endpoints**: 16+ RESTful endpoints
- **When to modify**: When adding API features
- **Lines of code**: ~550

#### 5. `timetable_generator/app.py` ⭐
- **Purpose**: Streamlit interactive web UI
- **What it does**:
  - Provides user interface for faculty/course management
  - Handles timetable generation requests
  - Displays results in colorful DataFrames
  - Enables CSV export
- **Pages**: Dashboard, Faculty Mgmt, Course Mgmt, Section Mgmt, Generate Timetable, Settings
- **When to modify**: When updating UI features
- **Lines of code**: ~700

---

### 📚 Documentation Files

#### `README.md`
- **What**: Main project documentation
- **Contains**: Features, tech stack, database models, API endpoints, usage examples
- **Read this**: First! For complete overview
- **Length**: ~500 lines

#### `QUICK_START.md`
- **What**: 5-minute quick start guide
- **Contains**: Step-by-step setup, time grid, key features, troubleshooting
- **Read this**: For immediate hands-on start
- **Length**: ~150 lines

#### `SETUP.md`
- **What**: Detailed setup and deployment guide
- **Contains**: Installation, configuration, running options, API testing, troubleshooting, production deployment
- **Read this**: For comprehensive setup instructions
- **Length**: ~400 lines

#### `IMPLEMENTATION_SUMMARY.md`
- **What**: Technical architecture and implementation details
- **Contains**: Algorithm description, constraint logic, data structures, examples
- **Read this**: For understanding how everything works
- **Length**: ~450 lines

#### `PROJECT_COMPLETION.md`
- **What**: Project completion report
- **Contains**: What's delivered, code quality, features checklist, verification
- **Read this**: For quality assurance and verification
- **Length**: ~400 lines

---

### ⚙️ Configuration & Testing Files

#### `requirements.txt`
- **Purpose**: Python package dependencies
- **Contains**: All required libraries with versions
- **Command to install**: `pip install -r requirements.txt`

#### `config_sample.json`
- **Purpose**: Sample configuration with test data
- **Contains**: Faculty, courses, sections, constraints examples
- **Usage**: Reference for JSON structure when importing data

#### `tests.py`
- **Purpose**: Comprehensive test suite
- **Contains**: Unit tests, integration tests, constraint validation
- **Run with**: `pytest tests.py -v`
- **Coverage**: Algorithm, database, constraints, DataFrame generation

#### `startup.py`
- **Purpose**: Easy startup helper script
- **Contains**: Dependency checker, backend/frontend starter
- **Run with**: `python startup.py`
- **Benefit**: Simplified startup without memorizing commands

---

## 🚀 Quick Navigation Guide

### 📖 Which File to Read?

**"I want to get started immediately"**
→ Read: [QUICK_START.md](QUICK_START.md)

**"I want to understand the full project"**
→ Read: [README.md](README.md)

**"I'm installing for the first time"**
→ Read: [SETUP.md](SETUP.md)

**"I need technical details about implementation"**
→ Read: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

**"I need to verify completeness/quality"**
→ Read: [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md)

**"I want to understand the algorithm"**
→ Read: [timetable_generator/algorithm.py](timetable_generator/algorithm.py) + IMPLEMENTATION_SUMMARY.md

**"I want to understand the database"**
→ Read: [timetable_generator/database.py](timetable_generator/database.py) + README.md

**"I want to use the API"**
→ Read: [timetable_generator/backend.py](timetable_generator/backend.py) + README.md

**"I want to customize the UI"**
→ Read: [timetable_generator/app.py](timetable_generator/app.py)

---

## 🎓 Learning Path

### Beginner (Want to use the app)
1. Start: [QUICK_START.md](QUICK_START.md)
2. Install: `pip install -r requirements.txt`
3. Run backend & frontend
4. Use Streamlit UI at http://localhost:8501

### Intermediate (Want to customize)
1. Read: [README.md](README.md)
2. Read: [SETUP.md](SETUP.md)
3. Understand: [timetable_generator/database.py](timetable_generator/database.py)
4. Modify: database models or UI in [timetable_generator/app.py](timetable_generator/app.py)

### Advanced (Want to modify algorithm)
1. Read: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
2. Study: [timetable_generator/algorithm.py](timetable_generator/algorithm.py)
3. Understand: CSP solver constraints
4. Modify: Constraint logic in TimetableCSP class

### Expert (Full understanding)
1. Read all: All documentation files
2. Study: All source files
3. Run: `pytest tests.py -v` to understand test patterns
4. Deploy: Following [SETUP.md](SETUP.md) production section

---

## 🔑 Key Concepts Quick Reference

### Time Grid
- **7 Periods**: P1(08:45-09:45) to P7(03:50-04:40)
- **3 Breaks**: After P2, P4, P5 (not schedulable)
- **Lab Blocks**: Can use (1,2), (3,4), (6,7) only

### Lab Constraint
- **Requirement**: 2 consecutive periods without break
- **Faculty**: Exactly 2 faculty members required
- **Validation**: Both faculty must be free simultaneously

### CSP Solver
- **Variables**: Each course → (day, period) slot
- **Domain**: All valid period combinations
- **Constraints**: Faculty availability, no clashes, block sizes
- **Solution**: First valid assignment found

### Database Models
- **Faculty**: Name, department, availability_slots, is_external
- **Course**: Code, name, type (THEORY/LAB), required_faculty_ids
- **Section**: Name, year, division
- **Constraint**: Course, section, block_size, preferred_days

### API Endpoints
- **CRUD**: `/api/faculty`, `/api/course`, `/api/section`, `/api/constraint`
- **Main**: `POST /api/generate-timetable?section_id=X`
- **Utilities**: `/api/health`, `/api/stats`, `/api/reset-db`

---

## 💻 Command Reference

### Installation
```bash
cd TIME-table
pip install -r requirements.txt
```

### Running
```bash
# Terminal 1 - Backend
python -m uvicorn timetable_generator.backend:app --reload

# Terminal 2 - Frontend
streamlit run timetable_generator/app.py

# Alternative - Easy startup
python startup.py
```

### API Testing
```bash
curl http://localhost:8000/api/faculty
curl http://localhost:8000/docs  # Swagger UI
```

### Database
```bash
# Initialize with samples
python timetable_generator/database.py

# Reset
curl -X POST http://localhost:8000/api/reset-db
```

### Testing
```bash
pytest tests.py -v
```

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Total Python Code | ~3,000 lines |
| Documentation | ~4,000 lines |
| Test Code | ~400 lines |
| Database Models | 5 models |
| API Endpoints | 16+ endpoints |
| Streamlit Pages | 6 pages |
| Supported Constraints | 5 hard + 1 soft |
| Files Created | 12 files |

---

## ✅ Feature Checklist

- ✅ Lab block size constraint (2 consecutive periods)
- ✅ Multi-faculty requirement for labs
- ✅ Faculty availability hard constraint
- ✅ No faculty clash constraint
- ✅ Preferred days soft constraint
- ✅ External faculty support (Math/Placement)
- ✅ Multiple section scheduling
- ✅ Break time handling
- ✅ REST API with 16+ endpoints
- ✅ Interactive Streamlit UI
- ✅ CSV export
- ✅ Database with ORM
- ✅ Test suite
- ✅ Comprehensive documentation

---

## 🎯 Use Cases

### Use Case 1: Simple Scheduling
- Add 5 faculty
- Create 3 courses (1 lab, 2 theory)
- Generate timetable for 1 section
- Done in < 5 minutes!

### Use Case 2: Complex Scheduling
- 20+ faculty members
- 50+ courses (labs + theories)
- 4+ sections
- Multiple constraints and preferences
- Full CSP solver in action

### Use Case 3: API Integration
- Call `/api/generate-timetable` from existing system
- Integrate with college MIS
- Webhooks for updates
- Automated scheduling

### Use Case 4: Data Import/Export
- Upload `config_sample.json` format
- Export results as CSV
- Share timetables with staff
- Backup in database

---

## 🔒 Security Notes

- ✅ Input validation on all endpoints
- ✅ SQL injection prevention (ORM)
- ✅ CORS enabled for frontend
- ✅ Error messages don't leak info
- ✅ Environment variables for secrets
- ✅ No hardcoded credentials

---

## 🚀 Deployment Options

### Option 1: Local Development
```bash
python -m uvicorn timetable_generator.backend:app --reload
streamlit run timetable_generator/app.py
```

### Option 2: Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 timetable_generator.backend:app
```

### Option 3: Docker
```bash
docker build -t mkce-timetable .
docker run -p 8000:8000 -p 8501:8501 mkce-timetable
```

### Option 4: Cloud (Heroku, AWS, Azure)
See [SETUP.md](SETUP.md) for detailed instructions

---

## 📞 Troubleshooting Map

| Problem | Solution |
|---------|----------|
| Dependencies not found | `pip install -r requirements.txt` |
| Port in use | Change port or kill process |
| API not responding | Start backend first |
| Database errors | Delete `timetable.db` and reinitialize |
| CSP no solution | Check faculty availability |
| UI won't load | Clear Streamlit cache |

See [SETUP.md](SETUP.md) for detailed troubleshooting.

---

## 🎓 Architecture Overview

```
┌─────────────────────────────────────┐
│      Streamlit Frontend (UI)        │
│   (timetable_generator/app.py)      │
└──────────────┬──────────────────────┘
               │
               │ HTTP
               ↓
┌─────────────────────────────────────┐
│    FastAPI Backend (REST API)       │
│  (timetable_generator/backend.py)   │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        ↓             ↓
    ┌───────────┐  ┌──────────────┐
    │ Database  │  │ CSP Solver   │
    │ (SQLModel)│  │ (algorithm)  │
    │ (SQLite)  │  │(Constraints) │
    └───────────┘  └──────────────┘
```

---

## 🎉 Ready to Go!

You have a complete, production-ready timetable generator!

### Next Steps:
1. **Read**: [QUICK_START.md](QUICK_START.md)
2. **Install**: `pip install -r requirements.txt`
3. **Run**: Backend + Frontend
4. **Use**: Generate your first timetable!

### For Help:
- Quick questions → [QUICK_START.md](QUICK_START.md)
- Setup issues → [SETUP.md](SETUP.md)
- Technical details → [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- API docs → http://localhost:8000/docs
- Inline code comments → Check each .py file

---

**Happy Scheduling!** 📅✨

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: January 2026
