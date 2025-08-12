from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Course:
    course_code: str
    course_name: str
    credit_hrs: int

@dataclass
class Teacher:
    teacher_code: str
    teacher_name: str
    teacher_designation: str

@dataclass
class CourseAssignment:
    teacher_code: str
    course_code: str
    period: int
    program: str
    semester: int
    day: str

class Constants:
    PROGRAMS = ["BCA", "BIT", "B.Tech AI"]
    SEMESTERS = list(range(1, 9))  # 1 to 8
    DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    PERIODS = {
        1: "6:30 AM - 7:20 AM",
        2: "7:20 AM - 8:10 AM", 
        3: "8:10 AM - 9:00 AM",
        4: "9:10 AM - 10:00 AM",
        5: "10:00 AM - 10:50 AM",
        6: "10:50 AM - 11:40 AM"
    }
    
    @staticmethod
    def get_period_times() -> Dict[int, str]:
        return Constants.PERIODS
    
    @staticmethod
    def get_period_display(period: int) -> str:
        return f"Period {period}: {Constants.PERIODS.get(period, 'Unknown')}"
