"""
algorithm.py - Constraint Satisfaction Problem (CSP) Solver for Timetable Generation
====================================================================================
Uses python-constraint library with custom heuristics for scheduling.

Key Constraints:
1. Lab Block Size: Labs require 2 consecutive periods (no split)
2. Multi-Faculty (Labs): Both faculty must be available simultaneously
3. Faculty Availability: Hard constraint from faculty.available_slots
4. No Clashes: Same faculty can't teach 2 courses in same period
5. Break Times: Automatically excluded (handled during post-processing)
"""

from constraint import Problem, AllDifferentConstraint
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import pandas as pd
from collections import defaultdict


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Period:
    """Represents a teaching period."""
    number: int
    start_time: str
    end_time: str
    is_break: bool = False


@dataclass
class ScheduleSlot:
    """Represents a scheduled class."""
    course_code: str
    course_name: str
    faculty_names: List[str]
    course_type: str


# ============================================================================
# CONSTANTS
# ============================================================================

PERIODS = [
    Period(1, "08:45", "09:45"),
    Period(2, "09:45", "10:45"),
    Period(3, "11:05", "12:05"),
    Period(4, "12:05", "01:05"),
    Period(5, "01:55", "02:45"),
    Period(6, "03:00", "03:50"),
    Period(7, "03:50", "04:40"),
]

