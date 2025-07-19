"""
Tests for file handler modules.

This module contains unit tests for file handling functionality.
"""

import unittest
import tempfile
import os
import pandas as pd
from unittest.mock import Mock, patch

from core.file_handler import FileHandler, ImportConfig, ExportConfig
from core.data_converter import DataConverter
from data.models import Contact, NumberRecord


class TestFileHandler(unittest.TestCase):
    """Test cases for FileHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.file_handler = FileHandler()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'phone_number': ['+905551234567', '+905421234567', '+905031234567'],
            'notes': ['Test 1', 'Test 2', 'Test 3']
        })
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test file handler initialization."""
        self.assertIsNotNone(self.file_handler.logger)
        self.assertIn('excel', self.file_handler.supported_formats)
        self.assertIn('txt', self.file_handler.supported_formats)
        self.assertIn('csv', self.file_handler.supported_formats)
        self.assertIn('.xlsx', self.file_handler.supported_extensions)
        self.assertIn('.txt', self.file_handler.supported_extensions)
        self.assertIn('.csv', self.file_handler.supported_extensions)
    
    def test_detect_file_type(self):
        """Test file type detection."""
        # Valid extensions
        self.assertEqual(self.file_handler.detect_file_type('test.xlsx'), 'excel')
        self.assertEqual(self.file_handler.detect_file_type('test.xls'), 'excel')
        self.assertEqual(self.file_handler.detect_file_type('test.txt'), 'txt')
        self.assertEqual(self.file_handler.detect_file_type('test.csv'), 'csv')
        
        # Invalid extensions
        self.assertIsNone(self.file_handler.detect_file_type('test.pdf'))
        self.assertIsNone(self.file_handler.detect_file_type('test'))
        self.assertIsNone(self.file_handler.detect_file_type(''))
    
    def test_validate_file_path(self):
        """Test file path validation."""
        # Create a temporary file
        temp_file = os.path.join(self.temp_dir, 'test.txt')
        with open(temp_file, 'w') as f:
            f.write('test content')
        
        # Valid file
        self.assertTrue(self.file_handler.validate_file_path(temp_file))
        
        # Invalid files
        self.assertFalse(self.file_handler.validate_file_path('nonexistent.txt'))
        self.assertFalse(self.file_handler.validate_file_path(self.temp_dir))
        self.assertFalse(self.file_handler.validate_file_path(''))
    
    def test_validate_file_type(self):
        """Test file type validation."""
        # Valid types
        self.assertTrue(self.file_handler.validate_file_type('excel'))
        self.assertTrue(self.file_handler.validate_file_type('txt'))
        self.assertTrue(self.file_handler.validate_file_type('csv'))
        self.assertTrue(self.file_handler.validate_file_type('EXCEL'))
        self.assertTrue(self.file_handler.validate_file_type('TXT'))
        
        # Invalid types
        self.assertFalse(self.file_handler.validate_file_type('pdf'))
        self.assertFalse(self.file_handler.validate_file_type('doc'))
        self.assertFalse(self.file_handler.validate_file_type(''))
    
    def test_write_and_read_excel_file(self):
        """Test Excel file write and read operations."""
        # Write Excel file
        excel_path = os.path.join(self.temp_dir, 'test.xlsx')
        export_config = ExportConfig(
            file_path=excel_path,
            file_type='excel',
            sheet_name='TestSheet'
        )
        
        success = self.file_handler.write_file(self.test_data, export_config)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(excel_path))
        
        # Read Excel file
        import_config = ImportConfig(
            file_path=excel_path,
            file_type='excel',
            sheet_name='TestSheet'
        )
        
        df = self.file_handler.read_file(import_config)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ['name', 'phone_number', 'notes'])
    
    def test_write_and_read_txt_file(self):
        """Test TXT file write and read operations."""
        # Write TXT file
        txt_path = os.path.join(self.temp_dir, 'test.txt')
        export_config = ExportConfig(
            file_path=txt_path,
            file_type='txt',
            delimiter='\t'
        )
        
        success = self.file_handler.write_file(self.test_data, export_config)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(txt_path))
        
        # Read TXT file
        import_config = ImportConfig(
            file_path=txt_path,
            file_type='txt',
            delimiter='\t'
        )
        
        df = self.file_handler.read_file(import_config)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ['name', 'phone_number', 'notes'])
    
    def test_write_and_read_csv_file(self):
        """Test CSV file write and read operations."""
        # Write CSV file
        csv_path = os.path.join(self.temp_dir, 'test.csv')
        export_config = ExportConfig(
            file_path=csv_path,
            file_type='csv',
            delimiter=','
        )
        
        success = self.file_handler.write_file(self.test_data, export_config)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(csv_path))
        
        # Read CSV file
        import_config = ImportConfig(
            file_path=csv_path,
            file_type='csv',
            delimiter=','
        )
        
        df = self.file_handler.read_file(import_config)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ['name', 'phone_number', 'notes'])
    
    def test_read_nonexistent_file(self):
        """Test reading non-existent file."""
        import_config = ImportConfig(
            file_path='nonexistent.xlsx',
            file_type='excel'
        )
        
        df = self.file_handler.read_file(import_config)
        self.assertIsNone(df)
    
    def test_write_with_invalid_type(self):
        """Test writing with invalid file type."""
        export_config = ExportConfig(
            file_path='test.pdf',
            file_type='pdf'
        )
        
        success = self.file_handler.write_file(self.test_data, export_config)
        self.assertFalse(success)
    
    def test_get_file_info(self):
        """Test getting file information."""
        # Create a temporary file
        temp_file = os.path.join(self.temp_dir, 'test.txt')
        with open(temp_file, 'w') as f:
            f.write('test content')
        
        file_info = self.file_handler.get_file_info(temp_file)
        
        self.assertIsNotNone(file_info)
        self.assertEqual(file_info['file_name'], 'test.txt')
        self.assertEqual(file_info['file_type'], 'txt')
        self.assertGreater(file_info['file_size'], 0)
        self.assertIn('created_time', file_info)
        self.assertIn('modified_time', file_info)
    
    def test_validate_dataframe(self):
        """Test DataFrame validation."""
        # Valid DataFrame
        self.assertTrue(self.file_handler.validate_dataframe(self.test_data, ['name', 'phone_number']))
        
        # Invalid DataFrame
        self.assertFalse(self.file_handler.validate_dataframe(None, ['name']))
        self.assertFalse(self.file_handler.validate_dataframe(pd.DataFrame(), ['name']))
        self.assertFalse(self.file_handler.validate_dataframe(self.test_data, ['nonexistent']))
    
    def test_clean_phone_numbers(self):
        """Test phone number cleaning."""
        # Create test data with messy phone numbers
        messy_data = pd.DataFrame({
            'phone': ['+90 555 123 4567', '(555) 123-4567', '555.123.4567', '5551234567']
        })
        
        cleaned_data = self.file_handler.clean_phone_numbers(messy_data, 'phone')
        
        # Check that all numbers start with +
        for phone in cleaned_data['phone']:
            self.assertTrue(phone.startswith('+'))
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.file_handler.get_supported_formats()
        self.assertIn('excel', formats)
        self.assertIn('txt', formats)
        self.assertIn('csv', formats)
    
    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extensions = self.file_handler.get_supported_extensions()
        self.assertIn('.xlsx', extensions)
        self.assertIn('.txt', extensions)
        self.assertIn('.csv', extensions)


