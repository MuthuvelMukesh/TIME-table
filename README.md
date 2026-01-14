# 🎓 MKCE Timetable Generator

A production-ready, full-stack Timetable Generator for M. Kumarasamy College of Engineering (MKCE) Department of Information Technology with constraint satisfaction problem (CSP) solving capabilities.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)](https://streamlit.io/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project is a comprehensive timetable generator designed to help educational institutions create and manage conflict-free schedules efficiently. It handles complex constraints including:

- **Multi-faculty lab scheduling** - Labs require exactly 2 faculty members simultaneously
- **Faculty availability** - Respects individual faculty member availability
- **Lab block constraints** - Ensures labs get 2 consecutive periods without breaks
- **No faculty clashes** - Prevents scheduling conflicts for faculty members
- **Preferred days** - Soft constraints for scheduling preferences

The system consists of:
- **Frontend**: Interactive Streamlit web UI for easy management
- **Backend**: FastAPI REST API for programmatic access
- **Algorithm**: Constraint Satisfaction Problem (CSP) solver
- **Database**: SQLModel + SQLite (PostgreSQL ready for production)

## ✨ Features

- ✅ **Automated Timetable Generation** - CSP solver generates conflict-free schedules
- ✅ **Multi-Faculty Lab Support** - Handle labs requiring multiple faculty members
- ✅ **Faculty Availability Management** - Set and track faculty availability by day and period
- ✅ **Section Management** - Create and manage multiple sections (year, division)
- ✅ **Course Management** - Support for both theory and lab courses
- ✅ **Constraint Validation** - Hard and soft constraint enforcement
- ✅ **Interactive Web UI** - User-friendly Streamlit interface
- ✅ **REST API** - 16+ endpoints for full CRUD operations
- ✅ **CSV Export** - Download generated timetables
- ✅ **Break Time Handling** - Proper handling of break periods in schedule
- ✅ **External Faculty Support** - Support for shared faculty (Math, Placement, etc.)
- ✅ **Database Persistence** - SQLite with ORM (PostgreSQL ready)
- ✅ **API Documentation** - Auto-generated Swagger/OpenAPI docs

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - SQL databases with Python type hints (combines SQLAlchemy & Pydantic)
- **Uvicorn** - Lightning-fast ASGI server
- **python-constraint** - Constraint Satisfaction Problem solver

### Frontend
- **Streamlit** - Interactive web application framework
- **Pandas** - Data manipulation and analysis
- **Requests** - HTTP library for API communication

### Database
- **SQLite** - Default embedded database (development)
- **PostgreSQL** - Optional for production deployment

## ⚡ Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### 1. Clone and Install (1 minute)
```bash
git clone https://github.com/MuthuvelMukesh/TIME-table.git
cd TIME-table
pip install -r requirements.txt
```

### 2. Start Backend (Terminal 1)
```bash
python -m uvicorn timetable_generator.backend:app --reload
```
✅ API available at: http://localhost:8000  
✅ API Docs at: http://localhost:8000/docs

### 3. Start Frontend (Terminal 2)
```bash
streamlit run timetable_generator/app.py
```
✅ UI available at: http://localhost:8501

### 4. Initialize Database
- Open http://localhost:8501
- Go to **Settings** tab
- Click **"Reset Database"** to load sample data

### 5. Generate Your First Timetable
- Go to **Generate Timetable** tab
- Select section: "II Year IT A"
- Click **"Generate Timetable"**
- View and download your schedule!

**That's it! You're ready to go!** 🎉

For detailed setup instructions, see [QUICK_START.md](QUICK_START.md).

## 📦 Installation

### Standard Installation

```bash
# Clone repository
git clone https://github.com/MuthuvelMukesh/TIME-table.git
cd TIME-table

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Using startup.py (Easy Mode)

```bash
python startup.py
```

This script will:
- Check dependencies
- Initialize database
- Offer options to start backend, frontend, or both

For advanced installation and deployment options, see [SETUP.md](SETUP.md).

## 💻 Usage

### Through Web UI (Recommended)

1. **Faculty Management**
   - Add faculty members with their availability slots
   - Mark external faculty (Math, Placement, etc.)
   - Edit or remove faculty as needed

2. **Course Management**
   - Create theory courses (single faculty)
   - Create lab courses (requires 2 faculty members)
   - Assign faculty to courses

3. **Section Management**
   - Create sections (year, division)
   - Manage multiple sections independently

4. **Generate Timetables**
   - Select a section
   - Click generate
   - View colorful schedule with break indicators
   - Export to CSV

### Through REST API

```bash
# Get all faculty
curl http://localhost:8000/api/faculty

# Create new course
curl -X POST http://localhost:8000/api/course \
  -H "Content-Type: application/json" \
  -d '{
    "code": "IT301",
    "name": "Machine Learning Lab",
    "course_type": "LAB",
    "credits": 4,
    "weekly_hours": 2,
    "required_faculty_ids": [1, 2]
  }'

