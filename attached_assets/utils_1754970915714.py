import pandas as pd
from typing import Dict, List, Any
from models import Constants

def create_empty_routine_dataframe() -> pd.DataFrame:
    """Create an empty routine dataframe structure"""
    periods = list(Constants.PERIODS.keys())
    days = Constants.DAYS
    
    # Create a multi-index dataframe
    data = []
    for day in days:
        row = {"Day": day}
        for period in periods:
            row[f"Period {period}"] = ""
        data.append(row)
    
    return pd.DataFrame(data)

def format_routine_for_display(routine_df: pd.DataFrame) -> pd.DataFrame:
    """Format routine dataframe for better display"""
    if routine_df.empty:
        return create_empty_routine_dataframe()
    
    # Pivot the data to show days as rows and periods as columns
    display_data = []
    
    for day in Constants.DAYS:
        row = {"Day": day}
        day_data = routine_df[routine_df["Day"] == day]
        
        for period in range(1, 7):
            period_data = day_data[day_data["Period"] == period]
            if len(period_data) > 0:
                course_info = period_data.iloc[0]
                cell_content = f"{course_info['Course_Name']}\n({course_info['Teacher_Name']})"
                row[f"Period {period}"] = cell_content
            else:
                row[f"Period {period}"] = ""
        
        display_data.append(row)
    
    return pd.DataFrame(display_data)

def validate_course_data(course_code: str, course_name: str, credit_hrs: str) -> tuple:
    """Validate course input data"""
    errors = []
    
    if not course_code.strip():
        errors.append("Course code is required")
    
    if not course_name.strip():
        errors.append("Course name is required")
    
    try:
        credit_hours = int(credit_hrs)
        if credit_hours <= 0:
            errors.append("Credit hours must be positive")
    except ValueError:
        errors.append("Credit hours must be a valid number")
        credit_hours = 0
    
    return errors, credit_hours

def validate_teacher_data(teacher_code: str, teacher_name: str, teacher_designation: str) -> list:
    """Validate teacher input data"""
    errors = []
    
    if not teacher_code.strip():
        errors.append("Teacher code is required")
    
    if not teacher_name.strip():
        errors.append("Teacher name is required")
    
    if not teacher_designation.strip():
        errors.append("Teacher designation is required")
    
    return errors

def get_time_slot_info() -> str:
    """Get formatted time slot information"""
    info = "**Class Schedule:**\n"
    for period, time in Constants.PERIODS.items():
        info += f"- Period {period}: {time}\n"
    info += "- Break: 9:00 AM - 9:10 AM (between Period 3 and 4)\n"
    info += "- Classes: Sunday to Friday (Saturday off)\n"
    return info

def get_teacher_weekly_routine(db, teacher_code: str) -> pd.DataFrame:
    """Get weekly routine for a specific teacher across all programs"""
    conn = db.get_connection()
    try:
        query = """
        SELECT 
            ct.Day,
            ct.Period,
            ct.Program,
            ct.Semester,
            c.Course_Name,
            c.Course_Code
        FROM Course_Teacher ct
        JOIN Course c ON ct.Course_Code = c.Course_Code
        WHERE ct.Teacher_Code = ?
        ORDER BY 
            CASE ct.Day 
                WHEN 'Sunday' THEN 1
                WHEN 'Monday' THEN 2
                WHEN 'Tuesday' THEN 3
                WHEN 'Wednesday' THEN 4
                WHEN 'Thursday' THEN 5
                WHEN 'Friday' THEN 6
            END,
            ct.Period
        """
        return pd.read_sql_query(query, conn, params=[teacher_code])
    finally:
        conn.close()

def format_teacher_routine_for_display(routine_df: pd.DataFrame) -> pd.DataFrame:
    """Format teacher routine dataframe for display in weekly format"""
    if routine_df.empty:
        return create_empty_routine_dataframe()
    
    # Create display data structure
    display_data = []
    
    for day in Constants.DAYS:
        row = {"Day": day}
        day_data = routine_df[routine_df["Day"] == day]
        
        for period in range(1, 7):
            period_data = day_data[day_data["Period"] == period]
            if not period_data.empty:
                class_info = period_data.iloc[0]
                cell_content = f"{class_info['Course_Name']}\n{class_info['Program']} Sem-{class_info['Semester']}"
                row[f"Period {period}"] = cell_content
            else:
                row[f"Period {period}"] = ""
        
        display_data.append(row)
    
    return pd.DataFrame(display_data)
