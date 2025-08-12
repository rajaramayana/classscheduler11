from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import DatabaseManager
from models import Constants
from utils import (
    validate_course_data, 
    validate_teacher_data, 
    get_time_slot_info,
    format_routine_for_display,
    get_teacher_weekly_routine,
    format_teacher_routine_for_display
)
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Initialize database
db = DatabaseManager()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', 
                         programs=Constants.PROGRAMS,
                         semesters=Constants.SEMESTERS,
                         days=Constants.DAYS,
                         periods=Constants.PERIODS)

@app.route('/courses')
def courses():
    """Course management page"""
    courses_data = db.get_courses()
    return render_template('courses.html', courses=courses_data.to_dict('records'))

@app.route('/add_course', methods=['POST'])
def add_course():
    """Add new course"""
    course_code = request.form.get('course_code', '').strip()
    course_name = request.form.get('course_name', '').strip()
    credit_hrs = request.form.get('credit_hours', '').strip()
    
    errors, credit_hours = validate_course_data(course_code, course_name, credit_hrs)
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('courses'))
    
    if db.add_course(course_code, course_name, credit_hours):
        flash(f'Course "{course_name}" added successfully!', 'success')
    else:
        flash(f'Failed to add course. Course code "{course_code}" may already exist.', 'error')
    
    return redirect(url_for('courses'))

@app.route('/teachers')
def teachers():
    """Teacher management page"""
    teachers_data = db.get_teachers()
    return render_template('teachers.html', teachers=teachers_data.to_dict('records'))

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    """Add new teacher"""
    teacher_code = request.form.get('teacher_code', '').strip()
    teacher_name = request.form.get('teacher_name', '').strip()
    teacher_designation = request.form.get('teacher_designation', '').strip()
    
    errors = validate_teacher_data(teacher_code, teacher_name, teacher_designation)
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('teachers'))
    
    if db.add_teacher(teacher_code, teacher_name, teacher_designation):
        flash(f'Teacher "{teacher_name}" added successfully!', 'success')
    else:
        flash(f'Failed to add teacher. Teacher code "{teacher_code}" may already exist.', 'error')
    
    return redirect(url_for('teachers'))

@app.route('/assignments')
def assignments():
    """Course assignments page"""
    courses = db.get_courses()
    teachers = db.get_teachers()
    assignments_data = db.get_course_assignments()
    
    return render_template('assignments.html',
                         courses=courses.to_dict('records'),
                         teachers=teachers.to_dict('records'),
                         assignments=assignments_data.to_dict('records'),
                         programs=Constants.PROGRAMS,
                         semesters=Constants.SEMESTERS,
                         days=Constants.DAYS,
                         periods=Constants.PERIODS)

@app.route('/add_assignment', methods=['POST'])
def add_assignment():
    """Add course assignment"""
    teacher_code = request.form.get('teacher_code', '').strip()
    course_code = request.form.get('course_code', '').strip()
    program = request.form.get('program', '').strip()
    semester_str = request.form.get('semester', '').strip()
    day = request.form.get('day', '').strip()
    period_str = request.form.get('period', '').strip()
    
    if not all([teacher_code, course_code, program, semester_str, day, period_str]):
        flash('All fields are required.', 'error')
        return redirect(url_for('assignments'))
    
    try:
        semester = int(semester_str)
        period = int(period_str)
        
        if db.assign_course_teacher(teacher_code, course_code, period, program, semester, day):
            flash('Assignment added successfully!', 'success')
        else:
            flash('Failed to add assignment. There might be a conflict or invalid data.', 'error')
    except (ValueError, TypeError):
        flash('Invalid semester or period value.', 'error')
    
    return redirect(url_for('assignments'))

@app.route('/delete_assignment', methods=['POST'])
def delete_assignment():
    """Delete course assignment"""
    teacher_code = request.form.get('teacher_code', '').strip()
    course_code = request.form.get('course_code', '').strip()
    program = request.form.get('program', '').strip()
    semester_str = request.form.get('semester', '').strip()
    day = request.form.get('day', '').strip()
    period_str = request.form.get('period', '').strip()
    
    if not all([teacher_code, course_code, program, semester_str, day, period_str]):
        flash('All fields are required for deletion.', 'error')
        return redirect(url_for('assignments'))
    
    try:
        semester = int(semester_str)
        period = int(period_str)
        
        if db.remove_course_assignment(teacher_code, course_code, program, semester, day, period):
            flash('Assignment deleted successfully!', 'success')
        else:
            flash('Failed to delete assignment.', 'error')
    except (ValueError, TypeError):
        flash('Invalid semester or period value.', 'error')
    
    return redirect(url_for('assignments'))

