from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os


@dataclass
class AppSettings:
    """
    Model representing application configuration settings.
    
    This class contains all configurable settings for the Turkish Phone Validator
    application, including Telegram API credentials, threading configuration,
    rate limiting settings, and UI preferences.
    
    Attributes:
        telegram_api_id: Telegram API ID for MTProto authentication
        telegram_api_hash: Telegram API Hash for MTProto authentication
        parallel_threads: Number of parallel validation threads (default: 2)
        rate_limit_min: Minimum delay between requests in seconds (default: 2)
        rate_limit_max: Maximum delay between requests in seconds (default: 5)
        dark_mode: Whether to use dark mode UI theme (default: True)
        export_path: Default path for exported files
        session_name: Name for Telegram session file (default: "validator_session")
        auto_save_results: Whether to automatically save validation results (default: True)
        max_retries: Maximum number of retry attempts for failed validations (default: 3)
        timeout_seconds: Request timeout in seconds (default: 30)
    """
    telegram_api_id: str = ""
    telegram_api_hash: str = ""
    parallel_threads: int = 2
    rate_limit_min: int = 2
    rate_limit_max: int = 5
    dark_mode: bool = True
    export_path: str = field(default_factory=lambda: os.path.expanduser("~/Downloads"))
    session_name: str = "validator_session"
    auto_save_results: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    
    def __post_init__(self):
        """Validate settings after initialization."""
        self._validate_settings()
    
    def _validate_settings(self) -> None:
        """
        Validate all settings and apply constraints.
        
        Raises:
            ValueError: If any setting is invalid
        """
        # Validate parallel threads (1-10 range, with warnings for high values)
        if self.parallel_threads < 1:
            self.parallel_threads = 1
        elif self.parallel_threads > 10:
            self.parallel_threads = 10
        
        # Validate rate limiting (must be positive, min <= max)
        if self.rate_limit_min < 1:
            self.rate_limit_min = 1
        if self.rate_limit_max < self.rate_limit_min:
            self.rate_limit_max = self.rate_limit_min + 1
        if self.rate_limit_max > 60:
            self.rate_limit_max = 60
        
        # Validate timeout
        if self.timeout_seconds < 5:
            self.timeout_seconds = 5
        elif self.timeout_seconds > 300:
            self.timeout_seconds = 300
        
        # Validate max retries
        if self.max_retries < 0:
            self.max_retries = 0
        elif self.max_retries > 10:
            self.max_retries = 10
        
        # Ensure export path exists or can be created
        if self.export_path and not os.path.exists(self.export_path):
            try:
                os.makedirs(self.export_path, exist_ok=True)
            except (OSError, PermissionError):
                # Fall back to user's home directory
                self.export_path = os.path.expanduser("~")
    
    def validate_telegram_credentials(self) -> bool:
        """
        Validate Telegram API credentials format.
        
        Returns:
            bool: True if credentials appear to be valid format, False otherwise
        """
        # API ID should be numeric and reasonable length
        if not self.telegram_api_id or not self.telegram_api_id.isdigit():
            return False
        
        api_id_int = int(self.telegram_api_id)
        if api_id_int < 1000 or api_id_int > 999999999:
            return False
        
        # API Hash should be 32 character hex string
        if not self.telegram_api_hash or len(self.telegram_api_hash) != 32:
            return False
        
        # Check if it's a valid hex string
        try:
            int(self.telegram_api_hash, 16)
        except ValueError:
            return False
        
        return True
    
    def get_risk_level(self) -> str:
        """
        Get risk level assessment based on current settings.
        
        Returns:
            str: Risk level ('Low', 'Medium', 'High', 'Very High')
        """
        risk_score = 0
        
        # Thread count risk
        if self.parallel_threads >= 8:
            risk_score += 3
        elif self.parallel_threads >= 5:
            risk_score += 2
        elif self.parallel_threads >= 3:
            risk_score += 1
        
        # Rate limiting risk
        avg_delay = (self.rate_limit_min + self.rate_limit_max) / 2
        if avg_delay < 2:
            risk_score += 3
        elif avg_delay < 3:
            risk_score += 2
        elif avg_delay < 4:
            risk_score += 1
        
        # Timeout risk
        if self.timeout_seconds < 10:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 6:
            return "Very High"
        elif risk_score >= 4:
            return "High"
        elif risk_score >= 2:
            return "Medium"
        else:
            return "Low"
    
    def get_risk_warnings(self) -> list[str]:
        """
        Get list of risk warnings based on current settings.
        
        Returns:
            list[str]: List of warning messages
        """
        warnings = []
        
        if self.parallel_threads >= 5:
            warnings.append(f"High thread count ({self.parallel_threads}) increases ban risk")
        
        avg_delay = (self.rate_limit_min + self.rate_limit_max) / 2
        if avg_delay < 3:
            warnings.append(f"Low average delay ({avg_delay:.1f}s) may trigger rate limits")
        
        if self.timeout_seconds < 15:
            warnings.append("Low timeout may cause unnecessary retries")
        
        if not self.validate_telegram_credentials():
            warnings.append("Invalid Telegram API credentials")
        
        return warnings
    
    def get_recommended_settings(self) -> 'AppSettings':
        """
        Get recommended safe settings for new users.
        
        Returns:
            AppSettings: New instance with recommended safe settings
        """
        return AppSettings(
            telegram_api_id=self.telegram_api_id,
            telegram_api_hash=self.telegram_api_hash,
            parallel_threads=2,
            rate_limit_min=3,
            rate_limit_max=6,
            dark_mode=True,
            export_path=self.export_path,
            session_name=self.session_name,
            auto_save_results=True,
            max_retries=2,
            timeout_seconds=30
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of settings
        """
        return {
            'telegram_api_id': self.telegram_api_id,
            'telegram_api_hash': self.telegram_api_hash,
            'parallel_threads': self.parallel_threads,
            'rate_limit_min': self.rate_limit_min,
            'rate_limit_max': self.rate_limit_max,
            'dark_mode': self.dark_mode,
            'export_path': self.export_path,
            'session_name': self.session_name,
            'auto_save_results': self.auto_save_results,
            'max_retries': self.max_retries,
            'timeout_seconds': self.timeout_seconds,
            'risk_level': self.get_risk_level()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """
        Create AppSettings instance from dictionary.
        
        Args:
            data: Dictionary containing settings data
            
        Returns:
            AppSettings: New instance created from dictionary data
        """
        # Filter out any keys that aren't valid AppSettings fields
        valid_fields = {
            'telegram_api_id', 'telegram_api_hash', 'parallel_threads',
            'rate_limit_min', 'rate_limit_max', 'dark_mode', 'export_path',
            'session_name', 'auto_save_results', 'max_retries', 'timeout_seconds'
        }
        
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def copy(self) -> 'AppSettings':
        """
        Create a copy of the current settings.
        
        Returns:
            AppSettings: New instance with same values
        """
        return AppSettings(
            telegram_api_id=self.telegram_api_id,
            telegram_api_hash=self.telegram_api_hash,
            parallel_threads=self.parallel_threads,
            rate_limit_min=self.rate_limit_min,
            rate_limit_max=self.rate_limit_max,
            dark_mode=self.dark_mode,
            export_path=self.export_path,
            session_name=self.session_name,
            auto_save_results=self.auto_save_results,
            max_retries=self.max_retries,
            timeout_seconds=self.timeout_seconds
        )