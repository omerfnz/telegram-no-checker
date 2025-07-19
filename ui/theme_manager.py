"""
Theme manager for modern UI components.

This module handles theme management with Shadcn-inspired design system.
"""

import flet as ft
from typing import Dict, Any, Optional
from enum import Enum


class ThemeMode(Enum):
    """Theme mode enumeration."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ThemeManager:
    """
    Manages application themes with Shadcn-inspired design system.
    
    This class handles:
    - Light and dark theme switching
    - CSS custom properties management
    - Responsive design tokens
    - Modern color palette
    """
    
    def __init__(self):
        """Initialize the theme manager."""
        self.current_mode = ThemeMode.AUTO
        self._setup_themes()
    
    def _setup_themes(self):
        """Setup theme configurations."""
        # Light theme (Shadcn default)
        self.light_theme = {
            # Base colors
            "--radius": "0.65rem",
            "--background": "oklch(1 0 0)",
            "--foreground": "oklch(0.145 0 0)",
            
            # Card colors
            "--card": "oklch(1 0 0)",
            "--card-foreground": "oklch(0.145 0 0)",
            
            # Popover colors
            "--popover": "oklch(1 0 0)",
            "--popover-foreground": "oklch(0.145 0 0)",
            
            # Primary colors
            "--primary": "oklch(0.205 0 0)",
            "--primary-foreground": "oklch(0.985 0 0)",
            
            # Secondary colors
            "--secondary": "oklch(0.97 0 0)",
            "--secondary-foreground": "oklch(0.205 0 0)",
            
            # Muted colors
            "--muted": "oklch(0.97 0 0)",
            "--muted-foreground": "oklch(0.556 0 0)",
            
            # Accent colors
            "--accent": "oklch(0.97 0 0)",
            "--accent-foreground": "oklch(0.205 0 0)",
            
            # Destructive colors
            "--destructive": "oklch(0.577 0.245 27.325)",
            "--destructive-foreground": "oklch(0.985 0 0)",
            
            # Success colors
            "--success": "oklch(0.646 0.222 41.116)",
            "--success-foreground": "oklch(0.985 0 0)",
            
            # Border and input colors
            "--border": "oklch(0.922 0 0)",
            "--input": "oklch(0.922 0 0)",
            "--ring": "oklch(0.708 0 0)",
            
            # Chart colors
            "--chart-1": "oklch(0.646 0.222 41.116)",
            "--chart-2": "oklch(0.6 0.118 184.704)",
            "--chart-3": "oklch(0.398 0.07 227.392)",
            "--chart-4": "oklch(0.828 0.189 84.429)",
            "--chart-5": "oklch(0.769 0.188 70.08)",
            
            # Sidebar colors
            "--sidebar": "oklch(0.985 0 0)",
            "--sidebar-foreground": "oklch(0.145 0 0)",
            "--sidebar-primary": "oklch(0.205 0 0)",
            "--sidebar-primary-foreground": "oklch(0.985 0 0)",
            "--sidebar-accent": "oklch(0.97 0 0)",
            "--sidebar-accent-foreground": "oklch(0.205 0 0)",
            "--sidebar-border": "oklch(0.922 0 0)",
            "--sidebar-ring": "oklch(0.708 0 0)",
            
            # Spacing and dimensions
            "--spacing-xs": "0.25rem",
            "--spacing-sm": "0.5rem",
            "--spacing-md": "1rem",
            "--spacing-lg": "1.5rem",
            "--spacing-xl": "2rem",
            "--spacing-2xl": "3rem",
            
            # Border radius
            "--radius-sm": "0.375rem",
            "--radius-md": "0.5rem",
            "--radius-lg": "0.75rem",
            "--radius-xl": "1rem",
            
            # Shadows
            "--shadow-sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            "--shadow-md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
            "--shadow-lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
            "--shadow-xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
        }
        
        # Dark theme (Shadcn dark)
        self.dark_theme = {
            # Base colors
            "--radius": "0.65rem",
            "--background": "oklch(0.145 0 0)",
            "--foreground": "oklch(0.985 0 0)",
            
            # Card colors
            "--card": "oklch(0.205 0 0)",
            "--card-foreground": "oklch(0.985 0 0)",
            
            # Popover colors
            "--popover": "oklch(0.205 0 0)",
            "--popover-foreground": "oklch(0.985 0 0)",
            
            # Primary colors
            "--primary": "oklch(0.922 0 0)",
            "--primary-foreground": "oklch(0.205 0 0)",
            
            # Secondary colors
            "--secondary": "oklch(0.269 0 0)",
            "--secondary-foreground": "oklch(0.985 0 0)",
            
            # Muted colors
            "--muted": "oklch(0.269 0 0)",
            "--muted-foreground": "oklch(0.708 0 0)",
            
            # Accent colors
            "--accent": "oklch(0.269 0 0)",
            "--accent-foreground": "oklch(0.985 0 0)",
            
            # Destructive colors
            "--destructive": "oklch(0.704 0.191 22.216)",
            "--destructive-foreground": "oklch(0.985 0 0)",
            
            # Success colors
            "--success": "oklch(0.488 0.243 264.376)",
            "--success-foreground": "oklch(0.985 0 0)",
            
            # Border and input colors
            "--border": "oklch(1 0 0 / 10%)",
            "--input": "oklch(1 0 0 / 15%)",
            "--ring": "oklch(0.556 0 0)",
            
            # Chart colors
            "--chart-1": "oklch(0.488 0.243 264.376)",
            "--chart-2": "oklch(0.696 0.17 162.48)",
            "--chart-3": "oklch(0.769 0.188 70.08)",
            "--chart-4": "oklch(0.627 0.265 303.9)",
            "--chart-5": "oklch(0.645 0.246 16.439)",
            
            # Sidebar colors
            "--sidebar": "oklch(0.205 0 0)",
            "--sidebar-foreground": "oklch(0.985 0 0)",
            "--sidebar-primary": "oklch(0.488 0.243 264.376)",
            "--sidebar-primary-foreground": "oklch(0.985 0 0)",
            "--sidebar-accent": "oklch(0.269 0 0)",
            "--sidebar-accent-foreground": "oklch(0.985 0 0)",
            "--sidebar-border": "oklch(1 0 0 / 10%)",
            "--sidebar-ring": "oklch(0.556 0 0)",
            
            # Spacing and dimensions (same as light)
            "--spacing-xs": "0.25rem",
            "--spacing-sm": "0.5rem",
            "--spacing-md": "1rem",
            "--spacing-lg": "1.5rem",
            "--spacing-xl": "2rem",
            "--spacing-2xl": "3rem",
            
            # Border radius (same as light)
            "--radius-sm": "0.375rem",
            "--radius-md": "0.5rem",
            "--radius-lg": "0.75rem",
            "--radius-xl": "1rem",
            
            # Shadows (adjusted for dark theme)
            "--shadow-sm": "0 1px 2px 0 rgb(0 0 0 / 0.3)",
            "--shadow-md": "0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.4)",
            "--shadow-lg": "0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.4)",
            "--shadow-xl": "0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.4)",
        }
    
    def get_current_theme(self) -> Dict[str, str]:
        """
        Get current theme variables.
        
        Returns:
            Dict[str, str]: Current theme variables
        """
        if self.current_mode == ThemeMode.DARK:
            return self.dark_theme
        else:
            return self.light_theme
    
    def set_theme_mode(self, mode: ThemeMode) -> None:
        """
        Set theme mode.
        
        Args:
            mode: Theme mode to set
        """
        self.current_mode = mode
    
    def set_theme(self, mode: ThemeMode) -> None:
        """
        Set theme mode (alias for set_theme_mode).
        
        Args:
            mode: Theme mode to set
        """
        self.set_theme_mode(mode)
    
    def get_color(self, color_name: str) -> str:
        """
        Get color value by name.
        
        Args:
            color_name: Name of the color variable
            
        Returns:
            str: Color value
        """
        theme = self.get_current_theme()
        return theme.get(f"--{color_name}", "")
    
    def get_spacing(self, size: str) -> str:
        """
        Get spacing value by size.
        
        Args:
            size: Size name (xs, sm, md, lg, xl, 2xl)
            
        Returns:
            str: Spacing value
        """
        theme = self.get_current_theme()
        return theme.get(f"--spacing-{size}", "1rem")
    
    def get_radius(self, size: str) -> str:
        """
        Get border radius value by size.
        
        Args:
            size: Size name (sm, md, lg, xl)
            
        Returns:
            str: Border radius value
        """
        theme = self.get_current_theme()
        return theme.get(f"--radius-{size}", "0.5rem")
    
    def get_shadow(self, size: str) -> str:
        """
        Get shadow value by size.
        
        Args:
            size: Size name (sm, md, lg, xl)
            
        Returns:
            str: Shadow value
        """
        theme = self.get_current_theme()
        return theme.get(f"--shadow-{size}", "")
    
    def apply_theme_to_page(self, page: ft.Page) -> None:
        """
        Apply current theme to Flet page.
        
        Args:
            page: Flet page to apply theme to
        """
        theme = self.get_current_theme()
        
        # Apply theme colors
        page.theme_mode = ft.ThemeMode.DARK if self.current_mode == ThemeMode.DARK else ft.ThemeMode.LIGHT
        
        # Set custom theme properties
        page.theme = ft.Theme(
            color_scheme_seed="#2563eb" if self.current_mode == ThemeMode.LIGHT else "#64748b",  # Blue/Blue Grey
            use_material3=True,
            # visual_density parameter removed - not available in current Flet version
        )
    
    def get_responsive_breakpoints(self) -> Dict[str, int]:
        """
        Get responsive breakpoints for different screen sizes.
        
        Returns:
            Dict[str, int]: Breakpoint values
        """
        return {
            "xs": 0,      # Extra small devices (phones)
            "sm": 576,    # Small devices (tablets)
            "md": 768,    # Medium devices (small laptops)
            "lg": 992,    # Large devices (desktops)
            "xl": 1200,   # Extra large devices (large desktops)
            "2xl": 1400,  # 2X large devices (ultra-wide)
        }
    
    def is_mobile(self, width: float) -> bool:
        """
        Check if screen width is mobile size.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            bool: True if mobile size
        """
        return width < 768
    
    def is_tablet(self, width: float) -> bool:
        """
        Check if screen width is tablet size.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            bool: True if tablet size
        """
        return 768 <= width < 992
    
    def is_desktop(self, width: float) -> bool:
        """
        Check if screen width is desktop size.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            bool: True if desktop size
        """
        return width >= 992
    
    def get_responsive_padding(self, width: float) -> float:
        """
        Get responsive padding based on screen width.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            float: Padding value
        """
        if self.is_mobile(width):
            return 16.0
        elif self.is_tablet(width):
            return 24.0
        else:
            return 32.0
    
    def get_responsive_font_size(self, width: float, base_size: float = 14.0) -> float:
        """
        Get responsive font size based on screen width.
        
        Args:
            width: Screen width in pixels
            base_size: Base font size
            
        Returns:
            float: Font size value
        """
        if self.is_mobile(width):
            return base_size * 0.9
        elif self.is_tablet(width):
            return base_size
        else:
            return base_size * 1.1 