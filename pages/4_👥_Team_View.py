"""
Team View Page - Manager view of direct reports
Accessible by: Managers
"""

import streamlit as st
from utils import require_login, initialize_auth
import yaml

st.set_page_config(
    page_title="My Team - Flexible Hybrid",
    page_icon="👥",
    layout="wide"
)

# Require login
require_login()

# Initialize auth
auth_manager = initialize_auth()
user = st.session_state.user

# Check permissions
auth_manager.require_permission('view_own_team')

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Header
st.title("👥 My Team")
st.markdown(f"*Viewing direct reports for: {user['name']}*")

# Month selector
months = list(config['flex_schedule']['months'].keys())
selected_month = st.sidebar.selectbox(
    "Select Reporting Month",
    months,
    index=len(months)-1 if months else 0
)

st.info("This page shows compliance data for your direct reports only.")

# TODO: Load team data filtered by manager email
st.warning("⚠️ Data integration pending. This is a placeholder page.")

st.markdown("""
**Available Features (when data is loaded):**

- 👥 View all direct reports' compliance status
- 📊 Team compliance metrics and trends
- 🎯 Identify team members needing support
- 📤 Export team report
- 📧 Email reminders to team members (future)
""")

# Placeholder metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Team Size", "—")

with col2:
    st.metric("Team Compliance Rate", "—")

with col3:
    st.metric("At Risk", "—")

with col4:
    st.metric("Non-Compliant", "—")
