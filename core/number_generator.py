"""
Number generator for creating phone numbers.

This module handles automatic phone number generation based on country codes and operators.
"""

import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NumberRecord:
    """Numara kaydı veri modeli."""
    id: Optional[int] = None
    country_code: str = ""
    operator_prefix: str = ""
    phone_number: str = ""
    full_number: str = ""
    is_valid: bool = False
    is_checked: bool = False
    check_date: Optional[datetime] = None
    check_count: int = 0
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


logger = logging.getLogger("number_generator")
logger.setLevel(logging.INFO)


class NumberGenerator:
    """
    Otomatik numara üretimi ve yönetimi için sınıf.
    """
    
    def __init__(self):
        """NumberGenerator sınıfını başlatır."""
        self.country_operators = self._init_country_operators()
    
    def _init_country_operators(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Ülke bazlı operatör numaralarını başlatır.
        
        Returns:
            Dict: Ülke operatör numaraları
        """
        return {
            "+90": {  # Türkiye
                "Turkcell": ["501", "502", "503", "504", "505", "506", "507", "508", "509", "530", "531", "532", "533", "534", "535", "536", "537", "538", "539", "561"],
                "Vodafone": ["542", "543", "544", "545", "546", "547", "548", "549", "552", "553", "554", "555", "556", "557", "558", "559"],
                "Türk Telekom": ["501", "502", "503", "504", "505", "506", "507", "508", "509", "530", "531", "532", "533", "534", "535", "536", "537", "538", "539"],
                "Diğer": ["540", "541", "550", "551", "560", "562", "563", "564", "565", "566", "567", "568", "569"]
            },
            "+1": {  # ABD
                "Verizon": ["201", "202", "203", "204", "205"],
                "AT&T": ["206", "207", "208", "209", "210"],
                "T-Mobile": ["211", "212", "213", "214", "215"]
            },
            "+44": {  # İngiltere
                "Vodafone": ["7700", "7701", "7702", "7703"],
                "O2": ["7704", "7705", "7706", "7707"],
                "EE": ["7708", "7709", "7710", "7711"]
            }
        }
    
    def get_supported_countries(self) -> List[str]:
        """
        Desteklenen ülke kodlarını döndürür.
        
        Returns:
            List[str]: Ülke kodları listesi
        """
        return list(self.country_operators.keys())
    
    def get_operators_for_country(self, country_code: str) -> List[str]:
        """
        Belirli ülke için operatör listesini döndürür.
        
        Args:
            country_code (str): Ülke kodu (örn: +90)
            
        Returns:
            List[str]: Operatör listesi
        """
        if country_code not in self.country_operators:
            return []
        return list(self.country_operators[country_code].keys())
    
    def get_prefixes_for_operator(self, country_code: str, operator: str) -> List[str]:
        """
        Belirli operatör için prefix listesini döndürür.
        
        Args:
            country_code (str): Ülke kodu
            operator (str): Operatör adı
            
        Returns:
            List[str]: Prefix listesi
        """
        if country_code not in self.country_operators:
            return []
        if operator not in self.country_operators[country_code]:
            return []
        return self.country_operators[country_code][operator]
    
    def generate_single_number(self, country_code: str, operator: str, pattern: Optional[str] = None) -> str:
        """
        Tek bir numara üretir.
        
        Args:
            country_code (str): Ülke kodu
            operator (str): Operatör adı
            pattern (str, optional): Özel pattern (örn: "1234567")
            
        Returns:
            str: Üretilen numara
        """
        try:
            # Operatör prefix'ini al
            prefixes = self.get_prefixes_for_operator(country_code, operator)
            if not prefixes:
                raise ValueError(f"Operatör bulunamadı: {operator}")
            
            prefix = random.choice(prefixes)
            
            # Numara kısmını üret
            if pattern:
                # Pattern kullan
                phone_part = pattern
            else:
                # Rastgele 7 haneli numara
                phone_part = ''.join([str(random.randint(0, 9)) for _ in range(7)])
            
            # Tam numarayı oluştur
            full_number = f"{country_code}{prefix}{phone_part}"
            
            return full_number
            
        except Exception as e:
            logger.error(f"Numara üretme hatası: {e}")
            raise
    
    def generate_numbers_bulk(self, country_code: str, operators: List[str], count: int, 
                            pattern: Optional[str] = None, exclude_existing: Optional[List[str]] = None) -> List[str]:
        """
        Toplu numara üretir.
        
        Args:
            country_code (str): Ülke kodu
            operators (List[str]): Operatör listesi
            count (int): Üretilecek numara sayısı
            pattern (str, optional): Özel pattern
            exclude_existing (List[str], optional): Hariç tutulacak numaralar
            
        Returns:
            List[str]: Üretilen numaralar listesi
        """
        try:
            generated_numbers = []
            exclude_set = set(exclude_existing or [])
            
            attempts = 0
            max_attempts = count * 10  # Sonsuz döngüyü önlemek için
            
            while len(generated_numbers) < count and attempts < max_attempts:
                # Rastgele operatör seç
                operator = random.choice(operators)
                
                # Numara üret
                number = self.generate_single_number(country_code, operator, pattern)
                
                # Eğer numara daha önce üretilmemişse ekle
                if number not in exclude_set and number not in generated_numbers:
                    generated_numbers.append(number)
                
                attempts += 1
            
            logger.info(f"{len(generated_numbers)} numara üretildi (deneme: {attempts})")
            return generated_numbers
            
        except Exception as e:
            logger.error(f"Toplu numara üretme hatası: {e}")
            raise
    
    def generate_numbers_by_pattern(self, country_code: str, operator: str, pattern: str) -> List[str]:
        """
        Pattern'e göre numara üretir.
        
        Args:
            country_code (str): Ülke kodu
            operator (str): Operatör adı
            pattern (str): Pattern (X yerine rastgele rakam)
            
        Returns:
            List[str]: Üretilen numaralar
        """
        try:
            numbers = []
            prefixes = self.get_prefixes_for_operator(country_code, operator)
            
            if not prefixes:
                raise ValueError(f"Operatör bulunamadı: {operator}")
            
            # Pattern'deki X'leri rastgele rakamlarla değiştir
            for prefix in prefixes:
                phone_part = ""
                for char in pattern:
                    if char == 'X':
                        phone_part += str(random.randint(0, 9))
                    else:
                        phone_part += char
                
                full_number = f"{country_code}{prefix}{phone_part}"
                numbers.append(full_number)
            
            logger.info(f"Pattern ile {len(numbers)} numara üretildi")
            return numbers
            
        except Exception as e:
            logger.error(f"Pattern numara üretme hatası: {e}")
            raise
    
    def generate_numbers_by_range(self, country_code: str, operator: str, start_range: int, end_range: int) -> List[str]:
        """
        Aralık bazında numara üretir.
        
        Args:
            country_code (str): Ülke kodu
            operator (str): Operatör adı
            start_range (int): Başlangıç numarası
            end_range (int): Bitiş numarası
            
        Returns:
            List[str]: Üretilen numaralar
        """
        try:
            numbers = []
            prefixes = self.get_prefixes_for_operator(country_code, operator)
            
            if not prefixes:
                raise ValueError(f"Operatör bulunamadı: {operator}")
            
            for prefix in prefixes:
                for num in range(start_range, end_range + 1):
                    phone_part = str(num).zfill(7)  # 7 haneli yap
                    full_number = f"{country_code}{prefix}{phone_part}"
                    numbers.append(full_number)
            
            logger.info(f"Aralık ile {len(numbers)} numara üretildi")
            return numbers
            
        except Exception as e:
            logger.error(f"Aralık numara üretme hatası: {e}")
            raise
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Telefon numarasının geçerli olup olmadığını kontrol eder.
        
        Args:
            phone_number (str): Kontrol edilecek numara
            
        Returns:
            bool: Geçerli mi
        """
        try:
            # + ile başlamalı
            if not phone_number.startswith('+'):
                return False
            
            # Sadece rakam ve + içermeli
            if not all(c.isdigit() or c == '+' for c in phone_number):
                return False
            
            # Minimum uzunluk kontrolü (ülke kodu + operatör + numara)
            if len(phone_number) < 12:  # +90 + 3 haneli operatör + 7 haneli numara
                return False
            
            return True
            
        except Exception:
            return False
    
    def parse_phone_number(self, phone_number: str) -> Optional[Dict[str, str]]:
        """
        Telefon numarasını parçalar.
        
        Args:
            phone_number (str): Telefon numarası
            
        Returns:
            Optional[Dict]: Parçalanmış bilgiler
        """
        try:
            if not self.validate_phone_number(phone_number):
                return None
            
            # Ülke kodunu bul
            country_code = None
            for code in self.get_supported_countries():
                if phone_number.startswith(code):
                    country_code = code
                    break
            
            if not country_code:
                return None
            
            # Operatör prefix'ini bul
            remaining = phone_number[len(country_code):]
            operator = None
            operator_prefix = None
            
            for op, prefixes in self.country_operators[country_code].items():
                for prefix in prefixes:
                    if remaining.startswith(prefix):
                        operator = op
                        operator_prefix = prefix
                        break
                if operator:
                    break
            
            if not operator:
                return None
            
            # Numara kısmını al
            phone_part = remaining[len(operator_prefix):]
            
            return {
                'country_code': country_code,
                'operator': operator,
                'operator_prefix': operator_prefix,
                'phone_number': phone_part,
                'full_number': phone_number
            }
            
        except Exception as e:
            logger.error(f"Numara parse hatası: {e}")
            return None
    
    def get_number_statistics(self, numbers: List[str]) -> Dict[str, Any]:
        """
        Numara listesi için istatistik döndürür.
        
        Args:
            numbers (List[str]): Numara listesi
            
        Returns:
            Dict[str, Any]: İstatistikler
        """
        try:
            stats = {
                'total_numbers': len(numbers),
                'valid_numbers': 0,
                'invalid_numbers': 0,
                'country_distribution': {},
                'operator_distribution': {}
            }
            
            for number in numbers:
                if self.validate_phone_number(number):
                    stats['valid_numbers'] += 1
                    
                    # Ülke dağılımı
                    parsed = self.parse_phone_number(number)
                    if parsed:
                        country = parsed['country_code']
                        operator = parsed['operator']
                        
                        stats['country_distribution'][country] = stats['country_distribution'].get(country, 0) + 1
                        stats['operator_distribution'][operator] = stats['operator_distribution'].get(operator, 0) + 1
                else:
                    stats['invalid_numbers'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"İstatistik alma hatası: {e}")
            return {}
    
    def export_numbers_to_file(self, numbers: List[str], file_path: str) -> bool:
        """
        Numara listesini dosyaya kaydeder.
        
        Args:
            numbers (List[str]): Numara listesi
            file_path (str): Dosya yolu
            
        Returns:
            bool: Başarılı mı
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for number in numbers:
                    file.write(f"{number}\n")
            
            logger.info(f"{len(numbers)} numara dosyaya kaydedildi: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Dosya kaydetme hatası: {e}")
            return False 