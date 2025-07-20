import unittest
import tempfile
import os
import shutil
from models.app_settings import AppSettings


class TestAppSettings(unittest.TestCase):
    """Unit tests for AppSettings model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_api_id = "12345678"
        self.valid_api_hash = "abcdef1234567890abcdef1234567890"
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_default_settings_creation(self):
        """Test creating AppSettings with default values."""
        settings = AppSettings()
        
        self.assertEqual(settings.telegram_api_id, "")
        self.assertEqual(settings.telegram_api_hash, "")
        self.assertEqual(settings.parallel_threads, 2)
        self.assertEqual(settings.rate_limit_min, 2)
        self.assertEqual(settings.rate_limit_max, 5)
        self.assertTrue(settings.dark_mode)
        self.assertEqual(settings.session_name, "validator_session")
        self.assertTrue(settings.auto_save_results)
        self.assertEqual(settings.max_retries, 3)
        self.assertEqual(settings.timeout_seconds, 30)
        self.assertTrue(settings.export_path.endswith("Downloads"))
    
    def test_custom_settings_creation(self):
        """Test creating AppSettings with custom values."""
        settings = AppSettings(
            telegram_api_id=self.valid_api_id,
            telegram_api_hash=self.valid_api_hash,
            parallel_threads=4,
            rate_limit_min=3,
            rate_limit_max=7,
            dark_mode=False,
            export_path=self.temp_dir
        )
        
        self.assertEqual(settings.telegram_api_id, self.valid_api_id)
        self.assertEqual(settings.telegram_api_hash, self.valid_api_hash)
        self.assertEqual(settings.parallel_threads, 4)
        self.assertEqual(settings.rate_limit_min, 3)
        self.assertEqual(settings.rate_limit_max, 7)
        self.assertFalse(settings.dark_mode)
        self.assertEqual(settings.export_path, self.temp_dir)
    
    def test_settings_validation_thread_limits(self):
        """Test validation of parallel thread limits."""
        # Test minimum limit
        settings = AppSettings(parallel_threads=0)
        self.assertEqual(settings.parallel_threads, 1)
        
        # Test maximum limit
        settings = AppSettings(parallel_threads=15)
        self.assertEqual(settings.parallel_threads, 10)
        
        # Test valid range
        settings = AppSettings(parallel_threads=5)
        self.assertEqual(settings.parallel_threads, 5)
    
    def test_settings_validation_rate_limits(self):
        """Test validation of rate limiting settings."""
        # Test minimum rate limit
        settings = AppSettings(rate_limit_min=0)
        self.assertEqual(settings.rate_limit_min, 1)
        
        # Test max < min correction
        settings = AppSettings(rate_limit_min=5, rate_limit_max=3)
        self.assertEqual(settings.rate_limit_min, 5)
        self.assertEqual(settings.rate_limit_max, 6)  # min + 1
        
        # Test maximum rate limit
        settings = AppSettings(rate_limit_max=100)
        self.assertEqual(settings.rate_limit_max, 60)
    
    def test_settings_validation_timeout(self):
        """Test validation of timeout settings."""
        # Test minimum timeout
        settings = AppSettings(timeout_seconds=1)
        self.assertEqual(settings.timeout_seconds, 5)
        
        # Test maximum timeout
        settings = AppSettings(timeout_seconds=500)
        self.assertEqual(settings.timeout_seconds, 300)
        
        # Test valid timeout
        settings = AppSettings(timeout_seconds=60)
        self.assertEqual(settings.timeout_seconds, 60)
    
    def test_settings_validation_max_retries(self):
        """Test validation of max retries setting."""
        # Test negative retries
        settings = AppSettings(max_retries=-1)
        self.assertEqual(settings.max_retries, 0)
        
        # Test excessive retries
        settings = AppSettings(max_retries=20)
        self.assertEqual(settings.max_retries, 10)
        
        # Test valid retries
        settings = AppSettings(max_retries=5)
        self.assertEqual(settings.max_retries, 5)
    
    def test_validate_telegram_credentials_valid(self):
        """Test validation of valid Telegram credentials."""
        settings = AppSettings(
            telegram_api_id=self.valid_api_id,
            telegram_api_hash=self.valid_api_hash
        )
        self.assertTrue(settings.validate_telegram_credentials())
    
    def test_validate_telegram_credentials_invalid(self):
        """Test validation of invalid Telegram credentials."""
        invalid_cases = [
            # Invalid API ID cases
            ("", self.valid_api_hash),  # Empty API ID
            ("abc", self.valid_api_hash),  # Non-numeric API ID
            ("123", self.valid_api_hash),  # Too short API ID
            ("1234567890", self.valid_api_hash),  # Too long API ID
            
            # Invalid API Hash cases
            (self.valid_api_id, ""),  # Empty API Hash
            (self.valid_api_id, "short"),  # Too short API Hash
            (self.valid_api_id, "abcdef1234567890abcdef1234567890xx"),  # Too long API Hash
            (self.valid_api_id, "gggggggggggggggggggggggggggggggg"),  # Invalid hex characters
        ]
        
        for api_id, api_hash in invalid_cases:
            with self.subTest(api_id=api_id, api_hash=api_hash):
                settings = AppSettings(
                    telegram_api_id=api_id,
                    telegram_api_hash=api_hash
                )
                self.assertFalse(settings.validate_telegram_credentials())
    
    def test_get_risk_level(self):
        """Test risk level assessment."""
        # Low risk settings
        low_risk = AppSettings(
            parallel_threads=2,
            rate_limit_min=4,
            rate_limit_max=6,
            timeout_seconds=30
        )
        self.assertEqual(low_risk.get_risk_level(), "Low")
        
        # Medium risk settings
        medium_risk = AppSettings(
            parallel_threads=3,
            rate_limit_min=3,
            rate_limit_max=4,
            timeout_seconds=15
        )
        self.assertEqual(medium_risk.get_risk_level(), "Medium")
        
        # High risk settings
        high_risk = AppSettings(
            parallel_threads=5,
            rate_limit_min=2,
            rate_limit_max=3,
            timeout_seconds=8
        )
        self.assertEqual(high_risk.get_risk_level(), "High")
        
        # Very high risk settings
        very_high_risk = AppSettings(
            parallel_threads=8,
            rate_limit_min=1,
            rate_limit_max=1,
            timeout_seconds=5
        )
        self.assertEqual(very_high_risk.get_risk_level(), "Very High")
    
    def test_get_risk_warnings(self):
        """Test risk warning generation."""
        # Safe settings - no warnings
        safe_settings = AppSettings(
            telegram_api_id=self.valid_api_id,
            telegram_api_hash=self.valid_api_hash,
            parallel_threads=2,
            rate_limit_min=3,
            rate_limit_max=6,
            timeout_seconds=30
        )
        warnings = safe_settings.get_risk_warnings()
        self.assertEqual(len(warnings), 0)
        
        # Risky settings - multiple warnings
        risky_settings = AppSettings(
            telegram_api_id="invalid",
            telegram_api_hash="invalid",
            parallel_threads=6,
            rate_limit_min=1,
            rate_limit_max=2,
            timeout_seconds=10
        )
        warnings = risky_settings.get_risk_warnings()
        self.assertGreater(len(warnings), 0)
        
        # Check specific warning types
        warning_text = " ".join(warnings)
        self.assertIn("thread count", warning_text)
        self.assertIn("delay", warning_text)
        self.assertIn("credentials", warning_text)
    
    def test_get_recommended_settings(self):
        """Test getting recommended safe settings."""
        original = AppSettings(
            telegram_api_id=self.valid_api_id,
            telegram_api_hash=self.valid_api_hash,
            parallel_threads=8,
            rate_limit_min=1,
            rate_limit_max=2
        )
        
        recommended = original.get_recommended_settings()
        
        # Should preserve credentials
        self.assertEqual(recommended.telegram_api_id, self.valid_api_id)
        self.assertEqual(recommended.telegram_api_hash, self.valid_api_hash)
        
        # Should use safe values
        self.assertEqual(recommended.parallel_threads, 2)
        self.assertEqual(recommended.rate_limit_min, 3)
        self.assertEqual(recommended.rate_limit_max, 6)
        self.assertEqual(recommended.max_retries, 2)
        
        # Should be low risk
        self.assertEqual(recommended.get_risk_level(), "Low")
    
    def test_to_dict(self):
        """Test converting settings to dictionary."""
        settings = AppSettings(
            telegram_api_id=self.valid_api_id,
            telegram_api_hash=self.valid_api_hash,
            parallel_threads=3,
            dark_mode=False
        )
        
        settings_dict = settings.to_dict()
        
        expected_keys = [
            'telegram_api_id', 'telegram_api_hash', 'parallel_threads',
            'rate_limit_min', 'rate_limit_max', 'dark_mode', 'export_path',
            'session_name', 'auto_save_results', 'max_retries', 'timeout_seconds',
            'risk_level'
        ]
        
        for key in expected_keys:
            self.assertIn(key, settings_dict)
        
        self.assertEqual(settings_dict['telegram_api_id'], self.valid_api_id)
        self.assertEqual(settings_dict['parallel_threads'], 3)
        self.assertFalse(settings_dict['dark_mode'])
        self.assertIn(settings_dict['risk_level'], ['Low', 'Medium', 'High', 'Very High'])
    
    def test_from_dict(self):
        """Test creating settings from dictionary."""
        data = {
            'telegram_api_id': self.valid_api_id,
            'telegram_api_hash': self.valid_api_hash,
            'parallel_threads': 4,
            'dark_mode': False,
            'extra_field': 'should_be_ignored'  # Should be filtered out
        }
        
        settings = AppSettings.from_dict(data)
        
        self.assertEqual(settings.telegram_api_id, self.valid_api_id)
        self.assertEqual(settings.telegram_api_hash, self.valid_api_hash)
        self.assertEqual(settings.parallel_threads, 4)
        self.assertFalse(settings.dark_mode)
        
        # Should not have extra field
        self.assertFalse(hasattr(settings, 'extra_field'))
    
    def test_copy(self):
        """Test copying settings."""
        original = AppSettings(
            telegram_api_id=self.valid_api_id,
            telegram_api_hash=self.valid_api_hash,
            parallel_threads=5,
            dark_mode=False
        )
        
        copy = original.copy()
        
        # Should have same values
        self.assertEqual(copy.telegram_api_id, original.telegram_api_id)
        self.assertEqual(copy.telegram_api_hash, original.telegram_api_hash)
        self.assertEqual(copy.parallel_threads, original.parallel_threads)
        self.assertEqual(copy.dark_mode, original.dark_mode)
        
        # Should be different objects
        self.assertIsNot(copy, original)
        
        # Modifying copy should not affect original
        copy.parallel_threads = 10
        self.assertEqual(original.parallel_threads, 5)
        self.assertEqual(copy.parallel_threads, 10)
    
    def test_export_path_creation(self):
        """Test that export path is created if it doesn't exist."""
        non_existent_path = os.path.join(self.temp_dir, "new_folder")
        self.assertFalse(os.path.exists(non_existent_path))
        
        settings = AppSettings(export_path=non_existent_path)
        
        # Path should be created during validation
        self.assertTrue(os.path.exists(settings.export_path))


if __name__ == '__main__':
    unittest.main()