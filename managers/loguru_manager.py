"""
Модуль для централизованного управления логированием во всем приложении.

Отвечает за:
- Конфигурацию "приемников" (sinks) для вывода логов в файлы, консоль, Sentry.
- Установку единого формата логов для всех компонентов системы.
- Обогащение логов контекстной информацией (например, user_id, deal_id).
"""

import sys
import logging
from pathlib import Path

from loguru import logger


def setup_logger(process_name: str = "app"):
    """
    Настраивает логгер Loguru для всего приложения (клиент и сервер).

    :param process_name: Имя процесса ('client', 'server'), используется для имени файла лога.
    - Удаляет стандартные обработчики.
    - Добавляет цветной вывод в консоль (уровень INFO и выше).
    - Добавляет запись всех логов (уровень DEBUG и выше) в файл с ротацией.
    """
    logger.remove()  # Удаляем все предыдущие обработчики для чистоты

    # --- Прямая настройка стандартных логгеров ---
    # Вместо "перехвата" мы напрямую настраиваем уровень стандартных логгеров.
    # Это более простой и надежный способ избежать конфликтов и рекурсии.
    # Их сообщения будут выводиться в консоль в их собственном формате.
    logging.basicConfig(level=logging.WARNING)  # Устанавливаем базовый уровень для всех
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    # Отключаем "шумные" логи доступа uvicorn, оставляя только предупреждения и ошибки
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("kivy").setLevel(logging.INFO)

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
    logger.add(
        sys.stderr,
        level="INFO",
        format=console_format,
        colorize=True,
        # enqueue=False (по умолчанию). Для консоли клиента на Windows
        # использование enqueue=True может приводить к deadlock при запуске.
        # Поэтому оставляем синхронный вывод в консоль.
    )

    # Настройка вывода в файл
    logger.add(
        log_dir / f"{process_name}_{{time}}.log",
        level="DEBUG",
        rotation="10 MB",  # Ротация файла при достижении 10 MB
        retention="7 days",  # Хранить файлы за последние 7 дней
        compression="zip",  # Сжимать старые файлы
        enqueue=True,  # Делает логирование неблокирующим (важно для async и GUI)
        backtrace=True,  # Показывает полный стектрейс при ошибках
        diagnose=True,
    )

    logger.info(f"Logger for '{process_name}' has been successfully configured.")
