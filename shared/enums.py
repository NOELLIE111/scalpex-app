"""
Модуль для хранения общих перечислений (Enums) для всего проекта.
"""

from enum import Enum


class BotStatus(str, Enum):
    """Перечисление возможных статусов бота."""

    RUNNING = "Running"
    STOPPED = "Stopped"
    UNKNOWN = "Unknown"