# Generate timetable for section
curl -X POST "http://localhost:8000/api/generate-timetable?section_id=1"
```

For complete API documentation, visit http://localhost:8000/docs

### Using Python

```python
import requests

API_URL = "http://localhost:8000/api"

# Get all faculty
response = requests.get(f"{API_URL}/faculty")
faculty = response.json()

# Generate timetable
response = requests.post(
    f"{API_URL}/generate-timetable",
    params={"section_id": 1}
)
timetable = response.json()
print(timetable)
```

## 🗄️ Database Models

### Faculty
```python
{
  "id": int,
  "name": str,
  "department": str,
  "specialization": str,
  "available_slots": {
    "Monday": [1, 2, 3, 5, 6, 7],
    "Tuesday": [1, 2, 3, 5, 6, 7],
    ...
  },
  "is_external": bool
}
```

### Course
```python
{
  "id": int,
  "code": str,              # e.g., "IT301"
  "name": str,              # e.g., "Machine Learning Lab"
  "course_type": str,       # "THEORY" or "LAB"
  "credits": int,
  "weekly_hours": int,
  "required_faculty_ids": [int]  # List of faculty IDs
}
```

### Section
```python
{
  "id": int,
  "name": str,              # e.g., "II Year IT A"
  "year": int,              # 1, 2, 3, or 4
  "division": str,          # "A", "B", "C", etc.
  "department": str         # "IT", "CSE", etc.
}
```

### Constraint
```python
{
  "id": int,
  "course_id": int,
  "section_id": int,
  "block_size": int,        # 1 for theory, 2 for labs
  "preferred_days": [str],  # ["Monday", "Wednesday"]
  "is_hard": bool          # true for required, false for preferred
}
```

## 🔌 API Endpoints

### Faculty Endpoints
- `POST /api/faculty` - Create faculty
- `GET /api/faculty` - List all faculty
- `GET /api/faculty/{id}` - Get specific faculty
- `PUT /api/faculty/{id}` - Update faculty
- `DELETE /api/faculty/{id}` - Delete faculty

### Course Endpoints
- `POST /api/course` - Create course
- `GET /api/course` - List all courses
- `GET /api/course/{id}` - Get specific course
- `PUT /api/course/{id}` - Update course
- `DELETE /api/course/{id}` - Delete course

### Section Endpoints
- `POST /api/section` - Create section
- `GET /api/section` - List all sections
- `GET /api/section/{id}` - Get specific section

### Constraint Endpoints
- `POST /api/constraint` - Create constraint
- `GET /api/constraint` - List all constraints
- `GET /api/constraint/{id}` - Get specific constraint

### Timetable Generation
- `POST /api/generate-timetable?section_id={id}` - Generate timetable for section

### Utilities
- `GET /api/health` - Health check
- `GET /api/stats` - Database statistics
- `POST /api/reset-db` - Reset database with sample data
- `POST /api/upload-config` - Upload JSON configuration

For interactive API testing, visit: http://localhost:8000/docs

## 📁 Project Structure

```
TIME-table/
├── timetable_generator/
│   ├── __init__.py          # Package initialization
│   ├── database.py          # SQLModel schemas & DB management
│   ├── algorithm.py         # CSP solver with constraint logic
│   ├── backend.py           # FastAPI REST API server
│   └── app.py               # Streamlit interactive UI
│
├── tests.py                 # Comprehensive test suite
├── startup.py               # Easy startup script
├── requirements.txt         # Python dependencies
├── config_sample.json       # Sample configuration
│
├── README.md                # This file
├── INDEX.md                 # Complete project index
├── QUICK_START.md           # 5-minute quick start guide
├── SETUP.md                 # Detailed setup & deployment
├── IMPLEMENTATION_SUMMARY.md # Technical implementation details
└── PROJECT_COMPLETION.md    # Project completion report
```

## 📚 Documentation

This project includes comprehensive documentation:

- **[README.md](README.md)** - This file, main overview
- **[INDEX.md](INDEX.md)** - Complete project navigation guide
- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[SETUP.md](SETUP.md)** - Detailed setup and configuration
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical architecture
- **[PROJECT_COMPLETION.md](PROJECT_COMPLETION.md)** - Quality assurance report

### Which Documentation to Read?

- **"I want to get started immediately"** → [QUICK_START.md](QUICK_START.md)
- **"I want the full overview"** → You're reading it! (README.md)
- **"I'm installing for the first time"** → [SETUP.md](SETUP.md)
- **"I need technical details"** → [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **"I need to navigate the codebase"** → [INDEX.md](INDEX.md)

## ⏰ Time Grid Reference

| Period | Time |
|--------|------|
| P1 | 08:45 - 09:45 |
| P2 | 09:45 - 10:45 |
| 🔴 BREAK | 10:45 - 11:05 |
| P3 | 11:05 - 12:05 |
| P4 | 12:05 - 01:05 |
| 🔴 LUNCH | 01:05 - 01:55 |
| P5 | 01:55 - 02:45 |
| 🔴 BREAK | 02:45 - 03:00 |
| P6 | 03:00 - 03:50 |
| P7 | 03:50 - 04:40 |

**Valid Lab Blocks**: (1,2), (3,4), (6,7) - 2 consecutive periods without breaks

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests.py -v

# Run with coverage
pip install pytest-cov
pytest tests.py --cov=timetable_generator
```

