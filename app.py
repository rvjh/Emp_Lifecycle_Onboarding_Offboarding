import streamlit as st
import pandas as pd
from datetime import datetime
from database import create_tables, insert_dummy_data, get_connection

# Initialize DB
create_tables()
insert_dummy_data()

st.set_page_config(page_title="Employee Lifecycle", layout="wide")

# ---------------------------
# Session Handling
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


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
            if username == "HR_USER" and password == "HR_USER_123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")


# ---------------------------
# HEADER
# ---------------------------
def header():
    col1, col2 = st.columns([6,1])
    with col1:
        st.markdown("<h2>📊 Employee Lifecycle Management System</h2>", unsafe_allow_html=True)
    with col2:
        with st.popover("👤 HR_USER"):
            st.write("Logged in as HR_USER")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()


# ---------------------------
# HOME DASHBOARD
# ---------------------------
def home_page():
    st.subheader("🏠 Dashboard Overview")

    conn = get_connection()
    today = str(datetime.now().date())

    # Onboarding today
    onboarding_df = pd.read_sql(
        f"SELECT * FROM employees WHERE joining_date = '{today}'",
        conn
    )

    total_onboarding = len(onboarding_df)
    total_freshers = len(onboarding_df[onboarding_df["employee_type"] == "FRESHER"])
    total_experienced = len(onboarding_df[onboarding_df["employee_type"] == "EXPERIENCED"])

    # Offboarding today
    offboarding_df = pd.read_sql(
        f"SELECT * FROM employees WHERE last_working_date = '{today}'",
        conn
    )

    total_offboarding = len(offboarding_df)

    conn.close()

    col1, col2 = st.columns(2)

    # ------------------ ONBOARDING COLUMN ------------------
    with col1:
        st.markdown("### 🟢 Onboarding Today")
        st.metric("Total Onboarding", total_onboarding)
        st.metric("Freshers", total_freshers)
        st.metric("Experienced", total_experienced)

    # ------------------ OFFBOARDING COLUMN ------------------
    with col2:
        st.markdown("### 🔴 Offboarding Today")
        st.metric("Employees Leaving Today", total_offboarding)


# ---------------------------
# VIEW TABLES PAGE
# ---------------------------
def view_tables():
    st.subheader("📂 Database Tables")
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn)
    st.dataframe(tables)
    conn.close()


# ---------------------------
# VIEW TABLE DATA PAGE
# ---------------------------
def view_table_data():
    st.subheader("📊 View Table Data")
    conn = get_connection()

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn)
    table_list = tables["name"].tolist()

    selected_table = st.selectbox("Select Table", table_list)

    if st.button("Show Data"):
        df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
        st.dataframe(df)

    conn.close()


# ---------------------------
# UPLOAD DATA PAGE
# ---------------------------
def upload_data():
    st.subheader("📤 Upload CSV / Excel Data")
    conn = get_connection()

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn)
    table_list = tables["name"].tolist()

    selected_table = st.selectbox("Select Table", table_list)

    schema = pd.read_sql(f"PRAGMA table_info({selected_table});", conn)
    columns = schema["name"].tolist()

    st.write("Expected Columns:")
    st.code(columns)

    uploaded_file = st.file_uploader("Upload CSV or Excel",
                                     type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.dataframe(df.head())

        if list(df.columns) == columns:
            if st.button("Insert Data"):
                df.to_sql(selected_table, conn,
                          if_exists='append', index=False)
                st.success("Data Inserted Successfully!")
        else:
            st.error("Schema mismatch! Columns must match exactly.")

    conn.close()


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
        "Upload Data"
    ])

    if page == "Home":
        home_page()
    elif page == "View Tables":
        view_tables()
    elif page == "View Table Data":
        view_table_data()
    elif page == "Upload Data":
        upload_data()
