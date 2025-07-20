import unittest
from datetime import datetime
from models.phone_number import PhoneNumber


class TestPhoneNumber(unittest.TestCase):
    """Unit tests for PhoneNumber model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_number = "+90 532 123 45 67"
        self.invalid_format_number = "+90 432 123 45 67"  # Invalid operator code
        self.malformed_number = "532 123 45 67"  # Missing +90
        
    def test_phone_number_creation(self):
        """Test basic PhoneNumber creation."""
        phone = PhoneNumber(number=self.valid_number, name="Test User")
        
        self.assertEqual(phone.number, self.valid_number)
        self.assertEqual(phone.name, "Test User")
        self.assertIsNone(phone.is_valid)
        self.assertIsNone(phone.checked_date)
        self.assertEqual(phone.operator_code, "532")
    
    def test_operator_code_extraction(self):
        """Test operator code extraction from different formats."""
        test_cases = [
            ("+90 532 123 45 67", "532"),
            ("+905321234567", "532"),
            ("+90-555-123-45-67", "555"),
            ("+90 559 999 88 77", "559"),
            ("invalid", ""),
            ("", ""),
        ]
        
        for number, expected_code in test_cases:
            with self.subTest(number=number):
                phone = PhoneNumber(number=number)
                self.assertEqual(phone.operator_code, expected_code)
    
    def test_validate_format_valid_numbers(self):
        """Test validation of valid Turkish phone numbers."""
        valid_numbers = [
            "+90 532 123 45 67",
            "+905321234567",
            "+90-555-999-88-77",
            "+90 559 123 45 67",
            "+90 501 234 56 78",
            "+90 542 987 65 43",
        ]
        
        for number in valid_numbers:
            with self.subTest(number=number):
                phone = PhoneNumber(number=number)
                self.assertTrue(phone.validate_format(), f"Should be valid: {number}")
    
    def test_validate_format_invalid_numbers(self):
        """Test validation of invalid phone numbers."""
        invalid_numbers = [
            "+90 432 123 45 67",  # Invalid operator code (4XX)
            "+90 632 123 45 67",  # Invalid operator code (6XX)
            "+91 532 123 45 67",  # Wrong country code
            "532 123 45 67",      # Missing country code
            "+90 532 123 45",     # Too short
            "+90 532 123 45 678", # Too long
            "+90 532 12a 45 67",  # Contains letters
            "",                   # Empty string
            "+90 532",            # Incomplete
        ]
        
        for number in invalid_numbers:
            with self.subTest(number=number):
                phone = PhoneNumber(number=number)
                self.assertFalse(phone.validate_format(), f"Should be invalid: {number}")
    
    def test_get_display_format(self):
        """Test display formatting of phone numbers."""
        test_cases = [
            ("+905321234567", "+90 532 123 45 67"),
            ("+90 532 123 45 67", "+90 532 123 45 67"),
            ("+90-555-999-88-77", "+90 555 999 88 77"),
            ("invalid", "invalid"),
            ("", ""),
        ]
        
        for input_number, expected_display in test_cases:
            with self.subTest(input_number=input_number):
                phone = PhoneNumber(number=input_number)
                self.assertEqual(phone.get_display_format(), expected_display)
    
    def test_is_checked(self):
        """Test checking if phone number has been validated."""
        # Not checked - no date or validity
        phone1 = PhoneNumber(number=self.valid_number)
        self.assertFalse(phone1.is_checked())
        
        # Not checked - has date but no validity
        phone2 = PhoneNumber(number=self.valid_number, checked_date=datetime.now())
        self.assertFalse(phone2.is_checked())
        
        # Not checked - has validity but no date
        phone3 = PhoneNumber(number=self.valid_number, is_valid=True)
        self.assertFalse(phone3.is_checked())
        
        # Checked - has both date and validity
        phone4 = PhoneNumber(
            number=self.valid_number,
            checked_date=datetime.now(),
            is_valid=True
        )
        self.assertTrue(phone4.is_checked())
    
    def test_get_status_text(self):
        """Test status text generation."""
        # Not checked
        phone1 = PhoneNumber(number=self.valid_number)
        self.assertEqual(phone1.get_status_text(), "Not checked")
        
        # Valid and checked
        phone2 = PhoneNumber(
            number=self.valid_number,
            checked_date=datetime.now(),
            is_valid=True
        )
        self.assertEqual(phone2.get_status_text(), "Valid (Telegram registered)")
        
        # Invalid and checked
        phone3 = PhoneNumber(
            number=self.valid_number,
            checked_date=datetime.now(),
            is_valid=False
        )
        self.assertEqual(phone3.get_status_text(), "Invalid (Not registered)")
    
    def test_all_turkish_operator_codes(self):
        """Test validation with all valid Turkish operator codes."""
        # Test a sample from each operator range
        operator_samples = [
            "500", "505", "509",  # 50X range
            "510", "515", "519",  # 51X range
            "520", "525", "529",  # 52X range
            "530", "535", "539",  # 53X range
            "540", "545", "549",  # 54X range
            "550", "555", "559",  # 55X range
        ]
        
        for operator in operator_samples:
            number = f"+90 {operator} 123 45 67"
            with self.subTest(operator=operator):
                phone = PhoneNumber(number=number)
                self.assertTrue(phone.validate_format(), f"Operator {operator} should be valid")
                self.assertEqual(phone.operator_code, operator)


if __name__ == '__main__':
    unittest.main()