@app.route('/routines')
def routines():
    """Class routines page"""
    return render_template('routines.html',
                         programs=Constants.PROGRAMS,
                         semesters=Constants.SEMESTERS)

@app.route('/get_routine/<program>/<int:semester>')
def get_routine(program, semester):
    """Get routine data for program and semester"""
    routine_data = db.get_routine_for_program_semester(program, semester)
    
    if routine_data.empty:
        return jsonify({'error': f'No routine found for {program} Semester {semester}'})
    
    formatted_routine = format_routine_for_display(routine_data)
    
    # Convert to HTML table
    html_table = create_html_table(formatted_routine)
    
    # Get detailed schedule
    detailed_schedule = []
    for day in Constants.DAYS:
        day_schedule = routine_data[routine_data['Day'] == day]
        if not day_schedule.empty:
            day_classes = []
            for _, class_info in day_schedule.iterrows():
                period_time = Constants.PERIODS.get(int(class_info['Period']), "Unknown")
                day_classes.append({
                    'period': int(class_info['Period']),
                    'time': period_time,
                    'course_name': class_info['Course_Name'],
                    'teacher_name': class_info['Teacher_Name']
                })
            detailed_schedule.append({
                'day': day,
                'classes': day_classes
            })
    
    return jsonify({
        'html_table': html_table,
        'detailed_schedule': detailed_schedule
    })

@app.route('/teacher_routines')
def teacher_routines():
    """Teacher routines page"""
    teachers = db.get_teachers()
    return render_template('teacher_routines.html',
                         teachers=teachers.to_dict('records'))

@app.route('/get_teacher_routine/<teacher_code>')
def get_teacher_routine(teacher_code):
    """Get routine for specific teacher"""
    teachers = db.get_teachers()
    teacher_info = teachers[teachers['Teacher_Code'] == teacher_code]
    teacher_name = teacher_info['Teacher_Name'].iloc[0] if not teacher_info.empty else 'Unknown'
    
    teacher_routine = get_teacher_weekly_routine(db, teacher_code)
    
    if teacher_routine.empty:
        return jsonify({'error': f'No schedule found for {teacher_name}'})
    
    formatted_routine = format_teacher_routine_for_display(teacher_routine)
    html_table = create_html_table(formatted_routine)
    
    # Get detailed schedule
    detailed_schedule = []
    for day in Constants.DAYS:
        day_schedule = teacher_routine[teacher_routine['Day'] == day]
        if not day_schedule.empty:
            day_classes = []
            for _, class_info in day_schedule.iterrows():
                period_time = Constants.PERIODS.get(int(class_info['Period']), "Unknown")
                day_classes.append({
                    'period': int(class_info['Period']),
                    'time': period_time,
                    'course_name': class_info['Course_Name'],
                    'program': class_info['Program'],
                    'semester': int(class_info['Semester'])
                })
            detailed_schedule.append({
                'day': day,
                'classes': day_classes
            })
    
    return jsonify({
        'teacher_name': teacher_name,
        'html_table': html_table,
        'detailed_schedule': detailed_schedule
    })

def create_html_table(df):
    """Create HTML table from dataframe"""
    html = "<table class='table table-bordered table-striped'>"
    
    # Header
    html += "<thead class='table-dark'><tr>"
    for col in df.columns:
        html += f"<th class='text-center'>{col}</th>"
    html += "</tr></thead>"
    
    # Body
    html += "<tbody>"
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            cell_value = str(row[col]) if row[col] else ""
            cell_value = cell_value.replace('\n', '<br>')
            if col == 'Day':
                html += f"<td class='text-center fw-bold table-secondary'>{cell_value}</td>"
            else:
                html += f"<td class='text-center'>{cell_value}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)