"""
File handler for importing and exporting data.

This module handles file operations including Excel, TXT, and CSV formats.
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger("file_handler")
logger.setLevel(logging.INFO)


class FileHandler:
    """
    Excel ve TXT dosyalarından numara listesi okuma, sonuçları kaydetme için sınıf.
    """
    
    def __init__(self):
        """FileHandler sınıfını başlatır."""
        self.supported_formats = ['.xlsx', '.xls', '.csv', '.txt']
    
    def read_numbers_from_excel(self, file_path: str, column_name: Optional[str] = None) -> List[str]:
        """
        Excel dosyasından numara listesi okur.
        
        Args:
            file_path (str): Excel dosyasının yolu
            column_name (str, optional): Numara sütununun adı. None ise ilk sütun kullanılır.
            
        Returns:
            List[str]: Numara listesi
            
        Raises:
            FileNotFoundError: Dosya bulunamadığında
            ValueError: Geçersiz dosya formatı veya sütun adı
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
            
            # Dosya uzantısını kontrol et
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in ['.xlsx', '.xls', '.csv']:
                raise ValueError(f"Desteklenmeyen dosya formatı: {file_ext}")
            
            # Dosyayı oku
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Sütun seçimi
            if column_name:
                if column_name not in df.columns:
                    raise ValueError(f"Sütun bulunamadı: {column_name}")
                numbers = df[column_name].astype(str).tolist()
            else:
                # İlk sütunu kullan
                numbers = df.iloc[:, 0].astype(str).tolist()
            
            # Boş değerleri temizle
            numbers = [num.strip() for num in numbers if num.strip() and num.strip() != 'nan']
            
            logger.info(f"{len(numbers)} numara başarıyla okundu: {file_path}")
            return numbers
            
        except Exception as e:
            logger.error(f"Excel dosyası okuma hatası: {e}")
            raise
    
    def read_numbers_from_txt(self, file_path: str) -> List[str]:
        """
        TXT dosyasından numara listesi okur.
        
        Args:
            file_path (str): TXT dosyasının yolu
            
        Returns:
            List[str]: Numara listesi
            
        Raises:
            FileNotFoundError: Dosya bulunamadığında
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
            
            numbers = []
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Yorum satırlarını atla
                        numbers.append(line)
            
            logger.info(f"{len(numbers)} numara başarıyla okundu: {file_path}")
            return numbers
            
        except Exception as e:
            logger.error(f"TXT dosyası okuma hatası: {e}")
            raise
    
    def read_numbers_from_file(self, file_path: str, column_name: Optional[str] = None) -> List[str]:
        """
        Dosya uzantısına göre uygun okuma fonksiyonunu çağırır.
        
        Args:
            file_path (str): Dosya yolu
            column_name (str, optional): Excel için sütun adı
            
        Returns:
            List[str]: Numara listesi
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.xlsx', '.xls', '.csv']:
            return self.read_numbers_from_excel(file_path, column_name)
        elif file_ext == '.txt':
            return self.read_numbers_from_txt(file_path)
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {file_ext}")
    
    def save_results_to_excel(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Kontrol sonuçlarını Excel dosyasına kaydeder.
        
        Args:
            results (List[Dict]): Kontrol sonuçları listesi
            output_path (str): Çıktı dosyasının yolu
            
        Raises:
            ValueError: Geçersiz veri formatı
        """
        try:
            if not results:
                logger.warning("Kaydedilecek sonuç bulunamadı.")
                return
            
            # DataFrame oluştur
            df = pd.DataFrame(results)
            
            # Dosyayı kaydet
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.info(f"Sonuçlar başarıyla kaydedildi: {output_path}")
            
        except Exception as e:
            logger.error(f"Excel dosyasına kaydetme hatası: {e}")
            raise
    
    def save_results_to_txt(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Kontrol sonuçlarını TXT dosyasına kaydeder.
        
        Args:
            results (List[Dict]): Kontrol sonuçları listesi
            output_path (str): Çıktı dosyasının yolu
        """
        try:
            if not results:
                logger.warning("Kaydedilecek sonuç bulunamadı.")
                return
            
            with open(output_path, 'w', encoding='utf-8') as file:
                # Başlık satırı
                if results:
                    headers = list(results[0].keys())
                    file.write('\t'.join(headers) + '\n')
                
                # Veri satırları
                for result in results:
                    row = '\t'.join(str(result.get(header, '')) for header in headers)
                    file.write(row + '\n')
            
            logger.info(f"Sonuçlar başarıyla kaydedildi: {output_path}")
            
        except Exception as e:
            logger.error(f"TXT dosyasına kaydetme hatası: {e}")
            raise
    
    def save_results_to_file(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Dosya uzantısına göre uygun kaydetme fonksiyonunu çağırır.
        
        Args:
            results (List[Dict]): Kontrol sonuçları listesi
            output_path (str): Çıktı dosyasının yolu
        """
        file_ext = Path(output_path).suffix.lower()
        
        if file_ext in ['.xlsx', '.xls']:
            self.save_results_to_excel(results, output_path)
        elif file_ext in ['.txt', '.csv']:
            self.save_results_to_txt(results, output_path)
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {file_ext}")
    
    def validate_phone_numbers(self, numbers: List[str]) -> List[str]:
        """
        Numara listesini temizler ve geçerli formatları döndürür.
        
        Args:
            numbers (List[str]): Ham numara listesi
            
        Returns:
            List[str]: Temizlenmiş ve geçerli numara listesi
        """
        valid_numbers = []
        
        for number in numbers:
            # Boşlukları ve özel karakterleri temizle
            cleaned = ''.join(c for c in str(number) if c.isdigit() or c in '+')
            
            # + ile başlamıyorsa ekle
            if cleaned and not cleaned.startswith('+'):
                cleaned = '+' + cleaned
            
            # Geçerli uzunluk kontrolü (en az 10 rakam)
            digits_only = ''.join(c for c in cleaned if c.isdigit())
            if len(digits_only) >= 10:
                valid_numbers.append(cleaned)
        
        logger.info(f"{len(valid_numbers)} geçerli numara bulundu (toplam: {len(numbers)})")
        return valid_numbers
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Dosya hakkında bilgi döndürür.
        
        Args:
            file_path (str): Dosya yolu
            
        Returns:
            Dict[str, Any]: Dosya bilgileri
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
            
            file_path_obj = Path(file_path)
            file_size = os.path.getsize(file_path)
            
            info = {
                'name': file_path_obj.name,
                'extension': file_path_obj.suffix,
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'exists': True
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Dosya bilgisi alma hatası: {e}")
            return {'exists': False, 'error': str(e)}
    
    def export_contacts_to_excel(self, contacts: List, output_path: str) -> bool:
        """
        Contact listesini Excel dosyasına export eder.
        
        Args:
            contacts: Contact listesi
            output_path: Çıktı dosyasının yolu
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            if not contacts:
                logger.warning("Export edilecek contact bulunamadı.")
                return False
            
            # Contact verilerini DataFrame'e dönüştür
            contact_data = []
            for contact in contacts:
                contact_data.append({
                    'ID': contact.id,
                    'Name': contact.name,
                    'Phone Number': contact.phone_number,
                    'Is Valid': contact.is_valid,
                    'Last Checked': contact.last_checked.isoformat() if contact.last_checked else '',
                    'Notes': contact.notes,
                    'Created At': contact.created_at.isoformat(),
                    'Updated At': contact.updated_at.isoformat()
                })
            
            # DataFrame oluştur
            df = pd.DataFrame(contact_data)
            
            # Dosyayı kaydet
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.info(f"Contacts başarıyla export edildi: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Contact export hatası: {e}")
            return False
    
    def export_number_records_to_excel(self, number_records: List, output_path: str) -> bool:
        """
        Number record listesini Excel dosyasına export eder.
        
        Args:
            number_records: Number record listesi veya string listesi
            output_path: Çıktı dosyasının yolu
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            if not number_records:
                logger.warning("Export edilecek number record bulunamadı.")
                return False
            
            # Number record verilerini DataFrame'e dönüştür
            record_data = []
            for record in number_records:
                if isinstance(record, str):
                    # String ise basit format
                    record_data.append({
                        'Phone Number': record,
                        'Generated At': datetime.now().isoformat()
                    })
                else:
                    # NumberRecord objesi ise detaylı format
                    record_data.append({
                        'ID': record.id,
                        'Country Code': record.country_code,
                        'Operator Prefix': record.operator_prefix,
                        'Phone Number': record.phone_number,
                        'Full Number': record.full_number,
                        'Is Valid': record.is_valid,
                        'Is Checked': record.is_checked,
                        'Check Date': record.check_date.isoformat() if record.check_date else '',
                        'Check Count': record.check_count,
                        'Notes': record.notes,
                        'Created At': record.created_at.isoformat(),
                        'Updated At': record.updated_at.isoformat()
                    })
            
            # DataFrame oluştur
            df = pd.DataFrame(record_data)
            
            # Dosyayı kaydet
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.info(f"Number records başarıyla export edildi: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Number record export hatası: {e}")
            return False 