import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "hr_lifecycle.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def drop_all_tables(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        if table[0] != "metadata" and table[0] != "sqlite_sequence":
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
    conn.commit()
    cursor.execute("PRAGMA foreign_keys = ON;")

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- METADATA ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    cursor.execute("SELECT value FROM metadata WHERE key='initialized'")
    if cursor.fetchone():
        conn.close()
        return

    drop_all_tables(conn)

    # ---------------- DEPARTMENTS ----------------
    cursor.execute("""
    CREATE TABLE departments (
        department_id TEXT PRIMARY KEY,
        department_name TEXT
    );
    """)

    # ---------------- ROLES ----------------
    cursor.execute("""
    CREATE TABLE roles (
        role_id TEXT PRIMARY KEY,
        role_name TEXT,
        description TEXT
    );
    """)

    # ---------------- EMPLOYEES ----------------
    cursor.execute("""
    CREATE TABLE employees (
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
        last_working_date TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(department_id) REFERENCES departments(department_id),
        FOREIGN KEY(manager_id) REFERENCES employees(employee_id)
    );
    """)

    # ---------------- OFFERS ----------------
    cursor.execute("""
    CREATE TABLE offers (
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

    # ---------------- DOCUMENTS ----------------
    cursor.execute("""
    CREATE TABLE document_types (
        document_type_id TEXT PRIMARY KEY,
        name TEXT,
        mandatory_for TEXT,
        required_stage TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE employee_documents (
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

    # ---------------- EMPLOYEE ROLES ----------------
    cursor.execute("""
    CREATE TABLE employee_roles (
        employee_role_id TEXT PRIMARY KEY,
        employee_id TEXT,
        role_id TEXT,
        assigned_at TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY(role_id) REFERENCES roles(role_id)
    );
    """)

    # ---------------- ASSETS ----------------
    cursor.execute("""
    CREATE TABLE assets (
        asset_id TEXT PRIMARY KEY,
        asset_type TEXT,
        asset_number TEXT,
        status TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE employee_assets (
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

    # ---------------- ACCESS ----------------
    cursor.execute("""
    CREATE TABLE access_types (
        access_type_id TEXT PRIMARY KEY,
        access_name TEXT,
        role_based INTEGER
    );
    """)
    cursor.execute("""
    CREATE TABLE employee_access (
        emp_access_id TEXT PRIMARY KEY,
        employee_id TEXT,
        access_type_id TEXT,
        granted_date TEXT,
        revoked_date TEXT,
        status TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY(access_type_id) REFERENCES access_types(access_type_id)
    );
    """)

    # ---------------- TRAININGS ----------------
    cursor.execute("""
    CREATE TABLE trainings (
        training_id TEXT PRIMARY KEY,
        training_name TEXT,
        training_type TEXT,
        created_by TEXT,
        link TEXT,
        description TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE employee_trainings (
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

    # ---------------- PROJECTS ----------------
    cursor.execute("""
    CREATE TABLE projects (
        project_id TEXT PRIMARY KEY,
        project_name TEXT,
        objective TEXT,
        start_date TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE employee_projects (
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

    # ---------------- RESIGNATIONS ----------------
    cursor.execute("""
    CREATE TABLE resignations (
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
    cursor.execute("""
    CREATE TABLE exit_interviews (
        exit_id TEXT PRIMARY KEY,
        employee_id TEXT,
        interview_date TEXT,
        feedback TEXT,
        full_and_final_date TEXT,
        experience_letter_sent INTEGER,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE clearance_checklist (
        clearance_id TEXT PRIMARY KEY,
        employee_id TEXT,
        asset_cleared INTEGER,
        access_revoked INTEGER,
        id_card_returned INTEGER,
        laptop_returned INTEGER,
        nda_signed INTEGER,
        manager_approved INTEGER,
        hr_approved INTEGER,
        completed_at TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
    );
    """)

    # ---------------- WORKFLOW TASKS ----------------
    cursor.execute("""
    CREATE TABLE workflow_tasks (
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
    insert_sample_data(conn)
    cursor.execute("INSERT INTO metadata VALUES ('initialized','true')")
    conn.commit()
    conn.close()


# -------------------- SAMPLE DATA --------------------
def insert_sample_data(conn):
    cursor = conn.cursor()
    today = datetime.now().date()

    # ---------------- DEPARTMENTS ----------------
    dept_names = ["HR","Engineering","Finance","Marketing","Operations",
                  "IT Support","Sales","Legal","Customer Success","R&D"]
    depts = [f"dep_id_{i+1}" for i in range(len(dept_names))]
    for d, n in zip(depts, dept_names):
        cursor.execute("INSERT INTO departments VALUES (?,?)",(d,n))

    # ---------------- ROLES ----------------
    role_names = ["HR Manager","Team Lead","Software Engineer","DevOps","Finance Analyst",
                  "Marketing Manager","Operations Lead","Support Engineer","Legal Advisor",
                  "Product Manager"]
    role_ids = [f"role_id_{i+1}" for i in range(len(role_names))]
    for r, n in zip(role_ids, role_names):
        cursor.execute("INSERT INTO roles VALUES (?,?,?)",(r,n,f"{n} role"))

    # ---------------- EMPLOYEES ----------------
    first_names = ["Rahul","Priya","Amit","Sneha","Vikram","Neha","Arjun","Pooja","Karan","Anjali"]
    last_names = ["Sharma","Mehta","Verma","Reddy","Singh","Kapoor","Nair","Iyer","Malhotra","Desai"]
    employee_ids = [f"emp_id_{i+1}" for i in range(10)]
    manager_map = [None, None, "emp_id_1", "emp_id_1", "emp_id_2", "emp_id_2", "emp_id_3", "emp_id_3", "emp_id_4", "emp_id_4"]

    for i in range(10):
        j_date = today + timedelta(days=random.randint(0,10))   # onboarding in next 10 days
        a_date = j_date + timedelta(days=1)
        # Make some employees leave in next 7 days for offboarding
        l_date = today + timedelta(days=random.randint(1,7)) if i < 3 else None
        dept_id = random.choice(depts)
        emp_type = random.choice(["FRESHER","EXPERIENCED"])
        emp_status = "PREJOIN" if j_date > today else "ACTIVE"
        if l_date:
            emp_status = "RESIGNED"
        cursor.execute("""
        INSERT INTO employees (
            employee_id, first_name, last_name, email, phone, employee_type,
            employment_status, department_id, manager_id, hr_id,
            joining_date, actual_joining_date, last_working_date,
            created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            employee_ids[i],
            first_names[i],
            last_names[i],
            f"{first_names[i].lower()}.{last_names[i].lower()}@company.com",
            f"98765432{i+10}",
            emp_type,
            emp_status,
            dept_id,
            manager_map[i],
            "HR_USER",
            str(j_date),
            str(a_date),
            str(l_date) if l_date else None,
            str(datetime.now()),
            str(datetime.now())
        ))

    # ---------------- OFFERS ----------------
    for emp_id in employee_ids:
        cursor.execute("INSERT INTO offers VALUES (?,?,?,?,?,?,?,?)",(
            f"offer_{emp_id}",
            emp_id,
            random.choice(["PENDING","ACCEPTED","REJECTED"]),
            str(today + timedelta(days=random.randint(0,5))),
            random.choice(["Office","Home"]),
            random.choice(["CONFIRMED","NOT_CONFIRMED"]),
            random.randint(0,1),
            "Remarks"
        ))

    # ---------------- ASSETS ----------------
    asset_types = ["Laptop","Mobile","Access Card","Headset"]
    asset_ids = [f"asset_{i+1}" for i in range(10)]
    for a_id, atype in zip(asset_ids, asset_types*3):
        cursor.execute("INSERT INTO assets VALUES (?,?,?,?)",(a_id,atype,f"{atype[:3]}-{random.randint(1000,9999)}","Assigned"))
    for emp_id, asset_id in zip(employee_ids, asset_ids):
        cursor.execute("INSERT INTO employee_assets VALUES (?,?,?,?,?,?)",(
            f"emp_asset_{emp_id}",
            emp_id,
            asset_id,
            str(today),
            None,
            "Assigned"
        ))

    # ---------------- ACCESS ----------------
    access_types = ["Admin Panel","Payroll","Project Repo","Email System"]
    access_ids = [f"access_{i+1}" for i in range(len(access_types))]
    for a_id, a_name in zip(access_ids, access_types):
        cursor.execute("INSERT INTO access_types VALUES (?,?,?)",(a_id,a_name,random.randint(0,1)))
    for emp_id, access_id in zip(employee_ids, access_ids*3):
        cursor.execute("INSERT INTO employee_access VALUES (?,?,?,?,?,?)",(
            f"emp_access_{emp_id}_{access_id}",
            emp_id,
            access_id,
            str(today),
            None,
            "Active"
        ))

    # ---------------- TRAININGS ----------------
    training_ids = [f"train_{i+1}" for i in range(5)]
    training_names = ["Safety","Orientation","Technical","Compliance","Leadership"]
    for t_id, t_name in zip(training_ids, training_names):
        cursor.execute("INSERT INTO trainings VALUES (?,?,?,?,?,?)",(
            t_id,
            t_name,
            "Mandatory",
            "HR_USER",
            f"http://link.com/{t_name.lower()}",
            f"{t_name} training description"
        ))
    for emp_id in employee_ids:
        t_id = random.choice(training_ids)
        cursor.execute("INSERT INTO employee_trainings VALUES (?,?,?,?,?,?)",(
            f"emp_train_{emp_id}",
            emp_id,
            t_id,
            "HR_USER",
            random.choice(["Pending","Completed"]),
            str(today + timedelta(days=random.randint(1,10)))
        ))

    # ---------------- PROJECTS ----------------
    project_ids = [f"proj_{i+1}" for i in range(5)]
    project_names = ["Website Revamp","Mobile App","CRM Integration","Marketing Campaign","Data Analytics"]
    for p_id, p_name in zip(project_ids, project_names):
        cursor.execute("INSERT INTO projects VALUES (?,?,?,?)",(
            p_id,
            p_name,
            f"Objective of {p_name}",
            str(today - timedelta(days=random.randint(10,30)))
        ))
    for emp_id in employee_ids:
        p_id = random.choice(project_ids)
        cursor.execute("INSERT INTO employee_projects VALUES (?,?,?,?,?,?)",(
            f"emp_proj_{emp_id}",
            emp_id,
            p_id,
            str(today),
            f"http://kt.com/{p_id}",
            random.choice(["Pending","Completed"])
        ))

    # ---------------- DOCUMENT TYPES ----------------
    doc_types = ["ID Proof","Address Proof","Resume","Offer Letter"]
    doc_ids = [f"doc_type_{i+1}" for i in range(len(doc_types))]
    for d_id, d_name in zip(doc_ids, doc_types):
        cursor.execute("INSERT INTO document_types VALUES (?,?,?,?)",(d_id,d_name,"ALL","Onboarding"))
    for emp_id in employee_ids:
        doc_id = random.choice(doc_ids)
        cursor.execute("INSERT INTO employee_documents VALUES (?,?,?,?,?,?,?)",(
            f"emp_doc_{emp_id}",
            emp_id,
            doc_id,
            f"/files/{emp_id}_{doc_id}.pdf",
            random.choice(["Verified","Pending"]),
            str(today),
            "HR_USER"
        ))

    # ---------------- EMPLOYEE ROLES ----------------
    for emp_id, role_id in zip(employee_ids, role_ids*2):
        cursor.execute("INSERT INTO employee_roles VALUES (?,?,?,?)",(
            f"emp_role_{emp_id}",
            emp_id,
            role_id,
            str(today)
        ))

    # ---------------- RESIGNATIONS, EXIT INTERVIEWS, CLEARANCE ----------------
    for emp_id in employee_ids[:3]:  # first 3 have offboarding in next 7 days
        l_date = today + timedelta(days=random.randint(1,7))
        res_date = today - timedelta(days=random.randint(1,3))
        cursor.execute("INSERT INTO resignations VALUES (?,?,?,?,?,?,?,?)",(
            f"res_{emp_id}",
            emp_id,
            str(res_date),
            "Personal",
            "Manager approved",
            "HR approved",
            str(l_date),
            "Approved"
        ))
        cursor.execute("INSERT INTO exit_interviews VALUES (?,?,?,?,?,?)",(
            f"exit_{emp_id}",
            emp_id,
            str(today),
            "Good experience",
            str(l_date + timedelta(days=1)),
            1
        ))
        cursor.execute("INSERT INTO clearance_checklist VALUES (?,?,?,?,?,?,?,?,?,?)",(
            f"clear_{emp_id}",
            emp_id,
            1,1,1,1,1,1,1,
            str(today)
        ))

    # ---------------- WORKFLOW TASKS ----------------
    for emp_id in employee_ids:
        cursor.execute("INSERT INTO workflow_tasks VALUES (?,?,?,?,?,?,?,?)",(
            f"task_{emp_id}",
            emp_id,
            random.choice(["Onboarding","Offboarding","Training","Project"]),
            "HR_USER",
            str(today + timedelta(days=random.randint(1,7))),
            random.choice(["Pending","Completed"]),
            "{}",
            str(datetime.now())
        ))

    conn.commit()

if __name__ == "__main__":
    create_tables()
