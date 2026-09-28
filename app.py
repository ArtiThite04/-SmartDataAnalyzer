import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sqlite3
import hashlib
import io

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Data Analyzer",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #666;
    margin-bottom: 25px;
}

.card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    background-color: #ffffff;
    margin-bottom: 15px;
}

.section-title {
    font-size: 25px;
    font-weight: 600;
    margin-top: 20px;
    margin-bottom: 15px;
}

.footer {
    text-align: center;
    padding: 25px;
    color: #777;
    margin-top: 40px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE
# =========================================================

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

    df = pd.read_sql_query(
        "SELECT username FROM users",
        connection
    )

    connection.close()

    return df


create_database()


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""


# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="main-title">📊 Smart Data Analyzer</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Smart Data Visualization and Business Insights System</div>',
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(
        ["🔐 Login", "📝 Sign Up"]
    )

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    with tab1:

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
            type="primary",
            use_container_width=True
        ):

            if username == "" or password == "":

                st.warning(
                    "Please enter username and password."
                )

            elif check_login(username, password):

                st.session_state.logged_in = True
                st.session_state.username = username

                st.success(
                    "Login successful!"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    # -----------------------------------------------------
    # SIGNUP
    # -----------------------------------------------------

    with tab2:

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
            type="primary",
            use_container_width=True
        ):

            if new_username == "" or new_password == "":

                st.warning(
                    "Please fill all fields."
                )

            elif len(new_password) < 4:

                st.warning(
                    "Password must contain at least 4 characters."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif create_user(
                new_username,
                new_password
            ):

                st.success(
                    "Account created successfully! Please login."
                )

            else:

                st.error(
                    "Username already exists."
                )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📊 Smart Data Analyzer")

st.sidebar.write(
    f"Welcome, **{st.session_state.username}**"
)

st.sidebar.divider()

if st.session_state.username == "admin":

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📊 Data Analyzer",
            "👥 User Management",
            "ℹ️ System Information"
        ]
    )

else:

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📊 Data Analyzer"
        ]
    )


st.sidebar.divider()

if st.sidebar.button(
    "Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

if page == "🏠 Home":

    st.markdown(
        '<div class="main-title">Smart Data Analyzer</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Turn raw data into meaningful business insights</div>',
        unsafe_allow_html=True
    )

    st.success(
        f"👋 Welcome **{st.session_state.username}**!"
    )

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
            "Dataset",
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

    st.divider()

    st.subheader("🚀 Quick Start")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class="card">

        ### 📁 1. Upload Data

        Upload your CSV or Excel dataset.

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="card">

        ### 📊 2. Analyze Data

        Automatically explore columns,
        statistics and patterns.

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""
        <div class="card">

        ### 💡 3. Get Insights

        Generate automatic business
        insights and recommendations.

        </div>
        """, unsafe_allow_html=True)

    st.subheader("✨ Main Features")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
        ### 📂 Data Management

        - CSV upload
        - Excel upload
        - Missing value handling
        - Duplicate removal
        - Data preview
        """)

        st.markdown("""
        ### 📈 Visualization

        - Bar charts
        - Pie charts
        - Histograms
        - Trend analysis
        - Correlation matrix
        """)

    with col2:

        st.markdown("""
        ### 🤖 Smart Insights

        - Average analysis
        - Maximum and minimum values
        - Outlier detection
        - Correlation analysis
        - Category analysis
        """)

        st.markdown("""
        ### 📥 Reports

        - CSV download
        - Excel download
        - PDF report
        - Business summary
        """)

    st.divider()

    st.subheader("🔄 Project Workflow")

    workflow = st.columns(4)

    steps = [
        ("1️⃣", "Upload Dataset"),
        ("2️⃣", "Clean Data"),
        ("3️⃣", "Analyze Data"),
        ("4️⃣", "Generate Insights")
    ]

    for column, (number, title) in zip(
        workflow,
        steps
    ):

        with column:

            st.info(
                f"{number}\n\n**{title}**"
            )


