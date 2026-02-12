import sqlite3
import uuid
import random
from datetime import datetime, timedelta

DB_NAME = "hr_lifecycle.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Employees
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        employee_type TEXT,
        employment_status TEXT,
        department_id TEXT,
        manager_id TEXT,
        hr_id TEXT,
        joining_date TEXT,
        actual_joining_date TEXT,
        last_working_date TEXT
    );
    """)

    # Departments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        department_id TEXT PRIMARY KEY,
        department_name TEXT
    );
    """)

    # Offers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS offers (
        offer_id TEXT PRIMARY KEY,
        employee_id TEXT,
        offer_status TEXT,
        joining_date_offered TEXT,
        joining_venue TEXT,
        confirmation_status TEXT,
        change_requested INTEGER,
        remarks TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
    );
    """)

    # Document Types
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document_types (
        document_type_id TEXT PRIMARY KEY,
        name TEXT,
        mandatory_for TEXT,
        required_stage TEXT
    );
    """)

    # Employee Documents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_documents (
        emp_doc_id TEXT PRIMARY KEY,
        employee_id TEXT,
        document_type_id TEXT,
        file_path TEXT,
        verification_status TEXT,
        uploaded_at TEXT,
        verified_by TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY(document_type_id) REFERENCES document_types(document_type_id)
    );
    """)

    # Assets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        asset_id TEXT PRIMARY KEY,
        asset_type TEXT,
        asset_number TEXT,
        status TEXT
    );
    """)

    # Employee Assets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_assets (
        employee_asset_id TEXT PRIMARY KEY,
        employee_id TEXT,
        asset_id TEXT,
        assigned_date TEXT,
        returned_date TEXT,
        asset_status TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY(asset_id) REFERENCES assets(asset_id)
    );
    """)

    # Trainings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trainings (
        training_id TEXT PRIMARY KEY,
        training_name TEXT,
        training_type TEXT,
        created_by TEXT,
        link TEXT,
        description TEXT
    );
    """)

    # Employee Trainings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_trainings (
        emp_training_id TEXT PRIMARY KEY,
        employee_id TEXT,
        training_id TEXT,
        assigned_by TEXT,
        status TEXT,
        completion_date TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY(training_id) REFERENCES trainings(training_id)
    );
    """)

    # Projects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY,
        project_name TEXT,
        objective TEXT,
        start_date TEXT
    );
    """)

    # Employee Projects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_projects (
        emp_project_id TEXT PRIMARY KEY,
        employee_id TEXT,
        project_id TEXT,
        onboarding_date TEXT,
        kt_link TEXT,
        kt_status TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    );
    """)

    # Resignations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resignations (
        resignation_id TEXT PRIMARY KEY,
        employee_id TEXT,
        resignation_date TEXT,
        reason TEXT,
        manager_comments TEXT,
        hr_comments TEXT,
        last_working_date TEXT,
        status TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
    );
    """)

    # Exit Interviews
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exit_interviews (
        exit_id TEXT PRIMARY KEY,
        employee_id TEXT,
        interview_date TEXT,
        feedback TEXT,
        full_and_final_date TEXT,
        experience_letter_sent INTEGER,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
    );
    """)

    # Workflow Tasks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workflow_tasks (
        task_id TEXT PRIMARY KEY,
        employee_id TEXT,
        task_type TEXT,
        assigned_to TEXT,
        due_date TEXT,
        status TEXT,
        metadata TEXT,
        created_at TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
    );
    """)

    conn.commit()
    conn.close()


