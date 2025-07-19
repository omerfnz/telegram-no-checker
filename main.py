#!/usr/bin/env python3
"""
Telegram Analiz Aracı - Ana Uygulama Giriş Noktası

Bu dosya, UI ve Core katmanlarını entegre eder ve uygulamayı başlatır.
"""

import sys
import os
import logging
import asyncio
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Flet import'u
import flet as ft

# Core modüller
from core.telegram_client import TelegramCoreClient
from core.file_handler import FileHandler
from core.contact_manager import ContactManager
from core.number_generator import NumberGenerator
from core.anti_robot_driver import AntiRobotDriver, RateLimitConfig

# UI modüller
from ui.main_window import MainWindow
from ui.theme_manager import ThemeManager

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("main")


class TelegramAnalyzerApp:
    """
    Ana uygulama sınıfı - UI ve Core katmanlarını yönetir.
    """
    
    def __init__(self):
        """Uygulamayı başlatır."""
        self.core_modules = {}
        self.ui_window = None
        self.theme_manager = None
        
        # Core modüllerini başlat
        self._init_core_modules()
        
        # Tema yöneticisini başlat
        self.theme_manager = ThemeManager()
        
        logger.info("Telegram Analyzer App başlatıldı")
    
    def _init_core_modules(self):
        """Core modüllerini başlatır."""
        try:
            # Anti-robot driver konfigürasyonu
            rate_config = RateLimitConfig(
                max_requests_per_minute=30,
                max_requests_per_hour=1000,
                base_delay=2.0,
                jitter=0.5,
                flood_wait_multiplier=1.5
            )
            
            # Core modüller
            self.core_modules = {
                'anti_robot_driver': AntiRobotDriver(rate_config),
                'telegram_client': TelegramCoreClient(),
                'file_handler': FileHandler(),
                'contact_manager': ContactManager(),
                'number_generator': NumberGenerator()
            }
            
            logger.info("Core modüller başarıyla başlatıldı")
            
        except Exception as e:
            logger.error(f"Core modüller başlatma hatası: {e}")
            raise
    
    def create_main_window(self, page: ft.Page):
        """
        Ana pencereyi oluşturur.
        
        Args:
            page (ft.Page): Flet sayfa nesnesi
        """
        try:
            self.ui_window = MainWindow(
                page=page,
                core_modules=self.core_modules,
                theme_manager=self.theme_manager
            )
            
            logger.info("Ana pencere oluşturuldu")
            
        except Exception as e:
            logger.error(f"Ana pencere oluşturma hatası: {e}")
            raise
    
    def run(self):
        """Uygulamayı çalıştırır."""
        try:
            def main(page: ft.Page):
                # Sayfa ayarları
                page.title = "Telegram Analiz Aracı"
                page.theme_mode = ft.ThemeMode.LIGHT
                page.window_width = 1200
                page.window_height = 800
                page.window_min_width = 800
                page.window_min_height = 600
                page.padding = 0
                page.spacing = 0
                
                # Ana pencereyi oluştur
                self.create_main_window(page)
                
                # Sayfayı güncelle
                page.update()
                
                logger.info("Uygulama başarıyla başlatıldı")
            
            # Flet uygulamasını başlat
            ft.app(target=main)
            
        except Exception as e:
            logger.error(f"Uygulama çalıştırma hatası: {e}")
            raise
    
    def cleanup(self):
        """Uygulama kapatılırken temizlik işlemleri."""
        try:
            # Core modüllerini temizle
            if 'telegram_client' in self.core_modules:
                try:
                    # Try to disconnect if possible
                    loop = asyncio.get_event_loop()
                    if not loop.is_closed():
                        loop.run_until_complete(self.core_modules['telegram_client'].disconnect())
                except:
                    pass  # Ignore cleanup errors
            
            logger.info("Uygulama temizlik işlemleri tamamlandı")
            
        except Exception as e:
            logger.error(f"Temizlik hatası: {e}")


def main():
    """Ana fonksiyon."""
    app = None
    
    try:
        # Uygulamayı başlat
        app = TelegramAnalyzerApp()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Kullanıcı tarafından durduruldu")
        
    except Exception as e:
        logger.error(f"Kritik hata: {e}")
        print(f"❌ Uygulama hatası: {e}")
        
    finally:
        # Temizlik işlemleri
        if app:
            app.cleanup()


if __name__ == "__main__":
    main() 