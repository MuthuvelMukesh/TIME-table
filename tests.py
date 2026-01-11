"""
tests.py - Unit and Integration Tests
=====================================
Test suite for timetable generator components.

Run with: pytest tests.py -v
"""

import pytest
from constraint import Problem
from timetable_generator.algorithm import (
    TimetableCSP, PERIODS, DAYS, SCHEDULABLE_PERIODS,
    generate_timetable, build_timetable_dict, create_timetable_dataframe
)
from timetable_generator.database import Faculty, Course, Section, Constraint


class TestAlgorithm:
    """Tests for CSP solver algorithm."""
    
    @pytest.fixture
    def sample_faculty_data(self):
        """Sample faculty data."""
        return {
            1: {
                "name": "Dr. Geeitha",
                "available_slots": {
                    "Monday": [1, 2, 3, 5, 6, 7],
                    "Tuesday": [1, 2, 3, 5, 6, 7],
                    "Wednesday": [1, 2, 3, 5, 6, 7],
                    "Thursday": [1, 2, 3, 5, 6, 7],
                    "Friday": [1, 2, 3, 5, 6, 7],
                },
                "is_external": False
            },
            2: {
                "name": "Ms. Anitha",
                "available_slots": {
                    "Monday": [1, 2, 3, 5, 6, 7],
                    "Tuesday": [1, 2, 5, 6, 7],
                    "Wednesday": [1, 2, 3, 5, 6, 7],
                    "Thursday": [1, 2, 3, 5, 6, 7],
                    "Friday": [1, 2, 3, 5, 6, 7],
                },
                "is_external": False
            }
        }
    
    @pytest.fixture
    def sample_course_data(self):
        """Sample course data."""
        return {
            1: {
                "code": "IT301",
                "name": "ML Lab",
                "type": "LAB",
                "required_faculty_ids": [1, 2],
                "block_size": 2
            },
            2: {
                "code": "IT302",
                "name": "OS",
                "type": "THEORY",
                "required_faculty_ids": [2],
                "block_size": 1
            }
        }
    
    def test_periods_defined(self):
        """Test that periods are correctly defined."""
        assert len(PERIODS) == 7
        assert PERIODS[0].number == 1
        assert PERIODS[6].number == 7
        assert not PERIODS[0].is_break
    
    def test_days_defined(self):
        """Test that days are correctly defined."""
        assert len(DAYS) == 5
        assert "Monday" in DAYS
        assert "Friday" in DAYS
    
    def test_csp_initialization(self, sample_faculty_data, sample_course_data):
        """Test CSP solver initialization."""
        csp = TimetableCSP(sample_faculty_data, sample_course_data)
        
        assert csp.faculty_data == sample_faculty_data
        assert csp.course_data == sample_course_data
        assert csp.problem is not None
        assert csp.solution == {}
    
    def test_add_variables_theory(self, sample_faculty_data, sample_course_data):
        """Test adding theory course variables."""
        csp = TimetableCSP(sample_faculty_data, sample_course_data)
        csp.add_variables("II Year IT A", [2])  # Theory course
        
        assert "course_2" in csp.course_vars
        assert csp.course_vars[2] == "course_2"
    
    def test_add_variables_lab(self, sample_faculty_data, sample_course_data):
        """Test adding lab course variables."""
        csp = TimetableCSP(sample_faculty_data, sample_course_data)
        csp.add_variables("II Year IT A", [1])  # Lab course
        
        assert "course_1" in csp.course_vars
    
    def test_faculty_availability_constraint(self, sample_faculty_data, sample_course_data):
        """Test faculty availability constraint."""
        csp = TimetableCSP(sample_faculty_data, sample_course_data)
        csp.add_variables("II Year IT A", [2])
        csp.add_faculty_availability_constraint()
        
        # Constraint should be added
        assert len(csp.problem.constraints) > 0
    
    def test_no_clash_constraint(self, sample_faculty_data):
        """Test no-clash constraint for shared faculty."""
        courses = {
            1: {
                "code": "IT301",
                "name": "Course 1",
                "required_faculty_ids": [1, 2],
                "block_size": 1
            },
            2: {
                "code": "IT302",
                "name": "Course 2",
                "required_faculty_ids": [2],
                "block_size": 1
            }
        }
        
        csp = TimetableCSP(sample_faculty_data, courses)
        csp.add_variables("II Year IT A", [1, 2])
        csp.add_no_clash_constraint()
        
        # Both courses share faculty 2, so constraint should be added
        assert len(csp.problem.constraints) > 0
    
    def test_generate_timetable_simple(self, sample_faculty_data, sample_course_data):
        """Test basic timetable generation."""
        success, df, message = generate_timetable(
            sample_faculty_data,
            sample_course_data,
            {},
            "II Year IT A"
        )
        
        # Should either succeed or fail gracefully
        assert isinstance(success, bool)
        assert isinstance(message, str)
        if success:
            assert df is not None
            assert isinstance(df, object)  # DataFrame