def insert_dummy_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    dept_ids = [str(uuid.uuid4()) for _ in range(10)]
    for i in range(10):
        cursor.execute("INSERT INTO departments VALUES (?,?)",
                       (dept_ids[i], f"Department_{i}"))

    emp_ids = []
    for i in range(10):
        emp_id = str(uuid.uuid4())
        emp_ids.append(emp_id)
        cursor.execute("""
        INSERT INTO employees VALUES (?,?,?,?,?,?,?,?,?,?,?, ?,?)
        """, (
            emp_id,
            f"First{i}",
            f"Last{i}",
            f"user{i}@company.com",
            f"99999999{i}",
            random.choice(["FRESHER", "EXPERIENCED"]),
            "ACTIVE",
            dept_ids[i],
            None,
            "HR_USER",
            str(datetime.now().date()),
            str(datetime.now().date()),
            None
        ))

    for i in range(10):
        cursor.execute("INSERT INTO offers VALUES (?,?,?,?,?,?,?,?)",
                       (str(uuid.uuid4()), emp_ids[i], "ACCEPTED",
                        str(datetime.now().date()), "Office_A",
                        "CONFIRMED", 0, "No remarks"))

    for i in range(10):
        doc_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO document_types VALUES (?,?,?,?)",
                       (doc_id, f"Doc_{i}", "ALL", "ONBOARD"))

        cursor.execute("INSERT INTO employee_documents VALUES (?,?,?,?,?,?,?)",
                       (str(uuid.uuid4()), emp_ids[i], doc_id,
                        "/path/file.pdf", "VERIFIED",
                        str(datetime.now()), "HR_USER"))

    asset_ids = []
    for i in range(10):
        asset_id = str(uuid.uuid4())
        asset_ids.append(asset_id)
        cursor.execute("INSERT INTO assets VALUES (?,?,?,?)",
                       (asset_id, "LAPTOP", f"LAP{i}", "ASSIGNED"))

        cursor.execute("INSERT INTO employee_assets VALUES (?,?,?,?,?,?)",
                       (str(uuid.uuid4()), emp_ids[i], asset_id,
                        str(datetime.now().date()), None, "ASSIGNED"))

    training_ids = []
    for i in range(10):
        training_id = str(uuid.uuid4())
        training_ids.append(training_id)
        cursor.execute("INSERT INTO trainings VALUES (?,?,?,?,?,?)",
                       (training_id, f"Training_{i}", "MANDATORY",
                        "HR_USER", "http://link.com", "Description"))

        cursor.execute("INSERT INTO employee_trainings VALUES (?,?,?,?,?,?)",
                       (str(uuid.uuid4()), emp_ids[i], training_id,
                        "Manager", "COMPLETED",
                        str(datetime.now().date())))

    project_ids = []
    for i in range(10):
        project_id = str(uuid.uuid4())
        project_ids.append(project_id)
        cursor.execute("INSERT INTO projects VALUES (?,?,?,?)",
                       (project_id, f"Project_{i}",
                        "Objective", str(datetime.now().date())))

        cursor.execute("INSERT INTO employee_projects VALUES (?,?,?,?,?,?)",
                       (str(uuid.uuid4()), emp_ids[i], project_id,
                        str(datetime.now().date()),
                        "http://ktlink.com", "COMPLETED"))

    for i in range(10):
        cursor.execute("INSERT INTO resignations VALUES (?,?,?,?,?,?,?,?)",
                       (str(uuid.uuid4()), emp_ids[i],
                        str(datetime.now().date()), "Personal",
                        "Approved", "Processed",
                        str(datetime.now().date()), "COMPLETED"))

        cursor.execute("INSERT INTO exit_interviews VALUES (?,?,?,?,?,?)",
                       (str(uuid.uuid4()), emp_ids[i],
                        str(datetime.now().date()), "Good",
                        str(datetime.now().date()), 1))

        cursor.execute("INSERT INTO workflow_tasks VALUES (?,?,?,?,?,?,?,?)",
                       (str(uuid.uuid4()), emp_ids[i],
                        "DOC_UPLOAD", "HR_USER",
                        str(datetime.now().date()),
                        "COMPLETED", "{}", str(datetime.now())))

    conn.commit()
    conn.close()
