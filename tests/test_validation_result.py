import unittest
from datetime import datetime, timedelta
from models.phone_number import PhoneNumber
from models.validation_result import ValidationResult


class TestValidationResult(unittest.TestCase):
    """Unit tests for ValidationResult model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.phone_number = PhoneNumber(number="+90 532 123 45 67", name="Test User")
        self.validation_date = datetime.now()
        self.response_time = 2.5
    
    def test_validation_result_creation_success(self):
        """Test creating a successful ValidationResult."""
        result = ValidationResult(
            phone_number=self.phone_number,
            is_telegram_registered=True,
            validation_date=self.validation_date,
            response_time=self.response_time
        )
        
        self.assertEqual(result.phone_number, self.phone_number)
        self.assertTrue(result.is_telegram_registered)
        self.assertEqual(result.validation_date, self.validation_date)
        self.assertEqual(result.response_time, self.response_time)
        self.assertIsNone(result.error_message)
        
        # Check that phone number was updated
        self.assertTrue(self.phone_number.is_valid)
        self.assertEqual(self.phone_number.checked_date, self.validation_date)
    
    def test_validation_result_creation_with_error(self):
        """Test creating a ValidationResult with error."""
        error_message = "Network timeout"
        result = ValidationResult(
            phone_number=self.phone_number,
            is_telegram_registered=False,
            validation_date=self.validation_date,
            response_time=self.response_time,
            error_message=error_message
        )
        
        self.assertEqual(result.error_message, error_message)
        self.assertFalse(result.is_telegram_registered)
        
        # Phone number should not be updated when there's an error
        self.assertIsNone(self.phone_number.is_valid)
        self.assertIsNone(self.phone_number.checked_date)
    
    def test_is_successful(self):
        """Test checking if validation was successful."""
        # Successful validation
        success_result = ValidationResult(
            phone_number=self.phone_number,
            is_telegram_registered=True,
            validation_date=self.validation_date,
            response_time=self.response_time
        )
        self.assertTrue(success_result.is_successful())
        
        # Failed validation
        error_result = ValidationResult(
            phone_number=self.phone_number,
            is_telegram_registered=False,
            validation_date=self.validation_date,
            response_time=self.response_time,
            error_message="API Error"
        )
        self.assertFalse(error_result.is_successful())
    
    def test_get_result_summary(self):
        """Test getting result summary text."""
        # Successful validation - registered
        success_result = ValidationResult(
            phone_number=self.phone_number,
            is_telegram_registered=True,
            validation_date=self.validation_date,
            response_time=2.5
        )
        expected = "Number is registered on Telegram (validated in 2.50s)"
        self.assertEqual(success_result.get_result_summary(), expected)
        
        # Successful validation - not registered
        not_registered_result = ValidationResult(
            phone_number=self.phone_number,
            is_telegram_registered=False,
            validation_date=self.validation_date,
            response_time=1.2
        )
        expected = "Number is not registered on Telegram (validated in 1.20s)"
        self.assertEqual(not_registered_result.get_result_summary(), expected)
        
        # Failed validation
        error_result = ValidationResult(
            phone_number=self.phone_number,
            is_telegram_registered=False,
            validation_date=self.validation_date,
            response_time=0.5,
            error_message="Connection failed"
        )
        expected = "Validation failed: Connection failed"
        self.assertEqual(error_result.get_result_summary(), expected)
    
    def test_get_performance_category(self):
        """Test performance categorization based on response time."""
        test_cases = [
            (0.5, "Fast"),
            (0.9, "Fast"),
            (1.0, "Normal"),
            (2.5, "Normal"),
            (2.9, "Normal"),
            (3.0, "Slow"),
            (5.0, "Slow"),
            (9.9, "Slow"),
            (10.0, "Very Slow"),
            (15.0, "Very Slow"),
        ]
        
        for response_time, expected_category in test_cases:
            with self.subTest(response_time=response_time):
                result = ValidationResult(
                    phone_number=self.phone_number,
                    is_telegram_registered=True,
                    validation_date=self.validation_date,
                    response_time=response_time
                )
                self.assertEqual(result.get_performance_category(), expected_category)
    
    def test_to_dict(self):
        """Test converting ValidationResult to dictionary."""
        result = ValidationResult(
            phone_number=self.phone_number,
            is_telegram_registered=True,
            validation_date=self.validation_date,
            response_time=2.5
        )
        
        result_dict = result.to_dict()
        
        expected_keys = [
            'phone_number', 'name', 'is_telegram_registered', 
            'validation_date', 'response_time', 'error_message',
            'operator_code', 'performance_category'
        ]
        
        for key in expected_keys:
            self.assertIn(key, result_dict)
        
        self.assertEqual(result_dict['phone_number'], "+90 532 123 45 67")
        self.assertEqual(result_dict['name'], "Test User")
        self.assertTrue(result_dict['is_telegram_registered'])
        self.assertEqual(result_dict['response_time'], 2.5)
        self.assertIsNone(result_dict['error_message'])
        self.assertEqual(result_dict['operator_code'], "532")
        self.assertEqual(result_dict['performance_category'], "Normal")
    
    def test_create_error_result(self):
        """Test creating error result using class method."""
        error_message = "API rate limit exceeded"
        response_time = 1.5
        
        result = ValidationResult.create_error_result(
            phone_number=self.phone_number,
            error_message=error_message,
            response_time=response_time
        )
        
        self.assertEqual(result.phone_number, self.phone_number)
        self.assertFalse(result.is_telegram_registered)
        self.assertEqual(result.error_message, error_message)
        self.assertEqual(result.response_time, response_time)
        self.assertFalse(result.is_successful())
        
        # Validation date should be recent (within last minute)
        time_diff = datetime.now() - result.validation_date
        self.assertLess(time_diff, timedelta(minutes=1))
    
    def test_create_success_result(self):
        """Test creating success result using class method."""
        is_registered = True
        response_time = 3.2
        
        result = ValidationResult.create_success_result(
            phone_number=self.phone_number,
            is_registered=is_registered,
            response_time=response_time
        )
        
        self.assertEqual(result.phone_number, self.phone_number)
        self.assertTrue(result.is_telegram_registered)
        self.assertIsNone(result.error_message)
        self.assertEqual(result.response_time, response_time)
        self.assertTrue(result.is_successful())
        
        # Validation date should be recent (within last minute)
        time_diff = datetime.now() - result.validation_date
        self.assertLess(time_diff, timedelta(minutes=1))
        
        # Phone number should be updated
        self.assertTrue(self.phone_number.is_valid)
        self.assertIsNotNone(self.phone_number.checked_date)
    
    def test_phone_number_update_on_success(self):
        """Test that phone number is updated correctly on successful validation."""
        phone = PhoneNumber(number="+90 555 999 88 77")
        
        # Initially not checked
        self.assertFalse(phone.is_checked())
        
        # Create successful result
        result = ValidationResult(
            phone_number=phone,
            is_telegram_registered=True,
            validation_date=self.validation_date,
            response_time=1.0
        )
        
        # Phone should now be marked as checked and valid
        self.assertTrue(phone.is_checked())
        self.assertTrue(phone.is_valid)
        self.assertEqual(phone.checked_date, self.validation_date)
    
    def test_phone_number_not_updated_on_error(self):
        """Test that phone number is not updated when validation has error."""
        phone = PhoneNumber(number="+90 555 999 88 77")
        
        # Initially not checked
        self.assertFalse(phone.is_checked())
        
        # Create error result
        result = ValidationResult(
            phone_number=phone,
            is_telegram_registered=False,
            validation_date=self.validation_date,
            response_time=0.5,
            error_message="Network error"
        )
        
        # Phone should still not be marked as checked
        self.assertFalse(phone.is_checked())
        self.assertIsNone(phone.is_valid)
        self.assertIsNone(phone.checked_date)


if __name__ == '__main__':
    unittest.main()