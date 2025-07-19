"""
Number Checker Panel for Telegram Analyzer Tool.

This module contains the number checking interface.
"""

import flet as ft
from typing import Optional, Dict, Any
from ..theme_manager import ThemeManager
from ..widgets import ModernButton, ModernCard, ModernInput


class NumberCheckerPanel:
    """
    Number checker panel with modern design.
    
    This panel provides:
    - File upload for number lists
    - Number validation and checking
    - Progress tracking
    - Results display
    """

    def __init__(self, theme_manager: ThemeManager, core_modules: Dict[str, Any]):
        """
        Initialize the number checker panel.
        
        Args:
            theme_manager: Theme manager instance
            core_modules: Core modules dictionary
        """
        self.theme_manager = theme_manager
        self.core_modules = core_modules
        self.file_handler = core_modules.get('file_handler')
        self.telegram_client = core_modules.get('telegram_client')
        
        # UI components
        self.file_picker = None
        self.selected_file_text = None
        self.check_button = None
        self.progress_bar = None
        self.results_list = None
        
        # State
        self.selected_file_path = None
        self.numbers_to_check = []
        self.check_results = []
        self.is_checking = False
        
        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build the panel UI."""
        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Number Checker",
                        size=24,
                        weight=ft.FontWeight.W_700,
                        color=self.theme_manager.get_color("foreground")
                    ),
                    ft.Icon(
                        name="search",
                        size=24,
                        color=self.theme_manager.get_color("primary")
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.all(16),
            border=ft.border.only(bottom=ft.border.BorderSide(1, self.theme_manager.get_color("border")))
        )

        # File upload section
        upload_section = self._create_upload_section()
        
        # Progress section
        progress_section = self._create_progress_section()
        
        # Results section
        results_section = self._create_results_section()

        # Main content
        content = ft.Column(
            [
                header,
                upload_section,
                progress_section,
                results_section
            ],
            spacing=0,
            expand=True
        )

        self.content = ft.Container(
            content=content,
            expand=True,
            bgcolor=self.theme_manager.get_color("background")
        )

    def _create_upload_section(self) -> ft.Container:
        """Create file upload section."""
        # File picker
        self.file_picker = ft.FilePicker(
            on_result=self._on_file_selected
        )

        # Selected file text
        self.selected_file_text = ft.Text(
            "No file selected",
            size=14,
            color=self.theme_manager.get_color("muted_foreground")
        )

        # Upload button
        upload_button = ModernButton(
            text="Select File",
            on_click=lambda _: self.file_picker.pick_files(
                allowed_extensions=["txt", "xlsx", "xls", "csv"],
                allow_multiple=False
            ),
            variant="secondary"
        )

        # Upload content
        upload_content = ft.Column(
            [
                ft.Text(
                    "File Upload",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self.theme_manager.get_color("foreground")
                ),
                ft.Container(height=16),
                ft.Row(
                                    [
                    upload_button,
                    ft.Container(content=self.selected_file_text, expand=True)
                ],
                    spacing=12
                ),
                ft.Text(
                    "Supported formats: TXT, Excel (XLSX/XLS), CSV",
                    size=12,
                    color=self.theme_manager.get_color("muted_foreground")
                )
            ],
            spacing=8
        )

        return ModernCard(
            content=ft.Container(
                content=upload_content,
                padding=ft.padding.all(16)
            ),
            margin=ft.margin.all(16),
            theme_manager=self.theme_manager
        )

    def _create_progress_section(self) -> ft.Container:
        """Create progress section."""
        # Progress bar
        self.progress_bar = ft.ProgressBar(
            value=0,
            color=self.theme_manager.get_color("primary"),
            bgcolor=self.theme_manager.get_color("muted")
        )

        # Progress text
        self.progress_text = ft.Text(
            "Ready to check",
            size=14,
            color=self.theme_manager.get_color("muted_foreground")
        )

        # Check button
        self.check_button = ModernButton(
            text="Start Checking",
            on_click=self._on_start_checking,
            variant="primary",
            expand=True,
            disabled=True
        )

        # Progress content
        progress_content = ft.Column(
            [
                ft.Text(
                    "Progress",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self.theme_manager.get_color("foreground")
                ),
                ft.Container(height=16),
                self.progress_bar,
                ft.Container(height=8),
                self.progress_text,
                ft.Container(height=16),
                self.check_button
            ],
            spacing=8
        )

        return ModernCard(
            content=ft.Container(
                content=progress_content,
                padding=ft.padding.all(16)
            ),
            margin=ft.margin.symmetric(horizontal=16),
            theme_manager=self.theme_manager
        )

    def _create_results_section(self) -> ft.Container:
        """Create results section."""
        # Results header
        results_header = ft.Row(
            [
                ft.Text(
                    "Results",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self.theme_manager.get_color("foreground")
                ),
                ft.Text(
                    f"({len(self.check_results)} checked)",
                    size=14,
                    color=self.theme_manager.get_color("muted_foreground")
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Export button
        export_button = ModernButton(
            text="Export Results",
            on_click=self._on_export_results,
            variant="secondary"
        )

        # Results list
        self.results_list = ft.ListView(
            spacing=4,
            padding=ft.padding.all(16),
            height=300
        )

        # Results content
        results_content = ft.Column(
            [
                ft.Row(
                    [
                        results_header,
                        export_button
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=16),
                self.results_list
            ],
            spacing=8
        )

        return ModernCard(
            content=ft.Container(
                content=results_content,
                padding=ft.padding.all(16)
            ),
            margin=ft.margin.all(16),
            theme_manager=self.theme_manager
        )

    def _on_file_selected(self, e: ft.FilePickerResultEvent):
        """Handle file selection."""
        if e.files:
            file_path = e.files[0].path
            file_name = e.files[0].name
            
            self.selected_file_path = file_path
            self.selected_file_text.value = f"Selected: {file_name}"
            self.selected_file_text.color = self.theme_manager.get_color("foreground")
            
            # Enable check button
            self.check_button.disabled = False
            
            # Load numbers from file
            self._load_numbers_from_file()
            
            self.page.update()

    def _load_numbers_from_file(self):
        """Load numbers from selected file."""
        try:
            if self.file_handler and self.selected_file_path:
                self.numbers_to_check = self.file_handler.read_numbers_from_file(
                    self.selected_file_path
                )
                
                # Validate numbers
                self.numbers_to_check = self.file_handler.validate_phone_numbers(
                    self.numbers_to_check
                )
                
                self.progress_text.value = f"Loaded {len(self.numbers_to_check)} numbers"
                self.page.update()
                
        except Exception as e:
            print(f"Error loading file: {e}")
            self.progress_text.value = f"Error loading file: {e}"
            self.page.update()

    def _on_start_checking(self, e):
        """Handle start checking button click."""
        if not self.numbers_to_check:
            print("No numbers to check")
            return
        
        self.is_checking = True
        self.check_button.disabled = True
        self.check_button.text = "Checking..."
        self.progress_text.value = "Starting check..."
        self.page.update()
        
        # Start checking process (simplified for now)
        self._check_numbers()

    def _check_numbers(self):
        """Check numbers (simplified implementation)."""
        try:
            total = len(self.numbers_to_check)
            self.check_results = []
            
            for i, number in enumerate(self.numbers_to_check):
                # Simulate checking (replace with actual Telegram API call)
                is_valid = i % 3 == 0  # Simulate 33% valid rate
                
                result = {
                    'number': number,
                    'is_valid': is_valid,
                    'status': 'Valid' if is_valid else 'Invalid'
                }
                
                self.check_results.append(result)
                
                # Update progress
                progress = (i + 1) / total
                self.progress_bar.value = progress
                self.progress_text.value = f"Checking {i + 1}/{total} numbers..."
                self.page.update()
            
            # Update UI
            self.is_checking = False
            self.check_button.disabled = False
            self.check_button.text = "Start Checking"
            self.progress_text.value = f"Completed! {len([r for r in self.check_results if r['is_valid']])} valid numbers found"
            self._update_results_list()
            
        except Exception as e:
            print(f"Error checking numbers: {e}")
            self.is_checking = False
            self.check_button.disabled = False
            self.check_button.text = "Start Checking"
            self.progress_text.value = f"Error: {e}"
            self.page.update()

    def _update_results_list(self):
        """Update the results list display."""
        self.results_list.controls.clear()
        
        if not self.check_results:
            empty_state = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            name="search_off",
                            size=48,
                            color=self.theme_manager.get_color("muted_foreground")
                        ),
                        ft.Text(
                            "No results yet",
                            size=14,
                            color=self.theme_manager.get_color("muted_foreground")
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8
                ),
                padding=ft.padding.all(16),
                alignment=ft.alignment.center
            )
            self.results_list.controls.append(empty_state)
        else:
            # Show results
            for result in self.check_results[:50]:  # Show first 50
                status_color = "#22c55e" if result['is_valid'] else "#ef4444"  # Green/Red
                
                result_item = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                result['number'],
                                size=14,
                                color=self.theme_manager.get_color("foreground")
                            ),
                            ft.Container(
                                content=ft.Text(
                                    result['status'],
                                    size=12,
                                    color="#ffffff",  # White
                                    weight=ft.FontWeight.W_500
                                ),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=12
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=self.theme_manager.get_color("card"),
                    border_radius=4
                )
                self.results_list.controls.append(result_item)
            
            if len(self.check_results) > 50:
                more_text = ft.Text(
                    f"... and {len(self.check_results) - 50} more",
                    size=12,
                    color=self.theme_manager.get_color("muted_foreground"),
                    italic=True
                )
                self.results_list.controls.append(more_text)

        self.results_list.update()

    def _on_export_results(self, e):
        """Handle results export."""
        if not self.check_results:
            print("No results to export")
            return
        
        # TODO: Implement export functionality
        print(f"Exporting {len(self.check_results)} results")

    def get_content(self) -> ft.Control:
        """Get the panel content."""
        return self.content
    
    def rebuild_with_theme(self):
        """Rebuild UI with current theme."""
        self._build_ui()
        # Don't update lists during theme change - they will be updated when panel is shown
