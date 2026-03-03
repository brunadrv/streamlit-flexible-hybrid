"""
Data Processing Module
Contains business logic for calculating flexible hybrid compliance metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yaml


class FlexibleHybridProcessor:
    """Processes flexible hybrid compliance data"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.flex_schedule = self.config.get('flex_schedule', {})
        self.compliance_threshold = self.flex_schedule.get('compliance_threshold', 2.5)
        self.schedule_types = self.flex_schedule.get('schedule_types', {})
    
    def get_month_config(self, month: str) -> Dict:
        """
        Get configuration for a specific month
        
        Args:
            month: Month string in YYYY-MM format
            
        Returns:
            Dictionary with month configuration
        """
        months = self.flex_schedule.get('months', {})
        return months.get(month, {})
    
    def calculate_days_possible(self, 
                                 month: str,
                                 pto_days: int = 0,
                                 loa_days: int = 0,
                                 company_holidays: int = 0) -> int:
        """
        Calculate possible working days for an employee in a month
        
        Formula: Base Days - PTO - LOA (company holidays already deducted from base)
        
        Args:
            month: Month string in YYYY-MM format
            pto_days: Number of PTO days taken
            loa_days: Number of LOA weekdays
            company_holidays: Number of company holidays (usually already in base)
            
        Returns:
            Total possible working days
        """
        month_config = self.get_month_config(month)
        base_days = month_config.get('days_possible', 20)
        
        # Subtract PTO and LOA from base days
        days_possible = base_days - pto_days - loa_days
        
        # Ensure days_possible doesn't go negative
        return max(0, days_possible)
    
    def calculate_adjusted_weekly_average(self,
                                          swipes_total: int,
                                          days_possible: int,
                                          exceptions: int = 0) -> float:
        """
        Calculate adjusted weekly average
        
        Formula: ((Swipes + Exceptions) / Days Possible) * 5
        
        Args:
            swipes_total: Total swipe count (Lenel + Manual)
            days_possible: Total possible working days
            exceptions: Number of exception days granted
            
        Returns:
            Adjusted weekly average (0-5 scale)
        """
        if days_possible == 0:
            return 0.0
        
        total_credited_days = swipes_total + exceptions
        adjusted_avg = (total_credited_days / days_possible) * 5
        
        return round(adjusted_avg, 2)
    
    def determine_compliance_status(self, 
                                    adjusted_avg: float,
                                    schedule_type: str = "Mon - Fri, 8 Hour Days (Default)",
                                    is_essential: bool = False,
                                    has_exception: bool = False,
                                    is_on_leave: bool = False) -> str:
        """
        Determine compliance status for an employee
        
        Args:
            adjusted_avg: Adjusted weekly average
            schedule_type: Employee schedule type
            is_essential: Whether employee is classified as essential
            has_exception: Whether employee has an exception
            is_on_leave: Whether employee is currently on leave
            
        Returns:
            Compliance status string
        """
        # Special cases
        if is_on_leave:
            return "On Leave"
        
        if is_essential:
            return "Essential (Exempt)"
        
        if has_exception:
            return "Exception Granted"
        
        # Get expected average for schedule type
        expected_avg = self.schedule_types.get(schedule_type, 2.5)
        
        # Determine compliance
        if adjusted_avg >= expected_avg:
            return "Compliant"
        elif adjusted_avg >= expected_avg * 0.8:  # Within 20% of target
            return "At Risk"
        else:
            return "Non-Compliant"
    
    def process_monthly_data(self,
                            roster_df: pd.DataFrame,
                            lenel_swipes_df: pd.DataFrame,
                            manual_swipes_df: pd.DataFrame,
                            pto_df: pd.DataFrame,
                            loa_df: pd.DataFrame,
                            schedules_df: pd.DataFrame,
                            exceptions_df: pd.DataFrame,
                            month: str) -> pd.DataFrame:
        """
        Process all monthly data and calculate compliance metrics
        
        Args:
            roster_df: Employee roster DataFrame
            lenel_swipes_df: Lenel swipes DataFrame
            manual_swipes_df: Manual swipes DataFrame (WeWork)
            pto_df: PTO days DataFrame
            loa_df: LOA days DataFrame
            schedules_df: Employee schedules DataFrame
            exceptions_df: Exceptions DataFrame
            month: Month string in YYYY-MM format
            
        Returns:
            Complete processed DataFrame with all metrics
        """
        # Start with roster
        df = roster_df.copy()
        
        # Merge swipes data
        df = df.merge(lenel_swipes_df, on='EMPLOYEE_ID', how='left')
        df = df.merge(manual_swipes_df, on='EMPLOYEE_ID', how='left')
        
        # Fill NaN swipes with 0
        df['SWIPES_LENEL'] = df['SWIPES_LENEL'].fillna(0).astype(int)
        df['SWIPES_MANUAL'] = df['SWIPES_MANUAL'].fillna(0).astype(int)
        
        # Calculate total swipes
        df['SWIPES_TOTAL'] = df['SWIPES_LENEL'] + df['SWIPES_MANUAL']
        
        # Merge PTO data
        df = df.merge(pto_df, on='EMPLOYEE_ID', how='left')
        df['PTO_DAYS'] = df['PTO_DAYS'].fillna(0).astype(int)
        
        # Merge LOA data
        df = df.merge(loa_df, on='EMPLOYEE_ID', how='left')
        df['LOA_DAYS'] = df['LOA_DAYS'].fillna(0).astype(int)
        df['IS_ON_LEAVE'] = df.get('IS_ON_LEAVE', False).fillna(False)
        
        # Merge schedules
        df = df.merge(schedules_df[['EMPLOYEE_ID', 'SCHEDULE_NAME']], on='EMPLOYEE_ID', how='left')
        df['SCHEDULE_NAME'] = df['SCHEDULE_NAME'].fillna('Mon - Fri, 8 Hour Days (Default)')
        
        # Merge exceptions
        df = df.merge(exceptions_df, on='EMPLOYEE_ID', how='left')
        df['EXCEPTIONS'] = df['EXCEPTIONS'].fillna(0).astype(int)
        df['HAS_EXCEPTION'] = df.get('HAS_EXCEPTION', False).fillna(False)
        df['IS_ESSENTIAL'] = df.get('IS_ESSENTIAL', False).fillna(False)
        
        # Calculate days possible
        month_config = self.get_month_config(month)
        company_holidays = month_config.get('company_holidays', 0)
        
        df['COMPANY_HOLIDAYS'] = company_holidays
        df['DAYS_POSSIBLE'] = df.apply(
            lambda row: self.calculate_days_possible(
                month, 
                row['PTO_DAYS'], 
                row['LOA_DAYS'],
                company_holidays
            ), 
            axis=1
        )
        
        # Calculate adjusted weekly average
        df['ADJUSTED_WEEKLY_AVG'] = df.apply(
            lambda row: self.calculate_adjusted_weekly_average(
                row['SWIPES_TOTAL'],
                row['DAYS_POSSIBLE'],
                row['EXCEPTIONS']
            ),
            axis=1
        )
        
        # Determine compliance status
        df['COMPLIANCE_STATUS'] = df.apply(
            lambda row: self.determine_compliance_status(
                row['ADJUSTED_WEEKLY_AVG'],
                row['SCHEDULE_NAME'],
                row['IS_ESSENTIAL'],
                row['HAS_EXCEPTION'],
                row['IS_ON_LEAVE']
            ),
            axis=1
        )
        
        # Add month column
        df['FLEX_HYBRID_MONTH'] = month
        
        # Add timestamp
        df['LAST_UPDATED'] = datetime.now()
        
        return df
    
    def generate_summary_stats(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for reporting
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        total_employees = len(df)
        
        # Filter for non-essential, non-exception employees
        eligible_df = df[
            (~df['IS_ESSENTIAL']) & 
            (~df['HAS_EXCEPTION']) & 
            (~df['IS_ON_LEAVE'])
        ]
        
        eligible_count = len(eligible_df)
        
        if eligible_count == 0:
            return {
                'total_employees': total_employees,
                'eligible_employees': 0,
                'compliant_count': 0,
                'at_risk_count': 0,
                'non_compliant_count': 0,
                'compliance_rate': 0,
                'avg_weekly_average': 0
            }
        
        compliant = len(eligible_df[eligible_df['COMPLIANCE_STATUS'] == 'Compliant'])
        at_risk = len(eligible_df[eligible_df['COMPLIANCE_STATUS'] == 'At Risk'])
        non_compliant = len(eligible_df[eligible_df['COMPLIANCE_STATUS'] == 'Non-Compliant'])
        
        return {
            'total_employees': total_employees,
            'eligible_employees': eligible_count,
            'compliant_count': compliant,
            'at_risk_count': at_risk,
            'non_compliant_count': non_compliant,
            'compliance_rate': round((compliant / eligible_count) * 100, 2),
            'avg_weekly_average': round(eligible_df['ADJUSTED_WEEKLY_AVG'].mean(), 2)
        }
    
    def generate_department_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate department-level summary
        
        Args:
            df: Processed DataFrame
            
        Returns:
            DataFrame with department summaries
        """
        # Filter for eligible employees
        eligible_df = df[
            (~df['IS_ESSENTIAL']) & 
            (~df['HAS_EXCEPTION']) & 
            (~df['IS_ON_LEAVE'])
        ]
        
        summary = eligible_df.groupby('DEPARTMENT').agg({
            'EMPLOYEE_ID': 'count',
            'ADJUSTED_WEEKLY_AVG': 'mean',
            'COMPLIANCE_STATUS': lambda x: (x == 'Compliant').sum()
        }).reset_index()
        
        summary.columns = ['DEPARTMENT', 'EMPLOYEE_COUNT', 'AVG_WEEKLY_AVERAGE', 'COMPLIANT_COUNT']
        summary['COMPLIANCE_RATE'] = (summary['COMPLIANT_COUNT'] / summary['EMPLOYEE_COUNT'] * 100).round(2)
        summary['AVG_WEEKLY_AVERAGE'] = summary['AVG_WEEKLY_AVERAGE'].round(2)
        
        return summary.sort_values('COMPLIANCE_RATE', ascending=False)
