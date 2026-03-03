"""
Google Sheets Integration
Handles reading and writing to Google Sheets for manual data sources
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from typing import Optional
import os


class GoogleSheetsConnector:
    """Manages Google Sheets connections"""
    
    def __init__(self, credentials_file: Optional[str] = None):
        self.credentials_file = credentials_file or os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
        self.client = None
        
    def connect(self) -> bool:
        """Establish connection to Google Sheets API"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, 
                scope
            )
            self.client = gspread.authorize(creds)
            return True
        except Exception as e:
            st.error(f"Failed to connect to Google Sheets: {str(e)}")
            return False
    
    def read_sheet(self, 
                   sheet_url: str, 
                   worksheet_name: str = None,
                   worksheet_index: int = 0) -> pd.DataFrame:
        """
        Read data from a Google Sheet
        
        Args:
            sheet_url: URL or ID of the Google Sheet
            worksheet_name: Name of specific worksheet (optional)
            worksheet_index: Index of worksheet if name not provided
            
        Returns:
            DataFrame with sheet data
        """
        try:
            if not self.client:
                if not self.connect():
                    return pd.DataFrame()
            
            # Open the spreadsheet
            if 'docs.google.com' in sheet_url:
                spreadsheet = self.client.open_by_url(sheet_url)
            else:
                spreadsheet = self.client.open_by_key(sheet_url)
            
            # Get the worksheet
            if worksheet_name:
                worksheet = spreadsheet.worksheet(worksheet_name)
            else:
                worksheet = spreadsheet.get_worksheet(worksheet_index)
            
            # Get all values and convert to DataFrame
            data = worksheet.get_all_values()
            
            if not data:
                return pd.DataFrame()
            
            # Use first row as headers
            df = pd.DataFrame(data[1:], columns=data[0])
            
            return df
        except Exception as e:
            st.error(f"Failed to read Google Sheet: {str(e)}")
            return pd.DataFrame()
    
    def write_sheet(self,
                    sheet_url: str,
                    df: pd.DataFrame,
                    worksheet_name: str = None,
                    worksheet_index: int = 0,
                    clear_first: bool = True) -> bool:
        """
        Write DataFrame to a Google Sheet
        
        Args:
            sheet_url: URL or ID of the Google Sheet
            df: DataFrame to write
            worksheet_name: Name of specific worksheet (optional)
            worksheet_index: Index of worksheet if name not provided
            clear_first: Whether to clear existing data first
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                if not self.connect():
                    return False
            
            # Open the spreadsheet
            if 'docs.google.com' in sheet_url:
                spreadsheet = self.client.open_by_url(sheet_url)
            else:
                spreadsheet = self.client.open_by_key(sheet_url)
            
            # Get the worksheet
            if worksheet_name:
                worksheet = spreadsheet.worksheet(worksheet_name)
            else:
                worksheet = spreadsheet.get_worksheet(worksheet_index)
            
            # Clear existing data if requested
            if clear_first:
                worksheet.clear()
            
            # Convert DataFrame to list of lists
            data = [df.columns.tolist()] + df.values.tolist()
            
            # Update the worksheet
            worksheet.update('A1', data)
            
            return True
        except Exception as e:
            st.error(f"Failed to write to Google Sheet: {str(e)}")
            return False
    
    def get_wework_swipes(self, sheet_url: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get WeWork swipe data from Chicago tracker
        
        Args:
            sheet_url: URL to WeWork swipe tracker
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with swipe counts per employee
        """
        df = self.read_sheet(sheet_url)
        
        if df.empty:
            return pd.DataFrame(columns=['EMPLOYEE_ID', 'SWIPES_MANUAL'])
        
        # Filter by date range
        df['DATE'] = pd.to_datetime(df['DATE'])
        mask = (df['DATE'] >= start_date) & (df['DATE'] <= end_date)
        df_filtered = df[mask]
        
        # Aggregate swipes per employee
        if not df_filtered.empty:
            swipes = df_filtered.groupby('EMPLOYEE_ID').agg({
                'SWIPE_COUNT': 'sum'
            }).reset_index()
            swipes.columns = ['EMPLOYEE_ID', 'SWIPES_MANUAL']
            return swipes
        
        return pd.DataFrame(columns=['EMPLOYEE_ID', 'SWIPES_MANUAL'])


@st.cache_resource
def get_gsheets_connector():
    """Cached Google Sheets connector instance"""
    return GoogleSheetsConnector()