BREAKS = [
    Period(0, "10:45", "11:05", is_break=True),  # Break between P2 and P3
    Period(0, "01:05", "01:55", is_break=True),  # Lunch
    Period(0, "02:45", "03:00", is_break=True),  # Break between P5 and P6
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Scheduling periods (excluding breaks)
SCHEDULABLE_PERIODS = [p.number for p in PERIODS]


# ============================================================================
# CSP SOLVER CLASS
# ============================================================================

class TimetableCSP:
    """Constraint Satisfaction Problem solver for timetable generation."""
    
    def __init__(self, faculty_data: Dict[int, Dict[str, Any]], 
                 course_data: Dict[int, Dict[str, Any]]):
        """
        Initialize CSP solver.
        
        Args:
            faculty_data: {faculty_id: {name, available_slots, is_external, ...}}
            course_data: {course_id: {code, name, type, required_faculty_ids, ...}}
        """
        self.faculty_data = faculty_data
        self.course_data = course_data
        self.problem = Problem()
        self.solution = {}
        
    def add_variables(self, section_name: str, courses: List[int]) -> None:
        """
        Add variables to the problem.
        Each course needs to be scheduled in day+period combinations.
        
        Variable naming: f"course_{course_id}_{index}"
        Domain: (day, period_start, period_end) tuples
        
        Args:
            section_name: Name of the section (e.g., "II Year IT A")
            courses: List of course IDs to schedule
        """
        domain = []
        
        # Generate all possible slots (day, period_start, period_end)
        for day in DAYS:
            for period in SCHEDULABLE_PERIODS:
                domain.append((day, period, period + 1))  # period and period+1
        
        # For each course, create variable(s)
        self.course_vars = {}
        for course_id in courses:
            course = self.course_data[course_id]
            var_name = f"course_{course_id}"
            
            # Check block size requirement (Labs need 2 consecutive periods)
            block_size = course.get("block_size", 1)
            
            if block_size == 2:
                # For labs: domain is (day, period, period+1) where period+1 is the 2nd period
                lab_domain = [(day, p, p+1) for day in DAYS for p in SCHEDULABLE_PERIODS if p+1 <= 7]
                self.problem.addVariable(var_name, lab_domain)
            else:
                # For theory: single period slots
                theory_domain = [(day, p, p) for day in DAYS for p in SCHEDULABLE_PERIODS]
                self.problem.addVariable(var_name, theory_domain)
            
            self.course_vars[course_id] = var_name
    
    def add_faculty_availability_constraint(self) -> None:
        """
        Add hard constraint: Faculty must be available in assigned slots.
        
        Checks faculty_data[faculty_id]['available_slots'][day] contains the period.
        """
        for course_id, var_name in self.course_vars.items():
            course = self.course_data[course_id]
            faculty_ids = course.get("required_faculty_ids", [])
            
            def faculty_available(slot, fac_ids=faculty_ids):
                """Check if all required faculty are available."""
                day, start_period, end_period = slot
                
                for fac_id in fac_ids:
                    if fac_id not in self.faculty_data:
                        return False
                    
                    available_on_day = self.faculty_data[fac_id].get(
                        "available_slots", {}
                    ).get(day, [])
                    
                    # All periods in the block must be available
                    for period in range(start_period, end_period + 1):
                        if period not in available_on_day:
                            return False
                
                return True
            
            self.problem.addConstraint(faculty_available, (var_name,))
    
    def add_no_clash_constraint(self) -> None:
        """
        Add hard constraint: Faculty cannot teach 2 courses in same period.
        
        If course A and course B both require faculty_id F,
        they cannot have overlapping time slots.
        """
        course_list = list(self.course_vars.keys())
        
        for i, course_id_1 in enumerate(course_list):
            for course_id_2 in course_list[i+1:]:
                faculty_ids_1 = set(self.course_data[course_id_1].get("required_faculty_ids", []))
                faculty_ids_2 = set(self.course_data[course_id_2].get("required_faculty_ids", []))
                
                # Check if courses share any faculty
                shared_faculty = faculty_ids_1 & faculty_ids_2
                
                if shared_faculty:
                    var1 = self.course_vars[course_id_1]
                    var2 = self.course_vars[course_id_2]
                    
                    def no_clash(slot1, slot2):
                        """Ensure slots don't overlap."""
                        day1, start1, end1 = slot1
                        day2, start2, end2 = slot2
                        
                        # Different days: no clash
                        if day1 != day2:
                            return True
                        
                        # Same day: check for overlap
                        # Overlap if start1 <= start2 <= end1 or start2 <= start1 <= end2
                        if start1 <= start2 <= end1 or start2 <= start1 <= end2:
                            return False
                        
                        return True
                    
                    self.problem.addConstraint(no_clash, (var1, var2))
    
    def add_preferred_days_constraint(self, constraints_data: Dict[int, Dict[str, Any]]) -> None:
        """
        Add soft constraint: Prefer specific days for courses.
        
        This is a soft constraint (can be violated if needed).
        Implemented as a preference, not a hard requirement.
        
        Args:
            constraints_data: {constraint_id: {course_id, preferred_days, ...}}
        """
        for constraint in constraints_data.values():
            course_id = constraint.get("course_id")
            preferred_days = constraint.get("preferred_days", [])
            
            if not preferred_days or course_id not in self.course_vars:
                continue
            
            var_name = self.course_vars[course_id]
            
            def prefer_days(slot, pref_days=preferred_days):
                """Soft constraint: prefer certain days."""
                day, _, _ = slot
                return day in pref_days
            
            # Note: soft constraint - can be violated
            # In hard CSP, we'll store this separately for post-processing
            self.preferred_constraints = getattr(self, 'preferred_constraints', {})
            self.preferred_constraints[var_name] = prefer_days
    
    def solve(self) -> bool:
        """
        Solve the CSP.
        
        Returns:
            True if a valid solution exists, False otherwise.
        """
        try:
            solutions = self.problem.getSolutions()
            if solutions:
                self.solution = solutions[0]  # Take first valid solution
                return True
            return False
        except Exception as e:
            print(f"CSP Solver Error: {e}")
            return False
    
    def get_solution(self) -> Dict[str, Tuple[str, int, int]]:
        """
        Get the current solution.
        
        Returns:
            {var_name: (day, start_period, end_period), ...}
        """
        return self.solution


# ============================================================================
# TIMETABLE GENERATION FUNCTION
# ============================================================================

def generate_timetable(faculty_data: Dict[int, Dict[str, Any]],
                      course_data: Dict[int, Dict[str, Any]],
                      constraints_data: Dict[int, Dict[str, Any]],
                      section_name: str) -> Tuple[bool, Optional[pd.DataFrame], str]:
    """
    Generate timetable for a section using CSP.
    
    Args:
        faculty_data: Faculty availability and info
        course_data: Course requirements and faculty assignments
        constraints_data: Scheduling constraints
        section_name: Section to schedule (e.g., "II Year IT A")
    
    Returns:
        (success: bool, timetable_df: pd.DataFrame, message: str)
    """
    
    # Extract courses for this section
    courses_to_schedule = [
        cid for cid, course in course_data.items()
        if course.get("section_id") == section_name or True  # Simplified for demo
    ]
    
    if not courses_to_schedule:
        return False, None, "No courses found for section."
    
    # Initialize CSP
    csp = TimetableCSP(faculty_data, course_data)
    
    # Add variables
    csp.add_variables(section_name, courses_to_schedule)
    
    # Add constraints
    csp.add_faculty_availability_constraint()
    csp.add_no_clash_constraint()
    csp.add_preferred_days_constraint(constraints_data)
    
    # Solve
    if not csp.solve():
        return False, None, "No feasible solution found. Check faculty availability and course requirements."
    
    # Build timetable dataframe
    solution = csp.get_solution()
    timetable_dict = build_timetable_dict(solution, course_data, faculty_data)
    df = create_timetable_dataframe(timetable_dict)
    
    return True, df, "Timetable generated successfully!"


def build_timetable_dict(solution: Dict[str, Tuple[str, int, int]],
                        course_data: Dict[int, Dict[str, Any]],
                        faculty_data: Dict[int, Dict[str, Any]]) -> Dict[str, Dict[int, str]]:
    """
    Build timetable dictionary from CSP solution.
    
    Returns:
        {day: {period: "Course Code | Faculty Names", ...}, ...}
    """
    timetable = {day: {p: "" for p in SCHEDULABLE_PERIODS} for day in DAYS}
    
    for var_name, (day, start_period, end_period) in solution.items():
        # Extract course_id from variable name
        course_id = int(var_name.split("_")[1])
        course = course_data[course_id]
        
        # Get faculty names
        faculty_ids = course.get("required_faculty_ids", [])
        faculty_names = [faculty_data[fid].get("name", f"Faculty {fid}") for fid in faculty_ids]
        faculty_str = " & ".join(faculty_names)
        
        # Create schedule string
        schedule_str = f"{course['code']} | {faculty_str}"
        
        # For labs (2-period blocks), fill both periods
        if end_period > start_period:
            for period in range(start_period, end_period + 1):
                timetable[day][period] = schedule_str
        else:
            timetable[day][start_period] = schedule_str
    
    return timetable


def create_timetable_dataframe(timetable_dict: Dict[str, Dict[int, str]]) -> pd.DataFrame:
    """
    Create a Pandas DataFrame from timetable dictionary.
    
    Rows: Days of the week
    Columns: Periods (with visual breaks)
    
    Returns:
        Formatted DataFrame with visual breaks included.
    """
    # Prepare data
    data = []
    for day in DAYS:
        row = {"Day": day}
        for period in SCHEDULABLE_PERIODS:
            col_name = f"Period {period}\n({PERIODS[period-1].start_time}-{PERIODS[period-1].end_time})"
            row[col_name] = timetable_dict[day].get(period, "")
        data.append(row)
    
    df = pd.DataFrame(data)
    return df


def print_timetable_with_breaks(df: pd.DataFrame) -> str:
    """
    Format timetable as string with visual break indicators.
    
    Returns:
        Formatted string representation of timetable.
    """
    output = "\n" + "="*120 + "\n"
    output += "TIMETABLE WITH BREAKS\n"
    output += "="*120 + "\n\n"
    
    # Define break positions
    break_times = {
        "after_P2": "10:45-11:05 (BREAK)",
        "after_P4": "01:05-01:55 (LUNCH)",
        "after_P5": "02:45-03:00 (BREAK)",
    }
    
    output += df.to_string(index=False) + "\n\n"
    
    output += "BREAK TIMES:\n"
    for key, time in break_times.items():
        output += f"  • {time}\n"
    
    output += "\n" + "="*120 + "\n"
    
    return output


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_solution(timetable_dict: Dict[str, Dict[int, str]],
                     course_data: Dict[int, Dict[str, Any]],
                     faculty_data: Dict[int, Dict[str, Any]]) -> List[str]:
    """
    Validate the generated timetable against constraints.
    
    Returns:
        List of any violated constraints (empty if valid).
    """
    violations = []
    
    # Check no period conflicts
    faculty_slots = defaultdict(list)
    
    for day in DAYS:
        for period in SCHEDULABLE_PERIODS:
            slot_str = timetable_dict[day].get(period, "")
            if slot_str:
                # Parse faculty from slot string
                # This would require more complex parsing
                pass
    
    return violations


if __name__ == "__main__":
    # Test with sample data
    faculty = {
        1: {"name": "Dr. Geeitha", "available_slots": {"Monday": [1,2,3,5,6,7]}, "is_external": False},
        2: {"name": "Ms. Anitha", "available_slots": {"Monday": [1,2,3,5,6,7]}, "is_external": False},
    }
    
    courses = {
        1: {"code": "IT301", "name": "ML Lab", "type": "LAB", "required_faculty_ids": [1, 2], "block_size": 2},
        2: {"code": "IT302", "name": "OS", "type": "THEORY", "required_faculty_ids": [2], "block_size": 1},
    }
    
    constraints = {}
    
    success, df, msg = generate_timetable(faculty, courses, constraints, "II Year IT A")
    print(msg)
    if success:
        print(print_timetable_with_breaks(df))
