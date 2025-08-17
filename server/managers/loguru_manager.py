"""
Модуль для централизованного управления логированием во всем приложении.

Отвечает за:
- Конфигурацию "приемников" (sinks) для вывода логов в файлы, консоль, Sentry.
- Установку единого формата логов для всех компонентов системы.
- Обогащение логов контекстной информацией (например, user_id, deal_id).
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logger():
    """
    Настраивает логгер Loguru для всего серверного приложения.

    - Удаляет стандартные обработчики.
    - Добавляет цветной вывод в консоль (уровень INFO и выше).
    - Добавляет запись всех логов (уровень DEBUG и выше) в файл с ротацией.
    """
    logger.remove()  # Удаляем все предыдущие обработчики для чистоты

    # Формат для консоли с цветами
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Создаем папку для логов, если ее нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Настройка вывода в консоль
    logger.add(sys.stderr, level="INFO", format=console_format, colorize=True)

    # Настройка вывода в файл
    logger.add(
        log_dir / "server_{time}.log",
        level="DEBUG",
        rotation="10 MB",  # Ротация файла при достижении 10 MB
        retention="7 days",  # Хранить файлы за последние 7 дней
        compression="zip",  # Сжимать старые файлы
        enqueue=True,  # Делает логирование неблокирующим (важно для async)
        backtrace=True,  # Показывает полный стектрейс при ошибках
        diagnose=True,
    )

    logger.info("Logger has been successfully configured.")
