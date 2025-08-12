# Class Routine Management System

## Overview

A comprehensive class scheduling and routine management system built with Streamlit for educational institutions. The application enables administrators to manage courses, teachers, and class assignments while automatically generating conflict-free timetables. The system supports multiple academic programs (BCA, BIT, B.Tech AI) with semester-based organization and provides both course-centric and teacher-centric routine views. Enhanced with advanced assignment deletion capabilities including bulk delete operations with filtering options and improved display formatting with teacher names appearing below course names in all sections.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with component-based UI design
- **Layout**: Wide layout configuration with expandable sidebar navigation for optimal screen utilization
- **Component Structure**: Modular UI components separated into dedicated modules (`ui_components.py`) for course management, teacher management, assignment management with advanced deletion capabilities, and routine display
- **State Management**: Leverages Streamlit's built-in session state and resource caching mechanisms for database connections
- **Navigation**: Tab-based interface within sections for organized user workflows
- **Display Enhancement**: Custom HTML table rendering for weekly routines to properly display teacher names below course names with line breaks

### Backend Architecture
- **Database Layer**: Custom `DatabaseManager` class providing abstraction over SQLite operations with connection management
- **Data Models**: Dataclass-based models (`models.py`) defining Course, Teacher, and CourseAssignment entities with type safety
- **Business Logic**: Separated utility functions (`utils.py`) handling data validation, formatting, and routine generation logic
- **Architecture Pattern**: Layered architecture with clear separation of concerns between presentation (UI), business logic (utils), and data access (database) layers

### Data Storage Solutions
- **Primary Database**: SQLite database (`Class_routine.db`) chosen for simplicity and zero-configuration deployment
- **Schema Design**: Three-table relational structure:
  - `Course`: Stores course metadata (code, name, credit hours)
  - `Teacher`: Contains teacher profiles (code, name, designation)
  - `Course_Teacher`: Junction table managing course assignments with scheduling details (program, semester, day, period)
- **Data Integrity**: Foreign key constraints ensuring referential integrity between related entities
- **Connection Management**: Cached database manager instance preventing connection overhead

### Core Business Logic
- **Academic Structure**: Fixed 6-period daily schedule (6:30 AM - 11:40 AM) with 50-minute periods
- **Program Management**: Support for three distinct academic programs with semester-based organization
- **Schedule Constraints**: Sunday-Friday academic week (6-day schedule, Saturday off) with period-based time slot allocation
- **Conflict Resolution**: Built-in validation preventing scheduling conflicts for teachers and rooms
- **Routine Generation**: Automated timetable creation with program and semester filtering

### Data Validation and Business Rules
- **Input Validation**: Comprehensive client-side validation for all user inputs with real-time error feedback
- **Academic Constraints**: Enforcement of credit hour limits, teacher availability, and scheduling conflicts
- **Schedule Validation**: 6-day weekly schedule (Sunday to Friday, Saturday off) with teacher conflict prevention
- **Data Consistency**: Server-side validation ensuring database integrity and business rule compliance

## External Dependencies

### Core Framework Dependencies
- **Streamlit**: Primary web application framework for rapid UI development and deployment
- **Pandas**: Data manipulation and analysis library for handling routine data structures and transformations
- **SQLite3**: Built-in Python database engine for local data persistence (no external database server required)

### Standard Library Dependencies
- **typing**: Type hints and annotations for improved code maintainability and IDE support
- **dataclasses**: Structured data models without boilerplate code
- **os**: File system operations for database file management

### Development and Testing
- **simple_test.py**: Basic functionality testing module to verify component loading and Streamlit integration