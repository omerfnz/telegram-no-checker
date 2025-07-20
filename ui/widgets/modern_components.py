"""
Modern UI components with Shadcn-inspired design.

This module contains modern, responsive UI components.
"""

import flet as ft
from typing import Optional, Callable, List, Dict, Any
from ..theme_manager import ThemeManager


class ModernButton(ft.ElevatedButton):
    """Modern button with Shadcn-inspired design."""
    
    def __init__(
        self,
        text: str,
        on_click: Optional[Callable] = None,
        variant: str = "default",  # default, destructive, outline, secondary, ghost, link
        size: str = "default",     # default, sm, lg, icon
        disabled: bool = False,
        loading: bool = False,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.text = text
        self.on_click = on_click
        self.variant = variant
        self.size = size
        self.disabled = disabled
        self.loading = loading
        self.theme_manager = theme_manager
        
        self._setup_button()
    
    def _setup_button(self):
        """Setup button styling based on variant and size."""
        # Base styling
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=self._get_padding(),
        )
        
        # Variant-specific styling
        if self.variant == "default":
            self.bgcolor = "#2563eb"  # Blue 600
            self.color = "#ffffff"    # White
        elif self.variant == "destructive":
            self.bgcolor = "#dc2626"  # Red 600
            self.color = "#ffffff"    # White
        elif self.variant == "outline":
            self.bgcolor = "transparent"
            self.color = "#2563eb"    # Blue 600
            self.style.border = ft.border.all(1, "#2563eb")
        elif self.variant == "secondary":
            self.bgcolor = "#f3f4f6"  # Grey 100
            self.color = "#000000"    # Black
        elif self.variant == "ghost":
            self.bgcolor = "transparent"
            self.color = "#2563eb"    # Blue 600
        elif self.variant == "link":
            self.bgcolor = "transparent"
            self.color = "#2563eb"    # Blue 600
            self.style.underlined = True
        
        # Size-specific styling
        if self.size == "sm":
            self.style.padding = ft.padding.all(8)
        elif self.size == "lg":
            self.style.padding = ft.padding.all(16)
        elif self.size == "icon":
            self.style.padding = ft.padding.all(12)
        
        # Loading state
        if self.loading:
            self.content = ft.Row([
                ft.ProgressRing(width=16, height=16, stroke_width=2),
                ft.Text("Loading...", size=14)
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
        else:
            self.content = ft.Text(self.text, size=self._get_font_size())
        
        # Disabled state
        if self.disabled:
            self.opacity = 0.5
    
    def _get_padding(self) -> Any:
        """Get padding based on size."""
        if self.size == "sm":
            return ft.padding.symmetric(horizontal=12, vertical=6)
        elif self.size == "lg":
            return ft.padding.symmetric(horizontal=24, vertical=12)
        elif self.size == "icon":
            return ft.padding.all(12)
        else:  # default
            return ft.padding.symmetric(horizontal=16, vertical=8)
    
    def _get_font_size(self) -> int:
        """Get font size based on button size."""
        if self.size == "sm":
            return 12
        elif self.size == "lg":
            return 16
        else:
            return 14


class ModernCard(ft.Card):
    """Modern card with Shadcn-inspired design."""
    
    def __init__(
        self,
        content: ft.Control,
        padding: float = 16,
        margin: float = 8,
        elevation: int = 1,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.content = content
        self.padding = padding
        self.margin = margin
        self.elevation = elevation
        self.theme_manager = theme_manager
        
        self._setup_card()
    
    def _setup_card(self):
        """Setup card styling."""
        self.content = ft.Container(
            content=self.content,
            padding=self.padding,
            margin=self.margin,
            bgcolor=self.theme_manager.get_color("card") if self.theme_manager else None,
        )
        
        # Apply modern styling
        self.elevation = self.elevation
        if self.theme_manager:
            self.color = self.theme_manager.get_color("card") or "#ffffff"
            self.shadow_color = self.theme_manager.get_color("shadow-sm") or "#0000001f"
        else:
            self.color = "#ffffff"  # White
            self.shadow_color = "#0000001f"  # Black12


class ModernInput(ft.TextField):
    """Modern input field with Shadcn-inspired design."""
    
    def __init__(
        self,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        placeholder: Optional[str] = None,  # Alias for hint_text
        value: Optional[str] = None,
        on_change: Optional[Callable] = None,
        size: str = "default",  # sm, default, lg
        variant: str = "outlined",  # outlined, filled
        disabled: bool = False,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        # Remove placeholder from kwargs to avoid conflict
        kwargs.pop('placeholder', None)
        super().__init__(**kwargs)
        
        self.label = label
        self.hint_text = hint_text or placeholder  # Use placeholder as alias
        self.value = value
        self.on_change = on_change
        self.size = size
        self.variant = variant
        self.disabled = disabled
        self.theme_manager = theme_manager
        
        self._setup_input()
    
    def _setup_input(self):
        """Setup input styling."""
        # Base properties
        self.label = self.label
        self.hint_text = self.hint_text
        self.value = self.value
        self.on_change = self.on_change
        self.disabled = self.disabled
        
        # Size-specific styling
        if self.size == "sm":
            self.text_size = 12
            self.content_padding = ft.padding.symmetric(horizontal=12, vertical=8)
        elif self.size == "lg":
            self.text_size = 16
            self.content_padding = ft.padding.symmetric(horizontal=16, vertical=12)
        else:  # default
            self.text_size = 14
            self.content_padding = ft.padding.symmetric(horizontal=16, vertical=10)
        
        # Variant-specific styling
        if self.variant == "filled":
            self.filled = True
            if self.theme_manager:
                self.bgcolor = self.theme_manager.get_color("muted") or "#f9fafb"
            else:
                self.bgcolor = "#f9fafb"  # Grey 50
        
        # Border styling
        self.border_radius = 8
        if self.theme_manager:
            self.border_color = self.theme_manager.get_color("border") or "#d1d5db"
            self.focused_border_color = self.theme_manager.get_color("ring") or "#3b82f6"
        else:
            self.border_color = "#d1d5db"  # Grey 300
            self.focused_border_color = "#3b82f6"  # Blue 500


class ModernSelect(ft.Dropdown):
    """Modern select dropdown with Shadcn-inspired design."""
    
    def __init__(
        self,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        options: Optional[List[ft.dropdown.Option]] = None,
        value: Optional[str] = None,
        on_change: Optional[Callable] = None,
        size: str = "default",
        disabled: bool = False,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.label = label
        self.hint_text = hint_text
        self.options = options or []
        self.value = value
        self.on_change = on_change
        self.size = size
        self.disabled = disabled
        self.theme_manager = theme_manager
        
        self._setup_select()
    
    def _setup_select(self):
        """Setup select styling."""
        # Base properties
        self.label = self.label
        self.hint_text = self.hint_text
        self.options = self.options
        self.value = self.value
        self.on_change = self.on_change
        self.disabled = self.disabled
        
        # Size-specific styling
        if self.size == "sm":
            self.text_size = 12
            self.content_padding = ft.padding.symmetric(horizontal=12, vertical=8)
        elif self.size == "lg":
            self.text_size = 16
            self.content_padding = ft.padding.symmetric(horizontal=16, vertical=12)
        else:  # default
            self.text_size = 14
            self.content_padding = ft.padding.symmetric(horizontal=16, vertical=10)
        
        # Border styling
        self.border_radius = 8
        if self.theme_manager:
            self.border_color = self.theme_manager.get_color("border") or "#d1d5db"
            self.focused_border_color = self.theme_manager.get_color("ring") or "#3b82f6"
        else:
            self.border_color = "#d1d5db"  # Grey 300
            self.focused_border_color = "#3b82f6"  # Blue 500


class ModernCheckbox(ft.Checkbox):
    """Modern checkbox with Shadcn-inspired design."""
    
    def __init__(
        self,
        label: Optional[str] = None,
        value: bool = False,
        on_change: Optional[Callable] = None,
        disabled: bool = False,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.label = label
        self.value = value
        self.on_change = on_change
        self.disabled = disabled
        self.theme_manager = theme_manager
        
        self._setup_checkbox()
    
    def _setup_checkbox(self):
        """Setup checkbox styling."""
        # Base properties
        self.label = self.label
        self.value = self.value
        self.on_change = self.on_change
        self.disabled = self.disabled
        
        # Modern styling
        self.check_color = "#ffffff"  # White
        self.fill_color = "#2563eb"   # Blue 600
        self.hover_color = "#3b82f6"  # Blue 500


class ModernSwitch(ft.Switch):
    """Modern switch with Shadcn-inspired design."""
    
    def __init__(
        self,
        label: Optional[str] = None,
        value: bool = False,
        on_change: Optional[Callable] = None,
        disabled: bool = False,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.label = self.label
        self.value = value
        self.on_change = on_change
        self.disabled = disabled
        self.theme_manager = theme_manager
        
        self._setup_switch()
    
    def _setup_switch(self):
        """Setup switch styling."""
        # Base properties
        self.label = self.label
        self.value = self.value
        self.on_change = self.on_change
        self.disabled = self.disabled
        
        # Modern styling
        self.active_color = "#2563eb"  # Blue 600
        self.inactive_color = "#d1d5db"  # Grey 300


class ModernSlider(ft.Slider):
    """Modern slider with Shadcn-inspired design."""
    
    def __init__(
        self,
        min_value: float = 0,
        max_value: float = 100,
        value: float = 50,
        divisions: Optional[int] = None,
        on_change: Optional[Callable] = None,
        disabled: bool = False,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.min = min_value
        self.max = max_value
        self.value = value
        self.divisions = divisions
        self.on_change = on_change
        self.disabled = disabled
        self.theme_manager = theme_manager
        
        self._setup_slider()
    
    def _setup_slider(self):
        """Setup slider styling."""
        # Base properties
        self.min = self.min
        self.max = self.max
        self.value = self.value
        self.divisions = self.divisions
        self.on_change = self.on_change
        self.disabled = self.disabled
        
        # Modern styling
        self.active_color = "#2563eb"  # Blue 600
        self.inactive_color = "#d1d5db"  # Grey 300
        self.thumb_color = "#2563eb"  # Blue 600


class ModernProgressBar(ft.ProgressBar):
    """Modern progress bar with Shadcn-inspired design."""
    
    def __init__(
        self,
        value: float = 0,
        color: Optional[str] = None,
        bgcolor: Optional[str] = None,
        size: str = "default",  # sm, default, lg
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.value = value
        self.color = color
        self.bgcolor = bgcolor
        self.size = size
        self.theme_manager = theme_manager
        
        self._setup_progress_bar()
    
    def _setup_progress_bar(self):
        """Setup progress bar styling."""
        # Base properties
        self.value = self.value
        
        # Color styling
        if self.color:
            self.color = self.color
        else:
            self.color = "#2563eb"  # Blue 600
        
        if self.bgcolor:
            self.bgcolor = self.bgcolor
        else:
            self.bgcolor = "#e5e7eb"  # Grey 200
        
        # Size-specific styling
        if self.size == "sm":
            self.bar_height = 4
        elif self.size == "lg":
            self.bar_height = 12
        else:  # default
            self.bar_height = 8
        
        # Border radius
        self.border_radius = 4


class ModernDataTable(ft.DataTable):
    """Modern data table with Shadcn-inspired design."""
    
    def __init__(
        self,
        columns: List[ft.DataColumn],
        rows: List[ft.DataRow],
        border: Optional[Any] = None,
        border_radius: float = 8,
        heading_row_height: float = 56,
        data_row_min_height: float = 52,
        data_row_max_height: float = 52,
        divider_thickness: float = 1,
        column_spacing: float = 56,
        sort_column_index: Optional[int] = None,
        sort_ascending: bool = True,
        on_select_all: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.columns = columns
        self.rows = rows
        self.border = border
        self.border_radius = border_radius
        self.heading_row_height = heading_row_height
        self.data_row_min_height = data_row_min_height
        self.data_row_max_height = data_row_max_height
        self.divider_thickness = divider_thickness
        self.column_spacing = column_spacing
        self.sort_column_index = sort_column_index
        self.sort_ascending = sort_ascending
        self.on_select_all = on_select_all
        self.theme_manager = theme_manager
        
        self._setup_data_table()
    
    def _setup_data_table(self):
        """Setup data table styling."""
        # Base properties
        self.columns = self.columns
        self.rows = self.rows
        self.border = self.border or ft.border.all(1, "#e5e7eb")  # Grey 200
        self.border_radius = self.border_radius
        self.heading_row_height = self.heading_row_height
        self.data_row_min_height = self.data_row_min_height
        self.data_row_max_height = self.data_row_max_height
        self.divider_thickness = self.divider_thickness
        self.column_spacing = self.column_spacing
        self.sort_column_index = self.sort_column_index
        self.sort_ascending = self.sort_ascending
        self.on_select_all = self.on_select_all
        
        # Modern styling
        self.heading_text_style = ft.TextStyle(
            size=14,
            weight=ft.FontWeight.W_600,
            color="#374151"  # Grey 700
        )
        
        self.data_text_style = ft.TextStyle(
            size=14,
            color="#111827"  # Grey 900
        )


class ModernSidebar(ft.NavigationRail):
    """Modern sidebar with Shadcn-inspired design."""
    
    def __init__(
        self,
        selected_index: int = 0,
        label_type: ft.NavigationRailLabelType = ft.NavigationRailLabelType.ALL,
        min_width: float = 72,
        min_extended_width: float = 256,
        group_alignment: ft.NavigationRailTheme = ft.NavigationRailTheme(),
        destinations: Optional[List[ft.NavigationRailDestination]] = None,
        on_change: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.selected_index = selected_index
        self.label_type = label_type
        self.min_width = min_width
        self.min_extended_width = min_extended_width
        self.group_alignment = group_alignment
        self.destinations = destinations or []
        self.on_change = on_change
        self.theme_manager = theme_manager
        
        self._setup_sidebar()
    
    def _setup_sidebar(self):
        """Setup sidebar styling."""
        # Base properties
        self.selected_index = self.selected_index
        self.label_type = self.label_type
        self.min_width = self.min_width
        self.min_extended_width = self.min_extended_width
        self.group_alignment = self.group_alignment
        self.destinations = self.destinations
        self.on_change = self.on_change
        
        # Modern styling
        self.bgcolor = "#ffffff"  # White
        self.extended = True


class ModernNavigation(ft.NavigationBar):
    """Modern navigation bar with Shadcn-inspired design."""
    
    def __init__(
        self,
        destinations: List[ft.NavigationBarDestination],
        selected_index: int = 0,
        on_change: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.destinations = destinations
        self.selected_index = selected_index
        self.on_change = on_change
        self.theme_manager = theme_manager
        
        self._setup_navigation()
    
    def _setup_navigation(self):
        """Setup navigation styling."""
        # Base properties
        self.destinations = self.destinations
        self.selected_index = self.selected_index
        self.on_change = self.on_change
        
        # Modern styling
        self.bgcolor = "#ffffff"  # White
        self.elevation = 8


class ModernModal(ft.AlertDialog):
    """Modern modal dialog with Shadcn-inspired design."""
    
    def __init__(
        self,
        title: Optional[str] = None,
        content: Optional[ft.Control] = None,
        actions: Optional[List[ft.Control]] = None,
        actions_alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.END,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.title = ft.Text(title) if title else None
        self.content = content
        self.actions = actions or []
        self.actions_alignment = actions_alignment
        self.theme_manager = theme_manager
        
        self._setup_modal()
    
    def _setup_modal(self):
        """Setup modal styling."""
        # Base properties
        self.title = self.title
        self.content = self.content
        self.actions = self.actions
        self.actions_alignment = self.actions_alignment
        
        # Modern styling
        self.bgcolor = "#ffffff"  # White
        self.elevation = 24


class ModernBadge(ft.Container):
    """Modern badge with Shadcn-inspired design."""
    
    def __init__(
        self,
        text: str,
        variant: str = "default",  # default, secondary, destructive, outline
        size: str = "default",     # default, sm, lg
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.text = text
        self.variant = variant
        self.size = size
        self.theme_manager = theme_manager
        
        self._setup_badge()
    
    def _setup_badge(self):
        """Setup badge styling."""
        # Content
        self.content = ft.Text(
            self.text,
            size=self._get_font_size(),
            color=self._get_text_color(),
            weight=ft.FontWeight.W_500
        )
        
        # Container styling
        self.bgcolor = self._get_bg_color()
        self.border = self._get_border()
        self.border_radius = self._get_border_radius()
        self.padding = self._get_padding()
    
    def _get_font_size(self) -> int:
        """Get font size based on badge size."""
        if self.size == "sm":
            return 10
        elif self.size == "lg":
            return 14
        else:
            return 12
    
    def _get_text_color(self) -> str:
        """Get text color based on variant."""
        if self.variant == "default":
            return "#ffffff"  # White
        elif self.variant == "secondary":
            return "#374151"  # Grey 700
        elif self.variant == "destructive":
            return "#ffffff"  # White
        elif self.variant == "outline":
            return "#374151"  # Grey 700
        else:
            return "#ffffff"  # White
    
    def _get_bg_color(self) -> str:
        """Get background color based on variant."""
        if self.variant == "default":
            return "#2563eb"  # Blue 600
        elif self.variant == "secondary":
            return "#f3f4f6"  # Grey 100
        elif self.variant == "destructive":
            return "#dc2626"  # Red 600
        elif self.variant == "outline":
            return "transparent"
        else:
            return "#2563eb"  # Blue 600
    
    def _get_border(self) -> Optional[Any]:
        """Get border based on variant."""
        if self.variant == "outline":
            return ft.border.all(1, "#d1d5db")  # Grey 300
        return None
    
    def _get_border_radius(self) -> float:
        """Get border radius based on size."""
        if self.size == "sm":
            return 4
        elif self.size == "lg":
            return 12
        else:
            return 8
    
    def _get_padding(self) -> Any:
        """Get padding based on size."""
        if self.size == "sm":
            return ft.padding.symmetric(horizontal=6, vertical=2)
        elif self.size == "lg":
            return ft.padding.symmetric(horizontal=12, vertical=6)
        else:
            return ft.padding.symmetric(horizontal=8, vertical=4)


class ModernAvatar(ft.CircleAvatar):
    """Modern avatar with Shadcn-inspired design."""
    
    def __init__(
        self,
        content: Optional[ft.Control] = None,
        foreground_image_url: Optional[str] = None,
        background_image_url: Optional[str] = None,
        radius: Optional[float] = None,
        min_radius: float = 0,
        max_radius: Optional[float] = None,
        size: str = "default",  # sm, default, lg, xl
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.content = content
        self.foreground_image_url = foreground_image_url
        self.background_image_url = background_image_url
        self.radius = radius
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.size = size
        self.theme_manager = theme_manager
        
        self._setup_avatar()
    
    def _setup_avatar(self):
        """Setup avatar styling."""
        # Base properties
        self.content = self.content
        self.foreground_image_url = self.foreground_image_url
        self.background_image_url = self.background_image_url
        self.radius = self.radius or self._get_radius()
        self.min_radius = self.min_radius
        self.max_radius = self.max_radius
        
        # Modern styling
        self.bgcolor = "#e5e7eb"  # Grey 200
        self.color = "#6b7280"  # Grey 600
    
    def _get_radius(self) -> float:
        """Get radius based on size."""
        if self.size == "sm":
            return 16
        elif self.size == "lg":
            return 48
        elif self.size == "xl":
            return 64
        else:  # default
            return 32


class ModernDivider(ft.Divider):
    """Modern divider with Shadcn-inspired design."""
    
    def __init__(
        self,
        height: float = 1,
        thickness: float = 1,
        color: Optional[str] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.height = height
        self.thickness = thickness
        self.color = color or "#e5e7eb"  # Grey 200
        self.theme_manager = theme_manager
        
        self._setup_divider()
    
    def _setup_divider(self):
        """Setup divider styling."""
        # Base properties
        self.height = self.height
        self.thickness = self.thickness
        self.color = self.color


class ModernSpacer(ft.Container):
    """Modern spacer for layout management."""
    
    def __init__(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        size: str = "default",  # xs, sm, default, lg, xl, 2xl
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.width = width
        self.height = height
        self.size = size
        self.theme_manager = theme_manager
        
        self._setup_spacer()
    
    def _setup_spacer(self):
        """Setup spacer styling."""
        # Size-based spacing
        if self.width is None and self.height is None:
            spacing = self._get_spacing()
            self.width = spacing
            self.height = spacing
        else:
            self.width = self.width
            self.height = self.height
    
    def _get_spacing(self) -> float:
        """Get spacing based on size."""
        if self.size == "xs":
            return 4
        elif self.size == "sm":
            return 8
        elif self.size == "lg":
            return 24
        elif self.size == "xl":
            return 32
        elif self.size == "2xl":
            return 48
        else:  # default
            return 16 