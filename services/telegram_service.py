import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError, 
    PhoneNumberInvalidError, 
    ApiIdInvalidError,
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    AuthKeyUnregisteredError
)
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.auth import CheckPhoneRequest
from models.phone_number import PhoneNumber
from models.validation_result import ValidationResult


class TelegramServiceException(Exception):
    """Base exception for TelegramService errors."""
    pass


class TelegramAuthenticationError(TelegramServiceException):
    """Raised when authentication with Telegram fails."""
    pass


class TelegramAPIError(TelegramServiceException):
    """Raised when Telegram API returns an error."""
    pass


class TelegramService:
    """
    Service for validating phone numbers against Telegram using MTProto API.
    
    This service uses the Telethon library to interact with Telegram's MTProto API
    to check if phone numbers are registered on the platform. It includes proper
    error handling, session management, and authentication.
    
    Attributes:
        api_id: Telegram API ID from my.telegram.org
        api_hash: Telegram API Hash from my.telegram.org
        session_name: Name for the Telegram session file
        client: Telethon TelegramClient instance
        is_authenticated: Whether the client is authenticated
        logger: Logger instance for this service
    """
    
    def __init__(self, api_id: str, api_hash: str, session_name: str = "turkish_phone_validator"):
        """
        Initialize TelegramService with API credentials.
        
        Args:
            api_id: Telegram API ID as string
            api_hash: Telegram API Hash
            session_name: Name for the session file (default: "turkish_phone_validator")
            
        Raises:
            TelegramAuthenticationError: If API credentials are invalid
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client: Optional[TelegramClient] = None
        self.is_authenticated = False
        self.logger = logging.getLogger(__name__)
        
        # Validate credentials
        if not api_id or not api_hash:
            raise TelegramAuthenticationError("API ID and API Hash are required")
        
        try:
            self.api_id_int = int(api_id)
        except ValueError:
            raise TelegramAuthenticationError("API ID must be a valid integer")
    
    async def initialize_session(self) -> bool:
        """
        Initialize and authenticate the Telegram session.
        
        This method creates a TelegramClient instance and attempts to authenticate
        with the provided credentials. It handles various authentication scenarios
        including existing sessions and new authentication requirements.
        
        Returns:
            bool: True if session initialization was successful, False otherwise
            
        Raises:
            TelegramAuthenticationError: If authentication fails
            TelegramAPIError: If API connection fails
        """
        try:
            self.logger.info("Initializing Telegram session...")
            
            # Create client instance
            self.client = TelegramClient(
                session=self.session_name,
                api_id=self.api_id_int,
                api_hash=self.api_hash
            )
            
            # Connect to Telegram
            await self.client.connect()
            
            # Check if already authenticated
            if await self.client.is_user_authorized():
                self.is_authenticated = True
                self.logger.info("Using existing authenticated session")
                return True
            
            # If not authenticated, we need phone number and code
            # For automated validation, we assume session is pre-authenticated
            # In a real scenario, this would require manual authentication setup
            self.logger.warning("Session not authenticated. Manual authentication required.")
            self.is_authenticated = False
            return False
            
        except ApiIdInvalidError:
            error_msg = "Invalid API ID or API Hash provided"
            self.logger.error(error_msg)
            raise TelegramAuthenticationError(error_msg)
        
        except AuthKeyUnregisteredError:
            error_msg = "Authentication key is unregistered. Please re-authenticate."
            self.logger.error(error_msg)
            raise TelegramAuthenticationError(error_msg)
        
        except Exception as e:
            error_msg = f"Failed to initialize Telegram session: {str(e)}"
            self.logger.error(error_msg)
            raise TelegramAPIError(error_msg)
    
    async def check_phone_registered(self, phone: str) -> ValidationResult:
        """
        Check if a phone number is registered on Telegram.
        
        This method validates a Turkish phone number against Telegram's database
        to determine if it's registered on the platform. It includes proper error
        handling and timing measurement.
        
        Args:
            phone: Phone number in +90 5XX XXX XX XX format
            
        Returns:
            ValidationResult: Result object containing validation details
            
        Raises:
            TelegramAPIError: If API call fails
            TelegramAuthenticationError: If session is not authenticated
        """
        if not self.client or not self.is_authenticated:
            error_msg = "Telegram session not initialized or authenticated"
            phone_obj = PhoneNumber(number=phone)
            return ValidationResult.create_error_result(phone_obj, error_msg)
        
        phone_obj = PhoneNumber(number=phone)
        start_time = time.time()
        
        try:
            self.logger.debug(f"Checking phone number: {phone}")
            
            # Normalize phone number for Telegram API
            normalized_phone = self._normalize_phone_number(phone)
            
            # Use Telegram's CheckPhone method to verify registration
            result = await self.client(CheckPhoneRequest(phone_number=normalized_phone))
            
            response_time = time.time() - start_time
            is_registered = result.phone_registered
            
            self.logger.debug(f"Phone {phone} check completed: {'registered' if is_registered else 'not registered'}")
            
            return ValidationResult.create_success_result(
                phone_number=phone_obj,
                is_registered=is_registered,
                response_time=response_time
            )
            
        except PhoneNumberInvalidError:
            response_time = time.time() - start_time
            error_msg = f"Invalid phone number format: {phone}"
            self.logger.warning(error_msg)
            return ValidationResult.create_error_result(phone_obj, error_msg, response_time)
        
        except FloodWaitError as e:
            response_time = time.time() - start_time
            error_msg = f"Rate limited by Telegram. Wait {e.seconds} seconds"
            self.logger.warning(error_msg)
            return ValidationResult.create_error_result(phone_obj, error_msg, response_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Telegram API error: {str(e)}"
            self.logger.error(error_msg)
            return ValidationResult.create_error_result(phone_obj, error_msg, response_time)
    
    def _normalize_phone_number(self, phone: str) -> str:
        """
        Normalize phone number for Telegram API.
        
        Telegram API expects phone numbers without the + prefix and spaces.
        Converts +90 5XX XXX XX XX to 905XXXXXXXXX format.
        
        Args:
            phone: Phone number in any format
            
        Returns:
            str: Normalized phone number for API
        """
        # Remove all non-digit characters except +
        normalized = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Remove + prefix if present
        if normalized.startswith('+'):
            normalized = normalized[1:]
        
        # Ensure it starts with 90 for Turkish numbers
        if not normalized.startswith('90') and normalized.startswith('5'):
            normalized = '90' + normalized
        
        return normalized
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the Telegram connection and return status information.
        
        This method performs a basic connectivity test and returns detailed
        information about the connection status, authentication state, and
        any potential issues.
        
        Returns:
            Dict[str, Any]: Dictionary containing connection test results
        """
        result = {
            'connected': False,
            'authenticated': False,
            'user_info': None,
            'error': None,
            'response_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            if not self.client:
                await self.initialize_session()
            
            if self.client and await self.client.is_user_authorized():
                result['connected'] = True
                result['authenticated'] = True
                
                # Get user information
                me = await self.client.get_me()
                result['user_info'] = {
                    'id': me.id,
                    'username': me.username,
                    'phone': me.phone,
                    'first_name': me.first_name,
                    'last_name': me.last_name
                }
                
                self.logger.info("Telegram connection test successful")
            else:
                result['error'] = "Not authenticated"
                self.logger.warning("Telegram connection test failed: Not authenticated")
        
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Telegram connection test failed: {str(e)}")
        
        result['response_time'] = time.time() - start_time
        return result
    
    async def disconnect(self) -> None:
        """
        Disconnect from Telegram and cleanup resources.
        
        This method properly closes the Telegram connection and cleans up
        any resources used by the client.
        """
        if self.client:
            try:
                await self.client.disconnect()
                self.logger.info("Telegram client disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting Telegram client: {str(e)}")
            finally:
                self.client = None
                self.is_authenticated = False
    
    def is_connected(self) -> bool:
        """
        Check if the client is connected to Telegram.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.client is not None and self.client.is_connected()
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.
        
        Returns:
            Dict[str, Any]: Session information including connection and auth status
        """
        return {
            'session_name': self.session_name,
            'api_id': self.api_id,
            'connected': self.is_connected(),
            'authenticated': self.is_authenticated,
            'client_initialized': self.client is not None
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()