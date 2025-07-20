import random
import re
from typing import List
import logging


class PhoneGeneratorService:
    """
    Service for generating and validating Turkish phone numbers.
    
    This service generates random Turkish phone numbers using valid operator codes
    and provides validation for Turkish phone number format.
    """
    
    # Turkish mobile operator codes
    # Note: 559 is listed separately from 55X, meaning 55X should expand to 550-558, not 550-559
    TURKISH_OPERATORS = ['50X', '51X', '52X', '53X', '54X', '55X', '559']
    
    def __init__(self):
        """Initialize the phone generator service."""
        self.logger = logging.getLogger(__name__)
        
        # Expand operator codes to actual numeric ranges
        self._expanded_operators = self._expand_operator_codes()
        
    def _expand_operator_codes(self) -> List[str]:
        """
        Expand operator codes like '50X' to actual numeric codes like ['500', '501', ..., '509'].
        Special handling for '559' which is listed separately from '55X'.
        
        Returns:
            List of all valid 3-digit operator codes
        """
        expanded = []
        
        for operator in self.TURKISH_OPERATORS:
            if operator == '559':
                # Special case for 559 - add it directly
                expanded.append('559')
            elif operator.endswith('X'):
                base = operator[:-1]  # Remove 'X'
                if base == '55':
                    # Special handling for 55X: expand to 550-558 (not 559, as it's listed separately)
                    for digit in range(9):  # 0-8, not 0-9
                        expanded.append(f"{base}{digit}")
                else:
                    # Regular expansion for other operator codes: 50X -> 500-509, etc.
                    for digit in range(10):
                        expanded.append(f"{base}{digit}")
                    
        return expanded
    
    def generate_random_number(self) -> str:
        """
        Generate a single random Turkish phone number.
        
        Returns:
            A random Turkish phone number in format +90 5XX XXX XX XX
        """
        try:
            # Select random operator code
            operator_code = random.choice(self._expanded_operators)
            
            # Generate remaining 7 digits (XXX XX XX)
            remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(7)])
            
            # Format as +90 5XX XXX XX XX
            formatted_number = f"+90 {operator_code} {remaining_digits[:3]} {remaining_digits[3:5]} {remaining_digits[5:7]}"
            
            self.logger.debug(f"Generated phone number: {formatted_number}")
            return formatted_number
            
        except Exception as e:
            self.logger.error(f"Error generating random number: {e}")
            raise
    
    def generate_batch(self, count: int) -> List[str]:
        """
        Generate a batch of random Turkish phone numbers.
        
        Args:
            count: Number of phone numbers to generate
            
        Returns:
            List of random Turkish phone numbers
        """
        if count <= 0:
            raise ValueError("Count must be positive")
            
        try:
            numbers = []
            for _ in range(count):
                numbers.append(self.generate_random_number())
                
            self.logger.info(f"Generated batch of {count} phone numbers")
            return numbers
            
        except Exception as e:
            self.logger.error(f"Error generating batch of {count} numbers: {e}")
            raise
    
    def validate_turkish_format(self, number: str) -> bool:
        """
        Validate if a phone number follows Turkish mobile format.
        
        Args:
            number: Phone number to validate
            
        Returns:
            True if number is valid Turkish format, False otherwise
        """
        if not number:
            return False
            
        try:
            # Remove all spaces and normalize
            clean_number = number.replace(" ", "").replace("-", "")
            
            # Check if starts with +90
            if not clean_number.startswith("+90"):
                return False
                
            # Extract the mobile part (should be 10 digits after +90)
            mobile_part = clean_number[3:]  # Remove +90
            
            # Should be exactly 10 digits
            if len(mobile_part) != 10:
                return False
                
            # Should be all digits
            if not mobile_part.isdigit():
                return False
                
            # Should start with 5 (mobile numbers)
            if not mobile_part.startswith('5'):
                return False
                
            # Extract operator code (first 3 digits of mobile part)
            operator_code = mobile_part[:3]
            
            # Check if operator code is valid
            is_valid = operator_code in self._expanded_operators
            
            if is_valid:
                self.logger.debug(f"Valid Turkish number: {number}")
            else:
                self.logger.debug(f"Invalid operator code {operator_code} in number: {number}")
                
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Error validating number {number}: {e}")
            return False
    
    def get_operator_code(self, number: str) -> str:
        """
        Extract operator code from a Turkish phone number.
        
        Args:
            number: Phone number to extract operator code from
            
        Returns:
            3-digit operator code or empty string if invalid
        """
        if not self.validate_turkish_format(number):
            return ""
            
        try:
            clean_number = number.replace(" ", "").replace("-", "")
            mobile_part = clean_number[3:]  # Remove +90
            return mobile_part[:3]  # First 3 digits are operator code
            
        except Exception as e:
            self.logger.error(f"Error extracting operator code from {number}: {e}")
            return ""
    
    def get_supported_operators(self) -> List[str]:
        """
        Get list of all supported Turkish operator codes.
        
        Returns:
            List of supported 3-digit operator codes
        """
        return self._expanded_operators.copy()