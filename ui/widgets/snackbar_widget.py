"""
Snackbar Widget for Flet applications.

This module provides a robust snackbar notification system using Flet's built-in SnackBar.
"""

import flet as ft
from typing import Optional
from enum import Enum
import logging


class SnackbarType(Enum):
    """Snackbar notification types."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SnackbarManager:
    """
    Robust snackbar manager for handling notifications.
    
    Features:
    - Reliable snackbar notifications
    - Multiple types (success, error, warning, info)
    - Auto-dismiss with configurable duration
    - Action button support
    - Error handling and fallback
    """
    
    def __init__(self, page: ft.Page):
        """
        Initialize the snackbar manager.
        
        Args:
            page: Flet page instance
        """
        self.page = page
        self.logger = logging.getLogger("snackbar_manager")
        self._active_snackbar = None
    
    def show_snackbar(
        self,
        message: str,
        snackbar_type: SnackbarType = SnackbarType.INFO,
        duration: int = 3000,
        action_text: str = "Tamam"
    ):
        """
        Show a snackbar notification.
        
        Args:
            message: Snackbar message
            snackbar_type: Type of snackbar
            duration: Duration in milliseconds
            action_text: Action button text
        """
        try:
            # Get colors based on type
            colors = self._get_colors(snackbar_type)
            
            # Create snackbar
            snackbar = ft.SnackBar(
                content=ft.Text(
                    message,
                    color=colors['text'],
                    size=14,
                    weight=ft.FontWeight.W_500
                ),
                action=ft.TextButton(
                    action_text,
                    on_click=self._on_action_click,
                    style=ft.ButtonStyle(
                        color=colors['action']
                    )
                ),
                duration=duration,
                bgcolor=colors['background'],
                show_close_icon=True,
                close_icon_color=colors['text']
            )
            
            # Store active snackbar
            self._active_snackbar = snackbar
            
            # Show snackbar using the correct Flet API
            self.page.snack_bar = snackbar
            self.page.update()
            
            self.logger.debug(f"Snackbar shown: {snackbar_type.value} - {message}")
            
        except Exception as e:
            # Fallback - just print the message
            self.logger.error(f"Snackbar error: {e}")
            print(f"[{snackbar_type.value.upper()}] {message}")
    
    def _get_colors(self, snackbar_type: SnackbarType) -> dict:
        """Get colors based on snackbar type."""
        if snackbar_type == SnackbarType.SUCCESS:
            return {
                'background': '#22c55e',  # Green
                'text': '#ffffff',
                'action': '#ffffff'
            }
        elif snackbar_type == SnackbarType.ERROR:
            return {
                'background': '#ef4444',  # Red
                'text': '#ffffff',
                'action': '#ffffff'
            }
        elif snackbar_type == SnackbarType.WARNING:
            return {
                'background': '#f97316',  # Orange
                'text': '#ffffff',
                'action': '#ffffff'
            }
        else:  # INFO
            return {
                'background': '#3b82f6',  # Blue
                'text': '#ffffff',
                'action': '#ffffff'
            }
    
    def _on_action_click(self, e):
        """Handle action button click."""
        # Clear the snackbar
        self.clear_snackbar()
    
    def clear_snackbar(self):
        """Clear the current snackbar."""
        try:
            if self.page and self._active_snackbar:
                self.page.snack_bar = None
                self.page.update()
                self._active_snackbar = None
        except Exception as e:
            self.logger.error(f"Error clearing snackbar: {e}")
    
    def show_success(self, message: str, duration: int = 3000):
        """Show success snackbar."""
        self.show_snackbar(message, SnackbarType.SUCCESS, duration)
    
    def show_error(self, message: str, duration: int = 4000):
        """Show error snackbar."""
        self.show_snackbar(message, SnackbarType.ERROR, duration)
    
    def show_warning(self, message: str, duration: int = 3500):
        """Show warning snackbar."""
        self.show_snackbar(message, SnackbarType.WARNING, duration)
    
    def show_info(self, message: str, duration: int = 3000):
        """Show info snackbar."""
        self.show_snackbar(message, SnackbarType.INFO, duration) 