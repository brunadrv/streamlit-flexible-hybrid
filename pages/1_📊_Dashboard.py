"""
Dashboard Page - Main compliance overview and metrics
"""

import streamlit as st
from utils import require_login, initialize_auth, get_snowflake_connector, FlexibleHybridProcessor
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import yaml

# Page configuration
st.set_page_config(
    page_title="Dashboard - Flexible Hybrid",
    page_icon="📊",
    layout="wide"
)

# Require login
require_login()

# Initialize components
auth_manager = initialize_auth()
user = st.session_state.user

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Header
st.title("📊 Compliance Dashboard")
st.markdown(f"*Viewing data as: {user['name']} ({user['role'].upper()})*")

# Month selector
st.sidebar.markdown("### Filters")
months = list(config['flex_schedule']['months'].keys())
selected_month = st.sidebar.selectbox(
    "Select Reporting Month",
    months,
    index=len(months)-1 if months else 0
)

# Demo data flag
use_demo_data = st.sidebar.checkbox("Use Demo Data (for testing)", value=True)

# Function to load data
@st.cache_data(ttl=3600)
def load_compliance_data(month: str, use_demo: bool = False):
    """Load compliance data for the selected month"""
    
    if use_demo:
        # Generate demo data
        import numpy as np
        
        num_employees = 150
        
        demo_data = {
            'EMPLOYEE_ID': [f"EMP{str(i).zfill(6)}" for i in range(num_employees)],
            'FIRST_NAME': [f"First{i}" for i in range(num_employees)],
            'LAST_NAME': [f"Last{i}" for i in range(num_employees)],
            'DEPARTMENT': np.random.choice(['People', 'Operations', 'Meal Kits', 'Technology', 'Finance'], num_employees),
            'SWIPES_TOTAL': np.random.randint(8, 22, num_employees),
            'PTO_DAYS': np.random.randint(0, 5, num_employees),
            'LOA_DAYS': np.random.choice([0, 0, 0, 0, 5, 10], num_employees),
            'DAYS_POSSIBLE': np.random.randint(18, 21, num_employees),
            'ADJUSTED_WEEKLY_AVG': np.random.uniform(1.5, 4.0, num_employees),
            'IS_ESSENTIAL': np.random.choice([True, False], num_employees, p=[0.1, 0.9]),
            'HAS_EXCEPTION': np.random.choice([True, False], num_employees, p=[0.05, 0.95]),
            'IS_ON_LEAVE': np.random.choice([True, False], num_employees, p=[0.05, 0.95]),
        }
        
        df = pd.DataFrame(demo_data)
        
        # Calculate compliance status
        def get_status(row):
            if row['IS_ON_LEAVE']:
                return 'On Leave'
            if row['IS_ESSENTIAL']:
                return 'Essential (Exempt)'
            if row['HAS_EXCEPTION']:
                return 'Exception Granted'
            if row['ADJUSTED_WEEKLY_AVG'] >= 2.5:
                return 'Compliant'
            elif row['ADJUSTED_WEEKLY_AVG'] >= 2.0:
                return 'At Risk'
            else:
                return 'Non-Compliant'
        
        df['COMPLIANCE_STATUS'] = df.apply(get_status, axis=1)
        
        return df
    else:
        # TODO: Load real data from Snowflake
        st.warning("Real data loading not yet configured. Please use demo data.")
        return pd.DataFrame()

# Load data
df = load_compliance_data(selected_month, use_demo_data)

if df.empty:
    st.warning("No data available for the selected period.")
    st.stop()

# Apply access control filters
df_filtered = auth_manager.filter_data_by_access(
    df, 
    user['email'], 
    user['role']
)

# Calculate summary metrics
eligible_df = df_filtered[
    (~df_filtered['IS_ESSENTIAL']) & 
    (~df_filtered['HAS_EXCEPTION']) & 
    (~df_filtered['IS_ON_LEAVE'])
]

total_employees = len(df_filtered)
eligible_count = len(eligible_df)
compliant_count = len(eligible_df[eligible_df['COMPLIANCE_STATUS'] == 'Compliant'])
at_risk_count = len(eligible_df[eligible_df['COMPLIANCE_STATUS'] == 'At Risk'])
non_compliant_count = len(eligible_df[eligible_df['COMPLIANCE_STATUS'] == 'Non-Compliant'])

compliance_rate = (compliant_count / eligible_count * 100) if eligible_count > 0 else 0
avg_weekly_avg = eligible_df['ADJUSTED_WEEKLY_AVG'].mean() if eligible_count > 0 else 0

