"""
Telegram Client for number validation.

This module handles Telegram API connections and basic operations.
"""

import os
import logging
from typing import Optional, Any
from telethon import TelegramClient, errors
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "anon")

logger = logging.getLogger("telegram_client")
logger.setLevel(logging.INFO)


class TelegramCoreClient:
    """
    Telegram ile bağlantı, login, session yönetimi ve numara kontrolü için temel sınıf.
    """
    def __init__(self, api_id: Optional[str] = None, api_hash: Optional[str] = None, session_name: Optional[str] = None):
        """
        Args:
            api_id (str, optional): Telegram API ID
            api_hash (str, optional): Telegram API HASH
            session_name (str, optional): Session dosya adı
        """
        self.api_id = api_id or API_ID
        self.api_hash = api_hash or API_HASH
        self.session_name = session_name or SESSION_NAME
        self.client: Optional[TelegramClient] = None

    async def connect(self) -> None:
        """
        Telegram'a bağlanır ve oturum açar. Gerekirse kullanıcıdan kod ister.
        """
        if not self.api_id or not self.api_hash:
            raise ValueError("API_ID ve API_HASH tanımlı olmalı!")
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.start()
        logger.info("Telegram'a başarıyla bağlanıldı.")

    async def disconnect(self) -> None:
        """
        Telegram oturumunu kapatır.
        """
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram oturumu kapatıldı.")

    async def is_user_registered(self, phone_number: str) -> bool:
        """
        Verilen telefon numarasının Telegram'da kayıtlı olup olmadığını kontrol eder.
        Args:
            phone_number (str): Kontrol edilecek numara (örn: +905xxxxxxxxx)
        Returns:
            bool: Kayıtlıysa True, değilse False
        """
        if not self.client:
            raise RuntimeError("TelegramClient bağlı değil. Önce connect() çağırın.")
        try:
            result = await self.client.is_user_authorized()
            if not result:
                raise RuntimeError("Telegram oturumu açık değil.")
            user = await self.client.get_entity(phone_number)
            return user is not None
        except errors.PhoneNumberInvalidError:
            logger.warning(f"Geçersiz numara: {phone_number}")
            return False
        except errors.FloodWaitError as e:
            logger.error(f"FloodWait: {e.seconds} saniye beklenmeli.")
            raise
        except Exception as e:
            logger.error(f"Numara kontrolünde hata: {e}")
            return False

    async def get_me(self) -> Optional[Any]:
        """
        Giriş yapan kullanıcıyı döndürür.
        Returns:
            Kullanıcı nesnesi veya None
        """
        if self.client:
            return await self.client.get_me()
        return None 