import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Contact:
    """Contact veri modeli."""
    id: Optional[int] = None
    name: str = ""
    phone_number: str = ""
    is_valid: bool = False
    last_checked: Optional[datetime] = None
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


logger = logging.getLogger("contact_manager")
logger.setLevel(logging.INFO)


class ContactManager:
    """
    Contact CRUD işlemleri ve veritabanı yönetimi için sınıf.
    """
    
    def __init__(self, db_path: str = "contacts.db"):
        """
        ContactManager sınıfını başlatır.
        
        Args:
            db_path (str): SQLite veritabanı dosya yolu
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Veritabanını başlatır ve tabloları oluşturur."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contacts tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone_number TEXT NOT NULL UNIQUE,
                        is_valid BOOLEAN DEFAULT FALSE,
                        last_checked DATETIME,
                        notes TEXT DEFAULT '',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Index'ler
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone ON contacts(phone_number)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON contacts(name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_valid ON contacts(is_valid)")
                
                conn.commit()
                logger.info("Veritabanı başarıyla başlatıldı.")
                
        except Exception as e:
            logger.error(f"Veritabanı başlatma hatası: {e}")
            raise
    
    def add_contact(self, name: str, phone_number: str, notes: str = "") -> int:
        """
        Yeni contact ekler.
        
        Args:
            name (str): Contact adı
            phone_number (str): Telefon numarası
            notes (str): Ek notlar
            
        Returns:
            int: Eklenen contact'ın ID'si
            
        Raises:
            sqlite3.IntegrityError: Aynı numara zaten varsa
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO contacts (name, phone_number, notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, phone_number, notes, datetime.now(), datetime.now()))
                
                contact_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Contact eklendi: {name} - {phone_number}")
                return contact_id
                
        except sqlite3.IntegrityError:
            logger.warning(f"Bu numara zaten mevcut: {phone_number}")
            raise
        except Exception as e:
            logger.error(f"Contact ekleme hatası: {e}")
            raise
    
    def get_contact(self, contact_id: int) -> Optional[Contact]:
        """
        ID ile contact getirir.
        
        Args:
            contact_id (int): Contact ID'si
            
        Returns:
            Optional[Contact]: Contact nesnesi veya None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, phone_number, is_valid, last_checked, notes, created_at, updated_at
                    FROM contacts WHERE id = ?
                """, (contact_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_contact(row)
                return None
                
        except Exception as e:
            logger.error(f"Contact getirme hatası: {e}")
            return None
    
    def get_contact_by_phone(self, phone_number: str) -> Optional[Contact]:
        """
        Telefon numarası ile contact getirir.
        
        Args:
            phone_number (str): Telefon numarası
            
        Returns:
            Optional[Contact]: Contact nesnesi veya None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, phone_number, is_valid, last_checked, notes, created_at, updated_at
                    FROM contacts WHERE phone_number = ?
                """, (phone_number,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_contact(row)
                return None
                
        except Exception as e:
            logger.error(f"Contact getirme hatası: {e}")
            return None
    
    def update_contact(self, contact_id: int, **kwargs) -> bool:
        """
        Contact bilgilerini günceller.
        
        Args:
            contact_id (int): Contact ID'si
            **kwargs: Güncellenecek alanlar (name, phone_number, is_valid, notes)
            
        Returns:
            bool: Güncelleme başarılı mı
        """
        try:
            valid_fields = {'name', 'phone_number', 'is_valid', 'notes', 'last_checked'}
            update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
            
            if not update_fields:
                return False
            
            update_fields['updated_at'] = datetime.now()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
                values = list(update_fields.values()) + [contact_id]
                
                cursor.execute(f"""
                    UPDATE contacts SET {set_clause}
                    WHERE id = ?
                """, values)
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Contact güncellendi: ID {contact_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Contact güncelleme hatası: {e}")
            return False
    
    def delete_contact(self, contact_id: int) -> bool:
        """
        Contact siler.
        
        Args:
            contact_id (int): Contact ID'si
            
        Returns:
            bool: Silme başarılı mı
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Contact silindi: ID {contact_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Contact silme hatası: {e}")
            return False
    
    def get_all_contacts(self, limit: Optional[int] = None, offset: int = 0) -> List[Contact]:
        """
        Tüm contact'ları getirir.
        
        Args:
            limit (int, optional): Maksimum kayıt sayısı
            offset (int): Atlanacak kayıt sayısı
            
        Returns:
            List[Contact]: Contact listesi
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, name, phone_number, is_valid, last_checked, notes, created_at, updated_at
                    FROM contacts
                    ORDER BY created_at DESC
                """
                
                if limit:
                    query += f" LIMIT {limit} OFFSET {offset}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                return [self._row_to_contact(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Contact listesi getirme hatası: {e}")
            return []
    
    def search_contacts(self, query: str, search_type: str = "name") -> List[Contact]:
        """
        Contact'ları arar.
        
        Args:
            query (str): Arama terimi
            search_type (str): Arama tipi ("name", "phone", "both")
            
        Returns:
            List[Contact]: Bulunan contact'lar
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if search_type == "name":
                    sql = """
                        SELECT id, name, phone_number, is_valid, last_checked, notes, created_at, updated_at
                        FROM contacts
                        WHERE name LIKE ?
                        ORDER BY name
                    """
                    params = (f"%{query}%",)
                elif search_type == "phone":
                    sql = """
                        SELECT id, name, phone_number, is_valid, last_checked, notes, created_at, updated_at
                        FROM contacts
                        WHERE phone_number LIKE ?
                        ORDER BY phone_number
                    """
                    params = (f"%{query}%",)
                else:  # both
                    sql = """
                        SELECT id, name, phone_number, is_valid, last_checked, notes, created_at, updated_at
                        FROM contacts
                        WHERE name LIKE ? OR phone_number LIKE ?
                        ORDER BY name
                    """
                    params = (f"%{query}%", f"%{query}%")
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                return [self._row_to_contact(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Contact arama hatası: {e}")
            return []
    
    def filter_contacts(self, is_valid: Optional[bool] = None, limit: Optional[int] = None) -> List[Contact]:
        """
        Contact'ları filtreler.
        
        Args:
            is_valid (bool, optional): Geçerlilik durumu
            limit (int, optional): Maksimum kayıt sayısı
            
        Returns:
            List[Contact]: Filtrelenmiş contact'lar
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, name, phone_number, is_valid, last_checked, notes, created_at, updated_at
                    FROM contacts
                """
                params = []
                
                if is_valid is not None:
                    query += " WHERE is_valid = ?"
                    params.append(is_valid)
                
                query += " ORDER BY created_at DESC"
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_contact(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Contact filtreleme hatası: {e}")
            return []
    
    def get_contact_stats(self) -> Dict[str, Any]:
        """
        Contact istatistiklerini döndürür.
        
        Returns:
            Dict[str, Any]: İstatistikler
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Toplam contact sayısı
                cursor.execute("SELECT COUNT(*) FROM contacts")
                total_contacts = cursor.fetchone()[0]
                
                # Geçerli contact sayısı
                cursor.execute("SELECT COUNT(*) FROM contacts WHERE is_valid = 1")
                valid_contacts = cursor.fetchone()[0]
                
                # Geçersiz contact sayısı
                cursor.execute("SELECT COUNT(*) FROM contacts WHERE is_valid = 0")
                invalid_contacts = cursor.fetchone()[0]
                
                # Kontrol edilmemiş contact sayısı
                cursor.execute("SELECT COUNT(*) FROM contacts WHERE last_checked IS NULL")
                unchecked_contacts = cursor.fetchone()[0]
                
                return {
                    'total_contacts': total_contacts,
                    'valid_contacts': valid_contacts,
                    'invalid_contacts': invalid_contacts,
                    'unchecked_contacts': unchecked_contacts,
                    'valid_percentage': round((valid_contacts / total_contacts * 100) if total_contacts > 0 else 0, 2)
                }
                
        except Exception as e:
            logger.error(f"İstatistik alma hatası: {e}")
            return {}
    
    def bulk_update_validity(self, updates: List[Tuple[str, bool]]) -> int:
        """
        Toplu olarak contact geçerliliğini günceller.
        
        Args:
            updates (List[Tuple]): (phone_number, is_valid) listesi
            
        Returns:
            int: Güncellenen kayıt sayısı
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                updated_count = 0
                for phone_number, is_valid in updates:
                    cursor.execute("""
                        UPDATE contacts 
                        SET is_valid = ?, last_checked = ?, updated_at = ?
                        WHERE phone_number = ?
                    """, (is_valid, datetime.now(), datetime.now(), phone_number))
                    updated_count += cursor.rowcount
                
                conn.commit()
                logger.info(f"{updated_count} contact güncellendi.")
                return updated_count
                
        except Exception as e:
            logger.error(f"Toplu güncelleme hatası: {e}")
            return 0
    
    def _row_to_contact(self, row: Tuple) -> Contact:
        """Veritabanı satırını Contact nesnesine dönüştürür."""
        return Contact(
            id=row[0],
            name=row[1],
            phone_number=row[2],
            is_valid=bool(row[3]),
            last_checked=datetime.fromisoformat(row[4]) if row[4] else None,
            notes=row[5],
            created_at=datetime.fromisoformat(row[6]) if row[6] else None,
            updated_at=datetime.fromisoformat(row[7]) if row[7] else None
        )
    
    def export_contacts_to_dict(self) -> List[Dict[str, Any]]:
        """
        Tüm contact'ları dictionary listesi olarak döndürür.
        
        Returns:
            List[Dict]: Contact dictionary listesi
        """
        contacts = self.get_all_contacts()
        return [asdict(contact) for contact in contacts] 