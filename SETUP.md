# 🚀 MKCE Timetable Generator - Setup & Configuration Guide

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Application](#running-the-application)
4. [Database Setup](#database-setup)
5. [API Testing](#api-testing)
6. [Troubleshooting](#troubleshooting)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/MuthuvelMukesh/TIME-table.git
cd TIME-table
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **fastapi** (REST API framework)
- **uvicorn** (ASGI server)
- **streamlit** (Web UI)
- **sqlmodel** (ORM)
- **pandas** (Data handling)
- **python-constraint** (CSP solver)
- **requests** (HTTP client)

---

## Configuration

### Directory Structure

```
TIME-table/
├── timetable_generator/
│   ├── __init__.py          # Package init
│   ├── database.py          # SQLModel schemas
│   ├── algorithm.py         # CSP solver logic
│   ├── backend.py           # FastAPI app
│   └── app.py               # Streamlit UI
├── config_sample.json       # Sample configuration
├── startup.py               # Easy startup script
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

### Database Configuration

The application uses SQLite by default. Configuration is in `database.py`:

```python
DATABASE_URL = "sqlite:///timetable.db"
```

**To use PostgreSQL (Production):**

1. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

2. Update `database.py`:
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/timetable_db"
```

### API Configuration

Backend API runs on `http://localhost:8000` by default.

To change port, modify in `backend.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

Or run with flag:
```bash
python -m uvicorn timetable_generator.backend:app --port 8001
```

### Frontend Configuration

Frontend UI runs on `http://localhost:8501` by default.

To change, create `.streamlit/config.toml`:
```toml
[server]
port = 8502
```

---

## Running the Application

### Option 1: Using Startup Script (Recommended)

```bash
python startup.py
```

Follow the prompts to start backend, frontend, or both.

### Option 2: Manual Startup

**Terminal 1 - Start Backend:**
```bash
python -m uvicorn timetable_generator.backend:app --reload
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run timetable_generator/app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.
  URL: http://localhost:8501
```

### Option 3: Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "startup.py"]
```

Build and run:
```bash
docker build -t mkce-timetable .
docker run -p 8000:8000 -p 8501:8501 mkce-timetable
```

---

## Database Setup

### Initialize with Sample Data

**Option A: Through Streamlit UI**
1. Open http://localhost:8501
2. Go to Settings tab
3. Click "Reset Database"

**Option B: Through Python Script**
```bash
python timetable_generator/database.py
```

**Option C: Through API**
```bash
curl -X POST http://localhost:8000/api/reset-db
```

### What Gets Initialized

Sample data includes:
- **4 Faculty Members** (3 IT + 1 Math)
- **2 Sections** (II Year IT A, II Year IT B)
- **5 Courses** (3 Theory + 2 Labs)
- **10 Constraints** (5 per section)

---

## API Testing

### Using Swagger UI (Built-in)

1. Navigate to: `http://localhost:8000/docs`
2. All endpoints are documented and testable
3. Try endpoints directly from browser

### Using cURL

**Get All Faculty:**
```bash
curl http://localhost:8000/api/faculty
```

**Create New Faculty:**
```bash
curl -X POST http://localhost:8000/api/faculty \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. New Faculty",
    "department": "IT",
    "specialization": "AI",
    "available_slots": {
      "Monday": [1,2,3,5,6,7],
      "Tuesday": [1,2,3,5,6,7],
      "Wednesday": [1,2,3,5,6,7],
      "Thursday": [1,2,3,5,6,7],
      "Friday": [1,2,3,5,6,7]
    },
    "is_external": false
  }'
```

**Generate Timetable:**
```bash
curl -X POST "http://localhost:8000/api/generate-timetable?section_id=1"
```

### Using Python Requests

```python
import requests
import json

API_URL = "http://localhost:8000/api"

# Get faculty
response = requests.get(f"{API_URL}/faculty")
print(response.json())

# Create course
payload = {
    "code": "IT305",
    "name": "Web Development",
    "course_type": "THEORY",
    "credits": 3,
    "weekly_hours": 3,
    "required_faculty_ids": [1]
}
response = requests.post(f"{API_URL}/course", json=payload)
print(response.json())

# Generate timetable
response = requests.post(f"{API_URL}/generate-timetable", params={"section_id": 1})
print(json.dumps(response.json(), indent=2))
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'timetable_generator'"

**Solution:**
- Ensure you're in the `TIME-table` directory
- Verify Python path includes current directory
- Try: `export PYTHONPATH=$PYTHONPATH:.` (Linux/Mac) or `set PYTHONPATH=%PYTHONPATH:%.` (Windows)

### Issue: "Connection refused" when accessing frontend

**Solution:**
- Ensure backend is running on port 8000
- Check firewall settings
- Verify API_BASE_URL in `app.py` matches your setup

### Issue: "Database is locked"

**Solution:**
```bash
# Delete the database file
rm timetable.db

# Reinitialize
python timetable_generator/database.py
```

### Issue: Port Already in Use

**Kill process on port 8000:**
```bash
# Linux/Mac
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "No feasible solution found"

**Solutions:**
1. Check faculty availability - ensure they have enough free slots
2. Verify course-faculty assignments are correct
3. Review constraint preferences
4. Temporarily disable soft constraints (preferred days)

### Issue: Streamlit app won't load

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with verbose logging
streamlit run timetable_generator/app.py --logger.level=debug
```

### Issue: CSP Solver too slow

**Solution:**
- Reduce number of courses
- Increase faculty availability
- Use fewer sections
- Optimize algorithm parameters in `algorithm.py`

---

## Performance Optimization

### For Large Datasets

1. **Increase timeouts in CSP solver:**
```python
# In algorithm.py
TIMEOUT = 60  # seconds
```

2. **Use database indexing:**
```python
# Add indexes in models
class Faculty(SQLModel, table=True):
    name: str = Field(index=True)
    department: str = Field(index=True)
```

3. **Cache results:**
```python
import functools
@functools.lru_cache(maxsize=10)
def get_faculty_data():
    # ...
```

4. **Parallel generation:**
```python
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(generate_timetable, section) 
               for section in sections]
```

---

## Production Deployment

### Using Gunicorn + Nginx

**1. Install Gunicorn:**
```bash
pip install gunicorn
```

**2. Run backend:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 timetable_generator.backend:app
```

**3. Nginx configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api {
        proxy_pass http://localhost:8000;
    }

    location / {
        proxy_pass http://localhost:8501;
    }
}
```

### Environment Variables

Create `.env` file:
```
DATABASE_URL=postgresql://user:pass@localhost/timetable
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=false
```

Load in code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run the application
3. ✅ Initialize database with sample data
4. ✅ Add your faculty and courses
5. ✅ Generate timetables
6. ✅ Download and export results

---

## Additional Resources

- **python-constraint**: https://github.com/python-constraint/python-constraint
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **SQLModel**: https://sqlmodel.tiangolo.com/

---

**Need Help?** Check the main README.md or API documentation at `/docs` endpoint.
