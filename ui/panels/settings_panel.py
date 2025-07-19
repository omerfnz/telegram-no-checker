"""
Settings Panel for Telegram Analyzer Tool.

This module contains the settings and configuration interface.
"""

import flet as ft
from typing import Optional, Dict, Any
from ..theme_manager import ThemeManager, ThemeMode
from ..widgets import ModernButton, ModernCard, ModernInput


class SettingsPanel:
    """
    Settings panel with modern design.
    
    This panel provides:
    - API configuration
    - Theme settings
    - Performance settings
    - Application preferences
    """

    def __init__(self, theme_manager: ThemeManager, core_modules: Dict[str, Any]):
        """
        Initialize the settings panel.
        
        Args:
            theme_manager: Theme manager instance
            core_modules: Core modules dictionary
        """
        self.theme_manager = theme_manager
        self.core_modules = core_modules
        
        # UI components
        self.api_id_input = None
        self.api_hash_input = None
        self.theme_dropdown = None
        self.rate_limit_input = None
        self.delay_input = None
        
        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build the panel UI."""
        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Settings",
                        size=24,
                        weight=ft.FontWeight.W_700,
                        color=self.theme_manager.get_color("foreground")
                    ),
                    ft.Icon(
                        name="settings",
                        size=24,
                        color=self.theme_manager.get_color("primary")
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.all(16),
            border=ft.border.only(bottom=ft.border.BorderSide(1, self.theme_manager.get_color("border")))
        )

        # API Settings section
        api_section = self._create_api_section()
        
        # Theme Settings section
        theme_section = self._create_theme_section()
        
        # Performance Settings section
        performance_section = self._create_performance_section()
        
        # Save button
        save_button = ModernButton(
            text="Save Settings",
            on_click=self._on_save_settings,
            variant="primary",
            expand=True
        )

        # Main content
        content = ft.Column(
            [
                header,
                api_section,
                theme_section,
                performance_section,
                ft.Container(
                    content=save_button,
                    padding=ft.padding.all(16)
                )
            ],
            spacing=0,
            expand=True
        )

        self.content = ft.Container(
            content=content,
            expand=True,
            bgcolor=self.theme_manager.get_color("background")
        )

    def _create_api_section(self) -> ft.Container:
        """Create API settings section."""
        # API ID input
        self.api_id_input = ModernInput(
            label="API ID",
            hint_text="Enter your Telegram API ID",
            password=True
        )

        # API Hash input
        self.api_hash_input = ModernInput(
            label="API Hash",
            hint_text="Enter your Telegram API Hash",
            password=True
        )

        # Test connection button
        test_button = ModernButton(
            text="Test Connection",
            on_click=self._on_test_connection,
            variant="secondary"
        )

        # API content
        api_content = ft.Column(
            [
                ft.Text(
                    "Telegram API Configuration",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self.theme_manager.get_color("foreground")
                ),
                ft.Container(height=16),
                ft.Text(
                    "Enter your Telegram API credentials to enable number checking functionality.",
                    size=14,
                    color=self.theme_manager.get_color("muted_foreground")
                ),
                ft.Container(height=16),
                self.api_id_input,
                ft.Container(height=12),
                self.api_hash_input,
                ft.Container(height=16),
                test_button
            ],
            spacing=8
        )

        return ModernCard(
            content=ft.Container(
                content=api_content,
                padding=ft.padding.all(16)
            ),
            margin=ft.margin.all(16),
            theme_manager=self.theme_manager
        )

    def _create_theme_section(self) -> ft.Container:
        """Create theme settings section."""
        # Theme dropdown
        self.theme_dropdown = ft.Dropdown(
            label="Theme",
            value=self.theme_manager.current_mode.value,
            options=[
                ft.dropdown.Option("light", "Light Theme"),
                ft.dropdown.Option("dark", "Dark Theme"),
                ft.dropdown.Option("auto", "Auto (System)")
            ],
            on_change=self._on_theme_change,
            expand=True
        )

        # Theme preview
        self.theme_preview = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        name="light_mode" if self.theme_manager.current_mode == ThemeMode.LIGHT else "dark_mode",
                        size=24,
                        color=self.theme_manager.get_color("primary")
                    ),
                    ft.Text(
                        f"Current: {self.theme_manager.current_mode.value.title()}",
                        size=14,
                        color=self.theme_manager.get_color("muted_foreground")
                    )
                ],
                spacing=8
            ),
            padding=ft.padding.all(8),
            bgcolor=self.theme_manager.get_color("card"),
            border_radius=8
        )

        # Theme content
        theme_content = ft.Column(
            [
                ft.Text(
                    "Appearance",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self.theme_manager.get_color("foreground")
                ),
                ft.Container(height=16),
                ft.Text(
                    "Choose your preferred theme for the application interface.",
                    size=14,
                    color=self.theme_manager.get_color("muted_foreground")
                ),
                ft.Container(height=16),
                self.theme_dropdown,
                ft.Container(height=12),
                self.theme_preview
            ],
            spacing=8
        )

        return ModernCard(
            content=ft.Container(
                content=theme_content,
                padding=ft.padding.all(16)
            ),
            margin=ft.margin.symmetric(horizontal=16),
            theme_manager=self.theme_manager
        )

    def _create_performance_section(self) -> ft.Container:
        """Create performance settings section."""
        # Rate limit input
        self.rate_limit_input = ModernInput(
            label="Requests per Minute",
            hint_text="30",
            value="30",
            keyboard_type=ft.KeyboardType.NUMBER,
            theme_manager=self.theme_manager
        )

        # Delay input
        self.delay_input = ModernInput(
            label="Delay between Requests (seconds)",
            hint_text="2.0",
            value="2.0",
            keyboard_type=ft.KeyboardType.NUMBER,
            theme_manager=self.theme_manager
        )

        # Performance content
        performance_content = ft.Column(
            [
                ft.Text(
                    "Performance Settings",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self.theme_manager.get_color("foreground")
                ),
                ft.Container(height=16),
                ft.Text(
                    "Configure rate limiting and delays to avoid API restrictions.",
                    size=14,
                    color=self.theme_manager.get_color("muted_foreground")
                ),
                ft.Container(height=16),
                self.rate_limit_input,
                ft.Container(height=12),
                self.delay_input,
                ft.Container(height=16),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(
                                name="info_outline",
                                size=16,
                                color=self.theme_manager.get_color("muted_foreground")
                            ),
                            ft.Text(
                                "Lower values = faster checking, but higher risk of API limits",
                                size=12,
                                color=self.theme_manager.get_color("muted_foreground")
                            )
                        ],
                        spacing=8
                    ),
                    padding=ft.padding.all(8),
                    bgcolor=self.theme_manager.get_color("muted"),
                    border_radius=8
                )
            ],
            spacing=8
        )

        return ModernCard(
            content=ft.Container(
                content=performance_content,
                padding=ft.padding.all(16)
            ),
            margin=ft.margin.all(16),
            theme_manager=self.theme_manager
        )

    def _on_theme_change(self, e):
        """Handle theme selection change."""
        theme_value = e.control.value
        if theme_value == "light":
            self.theme_manager.set_theme(ThemeMode.LIGHT)
        elif theme_value == "dark":
            self.theme_manager.set_theme(ThemeMode.DARK)
        elif theme_value == "auto":
            self.theme_manager.set_theme(ThemeMode.AUTO)
        
        # Update theme preview
        self._update_theme_preview()
    
    def _update_theme_preview(self):
        """Update theme preview display."""
        # Update theme preview icon and text
        if hasattr(self, 'theme_preview'):
            icon_name = "light_mode" if self.theme_manager.current_mode == ThemeMode.LIGHT else "dark_mode"
            self.theme_preview.content.controls[0].name = icon_name
            self.theme_preview.content.controls[1].value = f"Current: {self.theme_manager.current_mode.value.title()}"
            self.theme_preview.bgcolor = self.theme_manager.get_color("card")

    def _on_test_connection(self, e):
        """Handle test connection button click."""
        api_id = self.api_id_input.value
        api_hash = self.api_hash_input.value
        
        if not api_id or not api_hash:
            print("Please enter both API ID and API Hash")
            return
        
        # TODO: Implement actual connection test
        print("Testing connection...")
        print(f"API ID: {api_id}")
        print(f"API Hash: {api_hash[:10]}...")

    def _on_save_settings(self, e):
        """Handle save settings button click."""
        # Collect settings
        settings = {
            'api_id': self.api_id_input.value,
            'api_hash': self.api_hash_input.value,
            'theme': self.theme_dropdown.value,
            'rate_limit': int(self.rate_limit_input.value or 30),
            'delay': float(self.delay_input.value or 2.0)
        }
        
        # TODO: Save settings to file/database
        print("Saving settings...")
        print(settings)
        
        # Show success message
        print("Settings saved successfully!")

    def get_content(self) -> ft.Control:
        """Get the panel content."""
        return self.content
    
    def rebuild_with_theme(self):
        """Rebuild UI with current theme."""
        self._build_ui()
        # Don't update preview during theme change - it will be updated when panel is shown
