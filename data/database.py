"""
Database management for Telegram Analyzer Tool.

This module handles all database operations including:
- Database initialization
- Table creation and migration
- CRUD operations for all models
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager

from .models import Contact, NumberRecord, CheckSession


class DatabaseManager:
    """
    SQLite database manager for Telegram Analyzer Tool.
    
    This class handles all database operations including:
    - Database initialization and migration
    - CRUD operations for contacts, number records, and check sessions
    - Connection management and error handling
    """
    
    def __init__(self, db_path: str = "telegram_analyzer.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection with proper error handling.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable row factory for named columns
            yield conn
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _init_database(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        self.logger.info("Initializing database...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone_number TEXT NOT NULL UNIQUE,
                    is_valid BOOLEAN,
                    last_checked DATETIME,
                    notes TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create number_records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS number_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    country_code TEXT NOT NULL,
                    operator_prefix TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    full_number TEXT NOT NULL UNIQUE,
                    is_valid BOOLEAN,
                    is_checked BOOLEAN DEFAULT 0,
                    check_date DATETIME,
                    check_count INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create check_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS check_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    country_code TEXT NOT NULL,
                    operator_prefixes TEXT NOT NULL,  -- JSON array
                    total_numbers INTEGER DEFAULT 0,
                    checked_numbers INTEGER DEFAULT 0,
                    valid_numbers INTEGER DEFAULT 0,
                    invalid_numbers INTEGER DEFAULT 0,
                    start_time DATETIME,
                    end_time DATETIME,
                    status TEXT DEFAULT 'created',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_valid ON contacts(is_valid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_number_records_country ON number_records(country_code)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_number_records_operator ON number_records(operator_prefix)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_number_records_checked ON number_records(is_checked)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_number_records_valid ON number_records(is_valid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_number_records_full ON number_records(full_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_check_sessions_status ON check_sessions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_check_sessions_country ON check_sessions(country_code)")
            
            conn.commit()
            self.logger.info("Database initialized successfully")
    
    # Contact CRUD Operations
    def create_contact(self, contact: Contact) -> int:
        """
        Create a new contact in the database.
        
        Args:
            contact: Contact object to create
            
        Returns:
            int: ID of the created contact
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (name, phone_number, is_valid, last_checked, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                contact.name,
                contact.phone_number,
                contact.is_valid,
                contact.last_checked,
                contact.notes,
                contact.created_at,
                contact.updated_at
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_contact(self, contact_id: int) -> Optional[Contact]:
        """
        Get a contact by ID.
        
        Args:
            contact_id: ID of the contact to retrieve
            
        Returns:
            Optional[Contact]: Contact object or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            if row:
                return Contact(
                    id=row['id'],
                    name=row['name'],
                    phone_number=row['phone_number'],
                    is_valid=row['is_valid'],
                    last_checked=datetime.fromisoformat(row['last_checked']) if row['last_checked'] else None,
                    notes=row['notes'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
            return None
    
    def get_contact_by_phone(self, phone_number: str) -> Optional[Contact]:
        """
        Get a contact by phone number.
        
        Args:
            phone_number: Phone number to search for
            
        Returns:
            Optional[Contact]: Contact object or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE phone_number = ?", (phone_number,))
            row = cursor.fetchone()
            
            if row:
                return Contact(
                    id=row['id'],
                    name=row['name'],
                    phone_number=row['phone_number'],
                    is_valid=row['is_valid'],
                    last_checked=datetime.fromisoformat(row['last_checked']) if row['last_checked'] else None,
                    notes=row['notes'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
            return None
    
    def get_all_contacts(self, limit: Optional[int] = None, offset: int = 0) -> List[Contact]:
        """
        Get all contacts with optional pagination.
        
        Args:
            limit: Maximum number of contacts to return
            offset: Number of contacts to skip
            
        Returns:
            List[Contact]: List of contact objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if limit:
                cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
            else:
                cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
            
            contacts = []
            for row in cursor.fetchall():
                contact = Contact(
                    id=row['id'],
                    name=row['name'],
                    phone_number=row['phone_number'],
                    is_valid=row['is_valid'],
                    last_checked=datetime.fromisoformat(row['last_checked']) if row['last_checked'] else None,
                    notes=row['notes'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                contacts.append(contact)
            
            return contacts
    
    def update_contact(self, contact: Contact) -> bool:
        """
        Update an existing contact.
        
        Args:
            contact: Contact object with updated data
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not contact.id:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts 
                SET name = ?, phone_number = ?, is_valid = ?, last_checked = ?, notes = ?, updated_at = ?
                WHERE id = ?
            """, (
                contact.name,
                contact.phone_number,
                contact.is_valid,
                contact.last_checked,
                contact.notes,
                datetime.now(),
                contact.id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_contact(self, contact_id: int) -> bool:
        """
        Delete a contact by ID.
        
        Args:
            contact_id: ID of the contact to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_contacts(self, query: str, limit: Optional[int] = None) -> List[Contact]:
        """
        Search contacts by name or phone number.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List[Contact]: List of matching contacts
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            search_query = f"%{query}%"
            
            if limit:
                cursor.execute("""
                    SELECT * FROM contacts 
                    WHERE name LIKE ? OR phone_number LIKE ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (search_query, search_query, limit))
            else:
                cursor.execute("""
                    SELECT * FROM contacts 
                    WHERE name LIKE ? OR phone_number LIKE ?
                    ORDER BY created_at DESC
                """, (search_query, search_query))
            
            contacts = []
            for row in cursor.fetchall():
                contact = Contact(
                    id=row['id'],
                    name=row['name'],
                    phone_number=row['phone_number'],
                    is_valid=row['is_valid'],
                    last_checked=datetime.fromisoformat(row['last_checked']) if row['last_checked'] else None,
                    notes=row['notes'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                contacts.append(contact)
            
            return contacts
    
    # Number Record CRUD Operations
    def create_number_record(self, number_record: NumberRecord) -> int:
        """
        Create a new number record in the database.
        
        Args:
            number_record: NumberRecord object to create
            
        Returns:
            int: ID of the created number record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO number_records (
                    country_code, operator_prefix, phone_number, full_number,
                    is_valid, is_checked, check_date, check_count, notes, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                number_record.country_code,
                number_record.operator_prefix,
                number_record.phone_number,
                number_record.full_number,
                number_record.is_valid,
                number_record.is_checked,
                number_record.check_date,
                number_record.check_count,
                number_record.notes,
                number_record.created_at,
                number_record.updated_at
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_number_record(self, record_id: int) -> Optional[NumberRecord]:
        """
        Get a number record by ID.
        
        Args:
            record_id: ID of the number record to retrieve
            
        Returns:
            Optional[NumberRecord]: NumberRecord object or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM number_records WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            
            if row:
                return NumberRecord(
                    id=row['id'],
                    country_code=row['country_code'],
                    operator_prefix=row['operator_prefix'],
                    phone_number=row['phone_number'],
                    full_number=row['full_number'],
                    is_valid=row['is_valid'],
                    is_checked=bool(row['is_checked']),
                    check_date=datetime.fromisoformat(row['check_date']) if row['check_date'] else None,
                    check_count=row['check_count'],
                    notes=row['notes'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
            return None
    
    def get_number_record_by_full_number(self, full_number: str) -> Optional[NumberRecord]:
        """
        Get a number record by full phone number.
        
        Args:
            full_number: Full phone number to search for
            
        Returns:
            Optional[NumberRecord]: NumberRecord object or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM number_records WHERE full_number = ?", (full_number,))
            row = cursor.fetchone()
            
            if row:
                return NumberRecord(
                    id=row['id'],
                    country_code=row['country_code'],
                    operator_prefix=row['operator_prefix'],
                    phone_number=row['phone_number'],
                    full_number=row['full_number'],
                    is_valid=row['is_valid'],
                    is_checked=bool(row['is_checked']),
                    check_date=datetime.fromisoformat(row['check_date']) if row['check_date'] else None,
                    check_count=row['check_count'],
                    notes=row['notes'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
            return None
    
    def get_unchecked_numbers(self, country_code: str, operator_prefix: str, limit: int = 1000) -> List[NumberRecord]:
        """
        Get unchecked numbers for a specific country and operator.
        
        Args:
            country_code: Country code to filter by
            operator_prefix: Operator prefix to filter by
            limit: Maximum number of records to return
            
        Returns:
            List[NumberRecord]: List of unchecked number records
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM number_records 
                WHERE country_code = ? AND operator_prefix = ? AND is_checked = 0
                ORDER BY created_at ASC
                LIMIT ?
            """, (country_code, operator_prefix, limit))
            
            records = []
            for row in cursor.fetchall():
                record = NumberRecord(
                    id=row['id'],
                    country_code=row['country_code'],
                    operator_prefix=row['operator_prefix'],
                    phone_number=row['phone_number'],
                    full_number=row['full_number'],
                    is_valid=row['is_valid'],
                    is_checked=bool(row['is_checked']),
                    check_date=datetime.fromisoformat(row['check_date']) if row['check_date'] else None,
                    check_count=row['check_count'],
                    notes=row['notes'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                records.append(record)
            
            return records
    
    def update_number_record(self, number_record: NumberRecord) -> bool:
        """
        Update an existing number record.
        
        Args:
            number_record: NumberRecord object with updated data
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not number_record.id:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE number_records 
                SET country_code = ?, operator_prefix = ?, phone_number = ?, full_number = ?,
                    is_valid = ?, is_checked = ?, check_date = ?, check_count = ?, notes = ?, updated_at = ?
                WHERE id = ?
            """, (
                number_record.country_code,
                number_record.operator_prefix,
                number_record.phone_number,
                number_record.full_number,
                number_record.is_valid,
                number_record.is_checked,
                number_record.check_date,
                number_record.check_count,
                number_record.notes,
                datetime.now(),
                number_record.id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def bulk_update_number_records(self, records: List[NumberRecord]) -> int:
        """
        Bulk update multiple number records.
        
        Args:
            records: List of NumberRecord objects to update
            
        Returns:
            int: Number of records successfully updated
        """
        if not records:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updated_count = 0
            
            for record in records:
                if record.id:
                    cursor.execute("""
                        UPDATE number_records 
                        SET is_valid = ?, is_checked = ?, check_date = ?, check_count = ?, updated_at = ?
                        WHERE id = ?
                    """, (
                        record.is_valid,
                        record.is_checked,
                        record.check_date,
                        record.check_count,
                        datetime.now(),
                        record.id
                    ))
                    updated_count += cursor.rowcount
            
            conn.commit()
            return updated_count

    def delete_number_record(self, record_id: int) -> bool:
        """
        Delete a number record by ID.
        
        Args:
            record_id: ID of the number record to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM number_records WHERE id = ?", (record_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict[str, Any]: Dictionary containing various statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Contact statistics
            cursor.execute("SELECT COUNT(*) as total FROM contacts")
            total_contacts = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as valid FROM contacts WHERE is_valid = 1")
            valid_contacts = cursor.fetchone()['valid']
            
            cursor.execute("SELECT COUNT(*) as invalid FROM contacts WHERE is_valid = 0")
            invalid_contacts = cursor.fetchone()['invalid']
            
            # Number record statistics
            cursor.execute("SELECT COUNT(*) as total FROM number_records")
            total_numbers = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as checked FROM number_records WHERE is_checked = 1")
            checked_numbers = cursor.fetchone()['checked']
            
            cursor.execute("SELECT COUNT(*) as valid FROM number_records WHERE is_valid = 1")
            valid_numbers = cursor.fetchone()['valid']
            
            cursor.execute("SELECT COUNT(*) as invalid FROM number_records WHERE is_valid = 0")
            invalid_numbers = cursor.fetchone()['invalid']
            
            # Session statistics
            cursor.execute("SELECT COUNT(*) as total FROM check_sessions")
            total_sessions = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as running FROM check_sessions WHERE status = 'running'")
            running_sessions = cursor.fetchone()['running']
            
            return {
                'contacts': {
                    'total': total_contacts,
                    'valid': valid_contacts,
                    'invalid': invalid_contacts,
                    'unchecked': total_contacts - valid_contacts - invalid_contacts
                },
                'number_records': {
                    'total': total_numbers,
                    'checked': checked_numbers,
                    'unchecked': total_numbers - checked_numbers,
                    'valid': valid_numbers,
                    'invalid': invalid_numbers
                },
                'sessions': {
                    'total': total_sessions,
                    'running': running_sessions
                }
            }

    # CheckSession CRUD Operations
    def create_check_session(self, session: CheckSession) -> int:
        """
        Create a new check session in the database.
        
        Args:
            session: CheckSession object to create
            
        Returns:
            int: ID of the created session
        """
        import json
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO check_sessions (
                    session_name, country_code, operator_prefixes, total_numbers,
                    checked_numbers, valid_numbers, invalid_numbers, start_time,
                    end_time, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_name,
                session.country_code,
                json.dumps(session.operator_prefixes),
                session.total_numbers,
                session.checked_numbers,
                session.valid_numbers,
                session.invalid_numbers,
                session.start_time,
                session.end_time,
                session.status,
                session.created_at,
                session.updated_at
            ))
            conn.commit()
            return cursor.lastrowid

    def get_check_session(self, session_id: int) -> Optional[CheckSession]:
        """
        Get a check session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Optional[CheckSession]: CheckSession object or None if not found
        """
        import json
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM check_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            
            if row:
                return CheckSession(
                    id=row['id'],
                    session_name=row['session_name'],
                    country_code=row['country_code'],
                    operator_prefixes=json.loads(row['operator_prefixes']),
                    total_numbers=row['total_numbers'],
                    checked_numbers=row['checked_numbers'],
                    valid_numbers=row['valid_numbers'],
                    invalid_numbers=row['invalid_numbers'],
                    start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
            return None

    def get_all_check_sessions(self, limit: Optional[int] = None) -> List[CheckSession]:
        """
        Get all check sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List[CheckSession]: List of check session objects
        """
        import json
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if limit:
                cursor.execute("SELECT * FROM check_sessions ORDER BY created_at DESC LIMIT ?", (limit,))
            else:
                cursor.execute("SELECT * FROM check_sessions ORDER BY created_at DESC")
            
            sessions = []
            for row in cursor.fetchall():
                session = CheckSession(
                    id=row['id'],
                    session_name=row['session_name'],
                    country_code=row['country_code'],
                    operator_prefixes=json.loads(row['operator_prefixes']),
                    total_numbers=row['total_numbers'],
                    checked_numbers=row['checked_numbers'],
                    valid_numbers=row['valid_numbers'],
                    invalid_numbers=row['invalid_numbers'],
                    start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                sessions.append(session)
            
            return sessions

    def update_check_session(self, session: CheckSession) -> bool:
        """
        Update an existing check session.
        
        Args:
            session: CheckSession object with updated data
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        import json
        
        if not session.id:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE check_sessions 
                SET session_name = ?, country_code = ?, operator_prefixes = ?, total_numbers = ?,
                    checked_numbers = ?, valid_numbers = ?, invalid_numbers = ?, start_time = ?,
                    end_time = ?, status = ?, updated_at = ?
                WHERE id = ?
            """, (
                session.session_name,
                session.country_code,
                json.dumps(session.operator_prefixes),
                session.total_numbers,
                session.checked_numbers,
                session.valid_numbers,
                session.invalid_numbers,
                session.start_time,
                session.end_time,
                session.status,
                datetime.now(),
                session.id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_check_session(self, session_id: int) -> bool:
        """
        Delete a check session by ID.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM check_sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_running_sessions(self) -> List[CheckSession]:
        """
        Get all running check sessions.
        
        Returns:
            List[CheckSession]: List of running check session objects
        """
        import json
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM check_sessions WHERE status = 'running' ORDER BY created_at DESC")
            
            sessions = []
            for row in cursor.fetchall():
                session = CheckSession(
                    id=row['id'],
                    session_name=row['session_name'],
                    country_code=row['country_code'],
                    operator_prefixes=json.loads(row['operator_prefixes']),
                    total_numbers=row['total_numbers'],
                    checked_numbers=row['checked_numbers'],
                    valid_numbers=row['valid_numbers'],
                    invalid_numbers=row['invalid_numbers'],
                    start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                sessions.append(session)
            
            return sessions 