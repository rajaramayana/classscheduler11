import streamlit as st
import pandas as pd
from database import DatabaseManager
from models import Constants
from utils import validate_course_data, validate_teacher_data, format_routine_for_display, get_teacher_weekly_routine, format_teacher_routine_for_display

def render_course_management(db: DatabaseManager):
    """Render course management section"""
    st.header("📚 Course Management")
    
    tab1, tab2 = st.tabs(["Add/Edit Courses", "View Courses"])
    
    with tab1:
        st.subheader("Add New Course")
        
        col1, col2 = st.columns(2)
        with col1:
            course_code = st.text_input("Course Code", key="course_code_input")
            course_name = st.text_input("Course Name", key="course_name_input")
        with col2:
            credit_hrs = st.text_input("Credit Hours", key="credit_hrs_input")
        
        if st.button("Add Course", key="add_course_btn"):
            errors, validated_credit_hrs = validate_course_data(course_code, course_name, credit_hrs)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                if db.add_course(course_code.strip(), course_name.strip(), validated_credit_hrs):
                    st.success(f"Course {course_code} added successfully!")
                    st.rerun()
                else:
                    st.error("Course code already exists!")
    
    with tab2:
        st.subheader("Existing Courses")
        courses = db.get_courses()
        
        if not courses.empty:
            # Display courses with edit/delete options
            for idx, course in courses.iterrows():
                with st.expander(f"📖 {course['Course_Code']} - {course['Course_Name']}"):
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        new_name = st.text_input("Course Name", value=course['Course_Name'], 
                                                key=f"edit_name_{course['Course_Code']}")
                    with col2:
                        new_credit = st.number_input("Credit Hours", value=int(course['Credit_hrs']), 
                                                   min_value=1, key=f"edit_credit_{course['Course_Code']}")
                    with col3:
                        if st.button("Update", key=f"update_{course['Course_Code']}"):
                            if db.update_course(str(course['Course_Code']), new_name or "", int(new_credit)):
                                st.success("Course updated!")
                                st.rerun()
                            else:
                                st.error("Update failed!")
                    
                    with col4:
                        if st.button("Delete", key=f"delete_{course['Course_Code']}", type="secondary"):
                            if db.delete_course(str(course['Course_Code'])):
                                st.success("Course deleted!")
                                st.rerun()
                            else:
                                st.error("Delete failed!")
        else:
            st.info("No courses found. Add some courses to get started.")

def render_teacher_management(db: DatabaseManager):
    """Render teacher management section"""
    st.header("👨‍🏫 Teacher Management")
    
    tab1, tab2 = st.tabs(["Add/Edit Teachers", "View Teachers"])
    
    with tab1:
        st.subheader("Add New Teacher")
        
        col1, col2 = st.columns(2)
        with col1:
            teacher_code = st.text_input("Teacher Code", key="teacher_code_input")
            teacher_name = st.text_input("Teacher Name", key="teacher_name_input")
        with col2:
            teacher_designation = st.text_input("Teacher Designation", key="teacher_designation_input")
        
        if st.button("Add Teacher", key="add_teacher_btn"):
            errors = validate_teacher_data(teacher_code, teacher_name, teacher_designation)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                if db.add_teacher(teacher_code.strip(), teacher_name.strip(), teacher_designation.strip()):
                    st.success(f"Teacher {teacher_code} added successfully!")
                    st.rerun()
                else:
                    st.error("Teacher code already exists!")
    
    with tab2:
        st.subheader("Existing Teachers")
        teachers = db.get_teachers()
        
        if not teachers.empty:
            for idx, teacher in teachers.iterrows():
                with st.expander(f"👨‍🏫 {teacher['Teacher_Code']} - {teacher['Teacher_Name']}"):
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        new_name = st.text_input("Teacher Name", value=teacher['Teacher_Name'], 
                                               key=f"edit_teacher_name_{teacher['Teacher_Code']}")
                    with col2:
                        new_designation = st.text_input("Designation", value=teacher['Teacher_Designation'], 
                                                      key=f"edit_designation_{teacher['Teacher_Code']}")
                    with col3:
                        if st.button("Update", key=f"update_teacher_{teacher['Teacher_Code']}"):
                            if db.update_teacher(str(teacher['Teacher_Code']), new_name or "", new_designation or ""):
                                st.success("Teacher updated!")
                                st.rerun()
                            else:
                                st.error("Update failed!")
                    
                    with col4:
                        if st.button("Delete", key=f"delete_teacher_{teacher['Teacher_Code']}", type="secondary"):
                            if db.delete_teacher(str(teacher['Teacher_Code'])):
                                st.success("Teacher deleted!")
                                st.rerun()
                            else:
                                st.error("Delete failed!")
        else:
            st.info("No teachers found. Add some teachers to get started.")

