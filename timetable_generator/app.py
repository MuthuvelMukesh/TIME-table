"""
app.py - Streamlit Frontend for Timetable Generator
===================================================
Interactive UI for managing faculty, courses, and generating timetables.

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import plotly.graph_objects as go


# ============================================================================
# STREAMLIT CONFIG
# ============================================================================

st.set_page_config(
    page_title="MKCE Timetable Generator",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = "http://localhost:8000/api"

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .section-header {
        color: #2ca02c;
        border-bottom: 2px solid #2ca02c;
        padding-bottom: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    .timetable-container {
        margin-top: 20px;
        padding: 15px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
    .stats-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-message {
        color: #27ae60;
        font-weight: bold;
    }
    .error-message {
        color: #e74c3c;
        font-weight: bold;
    }
    .break-indicator {
        background-color: #fff3cd;
        padding: 8px;
        border-radius: 3px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_api_health():
    """Check if FastAPI backend is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def fetch_faculty():
    """Fetch all faculty from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/faculty")
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    except Exception as e:
        st.error(f"Error fetching faculty: {e}")
        return []


def fetch_courses():
    """Fetch all courses from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/course")
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    except Exception as e:
        st.error(f"Error fetching courses: {e}")
        return []


def fetch_sections():
    """Fetch all sections from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/section")
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    except Exception as e:
        st.error(f"Error fetching sections: {e}")
        return []


def fetch_stats():
    """Fetch database statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return {}


def create_faculty(name: str, department: str, specialization: str, 
                  available_slots: Dict[str, List[int]], is_external: bool):
    """Create a new faculty member via API."""
    try:
        payload = {
            "name": name,
            "department": department,
            "specialization": specialization,
            "available_slots": available_slots,
            "is_external": is_external
        }
        response = requests.post(f"{API_BASE_URL}/faculty", json=payload)
        if response.status_code == 200:
            return True, response.json().get("id")
        else:
            return False, response.json().get("detail", "Unknown error")
    except Exception as e:
        return False, str(e)


def create_course(code: str, name: str, course_type: str, credits: int,
                 weekly_hours: int, required_faculty_ids: List[int]):
    """Create a new course via API."""
    try:
        payload = {
            "code": code,
            "name": name,
            "course_type": course_type,
            "credits": credits,
            "weekly_hours": weekly_hours,
            "required_faculty_ids": required_faculty_ids
        }
        response = requests.post(f"{API_BASE_URL}/course", json=payload)
        if response.status_code == 200:
            return True, response.json().get("id")
        else:
            return False, response.json().get("detail", "Unknown error")
    except Exception as e:
        return False, str(e)


def create_section(name: str, year: int, division: str, department: str):
    """Create a new section via API."""
    try:
        payload = {
            "name": name,
            "year": year,
            "division": division,
            "department": department
        }
        response = requests.post(f"{API_BASE_URL}/section", json=payload)
        if response.status_code == 200:
            return True, response.json().get("id")
        else:
            return False, response.json().get("detail", "Unknown error")
    except Exception as e:
        return False, str(e)


def generate_timetable(section_id: int):
    """Generate timetable for a section."""
    try:
        response = requests.post(f"{API_BASE_URL}/generate-timetable", params={"section_id": section_id})
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get("detail", "Unknown error")
    except Exception as e:
        return False, str(e)


