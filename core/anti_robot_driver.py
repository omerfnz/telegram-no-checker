"""
Anti-Robot Driver for Telegram API.

This module handles rate limiting and anti-detection measures.
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import random


@dataclass
class RateLimitConfig:
    """Rate limit konfigürasyonu."""
    max_requests_per_minute: int = 30
    max_requests_per_hour: int = 1000
    base_delay: float = 2.0  # Saniye
    jitter: float = 0.5  # Rastgele gecikme
    flood_wait_multiplier: float = 1.5  # FloodWait için çarpan


logger = logging.getLogger("anti_robot_driver")
logger.setLevel(logging.INFO)


class AntiRobotDriver:
    """
    Rate limiting, flood wait ve anti-robot önlemleri için sınıf.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        AntiRobotDriver sınıfını başlatır.
        
        Args:
            config (RateLimitConfig, optional): Rate limit konfigürasyonu
        """
        self.config = config or RateLimitConfig()
        self.request_history: Dict[str, list] = {}
        self.flood_wait_until: Optional[datetime] = None
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        self.is_paused = False
        self.pause_until: Optional[datetime] = None
    
    async def execute_with_rate_limit(self, func: Callable, *args, **kwargs) -> Any:
        """
        Fonksiyonu rate limit ile çalıştırır.
        
        Args:
            func (Callable): Çalıştırılacak fonksiyon
            *args: Fonksiyon argümanları
            **kwargs: Fonksiyon keyword argümanları
            
        Returns:
            Any: Fonksiyon sonucu
            
        Raises:
            Exception: Rate limit aşıldığında veya fonksiyon hatası
        """
        try:
            # Flood wait kontrolü
            if self.flood_wait_until and datetime.now() < self.flood_wait_until:
                wait_time = (self.flood_wait_until - datetime.now()).total_seconds()
                logger.warning(f"FloodWait: {wait_time:.1f} saniye bekleniyor...")
                await asyncio.sleep(wait_time)
                self.flood_wait_until = None
            
            # Pause kontrolü
            if self.is_paused and self.pause_until and datetime.now() < self.pause_until:
                wait_time = (self.pause_until - datetime.now()).total_seconds()
                logger.warning(f"Pause: {wait_time:.1f} saniye bekleniyor...")
                await asyncio.sleep(wait_time)
                self.is_paused = False
                self.pause_until = None
            
            # Rate limit kontrolü
            await self._check_rate_limit()
            
            # Rastgele gecikme
            delay = self._calculate_delay()
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Fonksiyonu çalıştır
            result = await func(*args, **kwargs)
            
            # Başarılı istek kaydı
            self._record_successful_request()
            
            # Hata sayacını sıfırla
            self.consecutive_errors = 0
            
            return result
            
        except Exception as e:
            # Hata kaydı
            self._record_error(e)
            
            # Hata tipine göre işlem
            if "FloodWaitError" in str(e):
                await self._handle_flood_wait(e)
            elif "TooManyRequestsError" in str(e):
                await self._handle_too_many_requests(e)
            else:
                await self._handle_general_error(e)
            
            raise
    
    async def _check_rate_limit(self) -> None:
        """Rate limit kontrolü yapar."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        # Son 1 dakikadaki istekleri say
        recent_requests = [
            req_time for req_time in self.request_history.get('successful', [])
            if req_time > minute_ago
        ]
        
        if len(recent_requests) >= self.config.max_requests_per_minute:
            wait_time = 60 - (now - recent_requests[0]).total_seconds()
            logger.warning(f"Rate limit aşıldı: {wait_time:.1f} saniye bekleniyor...")
            await asyncio.sleep(wait_time)
        
        # Son 1 saatteki istekleri say
        hourly_requests = [
            req_time for req_time in self.request_history.get('successful', [])
            if req_time > hour_ago
        ]
        
        if len(hourly_requests) >= self.config.max_requests_per_hour:
            wait_time = 3600 - (now - hourly_requests[0]).total_seconds()
            logger.warning(f"Saatlik limit aşıldı: {wait_time:.1f} saniye bekleniyor...")
            await asyncio.sleep(wait_time)
    
    def _calculate_delay(self) -> float:
        """İstekler arası gecikme hesaplar."""
        base_delay = self.config.base_delay
        
        # Ardışık hatalara göre gecikmeyi artır
        if self.consecutive_errors > 0:
            base_delay *= (1 + self.consecutive_errors * 0.5)
        
        # Rastgele jitter ekle
        jitter = random.uniform(-self.config.jitter, self.config.jitter)
        delay = base_delay + jitter
        
        return max(0, delay)
    
    def _record_successful_request(self) -> None:
        """Başarılı isteği kaydeder."""
        if 'successful' not in self.request_history:
            self.request_history['successful'] = []
        
        self.request_history['successful'].append(datetime.now())
        
        # Eski kayıtları temizle (1 saatten eski)
        hour_ago = datetime.now() - timedelta(hours=1)
        self.request_history['successful'] = [
            req_time for req_time in self.request_history['successful']
            if req_time > hour_ago
        ]
    
    def _record_error(self, error: Exception) -> None:
        """Hata kaydı yapar."""
        if 'errors' not in self.request_history:
            self.request_history['errors'] = []
        
        self.request_history['errors'].append({
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'error_message': str(error)
        })
        
        self.consecutive_errors += 1
        
        # Eski hata kayıtlarını temizle (1 saatten eski)
        hour_ago = datetime.now() - timedelta(hours=1)
        self.request_history['errors'] = [
            error_record for error_record in self.request_history['errors']
            if error_record['timestamp'] > hour_ago
        ]
    
    async def _handle_flood_wait(self, error: Exception) -> None:
        """FloodWaitError'ı işler."""
        try:
            # Hata mesajından bekleme süresini çıkar
            error_msg = str(error)
            if "A wait of" in error_msg and "seconds is required" in error_msg:
                # "A wait of 123 seconds is required" formatından süreyi çıkar
                import re
                match = re.search(r"A wait of (\d+) seconds is required", error_msg)
                if match:
                    wait_seconds = int(match.group(1))
                    # Çarpan uygula
                    adjusted_wait = wait_seconds * self.config.flood_wait_multiplier
                    self.flood_wait_until = datetime.now() + timedelta(seconds=adjusted_wait)
                    
                    logger.warning(f"FloodWait tespit edildi: {wait_seconds} saniye (ayarlanmış: {adjusted_wait:.1f})")
                    return
            
            # Varsayılan bekleme süresi
            default_wait = 60 * self.config.flood_wait_multiplier
            self.flood_wait_until = datetime.now() + timedelta(seconds=default_wait)
            logger.warning(f"FloodWait (varsayılan): {default_wait:.1f} saniye")
            
        except Exception as e:
            logger.error(f"FloodWait işleme hatası: {e}")
            # Varsayılan bekleme
            self.flood_wait_until = datetime.now() + timedelta(minutes=5)
    
    async def _handle_too_many_requests(self, error: Exception) -> None:
        """TooManyRequestsError'ı işler."""
        logger.warning("Çok fazla istek hatası tespit edildi")
        
        # Kısa süreli pause
        pause_duration = min(300, 60 * (2 ** self.consecutive_errors))  # Maksimum 5 dakika
        self.is_paused = True
        self.pause_until = datetime.now() + timedelta(seconds=pause_duration)
        
        logger.warning(f"Pause aktif: {pause_duration} saniye")
    
    async def _handle_general_error(self, error: Exception) -> None:
        """Genel hataları işler."""
        logger.error(f"Genel hata: {error}")
        
        # Ardışık hata sayısına göre pause
        if self.consecutive_errors >= self.max_consecutive_errors:
            pause_duration = 300  # 5 dakika
            self.is_paused = True
            self.pause_until = datetime.now() + timedelta(seconds=pause_duration)
            logger.warning(f"Çok fazla hata: {pause_duration} saniye pause")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Driver durumunu döndürür.
        
        Returns:
            Dict[str, Any]: Durum bilgileri
        """
        now = datetime.now()
        
        # Son 1 dakikadaki istek sayısı
        minute_ago = now - timedelta(minutes=1)
        recent_requests = [
            req_time for req_time in self.request_history.get('successful', [])
            if req_time > minute_ago
        ]
        
        # Son 1 saatteki istek sayısı
        hour_ago = now - timedelta(hours=1)
        hourly_requests = [
            req_time for req_time in self.request_history.get('successful', [])
            if req_time > hour_ago
        ]
        
        # Son hatalar
        recent_errors = [
            error_record for error_record in self.request_history.get('errors', [])
            if error_record['timestamp'] > hour_ago
        ]
        
        status = {
            'is_paused': self.is_paused,
            'consecutive_errors': self.consecutive_errors,
            'requests_last_minute': len(recent_requests),
            'requests_last_hour': len(hourly_requests),
            'errors_last_hour': len(recent_errors),
            'rate_limit_per_minute': self.config.max_requests_per_minute,
            'rate_limit_per_hour': self.config.max_requests_per_hour,
            'base_delay': self.config.base_delay,
            'current_delay': self._calculate_delay()
        }
        
        if self.flood_wait_until:
            status['flood_wait_until'] = self.flood_wait_until.isoformat()
            status['flood_wait_remaining'] = (self.flood_wait_until - now).total_seconds()
        
        if self.pause_until:
            status['pause_until'] = self.pause_until.isoformat()
            status['pause_remaining'] = (self.pause_until - now).total_seconds()
        
        return status
    
    def reset(self) -> None:
        """Driver durumunu sıfırlar."""
        self.request_history.clear()
        self.flood_wait_until = None
        self.consecutive_errors = 0
        self.is_paused = False
        self.pause_until = None
        logger.info("AntiRobotDriver sıfırlandı")
    
    def update_config(self, config: RateLimitConfig) -> None:
        """
        Konfigürasyonu günceller.
        
        Args:
            config (RateLimitConfig): Yeni konfigürasyon
        """
        self.config = config
        logger.info("AntiRobotDriver konfigürasyonu güncellendi")
    
    def get_error_summary(self) -> Dict[str, int]:
        """
        Hata özetini döndürür.
        
        Returns:
            Dict[str, int]: Hata tipi ve sayısı
        """
        error_summary = {}
        
        for error_record in self.request_history.get('errors', []):
            error_type = error_record['error_type']
            error_summary[error_type] = error_summary.get(error_type, 0) + 1
        
        return error_summary
    
    def is_healthy(self) -> bool:
        """
        Driver'ın sağlıklı olup olmadığını kontrol eder.
        
        Returns:
            bool: Sağlıklı mı
        """
        # Çok fazla ardışık hata var mı?
        if self.consecutive_errors >= self.max_consecutive_errors:
            return False
        
        # Pause durumunda mı?
        if self.is_paused and self.pause_until and datetime.now() < self.pause_until:
            return False
        
        # Flood wait durumunda mı?
        if self.flood_wait_until and datetime.now() < self.flood_wait_until:
            return False
        
        return True 