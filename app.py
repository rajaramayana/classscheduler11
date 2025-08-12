import streamlit as st
import pandas as pd
from database import DatabaseManager
from ui_components import (
    render_course_management,
    render_teacher_management, 
    render_assignment_management,
    render_routine_display,
    render_teacher_routine_display
)
from utils import get_time_slot_info

# Page configuration
st.set_page_config(
    page_title="Class Routine Management System",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def init_database():
    return DatabaseManager()

def main():
    # Initialize database
    db = init_database()
    
    # Main title
    st.title("🏫 Class Routine Management System")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown(get_time_slot_info())
    
    # Navigation options
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["Dashboard", "Course Management", "Teacher Management", "Course Assignments", "View Routines", "Teacher Routines"]
    )
    
    # Dashboard
    if page == "Dashboard":
        st.header("📊 Dashboard")
        
        # Get summary statistics
        courses = db.get_courses()
        teachers = db.get_teachers()
        assignments = db.get_course_assignments()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Courses", len(courses))
        
        with col2:
            st.metric("Total Teachers", len(teachers))
        
        with col3:
            st.metric("Total Assignments", len(assignments))
        
        with col4:
            programs_with_assignments = int(assignments['Program'].nunique()) if len(assignments) > 0 else 0
            st.metric("Programs with Routines", programs_with_assignments)
        
        st.markdown("---")
        
        # Recent assignments
        if len(assignments) > 0:
            st.subheader("📋 Recent Assignments")
            recent_assignments = assignments.tail(10)
            
            display_data = []
            for idx, assignment in recent_assignments.iterrows():
                display_data.append({
                    "Program": assignment['Program'],
                    "Semester": f"Sem {assignment['Semester']}",
                    "Day": assignment['Day'],
                    "Period": f"P{assignment['Period']}",
                    "Course": assignment['Course_Name'],
                    "Teacher": assignment['Teacher_Name']
                })
            
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info("No assignments found. Start by adding courses and teachers, then create assignments.")
        
        # System status
        st.markdown("---")
        st.subheader("🔧 System Status")
        
        if courses.empty:
            st.warning("⚠️ No courses added yet")
        else:
            st.success(f"✅ {len(courses)} courses configured")
        
        if teachers.empty:
            st.warning("⚠️ No teachers added yet")
        else:
            st.success(f"✅ {len(teachers)} teachers configured")
        
        if assignments.empty:
            st.warning("⚠️ No course assignments made yet")
        else:
            st.success(f"✅ {len(assignments)} assignments configured")
    
    # Course Management
    elif page == "Course Management":
        render_course_management(db)
    
    # Teacher Management  
    elif page == "Teacher Management":
        render_teacher_management(db)
    
    # Course Assignments
    elif page == "Course Assignments":
        render_assignment_management(db)
    
    # View Routines
    elif page == "View Routines":
        render_routine_display(db)
    
    # Teacher Routines
    elif page == "Teacher Routines":
        render_teacher_routine_display(db)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
            Class Routine Management System | Academic Programs: BCA, BIT, B.Tech AI | 8 Semesters Each | Sunday to Friday Schedule (Saturday Off)
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
