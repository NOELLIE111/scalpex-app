"""
Основной файл клиентского GUI-приложения на Kivy.
"""

import threading
import requests
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

# Загружаем KV-файл для дизайна интерфейса
Builder.load_file("main_screen.kv")


class PairWidget(GridLayout):
    """Виджет для управления одной торговой парой."""

    def __init__(self, pair_symbol: str, app_instance: App, **kwargs):
        super().__init__(**kwargs)
        self.cols = 4
        self.size_hint_y = None
        self.height = "48dp"
        self.pair_symbol = pair_symbol
        self.app = app_instance

        self.add_widget(Label(text=pair_symbol))

        self.status_label = Label(text="Unknown")
        self.add_widget(self.status_label)

        start_button = Button(text="Start")
        start_button.bind(on_press=self.start_trading)
        self.add_widget(start_button)

        stop_button = Button(text="Stop")
        stop_button.bind(on_press=self.stop_trading)
        self.add_widget(stop_button)

    def start_trading(self, _instance):
        self.app.start_bot_for_pair(self.pair_symbol)

    def stop_trading(self, _instance):
        self.app.stop_bot_for_pair(self.pair_symbol)


class MainWidget(BoxLayout):
    """Главный виджет, чья структура описана в main_screen.kv"""

    pass


class ScalpEXApp(App):
    """Основной класс приложения Kivy (клиент)"""

    def __init__(self, **kwargs):
        """Инициализирует приложение и задает URL сервера."""
        super().__init__(**kwargs)
        self.server_url = "http://127.0.0.1:8000"

    def build(self):
        """Создает и возвращает корневой виджет приложения."""
        return MainWidget()

    def on_start(self):
        """Вызывается при старте приложения. Загружаем пары и запускаем обновление статуса."""
        self.pair_widgets: dict[str, PairWidget] = {}
        self.fetch_pairs()
        # Запрашивать статус каждые 3 секунды
        Clock.schedule_interval(self.fetch_status, 3)

    def fetch_pairs(self):
        """Запрашивает список доступных пар с сервера и строит для них виджеты."""
        self.update_status("Загрузка списка торговых пар...")
        threading.Thread(target=self._fetch_pairs_thread, daemon=True).start()

    def _fetch_pairs_thread(self):
        """Выполняет GET-запрос для получения пар в фоновом потоке."""
        try:
            url = f"{self.server_url}/api/pairs"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                pairs = response.json().get("pairs", [])
                self.build_pair_widgets(pairs)
            else:
                self.update_status(f"Ошибка загрузки пар: {response.status_code}")
        except requests.exceptions.RequestException:
            self.update_status("Ошибка: Сервер недоступен")

    @mainthread
    def build_pair_widgets(self, pairs: list[str]):
        """Создает и добавляет виджеты для каждой пары в GUI."""
        layout = self.root.ids.pairs_layout
        layout.clear_widgets()  # Очищаем на случай перезагрузки
        if not pairs:
            layout.add_widget(
                Label(text="На сервере не настроено ни одной торговой пары.")
            )
            return

        for pair in pairs:
            widget = PairWidget(pair_symbol=pair, app_instance=self)
            self.pair_widgets[pair] = widget
            layout.add_widget(widget)
        self.update_status("Пары загружены. Готов к работе.")

    def fetch_status(self, _dt=None):
        """Запрашивает статус всех пар с сервера."""
        threading.Thread(target=self._fetch_status_thread, daemon=True).start()

    def _fetch_status_thread(self):
        """Выполняет GET-запрос для получения статусов в фоновом потоке."""
        try:
            url = f"{self.server_url}/api/status"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                statuses = response.json()
                self.update_pair_statuses(statuses)
        except requests.exceptions.RequestException:
            # Молчаливая ошибка, чтобы не спамить в статус-бар
            self.update_pair_statuses({})
            print("Could not fetch status, server unavailable.")

    @mainthread
    def update_pair_statuses(self, statuses: dict[str, str]):
        """Обновляет статусы виджетов пар."""
        for pair, widget in self.pair_widgets.items():
            status = statuses.get(pair, "Unknown")
            widget.status_label.text = status

    @mainthread
    def update_status(self, text: str):
        """Безопасно обновляет главный статус-бар из любого потока."""
        self.root.ids.status_label.text = text

    def start_bot_for_pair(self, pair_symbol: str):
        """Запускает отправку команды start для конкретной пары."""
        self.update_status(f"Отправка команды на запуск для {pair_symbol}...")
        endpoint = f"/api/pairs/{pair_symbol}/start"
        threading.Thread(
            target=self._send_command_thread, args=(endpoint,), daemon=True
        ).start()

    def stop_bot_for_pair(self, pair_symbol: str):
        """Запускает отправку команды stop для конкретной пары."""
        self.update_status(f"Отправка команды на остановку для {pair_symbol}...")
        endpoint = f"/api/pairs/{pair_symbol}/stop"
        threading.Thread(
            target=self._send_command_thread, args=(endpoint,), daemon=True
        ).start()

    def _send_command_thread(self, endpoint: str):
        """Отправляет POST-запрос на сервер в отдельном потоке."""
        try:
            url = f"{self.server_url}{endpoint}"
            response = requests.post(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.update_status(f"Сервер: {data.get('message', 'OK')}")
            else:
                self.update_status(f"Ошибка: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException:
            self.update_status("Ошибка: Сервер недоступен")
        finally:
            # После отправки команды сразу запрашиваем свежий статус
            self.fetch_status()


if __name__ == "__main__":
    ScalpEXApp().run()
