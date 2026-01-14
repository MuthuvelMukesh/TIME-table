# 📅 MKCE Timetable Generator

A full-stack, production-ready timetable generator for M. Kumarasamy College of Engineering (MKCE) Department of Information Technology with intelligent constraint-based scheduling.

## 🎯 Overview

This application automatically generates conflict-free timetables for college sections while handling complex constraints like:
- Multi-faculty lab requirements (2 faculty members per lab)
- Faculty availability constraints
- Lab block scheduling (2 consecutive periods without breaks)
- No faculty clash prevention
- Preferred day soft constraints

### Technology Stack

- **Frontend**: Streamlit (Interactive Web UI)
- **Backend**: FastAPI (REST API)
- **Database**: SQLModel + SQLite (PostgreSQL ready)
- **Algorithm**: python-constraint (CSP Solver)
- **Data Processing**: Pandas

---

## ✨ Key Features

### Core Features
- ✅ **Multi-faculty lab scheduling** - Labs require 2 faculty members simultaneously
- ✅ **Faculty availability constraints** - Respects faculty free time slots
- ✅ **Lab block validation** - Ensures 2 consecutive periods without breaks
- ✅ **No faculty clashes** - Prevents double-booking faculty
- ✅ **Multiple sections** - Generate timetables for multiple class sections
- ✅ **Break time handling** - Properly handles 3 daily breaks in schedule

### User Interface
- ✅ **Interactive Streamlit UI** - 6 intuitive pages for complete management
- ✅ **CSV export** - Download generated timetables
- ✅ **Real-time validation** - Immediate feedback on constraint violations
- ✅ **Colorful displays** - Easy-to-read formatted schedules

### API Features
- ✅ **REST API** - 16+ endpoints for programmatic access
- ✅ **Swagger Documentation** - Interactive API docs at `/docs`
- ✅ **CRUD operations** - Full management of faculty, courses, sections
- ✅ **Database reset** - Easy sample data initialization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation (5 minutes)

1. **Clone the repository**
```bash
git clone https://github.com/MuthuvelMukesh/TIME-table.git
cd TIME-table
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the backend** (Terminal 1)
```bash
python -m uvicorn timetable_generator.backend:app --reload
```
✅ Ready when you see: `Uvicorn running on http://127.0.0.1:8000`

4. **Start the frontend** (Terminal 2)
```bash
streamlit run timetable_generator/app.py
```
✅ Ready when browser opens at `http://localhost:8501`

5. **Initialize database**
   - Go to **Settings** tab in Streamlit UI
   - Click **"Reset Database"** to load sample data

6. **Generate your first timetable**
   - Go to **Generate Timetable** tab
   - Select section: "II Year IT A"
   - Click **"Generate Timetable"**

### Alternative: Easy Startup Script
```bash
python startup.py
```
Follow the prompts to start backend, frontend, or both.

---

## ⏰ Time Grid Reference

| Period | Time | Notes |
|--------|------|-------|
| P1 | 08:45 - 09:45 | |
| P2 | 09:45 - 10:45 | |
| 🔴 **BREAK** | 10:45 - 11:05 | Not schedulable |
| P3 | 11:05 - 12:05 | |
| P4 | 12:05 - 01:05 | |
| 🔴 **LUNCH** | 01:05 - 01:55 | Not schedulable |
| P5 | 01:55 - 02:45 | |
| 🔴 **BREAK** | 02:45 - 03:00 | Not schedulable |
| P6 | 03:00 - 03:50 | |
| P7 | 03:50 - 04:40 | |

**Valid Lab Blocks**: (P1,P2), (P3,P4), (P6,P7) - consecutive periods without breaks

---

## 📚 Usage Examples

### Using the Streamlit UI

1. **Manage Faculty**
   - Navigate to "Faculty Management"
   - Add faculty with name, department, and availability slots
   - Mark external faculty (e.g., Math, Placement officers)

2. **Manage Courses**
   - Navigate to "Course Management"
   - Add courses with code, name, type (THEORY/LAB)
   - Assign required faculty (2 for labs, 1 for theory)