# Display metrics
st.markdown("## Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Employees",
        f"{total_employees:,}",
        help="Total employees in your view"
    )

with col2:
    st.metric(
        "Eligible Employees",
        f"{eligible_count:,}",
        help="Non-essential employees subject to policy"
    )

with col3:
    st.metric(
        "Compliance Rate",
        f"{compliance_rate:.1f}%",
        delta=f"{compliance_rate - 75:.1f}%" if compliance_rate >= 75 else f"{compliance_rate - 75:.1f}%",
        delta_color="normal" if compliance_rate >= 75 else "inverse",
        help="Percentage of eligible employees meeting 2.5 day threshold"
    )

with col4:
    st.metric(
        "At Risk",
        f"{at_risk_count:,}",
        help="Employees between 2.0 and 2.5 average"
    )

with col5:
    st.metric(
        "Non-Compliant",
        f"{non_compliant_count:,}",
        help="Employees below 2.0 average"
    )

st.divider()

# Visualizations
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Compliance Distribution")
    
    # Pie chart of compliance status
    status_counts = eligible_df['COMPLIANCE_STATUS'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        color=status_counts.index,
        color_discrete_map={
            'Compliant': '#00CC96',
            'At Risk': '#FFA15A',
            'Non-Compliant': '#EF553B'
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Average Weekly Average Distribution")
    
    # Histogram of adjusted weekly averages
    fig = px.histogram(
        eligible_df,
        x='ADJUSTED_WEEKLY_AVG',
        nbins=20,
        labels={'ADJUSTED_WEEKLY_AVG': 'Adjusted Weekly Average'},
        color_discrete_sequence=['#636EFA']
    )
    fig.add_vline(x=2.5, line_dash="dash", line_color="red", 
                  annotation_text="Threshold (2.5)")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Department breakdown (if admin or HRBP)
if user['role'] in ['admin', 'hrbp']:
    st.markdown("### Department Breakdown")
    
    # Calculate department stats
    dept_stats = eligible_df.groupby('DEPARTMENT').agg({
        'EMPLOYEE_ID': 'count',
        'ADJUSTED_WEEKLY_AVG': 'mean',
        'COMPLIANCE_STATUS': lambda x: (x == 'Compliant').sum()
    }).reset_index()
    
    dept_stats.columns = ['Department', 'Employee Count', 'Avg Weekly Avg', 'Compliant Count']
    dept_stats['Compliance Rate %'] = (dept_stats['Compliant Count'] / dept_stats['Employee Count'] * 100).round(1)
    dept_stats['Avg Weekly Avg'] = dept_stats['Avg Weekly Avg'].round(2)
    
    # Bar chart
    fig = px.bar(
        dept_stats,
        x='Department',
        y='Compliance Rate %',
        color='Compliance Rate %',
        color_continuous_scale=['red', 'yellow', 'green'],
        range_color=[0, 100],
        text='Compliance Rate %'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(showlegend=False)
    fig.add_hline(y=75, line_dash="dash", line_color="gray", 
                  annotation_text="Target (75%)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.dataframe(
        dept_stats.style.background_gradient(subset=['Compliance Rate %'], cmap='RdYlGn', vmin=0, vmax=100),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# Recent data table
st.markdown("### Recent Employee Data")

display_cols = [
    'EMPLOYEE_ID', 'FIRST_NAME', 'LAST_NAME', 'DEPARTMENT',
    'SWIPES_TOTAL', 'DAYS_POSSIBLE', 'ADJUSTED_WEEKLY_AVG', 'COMPLIANCE_STATUS'
]

# Filter options
status_filter = st.multiselect(
    "Filter by Status",
    options=['Compliant', 'At Risk', 'Non-Compliant', 'On Leave', 'Essential (Exempt)', 'Exception Granted'],
    default=['At Risk', 'Non-Compliant']
)

if status_filter:
    display_df = df_filtered[df_filtered['COMPLIANCE_STATUS'].isin(status_filter)]
else:
    display_df = df_filtered

# Style the dataframe
def color_compliance(val):
    if val == 'Compliant':
        return 'background-color: #d4edda'
    elif val == 'At Risk':
        return 'background-color: #fff3cd'
    elif val == 'Non-Compliant':
        return 'background-color: #f8d7da'
    return ''

styled_df = display_df[display_cols].style.applymap(
    color_compliance, 
    subset=['COMPLIANCE_STATUS']
)

st.dataframe(styled_df, use_container_width=True, height=400)

# Download button
csv = display_df.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name=f"flexible_hybrid_{selected_month}_filtered.csv",
    mime="text/csv"
)
