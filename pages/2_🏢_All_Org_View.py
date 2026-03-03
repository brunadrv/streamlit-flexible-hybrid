"""
All Org View Page - Comprehensive organizational reporting
Accessible by: Admin, HRBP
"""

import streamlit as st
from utils import require_login, initialize_auth
import pandas as pd
import plotly.express as px
import yaml

st.set_page_config(
    page_title="All Org View - Flexible Hybrid",
    page_icon="🏢",
    layout="wide"
)

# Require login
require_login()

# Initialize auth
auth_manager = initialize_auth()
user = st.session_state.user

# Check permissions
auth_manager.require_permission('view_all_org')

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Header
st.title("🏢 All Org View")
st.markdown("*Comprehensive organizational compliance reporting*")

st.info("This page shows all organization data with detailed employee-level information.")

# Month selector
months = list(config['flex_schedule']['months'].keys())
selected_month = st.sidebar.selectbox(
    "Select Reporting Month",
    months,
    index=len(months)-1 if months else 0
)

# TODO: Load actual data
st.warning("⚠️ Data integration pending. This is a placeholder page.")

st.markdown("""
**Available Features (when data is loaded):**

- 📋 Complete employee roster with compliance status
- 🔍 Advanced filtering and search
- 📊 Detailed metrics by supervisory org
- 📈 Trend analysis across months
- 📤 Bulk export capabilities
- 🎯 Identify employees needing interventions
""")

# Placeholder for future implementation
with st.expander("🔧 Implementation Notes"):
    st.markdown("""
    This page will:
    1. Load complete roster from Snowflake
    2. Display all employees regardless of department
    3. Show detailed breakdown by Supervisory Org levels
    4. Allow drill-down into specific teams
    5. Provide export for ELT reporting
    """)