def format_timetable_for_display(timetable_data: List[Dict]) -> pd.DataFrame:
    """Format timetable data for display."""
    return pd.DataFrame(timetable_data)


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown("<h1 class='main-title'>📅 MKCE IT Department - Timetable Generator</h1>", 
                unsafe_allow_html=True)
    
    # Check API connection
    if not check_api_health():
        st.error("❌ FastAPI backend is not running. Please start it with: python -m uvicorn timetable_generator.backend:app --reload")
        st.info("Backend should be running on http://localhost:8000")
        return
    
    st.success("✅ Connected to backend API")
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Dashboard", "Manage Faculty", "Manage Courses", "Manage Sections", "Generate Timetable", "Settings"]
    )
    
    # ========================================================================
    # DASHBOARD PAGE
    # ========================================================================
    if page == "Dashboard":
        st.markdown("<h2 class='section-header'>Dashboard</h2>", unsafe_allow_html=True)
        
        stats = fetch_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Faculty", stats.get("faculty", 0))
        with col2:
            st.metric("📚 Courses", stats.get("courses", 0))
        with col3:
            st.metric("🎓 Sections", stats.get("sections", 0))
        with col4:
            st.metric("⚙️ Constraints", stats.get("constraints", 0))
        
        st.markdown("---")
        
        # Quick Stats
        st.subheader("System Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Time Grid Configuration:**")
            time_grid = {
                "Period 1": "08:45 - 09:45",
                "Period 2": "09:45 - 10:45",
                "🔴 Break": "10:45 - 11:05",
                "Period 3": "11:05 - 12:05",
                "Period 4": "12:05 - 01:05",
                "🔴 Lunch": "01:05 - 01:55",
                "Period 5": "01:55 - 02:45",
                "🔴 Break": "02:45 - 03:00",
                "Period 6": "03:00 - 03:50",
                "Period 7": "03:50 - 04:40",
            }
            for period, time in time_grid.items():
                st.text(f"{period:15} : {time}")
        
        with col2:
            st.write("**Key Constraints:**")
            constraints_info = [
                "• Lab Block Size: 2 consecutive periods",
                "• Multi-Faculty: Labs require 2 faculty simultaneously",
                "• No Faculty Clash: Same faculty can't teach 2 courses",
                "• Faculty Availability: Hard constraint",
                "• External Constraints: Math/Placement shared globally",
                "• Sectioning: Distinct schedules per section"
            ]
            for constraint in constraints_info:
                st.text(constraint)
    
    # ========================================================================
    # MANAGE FACULTY PAGE
    # ========================================================================
    elif page == "Manage Faculty":
        st.markdown("<h2 class='section-header'>Faculty Management</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["View Faculty", "Add Faculty"])
        
        with tab1:
            st.subheader("Existing Faculty")
            faculty = fetch_faculty()
            
            if faculty:
                faculty_df = pd.DataFrame(faculty)
                # Display as table
                st.dataframe(faculty_df, use_container_width=True, hide_index=True)
            else:
                st.info("No faculty members found. Add one using the 'Add Faculty' tab.")
        
        with tab2:
            st.subheader("Add New Faculty Member")
            
            with st.form("add_faculty_form"):
                name = st.text_input("Name", placeholder="Dr. S. Geeitha")
                department = st.text_input("Department", placeholder="IT")
                specialization = st.text_input("Specialization", placeholder="AI/ML")
                is_external = st.checkbox("External (Shared with other depts)", value=False)
                
                st.write("**Available Slots (Select periods for each day)**")
                
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                periods = [1, 2, 3, 4, 5, 6, 7]
                available_slots = {}
                
                for day in days:
                    available = st.multiselect(
                        f"{day}",
                        periods,
                        default=periods,
                        key=f"periods_{day}"
                    )
                    available_slots[day] = available
                
                if st.form_submit_button("Add Faculty", use_container_width=True):
                    if name and department and specialization:
                        success, result = create_faculty(
                            name, department, specialization,
                            available_slots, is_external
                        )
                        if success:
                            st.success(f"✅ Faculty '{name}' added successfully! (ID: {result})")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result}")
                    else:
                        st.error("Please fill all required fields")
    
    # ========================================================================
    # MANAGE COURSES PAGE
    # ========================================================================
    elif page == "Manage Courses":
        st.markdown("<h2 class='section-header'>Course Management</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["View Courses", "Add Course"])
        
        with tab1:
            st.subheader("Existing Courses")
            courses = fetch_courses()
            
            if courses:
                courses_df = pd.DataFrame(courses)
                st.dataframe(courses_df, use_container_width=True, hide_index=True)
            else:
                st.info("No courses found. Add one using the 'Add Course' tab.")
        
        with tab2:
            st.subheader("Add New Course")
            
            faculty = fetch_faculty()
            faculty_options = {f["name"]: f["id"] for f in faculty}
            
            with st.form("add_course_form"):
                code = st.text_input("Course Code", placeholder="IT301")
                name = st.text_input("Course Name", placeholder="Machine Learning Lab")
                course_type = st.selectbox("Course Type", ["THEORY", "LAB"])
                credits = st.number_input("Credits", min_value=1, max_value=4, value=3)
                weekly_hours = st.number_input("Weekly Hours", min_value=1, max_value=4, value=3)
                
                required_faculty = st.multiselect(
                    "Required Faculty",
                    list(faculty_options.keys()),
                    help="For LABs: Select 2 faculty members"
                )
                required_faculty_ids = [faculty_options[name] for name in required_faculty]
                
                if st.form_submit_button("Add Course", use_container_width=True):
                    if code and name and required_faculty_ids:
                        if course_type == "LAB" and len(required_faculty_ids) != 2:
                            st.error("⚠️ LAB courses must have exactly 2 faculty members")
                        else:
                            success, result = create_course(
                                code, name, course_type, credits,
                                weekly_hours, required_faculty_ids
                            )
                            if success:
                                st.success(f"✅ Course '{code}' added successfully! (ID: {result})")
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {result}")
                    else:
                        st.error("Please fill all required fields")
    
    # ========================================================================
    # MANAGE SECTIONS PAGE
    # ========================================================================
    elif page == "Manage Sections":
        st.markdown("<h2 class='section-header'>Section Management</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["View Sections", "Add Section"])
        
        with tab1:
            st.subheader("Existing Sections")
            sections = fetch_sections()
            
            if sections:
                sections_df = pd.DataFrame(sections)
                st.dataframe(sections_df, use_container_width=True, hide_index=True)
            else:
                st.info("No sections found. Add one using the 'Add Section' tab.")
        
        with tab2:
            st.subheader("Add New Section")
            
            with st.form("add_section_form"):
                year = st.number_input("Academic Year", min_value=1, max_value=4, value=2)
                division = st.selectbox("Division", ["A", "B", "C"])
                department = st.text_input("Department Code", placeholder="IT", value="IT")
                name = st.text_input(
                    "Section Name",
                    value=f"Year {year} {department} {division}",
                    placeholder="II Year IT A"
                )
                
                if st.form_submit_button("Add Section", use_container_width=True):
                    if name and department:
                        success, result = create_section(name, year, division, department)
                        if success:
                            st.success(f"✅ Section '{name}' added successfully! (ID: {result})")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result}")
                    else:
                        st.error("Please fill all required fields")
    
    # ========================================================================
    # GENERATE TIMETABLE PAGE
    # ========================================================================
    elif page == "Generate Timetable":
        st.markdown("<h2 class='section-header'>Generate Timetable</h2>", unsafe_allow_html=True)
        
        sections = fetch_sections()
        
        if not sections:
            st.warning("⚠️ No sections found. Please create at least one section before generating timetable.")
        else:
            section_options = {s["name"]: s["id"] for s in sections}
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_section = st.selectbox("Select Section", list(section_options.keys()))
            
            with col2:
                st.write("")
                generate_btn = st.button("🔄 Generate Timetable", use_container_width=True, type="primary")
            
            if generate_btn:
                with st.spinner("Generating timetable... This may take a moment..."):
                    section_id = section_options[selected_section]
                    success, result = generate_timetable(section_id)
                    
                    if success:
                        st.success("✅ Timetable generated successfully!")
                        
                        # Display timetable
                        st.markdown("<div class='timetable-container'>", unsafe_allow_html=True)
                        
                        # Create colorful dataframe display
                        timetable_df = format_timetable_for_display(result["timetable"])
                        
                        st.subheader(f"📅 Timetable for {result['section']}")
                        
                        # Display with styling
                        st.dataframe(timetable_df, use_container_width=True, hide_index=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Break times info
                        st.markdown("<div class='break-indicator'>", unsafe_allow_html=True)
                        st.markdown("""
                        **🔴 Break Times:**
                        - **10:45 - 11:05** (Between Period 2 & 3)
                        - **01:05 - 01:55** (Lunch Break)
                        - **02:45 - 03:00** (Between Period 5 & 6)
                        """)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Download option
                        csv_data = timetable_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv_data,
                            file_name=f"timetable_{selected_section.replace(' ', '_')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error(f"❌ Error generating timetable: {result}")
                        st.info("💡 Tip: Make sure all faculty members and courses are properly configured with available slots and requirements.")
    
    # ========================================================================
    # SETTINGS PAGE
    # ========================================================================
    elif page == "Settings":
        st.markdown("<h2 class='section-header'>Settings & Administration</h2>", unsafe_allow_html=True)
        
        st.write("**Database Management**")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🔄 Reset Database", use_container_width=True, help="⚠️ This will delete all data and initialize with samples!"):
                with st.spinner("Resetting database..."):
                    try:
                        response = requests.post(f"{API_BASE_URL}/reset-db")
                        if response.status_code == 200:
                            st.success("✅ Database reset successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {response.json().get('detail')}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        with col2:
            st.write("Reset the database and initialize with sample faculty, courses, and constraints.")
        
        st.markdown("---")
        
        st.write("**API Configuration**")
        st.code(f"API Base URL: {API_BASE_URL}", language="bash")
        
        st.write("**Timetable Algorithm Configuration**")
        config_info = """
        - **Solver**: python-constraint with custom heuristics
        - **Hard Constraints**:
          1. Faculty availability (from available_slots)
          2. Lab block size (2 consecutive periods)
          3. No faculty clashes (same faculty can't teach 2 courses)
          4. Multi-faculty availability for labs
        - **Soft Constraints**:
          1. Preferred days for courses
        """
        st.markdown(config_info)


if __name__ == "__main__":
    main()
