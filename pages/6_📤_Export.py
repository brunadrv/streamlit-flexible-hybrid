"""
Export Page - Download reports and data
Accessible by: All users (with appropriate filters)
"""

import streamlit as st
from utils import require_login, initialize_auth
import pandas as pd
import yaml
from datetime import datetime
import io

st.set_page_config(
    page_title="Export Data - Flexible Hybrid",
    page_icon="📤",
    layout="wide"
)

# Require login
require_login()

# Initialize auth
auth_manager = initialize_auth()
user = st.session_state.user

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Header
st.title("📤 Export Data")
st.markdown("*Download compliance reports and data exports*")

# Export type selection
st.markdown("## Select Export Type")

export_type = st.radio(
    "Choose what to export:",
    [
        "📊 Monthly Compliance Report",
        "🏢 All Org Tracker (Admin Only)",
        "🏛️ Department Report",
        "👥 Team Report",
        "📋 Disciplinary Action List",
        "📈 Trend Analysis (Multi-Month)"
    ],
    key="export_type"
)

st.divider()

# Month selection
months = list(config['flex_schedule']['months'].keys())

if "Trend Analysis" in export_type:
    st.markdown("### Select Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_month = st.selectbox("Start Month", months, key="start_month")
    with col2:
        end_month = st.selectbox("End Month", months, index=len(months)-1, key="end_month")
else:
    selected_month = st.selectbox("Select Reporting Month", months, index=len(months)-1)

st.divider()

# Export format
st.markdown("### Export Format")
export_format = st.radio(
    "Choose format:",
    ["CSV", "Excel (XLSX)", "Google Sheets"],
    horizontal=True
)

# Export options based on type
st.markdown("### Export Options")

col1, col2 = st.columns(2)

with col1:
    include_sensitive = st.checkbox(
        "Include Employee IDs",
        value=True,
        help="Include personally identifiable information"
    )
    
    include_exempt = st.checkbox(
        "Include Exempt Employees",
        value=False,
        help="Include Essential and Exception employees"
    )

with col2:
    include_summary = st.checkbox(
        "Include Summary Sheet",
        value=True,
        help="Add a summary tab with key metrics"
    )
    
    include_charts = st.checkbox(
        "Include Visualizations",
        value=False,
        help="Add charts (Excel only)",
        disabled=(export_format != "Excel (XLSX)")
    )

st.divider()

# Preview section
with st.expander("📋 Preview Export Data"):
    st.markdown("*Preview of data to be exported (first 10 rows):*")
    
    # Demo preview data
    preview_data = {
        'Employee ID': ['EMP001', 'EMP002', 'EMP003'],
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'Department': ['Technology', 'Operations', 'Finance'],
        'Swipes': [15, 18, 12],
        'Days Possible': [20, 20, 19],
        'Adjusted Weekly Avg': [3.75, 4.50, 3.16],
        'Compliance Status': ['Compliant', 'Compliant', 'Compliant']
    }
    
    preview_df = pd.DataFrame(preview_data)
    st.dataframe(preview_df, use_container_width=True)

st.divider()

# Export button
st.markdown("### Generate Export")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if st.button("🚀 Generate Export", type="primary", use_container_width=True):
        with st.spinner("Generating export..."):
            # TODO: Generate actual export based on selections
            
            # Create demo export data
            export_data = {
                'EMPLOYEE_ID': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
                'FIRST_NAME': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
                'LAST_NAME': ['Doe', 'Smith', 'Johnson', 'Williams', 'Brown'],
                'DEPARTMENT': ['Technology', 'Operations', 'Finance', 'People', 'Technology'],
                'SWIPES_TOTAL': [15, 18, 12, 20, 16],
                'PTO_DAYS': [0, 1, 2, 0, 1],
                'DAYS_POSSIBLE': [20, 19, 18, 20, 19],
                'ADJUSTED_WEEKLY_AVG': [3.75, 4.74, 3.33, 5.00, 4.21],
                'COMPLIANCE_STATUS': ['Compliant', 'Compliant', 'Compliant', 'Compliant', 'Compliant']
            }
            
            df_export = pd.DataFrame(export_data)
            
            # Generate file based on format
            if export_format == "CSV":
                csv = df_export.to_csv(index=False)
                file_name = f"flexible_hybrid_export_{datetime.now().strftime('%Y%m%d')}.csv"
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=file_name,
                    mime="text/csv",
                    use_container_width=True
                )
                
            elif export_format == "Excel (XLSX)":
                # Create Excel file with multiple sheets
                output = io.BytesIO()
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Main data sheet
                    df_export.to_excel(writer, sheet_name='Data', index=False)
                    
                    # Summary sheet if requested
                    if include_summary:
                        summary_data = {
                            'Metric': ['Total Employees', 'Compliance Rate', 'Avg Weekly Avg'],
                            'Value': [len(df_export), '100%', '4.21']
                        }
                        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                output.seek(0)
                file_name = f"flexible_hybrid_export_{datetime.now().strftime('%Y%m%d')}.xlsx"
                
                st.download_button(
                    label="📥 Download Excel",
                    data=output,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            else:  # Google Sheets
                st.info("""
                📊 **Google Sheets Export**
                
                To export to Google Sheets:
                1. Download the CSV version
                2. Open Google Sheets
                3. Go to File → Import → Upload
                4. Select the downloaded CSV file
                
                *Direct Google Sheets integration coming soon!*
                """)
                
                # Provide CSV download as fallback
                csv = df_export.to_csv(index=False)
                file_name = f"flexible_hybrid_export_{datetime.now().strftime('%Y%m%d')}.csv"
                
                st.download_button(
                    label="📥 Download CSV (for Google Sheets)",
                    data=csv,
                    file_name=file_name,
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.success("✅ Export generated successfully!")

with col2:
    st.metric("Estimated Rows", "—")

with col3:
    st.metric("File Size", "—")

# Recent exports section
st.divider()
st.markdown("### 📁 Recent Exports")

recent_exports = pd.DataFrame({
    'Timestamp': [
        datetime.now().strftime('%Y-%m-%d %H:%M'),
    ],
    'Type': ['Monthly Compliance Report'],
    'Month': ['2026-03'],
    'Format': ['CSV'],
    'Status': ['✅ Available']
})

st.dataframe(recent_exports, use_container_width=True, hide_index=True)

# Help section
with st.expander("❓ Export Help"):
    st.markdown("""
    **Export Types:**
    
    - **Monthly Compliance Report**: Standard monthly report with all compliance metrics
    - **All Org Tracker**: Complete organizational view (Admin/HRBP only)
    - **Department Report**: Department-specific data
    - **Team Report**: Manager's team data
    - **Disciplinary Action List**: List of non-compliant employees for follow-up
    - **Trend Analysis**: Multi-month comparison data
    
    **Formats:**
    
    - **CSV**: Simple format, works with Excel and Google Sheets
    - **Excel**: Multi-sheet workbook with formatting and optional charts
    - **Google Sheets**: Direct export to Google Sheets (requires configuration)
    
    **Best Practices:**
    
    - Review preview data before exporting
    - Use descriptive file names
    - Protect files containing employee IDs
    - Export regularly for record-keeping
    """)