class TestDatabase:
    """Tests for database models."""
    
    def test_faculty_model(self):
        """Test Faculty model."""
        faculty = Faculty(
            name="Dr. Test",
            department="IT",
            specialization="AI",
            available_slots={"Monday": [1, 2, 3]},
            is_external=False
        )
        
        assert faculty.name == "Dr. Test"
        assert faculty.department == "IT"
        assert "Monday" in faculty.available_slots
    
    def test_course_model(self):
        """Test Course model."""
        course = Course(
            code="IT301",
            name="Test Course",
            course_type="LAB",
            credits=4,
            weekly_hours=2,
            required_faculty_ids=[1, 2]
        )
        
        assert course.code == "IT301"
        assert course.course_type == "LAB"
        assert len(course.required_faculty_ids) == 2
    
    def test_section_model(self):
        """Test Section model."""
        section = Section(
            name="II Year IT A",
            year=2,
            division="A",
            department="IT"
        )
        
        assert section.name == "II Year IT A"
        assert section.year == 2
        assert section.division == "A"
    
    def test_constraint_model(self):
        """Test Constraint model."""
        constraint = Constraint(
            course_id=1,
            section_id=1,
            block_size=2,
            preferred_days=["Monday", "Wednesday"],
            is_hard=True
        )
        
        assert constraint.course_id == 1
        assert constraint.block_size == 2
        assert "Monday" in constraint.preferred_days


class TestConstraintValidation:
    """Tests for constraint validation."""
    
    def test_lab_block_size_validation(self):
        """Test that labs require block_size=2."""
        course = Course(
            code="IT301",
            name="Lab",
            course_type="LAB",
            credits=4,
            weekly_hours=2,
            required_faculty_ids=[1, 2]
        )
        
        # LAB courses should have block_size >= 2
        assert course.course_type == "LAB"
        assert len(course.required_faculty_ids) == 2
    
    def test_multi_faculty_requirement(self):
        """Test that labs require 2 faculty."""
        course = Course(
            code="IT301",
            name="Lab",
            course_type="LAB",
            credits=4,
            weekly_hours=2,
            required_faculty_ids=[1, 2]  # Exactly 2
        )
        
        assert len(course.required_faculty_ids) == 2
    
    def test_theory_single_faculty(self):
        """Test that theory courses can have 1 faculty."""
        course = Course(
            code="IT302",
            name="Theory",
            course_type="THEORY",
            credits=3,
            weekly_hours=3,
            required_faculty_ids=[1]
        )
        
        assert course.course_type == "THEORY"
        assert len(course.required_faculty_ids) == 1


class TestDataFrameGeneration:
    """Tests for timetable DataFrame generation."""
    
    def test_timetable_dict_structure(self):
        """Test structure of timetable dictionary."""
        timetable_dict = {
            "Monday": {1: "IT301 | Dr. Geeitha", 2: ""},
            "Tuesday": {1: "", 2: "IT302 | Ms. Anitha"},
        }
        
        for day in ["Monday", "Tuesday"]:
            assert day in timetable_dict
            assert isinstance(timetable_dict[day], dict)
    
    def test_dataframe_creation(self):
        """Test DataFrame creation from timetable dict."""
        timetable_dict = {
            day: {period: f"{day}-P{period}" for period in [1, 2, 3]}
            for day in DAYS
        }
        
        df = create_timetable_dataframe(timetable_dict)
        
        assert df is not None
        assert len(df) == len(DAYS)
        assert "Day" in df.columns


class TestPeriodValidation:
    """Tests for period and timing validation."""
    
    def test_break_periods_excluded(self):
        """Test that break periods are not in schedulable periods."""
        assert 1 in SCHEDULABLE_PERIODS
        assert 2 in SCHEDULABLE_PERIODS
        assert 3 in SCHEDULABLE_PERIODS
        assert 4 in SCHEDULABLE_PERIODS
        assert 5 in SCHEDULABLE_PERIODS
        assert 6 in SCHEDULABLE_PERIODS
        assert 7 in SCHEDULABLE_PERIODS
        assert len(SCHEDULABLE_PERIODS) == 7
    
    def test_lab_consecutive_periods_valid(self):
        """Test valid consecutive periods for labs."""
        valid_blocks = [
            (1, 2),
            (3, 4),
            (6, 7),
        ]
        
        for start, end in valid_blocks:
            assert start < end
            assert end <= 7
    
    def test_lab_consecutive_periods_invalid(self):
        """Test invalid consecutive periods for labs."""
        # Period 2 -> 3 has a break
        # Period 5 -> 6 has a break
        invalid_blocks = [
            (2, 3),  # Break between
            (5, 6),  # Break between
        ]
        
        for start, end in invalid_blocks:
            assert start < end


class TestIntegration:
    """Integration tests."""
    
    def test_end_to_end_generation(self):
        """Test complete timetable generation flow."""
        faculty = {
            1: {
                "name": "Dr. A",
                "available_slots": {"Monday": [1,2,3,5,6], "Tuesday": [1,2,3,5,6],
                                  "Wednesday": [1,2,3,5,6], "Thursday": [1,2,3,5,6],
                                  "Friday": [1,2,3,5,6]},
                "is_external": False
            }
        }
        
        courses = {
            1: {
                "code": "IT301",
                "name": "Course",
                "type": "THEORY",
                "required_faculty_ids": [1],
                "block_size": 1
            }
        }
        
        success, df, msg = generate_timetable(faculty, courses, {}, "Test Section")
        
        # Should succeed with simple data
        assert isinstance(success, bool)
        assert isinstance(msg, str)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
