"""
Bulk number generator service.

This module handles bulk number generation and database integration.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from .number_generator import NumberGenerator, GenerationConfig
from data.models import NumberRecord, CheckSession
from data.database import DatabaseManager


class BulkGenerator:
    """
    Service for bulk number generation and database integration.
    
    This class handles:
    - Large-scale number generation
    - Database batch insertion
    - Progress tracking
    - Session management
    """
    
    def __init__(self, database: DatabaseManager):
        """
        Initialize the bulk generator.
        
        Args:
            database: Database manager for storing generated numbers
        """
        self.database = database
        self.number_generator = NumberGenerator(database)
        self.logger = logging.getLogger(__name__)
        
        # Progress tracking
        self.total_to_generate = 0
        self.generated_count = 0
        self.saved_count = 0
        self.failed_count = 0
        
        # Callbacks
        self.progress_callback: Optional[Callable] = None
        self.completion_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable) -> None:
        """
        Set progress callback function.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback
    
    def set_completion_callback(self, callback: Callable) -> None:
        """
        Set completion callback function.
        
        Args:
            callback: Function to call when generation is complete
        """
        self.completion_callback = callback
    
    def _update_progress(self) -> None:
        """Update progress and call callback if set."""
        if self.progress_callback:
            progress_data = {
                'total': self.total_to_generate,
                'generated': self.generated_count,
                'saved': self.saved_count,
                'failed': self.failed_count,
                'percentage': (self.generated_count / self.total_to_generate * 100) if self.total_to_generate > 0 else 0
            }
            self.progress_callback(progress_data)
    
    def generate_and_save_batch(
        self,
        config: GenerationConfig,
        session_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate numbers and save them to database.
        
        Args:
            config: Generation configuration
            session_name: Optional session name for tracking
            
        Returns:
            Dict[str, Any]: Generation results
        """
        # Create check session if session name provided
        session_id = None
        if session_name:
            session = CheckSession(
                session_name=session_name,
                country_code=config.country_code,
                operator_prefixes=config.operator_prefixes,
                total_numbers=config.batch_size,
                status="generating"
            )
            session_id = self.database.create_check_session(session)
        
        try:
            # Generate numbers
            generated_numbers = self.number_generator.generate_numbers_batch(config)
            
            # Save to database
            saved_count = 0
            failed_count = 0
            
            for number_record in generated_numbers:
                try:
                    self.database.create_number_record(number_record)
                    saved_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to save number {number_record.full_number}: {e}")
                    failed_count += 1
            
            # Update session if exists
            if session_id:
                session = self.database.get_check_session(session_id)
                if session:
                    session.total_numbers = len(generated_numbers)
                    session.checked_numbers = 0
                    session.status = "ready"
                    self.database.update_check_session(session)
            
            # Update statistics
            self.generated_count += len(generated_numbers)
            self.saved_count += saved_count
            self.failed_count += failed_count
            
            self._update_progress()
            
            return {
                'total_generated': len(generated_numbers),
                'saved_count': saved_count,
                'failed_count': failed_count,
                'session_id': session_id
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk generation: {e}")
            self.failed_count += config.batch_size
            
            # Update session status to error
            if session_id:
                session = self.database.get_check_session(session_id)
                if session:
                    session.status = "error"
                    self.database.update_check_session(session)
            
            return {
                'total_generated': 0,
                'saved_count': 0,
                'failed_count': config.batch_size,
                'session_id': session_id,
                'error': str(e)
            }
    
    def generate_for_multiple_operators(
        self,
        country_code: str,
        operators: Dict[str, int],  # operator_prefix -> count
        session_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate numbers for multiple operators with different counts.
        
        Args:
            country_code: Country code
            operators: Dictionary mapping operator prefixes to counts
            session_name: Optional session name
            
        Returns:
            Dict[str, Any]: Generation results
        """
        total_count = sum(operators.values())
        self.total_to_generate = total_count
        
        # Create check session
        session_id = None
        if session_name:
            session = CheckSession(
                session_name=session_name,
                country_code=country_code,
                operator_prefixes=list(operators.keys()),
                total_numbers=total_count,
                status="generating"
            )
            session_id = self.database.create_check_session(session)
        
        total_generated = 0
        total_saved = 0
        total_failed = 0
        
        try:
            for operator_prefix, count in operators.items():
                self.logger.info(f"Generating {count} numbers for {country_code} {operator_prefix}")
                
                # Generate numbers for this operator
                numbers = self.number_generator.generate_numbers_for_operator(
                    country_code=country_code,
                    operator_prefix=operator_prefix,
                    count=count,
                    exclude_existing=True
                )
                
                # Save to database
                saved_count = 0
                for number_record in numbers:
                    try:
                        self.database.create_number_record(number_record)
                        saved_count += 1
                    except Exception as e:
                        self.logger.error(f"Failed to save number {number_record.full_number}: {e}")
                        total_failed += 1
                
                total_generated += len(numbers)
                total_saved += saved_count
                
                # Update progress
                self.generated_count = total_generated
                self.saved_count = total_saved
                self.failed_count = total_failed
                self._update_progress()
            
            # Update session
            if session_id:
                session = self.database.get_check_session(session_id)
                if session:
                    session.total_numbers = total_generated
                    session.checked_numbers = 0
                    session.status = "ready"
                    self.database.update_check_session(session)
            
            return {
                'total_generated': total_generated,
                'saved_count': total_saved,
                'failed_count': total_failed,
                'session_id': session_id
            }
            
        except Exception as e:
            self.logger.error(f"Error in multi-operator generation: {e}")
            
            # Update session status to error
            if session_id:
                session = self.database.get_check_session(session_id)
                if session:
                    session.status = "error"
                    self.database.update_check_session(session)
            
            return {
                'total_generated': total_generated,
                'saved_count': total_saved,
                'failed_count': total_failed + (total_count - total_generated),
                'session_id': session_id,
                'error': str(e)
            }
    
    def generate_pattern_batch(
        self,
        country_code: str,
        operator_prefix: str,
        pattern: str,
        count: int,
        session_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate numbers based on pattern and save to database.
        
        Args:
            country_code: Country code
            operator_prefix: Operator prefix
            pattern: Number pattern
            count: Number of numbers to generate
            session_name: Optional session name
            
        Returns:
            Dict[str, Any]: Generation results
        """
        self.total_to_generate = count
        
        # Create check session
        session_id = None
        if session_name:
            session = CheckSession(
                session_name=session_name,
                country_code=country_code,
                operator_prefixes=[operator_prefix],
                total_numbers=count,
                status="generating"
            )
            session_id = self.database.create_check_session(session)
        
        try:
            # Generate pattern numbers
            generated_numbers = self.number_generator.generate_pattern_numbers(
                country_code=country_code,
                operator_prefix=operator_prefix,
                pattern=pattern,
                count=count
            )
            
            # Save to database
            saved_count = 0
            failed_count = 0
            
            for number_record in generated_numbers:
                try:
                    self.database.create_number_record(number_record)
                    saved_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to save pattern number {number_record.full_number}: {e}")
                    failed_count += 1
            
            # Update statistics
            self.generated_count += len(generated_numbers)
            self.saved_count += saved_count
            self.failed_count += failed_count
            
            # Update session
            if session_id:
                session = self.database.get_check_session(session_id)
                if session:
                    session.total_numbers = len(generated_numbers)
                    session.checked_numbers = 0
                    session.status = "ready"
                    self.database.update_check_session(session)
            
            self._update_progress()
            
            return {
                'total_generated': len(generated_numbers),
                'saved_count': saved_count,
                'failed_count': failed_count,
                'session_id': session_id
            }
            
        except Exception as e:
            self.logger.error(f"Error in pattern generation: {e}")
            self.failed_count += count
            
            # Update session status to error
            if session_id:
                session = self.database.get_check_session(session_id)
                if session:
                    session.status = "error"
                    self.database.update_check_session(session)
            
            return {
                'total_generated': 0,
                'saved_count': 0,
                'failed_count': count,
                'session_id': session_id,
                'error': str(e)
            }
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Get bulk generation statistics.
        
        Returns:
            Dict[str, Any]: Generation statistics
        """
        return {
            'total_generated': self.generated_count,
            'total_saved': self.saved_count,
            'total_failed': self.failed_count,
            'success_rate': (
                (self.saved_count / self.generated_count * 100)
                if self.generated_count > 0 else 0
            ),
            'generator_stats': self.number_generator.get_generation_statistics()
        }
    
    def reset(self) -> None:
        """Reset the bulk generator state."""
        self.total_to_generate = 0
        self.generated_count = 0
        self.saved_count = 0
        self.failed_count = 0
        self.number_generator.reset()
        self.logger.info("Bulk generator reset") 