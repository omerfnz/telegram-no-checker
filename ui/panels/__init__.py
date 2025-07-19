"""
UI panels for Telegram Analyzer Tool.

This module contains main application panels and layouts.
"""

from .contact_panel import ContactPanel
from .number_generator_panel import NumberGeneratorPanel
from .number_checker_panel import NumberCheckerPanel
from .settings_panel import SettingsPanel

__all__ = [
    'ContactPanel',
    'NumberGeneratorPanel',
    'NumberCheckerPanel',
    'SettingsPanel'
]
