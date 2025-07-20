from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


@dataclass
class PhoneNumber:
    """
    Model representing a Turkish phone number with validation and display capabilities.
    
    Attributes:
        number: The phone number in +90 5XX XXX XX XX format
        name: Optional name associated with the phone number
        is_valid: Whether the number is valid/registered on Telegram
        checked_date: When the number was last checked
        operator_code: Turkish operator code (50X, 51X, 52X, 53X, 54X, 55X, 559)
    """
    number: str
    name: Optional[str] = None
    is_valid: Optional[bool] = None
    checked_date: Optional[datetime] = None
    operator_code: str = ""
    
    def __post_init__(self):
        """Extract operator code from number after initialization."""
        if self.number and not self.operator_code:
            self.operator_code = self._extract_operator_code()
    
    def validate_format(self) -> bool:
        """
        Validate Turkish phone number format.
        
        Expected format: +90 5XX XXX XX XX where:
        - Starts with +90
        - Second part starts with 5
        - Valid operator codes: 50X, 51X, 52X, 53X, 54X, 55X, 559
        - Total length: 13 digits after +90
        
        Returns:
            bool: True if format is valid, False otherwise
        """
        if not self.number:
            return False
            
        # Remove spaces and normalize
        normalized = self.number.replace(" ", "").replace("-", "")
        
        # Check basic format: +90 followed by 10 digits starting with 5
        pattern = r'^\+905\d{9}$'
        if not re.match(pattern, normalized):
            return False
            
        # Extract the operator part (5XX)
        operator_part = normalized[3:6]  # Skip +90, get 5XX
        
        # Valid Turkish operator codes
        valid_operators = [
            '500', '501', '502', '503', '504', '505', '506', '507', '508', '509',
            '510', '511', '512', '513', '514', '515', '516', '517', '518', '519',
            '520', '521', '522', '523', '524', '525', '526', '527', '528', '529',
            '530', '531', '532', '533', '534', '535', '536', '537', '538', '539',
            '540', '541', '542', '543', '544', '545', '546', '547', '548', '549',
            '550', '551', '552', '553', '554', '555', '556', '557', '558', '559'
        ]
        
        return operator_part in valid_operators
    
    def get_display_format(self) -> str:
        """
        Get formatted phone number for UI display.
        
        Converts +905XXXXXXXXX to +90 5XX XXX XX XX format
        
        Returns:
            str: Formatted phone number for display
        """
        if not self.number:
            return ""
            
        # Remove existing formatting
        normalized = self.number.replace(" ", "").replace("-", "")
        
        # Check if it's a valid Turkish number format
        if len(normalized) == 13 and normalized.startswith('+905'):
            # Format as +90 5XX XXX XX XX
            return f"{normalized[:3]} {normalized[3:6]} {normalized[6:9]} {normalized[9:11]} {normalized[11:13]}"
        
        # Return as-is if not in expected format
        return self.number
    
    def _extract_operator_code(self) -> str:
        """
        Extract operator code from phone number.
        
        Returns:
            str: Three-digit operator code (e.g., '532', '555')
        """
        if not self.number:
            return ""
            
        normalized = self.number.replace(" ", "").replace("-", "")
        
        if len(normalized) >= 6 and normalized.startswith('+905'):
            return normalized[3:6]  # Extract 5XX part
            
        return ""
    
    def is_checked(self) -> bool:
        """
        Check if this phone number has been validated.
        
        Returns:
            bool: True if number has been checked (has checked_date and is_valid is not None)
        """
        return self.checked_date is not None and self.is_valid is not None
    
    def get_status_text(self) -> str:
        """
        Get human-readable status text.
        
        Returns:
            str: Status description for UI display
        """
        if not self.is_checked():
            return "Not checked"
        elif self.is_valid:
            return "Valid (Telegram registered)"
        else:
            return "Invalid (Not registered)"