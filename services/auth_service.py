"""
Authentication Service
Handles user authentication and authorization in a stateless manner
"""

from typing import Dict, Optional, Tuple, Any
import jwt
from datetime import datetime, timedelta

from supabase_service import SupabaseService
from monitoring import logger, monitor_database_query

class AuthService:
    """Stateless authentication service"""
    
    def __init__(self, supabase_service: SupabaseService):
        self.supabase_service = supabase_service
    
    @monitor_database_query()
    def signup_user(self, email: str, password: str, name: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Sign up a new user
        
        Args:
            email: User email
            password: User password
            name: Optional display name
            
        Returns:
            Tuple of (success, message, user_data)
        """
        try:
            # Validate input
            if not email or not password:
                return False, "Email and password are required", None
            
            if len(password) < 6:
                return False, "Password must be at least 6 characters", None
            
            # Attempt signup through Supabase
            user_data_dict = {'name': name} if name else {}
            success, message, user_data = self.supabase_service.sign_up(email, password, user_data_dict)
            
            if success:
                logger.info("User signed up successfully",
                           email=email,
                           user_id=user_data.get('id') if user_data else None)
            else:
                logger.warning("User signup failed",
                              email=email,
                              error_message=message)
            
            return success, message, user_data
            
        except Exception as e:
            logger.error("Signup error", error=e, email=email)
            return False, "Internal server error during signup", None
    
    @monitor_database_query()
    def signin_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Sign in an existing user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message, user_data_with_token)
        """
        try:
            # Validate input
            if not email or not password:
                return False, "Email and password are required", None
            
            # Attempt signin through Supabase
            success, message, user_data = self.supabase_service.sign_in(email, password)
            
            if success:
                logger.info("User signed in successfully",
                           email=email,
                           user_id=user_data.get('user', {}).get('id') if user_data else None)
            else:
                logger.warning("User signin failed",
                              email=email,
                              error_message=message)
            
            return success, message, user_data
            
        except Exception as e:
            logger.error("Signin error", error=e, email=email)
            return False, "Internal server error during signin", None
    
    def signout_user(self, access_token: str) -> Tuple[bool, str]:
        """
        Sign out a user
        
        Args:
            access_token: User's access token
            
        Returns:
            Tuple of (success, message)
        """
        try:
            success, message = self.supabase_service.signout_user(access_token)
            
            if success:
                logger.info("User signed out successfully")
            else:
                logger.warning("User signout failed", error_message=message)
            
            return success, message
            
        except Exception as e:
            logger.error("Signout error", error=e)
            return False, "Internal server error during signout"
    
    def get_current_user(self, access_token: str) -> Optional[Dict]:
        """
        Get current user from access token
        
        Args:
            access_token: JWT access token
            
        Returns:
            User data or None if invalid
        """
        try:
            user_data = self.supabase_service.get_current_user_from_token(access_token)
            
            if user_data:
                logger.debug("Retrieved current user",
                           user_id=user_data.get('user_id'))
            
            return user_data
            
        except Exception as e:
            logger.error("Get current user error", error=e)
            return None
    
    def validate_token(self, access_token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Validate an access token
        
        Args:
            access_token: JWT access token
            
        Returns:
            Tuple of (is_valid, user_data)
        """
        try:
            user_data = self.get_current_user(access_token)
            
            if user_data:
                return True, user_data
            else:
                return False, None
                
        except Exception as e:
            logger.error("Token validation error", error=e)
            return False, None
    
    def extract_user_from_request(self, request) -> Optional[Dict]:
        """
        Extract user from Flask request
        
        Args:
            request: Flask request object
            
        Returns:
            User data or None
        """
        try:
            # Try Authorization header first
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                is_valid, user_data = self.validate_token(token)
                if is_valid:
                    return user_data
            
            # Fallback to request body user data
            request_data = request.get_json() or {}
            user_from_request = request_data.get('user')
            
            if user_from_request and isinstance(user_from_request, dict):
                # Validate that this user data is legitimate
                user_id = user_from_request.get('id')
                if user_id:
                    # Verify user exists in database
                    profile = self.supabase_service.get_user_profile(user_id)
                    if profile:
                        return {
                            'user_id': user_id,
                            'email': user_from_request.get('email'),
                            'name': user_from_request.get('name')
                        }
            
            return None
            
        except Exception as e:
            logger.error("Extract user from request error", error=e)
            return None
    
    def require_auth(self, request) -> Tuple[bool, Optional[Dict], str]:
        """
        Require authentication for a request
        
        Args:
            request: Flask request object
            
        Returns:
            Tuple of (is_authenticated, user_data, error_message)
        """
        user_data = self.extract_user_from_request(request)
        
        if user_data:
            return True, user_data, ""
        else:
            return False, None, "Authentication required"
    
    @monitor_database_query()
    def refresh_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Refresh user profile from database
        
        Args:
            user_id: User identifier
            
        Returns:
            Updated user profile or None
        """
        try:
            profile = self.supabase_service.get_user_profile(user_id)
            
            if profile:
                logger.debug("User profile refreshed", user_id=user_id)
            else:
                logger.warning("User profile not found", user_id=user_id)
            
            return profile
            
        except Exception as e:
            logger.error("Refresh user profile error", error=e, user_id=user_id)
            return None