3. **Manage Sections**
   - Navigate to "Section Management"
   - Create sections (e.g., "II Year IT A")

4. **Generate Timetables**
   - Navigate to "Generate Timetable"
   - Select a section
   - Click "Generate Timetable"
   - View and download the result

### Using the REST API

**Get all faculty:**
```bash
curl http://localhost:8000/api/faculty
```

**Create a new course:**
```bash
curl -X POST http://localhost:8000/api/course \
  -H "Content-Type: application/json" \
  -d '{
    "code": "IT301",
    "name": "Data Structures",
    "course_type": "THEORY",
    "credits": 3,
    "weekly_hours": 3,
    "required_faculty_ids": [1]
  }'
```

**Generate timetable:**
```bash
curl -X POST "http://localhost:8000/api/generate-timetable?section_id=1"
```

**Interactive API Documentation:**
Visit `http://localhost:8000/docs` for Swagger UI with all endpoints.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      Streamlit Frontend (UI)        │
│   (timetable_generator/app.py)      │
│   - Dashboard                       │
│   - Faculty Management              │
│   - Course Management               │
│   - Section Management              │
│   - Generate Timetable              │
│   - Settings                        │
└──────────────┬──────────────────────┘
               │
               │ HTTP REST API
               ↓
┌─────────────────────────────────────┐
│    FastAPI Backend (REST API)       │
│  (timetable_generator/backend.py)   │
│   - 16+ RESTful endpoints           │
│   - CRUD operations                 │
│   - Swagger documentation           │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        ↓             ↓
    ┌───────────┐  ┌──────────────┐
    │ Database  │  │ CSP Solver   │
    │ (SQLModel)│  │ (algorithm)  │
    │ (SQLite)  │  │              │
    │           │  │ Constraints: │
    │ Models:   │  │ - Lab blocks │
    │ - Faculty │  │ - Faculty    │
    │ - Course  │  │   availability│
    │ - Section │  │ - No clashes │
    │ - Constr. │  │ - Preferences│
    │ - Entries │  │              │
    └───────────┘  └──────────────┘
```

---

## 📖 Database Models

### Faculty
- `id`: Unique identifier
- `name`: Faculty name
- `department`: Department (IT, Math, etc.)
- `specialization`: Subject expertise
- `available_slots`: JSON with daily free periods
- `is_external`: External faculty flag

### Course
- `id`: Unique identifier
- `code`: Course code (e.g., "IT301")
- `name`: Course name
- `course_type`: THEORY or LAB
- `credits`: Credit hours
- `weekly_hours`: Hours per week
- `required_faculty_ids`: List of faculty IDs

### Section
- `id`: Unique identifier
- `name`: Section name (e.g., "II Year IT A")
- `year`: Academic year
- `division`: Division/batch

### Constraint
- `id`: Unique identifier
- `course_id`: Associated course
- `section_id`: Associated section
- `block_size`: Required consecutive periods
- `preferred_days`: Preferred days list

### TimetableEntry
- `id`: Unique identifier
- `section_id`: Section reference
- `course_id`: Course reference
- `day`: Day of week
- `period`: Period number (1-7)
- `faculty_ids`: Assigned faculty list

---

## 🔌 API Endpoints

### Faculty Management
- `GET /api/faculty` - List all faculty
- `POST /api/faculty` - Create faculty
- `GET /api/faculty/{id}` - Get faculty by ID
- `PUT /api/faculty/{id}` - Update faculty
- `DELETE /api/faculty/{id}` - Delete faculty

### Course Management
- `GET /api/course` - List all courses
- `POST /api/course` - Create course
- `GET /api/course/{id}` - Get course by ID
- `PUT /api/course/{id}` - Update course
- `DELETE /api/course/{id}` - Delete course

### Section Management
- `GET /api/section` - List all sections
- `POST /api/section` - Create section
- `GET /api/section/{id}` - Get section by ID
- `PUT /api/section/{id}` - Update section
- `DELETE /api/section/{id}` - Delete section

### Constraint Management
- `GET /api/constraint` - List all constraints
- `POST /api/constraint` - Create constraint
- `GET /api/constraint/{id}` - Get constraint by ID
- `DELETE /api/constraint/{id}` - Delete constraint

### Timetable Operations
- `POST /api/generate-timetable?section_id={id}` - Generate timetable
- `GET /api/timetable/{section_id}` - Get existing timetable

### Utilities
- `GET /api/health` - Health check
- `GET /api/stats` - Database statistics
- `POST /api/reset-db` - Reset database with sample data

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
pytest tests.py -v
```