# =========================================================
# USER MANAGEMENT
# =========================================================

elif page == "👥 User Management":

    st.title("👥 User Management")

    if st.session_state.username != "admin":

        st.error(
            "Access denied."
        )

    else:

        users_df = get_users()

        st.metric(
            "Total Registered Users",
            len(users_df)
        )

        st.subheader("Registered Users")

        if len(users_df) > 0:

            st.dataframe(
                users_df,
                use_container_width=True,
                hide_index=True
            )

        st.info(
            "🔒 Passwords are securely stored as SHA-256 hashes."
        )


# =========================================================
# SYSTEM INFORMATION
# =========================================================

elif page == "ℹ️ System Information":

    st.title("ℹ️ System Information")

    st.subheader("Application")

    st.write(
        "Smart Data Visualization and Business Insights System"
    )

    st.subheader("Technology Stack")

    technology_df = pd.DataFrame({

        "Technology": [
            "Python",
            "Streamlit",
            "Pandas",
            "NumPy",
            "Plotly",
            "SQLite",
            "OpenPyXL",
            "ReportLab"
        ],

        "Purpose": [
            "Programming",
            "Web Application",
            "Data Analysis",
            "Numerical Analysis",
            "Visualization",
            "User Authentication",
            "Excel Processing",
            "PDF Reports"
        ]

    })

    st.dataframe(
        technology_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🎯 Project Objective")

    st.write(
        """
        The main objective of Smart Data Analyzer is to provide
        an easy-to-use web application for uploading, cleaning,
        analyzing and visualizing datasets while automatically
        generating useful business insights.
        """
    )

    st.subheader("📌 Main Modules")

    modules = [
        "User Authentication",
        "Dataset Upload",
        "Data Cleaning",
        "Statistical Analysis",
        "Data Visualization",
        "Smart Insights",
        "Business Report",
        "Excel Export",
        "PDF Export"
    ]

    for module in modules:

        st.write(
            f"✅ {module}"
        )


# =========================================================
# DATA ANALYZER
# =========================================================

elif page == "📊 Data Analyzer":

    st.title("📊 Data Analyzer")

    st.write(
        "Upload a CSV or Excel file to start analyzing your data."
    )

    uploaded_file = st.file_uploader(
        "Choose your dataset",
        type=["csv", "xlsx"]
    )

    if uploaded_file is None:

        st.info(
            "👆 Upload a CSV or Excel file to begin."
        )

        st.markdown("""
        ### Available Analysis

        - Dataset overview
        - Data cleaning
        - Column information
        - Statistical analysis
        - Automatic charts
        - Trend analysis
        - Outlier detection
        - Correlation analysis
        - Smart business insights
        - Excel export
        - CSV export
        - PDF report
        """)

        st.stop()


    # =====================================================
    # LOAD DATA
    # =====================================================

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


    # =====================================================
    # ORIGINAL DATA INFORMATION
    # =====================================================

    original_rows = len(df)

    original_columns = len(df.columns)

    original_missing = int(
        df.isnull().sum().sum()
    )

    original_duplicates = int(
        df.duplicated().sum()
    )


    # =====================================================
    # DATA CLEANING
    # =====================================================

    cleaned_df = df.copy()

    cleaned_df = cleaned_df.drop_duplicates()

    numeric_columns = cleaned_df.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical_columns = cleaned_df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()


    # Fill numeric missing values

    for column in numeric_columns:

        if cleaned_df[column].isnull().sum() > 0:

            cleaned_df[column] = cleaned_df[column].fillna(
                cleaned_df[column].median()
            )


    # Fill categorical missing values

    for column in categorical_columns:

        if cleaned_df[column].isnull().sum() > 0:

            cleaned_df[column] = cleaned_df[column].fillna(
                "Unknown"
            )


    # =====================================================
    # DATE DETECTION
    # =====================================================

    date_columns = []

    for column in cleaned_df.columns:

        if cleaned_df[column].dtype == "object":

            try:

                converted = pd.to_datetime(
                    cleaned_df[column],
                    errors="coerce"
                )

                valid_ratio = converted.notna().mean()

                if valid_ratio >= 0.70:

                    date_columns.append(column)

            except:

                pass


    # =====================================================
    # FILTERS
    # =====================================================

    st.sidebar.subheader("🔎 Filters")

    filter_df = cleaned_df.copy()

    filterable_columns = []

    for column in categorical_columns:

        unique_count = filter_df[column].nunique()

        if unique_count <= 30:

            filterable_columns.append(column)


    for column in filterable_columns:

        options = sorted(
            filter_df[column]
            .astype(str)
            .unique()
            .tolist()
        )

        selected = st.sidebar.multiselect(
            f"{column}",
            options,
            default=options
        )

        if selected:

            filter_df = filter_df[
                filter_df[column]
                .astype(str)
                .isin(selected)
            ]


    # =====================================================
    # TITLE
    # =====================================================

    st.success(
        f"📁 File loaded successfully: **{uploaded_file.name}**"
    )


    # =====================================================
    # OVERVIEW METRICS
    # =====================================================

    st.subheader("📌 Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Rows",
            len(filter_df)
        )

    with col2:

        st.metric(
            "Columns",
            len(filter_df.columns)
        )

    with col3:

        st.metric(
            "Missing Values",
            int(filter_df.isnull().sum().sum())
        )

    with col4:

        st.metric(
            "Duplicates Removed",
            original_duplicates
        )


    # =====================================================
    # DATA PREVIEW
    # =====================================================

    st.subheader("👀 Data Preview")

    st.dataframe(
        filter_df.head(20),
        use_container_width=True
    )


    # =====================================================
    # COLUMN INFORMATION
    # =====================================================

    st.subheader("📋 Column Information")

    column_info = pd.DataFrame({

        "Column": filter_df.columns,

        "Data Type": [
            str(filter_df[column].dtype)
            for column in filter_df.columns
        ],

        "Missing Values": [
            int(filter_df[column].isnull().sum())
            for column in filter_df.columns
        ],

        "Unique Values": [
            int(filter_df[column].nunique())
            for column in filter_df.columns
        ]

    })

    st.dataframe(
        column_info,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # NUMERICAL ANALYSIS
    # =====================================================

    if numeric_columns:

        st.subheader("🔢 Numerical Analysis")

        available_numeric = [
            column
            for column in numeric_columns
            if column in filter_df.columns
        ]

        if available_numeric:

            st.dataframe(
                filter_df[available_numeric].describe().T,
                use_container_width=True
            )


            selected_numeric = st.selectbox(
                "Select numerical column",
                available_numeric
            )


            fig_hist = px.histogram(
                filter_df,
                x=selected_numeric,
                title=f"Distribution of {selected_numeric}"
            )

            st.plotly_chart(
                fig_hist,
                use_container_width=True
            )


    # =====================================================
    # CATEGORY ANALYSIS
    # =====================================================

    if categorical_columns:

        st.subheader("🏷️ Category Analysis")

        available_categories = [
            column
            for column in categorical_columns
            if column in filter_df.columns
        ]

        if available_categories:

            selected_category = st.selectbox(
                "Select categorical column",
                available_categories
            )

            category_counts = (
                filter_df[selected_category]
                .astype(str)
                .value_counts()
                .reset_index()
            )

            category_counts.columns = [
                selected_category,
                "Count"
            ]

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


    # =====================================================
    # TREND ANALYSIS
    # =====================================================

    if date_columns and numeric_columns:

        st.subheader("📈 Trend Analysis")

        selected_date = st.selectbox(
            "Select date column",
            date_columns
        )

        selected_value = st.selectbox(
            "Select numerical column for trend",
            numeric_columns
        )

        trend_df = filter_df.copy()

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


    # =====================================================
    # SMART INSIGHTS
    # =====================================================

    st.subheader("🤖 Smart Data Insights")

    insights = []


    # Numeric insights

    for column in numeric_columns:

        if column not in filter_df.columns:
            continue

        series = pd.to_numeric(
            filter_df[column],
            errors="coerce"
        ).dropna()

        if len(series) == 0:
            continue

        mean_value = series.mean()

        max_value = series.max()

        min_value = series.min()

        median_value = series.median()

        insights.append(
            f"📌 **{column}** has an average value of "
            f"**{mean_value:,.2f}**."
        )

        insights.append(
            f"🔺 Maximum **{column}** is "
            f"**{max_value:,.2f}**."
        )

        insights.append(
            f"🔻 Minimum **{column}** is "
            f"**{min_value:,.2f}**."
        )

        if mean_value > median_value:

            insights.append(
                f"📊 **{column}** has a mean higher than "
                f"its median, indicating possible "
                f"right-skewed values."
            )


        # IQR outlier detection

        q1 = series.quantile(0.25)

        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr

        upper_bound = q3 + 1.5 * iqr

        outliers = series[
            (series < lower_bound) |
            (series > upper_bound)
        ]

        if len(outliers) > 0:

            insights.append(
                f"⚠️ Detected **{len(outliers)}** "
                f"potential outliers in **{column}** "
                f"using the IQR method."
            )


    # Category insights

    for column in categorical_columns:

        if column not in filter_df.columns:
            continue

        if len(filter_df[column]) == 0:
            continue

        top_category = (
            filter_df[column]
            .astype(str)
            .value_counts()
            .idxmax()
        )

        top_count = (
            filter_df[column]
            .astype(str)
            .value_counts()
            .max()
        )

        insights.append(
            f"🏆 Most common value in **{column}** is "
            f"**{top_category}** with **{top_count} records**."
        )


    # Display insights

    if insights:

        for insight in insights:

            st.info(insight)

    else:

        st.warning(
            "No automatic insights could be generated."
        )


    # =====================================================
    # CORRELATION
    # =====================================================

    if len(numeric_columns) >= 2:

        st.subheader("🔗 Correlation Analysis")

        correlation_df = filter_df[
            numeric_columns
        ].corr()

        fig_corr = px.imshow(
            correlation_df,
            text_auto=True,
            title="Correlation Matrix"
        )

        st.plotly_chart(
            fig_corr,
            use_container_width=True
        )

        correlation_values = correlation_df.copy()

        np.fill_diagonal(
            correlation_values.values,
            np.nan
        )

        if correlation_values.notna().any().any():

            max_pair = correlation_values.stack().idxmax()

            min_pair = correlation_values.stack().idxmin()

            max_corr = correlation_values.stack().max()

            min_corr = correlation_values.stack().min()

            st.write(
                f"🔗 Strongest positive relationship: "
                f"**{max_pair[0]}** and **{max_pair[1]}** "
                f"({max_corr:.2f})"
            )

            st.write(
                f"🔗 Strongest negative relationship: "
                f"**{min_pair[0]}** and **{min_pair[1]}** "
                f"({min_corr:.2f})"
            )


    # =====================================================
    # BUSINESS SUMMARY
    # =====================================================

    st.subheader("💼 Automatic Business Summary")

    st.write(
        f"""
        The uploaded dataset contains **{len(filter_df)} rows**
        and **{len(filter_df.columns)} columns** after filtering.

        The system automatically cleaned duplicate records
        and handled missing values where possible.

        Numerical columns were analyzed using statistical
        measures such as mean, median, minimum, maximum
        and outlier detection.

        Categorical columns were analyzed based on their
        frequency and distribution.

        The system also generated visualizations and
        correlation analysis to help identify patterns
        within the dataset.
        """
    )


    # =====================================================
    # DATA CLEANING REPORT
    # =====================================================

    st.subheader("🧹 Data Cleaning Report")

    cleaned_missing = int(
        cleaned_df.isnull().sum().sum()
    )

    cleaning_report = pd.DataFrame({

        "Metric": [
            "Original Rows",
            "Original Columns",
            "Original Missing Values",
            "Original Duplicate Rows",
            "Rows After Cleaning",
            "Columns After Cleaning"
        ],

        "Value": [
            original_rows,
            original_columns,
            original_missing,
            original_duplicates,
            len(cleaned_df),
            len(cleaned_df.columns)
        ]

    })

    st.dataframe(
        cleaning_report,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # DOWNLOAD SECTION
    # =====================================================

    st.divider()

    st.subheader("📥 Download Reports & Data")

    col1, col2, col3 = st.columns(3)


    # -----------------------------------------------------
    # CSV DOWNLOAD
    # -----------------------------------------------------

    with col1:

        csv_data = filter_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="analyzed_data.csv",
            mime="text/csv",
            use_container_width=True
        )


    # -----------------------------------------------------
    # EXCEL DOWNLOAD
    # -----------------------------------------------------

    with col2:

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="xlsxwriter"
        ) as writer:

            filter_df.to_excel(
                writer,
                index=False,
                sheet_name="Analyzed Data"
            )

            cleaning_report.to_excel(
                writer,
                index=False,
                sheet_name="Cleaning Report"
            )

            if numeric_columns:

                available_numeric = [
                    column
                    for column in numeric_columns
                    if column in filter_df.columns
                ]

                if available_numeric:

                    filter_df[
                        available_numeric
                    ].describe().T.to_excel(
                        writer,
                        sheet_name="Statistics"
                    )

            worksheet = writer.sheets[
                "Analyzed Data"
            ]

            worksheet.freeze_panes(
                1,
                0
            )

            for column_index, column_name in enumerate(
                filter_df.columns
            ):

                worksheet.set_column(
                    column_index,
                    column_index,
                    18
                )

        excel_buffer.seek(0)

        st.download_button(
            label="📊 Download Excel",
            data=excel_buffer,
            file_name="Smart_Data_Analyzer.xlsx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            use_container_width=True
        )


    # =====================================================
    # PDF REPORT
    # =====================================================

    with col3:

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
            from reportlab.lib.enums import TA_CENTER


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
                    f"Dataset: {uploaded_file.name}",
                    styles["Heading2"]
                )
            )

            story.append(
                Spacer(1, 10)
            )

            report_data = [
                ["Metric", "Value"],
                ["Rows", str(len(filter_df))],
                ["Columns", str(len(filter_df.columns))],
                [
                    "Missing Values",
                    str(
                        int(
                            filter_df.isnull()
                            .sum()
                            .sum()
                        )
                    )
                ],
                [
                    "Duplicate Rows Removed",
                    str(original_duplicates)
                ]
            ]

            report_table = Table(
                report_data
            )

            report_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
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
                report_table
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
                    .replace("🔺", "")
                    .replace("🔻", "")
                    .replace("⚠️", "")
                    .replace("📊", "")
                    .replace("🏆", "")
                )

                story.append(
                    Paragraph(
                        clean_insight,
                        styles["BodyText"]
                    )
                )

                story.append(
                    Spacer(1, 8)
                )

            story.append(
                Spacer(1, 15)
            )

            story.append(
                Paragraph(
                    "Business Summary",
                    styles["Heading2"]
                )
            )

            story.append(
                Paragraph(
                    "The Smart Data Analyzer system "
                    "processed the uploaded dataset, "
                    "performed data cleaning, statistical "
                    "analysis, visualization and automatic "
                    "business insight generation.",
                    styles["BodyText"]
                )
            )

            document.build(
                story
            )

            pdf_buffer.seek(0)

            st.download_button(
                label="📄 Download PDF",
                data=pdf_buffer,
                file_name="Smart_Data_Analyzer_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except ImportError:

            st.warning(
                "Install ReportLab using: pip install reportlab"
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

    📊 <b>Smart Data Analyzer</b><br>

    Smart Data Visualization and Business Insights System<br>

    Built using Python • Streamlit • Pandas • Plotly • NumPy

    </div>
    """,
    unsafe_allow_html=True
)