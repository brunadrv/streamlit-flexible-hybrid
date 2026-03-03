"""
Snowflake Connection Manager
Handles all connections and queries to Snowflake data warehouse
"""

import snowflake.connector
import pandas as pd
from typing import Optional, Dict, Any
import streamlit as st
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class SnowflakeConnector:
    """Manages Snowflake connections and queries"""
    
    def __init__(self):
        self.connection = None
        
    def connect(self) -> bool:
        """Establish connection to Snowflake"""
        try:
            # Try to use Streamlit secrets first, fall back to env variables
            if hasattr(st, 'secrets') and 'snowflake' in st.secrets:
                credentials = st.secrets['snowflake']
            else:
                credentials = {
                    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
                    'user': os.getenv('SNOWFLAKE_USER'),
                    'password': os.getenv('SNOWFLAKE_PASSWORD'),
                    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
                    'database': os.getenv('SNOWFLAKE_DATABASE'),
                    'schema': os.getenv('SNOWFLAKE_SCHEMA'),
                    'role': os.getenv('SNOWFLAKE_ROLE')
                }
            
            self.connection = snowflake.connector.connect(
                account=credentials['account'],
                user=credentials['user'],
                password=credentials['password'],
                warehouse=credentials['warehouse'],
                database=credentials['database'],
                schema=credentials['schema'],
                role=credentials.get('role')
            )
            return True
        except Exception as e:
            st.error(f"Failed to connect to Snowflake: {str(e)}")
            return False
    
    def close(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Execute a query and return results as DataFrame"""
        try:
            if not self.connection:
                if not self.connect():
                    return pd.DataFrame()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            
            # Fetch results and column names
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchall()
            
            cursor.close()
            
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            return pd.DataFrame()
    
    def get_kitchen_sink_roster(self, as_of_date: Optional[str] = None) -> pd.DataFrame:
        """
        Get active employee roster from Kitchen Sink view
        
        Args:
            as_of_date: Date string in YYYY-MM-DD format
            
        Returns:
            DataFrame with employee roster data
        """
        if not as_of_date:
            as_of_date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
        SELECT 
            EMPLOYEE_ID,
            POSITION_ID,
            FIRST_NAME,
            LAST_NAME,
            WORK_EMAIL,
            WORK_LOCATION,
            DEPARTMENT,
            SUPERVISORY_ORG_1,
            SUPERVISORY_ORG_2,
            SUPERVISORY_ORG_3,
            SUPERVISORY_ORG_4,
            SUPERVISORY_ORG_5,
            MANAGER_NAME,
            MANAGER_EMAIL,
            SKIP_LEVEL_MANAGER_NAME,
            SKIP_LEVEL_MANAGER_EMAIL,
            HIRE_DATE,
            TERMINATION_DATE,
            ACTIVE_STATUS
        FROM US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_WORKDAY_KITCHEN_SINK_PI
        WHERE ACTIVE_STATUS = 'Active'
            AND TERMINATION_DATE IS NULL
        ORDER BY LAST_NAME, FIRST_NAME
        """
        
        return self.execute_query(query)
    
    def get_lenel_swipes(self, start_date: str, end_date: str, employee_ids: Optional[list] = None) -> pd.DataFrame:
        """
        Get badge swipe data from Lenel system
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            employee_ids: Optional list of employee IDs to filter
            
        Returns:
            DataFrame with swipe counts per employee
        """
        employee_filter = ""
        if employee_ids:
            ids_str = ','.join([f"'{id}'" for id in employee_ids])
            employee_filter = f"AND EMPLOYEE_ID IN ({ids_str})"
        
        query = f"""
        SELECT 
            EMPLOYEE_ID,
            DATE(EVENT_TIME) as SWIPE_DATE,
            COUNT(DISTINCT DATE(EVENT_TIME)) as SWIPE_COUNT
        FROM US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_LENEL_S2_EVENTS_180_DAYS_v2
        WHERE DATE(EVENT_TIME) BETWEEN '{start_date}' AND '{end_date}'
            {employee_filter}
        GROUP BY EMPLOYEE_ID, DATE(EVENT_TIME)
        ORDER BY EMPLOYEE_ID, SWIPE_DATE
        """
        
        df = self.execute_query(query)
        
        # Aggregate to total swipes per employee
        if not df.empty:
            df_agg = df.groupby('EMPLOYEE_ID').agg({
                'SWIPE_COUNT': 'sum'
            }).reset_index()
            df_agg.columns = ['EMPLOYEE_ID', 'SWIPES_LENEL']
            return df_agg
        
        return pd.DataFrame(columns=['EMPLOYEE_ID', 'SWIPES_LENEL'])
    
    def get_pto_days(self, start_date: str, end_date: str, employee_ids: Optional[list] = None) -> pd.DataFrame:
        """
        Get PTO days from ADP time off requests
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            employee_ids: Optional list of employee IDs to filter
            
        Returns:
            DataFrame with PTO day counts per employee
        """
        employee_filter = ""
        if employee_ids:
            ids_str = ','.join([f"'{id}'" for id in employee_ids])
            employee_filter = f"AND EMPLOYEE_ID IN ({ids_str})"
        
        query = f"""
        SELECT 
            EMPLOYEE_ID,
            COUNT(DISTINCT TIME_OFF_DATE) as PTO_DAYS
        FROM US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_ADP_TIME_OFF_APPROVED
        WHERE TIME_OFF_DATE BETWEEN '{start_date}' AND '{end_date}'
            AND TIME_OFF_STATUS = 'Approved'
            {employee_filter}
        GROUP BY EMPLOYEE_ID
        """
        
        return self.execute_query(query)
    
    def get_employee_schedules(self, employee_ids: Optional[list] = None) -> pd.DataFrame:
        """
        Get employee schedule information from Workday
        
        Args:
            employee_ids: Optional list of employee IDs to filter
            
        Returns:
            DataFrame with employee schedules
        """
        employee_filter = ""
        if employee_ids:
            ids_str = ','.join([f"'{id}'" for id in employee_ids])
            employee_filter = f"WHERE EMPLOYEE_ID IN ({ids_str})"
        
        query = f"""
        SELECT 
            EMPLOYEE_ID,
            SCHEDULE_NAME,
            EFFECTIVE_DATE
        FROM US_PEOPLE_INSIGHTS.WORKDAY.INT0136_WORKER_SCHEDULE_CHANGES
        {employee_filter}
        ORDER BY EMPLOYEE_ID, EFFECTIVE_DATE DESC
        """
        
        df = self.execute_query(query)
        
        # Get most recent schedule per employee
        if not df.empty:
            df = df.groupby('EMPLOYEE_ID').first().reset_index()
        
        return df


@st.cache_resource
def get_snowflake_connector():
    """Cached Snowflake connector instance"""
    return SnowflakeConnector()
