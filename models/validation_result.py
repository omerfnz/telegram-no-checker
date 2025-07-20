from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from models.phone_number import PhoneNumber


@dataclass
class ValidationResult:
    """
    Model representing the result of a phone number validation against Telegram.
    
    This class contains all metadata about a validation attempt, including
    the phone number that was validated, the result, timing information,
    and any errors that occurred during validation.
    
    Attributes:
        phone_number: The PhoneNumber object that was validated
        is_telegram_registered: Whether the number is registered on Telegram
        validation_date: When the validation was performed
        response_time: How long the validation took in seconds
        error_message: Any error message if validation failed
    """
    phone_number: PhoneNumber
    is_telegram_registered: bool
    validation_date: datetime
    response_time: float
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Update the phone number's validation status after creation."""
        if self.phone_number and self.error_message is None:
            # Only update if validation was successful (no error)
            self.phone_number.is_valid = self.is_telegram_registered
            self.phone_number.checked_date = self.validation_date
    
    def is_successful(self) -> bool:
        """
        Check if the validation was successful (no errors occurred).
        
        Returns:
            bool: True if validation completed without errors, False otherwise
        """
        return self.error_message is None
    
    def get_result_summary(self) -> str:
        """
        Get a human-readable summary of the validation result.
        
        Returns:
            str: Summary text describing the validation result
        """
        if not self.is_successful():
            return f"Validation failed: {self.error_message}"
        
        status = "registered" if self.is_telegram_registered else "not registered"
        return f"Number is {status} on Telegram (validated in {self.response_time:.2f}s)"
    
    def get_performance_category(self) -> str:
        """
        Categorize the validation performance based on response time.
        
        Returns:
            str: Performance category ('Fast', 'Normal', 'Slow', 'Very Slow')
        """
        if self.response_time < 1.0:
            return "Fast"
        elif self.response_time < 3.0:
            return "Normal"
        elif self.response_time < 10.0:
            return "Slow"
        else:
            return "Very Slow"
    
    def to_dict(self) -> dict:
        """
        Convert ValidationResult to dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the validation result
        """
        return {
            'phone_number': self.phone_number.number,
            'name': self.phone_number.name,
            'is_telegram_registered': self.is_telegram_registered,
            'validation_date': self.validation_date.isoformat(),
            'response_time': self.response_time,
            'error_message': self.error_message,
            'operator_code': self.phone_number.operator_code,
            'performance_category': self.get_performance_category()
        }
    
    @classmethod
    def create_error_result(cls, phone_number: PhoneNumber, error_message: str, 
                          response_time: float = 0.0) -> 'ValidationResult':
        """
        Create a ValidationResult for a failed validation attempt.
        
        Args:
            phone_number: The phone number that failed validation
            error_message: Description of the error that occurred
            response_time: Time taken before the error occurred
            
        Returns:
            ValidationResult: A result object representing the failed validation
        """
        return cls(
            phone_number=phone_number,
            is_telegram_registered=False,
            validation_date=datetime.now(),
            response_time=response_time,
            error_message=error_message
        )
    
    @classmethod
    def create_success_result(cls, phone_number: PhoneNumber, is_registered: bool, 
                            response_time: float) -> 'ValidationResult':
        """
        Create a ValidationResult for a successful validation attempt.
        
        Args:
            phone_number: The phone number that was validated
            is_registered: Whether the number is registered on Telegram
            response_time: Time taken to complete the validation
            
        Returns:
            ValidationResult: A result object representing the successful validation
        """
        return cls(
            phone_number=phone_number,
            is_telegram_registered=is_registered,
            validation_date=datetime.now(),
            response_time=response_time,
            error_message=None
        )