import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sqlite3
import hashlib
import io


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Smart Data Analyzer",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
}

h1 {
    font-weight: 700;
}

.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

.feature-card {
    background-color: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    min-height: 180px;
}

.footer {
    text-align: center;
    padding: 20px;
    color: gray;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def create_database():

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    connection.commit()

    # --------------------------------------------------------
    # AUTOMATIC ADMIN ACCOUNT
    # Username: admin
    # Password: admin123
    # --------------------------------------------------------

    admin_password = hash_password("admin123")

    cursor.execute(
        "SELECT username FROM users WHERE username = ?",
        ("admin",)
    )

    admin_exists = cursor.fetchone()

    if admin_exists:
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (admin_password, "admin")
        )
    else:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", admin_password)
        )

    connection.commit()
    connection.close()


def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def create_user(username, password):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    try:

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (
                username,
                hash_password(password)
            )
        )

        connection.commit()

        result = True

    except sqlite3.IntegrityError:

        result = False

    connection.close()

    return result


def check_login(username, password):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE username = ?
        AND password = ?
        """,
        (
            username,
            hash_password(password)
        )
    )

    user = cursor.fetchone()

    connection.close()

    return user is not None


def get_users():

    connection = sqlite3.connect("users.db")

    dataframe = pd.read_sql_query(
        "SELECT username FROM users",
        connection
    )

    connection.close()

    return dataframe


# Create database automatically
create_database()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""


# ============================================================
# LOGIN / SIGNUP PAGE
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        "<h1 style='text-align:center;'>📊 Smart Data Analyzer</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;'>"
        "Smart Data Visualization and Business Insights System"
        "</p>",
        unsafe_allow_html=True
    )

    st.write("")

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Sign Up"]
    )

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader("Login")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if username.strip() == "" or password.strip() == "":

                st.error("Please enter username and password.")

            elif check_login(username, password):

                st.session_state.logged_in = True
                st.session_state.username = username

                st.success("Login successful!")

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    # ========================================================
    # SIGNUP
    # ========================================================

    with signup_tab:

        st.subheader("Create New Account")

        new_username = st.text_input(
            "Create Username",
            key="signup_username"
        )

        new_password = st.text_input(
            "Create Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if (
                new_username.strip() == ""
                or new_password.strip() == ""
                or confirm_password.strip() == ""
            ):

                st.error(
                    "Please fill all fields."
                )

            elif len(new_password) < 4:

                st.error(
                    "Password must contain at least 4 characters."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif new_username.lower() == "admin":

                st.error(
                    "The username 'admin' is reserved for the administrator."
                )

            elif create_user(
                new_username.strip(),
                new_password
            ):

                st.success(
                    "Account created successfully! "
                    "You can now login."
                )

            else:

                st.error(
                    "Username already exists."
                )

    st.markdown(
        "<div class='footer'>"
        "Smart Data Analyzer | MCA Academic Project"
        "</div>",
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📊 Smart Data Analyzer")

    st.write(
        f"Welcome, **{st.session_state.username}**"
    )

    st.divider()

    if st.session_state.username == "admin":

        menu = st.radio(
            "Navigation",
            [
                "🏠 Home",
                "📊 Data Analyzer",
                "👥 User Management",
                "ℹ️ System Information"
            ]
        )

    else:

        menu = st.radio(
            "Navigation",
            [
                "🏠 Home",
                "📊 Data Analyzer"
            ]
        )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()


# ============================================================
# HOME PAGE
# ============================================================

if menu == "🏠 Home":

    st.title("📊 Smart Data Analyzer")

    st.subheader(
        "Smart Data Visualization and Business Insights System"
    )

    st.write(
        "Analyze CSV and Excel datasets, clean data, "
        "create interactive visualizations and generate "
        "business insights."
    )

    st.write("")

    # Metrics

    users_df = get_users()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Registered Users",
            len(users_df)
        )

    with col2:

        st.metric(
            "Current Dataset",
            "Ready"
        )

    with col3:

        st.metric(
            "Analysis Engine",
            "Active"
        )

    with col4:

        st.metric(
            "Smart Insights",
            "Enabled"
        )

    st.write("")

    st.subheader("🚀 Quick Start")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown("""
        <div class="feature-card">
        <h3>📁 Upload</h3>
        <p>
        Upload CSV or Excel files for analysis.
        </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="feature-card">
        <h3>🧹 Clean</h3>
        <p>
        Handle missing values and duplicate records.
        </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""
        <div class="feature-card">
        <h3>📈 Visualize</h3>
        <p>
        Create interactive charts and trends.
        </p>
        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown("""
        <div class="feature-card">
        <h3>💡 Insights</h3>
        <p>
        Discover business insights automatically.
        </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    st.subheader("🔄 Workflow")

    st.write("""
    **1. Upload Dataset**  
    ↓  
    **2. Clean Data**  
    ↓  
    **3. Analyze Data**  
    ↓  
    **4. Generate Visualizations**  
    ↓  
    **5. Generate Smart Insights**  
    ↓  
    **6. Export Reports**
    """)


# ============================================================
# ADMIN USER MANAGEMENT
# ============================================================

elif menu == "👥 User Management":

    if st.session_state.username != "admin":

        st.error(
            "Access denied. Administrator access required."
        )

    else:

        st.title("👥 User Management")

        users_df = get_users()

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Total Registered Users",
                len(users_df)
            )

        with col2:

            st.metric(
                "Administrator",
                "admin"
            )

        st.subheader("Registered Users")

        st.dataframe(
            users_df,
            use_container_width=True,
            hide_index=True
        )

        st.info(
            "User passwords are securely stored as SHA-256 hashes "
            "and are not displayed."
        )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

elif menu == "ℹ️ System Information":

    if st.session_state.username != "admin":

        st.error(
            "Access denied."
        )

    else:

        st.title("ℹ️ System Information")

        st.subheader("Application")

        st.write(
            "**Application:** Smart Data Analyzer"
        )

        st.write(
            "**Type:** Web-Based Data Analysis System"
        )

        st.write(
            "**Purpose:** Data Visualization and Business Insights"
        )

        st.subheader("🛠️ Technology Stack")

        technologies = pd.DataFrame({
            "Technology": [
                "Python",
                "Streamlit",
                "Pandas",
                "NumPy",
                "Plotly",
                "SQLite",
                "OpenPyXL",
                "XlsxWriter",
                "ReportLab"
            ],
            "Purpose": [
                "Programming",
                "Web Application",
                "Data Analysis",
                "Numerical Processing",
                "Data Visualization",
                "Database",
                "Excel Processing",
                "Excel Export",
                "PDF Report"
            ]
        })

        st.dataframe(
            technologies,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("📌 Main Features")

        st.write("""
        - User Login and Signup
        - Admin Panel
        - CSV Upload
        - Excel Upload
        - Data Cleaning
        - Missing Value Handling
        - Duplicate Removal
        - Statistical Analysis
        - Interactive Visualizations
        - Trend Analysis
        - Outlier Detection
        - Correlation Analysis
        - Smart Business Insights
        - CSV Export
        - Excel Export
        - PDF Report Generation
        """)


# ============================================================
# DATA ANALYZER
# ============================================================

elif menu == "📊 Data Analyzer":

    st.title("📊 Data Analyzer")

    st.write(
        "Upload your CSV or Excel dataset to begin analysis."
    )

    uploaded_file = st.file_uploader(
        "Upload Dataset",
        type=["csv", "xlsx"]
    )

    # ========================================================
    # NO FILE
    # ========================================================

    if uploaded_file is None:

        st.info(
            "Please upload a CSV or Excel file."
        )

        st.subheader("Available Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write("""
            ### 🧹 Data Cleaning

            - Missing values
            - Duplicate records
            - Data types
            """)

        with col2:

            st.write("""
            ### 📈 Visualization

            - Bar charts
            - Pie charts
            - Histograms
            - Trend charts
            """)

        with col3:

            st.write("""
            ### 💡 Smart Insights

            - Average
            - Maximum
            - Minimum
            - Outliers
            - Correlations
            """)

        st.stop()

    # ========================================================
    # LOAD DATASET
    # ========================================================

    try:

        if uploaded_file.name.endswith(".csv"):

            df = pd.read_csv(
                uploaded_file
            )

        else:

            df = pd.read_excel(
                uploaded_file
            )

    except Exception as error:

        st.error(
            f"Unable to read the file: {error}"
        )

        st.stop()

    st.session_state.uploaded_file_name = uploaded_file.name

    original_rows = len(df)
    original_columns = len(df.columns)

    # ========================================================
    # BASIC CLEANING
    # ========================================================

    duplicate_count = df.duplicated().sum()

    # Remove duplicates

    df = df.drop_duplicates()

    rows_after_duplicates = len(df)

    # Identify numeric columns

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    # Identify categorical columns

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    # ========================================================
    # DATE COLUMN DETECTION
    # ========================================================

    date_columns = []

    for column in df.columns:

        if (
            column not in numeric_columns
            and column not in categorical_columns
        ):
            continue

        try:

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_ratio = converted.notna().mean()

            if valid_ratio >= 0.70:

                date_columns.append(column)

        except Exception:

            pass

    # ========================================================
    # HANDLE MISSING VALUES
    # ========================================================

    missing_before = int(
        df.isnull().sum().sum()
    )

    missing_report = []

    for column in df.columns:

        missing_count = df[column].isnull().sum()

        if missing_count > 0:

            if pd.api.types.is_numeric_dtype(
                df[column]
            ):

                median_value = df[column].median()

                df[column] = df[column].fillna(
                    median_value
                )

                method = "Filled with median"

            else:

                df[column] = df[column].fillna(
                    "Unknown"
                )

                method = "Filled with Unknown"

            missing_report.append({
                "Column": column,
                "Missing Values": int(missing_count),
                "Method": method
            })

    missing_after = int(
        df.isnull().sum().sum()
    )

    # ========================================================
    # SIDEBAR FILTERS
    # ========================================================

    st.sidebar.subheader("🔎 Filters")

    filtered_df = df.copy()

    filter_columns = []

    for column in categorical_columns:

        unique_count = df[column].nunique()

        if unique_count <= 30:

            filter_columns.append(column)

    for column in filter_columns:

        options = sorted(
            df[column].astype(str).unique().tolist()
        )

        selected = st.sidebar.multiselect(
            f"Filter {column}",
            options,
            default=options
        )

        if selected:

            filtered_df = filtered_df[
                filtered_df[column].astype(str).isin(
                    selected
                )
            ]

    # ========================================================
    # DATASET OVERVIEW
    # ========================================================

    st.subheader("📌 Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Rows",
            len(filtered_df)
        )

    with col2:

        st.metric(
            "Columns",
            len(filtered_df.columns)
        )

    with col3:

        st.metric(
            "Missing Values",
            missing_after
        )

    with col4:

        st.metric(
            "Duplicates Removed",
            duplicate_count
        )

    # ========================================================
    # DATA PREVIEW
    # ========================================================

    st.subheader("👀 Data Preview")

    st.dataframe(
        filtered_df.head(100),
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # COLUMN INFORMATION
    # ========================================================

    st.subheader("📋 Column Information")

    column_info = pd.DataFrame({
        "Column": filtered_df.columns,
        "Data Type": [
            str(filtered_df[column].dtype)
            for column in filtered_df.columns
        ],
        "Missing Values": [
            int(filtered_df[column].isnull().sum())
            for column in filtered_df.columns
        ],
        "Unique Values": [
            int(filtered_df[column].nunique())
            for column in filtered_df.columns
        ]
    })

    st.dataframe(
        column_info,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # NUMERICAL STATISTICS
    # ========================================================

    if numeric_columns:

        st.subheader("📊 Numerical Statistics")

        statistics = filtered_df[
            numeric_columns
        ].describe().T

        statistics = statistics.reset_index()

        statistics = statistics.rename(
            columns={"index": "Column"}
        )

        st.dataframe(
            statistics,
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # VISUALIZATION
    # ========================================================

    st.subheader("📈 Data Visualization")

    # --------------------------------------------------------
    # HISTOGRAM
    # --------------------------------------------------------

    if numeric_columns:

        selected_numeric = st.selectbox(
            "Select numerical column",
            numeric_columns
        )

        fig_hist = px.histogram(
            filtered_df,
            x=selected_numeric,
            title=f"Distribution of {selected_numeric}",
            marginal="box"
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True
        )

    # --------------------------------------------------------
    # BAR + PIE CHART
    # --------------------------------------------------------

    if filter_columns:

        selected_category = st.selectbox(
            "Select categorical column",
            filter_columns
        )

        category_counts = (
            filtered_df[
                selected_category
            ]
            .astype(str)
            .value_counts()
            .reset_index()
        )

        category_counts.columns = [
            selected_category,
            "Count"
        ]

        col1, col2 = st.columns(2)

        with col1:

            fig_bar = px.bar(
                category_counts,
                x=selected_category,
                y="Count",
                title=f"{selected_category} Distribution"
            )

            st.plotly_chart(
                fig_bar,
                use_container_width=True
            )

        with col2:

            fig_pie = px.pie(
                category_counts,
                names=selected_category,
                values="Count",
                title=f"{selected_category} Share"
            )

            st.plotly_chart(
                fig_pie,
                use_container_width=True
            )

    # ========================================================
    # DATE / TREND ANALYSIS
    # ========================================================

    if date_columns and numeric_columns:

        st.subheader("📅 Trend Analysis")

        selected_date = st.selectbox(
            "Select date column",
            date_columns
        )

        selected_value = st.selectbox(
            "Select value column",
            numeric_columns
        )

        trend_df = filtered_df.copy()

        trend_df[selected_date] = pd.to_datetime(
            trend_df[selected_date],
            errors="coerce"
        )

        trend_df = trend_df.dropna(
            subset=[selected_date]
        )

        trend_df = trend_df.sort_values(
            selected_date
        )

        fig_trend = px.line(
            trend_df,
            x=selected_date,
            y=selected_value,
            markers=True,
            title=f"{selected_value} Trend Over Time"
        )

        st.plotly_chart(
            fig_trend,
            use_container_width=True
        )

    # ========================================================
    # SMART INSIGHTS
    # ========================================================

    st.subheader("💡 Smart Data Insights")

    insights = []

    # Numeric insights

    for column in numeric_columns:

        series = filtered_df[column].dropna()

        if len(series) == 0:
            continue

        average = series.mean()
        maximum = series.max()
        minimum = series.min()
        median = series.median()

        insights.append(
            f"📌 **{column}** has an average value of "
            f"**{average:,.2f}**."
        )

        insights.append(
            f"📈 Maximum value of **{column}** is "
            f"**{maximum:,.2f}**."
        )

        insights.append(
            f"📉 Minimum value of **{column}** is "
            f"**{minimum:,.2f}**."
        )

        if average > median:

            insights.append(
                f"📊 The average of **{column}** is higher "
                f"than its median, which may indicate "
                f"higher-value observations."
            )

        elif average < median:

            insights.append(
                f"📊 The average of **{column}** is lower "
                f"than its median, which may indicate "
                f"lower-value observations."
            )

        # IQR outlier detection

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr

        outliers = series[
            (series < lower_limit)
            |
            (series > upper_limit)
        ]

        if len(outliers) > 0:

            insights.append(
                f"⚠️ Detected **{len(outliers)}** "
                f"potential outliers in **{column}** "
                f"using the IQR method."
            )

    # Categorical insights

    for column in filter_columns:

        if len(filtered_df[column]) > 0:

            top_category = (
                filtered_df[column]
                .astype(str)
                .value_counts()
                .idxmax()
            )

            top_count = (
                filtered_df[column]
                .astype(str)
                .value_counts()
                .max()
            )

            insights.append(
                f"🏆 The most common value in **{column}** "
                f"is **{top_category}** with "
                f"**{top_count} records**."
            )

    # Correlation insights

    if len(numeric_columns) >= 2:

        correlation_matrix = filtered_df[
            numeric_columns
        ].corr()

        correlation_pairs = []

        for i in range(
            len(numeric_columns)
        ):

            for j in range(
                i + 1,
                len(numeric_columns)
            ):

                col1 = numeric_columns[i]
                col2 = numeric_columns[j]

                value = correlation_matrix.loc[
                    col1,
                    col2
                ]

                if not pd.isna(value):

                    correlation_pairs.append(
                        (
                            abs(value),
                            value,
                            col1,
                            col2
                        )
                    )

        if correlation_pairs:

            correlation_pairs.sort(
                reverse=True
            )

            _, strongest_value, col1, col2 = (
                correlation_pairs[0]
            )

            if strongest_value > 0:

                insights.append(
                    f"🔗 **{col1}** and **{col2}** "
                    f"have the strongest positive correlation "
                    f"of **{strongest_value:.2f}**."
                )

            else:

                insights.append(
                    f"🔗 **{col1}** and **{col2}** "
                    f"have the strongest negative correlation "
                    f"of **{strongest_value:.2f}**."
                )

    if insights:

        for insight in insights:

            st.write(insight)

    else:

        st.info(
            "Not enough numerical or categorical data "
            "to generate insights."
        )

    # ========================================================
    # CORRELATION MATRIX
    # ========================================================

    if len(numeric_columns) >= 2:

        st.subheader("🔗 Correlation Analysis")

        correlation_matrix = filtered_df[
            numeric_columns
        ].corr()

        fig_corr = px.imshow(
            correlation_matrix,
            text_auto=True,
            aspect="auto",
            title="Correlation Matrix"
        )

        st.plotly_chart(
            fig_corr,
            use_container_width=True
        )

    # ========================================================
    # AUTOMATIC BUSINESS SUMMARY
    # ========================================================

    st.subheader("📋 Automatic Business Summary")

    st.write(
        f"""
        The uploaded dataset contains **{original_rows}**
        original records and **{original_columns} columns**.

        After removing duplicate records, the dataset contains
        **{len(df)} records**.

        The system detected **{len(numeric_columns)} numerical
        columns** and **{len(categorical_columns)} categorical
        columns**.

        A total of **{missing_before} missing values** were
        identified before cleaning.

        After cleaning, **{missing_after} missing values**
        remain.

        The system performed statistical analysis,
        visualization, outlier detection and correlation
        analysis on the available data.
        """
    )

    # ========================================================
    # DATA CLEANING REPORT
    # ========================================================

    st.subheader("🧹 Data Cleaning Report")

    cleaning_report = pd.DataFrame({
        "Metric": [
            "Original Rows",
            "Rows After Duplicate Removal",
            "Original Columns",
            "Missing Values Before Cleaning",
            "Missing Values After Cleaning",
            "Duplicates Removed"
        ],
        "Value": [
            original_rows,
            rows_after_duplicates,
            original_columns,
            missing_before,
            missing_after,
            duplicate_count
        ]
    })

    st.dataframe(
        cleaning_report,
        use_container_width=True,
        hide_index=True
    )

    if missing_report:

        st.subheader("Missing Value Handling")

        missing_report_df = pd.DataFrame(
            missing_report
        )

        st.dataframe(
            missing_report_df,
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # PDF REPORT
    # ========================================================

    st.subheader("📄 Generate PDF Report")

    if st.button(
        "Generate PDF Report"
    ):

        try:

            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle
            )
            from reportlab.lib import colors
            from reportlab.lib.styles import (
                getSampleStyleSheet
            )
            from reportlab.lib.enums import (
                TA_CENTER
            )

            pdf_buffer = io.BytesIO()

            document = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4
            )

            styles = getSampleStyleSheet()

            title_style = styles["Title"]
            title_style.alignment = TA_CENTER

            story = []

            story.append(
                Paragraph(
                    "Smart Data Analyzer Report",
                    title_style
                )
            )

            story.append(
                Spacer(1, 20)
            )

            story.append(
                Paragraph(
                    "Dataset Overview",
                    styles["Heading2"]
                )
            )

            overview_data = [
                ["Metric", "Value"],
                ["File Name", uploaded_file.name],
                ["Rows", str(len(filtered_df))],
                ["Columns", str(len(filtered_df.columns))],
                ["Missing Values", str(missing_after)],
                ["Duplicates Removed", str(duplicate_count)]
            ]

            overview_table = Table(
                overview_data
            )

            overview_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.grey
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.black
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    )
                ])
            )

            story.append(
                overview_table
            )

            story.append(
                Spacer(1, 20)
            )

            story.append(
                Paragraph(
                    "Smart Insights",
                    styles["Heading2"]
                )
            )

            for insight in insights:

                clean_insight = (
                    insight
                    .replace("**", "")
                    .replace("📌", "")
                    .replace("📈", "")
                    .replace("📉", "")
                    .replace("📊", "")
                    .replace("⚠️", "")
                    .replace("🏆", "")
                    .replace("🔗", "")
                )

                story.append(
                    Paragraph(
                        clean_insight,
                        styles["BodyText"]
                    )
                )

                story.append(
                    Spacer(1, 5)
                )

            story.append(
                Spacer(1, 10)
            )

            story.append(
                Paragraph(
                    "Business Summary",
                    styles["Heading2"]
                )
            )

            story.append(
                Paragraph(
                    f"The dataset contains "
                    f"{len(filtered_df)} records and "
                    f"{len(filtered_df.columns)} columns. "
                    f"The system performed data cleaning, "
                    f"statistical analysis, visualization, "
                    f"outlier detection and correlation analysis.",
                    styles["BodyText"]
                )
            )

            document.build(
                story
            )

            pdf_buffer.seek(0)

            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_buffer,
                file_name="Smart_Data_Analyzer_Report.pdf",
                mime="application/pdf"
            )

        except ImportError:

            st.error(
                "ReportLab is not installed. "
                "Run: pip install reportlab"
            )

    # ========================================================
    # CSV DOWNLOAD
    # ========================================================

    st.subheader("📥 Download Analyzed CSV")

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name="analyzed_data.csv",
        mime="text/csv"
    )

    # ========================================================
    # EXCEL DOWNLOAD
    # ========================================================

    st.subheader("📥 Download Analyzed Excel")

    excel_buffer = io.BytesIO()

    try:

        with pd.ExcelWriter(
            excel_buffer,
            engine="xlsxwriter"
        ) as writer:

            filtered_df.to_excel(
                writer,
                sheet_name="Analyzed Data",
                index=False
            )

            cleaning_report.to_excel(
                writer,
                sheet_name="Cleaning Report",
                index=False
            )

            if numeric_columns:

                statistics.to_excel(
                    writer,
                    sheet_name="Statistics",
                    index=False
                )

            workbook = writer.book

            # Formatting

            for sheet_name in writer.sheets:

                worksheet = writer.sheets[
                    sheet_name
                ]

                worksheet.freeze_panes(
                    1,
                    0
                )

                worksheet.set_column(
                    0,
                    20,
                    20
                )

        excel_buffer.seek(0)

        st.download_button(
            label="⬇️ Download Excel",
            data=excel_buffer,
            file_name="analyzed_data.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    except Exception as error:

        st.error(
            f"Excel export error: {error}"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
    <hr>
    <b>Smart Data Analyzer</b><br>
    Smart Data Visualization and Business Insights System<br>
    MCA Academic Project
    </div>
    """,
    unsafe_allow_html=True
)