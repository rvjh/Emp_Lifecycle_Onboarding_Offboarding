import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import create_tables, get_connection

# Initialize DB and tables
create_tables()

st.set_page_config(page_title="Employee Lifecycle", layout="wide")

# ---------------------------
# Session Handling
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

# ---------------------------
# LOGIN PAGE
# ---------------------------
def login_page():
    st.markdown("<h1 style='text-align:center;'>🔐 HR Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            st.session_state.login_attempted = True
            if username == "HR_USER" and password == "HR_USER_123":
                st.session_state.logged_in = True
            else:
                st.session_state.logged_in = False
                st.error("Invalid Credentials")

# ---------------------------
# HEADER
# ---------------------------
def header():
    col1, col2 = st.columns([6,1])
    with col1:
        st.markdown("<h2>📊 Employee Lifecycle Management System</h2>", unsafe_allow_html=True)
    with col2:
        with st.expander("👤 HR_USER"):
            st.write("Logged in as HR_USER")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.login_attempted = False
                st.experimental_rerun_safe()

# ---------------------------
# HOME DASHBOARD
# ---------------------------
def home_page():
    st.subheader("🏠 Dashboard Overview")
    conn = get_connection()
    today = datetime.now().date()

    # Onboarding in next 7 days
    onboarding_df = pd.read_sql(
        f"SELECT * FROM employees WHERE joining_date BETWEEN '{today}' AND '{today + timedelta(days=7)}'", conn
    )
    total_onboarding = len(onboarding_df)
    total_freshers = len(onboarding_df[onboarding_df["employee_type"]=="FRESHER"])
    total_experienced = len(onboarding_df[onboarding_df["employee_type"]=="EXPERIENCED"])

    # Offboarding in next 7 days
    offboarding_df = pd.read_sql(
        f"SELECT * FROM employees WHERE last_working_date BETWEEN '{today}' AND '{today + timedelta(days=7)}'", conn
    )
    total_offboarding = len(offboarding_df)

    # Total counts
    total_employees = pd.read_sql("SELECT COUNT(*) AS total FROM employees", conn)["total"].iloc[0]
    total_departments = pd.read_sql("SELECT COUNT(*) AS total FROM departments", conn)["total"].iloc[0]
    total_roles = pd.read_sql("SELECT COUNT(*) AS total FROM roles", conn)["total"].iloc[0]
    total_offers = pd.read_sql("SELECT COUNT(*) AS total FROM offers", conn)["total"].iloc[0]
    total_assets = pd.read_sql("SELECT COUNT(*) AS total FROM assets", conn)["total"].iloc[0]
    total_trainings = pd.read_sql("SELECT COUNT(*) AS total FROM trainings", conn)["total"].iloc[0]

    conn.close()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🟢 Onboarding (Next 7 Days)")
        st.metric("Total Onboarding", total_onboarding)
        st.metric("Freshers", total_freshers)
        st.metric("Experienced", total_experienced)
    with col2:
        st.markdown("### 🔴 Offboarding (Next 7 Days)")
        st.metric("Employees Leaving", total_offboarding)
    with col3:
        st.markdown("### 📌 Company Overview")
        st.metric("Total Employees", total_employees)
        st.metric("Departments", total_departments)
        st.metric("Roles", total_roles)
        st.metric("Offers", total_offers)
        st.metric("Assets", total_assets)
        st.metric("Trainings", total_trainings)

# ---------------------------
# VIEW TABLES
# ---------------------------
def view_tables():
    st.subheader("📂 Database Tables")
    conn = get_connection()
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';", conn)
    st.dataframe(tables)
    conn.close()

# ---------------------------
# VIEW TABLE DATA
# ---------------------------
def view_table_data():
    st.subheader("📊 View Table Data")
    conn = get_connection()
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';", conn)
    table_list = tables["name"].tolist()
    selected_table = st.selectbox("Select Table", table_list)
    if selected_table:
        df = pd.read_sql(f"SELECT * FROM {selected_table} LIMIT 100", conn)
        st.dataframe(df)
    conn.close()

# ---------------------------
# UPLOAD DATA
# ---------------------------
def upload_data():
    st.subheader("📤 Upload CSV / Excel Data")
    conn = get_connection()
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';", conn)
    table_list = tables["name"].tolist()
    selected_table = st.selectbox("Select Table", table_list)

    schema = pd.read_sql(f"PRAGMA table_info({selected_table});", conn)
    columns = schema["name"].tolist()
    st.write("Expected Columns:")
    st.code(columns)

    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv","xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.dataframe(df.head())
        if set(df.columns) == set(columns):
            if st.button("Insert Data"):
                df.to_sql(selected_table, conn, if_exists='append', index=False)
                st.success("Data Inserted Successfully!")
        else:
            st.error("Schema mismatch! Columns must match exactly.")
    conn.close()

# ---------------------------
# ONBOARDING / OFFBOARDING WORKFLOW
# ---------------------------
def workflow_page():
    st.subheader("🛠️ Onboarding / Offboarding Workflow")
    st.info("Tracks employee onboarding, documents, assets, training, projects, resignations, and clearance.")

    conn = get_connection()
    employees_df = pd.read_sql("""
        SELECT e1.employee_id, e1.first_name, e1.last_name, e1.email AS employee_email, 
               e1.employment_status,
               e1.department_id,
               (SELECT email FROM employees e2 WHERE e2.employee_id = e1.manager_id) AS manager_email,
               (SELECT GROUP_CONCAT(asset_id) FROM employee_assets WHERE employee_id = e1.employee_id) AS assets_assigned,
               (SELECT GROUP_CONCAT(training_id) FROM employee_trainings WHERE employee_id = e1.employee_id) AS trainings_assigned,
               (SELECT GROUP_CONCAT(project_id) FROM employee_projects WHERE employee_id = e1.employee_id) AS projects_assigned,
               last_working_date
        FROM employees e1
    """, conn)
    st.dataframe(employees_df)
    conn.close()

# ---------------------------
# SAFE RERUN HELPER
# ---------------------------
def st_experimental_rerun_safe():
    st.session_state["rerun_trigger"] = st.session_state.get("rerun_trigger", 0) + 1
    st.experimental_rerun()

st.experimental_rerun_safe = st_experimental_rerun_safe

# ---------------------------
# MAIN APP
# ---------------------------
if not st.session_state.logged_in:
    login_page()
else:
    header()
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio("Go To", [
        "Home",
        "View Tables",
        "View Table Data",
        "Upload Data",
        "Workflow"
    ])
    if page=="Home":
        home_page()
    elif page=="View Tables":
        view_tables()
    elif page=="View Table Data":
        view_table_data()
    elif page=="Upload Data":
        upload_data()
    elif page=="Workflow":
        workflow_page()
