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
    
    tab1, tab2, tab3 = st.tabs(["Make Assignment", "View Assignments", "Delete Assignments"])
    
    with tab1:
        st.subheader("Assign Teacher to Course")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_teacher = st.selectbox("Select Teacher", 
                                          options=teachers['Teacher_Code'].tolist(),
                                          format_func=lambda x: f"{x} - {teachers[teachers['Teacher_Code']==x]['Teacher_Name'].iloc[0]}")
            
            selected_course = st.selectbox("Select Course",
                                         options=courses['Course_Code'].tolist(), 
                                         format_func=lambda x: f"{x} - {courses[courses['Course_Code']==x]['Course_Name'].iloc[0]}")
            
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
    
    with tab3:
        st.subheader("Delete Course Assignments")
        assignments = db.get_course_assignments()
        
        if len(assignments) > 0:
            st.write("Select assignments to delete:")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_program = st.selectbox("Filter by Program", ["All"] + Constants.PROGRAMS, key="delete_program_filter")
            with col2:
                filter_semester = st.selectbox("Filter by Semester", ["All"] + [str(s) for s in Constants.SEMESTERS], key="delete_semester_filter")
            with col3:
                filter_day = st.selectbox("Filter by Day", ["All"] + Constants.DAYS, key="delete_day_filter")
            
            # Apply filters
            filtered_assignments = assignments.copy()
            if filter_program != "All":
                filtered_assignments = filtered_assignments[filtered_assignments['Program'] == filter_program]
            if filter_semester != "All":
                filtered_assignments = filtered_assignments[filtered_assignments['Semester'] == int(filter_semester)]
            if filter_day != "All":
                filtered_assignments = filtered_assignments[filtered_assignments['Day'] == filter_day]
            
            if len(filtered_assignments) > 0:
                st.markdown("---")
                
                # Display assignments for deletion with checkboxes
                assignments_to_delete = []
                
                for idx, assignment in filtered_assignments.iterrows():
                    col1, col2 = st.columns([1, 6])
                    
                    with col1:
                        delete_selected = st.checkbox(
                            "Delete", 
                            key=f"delete_check_{idx}_{assignment['Teacher_Code']}_{assignment['Course_Code']}_{assignment['Program']}_{assignment['Semester']}_{assignment['Day']}_{assignment['Period']}"
                        )
                        if delete_selected:
                            assignments_to_delete.append(assignment)
                    
                    with col2:
                        # Display assignment details
                        st.markdown(f"""
                        <div style='background-color: #fff2f2; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #ff6b6b;'>
                            <strong>{assignment['Program']} - Semester {assignment['Semester']}</strong><br>
                            <strong>📅 {assignment['Day']} - Period {assignment['Period']}</strong> ({Constants.PERIODS.get(int(assignment['Period']), 'Unknown')})<br>
                            <span style='color: #1f77b4;'>{assignment['Course_Name']} ({assignment['Course_Code']})</span><br>
                            <em>Teacher: {assignment['Teacher_Name']} ({assignment['Teacher_Code']})</em>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Delete selected assignments
                if assignments_to_delete:
                    st.markdown("---")
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        if st.button("🗑️ Delete Selected Assignments", type="primary", key="bulk_delete_btn"):
                            deleted_count = 0
                            failed_count = 0
                            
                            for assignment in assignments_to_delete:
                                if db.remove_course_assignment(
                                    str(assignment['Teacher_Code']), 
                                    str(assignment['Course_Code']),
                                    str(assignment['Program']),
                                    int(assignment['Semester']),
                                    str(assignment['Day']),
                                    int(assignment['Period'])
                                ):
                                    deleted_count += 1
                                else:
                                    failed_count += 1
                            
                            if deleted_count > 0:
                                st.success(f"Successfully deleted {deleted_count} assignment(s)!")
                            if failed_count > 0:
                                st.error(f"Failed to delete {failed_count} assignment(s)!")
                            
                            if deleted_count > 0:
                                st.rerun()
                    
                    with col2:
                        st.info(f"Selected {len(assignments_to_delete)} assignment(s) for deletion")
                
            else:
                st.info("No assignments match the selected filters.")
        else:
            st.info("No assignments found to delete.")

def render_routine_display(db: DatabaseManager):
    """Render routine display section"""
    st.header("📅 Class Routines")
    
    # Selection controls
    col1, col2 = st.columns(2)
    
    with col1:
        selected_program = st.selectbox("Select Program", Constants.PROGRAMS, key="routine_program")
    
    with col2:
        selected_semester = st.selectbox("Select Semester", Constants.SEMESTERS, key="routine_semester")
    
    # Get routine data
    routine_data = db.get_routine_for_program_semester(selected_program, selected_semester)
    
    if routine_data.empty:
        st.info(f"No routine found for {selected_program} Semester {selected_semester}. Please create some course assignments first.")
        return
    
    st.subheader(f"Routine for {selected_program} - Semester {selected_semester}")
    
    # Format data for display
    formatted_routine = format_routine_for_display(routine_data)
    
    # Display as dataframe
    st.dataframe(formatted_routine, use_container_width=True)
    
    # Display detailed schedule
    st.markdown("---")
    st.subheader("Detailed Schedule")
    
    for day in Constants.DAYS:
        day_schedule = routine_data[routine_data['Day'] == day]
        if not day_schedule.empty:
            st.write(f"**{day}:**")
            for _, class_info in day_schedule.iterrows():
                period_time = Constants.PERIODS.get(int(class_info['Period']), "Unknown")
                st.write(f"- Period {class_info['Period']} ({period_time}): {class_info['Course_Name']} - {class_info['Teacher_Name']}")

def render_teacher_routine_display(db: DatabaseManager):
    """Render teacher routine display section"""
    st.header("👨‍🏫 Teacher Schedules")
    
    teachers = db.get_teachers()
    
    if teachers.empty:
        st.warning("No teachers found. Please add teachers first.")
        return
    
    # Teacher selection
    selected_teacher = st.selectbox(
        "Select Teacher",
        options=teachers['Teacher_Code'].tolist(),
        format_func=lambda x: f"{x} - {teachers[teachers['Teacher_Code']==x]['Teacher_Name'].iloc[0]}",
        key="teacher_routine_select"
    )
    
    if selected_teacher:
        teacher_name = teachers[teachers['Teacher_Code'] == selected_teacher]['Teacher_Name'].iloc[0]
        st.subheader(f"Weekly Schedule for {teacher_name} ({selected_teacher})")
        
        # Get teacher routine
        teacher_routine = get_teacher_weekly_routine(db, selected_teacher)
        
        if teacher_routine.empty:
            st.info(f"No schedule found for {teacher_name}. This teacher has no assigned classes.")
            return
        
        # Format for display
        formatted_teacher_routine = format_teacher_routine_for_display(teacher_routine)
        
        # Display as dataframe
        st.dataframe(formatted_teacher_routine, use_container_width=True)
        
        # Display detailed schedule
        st.markdown("---")
        st.subheader("Detailed Schedule")
        
        for day in Constants.DAYS:
            day_schedule = teacher_routine[teacher_routine['Day'] == day]
            if not day_schedule.empty:
                st.write(f"**{day}:**")
                for _, class_info in day_schedule.iterrows():
                    period_time = Constants.PERIODS.get(int(class_info['Period']), "Unknown")
                    st.write(f"- Period {class_info['Period']} ({period_time}): {class_info['Course_Name']} - {class_info['Program']} Sem {class_info['Semester']}")
