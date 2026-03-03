"""
Department View Page - Department-specific reporting
Accessible by: Admin, HRBP
"""

import streamlit as st
from utils import require_login, initialize_auth
import yaml

st.set_page_config(
    page_title="Department View - Flexible Hybrid",
    page_icon="🏛️",
    layout="wide"
)

# Require login
require_login()

# Initialize auth
auth_manager = initialize_auth()
user = st.session_state.user

# Check permissions
auth_manager.require_permission('view_assigned_departments')

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Header
st.title("🏛️ Department View")

# Get user's assigned departments
assigned_depts = auth_manager.get_user_departments(user['email'], user['role'])

if assigned_depts is None:
    st.markdown("*Viewing all departments (Admin access)*")
else:
    st.markdown(f"*Viewing assigned departments: {', '.join(assigned_depts)}*")

# Month selector
months = list(config['flex_schedule']['months'].keys())
selected_month = st.sidebar.selectbox(
    "Select Reporting Month",
    months,
    index=len(months)-1 if months else 0
)

st.info("This page shows department-specific compliance data for your assigned areas.")

# TODO: Load department data
st.warning("⚠️ Data integration pending. This is a placeholder page.")

st.markdown("""
**Available Features (when data is loaded):**

- 🏛️ Department-level compliance metrics
- 👥 Team breakdown within departments
- 📊 Manager-level compliance tracking
- 🎯 Identify teams needing support
- 📧 Generate reports for distribution to managers
""")
