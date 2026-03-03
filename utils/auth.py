"""
Authentication and Authorization Module
Handles user authentication and role-based access control
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
from typing import Optional, List, Dict


class AuthManager:
    """Manages authentication and authorization"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.load(f, Loader=SafeLoader)
        
        self.credentials = self.config.get('credentials', {})
        self.cookie_config = self.config.get('cookie', {})
        self.roles_config = self.config.get('roles', {})
        self.hrbp_assignments = self.config.get('hrbp_assignments', {})
        
        # Initialize authenticator
        self.authenticator = stauth.Authenticate(
            self.credentials,
            self.cookie_config['name'],
            self.cookie_config['key'],
            self.cookie_config['expiry_days']
        )
    
    def login(self) -> Optional[Dict]:
        """
        Display login form and authenticate user
        
        Returns:
            User information dict if authenticated, None otherwise
        """
        name, authentication_status, username = self.authenticator.login('Login', 'main')
        
        if authentication_status:
            return {
                'name': name,
                'username': username,
                'email': self.credentials['usernames'][username].get('email'),
                'role': self.credentials['usernames'][username].get('role')
            }
        elif authentication_status == False:
            st.error('Username/password is incorrect')
        elif authentication_status == None:
            st.warning('Please enter your username and password')
        
        return None
    
    def logout(self):
        """Display logout button"""
        self.authenticator.logout('Logout', 'sidebar')
    
    def get_user_permissions(self, user_role: str) -> List[str]:
        """
        Get list of permissions for a user role
        
        Args:
            user_role: User role string
            
        Returns:
            List of permission strings
        """
        role_config = self.roles_config.get(user_role, {})
        return role_config.get('permissions', [])
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """
        Check if user has specific permission
        
        Args:
            user_role: User role string
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        permissions = self.get_user_permissions(user_role)
        return permission in permissions
    
    def get_user_departments(self, user_email: str, user_role: str) -> Optional[List[str]]:
        """
        Get list of departments assigned to HRBP
        
        Args:
            user_email: User email address
            user_role: User role
            
        Returns:
            List of department names, or None if user has access to all
        """
        # Admins have access to all departments
        if user_role == 'admin':
            return None
        
        # HRBPs have access to assigned departments
        if user_role == 'hrbp':
            return self.hrbp_assignments.get(user_email, [])
        
        # Other roles don't have department-level access
        return []
    
    def filter_data_by_access(self, 
                              df: pd.DataFrame, 
                              user_email: str,
                              user_role: str,
                              manager_email_col: str = 'MANAGER_EMAIL') -> pd.DataFrame:
        """
        Filter DataFrame based on user's access level
        
        Args:
            df: DataFrame to filter
            user_email: User's email address
            user_role: User's role
            manager_email_col: Column name containing manager email
            
        Returns:
            Filtered DataFrame
        """
        # Admins see everything
        if user_role == 'admin':
            return df
        
        # HRBPs see their assigned departments
        if user_role == 'hrbp':
            departments = self.get_user_departments(user_email, user_role)
            if departments:
                return df[df['DEPARTMENT'].isin(departments)]
            return df
        
        # Managers see only their direct reports
        if user_role == 'manager':
            return df[df[manager_email_col] == user_email]
        
        # Employees see only their own data
        if user_role == 'employee':
            return df[df['WORK_EMAIL'] == user_email]
        
        # Default: no access
        return pd.DataFrame()
    
    def require_permission(self, permission: str):
        """
        Decorator/function to require a specific permission
        Redirects user if they don't have permission
        
        Args:
            permission: Required permission string
        """
        if 'user' not in st.session_state:
            st.error("You must be logged in to view this page")
            st.stop()
        
        user_role = st.session_state.user.get('role')
        if not self.has_permission(user_role, permission):
            st.error(f"You don't have permission to access this feature. Required permission: {permission}")
            st.stop()


def initialize_auth() -> AuthManager:
    """Initialize authentication manager in session state"""
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    return st.session_state.auth_manager


def require_login():
    """Decorator function to require login for a page"""
    auth_manager = initialize_auth()
    
    if 'user' not in st.session_state:
        st.title("🔐 Flexible Hybrid Reporting")
        st.markdown("### Please log in to continue")
        
        user = auth_manager.login()
        
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user['name']}!")
            st.rerun()
        else:
            st.stop()
