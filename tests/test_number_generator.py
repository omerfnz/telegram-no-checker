"""
Tests for number generator modules.

This module contains unit tests for number generation functionality.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch

from core.number_generator import NumberGenerator, GenerationConfig
from core.bulk_generator import BulkGenerator
from data.database import DatabaseManager
from data.models import NumberRecord


class TestNumberGenerator(unittest.TestCase):
    """Test cases for NumberGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_telegram_analyzer.db")
        self.database = DatabaseManager(self.db_path)
        
        # Create number generator
        self.generator = NumberGenerator(self.database)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.generated_count, 0)
        self.assertIsNotNone(self.generator.database)
        self.assertIsNotNone(self.generator.logger)
    
    def test_get_available_countries(self):
        """Test getting available countries."""
        countries = self.generator.get_available_countries()
        
        self.assertIsInstance(countries, list)
        self.assertIn("+90", countries)  # Turkey
        self.assertIn("+1", countries)   # USA
        self.assertIn("+44", countries)  # UK
    
    def test_get_operators_for_country(self):
        """Test getting operators for a country."""
        operators = self.generator.get_operators_for_country("+90")
        
        self.assertIsInstance(operators, dict)
        self.assertIn("Turkcell", operators)
        self.assertIn("Vodafone", operators)
        self.assertIn("Türk Telekom", operators)
        self.assertIn("Diğer", operators)
    
    def test_validate_country_code(self):
        """Test country code validation."""
        # Valid country codes
        self.assertTrue(self.generator.validate_country_code("+90"))
        self.assertTrue(self.generator.validate_country_code("+1"))
        self.assertTrue(self.generator.validate_country_code("+44"))
        
        # Invalid country codes
        self.assertFalse(self.generator.validate_country_code("+99"))
        self.assertFalse(self.generator.validate_country_code("invalid"))
        self.assertFalse(self.generator.validate_country_code(""))
    
    def test_validate_operator_prefix(self):
        """Test operator prefix validation."""
        # Valid combinations
        self.assertTrue(self.generator.validate_operator_prefix("+90", "555"))
        self.assertTrue(self.generator.validate_operator_prefix("+90", "542"))
        self.assertTrue(self.generator.validate_operator_prefix("+1", "201"))
        
        # Invalid combinations
        self.assertFalse(self.generator.validate_operator_prefix("+90", "999"))
        self.assertFalse(self.generator.validate_operator_prefix("+99", "555"))
        self.assertFalse(self.generator.validate_operator_prefix("invalid", "555"))
    
    def test_generate_single_number(self):
        """Test single number generation."""
        number_record = self.generator.generate_single_number("+90", "555")
        
        self.assertIsNotNone(number_record)
        self.assertIsInstance(number_record, NumberRecord)
        self.assertEqual(number_record.country_code, "+90")
        self.assertEqual(number_record.operator_prefix, "555")
        self.assertEqual(number_record.full_number[:6], "+90555")
        self.assertFalse(number_record.is_checked)
        self.assertEqual(self.generator.generated_count, 1)
    
    def test_generate_single_number_invalid_country(self):
        """Test single number generation with invalid country."""
        number_record = self.generator.generate_single_number("+99", "555")
        
        self.assertIsNone(number_record)
        self.assertEqual(self.generator.generated_count, 0)
    
    def test_generate_single_number_invalid_operator(self):
        """Test single number generation with invalid operator."""
        number_record = self.generator.generate_single_number("+90", "999")
        
        self.assertIsNone(number_record)
        self.assertEqual(self.generator.generated_count, 0)
    
    def test_generate_single_number_with_range(self):
        """Test single number generation with custom range."""
        number_record = self.generator.generate_single_number(
            "+90", "555", number_range=(1000000, 1999999)
        )
        
        self.assertIsNotNone(number_record)
        number_part = int(number_record.phone_number)
        self.assertGreaterEqual(number_part, 1000000)
        self.assertLessEqual(number_part, 1999999)
    
    def test_generate_numbers_for_operator(self):
        """Test generating multiple numbers for an operator."""
        numbers = self.generator.generate_numbers_for_operator(
            country_code="+90",
            operator_prefix="555",
            count=5
        )
        
        self.assertEqual(len(numbers), 5)
        self.assertEqual(self.generator.generated_count, 5)
        
        # Check all numbers have correct format
        for number_record in numbers:
            self.assertEqual(number_record.country_code, "+90")
            self.assertEqual(number_record.operator_prefix, "555")
            self.assertEqual(number_record.full_number[:6], "+90555")
    
    def test_generate_numbers_batch(self):
        """Test batch number generation."""
        config = GenerationConfig(
            country_code="+90",
            operator_prefixes=["555", "542"],
            batch_size=10
        )
        
        numbers = self.generator.generate_numbers_batch(config)
        
        self.assertEqual(len(numbers), 10)
        self.assertEqual(self.generator.generated_count, 10)
        
        # Check distribution across operators
        operator_counts = {}
        for number_record in numbers:
            op = number_record.operator_prefix
            operator_counts[op] = operator_counts.get(op, 0) + 1
        
        self.assertIn("555", operator_counts)
        self.assertIn("542", operator_counts)
        self.assertEqual(operator_counts["555"], 5)
        self.assertEqual(operator_counts["542"], 5)
    
    def test_generate_pattern_numbers(self):
        """Test pattern-based number generation."""
        numbers = self.generator.generate_pattern_numbers(
            country_code="+90",
            operator_prefix="555",
            pattern="123####",
            count=3
        )
        
        self.assertEqual(len(numbers), 3)
        
        # Check pattern compliance
        for number_record in numbers:
            self.assertEqual(number_record.phone_number[:3], "123")
            self.assertEqual(len(number_record.phone_number), 7)
    
    def test_validate_pattern(self):
        """Test pattern validation."""
        # Valid patterns
        self.assertTrue(self.generator._validate_pattern("123####"))
        self.assertTrue(self.generator._validate_pattern("####456"))
        self.assertTrue(self.generator._validate_pattern("12#45#7"))
        
        # Invalid patterns
        self.assertFalse(self.generator._validate_pattern("123###"))  # Too short
        self.assertFalse(self.generator._validate_pattern("123#####"))  # Too long
        self.assertFalse(self.generator._validate_pattern("123abc#"))  # Invalid chars
        self.assertFalse(self.generator._validate_pattern(""))  # Empty
    
    def test_generate_from_pattern(self):
        """Test number generation from pattern."""
        pattern = "123####"
        number = self.generator._generate_from_pattern(pattern)
        
        self.assertIsNotNone(number)
        self.assertEqual(len(number), 7)
        self.assertEqual(number[:3], "123")
        
        # Check that # parts are digits
        for char in number[3:]:
            self.assertIn(char, "0123456789")
    
    def test_get_generation_statistics(self):
        """Test generation statistics."""
        # Generate some numbers first
        self.generator.generate_single_number("+90", "555")
        self.generator.generate_single_number("+90", "542")
        
        stats = self.generator.get_generation_statistics()
        
        self.assertEqual(stats['total_generated'], 2)
        self.assertEqual(stats['supported_countries'], 3)  # +90, +1, +44
        self.assertIn('+90', stats['available_countries'])
    
    def test_reset(self):
        """Test generator reset."""
        # Generate some numbers
        self.generator.generate_single_number("+90", "555")
        self.assertEqual(self.generator.generated_count, 1)
        
        # Reset
        self.generator.reset()
        self.assertEqual(self.generator.generated_count, 0)


