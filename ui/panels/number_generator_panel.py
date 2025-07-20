"""
Number Generator Panel for Telegram Analyzer Tool.

This module contains the automatic number generation interface.
"""

import flet as ft
from typing import Optional, Dict, Any
from datetime import datetime
from ..theme_manager import ThemeManager
from ..widgets import ModernButton, ModernCard, ModernInput


class NumberGeneratorPanel:
    """
    Number generator panel with modern design.
    
    This panel provides:
    - Country and operator selection
    - Number range configuration
    - Bulk number generation
    - Generated numbers display
    """

    def __init__(self, theme_manager: ThemeManager, core_modules: Dict[str, Any], snackbar_manager = None):
        """
        Initialize the number generator panel.
        
        Args:
            theme_manager: Theme manager instance
            core_modules: Core modules dictionary
            snackbar_manager: Snackbar manager instance
        """
        self.theme_manager = theme_manager
        self.core_modules = core_modules
        self.snackbar_manager = snackbar_manager
        self.number_generator = core_modules.get('number_generator')
        
        # UI components
        self.country_dropdown = None
        self.operator_checkboxes = {}
        self.range_start_input = None
        self.range_end_input = None
        self.count_input = None
        self.generate_button = None
        self.numbers_list = None
        
        # State
        self.generated_numbers = []
        self.selected_country = "+90"
        self.selected_operators = []
        
        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build the panel UI."""
        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Number Generator",
                        size=24,
                        weight=ft.FontWeight.W_700,
                        color=self.theme_manager.get_color("foreground")
                    ),
                    ft.Icon(
                        name="generate",
                        size=24,
                        color=self.theme_manager.get_color("primary")
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.all(16),
            border=ft.border.only(bottom=ft.border.BorderSide(1, self.theme_manager.get_color("border")))
        )

        # Configuration section
        config_section = self._create_config_section()
        
        # Generation section
        generation_section = self._create_generation_section()
        
        # Results section
        results_section = self._create_results_section()

        # Main content
        content = ft.Column(
            [
                header,
                config_section,
                generation_section,
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

    def _create_config_section(self) -> ft.Container:
        """Create configuration section."""
        # Country selection
        self.country_dropdown = ft.Dropdown(
            label="Country Code",
            value=self.selected_country,
            options=[
                ft.dropdown.Option("+90", "Turkey (+90)"),
                ft.dropdown.Option("+1", "USA (+1)"),
                ft.dropdown.Option("+44", "UK (+44)")
            ],
            on_change=self._on_country_change,
            expand=True
        )

        # Operator selection
        operator_label = ft.Text(
            "Operators",
            size=14,
            weight=ft.FontWeight.W_600,
            color=self.theme_manager.get_color("foreground")
        )

        operator_grid = ft.GridView(
            runs_count=3,
            max_extent=150,
            child_aspect_ratio=2.0,
            spacing=8,
            run_spacing=8
        )

        # Add operator checkboxes
        if self.number_generator:
            operators = self.number_generator.get_operators_for_country(self.selected_country)
            for operator in operators:
                checkbox = ft.Checkbox(
                    label=operator,
                    value=False,
                    on_change=lambda e, op=operator: self._on_operator_change(e, op)
                )
                operator_grid.controls.append(checkbox)
                self.operator_checkboxes[operator] = checkbox

        # Range configuration
        range_label = ft.Text(
            "Number Range",
            size=14,
            weight=ft.FontWeight.W_600,
            color=self.theme_manager.get_color("foreground")
        )

        self.range_start_input = ModernInput(
            label="Start Range",
            hint_text="0",
            value="0",
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.range_end_input = ModernInput(
            label="End Range",
            hint_text="9999999",
            value="9999999",
            keyboard_type=ft.KeyboardType.NUMBER
        )

        range_row = ft.Row(
            [
                self.range_start_input,
                self.range_end_input
            ],
            spacing=12
        )

        # Configuration card
        config_content = ft.Column(
            [
                ft.Text(
                    "Configuration",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self.theme_manager.get_color("foreground")
                ),
                ft.Container(height=16),
                ft.Text("Country", size=14, weight=ft.FontWeight.W_500),
                self.country_dropdown,
                ft.Container(height=16),
                operator_label,
                operator_grid,
                ft.Container(height=16),
                range_label,
                range_row
            ],
            spacing=8
        )

        return ModernCard(
            content=ft.Container(
                content=config_content,
                padding=ft.padding.all(16)
            ),
            margin=ft.margin.all(16),
            theme_manager=self.theme_manager
        )

    def _create_generation_section(self) -> ft.Container:
        """Create generation section."""
        # Count input
        self.count_input = ModernInput(
            label="Number Count",
            hint_text="1000",
            value="1000",
            keyboard_type=ft.KeyboardType.NUMBER
        )

        # Generate button
        self.generate_button = ModernButton(
            text="Generate Numbers",
            on_click=self._on_generate_numbers,
            variant="primary",
            expand=True
        )

        # Generation controls
        generation_content = ft.Column(
            [
                ft.Text(
                    "Generation",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self.theme_manager.get_color("foreground")
                ),
                ft.Container(height=16),
                self.count_input,
                ft.Container(height=16),
                self.generate_button
            ],
            spacing=8
        )

        return ModernCard(
            content=ft.Container(
                content=generation_content,
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
                    "Generated Numbers",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self.theme_manager.get_color("foreground")
                ),
                ft.Text(
                    f"({len(self.generated_numbers)} numbers)",
                    size=14,
                    color=self.theme_manager.get_color("muted_foreground")
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Export button
        export_button = ModernButton(
            text="Export",
            on_click=self._on_export_numbers,
            variant="secondary"
        )

        # Numbers list
        self.numbers_list = ft.ListView(
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
                self.numbers_list
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

    def _on_country_change(self, e):
        """Handle country selection change."""
        self.selected_country = e.control.value
        self._update_operators()
        self.page.update()

    def _on_operator_change(self, e, operator):
        """Handle operator selection change."""
        if e.control.value:
            if operator not in self.selected_operators:
                self.selected_operators.append(operator)
        else:
            if operator in self.selected_operators:
                self.selected_operators.remove(operator)

    def _update_operators(self):
        """Update operator checkboxes based on selected country."""
        # Clear existing checkboxes
        for checkbox in self.operator_checkboxes.values():
            checkbox.value = False
        
        # Add new operators
        if self.number_generator:
            operators = self.number_generator.get_operators_for_country(self.selected_country)
            # Update existing checkboxes or create new ones
            # (Simplified for now)

    def _on_generate_numbers(self, e):
        """Handle number generation."""
        try:
            if not self.selected_operators:
                if self.snackbar_manager:
                    self.snackbar_manager.show_warning("Please select at least one operator")
                return

            count = int(self.count_input.value or 1000)
            
            if self.number_generator:
                # Show progress
                if self.snackbar_manager:
                    self.snackbar_manager.show_info(f"Generating {count} numbers...")
                
                self.generated_numbers = self.number_generator.generate_numbers_bulk(
                    country_code=self.selected_country,
                    operators=self.selected_operators,
                    count=count
                )
                
                self._update_numbers_list()
                
                # Show success
                if self.snackbar_manager:
                    self.snackbar_manager.show_success(f"Generated {len(self.generated_numbers)} numbers")
            
        except Exception as e:
            if self.snackbar_manager:
                self.snackbar_manager.show_error(f"Error generating numbers: {str(e)}")
            else:
                print(f"Error generating numbers: {e}")

    def _update_numbers_list(self):
        """Update the numbers list display."""
        self.numbers_list.controls.clear()
        
        if not self.generated_numbers:
            empty_state = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            name="numbers",
                            size=48,
                            color=self.theme_manager.get_color("muted_foreground")
                        ),
                        ft.Text(
                            "No numbers generated",
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
            self.numbers_list.controls.append(empty_state)
        else:
            # Show first 50 numbers
            for number in self.generated_numbers[:50]:
                number_item = ft.Container(
                    content=ft.Text(
                        number,
                        size=14,
                        color=self.theme_manager.get_color("foreground")
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=self.theme_manager.get_color("card"),
                    border_radius=4
                )
                self.numbers_list.controls.append(number_item)
            
            if len(self.generated_numbers) > 50:
                more_text = ft.Text(
                    f"... and {len(self.generated_numbers) - 50} more",
                    size=12,
                    color=self.theme_manager.get_color("muted_foreground"),
                    italic=True
                )
                self.numbers_list.controls.append(more_text)

        self.numbers_list.update()

    def _on_export_numbers(self, e):
        """Handle number export."""
        self._export_numbers_to_excel()
    
    def _export_numbers_to_excel(self):
        """Export generated numbers to Excel file."""
        try:
            if not self.generated_numbers:
                if self.snackbar_manager:
                    self.snackbar_manager.show_warning("No numbers to export")
                return
            
            # Get file handler
            file_handler = self.core_modules.get('file_handler')
            if not file_handler:
                if self.snackbar_manager:
                    self.snackbar_manager.show_error("File handler not available")
                return
            
            # Export to Excel
            filename = f"generated_numbers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            success = file_handler.export_number_records_to_excel(self.generated_numbers, filename)
            
            if success:
                if self.snackbar_manager:
                    self.snackbar_manager.show_success(f"Numbers exported to {filename}")
            else:
                if self.snackbar_manager:
                    self.snackbar_manager.show_error("Failed to export numbers")
                    
        except Exception as e:
            if self.snackbar_manager:
                self.snackbar_manager.show_error(f"Export error: {str(e)}")

    def get_content(self) -> ft.Control:
        """Get the panel content."""
        return self.content
    
    def set_page(self, page: ft.Page):
        """Set page reference."""
        self.page = page
    
    def rebuild_with_theme(self):
        """Rebuild UI with current theme."""
        self._build_ui()
        # Don't update lists during theme change - they will be updated when panel is shown
