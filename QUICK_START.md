# ⚡ MKCE Timetable Generator - 5-Minute Quick Start

## 🎯 Goal
Generate conflict-free timetables for college sections with multi-faculty labs.

---

## 📦 Prerequisites
- Python 3.8+
- pip

---

## 🚀 Step-by-Step Setup (5 minutes)

### 1️⃣ Install Dependencies (1 min)
```bash
cd TIME-table
pip install -r requirements.txt
```

### 2️⃣ Start Backend (Terminal 1)
```bash
python -m uvicorn timetable_generator.backend:app --reload
```
✅ Ready when you see: `Uvicorn running on http://127.0.0.1:8000`

### 3️⃣ Start Frontend (Terminal 2)
```bash
streamlit run timetable_generator/app.py
```
✅ Ready when browser opens at `http://localhost:8501`

### 4️⃣ Initialize Database
**In Streamlit UI:**
- Go to **Settings** tab
- Click **"Reset Database"**
- Loads sample faculty, courses, sections

### 5️⃣ Generate Timetable
**In Streamlit UI:**
- Go to **Generate Timetable** tab
- Select section: "II Year IT A"
- Click **"Generate Timetable"**
- View beautiful schedule with breaks marked!

---

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

---

## 📋 Key Features

- ✅ Multi-faculty lab scheduling
- ✅ Faculty availability constraints
- ✅ Lab block size validation (2 consecutive periods)
- ✅ No faculty clashes
- ✅ Multiple sections
- ✅ Interactive UI
- ✅ CSV export

---

## 🔌 API Quick Test

```bash
# Get all faculty
curl http://localhost:8000/api/faculty

# API Documentation
http://localhost:8000/docs
```

---

## 📚 More Documentation

- **README.md** - Full overview
- **SETUP.md** - Advanced setup
- **IMPLEMENTATION_SUMMARY.md** - Technical details

**You're ready! Start the backend and frontend, then go to http://localhost:8501** 🎉
