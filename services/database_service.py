import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path
import threading
from models.phone_number import PhoneNumber
from models.validation_result import ValidationResult
from models.app_settings import AppSettings


class DatabaseException(Exception):
    """Custom exception for database-related errors."""
    pass


class DatabaseService:
    """
    Service for managing SQLite database operations for the Turkish Phone Validator.
    
    This service handles all database operations including schema creation,
    CRUD operations for phone numbers, settings management, and validation logging.
    Implements connection pooling and proper error handling.
    """
    
    def __init__(self, db_path: str = "turkish_phone_validator.db"):
        """
        Initialize the database service.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
        # Ensure database directory exists
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise DatabaseException(f"Cannot create database directory: {e}")
        
        # Initialize database schema
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database schema and indexes."""
        try:
            with self._get_connection() as conn:
                self._create_tables(conn)
                self._create_indexes(conn)
                self.logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise DatabaseException(f"Database initialization failed: {e}")
    
    @contextmanager
    def _get_connection(self):
        """
        Get a database connection with proper error handling and cleanup.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row  # Enable column access by name
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            conn.execute("PRAGMA journal_mode = WAL")  # Enable WAL mode for better concurrency
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise DatabaseException(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def _create_tables(self, conn: sqlite3.Connection) -> None:
        """
        Create database tables if they don't exist.
        
        Args:
            conn: Database connection
        """
        # Phones table - stores phone numbers and their validation status
        conn.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE NOT NULL,
                name TEXT,
                is_valid BOOLEAN,
                checked_date TIMESTAMP,
                operator_code TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Settings table - stores application configuration
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Validation logs table - stores detailed validation attempt logs
        conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                validation_result BOOLEAN,
                response_time REAL,
                error_message TEXT,
                validation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (phone_number) REFERENCES phones (number)
            )
        """)
        
        conn.commit()
        self.logger.debug("Database tables created successfully")
    
    def _create_indexes(self, conn: sqlite3.Connection) -> None:
        """
        Create database indexes for performance optimization.
        
        Args:
            conn: Database connection
        """
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_phones_number ON phones(number)",
            "CREATE INDEX IF NOT EXISTS idx_phones_is_valid ON phones(is_valid)",
            "CREATE INDEX IF NOT EXISTS idx_phones_checked_date ON phones(checked_date)",
            "CREATE INDEX IF NOT EXISTS idx_phones_operator_code ON phones(operator_code)",
            "CREATE INDEX IF NOT EXISTS idx_validation_logs_phone_number ON validation_logs(phone_number)",
            "CREATE INDEX IF NOT EXISTS idx_validation_logs_validation_date ON validation_logs(validation_date)",
            "CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
        
        conn.commit()
        self.logger.debug("Database indexes created successfully")
    
    def save_phone_number(self, phone: PhoneNumber) -> bool:
        """
        Save or update a phone number in the database.
        
        Args:
            phone: PhoneNumber object to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO phones 
                        (number, name, is_valid, checked_date, operator_code, created_date)
                        VALUES (?, ?, ?, ?, ?, COALESCE(
                            (SELECT created_date FROM phones WHERE number = ?), 
                            CURRENT_TIMESTAMP
                        ))
                    """, (
                        phone.number,
                        phone.name,
                        phone.is_valid,
                        phone.checked_date,
                        phone.operator_code,
                        phone.number  # For the COALESCE subquery
                    ))
                    conn.commit()
                    self.logger.debug(f"Saved phone number: {phone.number}")
                    return True
            except Exception as e:
                self.logger.error(f"Failed to save phone number {phone.number}: {e}")
                return False
    
    def get_phone_number(self, number: str) -> Optional[PhoneNumber]:
        """
        Retrieve a phone number from the database.
        
        Args:
            number: Phone number to retrieve
            
        Returns:
            Optional[PhoneNumber]: PhoneNumber object if found, None otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM phones WHERE number = ?", (number,)
                )
                row = cursor.fetchone()
                
                if row:
                    return PhoneNumber(
                        number=row['number'],
                        name=row['name'],
                        is_valid=row['is_valid'],
                        checked_date=datetime.fromisoformat(row['checked_date']) if row['checked_date'] else None,
                        operator_code=row['operator_code'] or ""
                    )
                return None
        except Exception as e:
            self.logger.error(f"Failed to get phone number {number}: {e}")
            return None
    
    def is_number_checked(self, number: str) -> bool:
        """
        Check if a phone number has already been validated.
        
        Args:
            number: Phone number to check
            
        Returns:
            bool: True if number has been checked, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT is_valid FROM phones WHERE number = ? AND checked_date IS NOT NULL",
                    (number,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Failed to check if number is validated {number}: {e}")
            return False
    
    def get_all_valid_numbers(self) -> List[PhoneNumber]:
        """
        Get all valid (Telegram registered) phone numbers.
        
        Returns:
            List[PhoneNumber]: List of valid phone numbers
        """
        return self._get_numbers_by_validity(True)
    
    def get_all_invalid_numbers(self) -> List[PhoneNumber]:
        """
        Get all invalid (not Telegram registered) phone numbers.
        
        Returns:
            List[PhoneNumber]: List of invalid phone numbers
        """
        return self._get_numbers_by_validity(False)
    
    def _get_numbers_by_validity(self, is_valid: bool) -> List[PhoneNumber]:
        """
        Get phone numbers filtered by validity status.
        
        Args:
            is_valid: True for valid numbers, False for invalid
            
        Returns:
            List[PhoneNumber]: List of phone numbers matching the validity filter
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM phones WHERE is_valid = ? ORDER BY checked_date DESC",
                    (is_valid,)
                )
                
                numbers = []
                for row in cursor.fetchall():
                    numbers.append(PhoneNumber(
                        number=row['number'],
                        name=row['name'],
                        is_valid=row['is_valid'],
                        checked_date=datetime.fromisoformat(row['checked_date']) if row['checked_date'] else None,
                        operator_code=row['operator_code'] or ""
                    ))
                
                return numbers
        except Exception as e:
            self.logger.error(f"Failed to get numbers by validity {is_valid}: {e}")
            return []
    
    def search_numbers(self, query: str) -> List[PhoneNumber]:
        """
        Search phone numbers by number or name.
        
        Args:
            query: Search query (can match number or name)
            
        Returns:
            List[PhoneNumber]: List of matching phone numbers
        """
        if not query.strip():
            return []
        
        try:
            with self._get_connection() as conn:
                # Search in both number and name fields
                cursor = conn.execute("""
                    SELECT * FROM phones 
                    WHERE number LIKE ? OR name LIKE ?
                    ORDER BY checked_date DESC
                    LIMIT 100
                """, (f"%{query}%", f"%{query}%"))
                
                numbers = []
                for row in cursor.fetchall():
                    numbers.append(PhoneNumber(
                        number=row['number'],
                        name=row['name'],
                        is_valid=row['is_valid'],
                        checked_date=datetime.fromisoformat(row['checked_date']) if row['checked_date'] else None,
                        operator_code=row['operator_code'] or ""
                    ))
                
                return numbers
        except Exception as e:
            self.logger.error(f"Failed to search numbers with query '{query}': {e}")
            return []
    
    def get_all_numbers(self, limit: Optional[int] = None) -> List[PhoneNumber]:
        """
        Get all phone numbers from the database.
        
        Args:
            limit: Optional limit on number of results
            
        Returns:
            List[PhoneNumber]: List of all phone numbers
        """
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM phones ORDER BY checked_date DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor = conn.execute(query)
                
                numbers = []
                for row in cursor.fetchall():
                    numbers.append(PhoneNumber(
                        number=row['number'],
                        name=row['name'],
                        is_valid=row['is_valid'],
                        checked_date=datetime.fromisoformat(row['checked_date']) if row['checked_date'] else None,
                        operator_code=row['operator_code'] or ""
                    ))
                
                return numbers
        except Exception as e:
            self.logger.error(f"Failed to get all numbers: {e}")
            return []
    
    def save_validation_log(self, validation_result: ValidationResult) -> bool:
        """
        Save a validation attempt log to the database.
        
        Args:
            validation_result: ValidationResult object to log
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO validation_logs 
                    (phone_number, validation_result, response_time, error_message, validation_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    validation_result.phone_number.number,
                    validation_result.is_telegram_registered,
                    validation_result.response_time,
                    validation_result.error_message,
                    validation_result.validation_date
                ))
                conn.commit()
                self.logger.debug(f"Saved validation log for: {validation_result.phone_number.number}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to save validation log: {e}")
            return False
    
    def get_validation_logs(self, phone_number: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get validation logs from the database.
        
        Args:
            phone_number: Optional phone number to filter logs
            limit: Maximum number of logs to return
            
        Returns:
            List[Dict[str, Any]]: List of validation log dictionaries
        """
        try:
            with self._get_connection() as conn:
                if phone_number:
                    cursor = conn.execute("""
                        SELECT * FROM validation_logs 
                        WHERE phone_number = ?
                        ORDER BY validation_date DESC
                        LIMIT ?
                    """, (phone_number, limit))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM validation_logs 
                        ORDER BY validation_date DESC
                        LIMIT ?
                    """, (limit,))
                
                logs = []
                for row in cursor.fetchall():
                    logs.append({
                        'id': row['id'],
                        'phone_number': row['phone_number'],
                        'validation_result': row['validation_result'],
                        'response_time': row['response_time'],
                        'error_message': row['error_message'],
                        'validation_date': row['validation_date']
                    })
                
                return logs
        except Exception as e:
            self.logger.error(f"Failed to get validation logs: {e}")
            return []
    
    def save_setting(self, key: str, value: str) -> bool:
        """
        Save a setting to the database.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO settings (key, value, updated_date)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, value))
                conn.commit()
                self.logger.debug(f"Saved setting: {key}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to save setting {key}: {e}")
            return False
    
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a setting from the database.
        
        Args:
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Optional[str]: Setting value or default
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                return row['value'] if row else default
        except Exception as e:
            self.logger.error(f"Failed to get setting {key}: {e}")
            return default
    
    def save_app_settings(self, settings: AppSettings) -> bool:
        """
        Save application settings to the database.
        
        Args:
            settings: AppSettings object to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            settings_dict = settings.to_dict()
            success = True
            
            for key, value in settings_dict.items():
                if not self.save_setting(f"app_{key}", str(value)):
                    success = False
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to save app settings: {e}")
            return False
    
    def load_app_settings(self) -> AppSettings:
        """
        Load application settings from the database.
        
        Returns:
            AppSettings: Loaded settings or default settings if not found
        """
        try:
            settings_data = {}
            
            # Load all app settings from database
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT key, value FROM settings WHERE key LIKE 'app_%'")
                for row in cursor.fetchall():
                    # Remove 'app_' prefix from key
                    clean_key = row['key'][4:]
                    value = row['value']
                    
                    # Convert string values back to appropriate types
                    if clean_key in ['parallel_threads', 'rate_limit_min', 'rate_limit_max', 'max_retries', 'timeout_seconds']:
                        settings_data[clean_key] = int(value)
                    elif clean_key in ['dark_mode', 'auto_save_results']:
                        settings_data[clean_key] = value.lower() == 'true'
                    else:
                        settings_data[clean_key] = value
            
            return AppSettings.from_dict(settings_data) if settings_data else AppSettings()
        except Exception as e:
            self.logger.error(f"Failed to load app settings: {e}")
            return AppSettings()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict[str, Any]: Dictionary containing various statistics
        """
        try:
            with self._get_connection() as conn:
                stats = {}
                
                # Total numbers
                cursor = conn.execute("SELECT COUNT(*) as total FROM phones")
                stats['total_numbers'] = cursor.fetchone()['total']
                
                # Valid numbers
                cursor = conn.execute("SELECT COUNT(*) as valid FROM phones WHERE is_valid = 1")
                stats['valid_numbers'] = cursor.fetchone()['valid']
                
                # Invalid numbers
                cursor = conn.execute("SELECT COUNT(*) as invalid FROM phones WHERE is_valid = 0")
                stats['invalid_numbers'] = cursor.fetchone()['invalid']
                
                # Unchecked numbers
                cursor = conn.execute("SELECT COUNT(*) as unchecked FROM phones WHERE is_valid IS NULL")
                stats['unchecked_numbers'] = cursor.fetchone()['unchecked']
                
                # Total validation attempts
                cursor = conn.execute("SELECT COUNT(*) as total_validations FROM validation_logs")
                stats['total_validations'] = cursor.fetchone()['total_validations']
                
                # Average response time
                cursor = conn.execute("SELECT AVG(response_time) as avg_response_time FROM validation_logs WHERE error_message IS NULL")
                avg_time = cursor.fetchone()['avg_response_time']
                stats['avg_response_time'] = round(avg_time, 2) if avg_time else 0
                
                # Most recent validation
                cursor = conn.execute("SELECT MAX(validation_date) as last_validation FROM validation_logs")
                stats['last_validation'] = cursor.fetchone()['last_validation']
                
                return stats
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def batch_save_phone_numbers(self, phones: List[PhoneNumber]) -> int:
        """
        Save multiple phone numbers in a batch operation for better performance.
        
        Args:
            phones: List of PhoneNumber objects to save
            
        Returns:
            int: Number of successfully saved phone numbers
        """
        if not phones:
            return 0
        
        saved_count = 0
        with self._lock:
            try:
                with self._get_connection() as conn:
                    # Prepare batch data
                    batch_data = []
                    for phone in phones:
                        batch_data.append((
                            phone.number,
                            phone.name,
                            phone.is_valid,
                            phone.checked_date,
                            phone.operator_code
                        ))
                    
                    # Execute batch insert
                    conn.executemany("""
                        INSERT OR REPLACE INTO phones 
                        (number, name, is_valid, checked_date, operator_code)
                        VALUES (?, ?, ?, ?, ?)
                    """, batch_data)
                    
                    conn.commit()
                    saved_count = len(batch_data)
                    self.logger.info(f"Batch saved {saved_count} phone numbers")
                    
            except Exception as e:
                self.logger.error(f"Failed to batch save phone numbers: {e}")
        
        return saved_count
    
    def delete_phone_number(self, number: str) -> bool:
        """
        Delete a phone number and its associated validation logs.
        
        Args:
            number: Phone number to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    # Delete validation logs first (foreign key constraint)
                    conn.execute("DELETE FROM validation_logs WHERE phone_number = ?", (number,))
                    
                    # Delete phone number
                    cursor = conn.execute("DELETE FROM phones WHERE number = ?", (number,))
                    conn.commit()
                    
                    deleted = cursor.rowcount > 0
                    if deleted:
                        self.logger.debug(f"Deleted phone number: {number}")
                    
                    return deleted
            except Exception as e:
                self.logger.error(f"Failed to delete phone number {number}: {e}")
                return False
    
    def clear_all_data(self) -> bool:
        """
        Clear all data from the database (phones and validation logs).
        Settings are preserved.
        
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    conn.execute("DELETE FROM validation_logs")
                    conn.execute("DELETE FROM phones")
                    conn.commit()
                    self.logger.info("Cleared all phone data from database")
                    return True
            except Exception as e:
                self.logger.error(f"Failed to clear database: {e}")
                return False
    
    def close(self) -> None:
        """
        Close the database service and clean up resources.
        This method is called when the application shuts down.
        """
        self.logger.info("Database service closed")