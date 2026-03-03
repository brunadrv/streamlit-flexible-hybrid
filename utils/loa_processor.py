"""
LOA (Leave of Absence) Processing Module
Handles processing of Workday LOA exports
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import streamlit as st


class LOAProcessor:
    """Processes Leave of Absence data from Workday"""
    
    @staticmethod
    def calculate_weekdays(start_date: str, end_date: str) -> int:
        """
        Calculate number of weekdays between two dates
        
        Args:
            start_date: Start date string in YYYY-MM-DD format
            end_date: End date string in YYYY-MM-DD format
            
        Returns:
            Number of weekdays
        """
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            # Generate date range and count weekdays
            date_range = pd.date_range(start, end, freq='D')
            weekdays = date_range[date_range.dayofweek < 5]  # Monday=0, Friday=4
            
            return len(weekdays)
        except Exception as e:
            st.error(f"Error calculating weekdays: {str(e)}")
            return 0
    
    @staticmethod
    def process_loa_export(df: pd.DataFrame, 
                          reporting_start: str,
                          reporting_end: str) -> pd.DataFrame:
        """
        Process Workday LOA export to calculate days on leave during reporting period
        
        Args:
            df: DataFrame from Workday LOA export
            reporting_start: Reporting period start date (YYYY-MM-DD)
            reporting_end: Reporting period end date (YYYY-MM-DD)
            
        Returns:
            Processed DataFrame with LOA days calculated
        """
        try:
            # Ensure date columns are datetime
            df['LOA_START_DATE'] = pd.to_datetime(df['LOA_START_DATE'])
            df['LOA_END_DATE'] = pd.to_datetime(df['LOA_END_DATE'])
            
            reporting_start_dt = pd.to_datetime(reporting_start)
            reporting_end_dt = pd.to_datetime(reporting_end)
            
            # Calculate overlap between LOA period and reporting period
            df['OVERLAP_START'] = df['LOA_START_DATE'].apply(
                lambda x: max(x, reporting_start_dt) if pd.notna(x) else reporting_start_dt
            )
            df['OVERLAP_END'] = df['LOA_END_DATE'].apply(
                lambda x: min(x, reporting_end_dt) if pd.notna(x) else reporting_end_dt
            )
            
            # Calculate weekdays in overlap period
            df['LOA_DAYS'] = df.apply(
                lambda row: LOAProcessor.calculate_weekdays(
                    row['OVERLAP_START'].strftime('%Y-%m-%d'),
                    row['OVERLAP_END'].strftime('%Y-%m-%d')
                ) if row['OVERLAP_START'] <= row['OVERLAP_END'] else 0,
                axis=1
            )
            
            # Determine if still on leave at end of reporting period
            df['IS_ON_LEAVE'] = df['LOA_END_DATE'] >= reporting_end_dt
            
            # Group by employee (in case of multiple LOAs)
            result = df.groupby('EMPLOYEE_ID').agg({
                'LOA_DAYS': 'sum',
                'IS_ON_LEAVE': 'any'
            }).reset_index()
            
            return result
        except Exception as e:
            st.error(f"Error processing LOA data: {str(e)}")
            return pd.DataFrame(columns=['EMPLOYEE_ID', 'LOA_DAYS', 'IS_ON_LEAVE'])
    
    @staticmethod
    def parse_loa_text_input(text_input: str) -> pd.DataFrame:
        """
        Parse LOA data from text input (for manual entry)
        
        Format: Employee ID, Days on Leave (one per line)
        Example:
        3722446,5
        3722447,3
        
        Args:
            text_input: Text string with LOA data
            
        Returns:
            DataFrame with parsed LOA data
        """
        try:
            lines = [line.strip() for line in text_input.split('\n') if line.strip()]
            
            data = []
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 2:
                    employee_id = parts[0]
                    loa_days = int(parts[1])
                    data.append({
                        'EMPLOYEE_ID': employee_id,
                        'LOA_DAYS': loa_days,
                        'IS_ON_LEAVE': loa_days > 0
                    })
            
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error parsing LOA input: {str(e)}")
            return pd.DataFrame(columns=['EMPLOYEE_ID', 'LOA_DAYS', 'IS_ON_LEAVE'])
    
    @staticmethod
    def format_loa_for_export(df: pd.DataFrame, 
                             reporting_start: str,
                             reporting_end: str) -> pd.DataFrame:
        """
        Format LOA data for export to match SOP format
        
        Args:
            df: Processed LOA DataFrame
            reporting_start: Reporting period start
            reporting_end: Reporting period end
            
        Returns:
            Formatted DataFrame ready for export
        """
        export_df = df[['EMPLOYEE_ID', 'LOA_DAYS', 'IS_ON_LEAVE']].copy()
        export_df['REPORTING_PERIOD'] = f"{reporting_start} to {reporting_end}"
        export_df['PROCESSED_DATE'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return export_df
