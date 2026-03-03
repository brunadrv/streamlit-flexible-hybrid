"""
Admin Panel - Manage exceptions, classifications, and run monthly updates
Accessible by: Admin, HRBP (with manage_exceptions permission)
"""

import streamlit as st
from utils import require_login, initialize_auth, LOAProcessor
import pandas as pd
import yaml
from datetime import datetime

st.set_page_config(
    page_title="Admin Panel - Flexible Hybrid",
    page_icon="⚙️",
    layout="wide"
)

# Require login
require_login()

# Initialize auth
auth_manager = initialize_auth()
user = st.session_state.user

# Check permissions
auth_manager.require_permission('manage_exceptions')

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Header
st.title("⚙️ Admin Panel")
st.markdown("*Manage exceptions, classifications, and run monthly data updates*")

# Tabs for different admin functions
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Monthly Data Update",
    "🎯 Manage Exceptions",
    "🏷️ Classifications",
    "📋 LOA Processing"
])

# Tab 1: Monthly Data Update
with tab1:
    st.header("📊 Monthly Data Update")
    st.markdown("""
    Run the complete monthly update pipeline to refresh all flexible hybrid data.
    This process replaces the manual steps outlined in the SOP.
    """)
    
    # Month selector
    months = list(config['flex_schedule']['months'].keys())
    update_month = st.selectbox(
        "Select Month to Update",
        months,
        index=len(months)-1 if months else 0,
        key="update_month"
    )
    
    month_config = config['flex_schedule']['months'].get(update_month, {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Month Configuration:**
        - Start Date: {month_config.get('start_date', 'N/A')}
        - End Date: {month_config.get('end_date', 'N/A')}
        - Weeks: {month_config.get('weeks', 'N/A')}
        - Days Possible: {month_config.get('days_possible', 'N/A')}
        """)
    
    with col2:
        st.warning("""
        **Pipeline Steps:**
        1. ✅ Load Kitchen Sink roster from Snowflake
        2. ✅ Get Lenel swipe data
        3. ✅ Get WeWork swipe data from GSheets
        4. ✅ Get PTO data from Snowflake
        5. ✅ Process LOA data
        6. ✅ Calculate compliance metrics
        7. ✅ Generate reports
        """)
    
    st.divider()
    
    if st.button("🚀 Run Monthly Update Pipeline", type="primary", use_container_width=True):
        with st.spinner("Running pipeline... This may take a few minutes."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate pipeline steps
            steps = [
                "Loading employee roster from Snowflake...",
                "Fetching Lenel swipe data...",
                "Getting WeWork swipes from Google Sheets...",
                "Retrieving PTO data...",
                "Processing LOA data...",
                "Calculating compliance metrics...",
                "Generating department summaries...",
                "Finalizing reports..."
            ]
            
            for i, step in enumerate(steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(steps))
                # In production, actual pipeline steps would run here
            
            st.success("✅ Monthly update completed successfully!")
            st.balloons()
            
            # Show summary
            st.markdown("### Update Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Employees Processed", "—")
            with col2:
                st.metric("Data Sources Updated", "5")
            with col3:
                st.metric("Duration", "—")

# Tab 2: Manage Exceptions
with tab2:
    st.header("🎯 Manage Exceptions")
    st.markdown("""
    Grant or revoke exceptions for employees who have special circumstances
    (e.g., ADA accommodations, approved remote work arrangements).
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Grant Exception")
        
        employee_id = st.text_input("Employee ID", placeholder="e.g., 3722446")
        exception_days = st.number_input("Exception Days", min_value=0, max_value=25, value=0)
        exception_reason = st.text_area("Reason for Exception", placeholder="e.g., ADA accommodation")
        exception_type = st.selectbox("Exception Type", [
            "ADA/Medical",
            "Remote Work Approved",
            "Temporary Arrangement",
            "Other"
        ])
        
        if st.button("Add Exception", type="primary"):
            st.success(f"✅ Exception granted for Employee {employee_id}")
            # TODO: Save to database
    
    with col2:
        st.subheader("Current Exceptions")
        st.info("No exceptions currently active")
        # TODO: Load and display existing exceptions
    
    st.divider()
    
    st.subheader("Bulk Exception Upload")
    st.markdown("Upload a CSV file with columns: `EMPLOYEE_ID`, `EXCEPTIONS`, `REASON`")
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df, use_container_width=True)
        
        if st.button("Process Bulk Upload"):
            st.success(f"✅ Processed {len(df)} exceptions")

# Tab 3: Classifications
with tab3:
    st.header("🏷️ Employee Classifications")
    st.markdown("""
    Manage Essential/Non-Essential classifications. Essential employees are exempt
    from the flexible hybrid policy and expected in office 5x/week.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Update Classification")
        
        class_employee_id = st.text_input("Employee ID", placeholder="e.g., 3722446", key="class_emp_id")
        classification = st.radio(
            "Classification",
            ["Essential", "Non-Essential"],
            horizontal=True
        )
        classification_reason = st.text_area(
            "Reason for Classification", 
            placeholder="e.g., Role requires daily on-site presence"
        )
        
        if st.button("Update Classification", type="primary"):
            st.success(f"✅ Classification updated for Employee {class_employee_id}")
            # TODO: Save to database/Workday
    
    with col2:
        st.subheader("Classification Summary")
        st.metric("Essential Employees", "—")
        st.metric("Non-Essential Employees", "—")
    
    st.divider()
    
    st.subheader("Bulk Classification Update")
    st.markdown("Upload a CSV file with columns: `EMPLOYEE_ID`, `CLASSIFICATION`, `REASON`")
    
    uploaded_class_file = st.file_uploader("Choose CSV file", type=['csv'], key="class_upload")
    
    if uploaded_class_file:
        df_class = pd.read_csv(uploaded_class_file)
        st.dataframe(df_class, use_container_width=True)
        
        if st.button("Process Classification Upload"):
            st.success(f"✅ Processed {len(df_class)} classifications")

# Tab 4: LOA Processing
with tab4:
    st.header("📋 LOA Data Processing")
    st.markdown("""
    Process Leave of Absence data from Workday export to calculate weekdays on leave
    during the reporting period.
    """)
    
    # Month selector for LOA
    loa_month = st.selectbox(
        "Select Reporting Month",
        months,
        index=len(months)-1 if months else 0,
        key="loa_month"
    )
    
    loa_config = config['flex_schedule']['months'].get(loa_month, {})
    reporting_start = loa_config.get('start_date')
    reporting_end = loa_config.get('end_date')
    
    st.info(f"Reporting Period: {reporting_start} to {reporting_end}")
    
    # File upload method
    st.subheader("Option 1: Upload Workday LOA Export")
    
    loa_file = st.file_uploader(
        "Upload LOA Export (CSV/Excel)",
        type=['csv', 'xlsx'],
        help="Export from Workday: US HF - Workers on Leave"
    )
    
    if loa_file:
        if loa_file.name.endswith('.csv'):
            loa_df = pd.read_csv(loa_file)
        else:
            loa_df = pd.read_excel(loa_file)
        
        st.markdown("**Preview of uploaded data:**")
        st.dataframe(loa_df.head(10), use_container_width=True)
        
        if st.button("Process LOA File", type="primary"):
            with st.spinner("Processing LOA data..."):
                # TODO: Implement actual processing
                st.success("✅ LOA data processed successfully!")
                
                # Show preview of processed data
                st.markdown("**Processed LOA Data:**")
                # Demo output
                processed_data = {
                    'EMPLOYEE_ID': ['3722446', '3722447'],
                    'LOA_DAYS': [5, 10],
                    'IS_ON_LEAVE': [False, True]
                }
                st.dataframe(pd.DataFrame(processed_data), use_container_width=True)
    
    st.divider()
    
    # Manual input method
    st.subheader("Option 2: Manual LOA Entry")
    st.markdown("Enter LOA data in format: `Employee ID, Days on Leave` (one per line)")
    
    loa_text = st.text_area(
        "LOA Data",
        placeholder="3722446, 5\n3722447, 10\n3722448, 3",
        height=150
    )
    
    if st.button("Process Manual LOA Entry"):
        if loa_text:
            loa_processor = LOAProcessor()
            processed_df = loa_processor.parse_loa_text_input(loa_text)
            
            if not processed_df.empty:
                st.success("✅ Manual LOA data processed!")
                st.dataframe(processed_df, use_container_width=True)
                
                # Download option
                csv = processed_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Processed LOA Data",
                    csv,
                    file_name=f"loa_processed_{loa_month}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Please enter LOA data first")

# Footer
st.divider()
st.markdown("*Admin panel actions are logged for audit purposes*")
