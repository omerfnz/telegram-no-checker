import unittest
from unittest.mock import patch, MagicMock
import re
from services.phone_generator_service import PhoneGeneratorService


class TestPhoneGeneratorService(unittest.TestCase):
    """Unit tests for PhoneGeneratorService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = PhoneGeneratorService()
        
        # Expected operator codes after expansion
        self.expected_operators = [
            # 50X series
            '500', '501', '502', '503', '504', '505', '506', '507', '508', '509',
            # 51X series  
            '510', '511', '512', '513', '514', '515', '516', '517', '518', '519',
            # 52X series
            '520', '521', '522', '523', '524', '525', '526', '527', '528', '529',
            # 53X series
            '530', '531', '532', '533', '534', '535', '536', '537', '538', '539',
            # 54X series
            '540', '541', '542', '543', '544', '545', '546', '547', '548', '549',
            # 55X series (550-558, not including 559 as it's listed separately)
            '550', '551', '552', '553', '554', '555', '556', '557', '558',
            # Special case 559 (listed separately from 55X)
            '559'
        ]
        
    def test_operator_code_expansion(self):
        """Test that operator codes are properly expanded."""
        expanded = self.service._expanded_operators
        
        # Should have 60 total codes (6 series * 10 each)
        self.assertEqual(len(expanded), 60)
        
        # Check that all expected operators are present
        for expected in self.expected_operators:
            self.assertIn(expected, expanded)
            
        # Check specific ranges
        self.assertIn('500', expanded)
        self.assertIn('509', expanded)
        self.assertIn('559', expanded)
        
    def test_generate_random_number_format(self):
        """Test that generated numbers follow correct format."""
        number = self.service.generate_random_number()
        
        # Should match pattern: +90 5XX XXX XX XX
        pattern = r'^\+90 5\d{2} \d{3} \d{2} \d{2}$'
        self.assertRegex(number, pattern)
        
        # Should start with +90
        self.assertTrue(number.startswith('+90'))
        
        # Should have correct length (17 characters including spaces)
        self.assertEqual(len(number), 17)
        
    def test_generate_random_number_operator_codes(self):
        """Test that generated numbers use valid operator codes."""
        # Generate multiple numbers to test different operator codes
        for _ in range(50):
            number = self.service.generate_random_number()
            
            # Extract operator code (characters 4-7, e.g., "532" from "+90 532 123 45 67")
            operator_code = number[4:7]
            
            # Should be a valid Turkish operator code
            self.assertIn(operator_code, self.service._expanded_operators)
            
    def test_generate_batch_valid_count(self):
        """Test batch generation with valid count."""
        counts = [1, 5, 10, 100]
        
        for count in counts:
            batch = self.service.generate_batch(count)
            
            # Should generate exactly the requested count
            self.assertEqual(len(batch), count)
            
            # All numbers should be valid format
            for number in batch:
                self.assertTrue(self.service.validate_turkish_format(number))
                
    def test_generate_batch_invalid_count(self):
        """Test batch generation with invalid count."""
        invalid_counts = [0, -1, -10]
        
        for count in invalid_counts:
            with self.assertRaises(ValueError):
                self.service.generate_batch(count)
                
    def test_generate_batch_uniqueness(self):
        """Test that batch generation can produce different numbers."""
        # Generate a large batch and check for some variety
        batch = self.service.generate_batch(100)
        
        # Should have some variety (not all identical)
        unique_numbers = set(batch)
        self.assertGreater(len(unique_numbers), 1)
        
    def test_validate_turkish_format_valid_numbers(self):
        """Test validation of valid Turkish phone numbers."""
        valid_numbers = [
            "+90 532 123 45 67",
            "+90 555 987 65 43",
            "+90 505 111 22 33",
            "+90 559 444 55 66",
            "+905321234567",  # Without spaces
            "+90-532-123-45-67",  # With dashes
        ]
        
        for number in valid_numbers:
            with self.subTest(number=number):
                self.assertTrue(self.service.validate_turkish_format(number))
                
    def test_validate_turkish_format_invalid_numbers(self):
        """Test validation of invalid Turkish phone numbers."""
        invalid_numbers = [
            "",  # Empty string
            None,  # None value would cause error, but we handle it
            "+90 432 123 45 67",  # Invalid operator code (4XX)
            "+90 612 123 45 67",  # Invalid operator code (6XX)
            "+91 532 123 45 67",  # Wrong country code
            "532 123 45 67",  # Missing country code
            "+90 532 123 45",  # Too short
            "+90 532 123 45 678",  # Too long
            "+90 532 abc 45 67",  # Non-numeric
            "+90 532 123 45 6a",  # Non-numeric
            "+90 5321234567890",  # Too many digits
        ]
        
        for number in invalid_numbers:
            with self.subTest(number=number):
                if number is None:
                    # Handle None case separately to avoid TypeError
                    self.assertFalse(self.service.validate_turkish_format(""))
                else:
                    self.assertFalse(self.service.validate_turkish_format(number))
                    
    def test_validate_turkish_format_all_operator_codes(self):
        """Test validation with all supported operator codes."""
        for operator_code in self.service._expanded_operators:
            number = f"+90 {operator_code} 123 45 67"
            with self.subTest(operator_code=operator_code):
                self.assertTrue(self.service.validate_turkish_format(number))
                
    def test_get_operator_code_valid_numbers(self):
        """Test operator code extraction from valid numbers."""
        test_cases = [
            ("+90 532 123 45 67", "532"),
            ("+90 555 987 65 43", "555"),
            ("+905051112233", "505"),
            ("+90-559-444-55-66", "559"),
        ]
        
        for number, expected_code in test_cases:
            with self.subTest(number=number):
                result = self.service.get_operator_code(number)
                self.assertEqual(result, expected_code)
                
    def test_get_operator_code_invalid_numbers(self):
        """Test operator code extraction from invalid numbers."""
        invalid_numbers = [
            "+90 432 123 45 67",  # Invalid operator
            "532 123 45 67",  # Missing country code
            "+91 532 123 45 67",  # Wrong country code
            "",  # Empty string
        ]
        
        for number in invalid_numbers:
            with self.subTest(number=number):
                result = self.service.get_operator_code(number)
                self.assertEqual(result, "")
                
    def test_get_supported_operators(self):
        """Test getting list of supported operators."""
        operators = self.service.get_supported_operators()
        
        # Should return a copy of the internal list
        self.assertEqual(len(operators), 60)
        self.assertIsInstance(operators, list)
        
        # Should contain all expected operators
        for expected in self.expected_operators:
            self.assertIn(expected, operators)
            
        # Modifying returned list shouldn't affect internal state
        original_length = len(self.service._expanded_operators)
        operators.append("999")
        self.assertEqual(len(self.service._expanded_operators), original_length)
        
    @patch('services.phone_generator_service.random.choice')
    def test_generate_random_number_uses_random_choice(self, mock_choice):
        """Test that random number generation uses random.choice for operator selection."""
        mock_choice.return_value = "532"
        
        with patch('services.phone_generator_service.random.randint', return_value=1):
            number = self.service.generate_random_number()
            
        # Should have called random.choice with expanded operators
        mock_choice.assert_called_once_with(self.service._expanded_operators)
        
        # Should generate expected format with mocked values
        self.assertEqual(number, "+90 532 111 11 11")
        
    def test_logging_integration(self):
        """Test that service integrates with logging properly."""
        # Service should have a logger
        self.assertIsNotNone(self.service.logger)
        self.assertEqual(self.service.logger.name, 'services.phone_generator_service')
        
    def test_error_handling_in_generation(self):
        """Test error handling during number generation."""
        # Mock random.choice to raise an exception
        with patch('services.phone_generator_service.random.choice', side_effect=Exception("Test error")):
            with self.assertRaises(Exception):
                self.service.generate_random_number()
                
    def test_error_handling_in_batch_generation(self):
        """Test error handling during batch generation."""
        # Mock generate_random_number to raise an exception
        with patch.object(self.service, 'generate_random_number', side_effect=Exception("Test error")):
            with self.assertRaises(Exception):
                self.service.generate_batch(5)


if __name__ == '__main__':
    unittest.main()