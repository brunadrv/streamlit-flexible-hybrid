"""
Documentation Page - User guides and help
"""

import streamlit as st
from utils import require_login, initialize_auth

st.set_page_config(
    page_title="Documentation - Flexible Hybrid",
    page_icon="📚",
    layout="wide"
)

# Require login
require_login()

# Initialize auth
auth_manager = initialize_auth()
user = st.session_state.user

# Header
st.title("📚 Documentation")
st.markdown("*User guides, FAQs, and system documentation*")

# Documentation tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Getting Started",
    "📖 User Guide",
    "❓ FAQs",
    "🔧 Technical Docs"
])

# Tab 1: Getting Started
with tab1:
    st.header("🎯 Getting Started with Flexible Hybrid Reporting")
    
    st.markdown("""
    Welcome to the Flexible Hybrid Reporting System! This application automates the monthly 
    compliance tracking process for HelloFresh's Flexible Hybrid policy.
    """)
    
    st.divider()
    
    st.subheader("What is the Flexible Hybrid Policy?")
    
    st.info("""
    The Flexible Hybrid policy requires certain HelloFresh employees (Non-Essential) to be 
    in the office for an average of **2.5 days per week**. Badge swipes, PTO, LOA, and 
    Company Holidays are tracked towards the 2.5 average.
    """)
    
    st.divider()
    
    st.subheader("Quick Start by Role")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**👔 Admins & HRBPs:**")
        st.markdown("""
        1. Go to **Dashboard** to see overall compliance
        2. Check **All Org View** for detailed employee data
        3. Use **Admin Panel** to manage exceptions
        4. Run **Monthly Update** at the start of each month
        5. Export reports for leadership and managers
        """)
        
        st.markdown("**👥 Managers:**")
        st.markdown("""
        1. Visit **My Team** to see your direct reports
        2. Review compliance status regularly
        3. Reach out to employees who are at risk or non-compliant
        4. Export team reports for your records
        """)
    
    with col2:
        st.markdown("**📊 Key Metrics:**")
        st.markdown("""
        - **Adjusted Weekly Average**: (Swipes + Exceptions) / Days Possible × 5
        - **Days Possible**: Base Days - PTO - LOA
        - **Compliant**: ≥ 2.5 average
        - **At Risk**: 2.0 - 2.49 average
        - **Non-Compliant**: < 2.0 average
        """)
        
        st.markdown("**🎯 Compliance Threshold:**")
        st.success("Target: **2.5 days/week** (or 50% of work week)")

