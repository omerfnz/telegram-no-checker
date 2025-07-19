"""
Tests for core modules.

This module contains unit tests for core functionality.
"""

import unittest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from core.telegram_client import TelegramClientManager
from core.anti_robot_driver import AntiRobotDriver, RateLimitConfig
from core.number_checker import NumberChecker
from data.database import DatabaseManager
from data.models import NumberRecord, Contact


class TestAntiRobotDriver(unittest.TestCase):
    """Test cases for AntiRobotDriver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = RateLimitConfig(
            max_requests_per_minute=5,
            max_requests_per_hour=10,
            min_delay_between_requests=0.1,
            max_delay_between_requests=0.2
        )
        self.driver = AntiRobotDriver(self.config)
    
    def test_initialization(self):
        """Test driver initialization."""
        self.assertEqual(self.driver.config.max_requests_per_minute, 5)
        self.assertEqual(self.driver.config.max_requests_per_hour, 10)
        self.assertEqual(self.driver.total_requests, 0)
        self.assertEqual(self.driver.failed_requests, 0)
        self.assertIsNone(self.driver.flood_wait_until)
    
    def test_record_request(self):
        """Test request recording."""
        self.driver.record_request(success=True)
        self.assertEqual(self.driver.total_requests, 1)
        self.assertEqual(self.driver.failed_requests, 0)
        
        self.driver.record_request(success=False)
        self.assertEqual(self.driver.total_requests, 2)
        self.assertEqual(self.driver.failed_requests, 1)
    
    def test_handle_flood_wait(self):
        """Test flood wait handling."""
        self.driver.handle_flood_wait(60)
        
        self.assertIsNotNone(self.driver.flood_wait_until)
        self.assertTrue(self.driver.flood_wait_until > datetime.now())
    
    def test_get_statistics(self):
        """Test statistics generation."""
        # Record some requests
        self.driver.record_request(success=True)
        self.driver.record_request(success=False)
        self.driver.record_request(success=True)
        
        # Add small delay to ensure runtime > 0
        import time
        time.sleep(0.01)
        
        stats = self.driver.get_statistics()
        
        self.assertEqual(stats['total_requests'], 3)
        self.assertEqual(stats['failed_requests'], 1)
        self.assertAlmostEqual(stats['success_rate'], 66.67, places=1)
        self.assertGreaterEqual(stats['runtime_seconds'], 0)
    
    def test_reset(self):
        """Test driver reset."""
        # Add some data
        self.driver.record_request(success=True)
        self.driver.handle_flood_wait(60)
        
        # Reset
        self.driver.reset()
        
        self.assertEqual(self.driver.total_requests, 0)
        self.assertEqual(self.driver.failed_requests, 0)
        self.assertIsNone(self.driver.flood_wait_until)
        self.assertEqual(len(self.driver.request_times), 0)


class TestTelegramClientManager(unittest.TestCase):
    """Test cases for TelegramClientManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_id = "test_api_id"
        self.api_hash = "test_api_hash"
        self.client_manager = TelegramClientManager(self.api_id, self.api_hash)
    
    @patch('core.telegram_client.TelegramClient')
    async def test_connect_success(self, mock_telegram_client):
        """Test successful connection."""
        # Mock the client
        mock_client = AsyncMock()
        mock_client.is_user_authorized.return_value = True
        mock_client.connect = AsyncMock()
        mock_telegram_client.return_value = mock_client
        
        # Test connection
        result = await self.client_manager.connect()
        
        self.assertTrue(result)
        self.assertTrue(self.client_manager.is_connected())
        mock_client.connect.assert_called_once()
        mock_client.is_user_authorized.assert_called_once()
    
    @patch('core.telegram_client.TelegramClient')
    async def test_connect_unauthorized(self, mock_telegram_client):
        """Test connection with unauthorized user."""
        # Mock the client
        mock_client = AsyncMock()
        mock_client.is_user_authorized.return_value = False
        mock_client.connect = AsyncMock()
        mock_telegram_client.return_value = mock_client
        
        # Test connection
        result = await self.client_manager.connect()
        
        self.assertFalse(result)
        self.assertFalse(self.client_manager.is_connected())
    
    @patch('core.telegram_client.TelegramClient')
    async def test_disconnect(self, mock_telegram_client):
        """Test disconnection."""
        # Mock the client
        mock_client = AsyncMock()
        mock_client.is_user_authorized.return_value = True
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_telegram_client.return_value = mock_client
        
        # Connect first
        await self.client_manager.connect()
        self.assertTrue(self.client_manager.is_connected())
        
        # Disconnect
        await self.client_manager.disconnect()
        self.assertFalse(self.client_manager.is_connected())
        mock_client.disconnect.assert_called_once()


