import time
import threading


class TradingBot:
    """
    Класс, инкапсулирующий основную торговую логику.
    Работает в отдельном потоке, чтобы не блокировать графический интерфейс.
    """

    def __init__(self):
        self._is_running = False
        self._thread = None
        print("TradingBot инициализирован.")

    def start(self):
        if self._is_running:
            print("Бот уже запущен.")
            return

        self._is_running = True
        # Запускаем основную логику в отдельном потоке, чтобы не блокировать GUI
        self._thread = threading.Thread(target=self._run_logic, daemon=True)
        self._thread.start()
        print("Бот успешно запущен в фоновом потоке.")

    def stop(self):
        if not self._is_running:
            print("Бот уже остановлен.")
            return
        self._is_running = False
        print("Бот остановлен.")

    def _run_logic(self):
        """Основной цикл работы бота."""
        while self._is_running:
            print(f"Бот работает... {time.ctime()}")
            time.sleep(5)  # Имитация работы
        print("Основная логика бота завершила работу.")


1
