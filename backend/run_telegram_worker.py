#!/usr/bin/env python
"""
Telegram Arbitrage Worker - запускається окремим контейнером
"""
import os
import sys
import logging

# Додаємо поточну директорію до Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Основна функція запуску"""
    try:
        # Спробуємо імпортувати нашого воркера
        try:
            from app.workers.telegram_worker import TelegramArbitrageWorker
            logger.info("✅ Successfully imported Telegram worker")
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            
            # Спробуємо альтернативний шлях
            try:
                # Перевіримо, чи є файл
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "telegram_worker",
                    "app/workers/telegram_worker.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                TelegramArbitrageWorker = module.TelegramArbitrageWorker
                logger.info("✅ Imported via alternative method")
            except Exception as e2:
                logger.error(f"❌ Alternative import also failed: {e2}")
                sys.exit(1)
        
        # Створюємо воркер з параметрами за замовчуванням
        # (ці параметри можна змінити через змінні середовища)
        check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
        profit_threshold = float(os.getenv('PROFIT_THRESHOLD', '0.5'))
        
        worker = TelegramArbitrageWorker(
            check_interval=check_interval,
            profit_threshold=profit_threshold
        )
        
        # Запускаємо
        logger.info(f"🚀 Starting Telegram Arbitrage Worker")
        logger.info(f"   Interval: {check_interval}s")
        logger.info(f"   Threshold: {profit_threshold}%")
        
        worker.run_continuous()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Worker stopped by user")
    except Exception as e:
        logger.error(f"💥 Worker crashed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()