class TestBulkGenerator(unittest.TestCase):
    """Test cases for BulkGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_telegram_analyzer.db")
        self.database = DatabaseManager(self.db_path)
        
        # Create bulk generator
        self.bulk_generator = BulkGenerator(self.database)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test bulk generator initialization."""
        self.assertEqual(self.bulk_generator.total_to_generate, 0)
        self.assertEqual(self.bulk_generator.generated_count, 0)
        self.assertEqual(self.bulk_generator.saved_count, 0)
        self.assertEqual(self.bulk_generator.failed_count, 0)
        self.assertIsNotNone(self.bulk_generator.number_generator)
        self.assertIsNotNone(self.bulk_generator.database)
    
    def test_set_callbacks(self):
        """Test callback setting."""
        progress_callback = Mock()
        completion_callback = Mock()
        
        self.bulk_generator.set_progress_callback(progress_callback)
        self.bulk_generator.set_completion_callback(completion_callback)
        
        self.assertEqual(self.bulk_generator.progress_callback, progress_callback)
        self.assertEqual(self.bulk_generator.completion_callback, completion_callback)
    
    def test_generate_and_save_batch(self):
        """Test batch generation and saving."""
        config = GenerationConfig(
            country_code="+90",
            operator_prefixes=["555"],
            batch_size=5
        )
        
        result = self.bulk_generator.generate_and_save_batch(
            config, session_name="Test Session"
        )
        
        self.assertIn('total_generated', result)
        self.assertIn('saved_count', result)
        self.assertIn('failed_count', result)
        self.assertIn('session_id', result)
        
        self.assertEqual(result['total_generated'], 5)
        self.assertEqual(result['saved_count'], 5)
        self.assertEqual(result['failed_count'], 0)
        self.assertIsNotNone(result['session_id'])
        
        # Check database
        stats = self.database.get_statistics()
        self.assertEqual(stats['number_records']['total'], 5)
        self.assertEqual(stats['sessions']['total'], 1)
    
    def test_generate_for_multiple_operators(self):
        """Test generation for multiple operators."""
        operators = {
            "555": 3,
            "542": 2
        }
        
        result = self.bulk_generator.generate_for_multiple_operators(
            country_code="+90",
            operators=operators,
            session_name="Multi Operator Test"
        )
        
        self.assertEqual(result['total_generated'], 5)
        self.assertEqual(result['saved_count'], 5)
        self.assertEqual(result['failed_count'], 0)
        self.assertIsNotNone(result['session_id'])
        
        # Check database
        stats = self.database.get_statistics()
        self.assertEqual(stats['number_records']['total'], 5)
        self.assertEqual(stats['sessions']['total'], 1)
    
    def test_generate_pattern_batch(self):
        """Test pattern-based batch generation."""
        result = self.bulk_generator.generate_pattern_batch(
            country_code="+90",
            operator_prefix="555",
            pattern="123####",
            count=3,
            session_name="Pattern Test"
        )
        
        self.assertEqual(result['total_generated'], 3)
        self.assertEqual(result['saved_count'], 3)
        self.assertEqual(result['failed_count'], 0)
        self.assertIsNotNone(result['session_id'])
        
        # Check database
        stats = self.database.get_statistics()
        self.assertEqual(stats['number_records']['total'], 3)
        self.assertEqual(stats['sessions']['total'], 1)
    
    def test_get_generation_statistics(self):
        """Test generation statistics."""
        # Generate some numbers first
        config = GenerationConfig(
            country_code="+90",
            operator_prefixes=["555"],
            batch_size=2
        )
        self.bulk_generator.generate_and_save_batch(config)
        
        stats = self.bulk_generator.get_generation_statistics()
        
        self.assertEqual(stats['total_generated'], 2)
        self.assertEqual(stats['total_saved'], 2)
        self.assertEqual(stats['total_failed'], 0)
        self.assertEqual(stats['success_rate'], 100.0)
        self.assertIn('generator_stats', stats)
    
    def test_reset(self):
        """Test bulk generator reset."""
        # Generate some numbers
        config = GenerationConfig(
            country_code="+90",
            operator_prefixes=["555"],
            batch_size=2
        )
        self.bulk_generator.generate_and_save_batch(config)
        
        # Check state before reset
        self.assertGreater(self.bulk_generator.generated_count, 0)
        self.assertGreater(self.bulk_generator.saved_count, 0)
        
        # Reset
        self.bulk_generator.reset()
        
        self.assertEqual(self.bulk_generator.total_to_generate, 0)
        self.assertEqual(self.bulk_generator.generated_count, 0)
        self.assertEqual(self.bulk_generator.saved_count, 0)
        self.assertEqual(self.bulk_generator.failed_count, 0)


if __name__ == '__main__':
    unittest.main() 