# Tab 2: User Guide
with tab2:
    st.header("📖 User Guide")
    
    guide_section = st.selectbox(
        "Select a topic:",
        [
            "Navigating the Dashboard",
            "Understanding Compliance Metrics",
            "Managing Exceptions (Admin)",
            "Running Monthly Updates (Admin)",
            "Exporting Reports",
            "Processing LOA Data",
            "Troubleshooting"
        ]
    )
    
    if guide_section == "Navigating the Dashboard":
        st.markdown("""
        ### Navigating the Dashboard
        
        The Dashboard provides a high-level overview of compliance metrics:
        
        **Key Sections:**
        
        1. **Metrics Bar**: Shows total employees, compliance rate, at-risk, and non-compliant counts
        2. **Compliance Distribution Chart**: Pie chart showing breakdown of compliance statuses
        3. **Average Distribution**: Histogram of adjusted weekly averages across employees
        4. **Department Breakdown**: Department-level compliance rates (Admin/HRBP only)
        5. **Employee Data Table**: Detailed employee-level data with filtering
        
        **Using Filters:**
        
        - Use the month selector in the sidebar to view different periods
        - Use status filters to focus on specific employee groups
        - Click column headers in tables to sort
        
        **Color Coding:**
        
        - 🟢 Green: Compliant (≥ 2.5)
        - 🟡 Yellow: At Risk (2.0 - 2.49)
        - 🔴 Red: Non-Compliant (< 2.0)
        """)
    
    elif guide_section == "Understanding Compliance Metrics":
        st.markdown("""
        ### Understanding Compliance Metrics
        
        **Adjusted Weekly Average Formula:**
        
        ```
        Adjusted Weekly Avg = ((Swipes + Exceptions) / Days Possible) × 5
        ```
        
        **Example Calculation:**
        
        - Swipes (Lenel + Manual): 15 days
        - Exceptions granted: 0 days
        - PTO taken: 2 days
        - LOA days: 0 days
        - Base days in month: 20 days
        
        **Calculation:**
        ```
        Days Possible = 20 - 2 - 0 = 18 days
        Adjusted Weekly Avg = (15 + 0) / 18 × 5 = 4.17 days/week
        Status: Compliant ✅
        ```
        
        **Components:**
        
        - **Swipes**: Badge swipes from Lenel + Manual entry (WeWork)
        - **Exceptions**: Days granted for special circumstances
        - **Days Possible**: Workdays available after PTO and LOA
        - **PTO**: Paid time off reduces days possible
        - **LOA**: Leave of absence reduces days possible
        
        **Special Cases:**
        
        - **Essential Employees**: Exempt from policy (expected 5x/week)
        - **On Leave**: Excluded from compliance calculations
        - **Exceptions Granted**: May have different requirements
        """)
    
    elif guide_section == "Managing Exceptions (Admin)":
        st.markdown("""
        ### Managing Exceptions (Admin/HRBP Only)
        
        Exceptions are granted for employees with special circumstances such as:
        
        - ADA/Medical accommodations
        - Approved remote work arrangements
        - Temporary situations
        
        **Granting an Exception:**
        
        1. Navigate to **Admin Panel** → **Manage Exceptions** tab
        2. Enter Employee ID
        3. Specify number of exception days
        4. Provide detailed reason
        5. Select exception type
        6. Click "Add Exception"
        
        **Bulk Exception Upload:**
        
        1. Prepare CSV with columns: `EMPLOYEE_ID`, `EXCEPTIONS`, `REASON`
        2. Upload file in Admin Panel
        3. Review preview
        4. Process bulk upload
        
        **Best Practices:**
        
        - Document all exceptions clearly
        - Review exceptions quarterly
        - Coordinate with HRBPs for approvals
        - Track exception expiration dates
        """)
    
    elif guide_section == "Running Monthly Updates (Admin)":
        st.markdown("""
        ### Running Monthly Updates
        
        **When to Run:**
        - First week of the following month
        - After the reporting period ends
        - Before distributing reports
        
        **Steps:**
        
        1. **Navigate to Admin Panel** → Monthly Data Update tab
        2. **Select the month** to update
        3. **Review month configuration** (dates, weeks, days possible)
        4. **Click "Run Monthly Update Pipeline"**
        5. **Monitor progress** as pipeline executes
        6. **Review summary** when complete
        
        **What the Pipeline Does:**
        
        1. Loads active employee roster from Snowflake
        2. Fetches badge swipes from Lenel
        3. Gets WeWork swipes from Google Sheets
        4. Retrieves PTO data from Snowflake
        5. Processes LOA data
        6. Calculates compliance metrics
        7. Generates department summaries
        8. Updates historical records
        
        **After the Update:**
        
        - Review Dashboard for accuracy
        - Check for data anomalies
        - Export reports for distribution
        - Update Disciplinary Action tracker if needed
        """)
    
    elif guide_section == "Exporting Reports":
        st.markdown("""
        ### Exporting Reports
        
        **Export Types:**
        
        1. **Monthly Compliance Report**: Standard report with all metrics
        2. **All Org Tracker**: Complete organizational view (Admin only)
        3. **Department Report**: Department-specific data
        4. **Team Report**: Manager's direct reports
        5. **Disciplinary Action List**: Non-compliant employees
        6. **Trend Analysis**: Multi-month comparison
        
        **Export Formats:**
        
        - **CSV**: Universal format, works everywhere
        - **Excel (XLSX)**: Multi-sheet workbook with formatting
        - **Google Sheets**: Direct integration (coming soon)
        
        **Steps to Export:**
        
        1. Go to **Export Data** page
        2. Select export type
        3. Choose reporting month (or date range)
        4. Select export format
        5. Configure options (sensitive data, exempt employees, etc.)
        6. Preview data
        7. Click "Generate Export"
        8. Download file
        
        **Tips:**
        
        - Preview before exporting to verify data
        - Use Excel format for formatted reports
        - Protect files with employee IDs
        - Name files descriptively with dates
        """)
    
    elif guide_section == "Processing LOA Data":
        st.markdown("""
        ### Processing LOA Data
        
        LOA (Leave of Absence) data requires special processing to calculate weekdays on leave.
        
        **Method 1: Upload Workday Export**
        
        1. Export "US HF - Workers on Leave" from Workday
        2. Go to **Admin Panel** → **LOA Processing** tab
        3. Select reporting month
        4. Upload CSV or Excel file
        5. Review preview
        6. Click "Process LOA File"
        7. Download processed data
        
        **Method 2: Manual Entry**
        
        1. Go to **Admin Panel** → **LOA Processing** tab
        2. Select "Manual LOA Entry"
        3. Enter data in format: `Employee ID, Days on Leave`
        4. One employee per line
        5. Click "Process Manual LOA Entry"
        6. Download processed data
        
        **What Gets Calculated:**
        
        - Overlap between LOA period and reporting period
        - Only weekdays (Monday-Friday) count
        - "Is on Leave" status at end of period
        
        **Example:**
        
        Employee on LOA from Jan 15 - Feb 15
        Reporting period: Jan 5 - Feb 1
        
        Overlap: Jan 15 - Feb 1 = 13 weekdays
        Is on Leave: Yes (still on leave at end of period)
        """)
    
    else:  # Troubleshooting
        st.markdown("""
        ### Troubleshooting
        
        **Common Issues:**
        
        **1. "No data available for selected period"**
        - Ensure monthly update has been run
        - Check Snowflake connection
        - Verify month configuration in config.yaml
        
        **2. "Failed to connect to Snowflake"**
        - Check credentials in .env file or Streamlit secrets
        - Verify VPN connection if required
        - Confirm Snowflake permissions
        
        **3. "Employee not showing in report"**
        - Check if employee is active in Workday
        - Verify employment status
        - Check classification (Essential vs Non-Essential)
        
        **4. "Swipe count seems wrong"**
        - Verify badge system data is syncing
        - Check for manual WeWork entries
        - Review date range configuration
        
        **5. "Export failing"**
        - Try smaller date range
        - Use CSV instead of Excel
        - Check browser download settings
        
        **6. "Permission denied on page"**
        - Verify your role has required permissions
        - Contact admin to update role
        - Log out and log back in
        
        **Getting Help:**
        
        - 📧 Email: goat-team@hellofresh.com
        - 💬 Slack: #flexible-hybrid-support
        - 📖 Check this documentation
        - 🎫 Submit ticket: [Support Portal]
        """)

