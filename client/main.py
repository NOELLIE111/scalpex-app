"""
Основной файл клиентского GUI-приложения на Kivy.
"""

import asyncio
from kivy.utils import platform

from kivy.config import Config

# Устанавливаем размер окна только для десктопных платформ.
# На мобильных устройствах приложение автоматически развернется на весь экран.
if platform in ("win", "linux", "macosx"):
    Config.set("graphics", "width", "1024")
    Config.set("graphics", "height", "720")

import httpx
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.properties import StringProperty
from loguru import logger
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout

# Импорт и настройка нашего логгера
from managers.loguru_manager import setup_logger
from shared.enums import BotStatus


class PairWidget(MDBoxLayout):
    """Виджет для управления одной торговой парой. Его вид описан в .kv файле."""

    pair_symbol = StringProperty("")


class MainWidget(MDBoxLayout):
    """
    Главный виджет, чья структура описана в main_screen.kv.
    Доступ к дочерним виджетам осуществляется через словарь `ids`.
    """

    pass


class ScalpEXApp(MDApp):
    """Основной класс приложения Kivy (клиент)"""

    def __init__(self, **kwargs):
        """Инициализирует приложение и задает URL сервера."""
        super().__init__(**kwargs)
        self.server_url = "http://127.0.0.1:8000"
        self.http_client = httpx.AsyncClient(timeout=5)

    def build(self):
        """Стандартный метод Kivy для создания корневого виджета приложения."""
        # Вручную загружаем KV-файл в зависимости от платформы.
        # Это дает нам полный контроль над UI для разных устройств.
        if platform in ("win", "linux", "macosx"):
            Builder.load_file("client/desktop.kv")
        else:  # 'android', 'ios'
            Builder.load_file("client/mobile.kv")

        # Настраиваем визуальную тему приложения
        self.theme_cls.theme_style = "Dark"  # "Light" or "Dark"
        self.theme_cls.primary_palette = "Blue"  # "Red", "Green", "Purple", etc.
        return MainWidget()

    def on_start(self):
        """
        Вызывается один раз при старте приложения.
        Этот метод НЕ вызывается при горячей перезагрузке.
        """
        self.pair_widgets = {}
        # Используем Clock.schedule_once, чтобы гарантировать, что виджеты будут
        # созданы и доступны в self.root.ids перед тем, как мы к ним обратимся.
        # Это каноничный способ решения "гонки состояний" в Kivy.
        Clock.schedule_once(self.start_async_tasks)

    def start_async_tasks(self, _dt=None):
        """
        Этот метод запускает фоновые задачи после того, как GUI гарантированно отрисован.
        """
        # Теперь, когда GUI готов, мы можем безопасно запускать задачи,
        # которые будут с ним взаимодействовать.
        self.update_status("Подключение к серверу...")
        asyncio.create_task(self.fetch_pairs())
        asyncio.create_task(self.status_update_loop())

    async def fetch_pairs(self):
        """Запрашивает список доступных пар с сервера и строит для них виджеты."""
        self.update_status("Загрузка списка торговых пар...")
        try:
            response = await self.http_client.get(f"{self.server_url}/api/pairs")
            response.raise_for_status()  # Вызовет исключение для кодов 4xx/5xx
            if response.status_code == 200:
                pairs = response.json().get("pairs", [])
                self.build_pair_widgets(pairs)
            else:
                self.update_status(f"Ошибка загрузки пар: {response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch pairs: {e}")
            self.update_status("Ошибка: Сервер недоступен")

    @mainthread
    def build_pair_widgets(self, pairs: list[str]):
        """Создает и добавляет виджеты для каждой пары в GUI."""
        # Используем self.root, так как KivyMD Hot Reload может менять его
        layout = self.root.ids.pairs_layout
        if not layout:
            logger.error("Cannot build pair widgets, 'pairs_layout' not found in root.")
            return

        layout.clear_widgets()
        self.pair_widgets.clear()

        for pair in pairs:
            widget = PairWidget(pair_symbol=pair)
            self.pair_widgets[pair] = widget
            layout.add_widget(widget)

        if pairs:
            self.update_status("Пары загружены. Готов к работе.")
        else:
            self.update_status("Не удалось загрузить пары. Проверьте сервер.")

    async def status_update_loop(self):
        """Бесконечный цикл для периодического обновления статусов."""
        while True:
            await self.fetch_status()
            await asyncio.sleep(3)  # Пауза между запросами

    async def fetch_status(self):
        """Запрашивает и обновляет статус всех пар с сервера."""
        try:
            response = await self.http_client.get(
                f"{self.server_url}/api/status", timeout=2
            )
            if response.status_code == 200:
                statuses = response.json()
                self.update_pair_statuses(statuses)
        except httpx.RequestError:
            # Молчаливая ошибка, чтобы не спамить в статус-бар
            self.update_pair_statuses({})
            logger.warning("Could not fetch status, server unavailable.")

    @mainthread
    def update_pair_statuses(self, statuses: dict[str, str]):
        """Обновляет статусы виджетов пар."""
        for pair, widget in self.pair_widgets.items():
            status_text = statuses.get(pair, BotStatus.UNKNOWN)
            widget.ids.pair_status_label.text = status_text

            is_running = status_text == BotStatus.RUNNING

            # Обновляем цвет статуса для наглядности
            if is_running:
                widget.ids.pair_status_label.theme_text_color = "Custom"
                widget.ids.pair_status_label.text_color = self.theme_cls.primaryColor
            else:
                widget.ids.pair_status_label.theme_text_color = "Secondary"

            # Включаем/выключаем кнопки в зависимости от статуса
            widget.ids.start_button.disabled = is_running
            widget.ids.stop_button.disabled = not is_running

    @mainthread
    def update_status(self, text: str):
        """Безопасно обновляет главный статус-бар."""
        if self.root and self.root.ids.main_status_label:
            self.root.ids.main_status_label.text = text

    def start_bot_for_pair(self, pair_symbol: str):
        """Запускает отправку команды start для конкретной пары."""
        self.update_status(f"Отправка команды на запуск для {pair_symbol}...")
        asyncio.create_task(self._send_command(f"/api/pairs/{pair_symbol}/start"))

    def stop_bot_for_pair(self, pair_symbol: str):
        """Запускает отправку команды stop для конкретной пары."""
        self.update_status(f"Отправка команды на остановку для {pair_symbol}...")
        asyncio.create_task(self._send_command(f"/api/pairs/{pair_symbol}/stop"))

    async def _send_command(self, endpoint: str):
        """Асинхронно выполняет POST-запрос на сервер."""
        try:
            response = await self.http_client.post(f"{self.server_url}{endpoint}")
            response.raise_for_status()
            if response.status_code == 200:
                data = response.json()
                self.update_status(f"Сервер: {data.get('message', 'OK')}")
            else:
                self.update_status(f"Ошибка: {response.status_code} - {response.text}")
        except httpx.RequestError as e:
            logger.error(f"Command failed for endpoint {endpoint}: {e}")
            self.update_status("Ошибка: Сервер недоступен")
        finally:
            # После отправки команды сразу запрашиваем свежий статус
            await asyncio.sleep(
                0.5
            )  # Небольшая задержка, чтобы сервер успел обработать
            await self.fetch_status()


async def run_app(app: MDApp):
    """Асинхронная функция для запуска Kivy и управления фоновыми задачами."""
    await app.async_run(async_lib="asyncio")
    # Код здесь выполнится после закрытия окна приложения
    logger.info("Kivy app closed. Cancelling background tasks...")
    # Отменяем все еще работающие задачи (например, status_update_loop)
    for task in asyncio.all_tasks(loop=asyncio.get_running_loop()):
        if task is not asyncio.current_task():
            task.cancel()
    # Корректно закрываем http-клиент
    await app.http_client.aclose()
    logger.info("Cleanup complete.")


if __name__ == "__main__":
    # Настраиваем логгер здесь, внутри защищенного блока.
    # Это гарантирует, что дочерние процессы (созданные Loguru с enqueue=True)
    # не будут пытаться повторно инициализировать логгер, предотвращая deadlock.
    setup_logger("client")
    try:
        asyncio.run(run_app(ScalpEXApp()))
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Application interrupted by user.")
