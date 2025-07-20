"""
Turkish Phone Validator - Configuration Settings

Central configuration management for the application.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
EXPORTS_DIR = PROJECT_ROOT / "exports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # Database settings
    DATABASE_PATH: str = str(DATA_DIR / "turkish_phone_validator.db")
    
    # Telegram API settings (to be configured by user)
    TELEGRAM_API_ID: Optional[str] = None
    TELEGRAM_API_HASH: Optional[str] = None
    TELEGRAM_SESSION_NAME: str = "turkish_phone_validator_session"
    
    # Rate limiting settings
    RATE_LIMIT_MIN_SECONDS: int = 2
    RATE_LIMIT_MAX_SECONDS: int = 5
    DEFAULT_THREAD_COUNT: int = 2
    MAX_THREAD_COUNT: int = 5
    
    # UI settings
    WINDOW_TITLE: str = "Turkish Phone Validator"
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    THEME_MODE: str = "dark"  # "dark" or "light"
    
    # Export settings
    DEFAULT_EXPORT_PATH: str = str(EXPORTS_DIR)
    SUPPORTED_EXPORT_FORMATS: list = None
    
    # Turkish phone number settings
    TURKISH_COUNTRY_CODE: str = "+90"
    TURKISH_OPERATORS: list = None
    
    def __post_init__(self):
        """Initialize default values that require lists."""
        if self.SUPPORTED_EXPORT_FORMATS is None:
            self.SUPPORTED_EXPORT_FORMATS = ["csv", "excel", "json", "txt"]
        
        if self.TURKISH_OPERATORS is None:
            self.TURKISH_OPERATORS = [
                "50", "51", "52", "53", "54", "55", "559"
            ]

# Global configuration instance
config = AppConfig()

def load_config_from_env():
    """Load configuration from environment variables."""
    config.TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    config.TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    
    # Override other settings from environment if needed
    if os.getenv("RATE_LIMIT_MIN"):
        config.RATE_LIMIT_MIN_SECONDS = int(os.getenv("RATE_LIMIT_MIN"))
    
    if os.getenv("RATE_LIMIT_MAX"):
        config.RATE_LIMIT_MAX_SECONDS = int(os.getenv("RATE_LIMIT_MAX"))
    
    if os.getenv("DEFAULT_THREADS"):
        config.DEFAULT_THREAD_COUNT = int(os.getenv("DEFAULT_THREADS"))

# Load environment configuration on import
load_config_from_env()