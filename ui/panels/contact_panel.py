"""
Contact Management Panel for Telegram Analyzer Tool.

This module contains the contact management interface with modern design.
"""

import flet as ft
from typing import Optional, Dict, Any
from ..theme_manager import ThemeManager
from ..widgets import ModernButton, ModernCard, ModernInput


class ContactPanel:
    """
    Contact management panel with modern design.
    
    This panel provides:
    - Contact list display
    - Add/Edit/Delete contacts
    - Search and filter functionality
    - Bulk import/export
    """

    def __init__(self, theme_manager: ThemeManager, core_modules: Dict[str, Any]):
        """
        Initialize the contact panel.
        
        Args:
            theme_manager: Theme manager instance
            core_modules: Core modules dictionary
        """
        self.theme_manager = theme_manager
        self.core_modules = core_modules
        self.contact_manager = core_modules.get('contact_manager')
        
        # UI components
        self.contact_list = None
        self.search_input = None
        self.add_button = None
        self.import_button = None
        self.export_button = None
        
        # State
        self.contacts = []
        self.filtered_contacts = []
        
        # Build UI
        self._build_ui()
        self._load_contacts()

    def _build_ui(self):
        """Build the panel UI."""
        # Search bar
        self.search_input = ModernInput(
            hint_text="Search contacts...",
            on_change=self._on_search_change,
            theme_manager=self.theme_manager
        )

        # Action buttons
        self.add_button = ModernButton(
            text="Add Contact",
            on_click=self._on_add_contact,
            variant="primary",
            theme_manager=self.theme_manager
        )

        self.import_button = ModernButton(
            text="Import",
            on_click=self._on_import_contacts,
            variant="secondary",
            theme_manager=self.theme_manager
        )

        self.export_button = ModernButton(
            text="Export",
            on_click=self._on_export_contacts,
            variant="secondary",
            theme_manager=self.theme_manager
        )

        # Contact list
        self.contact_list = ft.ListView(
            spacing=8,
            padding=ft.padding.all(16),
            expand=True
        )

        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Contact Management",
                        size=24,
                        weight=ft.FontWeight.W_700,
                        color=self.theme_manager.get_color("foreground")
                    ),
                    ft.Icon(
                        name="contacts",
                        size=24,
                        color=self.theme_manager.get_color("primary")
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.all(16),
            border=ft.border.only(bottom=ft.border.BorderSide(1, self.theme_manager.get_color("border")))
        )

        # Search and actions
        search_actions = ft.Container(
            content=ft.Row(
                [
                    ft.Container(content=self.search_input, expand=True),
                    self.add_button,
                    self.import_button,
                    self.export_button
                ],
                spacing=12
            ),
            padding=ft.padding.all(16)
        )

        # Stats card
        stats_card = self._create_stats_card()

        # Main content
        content = ft.Column(
            [
                header,
                search_actions,
                stats_card,
                ft.Container(
                    content=self.contact_list,
                    expand=True,
                    bgcolor=self.theme_manager.get_color("background")
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

    def _create_stats_card(self) -> ft.Container:
        """Create statistics card."""
        stats_content = ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "0",
                                size=24,
                                weight=ft.FontWeight.W_700,
                                color=self.theme_manager.get_color("primary")
                            ),
                            ft.Text(
                                "Total Contacts",
                                size=12,
                                color=self.theme_manager.get_color("muted_foreground")
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.all(16),
                    bgcolor=self.theme_manager.get_color("card"),
                    border_radius=8,
                    expand=True
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "0",
                                size=24,
                                weight=ft.FontWeight.W_700,
                                color=self.theme_manager.get_color("success") or "#22c55e"
                            ),
                            ft.Text(
                                "Valid",
                                size=12,
                                color=self.theme_manager.get_color("muted_foreground")
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.all(16),
                    bgcolor=self.theme_manager.get_color("card"),
                    border_radius=8,
                    expand=True
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "0",
                                size=24,
                                weight=ft.FontWeight.W_700,
                                color=self.theme_manager.get_color("destructive") or "#ef4444"
                            ),
                            ft.Text(
                                "Invalid",
                                size=12,
                                color=self.theme_manager.get_color("muted_foreground")
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.all(16),
                    bgcolor=self.theme_manager.get_color("card"),
                    border_radius=8,
                    expand=True
                )
            ],
            spacing=12
        )

        return ft.Container(
            content=stats_content,
            padding=ft.padding.symmetric(horizontal=16, vertical=8)
        )

    def _load_contacts(self):
        """Load contacts from database."""
        try:
            if self.contact_manager:
                self.contacts = self.contact_manager.get_all_contacts(limit=100)
                self.filtered_contacts = self.contacts.copy()
                # Don't update list immediately - wait for page to be ready
                # self._update_contact_list()
                # self._update_stats()
        except Exception as e:
            print(f"Error loading contacts: {e}")
    
    def load_contacts_after_page_ready(self):
        """Load contacts after page is ready."""
        try:
            self._update_contact_list()
            self._update_stats()
        except Exception as e:
            print(f"Error updating contact list: {e}")

    def _update_contact_list(self):
        """Update the contact list display."""
        self.contact_list.controls.clear()
        
        if not self.filtered_contacts:
            # Empty state
            empty_state = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            name="contacts_outlined",
                            size=64,
                            color=self.theme_manager.get_color("muted_foreground")
                        ),
                        ft.Text(
                            "No contacts found",
                            size=16,
                            color=self.theme_manager.get_color("muted_foreground")
                        ),
                        ft.Text(
                            "Add your first contact to get started",
                            size=12,
                            color=self.theme_manager.get_color("muted_foreground")
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8
                ),
                padding=ft.padding.all(32),
                alignment=ft.alignment.center
            )
            self.contact_list.controls.append(empty_state)
        else:
            # Contact cards
            for contact in self.filtered_contacts:
                contact_card = self._create_contact_card(contact)
                self.contact_list.controls.append(contact_card)

        self.contact_list.update()

    def _create_contact_card(self, contact) -> ft.Container:
        """Create a contact card."""
        # Status indicator
        status_color = "#22c55e" if contact.is_valid else "#ef4444"  # Green/Red
        status_text = "Valid" if contact.is_valid else "Invalid"
        
        # Action buttons
        edit_button = ModernButton(
            text="Edit",
            on_click=lambda e, c=contact: self._on_edit_contact(c),
            variant="ghost",
            size="small"
        )
        
        delete_button = ModernButton(
            text="Delete",
            on_click=lambda e, c=contact: self._on_delete_contact(c),
            variant="ghost",
            size="small"
        )

        card_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    contact.name or "Unnamed",
                                    size=16,
                                    weight=ft.FontWeight.W_600,
                                    color=self.theme_manager.get_color("foreground")
                                ),
                                ft.Text(
                                    contact.phone_number,
                                    size=14,
                                    color=self.theme_manager.get_color("muted_foreground")
                                )
                            ],
                            expand=True
                        ),
                        ft.Container(
                            content=ft.Text(
                                status_text,
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
                ft.Row(
                    [
                        edit_button,
                        delete_button
                    ],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            spacing=8
        )

        return ModernCard(
            content=card_content,
            padding=ft.padding.all(16),
            theme_manager=self.theme_manager
        )

    def _update_stats(self):
        """Update statistics display."""
        total = len(self.contacts)
        valid = len([c for c in self.contacts if c.is_valid])
        invalid = total - valid
        
        # Update stats in the card (simplified for now)
        pass

    def _on_search_change(self, e):
        """Handle search input change."""
        query = e.control.value.lower()
        
        if not query:
            self.filtered_contacts = self.contacts.copy()
        else:
            self.filtered_contacts = [
                contact for contact in self.contacts
                if query in contact.name.lower() or query in contact.phone_number.lower()
            ]
        
        self._update_contact_list()

    def _on_add_contact(self, e):
        """Handle add contact button click."""
        # TODO: Implement add contact dialog
        print("Add contact clicked")

    def _on_edit_contact(self, contact):
        """Handle edit contact."""
        # TODO: Implement edit contact dialog
        print(f"Edit contact: {contact.name}")

    def _on_delete_contact(self, contact):
        """Handle delete contact."""
        # TODO: Implement delete confirmation
        print(f"Delete contact: {contact.name}")

    def _on_import_contacts(self, e):
        """Handle import contacts."""
        # TODO: Implement import dialog
        print("Import contacts clicked")

    def _on_export_contacts(self, e):
        """Handle export contacts."""
        # TODO: Implement export dialog
        print("Export contacts clicked")

    def get_content(self) -> ft.Control:
        """Get the panel content."""
        return self.content
    
    def rebuild_with_theme(self):
        """Rebuild UI with current theme."""
        self._build_ui()
        # Don't update lists during theme change - they will be updated when panel is shown
