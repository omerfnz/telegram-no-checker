"""
Specialized widgets for Telegram Analyzer Tool.

This module contains specialized UI components for specific functionality.
"""

import flet as ft
from typing import Optional, Callable, List, Dict, Any
from ..theme_manager import ThemeManager
from .modern_components import ModernInput, ModernButton, ModernCard, ModernBadge, ModernSelect


class FastFilter(ft.Container):
    """Fast filter widget with search and filter chips."""
    
    def __init__(
        self,
        placeholder: str = "Search...",
        on_change: Optional[Callable] = None,
        filters: Optional[List[str]] = None,
        on_filter_change: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.placeholder = placeholder
        self.on_change = on_change
        self.filters = filters or []
        self.on_filter_change = on_filter_change
        self.theme_manager = theme_manager
        
        self._setup_filter()
    
    def _setup_filter(self):
        """Setup filter widget."""
        # Search input
        self.search_input = ModernInput(
            hint_text=self.placeholder,
            on_change=self.on_change,
            size="default"
        )
        
        # Filter chips
        self.filter_chips = []
        for filter_name in self.filters:
            chip = ft.FilterChip(
                label=filter_name,
                selected=False,
                on_change=self._on_filter_change
            )
            self.filter_chips.append(chip)
        
        # Layout
        self.content = ft.Column([
            self.search_input,
            ft.Row(
                self.filter_chips,
                scroll=ft.ScrollMode.HORIZONTAL,
                spacing=8
            ) if self.filter_chips else None
        ], spacing=12)
        
        # Container styling
        self.padding = 16
        self.bgcolor = "#ffffff"  # White
        self.border_radius = 8
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200
    
    def _on_filter_change(self, e):
        """Handle filter change."""
        if self.on_filter_change:
            self.on_filter_change(e)


class ProgressBar(ft.Container):
    """Custom progress bar with detailed information."""
    
    def __init__(
        self,
        value: float = 0,
        total: float = 100,
        label: Optional[str] = None,
        show_percentage: bool = True,
        show_details: bool = True,
        color: Optional[str] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.value = value
        self.total = total
        self.label = label
        self.show_percentage = show_percentage
        self.show_details = show_details
        self.color = color
        self.theme_manager = theme_manager
        
        self._setup_progress_bar()
    
    def _setup_progress_bar(self):
        """Setup progress bar widget."""
        # Progress bar
        self.progress = ft.ProgressBar(
            value=self.value / self.total if self.total > 0 else 0,
            color=self.color or "#2563eb",  # Blue 600
            bgcolor="#e5e7eb",  # Grey 200
            bar_height=8,
            border_radius=4
        )
        
        # Label
        self.label_text = ft.Text(
            self.label or "Progress",
            size=14,
            weight=ft.FontWeight.W_500,
            color="#374151"  # Grey 700
        ) if self.label else None
        
        # Percentage
        self.percentage_text = ft.Text(
            f"{int((self.value / self.total) * 100)}%" if self.total > 0 else "0%",
            size=12,
            color="#6b7280"  # Grey 600
        ) if self.show_percentage else None
        
        # Details
        self.details_text = ft.Text(
            f"{int(self.value)} / {int(self.total)}",
            size=12,
            color="#6b7280"  # Grey 600
        ) if self.show_details else None
        
        # Layout
        content_parts = []
        if self.label_text:
            content_parts.append(self.label_text)
        
        content_parts.append(self.progress)
        
        if self.percentage_text or self.details_text:
            details_row = ft.Row([
                self.percentage_text,
                self.details_text
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            content_parts.append(details_row)
        
        self.content = ft.Column(content_parts, spacing=8)
        
        # Container styling
        self.padding = 16
        self.bgcolor = "#ffffff"  # White
        self.border_radius = 8
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200
    
    def update_progress(self, value: float, total: Optional[float] = None):
        """Update progress values."""
        self.value = value
        if total is not None:
            self.total = total
        
        self.progress.value = self.value / self.total if self.total > 0 else 0
        
        if self.percentage_text:
            self.percentage_text.value = f"{int((self.value / self.total) * 100)}%" if self.total > 0 else "0%"
        
        if self.details_text:
            self.details_text.value = f"{int(self.value)} / {int(self.total)}"
        
        self.update()


class NumberRangeInput(ft.Container):
    """Number range input widget for number generation."""
    
    def __init__(
        self,
        label: str = "Number Range",
        min_value: int = 0,
        max_value: int = 9999999,
        start_value: Optional[int] = None,
        end_value: Optional[int] = None,
        on_change: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.start_value = start_value or min_value
        self.end_value = end_value or max_value
        self.on_change = on_change
        self.theme_manager = theme_manager
        
        self._setup_range_input()
    
    def _setup_range_input(self):
        """Setup range input widget."""
        # Label
        self.label_text = ft.Text(
            self.label,
            size=14,
            weight=ft.FontWeight.W_500,
            color="#374151"  # Grey 700
        )
        
        # Start input
        self.start_input = ModernInput(
            label="Start",
            hint_text="Start number",
            value=str(self.start_value),
            on_change=self._on_start_change,
            size="default"
        )
        
        # End input
        self.end_input = ModernInput(
            label="End",
            hint_text="End number",
            value=str(self.end_value),
            on_change=self._on_end_change,
            size="default"
        )
        
        # Range slider
        self.range_slider = ft.RangeSlider(
            min=self.min_value,
            max=self.max_value,
            start_value=self.start_value,
            end_value=self.end_value,
            divisions=100,
            on_change=self._on_slider_change,
            active_color="#2563eb",  # Blue 600
            inactive_color="#d1d5db"  # Grey 300
        )
        
        # Layout
        self.content = ft.Column([
            self.label_text,
            ft.Row([
                self.start_input,
                self.end_input
            ], spacing=16),
            self.range_slider
        ], spacing=12)
        
        # Container styling
        self.padding = 16
        self.bgcolor = "#ffffff"  # White
        self.border_radius = 8
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200
    
    def _on_start_change(self, e):
        """Handle start value change."""
        try:
            value = int(e.control.value)
            if value < self.min_value:
                value = self.min_value
            elif value > self.end_value:
                value = self.end_value
            
            self.start_value = value
            self.range_slider.start_value = value
            
            if self.on_change:
                self.on_change(self.start_value, self.end_value)
            
            self.update()
        except ValueError:
            pass
    
    def _on_end_change(self, e):
        """Handle end value change."""
        try:
            value = int(e.control.value)
            if value > self.max_value:
                value = self.max_value
            elif value < self.start_value:
                value = self.start_value
            
            self.end_value = value
            self.range_slider.end_value = value
            
            if self.on_change:
                self.on_change(self.start_value, self.end_value)
            
            self.update()
        except ValueError:
            pass
    
    def _on_slider_change(self, e):
        """Handle slider change."""
        self.start_value = int(e.control.start_value)
        self.end_value = int(e.control.end_value)
        
        self.start_input.value = str(self.start_value)
        self.end_input.value = str(self.end_value)
        
        if self.on_change:
            self.on_change(self.start_value, self.end_value)
        
        self.update()


class FileUploader(ft.Container):
    """File upload widget with drag and drop support."""
    
    def __init__(
        self,
        label: str = "Upload File",
        accepted_types: Optional[List[str]] = None,
        max_size: Optional[int] = None,  # in MB
        on_file_selected: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.label = label
        self.accepted_types = accepted_types or ["txt", "xlsx", "xls", "csv"]
        self.max_size = max_size
        self.on_file_selected = on_file_selected
        self.theme_manager = theme_manager
        
        self._setup_uploader()
    
    def _setup_uploader(self):
        """Setup file uploader widget."""
        # File picker
        self.file_picker = ft.FilePicker(
            on_result=self._on_file_selected
        )
        
        # Upload area
        self.upload_area = ft.Container(
            content=ft.Column([
                ft.Icon(
                    name="upload_file",
                    size=48,
                    color="#6b7280"  # Grey 600
                ),
                ft.Text(
                    self.label,
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color="#374151"  # Grey 700
                ),
                ft.Text(
                    f"Supported: {', '.join(self.accepted_types).upper()}",
                    size=12,
                    color="#6b7280"  # Grey 600
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=32,
            bgcolor="#f9fafb",  # Grey 50
            border=ft.border.all(2, "#e5e7eb", style=ft.BorderStyle.DASHED)  # Grey 200
        )
        
        # Upload button
        self.upload_button = ModernButton(
            text="Select File",
            on_click=lambda _: self.file_picker.pick_files(
                allowed_extensions=self.accepted_types,
                allow_multiple=False
            ),
            variant="primary"
        )
        
        # Layout
        self.content = ft.Column([
            self.upload_area,
            self.upload_button
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Container styling
        self.padding = 16
        self.bgcolor = "#ffffff"  # White
        self.border_radius = 8
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200
    
    def _on_file_selected(self, e: ft.FilePickerResultEvent):
        """Handle file selection."""
        if e.files and self.on_file_selected:
            file_info = e.files[0]
            
            # Check file size
            if self.max_size and file_info.size > self.max_size * 1024 * 1024:
                print(f"File too large. Max size: {self.max_size}MB")
                return
            
            self.on_file_selected(file_info.path, file_info.name, file_info.size)


class CountrySelector(ft.Container):
    """Country selector widget."""
    
    def __init__(
        self,
        label: str = "Country",
        selected_country: str = "+90",
        countries: Optional[List[str]] = None,
        on_change: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.label = label
        self.selected_country = selected_country
        self.countries = countries or ["+90", "+1", "+44", "+49", "+33", "+39"]
        self.on_change = on_change
        self.theme_manager = theme_manager
        
        self._setup_selector()
    
    def _setup_selector(self):
        """Setup country selector widget."""
        # Label
        self.label_text = ft.Text(
            self.label,
            size=14,
            weight=ft.FontWeight.W_500,
            color="#374151"  # Grey 700
        )
        
        # Country dropdown
        self.country_dropdown = ft.Dropdown(
            value=self.selected_country,
            options=[
                ft.dropdown.Option(code, f"{self._get_country_name(code)} ({code})")
                for code in self.countries
            ],
            on_change=self._on_country_change,
            expand=True
        )
        
        # Layout
        self.content = ft.Column([
            self.label_text,
            self.country_dropdown
        ], spacing=8)
        
        # Container styling
        self.padding = 16
        self.bgcolor = "#ffffff"  # White
        self.border_radius = 8
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200
    
    def _get_country_name(self, country_code: str) -> str:
        """Get country name from code."""
        country_names = {
            "+90": "Turkey",
            "+1": "USA",
            "+44": "UK",
            "+49": "Germany",
            "+33": "France",
            "+39": "Italy"
        }
        return country_names.get(country_code, "Unknown")
    
    def _on_country_change(self, e):
        """Handle country change."""
        self.selected_country = e.control.value
        if self.on_change:
            self.on_change(self.selected_country)


class OperatorSelector(ft.Container):
    """Operator selector widget."""
    
    def __init__(
        self,
        label: str = "Operators",
        country_code: str = "+90",
        selected_operators: Optional[List[str]] = None,
        on_change: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.label = label
        self.country_code = country_code
        self.selected_operators = selected_operators or []
        self.on_change = on_change
        self.theme_manager = theme_manager
        
        self._setup_selector()
    
    def _setup_selector(self):
        """Setup operator selector widget."""
        # Label
        self.label_text = ft.Text(
            self.label,
            size=14,
            weight=ft.FontWeight.W_500,
            color="#374151"  # Grey 700
        )
        
        # Operator checkboxes
        operators = self._get_operators_for_country(self.country_code)
        self.operator_checkboxes = []
        
        for operator_name, prefixes in operators.items():
            checkbox = ft.Checkbox(
                label=operator_name,
                value=operator_name in self.selected_operators,
                on_change=self._on_operator_change
            )
            self.operator_checkboxes.append(checkbox)
        
        # Layout
        self.content = ft.Column([
            self.label_text,
            ft.Column(self.operator_checkboxes, spacing=8)
        ], spacing=12)
        
        # Container styling
        self.padding = 16
        self.bgcolor = "#ffffff"  # White
        self.border_radius = 8
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200
    
    def _get_operators_for_country(self, country_code: str) -> Dict[str, List[str]]:
        """Get operators for country."""
        operators = {
            "+90": {
                "Turkcell": ["501", "502", "503", "504", "505", "506", "507", "508", "509", "530", "531", "532", "533", "534", "535", "536", "537", "538", "539", "561"],
                "Vodafone": ["542", "543", "544", "545", "546", "547", "548", "549", "552", "553", "554", "555", "556", "557", "558", "559"],
                "Türk Telekom": ["501", "502", "503", "504", "505", "506", "507", "508", "509", "530", "531", "532", "533", "534", "535", "536", "537", "538", "539"]
            }
        }
        return operators.get(country_code, {})
    
    def _on_operator_change(self, e):
        """Handle operator change."""
        operator_name = e.control.label
        if e.control.value:
            if operator_name not in self.selected_operators:
                self.selected_operators.append(operator_name)
        else:
            if operator_name in self.selected_operators:
                self.selected_operators.remove(operator_name)
        
        if self.on_change:
            self.on_change(self.selected_operators)


class PatternInput(ft.Container):
    """Number pattern input widget."""
    
    def __init__(
        self,
        label: str = "Number Pattern",
        pattern: str = "####",
        on_change: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.label = label
        self.pattern = pattern
        self.on_change = on_change
        self.theme_manager = theme_manager
        
        self._setup_pattern_input()
    
    def _setup_pattern_input(self):
        """Setup pattern input widget."""
        # Label
        self.label_text = ft.Text(
            self.label,
            size=14,
            weight=ft.FontWeight.W_500,
            color="#374151"  # Grey 700
        )
        
        # Pattern input
        self.pattern_input = ModernInput(
            label="Pattern",
            hint_text="e.g., ####, ###-####, (###) ###-####",
            value=self.pattern,
            on_change=self._on_pattern_change
        )
        
        # Pattern preview
        self.preview_text = ft.Text(
            f"Preview: {self.pattern}",
            size=12,
            color="#6b7280"  # Grey 600
        )
        
        # Layout
        self.content = ft.Column([
            self.label_text,
            self.pattern_input,
            self.preview_text
        ], spacing=8)
        
        # Container styling
        self.padding = 16
        self.bgcolor = "#ffffff"  # White
        self.border_radius = 8
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200
    
    def _on_pattern_change(self, e):
        """Handle pattern change."""
        self.pattern = e.control.value
        self.preview_text.value = f"Preview: {self.pattern}"
        
        if self.on_change:
            self.on_change(self.pattern)
        
        self.update()


class SessionCard(ft.Container):
    """Session card widget for displaying session information."""
    
    def __init__(
        self,
        session_name: str,
        country_code: str,
        total_numbers: int,
        checked_numbers: int,
        status: str = "ready",
        on_click: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.session_name = session_name
        self.country_code = country_code
        self.total_numbers = total_numbers
        self.checked_numbers = checked_numbers
        self.status = status
        self.on_click = on_click
        self.theme_manager = theme_manager
        
        self._setup_session_card()
    
    def _setup_session_card(self):
        """Setup session card widget."""
        # Status badge
        status_badge = ModernBadge(
            text=self.status.title(),
            variant=self._get_status_variant()
        )
        
        # Progress
        progress = ft.ProgressBar(
            value=self.checked_numbers / self.total_numbers if self.total_numbers > 0 else 0,
            color="#2563eb",  # Blue 600
            bgcolor="#e5e7eb",  # Grey 200
            bar_height=4
        )
        
        # Content
        self.content = ft.Column([
            ft.Row([
                ft.Text(
                    self.session_name,
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color="#111827"  # Grey 900
                ),
                status_badge
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(
                f"Country: {self.country_code}",
                size=14,
                color="#6b7280"  # Grey 600
            ),
            ft.Text(
                f"Progress: {self.checked_numbers}/{self.total_numbers}",
                size=14,
                color="#6b7280"  # Grey 600
            ),
            progress
        ], spacing=8)
        
        # Container styling
        self.padding = 16
        self.bgcolor = "#ffffff"  # White
        self.border_radius = 8
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200
        
        if self.on_click:
            self.on_click = self.on_click
    
    def _get_status_variant(self) -> str:
        """Get status badge variant."""
        variants = {
            "ready": "default",
            "running": "secondary",
            "completed": "default",
            "error": "destructive"
        }
        return variants.get(self.status, "default")


class StatisticsCard(ft.Container):
    """Statistics card widget."""
    
    def __init__(
        self,
        title: str,
        value: str,
        subtitle: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        self.color = color or "#2563eb"  # Blue 600
        self.theme_manager = theme_manager
        
        self._setup_statistics_card()
    
    def _setup_statistics_card(self):
        """Setup statistics card widget."""
        # Icon
        icon_widget = ft.Icon(
            name=self.icon or "analytics",
            size=24,
            color=self.color
        ) if self.icon else None
        
        # Content
        content_parts = [
            ft.Text(
                self.value,
                size=24,
                weight=ft.FontWeight.W_700,
                color=self.color
            ),
            ft.Text(
                self.title,
                size=14,
                color="#6b7280"  # Grey 600
            )
        ]
        
        if self.subtitle:
            content_parts.append(ft.Text(
                self.subtitle,
                size=12,
                color="#6b7280"  # Grey 600
            ))
        
        self.content = ft.Column(
            content_parts,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4
        )
        
        # Container styling
        self.padding = 16
        self.bgcolor = "#ffffff"  # White
        self.border_radius = 8
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200


class StatusIndicator(ft.Container):
    """Status indicator widget."""
    
    def __init__(
        self,
        status: str = "disconnected",  # connected, disconnected, connecting, error
        on_click: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.status = status
        self.on_click = on_click
        self.theme_manager = theme_manager
        
        self._setup_status_indicator()
    
    def _setup_status_indicator(self):
        """Setup status indicator widget."""
        # Status dot
        self.status_dot = ft.Container(
            width=8,
            height=8,
            border_radius=4,
            bgcolor=self._get_status_color()
        )
        
        # Status text
        self.status_text = ft.Text(
            self.status.title(),
            size=12,
            color="#6b7280"  # Grey 600
        )
        
        # Content
        self.content = ft.Row([
            self.status_dot,
            self.status_text
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
        
        # Container styling
        self.padding = 8
        self.bgcolor = "#f3f4f6"  # Grey 100
        self.border_radius = 16
        self.border = ft.border.all(1, "#e5e7eb")  # Grey 200
        
        if self.on_click:
            self.on_click = self.on_click
    
    def _get_status_color(self) -> str:
        """Get status color."""
        status_colors = {
            "connected": "#22c55e",  # Green 500
            "disconnected": "#9ca3af",  # Grey 400
            "connecting": "#eab308",  # Yellow 500
            "error": "#ef4444"  # Red 500
        }
        return status_colors.get(self.status, "#9ca3af")  # Grey 400
    
    def update_status(self, status: str):
        """Update status."""
        self.status = status
        self.status_dot.bgcolor = self._get_status_color()
        self.status_text.value = self.status.title()
        self.update() 