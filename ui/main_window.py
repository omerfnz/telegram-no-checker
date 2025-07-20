"""
Main window for Telegram Analyzer Tool.

This module contains the main application window with modern, responsive design.
"""

import flet as ft
from typing import Optional
from .theme_manager import ThemeManager, ThemeMode
from .panels import (
    ContactPanel,
    NumberGeneratorPanel,
    NumberCheckerPanel,
    SettingsPanel
)
from .widgets import (
    ModernButton,
    StatusIndicator
)


class MainWindow:
    """
    Main application window with modern, responsive design.

    This class handles:
    - Responsive layout management
    - Theme switching
    - Navigation between panels
    - Sidebar and content area
    """

    def __init__(self, page: ft.Page, core_modules: dict = None, theme_manager: ThemeManager = None, snackbar_manager = None):
        """
        Initialize the main window.

        Args:
            page: Flet page instance
            core_modules: Core modules dictionary
            theme_manager: Theme manager instance
            snackbar_manager: Snackbar manager instance
        """
        self.page = page
        self.core_modules = core_modules or {}
        self.theme_manager = theme_manager or ThemeManager()
        self.snackbar_manager = snackbar_manager
        self.current_panel = "contacts"
        self.page_width = 1200
        self.page_height = 800

        # Initialize panels
        self.panels = {}
        self._setup_panels()

        # Setup page
        self._setup_page()

        # Setup layout
        self._setup_layout()

        # Apply initial theme
        self.theme_manager.apply_theme_to_page(self.page)

    def _setup_panels(self):
        """Initialize application panels."""
        self.panels = {
            "contacts": ContactPanel(self.theme_manager, self.core_modules, self.snackbar_manager),
            "generator": NumberGeneratorPanel(self.theme_manager, self.core_modules, self.snackbar_manager),
            "checker": NumberCheckerPanel(self.theme_manager, self.core_modules, self.snackbar_manager),
            "settings": SettingsPanel(self.theme_manager, self.core_modules, self.snackbar_manager)
        }
        
        # Set page reference for all panels
        for panel in self.panels.values():
            if hasattr(panel, 'set_page'):
                panel.set_page(self.page)
        
        # Add overlays to page
        self._add_overlays_to_page()

    def _setup_page(self):
        """Setup page properties."""
        self.page.title = "Telegram Analyzer Tool"
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        # self.page.window_maximized = True  # Bu özellik mevcut değil
        self.page.padding = 0
        self.page.spacing = 0
        self.page.on_resize = self._on_page_resize
        self.page.on_connect = self._on_page_connect
        self.page.on_disconnect = self._on_page_disconnect

    def _setup_layout(self):
        """Setup main layout."""
        # Sidebar
        self.sidebar = self._create_sidebar()

        # Content area
        self.content_area = self._create_content_area()

        # Main layout
        self.main_layout = ft.Row(
            [
                self.sidebar,
                ft.VerticalDivider(width=1),
                self.content_area
            ],
            expand=True
        )

        # Use main layout directly
        self.scrollable_layout = self.main_layout

        # Set page content
        self.page.add(self.scrollable_layout)

        # Show initial panel
        self._show_panel("contacts")

    def _create_sidebar(self) -> ft.Container:
        """Create modern sidebar."""
        # Sidebar destinations
        destinations = [
            ft.NavigationRailDestination(
                icon="contacts_outlined",
                selected_icon="contacts",
                label="Contacts"
            ),
            ft.NavigationRailDestination(
                icon="add_circle_outline",
                selected_icon="add_circle",
                label="Number Generator"
            ),
            ft.NavigationRailDestination(
                icon="search_outlined",
                selected_icon="search",
                label="Number Checker"
            ),
            ft.NavigationRailDestination(
                icon="settings_outlined",
                selected_icon="settings",
                label="Settings"
            )
        ]

        # Status indicator
        self.status_indicator = StatusIndicator(
            status="disconnected",
            on_click=self._on_status_click
        )

        # Theme toggle button
        self.theme_toggle = ModernButton(
            text="🌙" if self.theme_manager.current_mode == ThemeMode.LIGHT else "☀️",
            on_click=self._on_theme_toggle,
            variant="ghost",
            size="icon"
        )

        # Sidebar content
        sidebar_content = ft.Column(
            [
                # Header
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Telegram Analyzer",
                                size=18,
                                weight=ft.FontWeight.W_700,
                                color=self.theme_manager.get_color("foreground") or "#111827"
                            ),
                            ft.Text(
                                "Professional Tool",
                                size=12,
                                color=self.theme_manager.get_color("muted_foreground") or "#6b7280"
                            )
                        ],
                        spacing=4
                    ),
                    padding=ft.padding.all(16),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, self.theme_manager.get_color("border") or "#e5e7eb"))
                ),

                # Navigation
                ft.Container(
                    content=ft.NavigationRail(
                        selected_index=0,
                        label_type=ft.NavigationRailLabelType.ALL,
                        min_width=72,
                        min_extended_width=256,
                        group_alignment=ft.NavigationRailTheme(),
                        destinations=destinations,
                        on_change=self._on_navigation_change,
                        bgcolor=self.theme_manager.get_color("sidebar") or "#ffffff",
                        extended=True
                    ),
                    expand=True
                ),

                # Bottom section
                ft.Container(
                    content=ft.Column(
                        [
                            self.status_indicator,
                            self.theme_toggle
                        ],
                        spacing=8
                    ),
                    padding=ft.padding.all(16),
                    border=ft.border.only(top=ft.border.BorderSide(1, self.theme_manager.get_color("border") or "#e5e7eb"))
                )
            ],
            spacing=0
        )

        return ft.Container(
            content=sidebar_content,
            width=256,
            bgcolor=self.theme_manager.get_color("sidebar") or "#ffffff",
            border=ft.border.only(right=ft.border.BorderSide(1, self.theme_manager.get_color("sidebar-border") or "#e5e7eb"))
        )

    def _create_content_area(self) -> ft.Container:
        """Create content area."""
        # Header
        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Contacts",
                        size=24,
                        weight=ft.FontWeight.W_700,
                        color=self.theme_manager.get_color("foreground") or "#111827"
                    ),
                    ft.Container(width=0, expand=True),  # Spacer
                    ft.Text(
                        "Ready",
                        size=12,
                        color=self.theme_manager.get_color("muted_foreground") or "#6b7280"
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.all(24),
            border=ft.border.only(bottom=ft.border.BorderSide(1, self.theme_manager.get_color("border") or "#e5e7eb"))
        )

        # Content container
        self.content_container = ft.Container(
            content=ft.Text("Loading..."),
            padding=ft.padding.all(24),
            expand=True
        )

        # Content area
        content_area = ft.Column(
            [
                self.header,
                self.content_container
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

        return ft.Container(
            content=content_area,
            expand=True,
            bgcolor=self.theme_manager.get_color("background") or "#f9fafb"
        )

    def _on_navigation_change(self, e):
        """Handle navigation change."""
        panel_names = ["contacts", "generator", "checker", "settings"]
        selected_index = e.control.selected_index

        if 0 <= selected_index < len(panel_names):
            panel_name = panel_names[selected_index]
            self._show_panel(panel_name)

    def _show_panel(self, panel_name: str):
        """Show specified panel."""
        if panel_name not in self.panels:
            return

        # Update current panel
        self.current_panel = panel_name

        # Update header title
        panel_titles = {
            "contacts": "Contacts",
            "generator": "Number Generator",
            "checker": "Number Checker",
            "settings": "Settings"
        }

        self.header.content.controls[0].value = panel_titles.get(panel_name, "Unknown")

        # Update content
        panel = self.panels[panel_name]
        self.content_container.content = panel.get_content()

        # Update page
        self.page.update()

    def _on_page_resize(self, e):
        """Handle page resize."""
        self.page_width = e.width
        self.page_height = e.height

        # Update responsive layout
        self._update_responsive_layout()

    def _update_responsive_layout(self):
        """Update layout based on screen size."""
        if self.theme_manager.is_mobile(self.page_width):
            # Mobile layout
            self.sidebar.visible = False
            self.main_layout.controls = [self.content_area]
        elif self.theme_manager.is_tablet(self.page_width):
            # Tablet layout
            self.sidebar.visible = True
            self.sidebar.width = 200
            self.main_layout.controls = [
                self.sidebar,
                ft.VerticalDivider(width=1),
                self.content_area
            ]
        else:
            # Desktop layout
            self.sidebar.visible = True
            self.sidebar.width = 256
            self.main_layout.controls = [
                self.sidebar,
                ft.VerticalDivider(width=1),
                self.content_area
            ]

        self.page.update()

    def _on_theme_toggle(self, e):
        """Handle theme toggle."""
        if self.theme_manager.current_mode == ThemeMode.LIGHT:
            self.theme_manager.set_theme_mode(ThemeMode.DARK)
            self.theme_toggle.text = "☀️"
        else:
            self.theme_manager.set_theme_mode(ThemeMode.LIGHT)
            self.theme_toggle.text = "🌙"

        # Apply theme to page
        self.theme_manager.apply_theme_to_page(self.page)
        
        # Update all UI components with new theme
        self._update_ui_with_theme()

        # Update page
        self.page.update()
    
    def _update_ui_with_theme(self):
        """Update all UI components with current theme."""
        # Update sidebar colors
        sidebar_bg = self.theme_manager.get_color("sidebar") or "#ffffff"
        sidebar_border = self.theme_manager.get_color("sidebar-border") or "#e5e7eb"
        
        self.sidebar.bgcolor = sidebar_bg
        self.sidebar.border = ft.border.only(right=ft.border.BorderSide(1, sidebar_border))
        
        # Update content area colors
        content_bg = self.theme_manager.get_color("background") or "#f9fafb"
        self.content_area.bgcolor = content_bg
        
        # Update header colors
        header_bg = self.theme_manager.get_color("background") or "#f9fafb"
        header_border = self.theme_manager.get_color("border") or "#e5e7eb"
        header_text_color = self.theme_manager.get_color("foreground") or "#111827"
        
        self.header.bgcolor = header_bg
        self.header.border = ft.border.only(bottom=ft.border.BorderSide(1, header_border))
        self.header.content.controls[0].color = header_text_color  # Title
        self.header.content.controls[2].color = self.theme_manager.get_color("muted_foreground") or "#6b7280"  # Status
        
        # Update content container
        self.content_container.bgcolor = content_bg
        
        # Update current panel
        if self.current_panel in self.panels:
            # Rebuild current panel with new theme
            panel = self.panels[self.current_panel]
            if hasattr(panel, 'rebuild_with_theme'):
                panel.rebuild_with_theme()
            # Force update the panel content
            self._show_panel(self.current_panel)
            # Update page to reflect changes
            self.page.update()

    def _on_status_click(self, e):
        """Handle status indicator click."""
        # Show connection status modal or settings
        self._show_panel("settings")

    def _on_page_connect(self, e):
        """Handle page connect."""
        self.status_indicator.update_status("connected")
        # Load contacts after page is ready
        if "contacts" in self.panels:
            self.panels["contacts"].load_contacts_after_page_ready()

    def _on_page_disconnect(self, e):
        """Handle page disconnect."""
        self.status_indicator.update_status("disconnected")

    def show_snackbar(self, message: str, duration: int = 3000):
        """Show snackbar notification."""
        if self.snackbar_manager:
            self.snackbar_manager.show_info(message)
        else:
            snackbar = ft.SnackBar(
                content=ft.Text(message),
                duration=duration,
                bgcolor="#111827",  # Grey 900
                action="OK"
            )
            self.page.snack_bar = snackbar
            self.page.update()
    
    def _add_overlays_to_page(self):
        """Add overlays (FilePicker, etc.) to page."""
        try:
            # Add FilePicker from number checker panel
            number_checker = self.panels.get("checker")
            if number_checker and hasattr(number_checker, 'file_picker'):
                if number_checker.file_picker not in self.page.overlay:
                    self.page.overlay.append(number_checker.file_picker)
        except Exception as e:
            print(f"Error adding overlays: {e}")

    def show_modal(self, title: str, content: ft.Control, actions: Optional[list] = None):
        """Show modal dialog."""
        def close_dialog(e):
            """Close the modal dialog."""
            self.page.dialog.open = False
            self.page.update()

        modal = ft.AlertDialog(
            title=ft.Text(title),
            content=content,
            actions=actions or [
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("OK", on_click=close_dialog)
            ]
        )
        self.page.dialog = modal
        self.page.dialog.open = True
        self.page.update()

    def update_header_status(self, status: str):
        """Update header status text."""
        self.header.content.controls[2].value = status
        self.page.update()

    def get_current_panel(self) -> str:
        """Get current panel name."""
        return self.current_panel

    def get_theme_manager(self) -> ThemeManager:
        """Get theme manager instance."""
        return self.theme_manager
