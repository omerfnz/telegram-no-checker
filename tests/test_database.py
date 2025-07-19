"""
Tests for database operations.

This module contains unit tests for the DatabaseManager class.
"""

import unittest
import tempfile
import os
from datetime import datetime
from pathlib import Path

from data.database import DatabaseManager
from data.models import Contact, NumberRecord, CheckSession


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary database file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_telegram_analyzer.db")
        self.db_manager = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary database file
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_database_initialization(self):
        """Test database initialization."""
        # Check if database file was created
        self.assertTrue(os.path.exists(self.db_path))
        
        # Check if tables were created
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check contacts table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
            self.assertIsNotNone(cursor.fetchone())
            
            # Check number_records table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='number_records'")
            self.assertIsNotNone(cursor.fetchone())
            
            # Check check_sessions table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='check_sessions'")
            self.assertIsNotNone(cursor.fetchone())
    
    def test_contact_crud_operations(self):
        """Test contact CRUD operations."""
        # Create a test contact
        contact = Contact(
            name="Test User",
            phone_number="+905551234567",
            is_valid=True,
            notes="Test contact"
        )
        
        # Test create
        contact_id = self.db_manager.create_contact(contact)
        self.assertIsNotNone(contact_id)
        self.assertGreater(contact_id, 0)
        
        # Test get by ID
        retrieved_contact = self.db_manager.get_contact(contact_id)
        self.assertIsNotNone(retrieved_contact)
        self.assertEqual(retrieved_contact.name, "Test User")
        self.assertEqual(retrieved_contact.phone_number, "+905551234567")
        self.assertTrue(retrieved_contact.is_valid)
        self.assertEqual(retrieved_contact.notes, "Test contact")
        
        # Test get by phone number
        retrieved_contact = self.db_manager.get_contact_by_phone("+905551234567")
        self.assertIsNotNone(retrieved_contact)
        self.assertEqual(retrieved_contact.name, "Test User")
        
        # Test update
        retrieved_contact.name = "Updated User"
        retrieved_contact.is_valid = False
        success = self.db_manager.update_contact(retrieved_contact)
        self.assertTrue(success)
        
        # Verify update
        updated_contact = self.db_manager.get_contact(contact_id)
        self.assertEqual(updated_contact.name, "Updated User")
        self.assertFalse(updated_contact.is_valid)
        
        # Test search
        search_results = self.db_manager.search_contacts("Updated")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].name, "Updated User")
        
        # Test delete
        success = self.db_manager.delete_contact(contact_id)
        self.assertTrue(success)
        
        # Verify deletion
        deleted_contact = self.db_manager.get_contact(contact_id)
        self.assertIsNone(deleted_contact)
    
    def test_number_record_crud_operations(self):
        """Test number record CRUD operations."""
        # Create a test number record
        number_record = NumberRecord(
            country_code="+90",
            operator_prefix="555",
            phone_number="1234567",
            full_number="+905551234567",
            is_valid=True,
            is_checked=True,
            check_count=1,
            notes="Test number"
        )
        
        # Test create
        record_id = self.db_manager.create_number_record(number_record)
        self.assertIsNotNone(record_id)
        self.assertGreater(record_id, 0)
        
        # Test get by ID
        retrieved_record = self.db_manager.get_number_record(record_id)
        self.assertIsNotNone(retrieved_record)
        self.assertEqual(retrieved_record.country_code, "+90")
        self.assertEqual(retrieved_record.operator_prefix, "555")
        self.assertEqual(retrieved_record.phone_number, "1234567")
        self.assertEqual(retrieved_record.full_number, "+905551234567")
        self.assertTrue(retrieved_record.is_valid)
        self.assertTrue(retrieved_record.is_checked)
        self.assertEqual(retrieved_record.check_count, 1)
        self.assertEqual(retrieved_record.notes, "Test number")
        
        # Test get by full number
        retrieved_record = self.db_manager.get_number_record_by_full_number("+905551234567")
        self.assertIsNotNone(retrieved_record)
        self.assertEqual(retrieved_record.country_code, "+90")
        
        # Test update
        retrieved_record.is_valid = False
        retrieved_record.check_count = 2
        success = self.db_manager.update_number_record(retrieved_record)
        self.assertTrue(success)
        
        # Verify update
        updated_record = self.db_manager.get_number_record(record_id)
        self.assertFalse(updated_record.is_valid)
        self.assertEqual(updated_record.check_count, 2)
        
        # Test bulk update
        records_to_update = [updated_record]
        updated_count = self.db_manager.bulk_update_number_records(records_to_update)
        self.assertEqual(updated_count, 1)
        
        # Test delete
        success = self.db_manager.delete_number_record(record_id)
        self.assertTrue(success)
    
    def test_check_session_crud_operations(self):
        """Test check session CRUD operations."""
        # Create a test check session
        session = CheckSession(
            session_name="Test Session",
            country_code="+90",
            operator_prefixes=["555", "542"],
            total_numbers=1000,
            checked_numbers=500,
            valid_numbers=200,
            invalid_numbers=300,
            status="running"
        )
        
        # Test create
        session_id = self.db_manager.create_check_session(session)
        self.assertIsNotNone(session_id)
        self.assertGreater(session_id, 0)
        
        # Test get by ID
        retrieved_session = self.db_manager.get_check_session(session_id)
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_name, "Test Session")
        self.assertEqual(retrieved_session.country_code, "+90")
        self.assertEqual(retrieved_session.operator_prefixes, ["555", "542"])
        self.assertEqual(retrieved_session.total_numbers, 1000)
        self.assertEqual(retrieved_session.checked_numbers, 500)
        self.assertEqual(retrieved_session.valid_numbers, 200)
        self.assertEqual(retrieved_session.invalid_numbers, 300)
        self.assertEqual(retrieved_session.status, "running")
        
        # Test update
        retrieved_session.status = "completed"
        retrieved_session.checked_numbers = 1000
        retrieved_session.end_time = datetime.now()
        success = self.db_manager.update_check_session(retrieved_session)
        self.assertTrue(success)
        
        # Verify update
        updated_session = self.db_manager.get_check_session(session_id)
        self.assertEqual(updated_session.status, "completed")
        self.assertEqual(updated_session.checked_numbers, 1000)
        self.assertIsNotNone(updated_session.end_time)
        
        # Test get running sessions
        running_sessions = self.db_manager.get_running_sessions()
        self.assertEqual(len(running_sessions), 0)  # Should be 0 since we changed status to completed
        
        # Test delete
        success = self.db_manager.delete_check_session(session_id)
        self.assertTrue(success)
        
        # Verify deletion
        deleted_session = self.db_manager.get_check_session(session_id)
        self.assertIsNone(deleted_session)
    
    def test_get_unchecked_numbers(self):
        """Test getting unchecked numbers."""
        # Create some test number records
        records = [
            NumberRecord(
                country_code="+90",
                operator_prefix="555",
                phone_number="1234567",
                full_number="+905551234567",
                is_checked=False
            ),
            NumberRecord(
                country_code="+90",
                operator_prefix="555",
                phone_number="1234568",
                full_number="+905551234568",
                is_checked=True
            ),
            NumberRecord(
                country_code="+90",
                operator_prefix="542",
                phone_number="1234567",
                full_number="+905421234567",
                is_checked=False
            )
        ]
        
        # Insert records
        for record in records:
            self.db_manager.create_number_record(record)
        
        # Test getting unchecked numbers for specific country and operator
        unchecked_numbers = self.db_manager.get_unchecked_numbers("+90", "555")
        self.assertEqual(len(unchecked_numbers), 1)
        self.assertEqual(unchecked_numbers[0].phone_number, "1234567")
        
        # Test getting unchecked numbers for different operator
        unchecked_numbers = self.db_manager.get_unchecked_numbers("+90", "542")
        self.assertEqual(len(unchecked_numbers), 1)
        self.assertEqual(unchecked_numbers[0].phone_number, "1234567")
    
    def test_get_statistics(self):
        """Test getting database statistics."""
        # Create some test data
        contact1 = Contact(name="User1", phone_number="+905551234567", is_valid=True)
        contact2 = Contact(name="User2", phone_number="+905551234568", is_valid=False)
        contact3 = Contact(name="User3", phone_number="+905551234569", is_valid=None)
        
        self.db_manager.create_contact(contact1)
        self.db_manager.create_contact(contact2)
        self.db_manager.create_contact(contact3)
        
        number_record1 = NumberRecord(
            country_code="+90",
            operator_prefix="555",
            phone_number="1234567",
            full_number="+905551234567",
            is_valid=True,
            is_checked=True
        )
        number_record2 = NumberRecord(
            country_code="+90",
            operator_prefix="555",
            phone_number="1234568",
            full_number="+905551234568",
            is_valid=False,
            is_checked=True
        )
        number_record3 = NumberRecord(
            country_code="+90",
            operator_prefix="555",
            phone_number="1234569",
            full_number="+905551234569",
            is_checked=False
        )
        
        self.db_manager.create_number_record(number_record1)
        self.db_manager.create_number_record(number_record2)
        self.db_manager.create_number_record(number_record3)
        
        session = CheckSession(
            session_name="Test Session",
            country_code="+90",
            operator_prefixes=["555"],
            total_numbers=100,
            checked_numbers=50,
            valid_numbers=20,
            invalid_numbers=30,
            status="running"
        )
        
        self.db_manager.create_check_session(session)
        
        # Get statistics
        stats = self.db_manager.get_statistics()
        
        # Verify contact statistics
        self.assertEqual(stats['contacts']['total'], 3)
        self.assertEqual(stats['contacts']['valid'], 1)
        self.assertEqual(stats['contacts']['invalid'], 1)
        self.assertEqual(stats['contacts']['unchecked'], 1)
        
        # Verify number record statistics
        self.assertEqual(stats['number_records']['total'], 3)
        self.assertEqual(stats['number_records']['checked'], 2)
        self.assertEqual(stats['number_records']['unchecked'], 1)
        self.assertEqual(stats['number_records']['valid'], 1)
        self.assertEqual(stats['number_records']['invalid'], 1)
        
        # Verify session statistics
        self.assertEqual(stats['sessions']['total'], 1)
        self.assertEqual(stats['sessions']['running'], 1)


if __name__ == '__main__':
    unittest.main() 