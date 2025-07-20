import unittest
import tempfile
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from services.database_service import DatabaseService, DatabaseException
from models.phone_number import PhoneNumber
from models.validation_result import ValidationResult
from models.app_settings import AppSettings


class TestDatabaseService(unittest.TestCase):
    """Test cases for DatabaseService class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Initialize database service
        self.db_service = DatabaseService(self.db_path)
        
        # Create test phone numbers
        self.test_phone1 = PhoneNumber(
            number="+90 532 123 45 67",
            name="Test User 1",
            is_valid=True,
            checked_date=datetime.now(),
            operator_code="532"
        )
        
        self.test_phone2 = PhoneNumber(
            number="+90 555 987 65 43",
            name="Test User 2",
            is_valid=False,
            checked_date=datetime.now(),
            operator_code="555"
        )
        
        self.test_phone3 = PhoneNumber(
            number="+90 501 111 22 33",
            name=None,
            is_valid=None,
            checked_date=None,
            operator_code="501"
        )
    
    def tearDown(self):
        """Clean up after each test method."""
        # Close database service
        self.db_service.close()
        
        # Remove temporary database file
        try:
            os.unlink(self.db_path)
        except OSError:
            pass
    
    def test_database_initialization(self):
        """Test database initialization and schema creation."""
        # Database should be initialized and file should exist
        self.assertTrue(Path(self.db_path).exists())
        
        # Test with invalid path should raise exception
        with self.assertRaises((DatabaseException, OSError, PermissionError)):
            DatabaseService("Z:\\nonexistent\\invalid\\path\\database.db")
    
    def test_save_and_get_phone_number(self):
        """Test saving and retrieving phone numbers."""
        # Save phone number
        result = self.db_service.save_phone_number(self.test_phone1)
        self.assertTrue(result)
        
        # Retrieve phone number
        retrieved = self.db_service.get_phone_number(self.test_phone1.number)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.number, self.test_phone1.number)
        self.assertEqual(retrieved.name, self.test_phone1.name)
        self.assertEqual(retrieved.is_valid, self.test_phone1.is_valid)
        self.assertEqual(retrieved.operator_code, self.test_phone1.operator_code)
    
    def test_save_phone_number_update(self):
        """Test updating existing phone number."""
        # Save initial phone number
        self.db_service.save_phone_number(self.test_phone1)
        
        # Update the phone number
        updated_phone = PhoneNumber(
            number=self.test_phone1.number,
            name="Updated Name",
            is_valid=False,
            checked_date=datetime.now(),
            operator_code=self.test_phone1.operator_code
        )
        
        result = self.db_service.save_phone_number(updated_phone)
        self.assertTrue(result)
        
        # Retrieve and verify update
        retrieved = self.db_service.get_phone_number(self.test_phone1.number)
        self.assertEqual(retrieved.name, "Updated Name")
        self.assertEqual(retrieved.is_valid, False)
    
    def test_get_nonexistent_phone_number(self):
        """Test retrieving non-existent phone number."""
        result = self.db_service.get_phone_number("+90 999 999 99 99")
        self.assertIsNone(result)
    
    def test_is_number_checked(self):
        """Test checking if number has been validated."""
        # Initially not checked
        self.assertFalse(self.db_service.is_number_checked(self.test_phone1.number))
        
        # Save checked phone number
        self.db_service.save_phone_number(self.test_phone1)
        self.assertTrue(self.db_service.is_number_checked(self.test_phone1.number))
        
        # Save unchecked phone number
        self.db_service.save_phone_number(self.test_phone3)
        self.assertFalse(self.db_service.is_number_checked(self.test_phone3.number))
    
    def test_get_valid_and_invalid_numbers(self):
        """Test retrieving valid and invalid phone numbers."""
        # Save test phone numbers
        self.db_service.save_phone_number(self.test_phone1)  # Valid
        self.db_service.save_phone_number(self.test_phone2)  # Invalid
        self.db_service.save_phone_number(self.test_phone3)  # Unchecked
        
        # Get valid numbers
        valid_numbers = self.db_service.get_all_valid_numbers()
        self.assertEqual(len(valid_numbers), 1)
        self.assertEqual(valid_numbers[0].number, self.test_phone1.number)
        
        # Get invalid numbers
        invalid_numbers = self.db_service.get_all_invalid_numbers()
        self.assertEqual(len(invalid_numbers), 1)
        self.assertEqual(invalid_numbers[0].number, self.test_phone2.number)
    
    def test_search_numbers(self):
        """Test searching phone numbers by number or name."""
        # Save test phone numbers
        self.db_service.save_phone_number(self.test_phone1)
        self.db_service.save_phone_number(self.test_phone2)
        
        # Search by number
        results = self.db_service.search_numbers("532")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].number, self.test_phone1.number)
        
        # Search by name
        results = self.db_service.search_numbers("Test User 1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].number, self.test_phone1.number)
        
        # Search with no results
        results = self.db_service.search_numbers("nonexistent")
        self.assertEqual(len(results), 0)
        
        # Search with empty query
        results = self.db_service.search_numbers("")
        self.assertEqual(len(results), 0)
    
    def test_get_all_numbers(self):
        """Test retrieving all phone numbers."""
        # Initially empty
        all_numbers = self.db_service.get_all_numbers()
        self.assertEqual(len(all_numbers), 0)
        
        # Save test phone numbers
        self.db_service.save_phone_number(self.test_phone1)
        self.db_service.save_phone_number(self.test_phone2)
        
        # Get all numbers
        all_numbers = self.db_service.get_all_numbers()
        self.assertEqual(len(all_numbers), 2)
        
        # Test with limit
        limited_numbers = self.db_service.get_all_numbers(limit=1)
        self.assertEqual(len(limited_numbers), 1)
    
    def test_validation_log_operations(self):
        """Test validation log saving and retrieval."""
        # First save the phone number (required for foreign key constraint)
        self.db_service.save_phone_number(self.test_phone1)
        
        # Create validation result
        validation_result = ValidationResult(
            phone_number=self.test_phone1,
            is_telegram_registered=True,
            validation_date=datetime.now(),
            response_time=2.5,
            error_message=None
        )
        
        # Save validation log
        result = self.db_service.save_validation_log(validation_result)
        self.assertTrue(result)
        
        # Retrieve validation logs
        logs = self.db_service.get_validation_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['phone_number'], self.test_phone1.number)
        self.assertEqual(logs[0]['validation_result'], True)
        self.assertEqual(logs[0]['response_time'], 2.5)
        
        # Retrieve logs for specific phone number
        phone_logs = self.db_service.get_validation_logs(phone_number=self.test_phone1.number)
        self.assertEqual(len(phone_logs), 1)
    
    def test_settings_operations(self):
        """Test settings saving and retrieval."""
        # Save setting
        result = self.db_service.save_setting("test_key", "test_value")
        self.assertTrue(result)
        
        # Get setting
        value = self.db_service.get_setting("test_key")
        self.assertEqual(value, "test_value")
        
        # Get non-existent setting with default
        value = self.db_service.get_setting("nonexistent", "default")
        self.assertEqual(value, "default")
        
        # Get non-existent setting without default
        value = self.db_service.get_setting("nonexistent")
        self.assertIsNone(value)
    
    def test_app_settings_operations(self):
        """Test application settings saving and loading."""
        # Create test settings
        test_settings = AppSettings(
            telegram_api_id="123456",
            telegram_api_hash="abcdef123456789",
            parallel_threads=3,
            rate_limit_min=2,
            rate_limit_max=5,
            dark_mode=True
        )
        
        # Save settings
        result = self.db_service.save_app_settings(test_settings)
        self.assertTrue(result)
        
        # Load settings
        loaded_settings = self.db_service.load_app_settings()
        self.assertEqual(loaded_settings.telegram_api_id, test_settings.telegram_api_id)
        self.assertEqual(loaded_settings.telegram_api_hash, test_settings.telegram_api_hash)
        self.assertEqual(loaded_settings.parallel_threads, test_settings.parallel_threads)
        self.assertEqual(loaded_settings.dark_mode, test_settings.dark_mode)
    
    def test_statistics(self):
        """Test database statistics retrieval."""
        # Save test data
        self.db_service.save_phone_number(self.test_phone1)  # Valid
        self.db_service.save_phone_number(self.test_phone2)  # Invalid
        self.db_service.save_phone_number(self.test_phone3)  # Unchecked
        
        # Save validation log
        validation_result = ValidationResult(
            phone_number=self.test_phone1,
            is_telegram_registered=True,
            validation_date=datetime.now(),
            response_time=1.5
        )
        self.db_service.save_validation_log(validation_result)
        
        # Get statistics
        stats = self.db_service.get_statistics()
        
        self.assertEqual(stats['total_numbers'], 3)
        self.assertEqual(stats['valid_numbers'], 1)
        self.assertEqual(stats['invalid_numbers'], 1)
        self.assertEqual(stats['unchecked_numbers'], 1)
        self.assertEqual(stats['total_validations'], 1)
        self.assertEqual(stats['avg_response_time'], 1.5)
    
    def test_batch_save_phone_numbers(self):
        """Test batch saving of phone numbers."""
        phones = [self.test_phone1, self.test_phone2, self.test_phone3]
        
        # Batch save
        saved_count = self.db_service.batch_save_phone_numbers(phones)
        self.assertEqual(saved_count, 3)
        
        # Verify all were saved
        all_numbers = self.db_service.get_all_numbers()
        self.assertEqual(len(all_numbers), 3)
        
        # Test with empty list
        saved_count = self.db_service.batch_save_phone_numbers([])
        self.assertEqual(saved_count, 0)
    
    def test_delete_phone_number(self):
        """Test deleting phone numbers."""
        # Save phone number
        self.db_service.save_phone_number(self.test_phone1)
        
        # Verify it exists
        retrieved = self.db_service.get_phone_number(self.test_phone1.number)
        self.assertIsNotNone(retrieved)
        
        # Delete phone number
        result = self.db_service.delete_phone_number(self.test_phone1.number)
        self.assertTrue(result)
        
        # Verify it's deleted
        retrieved = self.db_service.get_phone_number(self.test_phone1.number)
        self.assertIsNone(retrieved)
        
        # Try to delete non-existent number
        result = self.db_service.delete_phone_number("+90 999 999 99 99")
        self.assertFalse(result)
    
    def test_clear_all_data(self):
        """Test clearing all data from database."""
        # Save test data
        self.db_service.save_phone_number(self.test_phone1)
        self.db_service.save_phone_number(self.test_phone2)
        self.db_service.save_setting("test_setting", "value")
        
        # Clear all data
        result = self.db_service.clear_all_data()
        self.assertTrue(result)
        
        # Verify phone data is cleared
        all_numbers = self.db_service.get_all_numbers()
        self.assertEqual(len(all_numbers), 0)
        
        # Verify settings are preserved
        setting_value = self.db_service.get_setting("test_setting")
        self.assertEqual(setting_value, "value")
    
    def test_database_error_handling(self):
        """Test database error handling."""
        # Test with corrupted database path
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            
            # Should handle error gracefully
            result = self.db_service.save_phone_number(self.test_phone1)
            self.assertFalse(result)
            
            retrieved = self.db_service.get_phone_number(self.test_phone1.number)
            self.assertIsNone(retrieved)
    
    def test_concurrent_access(self):
        """Test thread-safe database operations."""
        import threading
        import time
        
        results = []
        
        def save_phone(phone_num):
            phone = PhoneNumber(
                number=f"+90 532 {phone_num:03d} {phone_num:02d} {phone_num:02d}",
                name=f"User {phone_num}",
                is_valid=True,
                checked_date=datetime.now(),
                operator_code="532"
            )
            result = self.db_service.save_phone_number(phone)
            results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=save_phone, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations succeeded
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results))
        
        # Verify all numbers were saved
        all_numbers = self.db_service.get_all_numbers()
        self.assertEqual(len(all_numbers), 10)


if __name__ == '__main__':
    unittest.main()