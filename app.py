"""
Flexible Hybrid Reporting Application
Main entry point for the Streamlit application
"""

import streamlit as st
from utils import initialize_auth, require_login
import yaml

# Page configuration
st.set_page_config(
    page_title="Flexible Hybrid Reporting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize authentication
auth_manager = initialize_auth()

# Main app
def main():
    """Main application"""
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        st.title("🏢 Flexible Hybrid Reporting System")
        st.markdown("### Welcome to the Flexible Hybrid Compliance Dashboard")
        
        st.markdown("""
        This application provides automated reporting and compliance tracking for HelloFresh's 
        Flexible Hybrid policy. 
        
        **Features:**
        - 📊 Real-time compliance dashboards
        - 👥 Role-based access control
        - 📈 Department and team-level reporting
        - 🔄 Automated data processing
        - 📤 Export capabilities
        - ⚙️ Exception and classification management
        
        Please log in to continue.
        """)
        
        st.divider()
        
        # Login form
        user = auth_manager.login()
        
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user['name']}!")
            st.rerun()
    else:
        # User is logged in
        user = st.session_state.user
        
        # Sidebar
        with st.sidebar:
            st.title("🏢 Flexible Hybrid")
            st.markdown(f"**Welcome, {user['name']}**")
            st.markdown(f"*Role: {user['role'].upper()}*")
            st.divider()
            
            # Navigation
            st.markdown("### Navigation")
            st.page_link("app.py", label="🏠 Home", icon="🏠")
            st.page_link("pages/1_📊_Dashboard.py", label="Dashboard", icon="📊")
            
            # Role-based navigation
            if auth_manager.has_permission(user['role'], 'view_all_org'):
                st.page_link("pages/2_🏢_All_Org_View.py", label="All Org View", icon="🏢")
            
            if auth_manager.has_permission(user['role'], 'view_assigned_departments'):
                st.page_link("pages/3_🏛️_Department_View.py", label="Department View", icon="🏛️")
            
            if auth_manager.has_permission(user['role'], 'view_own_team'):
                st.page_link("pages/4_👥_Team_View.py", label="My Team", icon="👥")
            
            if auth_manager.has_permission(user['role'], 'manage_exceptions'):
                st.page_link("pages/5_⚙️_Admin.py", label="Admin Panel", icon="⚙️")
            
            st.page_link("pages/6_📤_Export.py", label="Export Data", icon="📤")
            st.page_link("pages/7_📚_Documentation.py", label="Documentation", icon="📚")
            
            st.divider()
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Main content
        st.title("🏠 Home")
        
        # Display role-specific welcome message
        st.markdown(f"## Welcome to Flexible Hybrid Reporting, {user['name']}!")
        
        # Quick stats or overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("📊 **Dashboard**\n\nView compliance metrics and trends")
        
        with col2:
            if user['role'] in ['admin', 'hrbp']:
                st.info("🏢 **All Org View**\n\nComprehensive organizational reporting")
            elif user['role'] == 'manager':
                st.info("👥 **My Team**\n\nView your team's compliance")
            else:
                st.info("📈 **My Status**\n\nView your compliance status")
        
        with col3:
            if auth_manager.has_permission(user['role'], 'manage_exceptions'):
                st.info("⚙️ **Admin Panel**\n\nManage exceptions and classifications")
            else:
                st.info("📤 **Export**\n\nDownload your reports")
        
        st.divider()
        
        # Getting Started Guide
        st.markdown("### 🚀 Getting Started")
        
        if user['role'] in ['admin', 'hrbp']:
            st.markdown("""
            **As an Admin/HRBP, you can:**
            
            1. **View the Dashboard** - See high-level compliance metrics across the organization
            2. **Access All Org View** - Detailed reporting for all employees
            3. **Manage Departments** - Department-specific views and reporting
            4. **Update Exceptions** - Grant exceptions or update employee classifications
            5. **Export Reports** - Download data for further analysis or distribution
            6. **Process Monthly Data** - Run the monthly update pipeline
            
            👉 Start by visiting the **Dashboard** to see current compliance status.
            """)
        elif user['role'] == 'manager':
            st.markdown("""
            **As a Manager, you can:**
            
            1. **View the Dashboard** - See compliance trends
            2. **My Team View** - See detailed compliance data for your direct reports
            3. **Export Team Data** - Download your team's compliance report
            
            👉 Start by visiting **My Team** to see your team's current status.
            """)
        else:
            st.markdown("""
            **As an Employee, you can:**
            
            1. **View Dashboard** - See your compliance status
            2. **Track Progress** - Monitor your swipes and adjusted weekly average
            3. **Export Your Data** - Download your compliance record
            
            👉 Visit the **Dashboard** to see your current compliance status.
            """)
        
        st.divider()
        
        # System Status
        st.markdown("### 🔧 System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("App Version", "1.0.0")
        
        with col2:
            st.metric("Last Data Sync", "Not configured")
        
        with col3:
            st.metric("Status", "✅ Operational")
        
        # Help and Support
        with st.expander("❓ Help & Support"):
            st.markdown("""
            **Need Help?**
            
            - 📖 Check the **Documentation** page for detailed guides
            - 📧 Contact your HRBP for policy questions
            - 🐛 Report technical issues to the GOAT team
            
            **Quick Links:**
            - [Flexible Hybrid Policy](https://docs.google.com)
            - [HRBP Directory](https://docs.google.com)
            - [Technical Support](mailto:support@hellofresh.com)
            """)


if __name__ == "__main__":
    main()
