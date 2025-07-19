"""
Data models for Telegram Analyzer Tool.

This module contains all data models used throughout the application.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Contact:
    """
    Contact model for storing contact information.
    
    Attributes:
        id: Unique identifier for the contact
        name: Contact name
        phone_number: Phone number in international format
        is_valid: Whether the number is valid in Telegram
        last_checked: Last time the number was checked
        notes: Additional notes about the contact
        created_at: When the contact was created
        updated_at: When the contact was last updated
    """
    id: Optional[int] = None
    name: str = ""
    phone_number: str = ""
    is_valid: Optional[bool] = None
    last_checked: Optional[datetime] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Update the updated_at timestamp when the object is modified."""
        if self.id is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the contact to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'is_valid': self.is_valid,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact':
        """Create a contact from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            phone_number=data.get('phone_number', ''),
            is_valid=data.get('is_valid'),
            last_checked=datetime.fromisoformat(data['last_checked']) if data.get('last_checked') else None,
            notes=data.get('notes', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        )


@dataclass
class NumberRecord:
    """
    Number record model for storing phone number information.
    
    Attributes:
        id: Unique identifier for the number record
        country_code: Country code (e.g., +90, +1, +44)
        operator_prefix: Operator prefix (e.g., 555, 542, 501)
        phone_number: Phone number without country code and operator prefix
        full_number: Complete phone number with country code
        is_valid: Whether the number is valid in Telegram
        is_checked: Whether the number has been checked
        check_date: When the number was last checked
        check_count: How many times the number has been checked
        notes: Additional notes about the number
        created_at: When the record was created
        updated_at: When the record was last updated
    """
    id: Optional[int] = None
    country_code: str = ""
    operator_prefix: str = ""
    phone_number: str = ""
    full_number: str = ""
    is_valid: Optional[bool] = None
    is_checked: bool = False
    check_date: Optional[datetime] = None
    check_count: int = 0
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Update the updated_at timestamp and generate full_number if not provided."""
        if self.id is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Generate full_number if not provided
        if not self.full_number and self.country_code and self.operator_prefix and self.phone_number:
            self.full_number = f"{self.country_code}{self.operator_prefix}{self.phone_number}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the number record to a dictionary."""
        return {
            'id': self.id,
            'country_code': self.country_code,
            'operator_prefix': self.operator_prefix,
            'phone_number': self.phone_number,
            'full_number': self.full_number,
            'is_valid': self.is_valid,
            'is_checked': self.is_checked,
            'check_date': self.check_date.isoformat() if self.check_date else None,
            'check_count': self.check_count,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NumberRecord':
        """Create a number record from a dictionary."""
        return cls(
            id=data.get('id'),
            country_code=data.get('country_code', ''),
            operator_prefix=data.get('operator_prefix', ''),
            phone_number=data.get('phone_number', ''),
            full_number=data.get('full_number', ''),
            is_valid=data.get('is_valid'),
            is_checked=data.get('is_checked', False),
            check_date=datetime.fromisoformat(data['check_date']) if data.get('check_date') else None,
            check_count=data.get('check_count', 0),
            notes=data.get('notes', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        )


@dataclass
class CheckSession:
    """
    Check session model for tracking number checking sessions.
    
    Attributes:
        id: Unique identifier for the session
        session_name: Name of the session
        country_code: Country code being checked
        operator_prefixes: List of operator prefixes being checked
        total_numbers: Total number of numbers to check
        checked_numbers: Number of numbers already checked
        valid_numbers: Number of valid numbers found
        invalid_numbers: Number of invalid numbers found
        start_time: When the session started
        end_time: When the session ended
        status: Status of the session (running, completed, paused, error)
        created_at: When the session was created
        updated_at: When the session was last updated
    """
    id: Optional[int] = None
    session_name: str = ""
    country_code: str = ""
    operator_prefixes: List[str] = field(default_factory=list)
    total_numbers: int = 0
    checked_numbers: int = 0
    valid_numbers: int = 0
    invalid_numbers: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "created"  # created, running, completed, paused, error
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Update the updated_at timestamp when the object is modified."""
        if self.id is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

    @property
    def progress_percentage(self) -> float:
        """Calculate the progress percentage."""
        if self.total_numbers == 0:
            return 0.0
        return (self.checked_numbers / self.total_numbers) * 100

    @property
    def is_completed(self) -> bool:
        """Check if the session is completed."""
        return self.status == "completed"

    @property
    def is_running(self) -> bool:
        """Check if the session is running."""
        return self.status == "running"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the check session to a dictionary."""
        return {
            'id': self.id,
            'session_name': self.session_name,
            'country_code': self.country_code,
            'operator_prefixes': self.operator_prefixes,
            'total_numbers': self.total_numbers,
            'checked_numbers': self.checked_numbers,
            'valid_numbers': self.valid_numbers,
            'invalid_numbers': self.invalid_numbers,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckSession':
        """Create a check session from a dictionary."""
        return cls(
            id=data.get('id'),
            session_name=data.get('session_name', ''),
            country_code=data.get('country_code', ''),
            operator_prefixes=data.get('operator_prefixes', []),
            total_numbers=data.get('total_numbers', 0),
            checked_numbers=data.get('checked_numbers', 0),
            valid_numbers=data.get('valid_numbers', 0),
            invalid_numbers=data.get('invalid_numbers', 0),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            status=data.get('status', 'created'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        )


# Constants for country operators
TURKEY_OPERATORS = {
    "Turkcell": ["501", "502", "503", "504", "505", "506", "507", "508", "509", "530", "531", "532", "533", "534", "535", "536", "537", "538", "539", "561"],
    "Vodafone": ["542", "543", "544", "545", "546", "547", "548", "549", "552", "553", "554", "555", "556", "557", "558", "559"],
    "Türk Telekom": ["501", "502", "503", "504", "505", "506", "507", "508", "509", "530", "531", "532", "533", "534", "535", "536", "537", "538", "539"],
    "Diğer": ["540", "541", "550", "551", "560", "562", "563", "564", "565", "566", "567", "568", "569"]
}

USA_OPERATORS = {
    "Verizon": ["201", "202", "203", "204", "205"],
    "AT&T": ["206", "207", "208", "209", "210"],
    "T-Mobile": ["211", "212", "213", "214", "215"]
}

UK_OPERATORS = {
    "Vodafone": ["7700", "7701", "7702", "7703"],
    "O2": ["7704", "7705", "7706", "7707"],
    "EE": ["7708", "7709", "7710", "7711"]
}

# Global operator mapping
COUNTRY_OPERATORS = {
    "+90": TURKEY_OPERATORS,
    "+1": USA_OPERATORS,
    "+44": UK_OPERATORS
} 