# Tab 3: FAQs
with tab3:
    st.header("❓ Frequently Asked Questions")
    
    with st.expander("What is the Flexible Hybrid policy?"):
        st.markdown("""
        The Flexible Hybrid policy requires Non-Essential employees to be in the office 
        for an average of 2.5 days per week (50% of work week). Badge swipes, PTO, LOA, 
        and Company Holidays are tracked towards this average.
        """)
    
    with st.expander("How is compliance calculated?"):
        st.markdown("""
        **Formula**: `((Swipes + Exceptions) / Days Possible) × 5`
        
        - **Swipes**: Badge swipes from Lenel + Manual entries
        - **Exceptions**: Days granted for special circumstances
        - **Days Possible**: Base working days minus PTO and LOA
        
        **Status**:
        - Compliant: ≥ 2.5
        - At Risk: 2.0 - 2.49
        - Non-Compliant: < 2.0
        """)
    
    with st.expander("What if I have PTO or LOA?"):
        st.markdown("""
        PTO and LOA days reduce your "Days Possible" for the month, which means you need 
        fewer swipes to maintain compliance. 
        
        Example: If the month has 20 working days and you take 3 days PTO, your Days Possible 
        is 17. To maintain 2.5 average, you'd need: (2.5 × 17) / 5 = 8.5 days in office.
        """)
    
    with st.expander("Who is exempt from this policy?"):
        st.markdown("""
        The following employees are exempt:
        
        - **Essential Employees**: Roles requiring daily on-site presence
        - **Exception Granted**: Employees with ADA accommodations or approved arrangements
        - **On Leave**: Employees currently on leave of absence
        """)
    
    with st.expander("How often is data updated?"):
        st.markdown("""
        - **Lenel Swipes**: Updated hourly in Snowflake
        - **PTO Data**: Updated daily in Snowflake
        - **Compliance Reports**: Updated monthly (first week of following month)
        - **Real-time View**: Coming soon (auto-refresh dashboards)
        """)
    
    with st.expander("Can I see historical data?"):
        st.markdown("""
        Yes! Use the month selector in the sidebar to view any historical month. You can 
        also use the Trend Analysis export to compare multiple months.
        """)
    
    with st.expander("What if my swipe count is incorrect?"):
        st.markdown("""
        If you believe your swipe count is incorrect:
        
        1. Verify you badged in correctly (some systems require badge-out too)
        2. Check if you work from a WeWork location (tracked separately)
        3. Contact your HRBP to investigate
        4. An exception can be granted if there's a valid reason
        """)
    
    with st.expander("How do I request an exception?"):
        st.markdown("""
        Contact your HRBP to discuss your situation. Valid exceptions include:
        
        - ADA/Medical accommodations
        - Approved remote work arrangements
        - Temporary circumstances (travel, projects, etc.)
        
        Your HRBP will work with the People team to grant exceptions if approved.
        """)

