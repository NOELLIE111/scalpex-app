"""
Основной модуль, содержащий бизнес-логику торгового бота.
"""

import asyncio


class TradingBot:
    """
    Класс, инкапсулирующий всю асинхронную торговую логику.
    Он управляет своим состоянием и основными задачами.
    """

    def __init__(self):
        """Инициализирует экземпляр торгового бота."""
        self._is_running: bool = False
        self._main_task: asyncio.Task | None = None
        print("TradingBot instance created.")

    def start(self):
        if self._is_running:
            print("BOT_LOGIC: Bot is already running.")
            return
        self._is_running = True
        # Создаем и запускаем основную задачу бота
        self._main_task = asyncio.create_task(self._run_logic())
        print("BOT_LOGIC: Bot has been started.")

    def stop(self):
        if not self._is_running or not self._main_task:
            print("BOT_LOGIC: Bot is not running.")
            return
        self._is_running = False
        self._main_task.cancel()  # Безопасно отменяем задачу
        print("BOT_LOGIC: Bot has been stopped.")

    async def _run_logic(self):
        """Основной асинхронный цикл работы бота."""
        while self._is_running:
            print("BOT_LOGIC: Bot is working...")
            await asyncio.sleep(5)  # Имитация асинхронной работы
        print("BOT_LOGIC: Main logic loop has finished.")