class TestDataConverter(unittest.TestCase):
    """Test cases for DataConverter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.file_handler = FileHandler()
        self.converter = DataConverter(self.file_handler)
        
        # Create test data
        self.test_data = pd.DataFrame({
            'name': ['John Doe', 'Jane Smith'],
            'phone_number': ['+905551234567', '+905421234567'],
            'notes': ['Test 1', 'Test 2']
        })
    
    def test_initialization(self):
        """Test data converter initialization."""
        self.assertIsNotNone(self.converter.file_handler)
        self.assertIsNotNone(self.converter.logger)
    
    def test_dataframe_to_contacts(self):
        """Test DataFrame to Contact conversion."""
        contacts = self.converter.dataframe_to_contacts(
            self.test_data,
            name_column='name',
            phone_column='phone_number',
            notes_column='notes'
        )
        
        self.assertEqual(len(contacts), 2)
        self.assertIsInstance(contacts[0], Contact)
        self.assertEqual(contacts[0].name, 'John Doe')
        self.assertEqual(contacts[0].phone_number, '+905551234567')
        self.assertEqual(contacts[0].notes, 'Test 1')
    
    def test_dataframe_to_number_records(self):
        """Test DataFrame to NumberRecord conversion."""
        number_records = self.converter.dataframe_to_number_records(
            self.test_data,
            phone_column='phone_number',
            country_code='+90',
            notes_column='notes'
        )
        
        self.assertEqual(len(number_records), 2)
        self.assertIsInstance(number_records[0], NumberRecord)
        self.assertEqual(number_records[0].country_code, '+90')
        self.assertEqual(number_records[0].operator_prefix, '555')
        self.assertEqual(number_records[0].full_number, '+905551234567')
    
    def test_contacts_to_dataframe(self):
        """Test Contact to DataFrame conversion."""
        # Create test contacts
        contacts = [
            Contact(name='John Doe', phone_number='+905551234567', notes='Test 1'),
            Contact(name='Jane Smith', phone_number='+905421234567', notes='Test 2')
        ]
        
        df = self.converter.contacts_to_dataframe(contacts)
        
        self.assertEqual(len(df), 2)
        self.assertIn('name', df.columns)
        self.assertIn('phone_number', df.columns)
        self.assertIn('notes', df.columns)
        self.assertEqual(df.iloc[0]['name'], 'John Doe')
    
    def test_number_records_to_dataframe(self):
        """Test NumberRecord to DataFrame conversion."""
        # Create test number records
        number_records = [
            NumberRecord(
                country_code='+90',
                operator_prefix='555',
                phone_number='1234567',
                full_number='+905551234567',
                notes='Test 1'
            ),
            NumberRecord(
                country_code='+90',
                operator_prefix='542',
                phone_number='1234567',
                full_number='+905421234567',
                notes='Test 2'
            )
        ]
        
        df = self.converter.number_records_to_dataframe(number_records)
        
        self.assertEqual(len(df), 2)
        self.assertIn('country_code', df.columns)
        self.assertIn('operator_prefix', df.columns)
        self.assertIn('full_number', df.columns)
        self.assertEqual(df.iloc[0]['country_code'], '+90')
    
    def test_extract_country_and_operator(self):
        """Test country and operator extraction."""
        # Test Turkish numbers
        country, operator = self.converter._extract_country_and_operator('+905551234567')
        self.assertEqual(country, '+90')
        self.assertEqual(operator, '555')
        
        # Test US numbers
        country, operator = self.converter._extract_country_and_operator('+12025551234')
        self.assertEqual(country, '+1')
        self.assertEqual(operator, '202')
        
        # Test UK numbers
        country, operator = self.converter._extract_country_and_operator('+447700123456')
        self.assertEqual(country, '+44')
        self.assertEqual(operator, '770')
    
    def test_extract_phone_part(self):
        """Test phone part extraction."""
        # Test Turkish numbers
        phone_part = self.converter._extract_phone_part('+905551234567')
        self.assertEqual(phone_part, '1234567')
        
        # Test US numbers
        phone_part = self.converter._extract_phone_part('+12025551234')
        self.assertEqual(phone_part, '5551234')
    
    def test_validate_phone_number(self):
        """Test phone number validation."""
        # Valid numbers
        self.assertTrue(self.converter.validate_phone_number('+905551234567'))
        self.assertTrue(self.converter.validate_phone_number('+12025551234'))
        self.assertTrue(self.converter.validate_phone_number('+447700123456'))
        
        # Invalid numbers
        self.assertFalse(self.converter.validate_phone_number('5551234567'))  # No +
        self.assertFalse(self.converter.validate_phone_number('+555'))  # Too short
        self.assertFalse(self.converter.validate_phone_number('+905551234567890'))  # Too long
    
    def test_standardize_phone_number(self):
        """Test phone number standardization."""
        # Test various formats
        self.assertEqual(self.converter.standardize_phone_number('5551234567'), '+5551234567')
        self.assertEqual(self.converter.standardize_phone_number('+90 555 123 4567'), '+905551234567')
        self.assertEqual(self.converter.standardize_phone_number('(555) 123-4567'), '+5551234567')
    
    def test_get_conversion_statistics(self):
        """Test conversion statistics."""
        stats = self.converter.get_conversion_statistics(self.test_data)
        
        self.assertEqual(stats['total_rows'], 2)
        self.assertEqual(stats['total_columns'], 3)
        self.assertIn('name', stats['column_names'])
        self.assertIn('phone_number', stats['column_names'])
        self.assertIn('notes', stats['column_names'])
        self.assertIn('phone_column', stats)
        self.assertEqual(stats['phone_column'], 'phone_number')
        self.assertEqual(stats['valid_phone_numbers'], 2)
        self.assertEqual(stats['invalid_phone_numbers'], 0)


if __name__ == '__main__':
    unittest.main() 