"""
Global Exception Handler and Snackbar System.

This module provides:
- Global exception handling
- Error logging and reporting
- Snackbar notifications
- Error statistics and monitoring
"""

import logging
import traceback
from datetime import datetime
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
import flet as ft
from enum import Enum


class SnackbarType(Enum):
    """Snackbar notification types."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SnackbarConfig:
    """Snackbar configuration."""
    duration: int = 3000  # milliseconds
    position: str = "bottom"  # top, bottom, center
    dismissible: bool = True
    show_progress: bool = True


class GlobalExceptionHandler:
    """
    Global exception handler with snackbar notifications.
    
    Features:
    - Global exception catching
    - Error logging to file
    - Snackbar notifications
    - Error statistics and monitoring
    """
    
    def __init__(self, page: Optional[ft.Page] = None):
        """
        Initialize the global exception handler.
        
        Args:
            page: Flet page instance for showing snackbars
        """
        self.page = page
        self.snackbar_callback: Optional[Callable] = None
        self.error_count = 0
        self.error_history: List[Dict[str, Any]] = []
        
        # Snackbar configuration
        self.snackbar_config = SnackbarConfig()
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup error logging to file."""
        self.logger = logging.getLogger("exception_handler")
        
        # Create file handler
        file_handler = logging.FileHandler(
            'logs/errors.log',
            encoding='utf-8',
            mode='a'
        )
        
        # Configure formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.ERROR)
    
    def set_page(self, page: ft.Page) -> None:
        """Set the Flet page for showing snackbars."""
        self.page = page
    
    def set_snackbar_callback(self, callback: Callable) -> None:
        """Set the snackbar callback function."""
        self.snackbar_callback = callback
    
    def handle_exception(self, exception: Exception, context: str = "") -> None:
        """
        Handle an exception globally.
        
        Args:
            exception: The exception to handle
            context: Context where the exception occurred
        """
        try:
            # Increment error count
            self.error_count += 1
            
            # Get error details
            error_type = type(exception).__name__
            error_message = str(exception)
            stack_trace = traceback.format_exc()
            
            # Log the error
            self.logger.error(
                f"Error in {context}: {error_type}: {error_message}\n{stack_trace}"
            )
            
            # Add to error history
            error_record = {
                'timestamp': datetime.now(),
                'type': error_type,
                'message': error_message,
                'context': context,
                'stack_trace': stack_trace
            }
            self.error_history.append(error_record)
            
            # Keep only last 100 errors
            if len(self.error_history) > 100:
                self.error_history = self.error_history[-100:]
            
            # Show user-friendly error message
            self._show_error_snackbar(error_type, error_message, context)
            
        except Exception as e:
            # Fallback error handling
            print(f"Error in exception handler: {e}")
    
    def _show_error_snackbar(self, error_type: str, error_message: str, context: str) -> None:
        """Show error snackbar to user."""
        # Map error types to user-friendly messages
        user_messages = {
            'ConnectionError': 'Bağlantı hatası oluştu. Lütfen internet bağlantınızı kontrol edin.',
            'TimeoutError': 'İşlem zaman aşımına uğradı. Lütfen tekrar deneyin.',
            'FileNotFoundError': 'Dosya bulunamadı. Lütfen dosya yolunu kontrol edin.',
            'PermissionError': 'Dosya erişim izni yok. Lütfen dosya izinlerini kontrol edin.',
            'ValueError': 'Geçersiz değer girildi. Lütfen girdiğiniz değerleri kontrol edin.',
            'KeyError': 'Gerekli bilgi eksik. Lütfen tüm alanları doldurun.',
            'IndexError': 'Liste indeksi hatası. Lütfen seçiminizi kontrol edin.',
            'FloodWaitError': 'Telegram API limiti aşıldı. Lütfen biraz bekleyin.',
            'PhoneNumberInvalidError': 'Geçersiz telefon numarası formatı.',
            'SessionPasswordNeededError': 'İki faktörlü doğrulama gerekli.',
            'ApiIdInvalidError': 'Geçersiz API kimlik bilgileri.',
            'AuthKeyUnregisteredError': 'Oturum süresi dolmuş. Lütfen tekrar giriş yapın.',
        }
        
        # Get user-friendly message
        if error_type in user_messages:
            message = user_messages[error_type]
        else:
            message = f"Beklenmeyen bir hata oluştu: {error_message}"
        
        # Show snackbar
        self.show_snackbar(
            message=message,
            snackbar_type=SnackbarType.ERROR,
            title="Hata"
        )
    
    def show_snackbar(
        self,
        message: str,
        snackbar_type: SnackbarType = SnackbarType.INFO,
        title: str = "",
        duration: Optional[int] = None
    ) -> None:
        """
        Show a snackbar notification.
        
        Args:
            message: Snackbar message
            snackbar_type: Type of snackbar (success, error, warning, info)
            title: Snackbar title (optional)
            duration: Duration in milliseconds (optional)
        """
        if self.snackbar_callback:
            self.snackbar_callback(message, snackbar_type, title, duration or self.snackbar_config.duration)
        elif self.page:
            # Fallback to simple snackbar
            snackbar = ft.SnackBar(
                content=ft.Text(message),
                action="Tamam",
                duration=duration or self.snackbar_config.duration
            )
            self.page.snack_bar = snackbar
            self.page.update()
    
    def show_success(self, message: str, title: str = "Başarılı") -> None:
        """Show success snackbar."""
        self.show_snackbar(message, SnackbarType.SUCCESS, title)
    
    def show_error(self, message: str, title: str = "Hata") -> None:
        """Show error snackbar."""
        self.show_snackbar(message, SnackbarType.ERROR, title)
    
    def show_warning(self, message: str, title: str = "Uyarı") -> None:
        """Show warning snackbar."""
        self.show_snackbar(message, SnackbarType.WARNING, title)
    
    def show_info(self, message: str, title: str = "Bilgi") -> None:
        """Show info snackbar."""
        self.show_snackbar(message, SnackbarType.INFO, title)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics."""
        return {
            'total_errors': self.error_count,
            'recent_errors': len(self.error_history),
            'last_error': self.error_history[-1] if self.error_history else None,
            'error_types': self._get_error_type_counts()
        }
    
    def _get_error_type_counts(self) -> Dict[str, int]:
        """Get count of each error type."""
        counts = {}
        for error in self.error_history:
            error_type = error['type']
            counts[error_type] = counts.get(error_type, 0) + 1
        return counts
    
    def clear_error_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.error_count = 0


# Global instance
exception_handler = GlobalExceptionHandler()


def handle_exception(func: Callable) -> Callable:
    """
    Decorator to handle exceptions in functions.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with exception handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            exception_handler.handle_exception(e, f"{func.__module__}.{func.__name__}")
            raise
    return wrapper


def async_handle_exception(func: Callable) -> Callable:
    """
    Decorator to handle exceptions in async functions.
    
    Args:
        func: Async function to wrap
        
    Returns:
        Wrapped async function with exception handling
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            exception_handler.handle_exception(e, f"{func.__module__}.{func.__name__}")
            raise
    return wrapper 