Tests include:
- Unit tests for algorithm components
- Integration tests for API endpoints
- Constraint validation tests
- Database model tests
- DataFrame generation tests

## 🔐 Security

- ✅ Input validation on all endpoints
- ✅ SQL injection prevention (ORM)
- ✅ CORS enabled for frontend
- ✅ Error messages don't leak sensitive info
- ✅ Environment variables for secrets
- ✅ No hardcoded credentials

## 🚀 Deployment

### Development
```bash
python -m uvicorn timetable_generator.backend:app --reload
streamlit run timetable_generator/app.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 timetable_generator.backend:app
```

### Docker
```bash
docker build -t mkce-timetable .
docker run -p 8000:8000 -p 8501:8501 mkce-timetable
```

See [SETUP.md](SETUP.md) for detailed deployment instructions including Heroku, AWS, and Azure.

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

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure:
- Code follows existing style conventions
- All tests pass
- New features include tests
- Documentation is updated

## 📝 License

This project is open source and available under the MIT License. See the LICENSE file for more details.

---

## 🎉 Ready to Use!

You now have a complete, production-ready timetable generator!

### Next Steps:
1. **Install**: `pip install -r requirements.txt`
2. **Run**: Start backend and frontend
3. **Initialize**: Reset database with sample data
4. **Generate**: Create your first timetable!

### Need Help?
- Quick questions → [QUICK_START.md](QUICK_START.md)
- Setup issues → [SETUP.md](SETUP.md)
- Technical details → [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- API docs → http://localhost:8000/docs

---

**Happy Scheduling!** 📅✨

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: January 2026