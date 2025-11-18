"""
Test data generator for creating sample project data similar to Oracle HR schema.
"""

from ..models import Project, Domain, Owner, Table, Diagram
from ..models.base import Column, Key, Index


class TestDataGenerator:
    """Generate test data similar to Oracle's HR schema."""

    @staticmethod
    def generate_hr_schema(project: Project) -> None:
        """
        Generate Oracle HR schema test data with domains, users, tablespaces, and tables.
        This includes classic tables like EMPLOYEES, DEPARTMENTS, JOBS, etc.
        """
        # Clear existing data
        project.domains.clear()
        project.owners.clear()
        project.tables.clear()
        project.diagrams.clear()
        project.foreign_keys.clear()

        # Create domains
        TestDataGenerator._create_domains(project)

        # Create owners (users)
        TestDataGenerator._create_owners(project)

        # Create tables
        TestDataGenerator._create_tables(project)

        # Create diagram
        TestDataGenerator._create_diagram(project)

    @staticmethod
    def _create_domains(project: Project) -> None:
        """Create standard domains for HR schema."""
        domains = [
            Domain("ID_NUMBER", "NUMBER(18, 0)", "Standard ID domain for primary keys"),
            Domain("NAME_VARCHAR", "VARCHAR2(100)", "Standard domain for names"),
            Domain("SHORT_NAME", "VARCHAR2(25)", "Short name domain"),
            Domain("EMAIL_VARCHAR", "VARCHAR2(50)", "Email address domain"),
            Domain("PHONE_VARCHAR", "VARCHAR2(20)", "Phone number domain"),
            Domain("AMOUNT_NUMBER", "NUMBER(10, 2)", "Monetary amount domain"),
            Domain("PERCENTAGE", "NUMBER(3, 2)", "Percentage domain (0-1)"),
            Domain("DATE_TYPE", "DATE", "Standard date domain"),
            Domain("LONG_TEXT", "VARCHAR2(4000)", "Long text field domain"),
            Domain("SMALL_INT", "NUMBER(4, 0)", "Small integer domain"),
            Domain("YEAR_NUMBER", "NUMBER(4, 0)", "Year domain"),
        ]

        for domain in domains:
            project.domains.append(domain)

    @staticmethod
    def _create_owners(project: Project) -> None:
        """Create database owners/users."""
        owners = [
            Owner(
                name="HR",
                default_tablespace="USERS",
                temp_tablespace="TEMP",
                default_index_tablespace="USERS",
                editionable=True,
                comment="HR schema owner"
            ),
            Owner(
                name="SYS",
                default_tablespace="SYSTEM",
                temp_tablespace="TEMP",
                default_index_tablespace="SYSTEM",
                editionable=False,
                comment="System owner"
            ),
        ]

        for owner in owners:
            project.owners.append(owner)

    @staticmethod
    def _create_tables(project: Project) -> None:
        """Create HR schema tables."""

        # REGIONS table
        regions = Table(
            name="REGIONS",
            owner="HR",
            tablespace="USERS",
            stereotype="Business",
            domain="Geographical",
            comment="Regions of the world"
        )
        regions.add_column(Column(
            name="REGION_ID",
            data_type="NUMBER(18, 0)",
            nullable=False,
            domain="ID_NUMBER",
            comment="Region identifier"
        ))
        regions.add_column(Column(
            name="REGION_NAME",
            data_type="VARCHAR2(25)",
            nullable=True,
            domain="SHORT_NAME",
            comment="Name of the region"
        ))
        regions.add_key(Key(
            name="REGIONS_PK",
            columns=["REGION_ID"]
        ))
        project.tables.append(regions)

        # COUNTRIES table
        countries = Table(
            name="COUNTRIES",
            owner="HR",
            tablespace="USERS",
            stereotype="Business",
            domain="Geographical",
            comment="Countries of the world"
        )
        countries.add_column(Column(
            name="COUNTRY_ID",
            data_type="VARCHAR2(25)",
            nullable=False,
            domain="SHORT_NAME",
            comment="Country identifier (ISO code)"
        ))
        countries.add_column(Column(
            name="COUNTRY_NAME",
            data_type="VARCHAR2(100)",
            nullable=True,
            domain="NAME_VARCHAR",
            comment="Country name"
        ))
        countries.add_column(Column(
            name="REGION_ID",
            data_type="NUMBER(18, 0)",
            nullable=True,
            domain="ID_NUMBER",
            comment="Region where country belongs"
        ))
        countries.add_key(Key(
            name="COUNTRIES_PK",
            columns=["COUNTRY_ID"]
        ))
        countries.add_key(Key(
            name="COUNTRIES_REGION_FK",
            columns=["REGION_ID"]
        ))
        project.tables.append(countries)

        # LOCATIONS table
        locations = Table(
            name="LOCATIONS",
            owner="HR",
            tablespace="USERS",
            stereotype="Business",
            domain="Geographical",
            comment="Office locations"
        )
        locations.add_column(Column(
            name="LOCATION_ID",
            data_type="NUMBER(18, 0)",
            nullable=False,
            domain="ID_NUMBER",
            comment="Location identifier"
        ))
        locations.add_column(Column(
            name="STREET_ADDRESS",
            data_type="VARCHAR2(100)",
            nullable=True,
            domain="NAME_VARCHAR",
            comment="Street address"
        ))
        locations.add_column(Column(
            name="POSTAL_CODE",
            data_type="VARCHAR2(25)",
            nullable=True,
            domain="SHORT_NAME",
            comment="Postal code"
        ))
        locations.add_column(Column(
            name="CITY",
            data_type="VARCHAR2(100)",
            nullable=False,
            domain="NAME_VARCHAR",
            comment="City name"
        ))
        locations.add_column(Column(
            name="STATE_PROVINCE",
            data_type="VARCHAR2(100)",
            nullable=True,
            domain="NAME_VARCHAR",
            comment="State or province"
        ))
        locations.add_column(Column(
            name="COUNTRY_ID",
            data_type="VARCHAR2(25)",
            nullable=True,
            domain="SHORT_NAME",
            comment="Country identifier"
        ))
        locations.add_key(Key(
            name="LOCATIONS_PK",
            columns=["LOCATION_ID"]
        ))
        locations.add_key(Key(
            name="LOCATIONS_COUNTRY_FK",
            columns=["COUNTRY_ID"]
        ))
        project.tables.append(locations)

        # DEPARTMENTS table
        departments = Table(
            name="DEPARTMENTS",
            owner="HR",
            tablespace="USERS",
            stereotype="Business",
            domain="Organization",
            comment="Company departments"
        )
        departments.add_column(Column(
            name="DEPARTMENT_ID",
            data_type="NUMBER(18, 0)",
            nullable=False,
            domain="ID_NUMBER",
            comment="Department identifier"
        ))
        departments.add_column(Column(
            name="DEPARTMENT_NAME",
            data_type="VARCHAR2(100)",
            nullable=False,
            domain="NAME_VARCHAR",
            comment="Department name"
        ))
        departments.add_column(Column(
            name="MANAGER_ID",
            data_type="NUMBER(18, 0)",
            nullable=True,
            domain="ID_NUMBER",
            comment="Manager employee ID"
        ))
        departments.add_column(Column(
            name="LOCATION_ID",
            data_type="NUMBER(18, 0)",
            nullable=True,
            domain="ID_NUMBER",
            comment="Location identifier"
        ))
        departments.add_key(Key(
            name="DEPARTMENTS_PK",
            columns=["DEPARTMENT_ID"]
        ))
        departments.add_key(Key(
            name="DEPARTMENTS_LOC_FK",
            columns=["LOCATION_ID"]
        ))
        project.tables.append(departments)

        # JOBS table
        jobs = Table(
            name="JOBS",
            owner="HR",
            tablespace="USERS",
            stereotype="Business",
            domain="Organization",
            comment="Job definitions"
        )
        jobs.add_column(Column(
            name="JOB_ID",
            data_type="VARCHAR2(25)",
            nullable=False,
            domain="SHORT_NAME",
            comment="Job identifier"
        ))
        jobs.add_column(Column(
            name="JOB_TITLE",
            data_type="VARCHAR2(100)",
            nullable=False,
            domain="NAME_VARCHAR",
            comment="Job title"
        ))
        jobs.add_column(Column(
            name="MIN_SALARY",
            data_type="NUMBER(10, 2)",
            nullable=True,
            domain="AMOUNT_NUMBER",
            comment="Minimum salary"
        ))
        jobs.add_column(Column(
            name="MAX_SALARY",
            data_type="NUMBER(10, 2)",
            nullable=True,
            domain="AMOUNT_NUMBER",
            comment="Maximum salary"
        ))
        jobs.add_key(Key(
            name="JOBS_PK",
            columns=["JOB_ID"]
        ))
        project.tables.append(jobs)

        # EMPLOYEES table
        employees = Table(
            name="EMPLOYEES",
            owner="HR",
            tablespace="USERS",
            stereotype="Business",
            domain="Organization",
            comment="Employee information"
        )
        employees.add_column(Column(
            name="EMPLOYEE_ID",
            data_type="NUMBER(18, 0)",
            nullable=False,
            domain="ID_NUMBER",
            comment="Employee identifier"
        ))
        employees.add_column(Column(
            name="FIRST_NAME",
            data_type="VARCHAR2(100)",
            nullable=True,
            domain="NAME_VARCHAR",
            comment="First name"
        ))
        employees.add_column(Column(
            name="LAST_NAME",
            data_type="VARCHAR2(100)",
            nullable=False,
            domain="NAME_VARCHAR",
            comment="Last name"
        ))
        employees.add_column(Column(
            name="EMAIL",
            data_type="VARCHAR2(50)",
            nullable=False,
            domain="EMAIL_VARCHAR",
            comment="Email address"
        ))
        employees.add_column(Column(
            name="PHONE_NUMBER",
            data_type="VARCHAR2(20)",
            nullable=True,
            domain="PHONE_VARCHAR",
            comment="Phone number"
        ))
        employees.add_column(Column(
            name="HIRE_DATE",
            data_type="DATE",
            nullable=False,
            domain="DATE_TYPE",
            comment="Date employee was hired"
        ))
        employees.add_column(Column(
            name="JOB_ID",
            data_type="VARCHAR2(25)",
            nullable=False,
            domain="SHORT_NAME",
            comment="Current job identifier"
        ))
        employees.add_column(Column(
            name="SALARY",
            data_type="NUMBER(10, 2)",
            nullable=True,
            domain="AMOUNT_NUMBER",
            comment="Current salary"
        ))
        employees.add_column(Column(
            name="COMMISSION_PCT",
            data_type="NUMBER(3, 2)",
            nullable=True,
            domain="PERCENTAGE",
            comment="Commission percentage"
        ))
        employees.add_column(Column(
            name="MANAGER_ID",
            data_type="NUMBER(18, 0)",
            nullable=True,
            domain="ID_NUMBER",
            comment="Manager employee ID"
        ))
        employees.add_column(Column(
            name="DEPARTMENT_ID",
            data_type="NUMBER(18, 0)",
            nullable=True,
            domain="ID_NUMBER",
            comment="Department identifier"
        ))
        employees.add_key(Key(
            name="EMPLOYEES_PK",
            columns=["EMPLOYEE_ID"]
        ))
        employees.add_key(Key(
            name="EMPLOYEES_JOB_FK",
            columns=["JOB_ID"]
        ))
        employees.add_key(Key(
            name="EMPLOYEES_DEPT_FK",
            columns=["DEPARTMENT_ID"]
        ))
        employees.add_key(Key(
            name="EMPLOYEES_MGR_FK",
            columns=["MANAGER_ID"]
        ))
        # Add unique constraint on email
        employees.add_key(Key(
            name="EMPLOYEES_EMAIL_UK",
            columns=["EMAIL"]
        ))
        # Add index on department_id
        employees.add_index(Index(
            name="EMPLOYEES_DEPT_IDX",
            columns=["DEPARTMENT_ID"],
            tablespace="USERS"
        ))
        project.tables.append(employees)

        # JOB_HISTORY table
        job_history = Table(
            name="JOB_HISTORY",
            owner="HR",
            tablespace="USERS",
            stereotype="Business",
            domain="Organization",
            comment="Job history of employees"
        )
        job_history.add_column(Column(
            name="EMPLOYEE_ID",
            data_type="NUMBER(18, 0)",
            nullable=False,
            domain="ID_NUMBER",
            comment="Employee identifier"
        ))
        job_history.add_column(Column(
            name="START_DATE",
            data_type="DATE",
            nullable=False,
            domain="DATE_TYPE",
            comment="Start date of the job"
        ))
        job_history.add_column(Column(
            name="END_DATE",
            data_type="DATE",
            nullable=False,
            domain="DATE_TYPE",
            comment="End date of the job"
        ))
        job_history.add_column(Column(
            name="JOB_ID",
            data_type="VARCHAR2(25)",
            nullable=False,
            domain="SHORT_NAME",
            comment="Job identifier"
        ))
        job_history.add_column(Column(
            name="DEPARTMENT_ID",
            data_type="NUMBER(18, 0)",
            nullable=True,
            domain="ID_NUMBER",
            comment="Department identifier"
        ))
        job_history.add_key(Key(
            name="JOB_HISTORY_PK",
            columns=["EMPLOYEE_ID", "START_DATE"]
        ))
        job_history.add_key(Key(
            name="JOB_HISTORY_EMP_FK",
            columns=["EMPLOYEE_ID"]
        ))
        job_history.add_key(Key(
            name="JOB_HISTORY_JOB_FK",
            columns=["JOB_ID"]
        ))
        job_history.add_key(Key(
            name="JOB_HISTORY_DEPT_FK",
            columns=["DEPARTMENT_ID"]
        ))
        project.tables.append(job_history)

        # Add self-referencing FK for DEPARTMENTS.MANAGER_ID
        departments.add_key(Key(
            name="DEPARTMENTS_MGR_FK",
            columns=["MANAGER_ID"]
        ))

    @staticmethod
    def _create_diagram(project: Project) -> None:
        """Create a diagram with all tables."""
        diagram = Diagram(
            name="HR Schema Overview",
            description="Complete HR schema diagram"
        )

        # Add all tables to the diagram with positions
        positions = {
            "REGIONS": (50, 50),
            "COUNTRIES": (50, 250),
            "LOCATIONS": (50, 450),
            "DEPARTMENTS": (400, 350),
            "JOBS": (400, 50),
            "EMPLOYEES": (750, 200),
            "JOB_HISTORY": (750, 500),
        }

        for table in project.tables:
            if table.name in positions:
                x, y = positions[table.name]
                full_name = f"{table.owner}.{table.name}"
                diagram.add_item("table", full_name, x, y)

        project.diagrams.append(diagram)