# Tab 4: Technical Docs
with tab4:
    st.header("🔧 Technical Documentation")
    
    if user['role'] in ['admin', 'hrbp']:
        st.markdown("""
        ### System Architecture
        
        **Data Sources:**
        
        1. **Snowflake**:
           - `VIEW_WORKDAY_KITCHEN_SINK_PI` - Employee roster
           - `VIEW_LENEL_S2_EVENTS_180_DAYS_v2` - Badge swipes
           - `VIEW_ADP_TIME_OFF_APPROVED` - PTO data
           - `INT0136_WORKER_SCHEDULE_CHANGES` - Employee schedules
        
        2. **Google Sheets**:
           - Chicago WeWork Swipe Tracker - Manual swipe entries
        
        3. **Workday**:
           - Workers on Leave report (manual export)
        
        **Data Pipeline:**
        
        ```
        Snowflake (Roster) → 
        Snowflake (Swipes) → 
        GSheets (Manual Swipes) → 
        Snowflake (PTO) → 
        Workday (LOA) → 
        Processing Engine → 
        Streamlit App
        ```
        
        **Configuration:**
        
        - `config.yaml`: Month configurations, role mappings, schedule types
        - `.env`: Snowflake credentials, API keys
        - `.streamlit/secrets.toml`: Streamlit Cloud secrets
        
        **Key Modules:**
        
        - `utils/snowflake_connector.py`: Snowflake data access
        - `utils/data_processor.py`: Compliance calculations
        - `utils/auth.py`: Authentication & authorization
        - `utils/gsheets_connector.py`: Google Sheets integration
        - `utils/loa_processor.py`: LOA data processing
        
        **Deployment:**
        
        - Platform: Streamlit Cloud (or internal server)
        - Python: 3.10+
        - Dependencies: See requirements.txt
        
        **Future Enhancements:**
        
        - Real-time dashboard updates
        - Automated email notifications
        - Integration with Disciplinary Action workflow
        - Mobile app version
        - Predictive analytics for compliance trends
        """)
    else:
        st.info("Technical documentation is available to administrators only.")

# Footer
st.divider()
st.markdown("""
*For additional help, contact your HRBP or the GOAT team.*

**Last Updated**: March 2026 | **Version**: 1.0.0
""")
