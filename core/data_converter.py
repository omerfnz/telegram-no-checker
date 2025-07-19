"""
Data converter for transforming between different data formats.

This module handles conversion between DataFrames and application models.
"""

import pandas as pd
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from data.models import Contact, NumberRecord
from .file_handler import FileHandler


class DataConverter:
    """
    Converts data between different formats.
    
    This class handles:
    - DataFrame to Contact conversion
    - DataFrame to NumberRecord conversion
    - Contact/NumberRecord to DataFrame conversion
    - Data validation and cleaning
    - Format standardization
    """
    
    def __init__(self, file_handler: Optional[FileHandler] = None):
        """
        Initialize the data converter.
        
        Args:
            file_handler: Optional file handler for additional operations
        """
        self.file_handler = file_handler or FileHandler()
        self.logger = logging.getLogger(__name__)
    
    def dataframe_to_contacts(
        self,
        df: pd.DataFrame,
        name_column: str = 'name',
        phone_column: str = 'phone_number',
        notes_column: Optional[str] = None
    ) -> List[Contact]:
        """
        Convert DataFrame to list of Contact objects.
        
        Args:
            df: DataFrame to convert
            name_column: Name of the name column
            phone_column: Name of the phone number column
            notes_column: Name of the notes column (optional)
            
        Returns:
            List[Contact]: List of Contact objects
        """
        contacts = []
        
        try:
            # Validate required columns
            required_columns = [name_column, phone_column]
            if not self.file_handler.validate_dataframe(df, required_columns):
                return contacts
            
            # Clean phone numbers
            df = self.file_handler.clean_phone_numbers(df, phone_column)
            
            # Convert each row to Contact
            for index, row in df.iterrows():
                try:
                    contact = Contact(
                        name=str(row[name_column]).strip(),
                        phone_number=str(row[phone_column]).strip(),
                        notes=str(row[notes_column]).strip() if notes_column and notes_column in df.columns else "",
                        is_valid=False,
                        last_checked=None
                    )
                    contacts.append(contact)
                    
                except Exception as e:
                    self.logger.warning(f"Error converting row {index} to Contact: {e}")
                    continue
            
            self.logger.info(f"Successfully converted {len(contacts)} contacts from DataFrame")
            
        except Exception as e:
            self.logger.error(f"Error converting DataFrame to contacts: {e}")
        
        return contacts
    
    def dataframe_to_number_records(
        self,
        df: pd.DataFrame,
        phone_column: str = 'phone_number',
        country_code: Optional[str] = None,
        operator_column: Optional[str] = None,
        notes_column: Optional[str] = None
    ) -> List[NumberRecord]:
        """
        Convert DataFrame to list of NumberRecord objects.
        
        Args:
            df: DataFrame to convert
            phone_column: Name of the phone number column
            country_code: Default country code to use
            operator_column: Name of the operator column (optional)
            notes_column: Name of the notes column (optional)
            
        Returns:
            List[NumberRecord]: List of NumberRecord objects
        """
        number_records = []
        
        try:
            # Validate required columns
            required_columns = [phone_column]
            if not self.file_handler.validate_dataframe(df, required_columns):
                return number_records
            
            # Clean phone numbers
            df = self.file_handler.clean_phone_numbers(df, phone_column)
            
            # Convert each row to NumberRecord
            for index, row in df.iterrows():
                try:
                    phone_number = str(row[phone_column]).strip()
                    
                    # Extract country code and operator prefix
                    extracted_country, extracted_operator = self._extract_country_and_operator(phone_number)
                    
                    # Use provided values or extracted ones
                    final_country = country_code or extracted_country
                    final_operator = (
                        str(row[operator_column]).strip() if operator_column and operator_column in df.columns
                        else extracted_operator
                    )
                    
                    # Create number record
                    number_record = NumberRecord(
                        country_code=final_country,
                        operator_prefix=final_operator,
                        phone_number=self._extract_phone_part(phone_number),
                        full_number=phone_number,
                        notes=str(row[notes_column]).strip() if notes_column and notes_column in df.columns else "",
                        is_checked=False
                    )
                    number_records.append(number_record)
                    
                except Exception as e:
                    self.logger.warning(f"Error converting row {index} to NumberRecord: {e}")
                    continue
            
            self.logger.info(f"Successfully converted {len(number_records)} number records from DataFrame")
            
        except Exception as e:
            self.logger.error(f"Error converting DataFrame to number records: {e}")
        
        return number_records
    
    def contacts_to_dataframe(self, contacts: List[Contact]) -> pd.DataFrame:
        """
        Convert list of Contact objects to DataFrame.
        
        Args:
            contacts: List of Contact objects
            
        Returns:
            pd.DataFrame: DataFrame with contact data
        """
        try:
            data = []
            
            for contact in contacts:
                data.append({
                    'id': contact.id,
                    'name': contact.name,
                    'phone_number': contact.phone_number,
                    'is_valid': contact.is_valid,
                    'last_checked': contact.last_checked.isoformat() if contact.last_checked else None,
                    'notes': contact.notes,
                    'created_at': contact.created_at.isoformat() if contact.created_at else None,
                    'updated_at': contact.updated_at.isoformat() if contact.updated_at else None
                })
            
            df = pd.DataFrame(data)
            self.logger.info(f"Successfully converted {len(contacts)} contacts to DataFrame")
            return df
            
        except Exception as e:
            self.logger.error(f"Error converting contacts to DataFrame: {e}")
            return pd.DataFrame()
    
    def number_records_to_dataframe(self, number_records: List[NumberRecord]) -> pd.DataFrame:
        """
        Convert list of NumberRecord objects to DataFrame.
        
        Args:
            number_records: List of NumberRecord objects
            
        Returns:
            pd.DataFrame: DataFrame with number record data
        """
        try:
            data = []
            
            for record in number_records:
                data.append({
                    'id': record.id,
                    'country_code': record.country_code,
                    'operator_prefix': record.operator_prefix,
                    'phone_number': record.phone_number,
                    'full_number': record.full_number,
                    'is_valid': record.is_valid,
                    'is_checked': record.is_checked,
                    'check_date': record.check_date.isoformat() if record.check_date else None,
                    'check_count': record.check_count,
                    'notes': record.notes,
                    'created_at': record.created_at.isoformat() if record.created_at else None,
                    'updated_at': record.updated_at.isoformat() if record.updated_at else None
                })
            
            df = pd.DataFrame(data)
            self.logger.info(f"Successfully converted {len(number_records)} number records to DataFrame")
            return df
            
        except Exception as e:
            self.logger.error(f"Error converting number records to DataFrame: {e}")
            return pd.DataFrame()
    
    def _extract_country_and_operator(self, phone_number: str) -> tuple[str, str]:
        """
        Extract country code and operator prefix from phone number.
        
        Args:
            phone_number: Full phone number
            
        Returns:
            tuple[str, str]: (country_code, operator_prefix)
        """
        try:
            # Remove any non-digit characters except +
            clean_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            # Known country codes
            country_codes = ['+90', '+1', '+44', '+49', '+33', '+39', '+34', '+31']
            
            for country_code in country_codes:
                if clean_number.startswith(country_code):
                    # Extract operator prefix (next 3-4 digits)
                    remaining = clean_number[len(country_code):]
                    if len(remaining) >= 3:
                        operator_prefix = remaining[:3]
                        return country_code, operator_prefix
            
            # Default to +90 if no match found
            if clean_number.startswith('+'):
                remaining = clean_number[1:]
                if len(remaining) >= 3:
                    operator_prefix = remaining[:3]
                    return '+90', operator_prefix
            
            return '+90', '000'
            
        except Exception as e:
            self.logger.error(f"Error extracting country and operator from {phone_number}: {e}")
            return '+90', '000'
    
    def _extract_phone_part(self, phone_number: str) -> str:
        """
        Extract phone number part (without country code and operator).
        
        Args:
            phone_number: Full phone number
            
        Returns:
            str: Phone number part
        """
        try:
            # Remove any non-digit characters except +
            clean_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            # Known country codes
            country_codes = ['+90', '+1', '+44', '+49', '+33', '+39', '+34', '+31']
            
            for country_code in country_codes:
                if clean_number.startswith(country_code):
                    # Remove country code and operator prefix
                    remaining = clean_number[len(country_code):]
                    if len(remaining) >= 3:
                        return remaining[3:]  # Remove operator prefix
            
            # Default handling
            if clean_number.startswith('+'):
                remaining = clean_number[1:]
                if len(remaining) >= 3:
                    return remaining[3:]  # Remove operator prefix
            
            return clean_number
            
        except Exception as e:
            self.logger.error(f"Error extracting phone part from {phone_number}: {e}")
            return phone_number
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Remove any non-digit characters except +
            clean_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            # Check if it starts with +
            if not clean_number.startswith('+'):
                return False
            
            # Check minimum length (country code + operator + number)
            if len(clean_number) < 10:
                return False
            
            # Check maximum length
            if len(clean_number) > 15:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating phone number {phone_number}: {e}")
            return False
    
    def standardize_phone_number(self, phone_number: str) -> str:
        """
        Standardize phone number format.
        
        Args:
            phone_number: Phone number to standardize
            
        Returns:
            str: Standardized phone number
        """
        try:
            # Remove all non-digit characters except +
            clean_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            # Ensure it starts with +
            if not clean_number.startswith('+'):
                clean_number = '+' + clean_number
            
            return clean_number
            
        except Exception as e:
            self.logger.error(f"Error standardizing phone number {phone_number}: {e}")
            return phone_number
    
    def get_conversion_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistics about DataFrame conversion.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dict[str, Any]: Conversion statistics
        """
        try:
            stats = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'column_names': list(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'data_types': df.dtypes.to_dict()
            }
            
            # Phone number statistics if phone column exists
            phone_columns = [col for col in df.columns if 'phone' in col.lower() or 'numara' in col.lower()]
            if phone_columns:
                phone_col = phone_columns[0]
                stats['phone_column'] = phone_col
                stats['valid_phone_numbers'] = sum(
                    self.validate_phone_number(str(phone)) 
                    for phone in df[phone_col] if pd.notna(phone)
                )
                stats['invalid_phone_numbers'] = len(df) - stats['valid_phone_numbers']
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting conversion statistics: {e}")
            return {} 