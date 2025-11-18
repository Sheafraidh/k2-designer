# Test Data Generation Feature

## Overview
Added a menu option to generate test data similar to Oracle's HR schema. This feature populates the current project with sample domains, users, tables, and a diagram for testing purposes.

## Implementation Date
November 18, 2025

## Files Created
- `src/k2_designer/controllers/test_data_generator.py` - Test data generator class

## Files Modified
- `src/k2_designer/views/main_window.py` - Added menu action and handler

## Feature Details

### Menu Location
**Tools → Generate Test Data (HR Schema)**

### What It Does
When activated, the feature:
1. Shows a confirmation dialog explaining what will be replaced
2. Clears all existing project data (domains, owners, tables, diagrams)
3. Generates Oracle HR schema-like data:
   - **11 Domains**: ID_NUMBER, NAME_VARCHAR, SHORT_NAME, EMAIL_VARCHAR, PHONE_VARCHAR, AMOUNT_NUMBER, PERCENTAGE, DATE_TYPE, LONG_TEXT, SMALL_INT, YEAR_NUMBER
   - **2 Users/Owners**: HR (with USERS tablespace) and SYS (with SYSTEM tablespace)
   - **7 Tables**: REGIONS, COUNTRIES, LOCATIONS, DEPARTMENTS, JOBS, EMPLOYEES, JOB_HISTORY
   - **1 Diagram**: "HR Schema Overview" with all tables positioned
4. Refreshes the UI and opens the generated diagram
5. Shows a success message

### Generated Tables

#### REGIONS
- REGION_ID (NUMBER(18, 0), PK)
- REGION_NAME (VARCHAR2(25))

#### COUNTRIES
- COUNTRY_ID (VARCHAR2(25), PK)
- COUNTRY_NAME (VARCHAR2(100))
- REGION_ID (NUMBER(18, 0), FK to REGIONS)

#### LOCATIONS
- LOCATION_ID (NUMBER(18, 0), PK)
- STREET_ADDRESS (VARCHAR2(100))
- POSTAL_CODE (VARCHAR2(25))
- CITY (VARCHAR2(100), NOT NULL)
- STATE_PROVINCE (VARCHAR2(100))
- COUNTRY_ID (VARCHAR2(25), FK to COUNTRIES)

#### DEPARTMENTS
- DEPARTMENT_ID (NUMBER(18, 0), PK)
- DEPARTMENT_NAME (VARCHAR2(100), NOT NULL)
- MANAGER_ID (NUMBER(18, 0), FK to EMPLOYEES)
- LOCATION_ID (NUMBER(18, 0), FK to LOCATIONS)

#### JOBS
- JOB_ID (VARCHAR2(25), PK)
- JOB_TITLE (VARCHAR2(100), NOT NULL)
- MIN_SALARY (NUMBER(10, 2))
- MAX_SALARY (NUMBER(10, 2))

#### EMPLOYEES
- EMPLOYEE_ID (NUMBER(18, 0), PK)
- FIRST_NAME (VARCHAR2(100))
- LAST_NAME (VARCHAR2(100), NOT NULL)
- EMAIL (VARCHAR2(50), NOT NULL, UK)
- PHONE_NUMBER (VARCHAR2(20))
- HIRE_DATE (DATE, NOT NULL)
- JOB_ID (VARCHAR2(25), NOT NULL, FK to JOBS)
- SALARY (NUMBER(10, 2))
- COMMISSION_PCT (NUMBER(3, 2))
- MANAGER_ID (NUMBER(18, 0), FK to EMPLOYEES - self-referencing)
- DEPARTMENT_ID (NUMBER(18, 0), FK to DEPARTMENTS)

Indexes:
- EMPLOYEES_DEPT_IDX on DEPARTMENT_ID

#### JOB_HISTORY
- EMPLOYEE_ID (NUMBER(18, 0), PK, FK to EMPLOYEES)
- START_DATE (DATE, PK)
- END_DATE (DATE, NOT NULL)
- JOB_ID (VARCHAR2(25), NOT NULL, FK to JOBS)
- DEPARTMENT_ID (NUMBER(18, 0), FK to DEPARTMENTS)

### Features Demonstrated
This test data demonstrates:
- Primary keys
- Foreign keys (including self-referencing)
- Unique constraints
- Indexes
- Not null constraints
- Domains with different data types
- Multiple users with tablespace configurations
- Complex relationships between tables
- Proper table positioning in diagrams

### Usage
1. Create or open a project
2. Go to **Tools → Generate Test Data (HR Schema)**
3. Confirm the action in the dialog
4. The project will be populated with test data
5. The HR Schema Overview diagram will automatically open

### Warning
This action will **replace all existing project data**. Users are warned via a confirmation dialog before proceeding.

## Technical Notes

### Implementation Details
- Uses the existing model classes (Domain, Owner, Table, Column, Key, Index, Diagram)
- All columns properly reference domains
- Tables are assigned to the "Business" stereotype
- Tables are organized by domain (Geographical, Organization)
- Tables include proper comments for documentation
- Diagram positions tables in a logical layout

### Error Handling
- Checks if a project is open before allowing generation
- Shows error dialog if generation fails
- Uses try-except to catch and display any exceptions

### Code Quality
- Clean separation of concerns with dedicated generator class
- Static methods for easy testing
- Comprehensive comments explaining each table and column
- Follows existing code patterns and conventions

