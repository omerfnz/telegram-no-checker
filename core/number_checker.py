"""
Number checker service for Telegram validation.

This module handles number validation using Telegram API.
"""

import asyncio
import logging
from typing import List, Optional, Callable, Dict, Any
from datetime import datetime

from .telegram_client import TelegramClientManager
from .anti_robot_driver import AntiRobotDriver, RateLimitConfig
from data.models import NumberRecord, Contact
from data.database import DatabaseManager


class NumberChecker:
    """
    Service for checking phone numbers on Telegram.
    
    This class handles:
    - Number validation using Telegram API
    - Database integration
    - Progress tracking
    - Error handling
    """
    
    def __init__(
        self,
        telegram_client: TelegramClientManager,
        database: DatabaseManager,
        anti_robot_driver: Optional[AntiRobotDriver] = None
    ):
        """
        Initialize the number checker.
        
        Args:
            telegram_client: Telegram client manager
            database: Database manager
            anti_robot_driver: Anti-robot driver for rate limiting
        """
        self.telegram_client = telegram_client
        self.database = database
        self.anti_robot_driver = anti_robot_driver or AntiRobotDriver()
        self.logger = logging.getLogger(__name__)
        
        # Progress tracking
        self.total_numbers = 0
        self.checked_numbers = 0
        self.valid_numbers = 0
        self.invalid_numbers = 0
        self.failed_numbers = 0
        
        # Callbacks
        self.progress_callback: Optional[Callable] = None
        self.completion_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable) -> None:
        """
        Set progress callback function.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback
    
    def set_completion_callback(self, callback: Callable) -> None:
        """
        Set completion callback function.
        
        Args:
            callback: Function to call when checking is complete
        """
        self.completion_callback = callback
    
    def _update_progress(self) -> None:
        """Update progress and call callback if set."""
        if self.progress_callback:
            progress_data = {
                'total': self.total_numbers,
                'checked': self.checked_numbers,
                'valid': self.valid_numbers,
                'invalid': self.invalid_numbers,
                'failed': self.failed_numbers,
                'percentage': (self.checked_numbers / self.total_numbers * 100) if self.total_numbers > 0 else 0
            }
            self.progress_callback(progress_data)
    
    async def check_single_number(self, phone_number: str) -> Optional[bool]:
        """
        Check a single phone number.
        
        Args:
            phone_number: Phone number to check (with country code)
            
        Returns:
            Optional[bool]: True if valid, False if invalid, None if error
        """
        try:
            # Wait for rate limiting
            await self.anti_robot_driver.wait_if_needed()
            
            # Check number
            result = await self.telegram_client.check_number_exists(phone_number)
            
            # Record request
            self.anti_robot_driver.record_request(result is not None)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking number {phone_number}: {e}")
            self.anti_robot_driver.record_request(success=False)
            return None
    
    async def check_number_record(self, number_record: NumberRecord) -> bool:
        """
        Check a number record and update database.
        
        Args:
            number_record: NumberRecord to check
            
        Returns:
            bool: True if check was successful, False otherwise
        """
        try:
            # Check if already checked recently (within 24 hours)
            if number_record.is_checked and number_record.check_date:
                hours_since_check = (datetime.now() - number_record.check_date).total_seconds() / 3600
                if hours_since_check < 24:
                    self.logger.debug(f"Number {number_record.full_number} checked recently, skipping")
                    return True
            
            # Check number
            result = await self.check_single_number(number_record.full_number)
            
            if result is not None:
                # Update record
                number_record.is_valid = result
                number_record.is_checked = True
                number_record.check_date = datetime.now()
                number_record.check_count += 1
                
                # Update database
                success = self.database.update_number_record(number_record)
                
                if success:
                    self.checked_numbers += 1
                    if result:
                        self.valid_numbers += 1
                    else:
                        self.invalid_numbers += 1
                    
                    self._update_progress()
                    return True
                else:
                    self.failed_numbers += 1
                    return False
            else:
                self.failed_numbers += 1
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking number record {number_record.full_number}: {e}")
            self.failed_numbers += 1
            return False
    
    async def check_contact(self, contact: Contact) -> bool:
        """
        Check a contact and update database.
        
        Args:
            contact: Contact to check
            
        Returns:
            bool: True if check was successful, False otherwise
        """
        try:
            # Check number
            result = await self.check_single_number(contact.phone_number)
            
            if result is not None:
                # Update contact
                contact.is_valid = result
                contact.last_checked = datetime.now()
                
                # Update database
                success = self.database.update_contact(contact)
                
                if success:
                    self.checked_numbers += 1
                    if result:
                        self.valid_numbers += 1
                    else:
                        self.invalid_numbers += 1
                    
                    self._update_progress()
                    return True
                else:
                    self.failed_numbers += 1
                    return False
            else:
                self.failed_numbers += 1
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking contact {contact.phone_number}: {e}")
            self.failed_numbers += 1
            return False
    
    async def check_number_list(self, numbers: List[str]) -> Dict[str, Any]:
        """
        Check a list of phone numbers.
        
        Args:
            numbers: List of phone numbers to check
            
        Returns:
            Dict[str, Any]: Results summary
        """
        self.total_numbers = len(numbers)
        self.checked_numbers = 0
        self.valid_numbers = 0
        self.invalid_numbers = 0
        self.failed_numbers = 0
        
        self.logger.info(f"Starting to check {self.total_numbers} numbers")
        
        for i, phone_number in enumerate(numbers):
            try:
                result = await self.check_single_number(phone_number)
                
                if result is not None:
                    self.checked_numbers += 1
                    if result:
                        self.valid_numbers += 1
                    else:
                        self.invalid_numbers += 1
                else:
                    self.failed_numbers += 1
                
                self._update_progress()
                
                # Log progress every 10 numbers
                if (i + 1) % 10 == 0:
                    self.logger.info(
                        f"Progress: {i + 1}/{self.total_numbers} "
                        f"({((i + 1) / self.total_numbers * 100):.1f}%)"
                    )
                
            except Exception as e:
                self.logger.error(f"Error checking number {phone_number}: {e}")
                self.failed_numbers += 1
        
        # Call completion callback
        if self.completion_callback:
            self.completion_callback(self.get_results())
        
        return self.get_results()
    
    async def check_unchecked_numbers(
        self,
        country_code: str,
        operator_prefix: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Check unchecked numbers for a specific country and operator.
        
        Args:
            country_code: Country code to check
            operator_prefix: Operator prefix to check
            limit: Maximum number of numbers to check
            
        Returns:
            Dict[str, Any]: Results summary
        """
        # Get unchecked numbers from database
        unchecked_numbers = self.database.get_unchecked_numbers(
            country_code, operator_prefix, limit
        )
        
        self.total_numbers = len(unchecked_numbers)
        self.checked_numbers = 0
        self.valid_numbers = 0
        self.invalid_numbers = 0
        self.failed_numbers = 0
        
        self.logger.info(
            f"Starting to check {self.total_numbers} unchecked numbers "
            f"for {country_code} {operator_prefix}"
        )
        
        for i, number_record in enumerate(unchecked_numbers):
            success = await self.check_number_record(number_record)
            
            if not success:
                self.failed_numbers += 1
            
            # Log progress every 10 numbers
            if (i + 1) % 10 == 0:
                self.logger.info(
                    f"Progress: {i + 1}/{self.total_numbers} "
                    f"({((i + 1) / self.total_numbers * 100):.1f}%)"
                )
        
        # Call completion callback
        if self.completion_callback:
            self.completion_callback(self.get_results())
        
        return self.get_results()
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get current results summary.
        
        Returns:
            Dict[str, Any]: Results summary
        """
        return {
            'total_numbers': self.total_numbers,
            'checked_numbers': self.checked_numbers,
            'valid_numbers': self.valid_numbers,
            'invalid_numbers': self.invalid_numbers,
            'failed_numbers': self.failed_numbers,
            'success_rate': (
                (self.checked_numbers / self.total_numbers * 100)
                if self.total_numbers > 0 else 0
            ),
            'valid_rate': (
                (self.valid_numbers / self.checked_numbers * 100)
                if self.checked_numbers > 0 else 0
            ),
            'anti_robot_stats': self.anti_robot_driver.get_statistics()
        }
    
    def reset(self) -> None:
        """Reset the checker state."""
        self.total_numbers = 0
        self.checked_numbers = 0
        self.valid_numbers = 0
        self.invalid_numbers = 0
        self.failed_numbers = 0
        self.anti_robot_driver.reset()
        self.logger.info("Number checker reset") 