The test suite includes:
- Unit tests for algorithm components
- Integration tests for database operations
- Constraint validation tests
- DataFrame generation tests
- API endpoint tests

---

## 🛠️ Configuration

### Database Configuration

Default: SQLite (`timetable.db`)

For PostgreSQL (production):
```python
# In database.py
DATABASE_URL = "postgresql://user:password@localhost:5432/timetable_db"
```

### Port Configuration

Backend (default: 8000):
```bash
python -m uvicorn timetable_generator.backend:app --port 8001
```

Frontend (default: 8501):
```bash
streamlit run timetable_generator/app.py --server.port 8502
```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'timetable_generator'"
**Solution:** Ensure you're in the TIME-table directory and Python path is set correctly.

### Issue: "Connection refused" when accessing frontend
**Solution:** Ensure backend is running on port 8000 first.

### Issue: "Database is locked"
**Solution:** Delete `timetable.db` and reinitialize with sample data.

### Issue: "No feasible solution found"
**Solutions:**
1. Check faculty availability - ensure sufficient free slots
2. Verify course-faculty assignments are correct
3. Review constraint preferences
4. Increase faculty availability or reduce courses

### Issue: Port already in use
**Solution:**
```bash
# Linux/Mac
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📁 Project Structure

```
TIME-table/
├── timetable_generator/
│   ├── __init__.py          # Package initialization
│   ├── database.py          # SQLModel schemas (~450 lines)
│   ├── algorithm.py         # CSP solver logic (~600 lines)
│   ├── backend.py           # FastAPI server (~550 lines)
│   └── app.py               # Streamlit UI (~700 lines)
├── tests.py                 # Test suite (~400 lines)
├── startup.py               # Easy startup script
├── requirements.txt         # Python dependencies
├── config_sample.json       # Sample configuration
├── README.md               # This file
├── QUICK_START.md          # 5-minute quick start
├── SETUP.md                # Detailed setup guide
├── IMPLEMENTATION_SUMMARY.md # Technical deep-dive
├── INDEX.md                # Complete project index
└── PROJECT_COMPLETION.md   # Completion report
```

---

## 📖 Additional Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[SETUP.md](SETUP.md)** - Detailed setup and deployment guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical architecture and algorithm details
- **[INDEX.md](INDEX.md)** - Complete project file guide and navigation
- **[PROJECT_COMPLETION.md](PROJECT_COMPLETION.md)** - Project completion report

---

## 🚀 Deployment

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 timetable_generator.backend:app
```

### Using Docker
```bash
docker build -t mkce-timetable .
docker run -p 8000:8000 -p 8501:8501 mkce-timetable
```

See [SETUP.md](SETUP.md) for detailed deployment instructions including Nginx configuration and environment variables.

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Total Python Code | ~3,000 lines |
| Documentation | ~4,000 lines |
| Test Coverage | ~400 lines |
| Database Models | 5 models |
| API Endpoints | 16+ endpoints |
| UI Pages | 6 pages |
| Supported Constraints | 5 hard + 1 soft |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

## 📄 License

This project is open source and available for use and modification.

---

## 👥 Author

**MuthuvelMukesh**

---

## 🙏 Acknowledgments

- M. Kumarasamy College of Engineering (MKCE)
- Department of Information Technology
- Python constraint programming community

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: January 2026

---

For questions, issues, or feature requests, please open an issue on GitHub.