def render_assignment_management(db: DatabaseManager):
    """Render course assignment management"""
    st.header("📋 Course Assignments")
    
    courses = db.get_courses()
    teachers = db.get_teachers()
    
    if courses.empty or teachers.empty:
        st.warning("Please add courses and teachers before making assignments.")
        return
    
    tab1, tab2 = st.tabs(["Make Assignment", "View Assignments"])
    
    with tab1:
        st.subheader("Assign Teacher to Course")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_teacher = st.selectbox("Select Teacher", 
                                          options=teachers['Teacher_Code'].tolist(),
                                          format_func=lambda x: f"{x} - {teachers[teachers['Teacher_Code']==x]['Teacher_Name'].values[0]}")
            
            selected_course = st.selectbox("Select Course",
                                         options=courses['Course_Code'].tolist(), 
                                         format_func=lambda x: f"{x} - {courses[courses['Course_Code']==x]['Course_Name'].values[0]}")
            
            selected_program = st.selectbox("Select Program", Constants.PROGRAMS)
        
        with col2:
            selected_semester = st.selectbox("Select Semester", Constants.SEMESTERS)
            selected_day = st.selectbox("Select Day", Constants.DAYS)
            selected_period = st.selectbox("Select Period", 
                                         options=list(Constants.PERIODS.keys()),
                                         format_func=lambda x: f"Period {x}: {Constants.PERIODS[x]}")
        
        if st.button("Make Assignment", key="make_assignment_btn"):
            # Check for teacher conflict
            if selected_teacher and selected_course and db.check_teacher_conflict(selected_teacher, selected_period, selected_day):
                st.error(f"Teacher {selected_teacher} is already assigned to another class in Period {selected_period} on {selected_day}!")
            else:
                if selected_teacher and selected_course and db.assign_course_teacher(selected_teacher, selected_course, selected_period, 
                                          selected_program, selected_semester, selected_day):
                    st.success("Assignment created successfully!")
                    st.rerun()
                else:
                    st.error("Assignment failed! This assignment might already exist.")
    
    with tab2:
        st.subheader("Current Assignments")
        assignments = db.get_course_assignments()
        
        if len(assignments) > 0:
            # Group by program and semester
            for program in Constants.PROGRAMS:
                program_assignments = assignments[assignments['Program'] == program]
                if len(program_assignments) > 0:
                    st.write(f"**{program} Program:**")
                    
                    for semester in Constants.SEMESTERS:
                        semester_assignments = program_assignments[program_assignments['Semester'] == semester]
                        if len(semester_assignments) > 0:
                            with st.expander(f"Semester {semester}"):
                                for idx, assignment in semester_assignments.iterrows():
                                    col1, col2 = st.columns([5, 1])
                                    
                                    with col1:
                                        # Display assignment with styled container
                                        st.markdown(f"""
                                        <div style='background-color: #f0f2f6; padding: 8px; border-radius: 5px; margin: 2px 0; border-left: 3px solid #1f77b4;'>
                                            <strong>📅 {assignment['Day']} - Period {assignment['Period']}</strong><br>
                                            <span style='color: #1f77b4;'>{assignment['Course_Name']}</span> by <em>{assignment['Teacher_Name']}</em>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    with col2:
                                        # Red cross delete button
                                        if st.button("❌", key=f"remove_{idx}_{assignment['Teacher_Code']}_{assignment['Course_Code']}", 
                                                   help="Delete this assignment", type="secondary"):
                                            if db.remove_course_assignment(str(assignment['Teacher_Code']), 
                                                                         str(assignment['Course_Code']),
                                                                         str(assignment['Program']),
                                                                         int(assignment['Semester']),
                                                                         str(assignment['Day']),
                                                                         int(assignment['Period'])):
                                                st.success("Assignment removed!")
                                                st.rerun()
                                            else:
                                                st.error("Failed to remove assignment!")
        else:
            st.info("No assignments found. Create some assignments to get started.")

def create_weekly_routine_table(routine_data: pd.DataFrame, selected_program: str, selected_semester: int, db):
    """Create weekly routine table with interactive delete functionality"""
    
    # Create the table header
    st.markdown("""
    <style>
    .routine-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-family: 'Arial', sans-serif;
    }
    .routine-table th, .routine-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
        vertical-align: middle;
        position: relative;
    }
    .routine-table th {
        background-color: #f2f2f2;
        font-weight: bold;
        color: #333;
    }
    .routine-table .day-header {
        background-color: #e3f2fd;
        font-weight: bold;
        width: 120px;
    }
    .class-cell {
        background-color: #f0f8ff;
        padding: 10px;
        border-radius: 5px;
        margin: 2px;
        position: relative;
        min-height: 60px;
        border-left: 4px solid #1f77b4;
        transition: all 0.2s ease;
    }
    .class-cell:hover {
        background-color: #e8f4ff;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .delete-button-container {
        position: absolute;
        top: 2px;
        right: 2px;
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    .class-cell:hover .delete-button-container {
        opacity: 1;
    }
    .empty-cell {
        background-color: #f8f9fa;
        color: #6c757d;
        font-style: italic;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create period headers
    period_headers = ["Day"] + [f"Period {i}\n{Constants.PERIODS[i]}" for i in range(1, 7)]
    
    # Display table header
    cols = st.columns(7)  # 1 for day + 6 for periods
    for i, header in enumerate(period_headers):
        with cols[i]:
            if i == 0:
                st.markdown("**Day**")
            else:
                period_num = i
                st.markdown(f"**Period {period_num}**")
                st.caption(Constants.PERIODS[period_num])
    
    # Display each day's schedule
    for day in Constants.DAYS:
        day_data = routine_data[routine_data['Day'] == day].sort_values('Period')
        
        cols = st.columns(7)
        
        # Day column
        with cols[0]:
            st.markdown(f"**📅 {day}**")
        
        # Period columns
        for period in range(1, 7):
            with cols[period]:
                period_class = day_data[day_data['Period'] == period]
                
                if not period_class.empty:
                    class_info = period_class.iloc[0]
                    delete_key = f"weekly_del_{selected_program}_{selected_semester}_{day}_{period}_{class_info['Course_Code']}_{class_info['Teacher_Code']}"
                    
                    # Create container for the cell with hover effect
                    container = st.container()
                    with container:
                        # Add global CSS to hide ALL delete buttons by default
                        st.markdown("""
                        <style>
                        /* Force hide ALL buttons with "Delete this class" help text */
                        button[title="Delete this class"] {
                            display: none !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Add hover CSS for this specific cell  
                        cell_class = f"hover-cell-{delete_key.replace('_', '-')}"
                        st.markdown(f"""
                        <style>
                        .{cell_class} {{
                            position: relative;
                            background-color: #f0f8ff;
                            padding: 10px;
                            border-radius: 5px;
                            margin: 2px;
                            min-height: 60px;
                            border-left: 4px solid #1f77b4;
                            transition: all 0.2s ease;
                        }}
                        .{cell_class}:hover {{
                            background-color: #e8f4ff;
                            transform: translateY(-1px);
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        }}
                        /* Show delete button when hovering over the content column */
                        div[data-testid="column"]:has(.{cell_class}:hover) + div[data-testid="column"] button[title="Delete this class"] {{
                            display: inline-block !important;
                            background-color: #dc3545 !important;
                            border: none !important;
                            border-radius: 50% !important;
                            width: 18px !important;
                            height: 18px !important;
                            padding: 0 !important;
                            color: white !important;
                            font-size: 12px !important;
                            font-weight: bold !important;
                            line-height: 1 !important;
                            min-height: 18px !important;
                            animation: fadeIn 0.3s ease !important;
                        }}
                        @keyframes fadeIn {{
                            from {{ opacity: 0; }}
                            to {{ opacity: 1; }}
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Create columns to separate content and delete button  
                        col_content, col_delete = st.columns([10, 1])
                        
                        with col_content:
                            # Class content with hover class
                            st.markdown(f"""
                            <div class="{cell_class}">
                                <strong style="color: #1f77b4;">{class_info['Course_Name']}</strong><br>
                                <small style="color: #666;">{class_info['Teacher_Name']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_delete:
                            # Delete button in separate column
                            if st.button("×", key=f"{delete_key}_btn", help="Delete this class"):
                                if db.remove_course_assignment(
                                    str(class_info['Teacher_Code']), 
                                    str(class_info['Course_Code']),
                                    selected_program,
                                    selected_semester,
                                    day,
                                    period
                                ):
                                    st.success("Class removed!")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove class!")
                else:
                    # Empty cell
                    st.markdown("""
                    <div class="empty-cell">
                        <em>No class</em>
                    </div>
                    """, unsafe_allow_html=True)

def render_routine_display(db: DatabaseManager):
    """Render interactive class routine display"""
    st.header("🗓️ Interactive Class Routine")
    
    # Program and semester selection
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_program = st.selectbox("Select Program", Constants.PROGRAMS, key="routine_program")
    with col2:
        selected_semester = st.selectbox("Select Semester", Constants.SEMESTERS, key="routine_semester")
    with col3:
        if st.button("🔄 Refresh", help="Refresh the routine display"):
            st.rerun()
    
    # Get data
    courses = db.get_courses()
    teachers = db.get_teachers()
    routine_data = db.get_routine_for_program_semester(selected_program, selected_semester)
    
    # Display period timings info
    with st.expander("📅 Period Timings", expanded=False):
        for p, t in Constants.PERIODS.items():
            st.write(f"**Period {p}:** {t}")
        st.write("**Break:** 9:00 AM - 9:10 AM (between Period 3 and 4)")
    
    st.subheader(f"{selected_program} - Semester {selected_semester} Weekly Routine")
    
    # Check if courses and teachers exist
    if courses.empty or teachers.empty:
        st.warning("Please add courses and teachers first before creating routines.")
        return
    
    # Create routine table
    if routine_data.empty:
        st.info("No classes scheduled for this program and semester yet.")
        
        # Show empty routine table
        empty_routine = format_routine_for_display(pd.DataFrame())
        st.dataframe(empty_routine, use_container_width=True)
        
        st.markdown("**Instructions:**")
        st.markdown("1. Go to 'Course Assignments' to schedule classes")
        st.markdown("2. Select teacher, course, program, semester, day, and period")
        st.markdown("3. Return here to view the complete routine")
        
    else:
        # Display weekly routine table with interactive delete functionality
        st.markdown("**Weekly Routine - Hover over classes to see delete option**")
        
        # Create weekly routine table
        routine_table = create_weekly_routine_table(routine_data, selected_program, selected_semester, db)
        
        st.markdown("---")
        
        # Additional routine statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_classes = len(routine_data)
            st.metric("Total Classes", total_classes)
        
        with col2:
            unique_teachers = routine_data['Teacher_Name'].nunique()
            st.metric("Teachers Involved", unique_teachers)
        
        with col3:
            unique_courses = routine_data['Course_Name'].nunique()
            st.metric("Courses Scheduled", unique_courses)
        
        # Show detailed schedule by day (collapsible)
        with st.expander("📋 Detailed Schedule Summary"):
            for day in Constants.DAYS:
                day_schedule = routine_data[routine_data['Day'] == day].sort_values('Period')
                if not day_schedule.empty:
                    st.write(f"**{day}:**")
                    for _, row in day_schedule.iterrows():
                        period_time = Constants.PERIODS[row['Period']]
                        st.write(f"  • Period {row['Period']} ({period_time}): {row['Course_Name']} - {row['Teacher_Name']}")
                else:
                    st.write(f"**{day}:** No classes scheduled")

def render_teacher_routine_display(db: DatabaseManager):
    """Render individual teacher weekly routine display"""
    st.header("👨‍🏫 Teacher Weekly Routine")
    
    # Get all teachers
    teachers = db.get_teachers()
    
    if teachers.empty:
        st.warning("No teachers found. Please add teachers first.")
        return
    
    # Teacher selection
    col1, col2 = st.columns([3, 1])
    with col1:
        teacher_options = [f"{row['Teacher_Code']} - {row['Teacher_Name']}" for _, row in teachers.iterrows()]
        selected_teacher_option = st.selectbox("Select Teacher", teacher_options, key="teacher_routine_select")
        
        if selected_teacher_option:
            selected_teacher_code = selected_teacher_option.split(" - ")[0]
            selected_teacher_name = selected_teacher_option.split(" - ")[1]
    
    with col2:
        if st.button("🔄 Refresh", help="Refresh the teacher routine"):
            st.rerun()
    
    if not selected_teacher_option:
        return
    
    # Get teacher's routine data
    teacher_routine = get_teacher_weekly_routine(db, selected_teacher_code)
    
    # Display teacher info
    teacher_info = teachers[teachers['Teacher_Code'] == selected_teacher_code].iloc[0]
    
    st.markdown(f"### {teacher_info['Teacher_Name']} ({teacher_info['Teacher_Code']})")
    st.markdown(f"**Designation:** {teacher_info['Designation']}")
    
    # Display period timings info
    with st.expander("📅 Period Timings", expanded=False):
        for p, t in Constants.PERIODS.items():
            st.write(f"**Period {p}:** {t}")
        st.write("**Break:** 9:00 AM - 9:10 AM (between Period 3 and 4)")
    
    if teacher_routine.empty:
        st.info(f"No classes assigned to {teacher_info['Teacher_Name']} yet.")
        st.markdown("**Instructions:**")
        st.markdown("1. Go to 'Course Assignments' to assign classes to this teacher")
        st.markdown("2. Select this teacher along with courses, programs, and time slots")
        st.markdown("3. Return here to view their complete weekly routine")
        return
    
    # Create teacher weekly routine table
    st.subheader(f"Weekly Schedule for {teacher_info['Teacher_Name']}")
    
    # Create the table header with custom styling
    st.markdown("""
    <style>
    .teacher-routine-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-family: 'Arial', sans-serif;
    }
    .teacher-class-cell {
        background-color: #e8f5e8;
        padding: 12px;
        border-radius: 8px;
        margin: 2px;
        min-height: 70px;
        border-left: 4px solid #28a745;
        transition: all 0.2s ease;
        text-align: center;
    }
    .teacher-class-cell:hover {
        background-color: #d4edda;
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(40, 167, 69, 0.2);
    }
    .teacher-empty-cell {
        background-color: #f8f9fa;
        color: #6c757d;
        font-style: italic;
        padding: 20px;
        text-align: center;
        border-radius: 8px;
        margin: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create period headers
    cols = st.columns(7)  # 1 for day + 6 for periods
    
    # Header row
    with cols[0]:
        st.markdown("**Day**")
    for i in range(1, 7):
        with cols[i]:
            st.markdown(f"**Period {i}**")
            st.caption(Constants.PERIODS[i])
    
    # Display each day's schedule for the teacher
    for day in Constants.DAYS:
        day_data = teacher_routine[teacher_routine['Day'] == day].sort_values('Period')
        
        cols = st.columns(7)
        
        # Day column
        with cols[0]:
            st.markdown(f"**{day}**")
        
        # Period columns
        for period in range(1, 7):
            with cols[period]:
                period_class = day_data[day_data['Period'] == period]
                
                if not period_class.empty:
                    class_info = period_class.iloc[0]
                    # Display teacher's class with program and semester info
                    st.markdown(f"""
                    <div class="teacher-class-cell">
                        <strong style="color: #28a745; font-size: 14px;">{class_info['Course_Name']}</strong><br>
                        <small style="color: #495057; font-weight: 500;">{class_info['Program']} - Sem {class_info['Semester']}</small><br>
                        <small style="color: #6c757d;">({class_info['Course_Code']})</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Empty period
                    st.markdown("""
                    <div class="teacher-empty-cell">
                        <em>Free</em>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Teacher schedule statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_classes = len(teacher_routine)
        st.metric("Total Classes/Week", total_classes)
    
    with col2:
        unique_courses = teacher_routine['Course_Name'].nunique()
        st.metric("Different Courses", unique_courses)
    
    with col3:
        unique_programs = teacher_routine['Program'].nunique()
        st.metric("Programs Teaching", unique_programs)
    
    with col4:
        total_periods = 6 * 6  # 6 days × 6 periods
        free_periods = total_periods - total_classes
        st.metric("Free Periods/Week", free_periods)
    
    # Detailed schedule summary
    with st.expander("📋 Detailed Weekly Schedule Summary"):
        for day in Constants.DAYS:
            day_schedule = teacher_routine[teacher_routine['Day'] == day].sort_values('Period')
            if not day_schedule.empty:
                st.write(f"**{day}:**")
                for _, row in day_schedule.iterrows():
                    period_time = Constants.PERIODS[row['Period']]
                    st.write(f"  • Period {row['Period']} ({period_time}): {row['Course_Name']} - {row['Program']} Semester {row['Semester']}")
            else:
                st.write(f"**{day}:** Free day")
        
        # Course load breakdown
        st.markdown("**Course Load Breakdown:**")
        course_summary = teacher_routine.groupby(['Course_Name', 'Program']).size().reset_index(name='Classes_Per_Week')
        for _, course in course_summary.iterrows():
            st.write(f"  • {course['Course_Name']} ({course['Program']}): {course['Classes_Per_Week']} classes/week")