class TestNumberChecker(unittest.TestCase):
    """Test cases for NumberChecker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_telegram_analyzer.db")
        self.database = DatabaseManager(self.db_path)
        
        # Mock telegram client
        self.telegram_client = Mock()
        self.telegram_client.is_connected.return_value = True
        
        # Create number checker
        self.number_checker = NumberChecker(
            self.telegram_client,
            self.database
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test number checker initialization."""
        self.assertEqual(self.number_checker.total_numbers, 0)
        self.assertEqual(self.number_checker.checked_numbers, 0)
        self.assertEqual(self.number_checker.valid_numbers, 0)
        self.assertEqual(self.number_checker.invalid_numbers, 0)
        self.assertEqual(self.number_checker.failed_numbers, 0)
        self.assertIsNotNone(self.number_checker.anti_robot_driver)
    
    def test_set_callbacks(self):
        """Test callback setting."""
        progress_callback = Mock()
        completion_callback = Mock()
        
        self.number_checker.set_progress_callback(progress_callback)
        self.number_checker.set_completion_callback(completion_callback)
        
        self.assertEqual(self.number_checker.progress_callback, progress_callback)
        self.assertEqual(self.number_checker.completion_callback, completion_callback)
    
    async def test_check_single_number_success(self):
        """Test successful single number check."""
        # Mock the telegram client
        self.telegram_client.check_number_exists = AsyncMock(return_value=True)
        
        # Test check
        result = await self.number_checker.check_single_number("+905551234567")
        
        self.assertEqual(result, True)
        self.telegram_client.check_number_exists.assert_called_once_with("+905551234567")
    
    async def test_check_single_number_failure(self):
        """Test failed single number check."""
        # Mock the telegram client
        self.telegram_client.check_number_exists = AsyncMock(return_value=False)
        
        # Test check
        result = await self.number_checker.check_single_number("+905551234567")
        
        self.assertEqual(result, False)
    
    async def test_check_single_number_error(self):
        """Test single number check with error."""
        # Mock the telegram client to raise exception
        self.telegram_client.check_number_exists = AsyncMock(side_effect=Exception("Test error"))
        
        # Test check
        result = await self.number_checker.check_single_number("+905551234567")
        
        self.assertIsNone(result)
    
    def test_get_results(self):
        """Test results generation."""
        # Set some test data
        self.number_checker.total_numbers = 100
        self.number_checker.checked_numbers = 50
        self.number_checker.valid_numbers = 30
        self.number_checker.invalid_numbers = 20
        self.number_checker.failed_numbers = 5
        
        results = self.number_checker.get_results()
        
        self.assertEqual(results['total_numbers'], 100)
        self.assertEqual(results['checked_numbers'], 50)
        self.assertEqual(results['valid_numbers'], 30)
        self.assertEqual(results['invalid_numbers'], 20)
        self.assertEqual(results['failed_numbers'], 5)
        self.assertEqual(results['success_rate'], 50.0)
        self.assertEqual(results['valid_rate'], 60.0)
        self.assertIn('anti_robot_stats', results)
    
    def test_reset(self):
        """Test checker reset."""
        # Set some test data
        self.number_checker.total_numbers = 100
        self.number_checker.checked_numbers = 50
        self.number_checker.valid_numbers = 30
        self.number_checker.invalid_numbers = 20
        self.number_checker.failed_numbers = 5
        
        # Reset
        self.number_checker.reset()
        
        self.assertEqual(self.number_checker.total_numbers, 0)
        self.assertEqual(self.number_checker.checked_numbers, 0)
        self.assertEqual(self.number_checker.valid_numbers, 0)
        self.assertEqual(self.number_checker.invalid_numbers, 0)
        self.assertEqual(self.number_checker.failed_numbers, 0)


def run_async_test(coro):
    """Helper function to run async tests."""
    return asyncio.run(coro)


# Add async test methods
class TestTelegramClientManagerAsync(unittest.TestCase):
    """Async test cases for TelegramClientManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_id = "test_api_id"
        self.api_hash = "test_api_hash"
        self.client_manager = TelegramClientManager(self.api_id, self.api_hash)
    
    def test_connect_success(self):
        """Test successful connection."""
        run_async_test(self._test_connect_success())
    
    async def _test_connect_success(self):
        """Async test for successful connection."""
        with patch('core.telegram_client.TelegramClient') as mock_telegram_client:
            # Mock the client
            mock_client = AsyncMock()
            mock_client.is_user_authorized.return_value = True
            mock_client.connect = AsyncMock()
            mock_telegram_client.return_value = mock_client
            
            # Test connection
            result = await self.client_manager.connect()
            
            self.assertTrue(result)
            self.assertTrue(self.client_manager.is_connected())
    
    def test_connect_unauthorized(self):
        """Test connection with unauthorized user."""
        run_async_test(self._test_connect_unauthorized())
    
    async def _test_connect_unauthorized(self):
        """Async test for unauthorized connection."""
        with patch('core.telegram_client.TelegramClient') as mock_telegram_client:
            # Mock the client
            mock_client = AsyncMock()
            mock_client.is_user_authorized.return_value = False
            mock_client.connect = AsyncMock()
            mock_telegram_client.return_value = mock_client
            
            # Test connection
            result = await self.client_manager.connect()
            
            self.assertFalse(result)
            self.assertFalse(self.client_manager.is_connected())


class TestNumberCheckerAsync(unittest.TestCase):
    """Async test cases for NumberChecker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_telegram_analyzer.db")
        self.database = DatabaseManager(self.db_path)
        
        # Mock telegram client
        self.telegram_client = Mock()
        self.telegram_client.is_connected.return_value = True
        
        # Create number checker
        self.number_checker = NumberChecker(
            self.telegram_client,
            self.database
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_check_single_number_success(self):
        """Test successful single number check."""
        run_async_test(self._test_check_single_number_success())
    
    async def _test_check_single_number_success(self):
        """Async test for successful single number check."""
        # Mock the telegram client
        self.telegram_client.check_number_exists = AsyncMock(return_value=True)
        
        # Test check
        result = await self.number_checker.check_single_number("+905551234567")
        
        self.assertEqual(result, True)
        self.telegram_client.check_number_exists.assert_called_once_with("+905551234567")
    
    def test_check_single_number_failure(self):
        """Test failed single number check."""
        run_async_test(self._test_check_single_number_failure())
    
    async def _test_check_single_number_failure(self):
        """Async test for failed single number check."""
        # Mock the telegram client
        self.telegram_client.check_number_exists = AsyncMock(return_value=False)
        
        # Test check
        result = await self.number_checker.check_single_number("+905551234567")
        
        self.assertEqual(result, False)


if __name__ == '__main__':
    unittest.main() 