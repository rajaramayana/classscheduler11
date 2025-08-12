import sqlite3
import pandas as pd
from typing import List, Dict, Optional, Tuple
import os

class DatabaseManager:
    def __init__(self, db_name="Class_routine.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create Course table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Course (
                    Course_Code TEXT PRIMARY KEY,
                    Course_Name TEXT NOT NULL,
                    Credit_hrs INTEGER NOT NULL
                )
            """)
            
            # Create Teacher table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Teacher (
                    Teacher_Code TEXT PRIMARY KEY,
                    Teacher_Name TEXT NOT NULL,
                    Teacher_Designation TEXT NOT NULL
                )
            """)
            
            # Create Course_Teacher table with additional fields for program and semester
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Course_Teacher (
                    Teacher_Code TEXT,
                    Course_Code TEXT,
                    Period INTEGER,
                    Program TEXT,
                    Semester INTEGER,
                    Day TEXT,
                    PRIMARY KEY (Teacher_Code, Course_Code, Program, Semester, Day, Period),
                    FOREIGN KEY (Teacher_Code) REFERENCES Teacher(Teacher_Code),
                    FOREIGN KEY (Course_Code) REFERENCES Course(Course_Code)
                )
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def add_course(self, course_code: str, course_name: str, credit_hrs: int) -> bool:
        """Add a new course"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Course (Course_Code, Course_Name, Credit_hrs)
                VALUES (?, ?, ?)
            """, (course_code, course_name, credit_hrs))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_course(self, course_code: str, course_name: str, credit_hrs: int) -> bool:
        """Update an existing course"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE Course 
                SET Course_Name = ?, Credit_hrs = ?
                WHERE Course_Code = ?
            """, (course_name, credit_hrs, course_code))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_course(self, course_code: str) -> bool:
        """Delete a course"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # First delete related course assignments
            cursor.execute("DELETE FROM Course_Teacher WHERE Course_Code = ?", (course_code,))
            # Then delete the course
            cursor.execute("DELETE FROM Course WHERE Course_Code = ?", (course_code,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def add_teacher(self, teacher_code: str, teacher_name: str, teacher_designation: str) -> bool:
        """Add a new teacher"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Teacher (Teacher_Code, Teacher_Name, Teacher_Designation)
                VALUES (?, ?, ?)
            """, (teacher_code, teacher_name, teacher_designation))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_teacher(self, teacher_code: str, teacher_name: str, teacher_designation: str) -> bool:
        """Update an existing teacher"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE Teacher 
                SET Teacher_Name = ?, Teacher_Designation = ?
                WHERE Teacher_Code = ?
            """, (teacher_name, teacher_designation, teacher_code))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_teacher(self, teacher_code: str) -> bool:
        """Delete a teacher"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # First delete related course assignments
            cursor.execute("DELETE FROM Course_Teacher WHERE Teacher_Code = ?", (teacher_code,))
            # Then delete the teacher
            cursor.execute("DELETE FROM Teacher WHERE Teacher_Code = ?", (teacher_code,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def assign_course_teacher(self, teacher_code: str, course_code: str, period: int, 
                            program: str, semester: int, day: str) -> bool:
        """Assign a teacher to a course for a specific period"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if teacher is already assigned to another course in the same period and day
            cursor.execute("""
                SELECT COUNT(*) FROM Course_Teacher 
                WHERE Teacher_Code = ? AND Period = ? AND Day = ?
            """, (teacher_code, period, day))
            
            if cursor.fetchone()[0] > 0:
                return False  # Teacher conflict
            
            cursor.execute("""
                INSERT INTO Course_Teacher (Teacher_Code, Course_Code, Period, Program, Semester, Day)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (teacher_code, course_code, period, program, semester, day))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def remove_course_assignment(self, teacher_code: str, course_code: str, 
                               program: str, semester: int, day: str, period: int) -> bool:
        """Remove a course assignment"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM Course_Teacher 
                WHERE Teacher_Code = ? AND Course_Code = ? AND Program = ? 
                AND Semester = ? AND Day = ? AND Period = ?
            """, (teacher_code, course_code, program, semester, day, period))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_courses(self) -> pd.DataFrame:
        """Get all courses"""
        conn = self.get_connection()
        try:
            return pd.read_sql_query("SELECT * FROM Course", conn)
        finally:
            conn.close()
    
    def get_teachers(self) -> pd.DataFrame:
        """Get all teachers"""
        conn = self.get_connection()
        try:
            return pd.read_sql_query("SELECT * FROM Teacher", conn)
        finally:
            conn.close()
    
    def get_course_assignments(self) -> pd.DataFrame:
        """Get all course assignments with teacher and course details"""
        conn = self.get_connection()
        try:
            query = """
                SELECT ct.*, t.Teacher_Name, c.Course_Name 
                FROM Course_Teacher ct
                JOIN Teacher t ON ct.Teacher_Code = t.Teacher_Code
                JOIN Course c ON ct.Course_Code = c.Course_Code
                ORDER BY ct.Program, ct.Semester, ct.Day, ct.Period
            """
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()
    
    def get_routine_for_program_semester(self, program: str, semester: int) -> pd.DataFrame:
        """Get routine for a specific program and semester"""
        conn = self.get_connection()
        try:
            query = """
                SELECT ct.Day, ct.Period, ct.Course_Code, c.Course_Name, 
                       ct.Teacher_Code, t.Teacher_Name
                FROM Course_Teacher ct
                JOIN Teacher t ON ct.Teacher_Code = t.Teacher_Code
                JOIN Course c ON ct.Course_Code = c.Course_Code
                WHERE ct.Program = ? AND ct.Semester = ?
                ORDER BY ct.Day, ct.Period
            """
            return pd.read_sql_query(query, conn, params=[program, semester])
        finally:
            conn.close()
    
    def check_teacher_conflict(self, teacher_code: str, period: int, day: str, 
                             exclude_program: str = "", exclude_semester: int = 0) -> bool:
        """Check if teacher has conflict in the given period and day"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if exclude_program and exclude_semester:
                cursor.execute("""
                    SELECT COUNT(*) FROM Course_Teacher 
                    WHERE Teacher_Code = ? AND Period = ? AND Day = ?
                    AND NOT (Program = ? AND Semester = ?)
                """, (teacher_code, period, day, exclude_program, exclude_semester))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM Course_Teacher 
                    WHERE Teacher_Code = ? AND Period = ? AND Day = ?
                """, (teacher_code, period, day))
            
            return cursor.fetchone()[0] > 0
        finally:
            conn.close()
