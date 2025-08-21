"""
Основной модуль, содержащий бизнес-логику торгового бота.
"""

import asyncio
import os

from shared.enums import BotStatus
from loguru import logger


class TradingBot:
    """
    Класс, инкапсулирующий всю асинхронную торговую логику.
    Он управляет своим состоянием и основными задачами.
    """

    def __init__(self):
        """Инициализирует экземпляр торгового бота."""
        self._is_running: bool = False
        self.trading_pairs: list[str] = self._load_trading_pairs()
        # Словарь для хранения задач для каждой торговой пары
        # {"KASUSDT": <Task>, "SOLUSDT": <Task>}
        self._pair_tasks: dict[str, asyncio.Task] = {}

        logger.info("TradingBot instance created.")
        if self.trading_pairs:
            logger.info(f"Bot is configured to trade with: {self.trading_pairs}")
        else:
            logger.warning("No trading pairs configured.")

    def _load_trading_pairs(self) -> list[str]:
        """Загружает и парсит список торговых пар из переменной окружения TRADING_PAIRS."""
        pairs_str = os.getenv("TRADING_PAIRS", "")
        if not pairs_str:
            return []
        # Разделяем строку по запятой и убираем лишние пробелы у каждой пары
        return [pair.strip().upper() for pair in pairs_str.split(",")]

    def start_for_pair(self, pair: str):
        """Запускает логику для указанной торговой пары."""
        if pair not in self.trading_pairs:
            logger.error(f"Attempted to start an unconfigured pair: {pair}")
            raise ValueError(f"Pair {pair} is not configured.")

        if pair in self._pair_tasks and not self._pair_tasks[pair].done():
            logger.info(f"Bot is already running for {pair}. No action taken.")
            return

        # Создаем и запускаем задачу для конкретной пары
        task = asyncio.create_task(self._run_logic_for_pair(pair))
        self._pair_tasks[pair] = task
        logger.success(f"Bot has been started for {pair}.")

    def stop_for_pair(self, pair: str):
        """Останавливает логику для указанной торговой пары."""
        if pair not in self._pair_tasks:
            logger.warning(f"Attempted to stop a bot that is not running for {pair}.")
            return

        task = self._pair_tasks.pop(pair)
        if not task.done():
            task.cancel()
        logger.success(f"Bot has been stopped for {pair}.")

    async def _run_logic_for_pair(self, pair: str):
        """Основной асинхронный цикл работы для одной пары."""
        logger.info(f"Starting logic loop for {pair}...")
        try:
            while True:
                logger.debug(f"Processing logic for pair {pair}...")
                await asyncio.sleep(5)  # Имитация асинхронной работы
        except asyncio.CancelledError:
            logger.info(f"Logic loop for {pair} was cancelled.")
        finally:
            logger.info(f"Main logic loop for {pair} has finished.")

    def get_status(self) -> dict[str, str]:
        """Возвращает статус работы ('Running' или 'Stopped') по всем настроенным парам."""
        status = {}
        for pair in self.trading_pairs:
            task = self._pair_tasks.get(pair)
            status[pair] = (
                BotStatus.RUNNING if task and not task.done() else BotStatus.STOPPED
            )
        return status
