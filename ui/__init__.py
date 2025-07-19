"""
UI module for Telegram Analyzer Tool.

This module contains all user interface components and theme management.
"""

from .theme_manager import ThemeManager
from .main_window import MainWindow
from .panels import (
    ContactPanel,
    NumberGeneratorPanel,
    NumberCheckerPanel,
    SettingsPanel
)
from .widgets.modern_components import (
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
    ModernToast,
    ModernBadge,
    ModernAvatar,
    ModernDivider,
    ModernSpacer
)
from .widgets.specialized_widgets import (
    FastFilter,
    ProgressBar,
    NumberRangeInput,
    StatusIndicator
)

__all__ = [
    'ThemeManager',
    'MainWindow',
    'ContactPanel',
    'NumberGeneratorPanel',
    'NumberCheckerPanel',
    'SettingsPanel',
    'FastFilter',
    'ProgressBar',
    'NumberRangeInput',
    'StatusIndicator',
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
    'ModernToast',
    'ModernBadge',
    'ModernAvatar',
    'ModernDivider',
    'ModernSpacer'
]
