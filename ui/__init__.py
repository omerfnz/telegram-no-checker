"""
UI Module for Telegram Analyzer Tool.

This module contains all UI-related components including:
- Main window
- Panels
- Widgets
- Theme management
"""

from .main_window import MainWindow
from .theme_manager import ThemeManager, ThemeMode

from .panels import (
    ContactPanel,
    NumberGeneratorPanel,
    NumberCheckerPanel,
    SettingsPanel
)

from .widgets import (
    ModernButton,
    ModernCard,
    ModernInput,
    ModernSelect,
    ModernCheckbox,
    ModernSwitch,
    ModernSlider,
    ModernProgressBar,
    ModernDataTable,
    ModernSidebar,
    ModernNavigation,
    ModernModal,
    ModernBadge,
    ModernAvatar,
    ModernDivider,
    ModernSpacer,
    StatusIndicator,
    NumberRangeInput,
    FastFilter,
    ProgressBar,
    FileUploader,
    CountrySelector,
    OperatorSelector,
    PatternInput,
    SessionCard,
    StatisticsCard,
    SnackbarManager,
    SnackbarType
)

__all__ = [
    # Main Components
    'MainWindow',
    'ThemeManager',
    'ThemeMode',
    
    # Panels
    'ContactPanel',
    'NumberGeneratorPanel',
    'NumberCheckerPanel',
    'SettingsPanel',
    
    # Modern Components
    'ModernButton',
    'ModernCard',
    'ModernInput',
    'ModernSelect',
    'ModernCheckbox',
    'ModernSwitch',
    'ModernSlider',
    'ModernProgressBar',
    'ModernDataTable',
    'ModernSidebar',
    'ModernNavigation',
    'ModernModal',
    'ModernBadge',
    'ModernAvatar',
    'ModernDivider',
    'ModernSpacer',
    
    # Specialized Widgets
    'StatusIndicator',
    'NumberRangeInput',
    'FastFilter',
    'ProgressBar',
    'FileUploader',
    'CountrySelector',
    'OperatorSelector',
    'PatternInput',
    'SessionCard',
    'StatisticsCard',
    
    # Snackbar System
    'SnackbarManager',
    'SnackbarType'
]
