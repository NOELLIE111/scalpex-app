import threading

import requests
from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

# Загружаем KV-файл для дизайна интерфейса
Builder.load_file("main_screen.kv")


class MainWidget(BoxLayout):
    """Главный виджет, чья структура описана в main_screen.kv"""

    pass


class ScalpEXApp(App):
    """Основной класс приложения Kivy (клиент)"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_url = "http://127.0.0.1:8000"

    def build(self):
        return MainWidget()

    def send_request(self, endpoint):
        """Отправляет запрос на сервер в отдельном потоке, чтобы не блокировать GUI."""
        try:
            url = f"{self.server_url}{endpoint}"
            response = requests.post(url, timeout=5)  # 5 секунд на ответ
            if response.status_code == 200:
                # Успешный ответ от сервера
                data = response.json()
                self.update_status(f"Сервер: {data.get('message', 'OK')}")
            else:
                # Сервер ответил ошибкой
                self.update_status(f"Ошибка: {response.status_code}")
        except requests.exceptions.RequestException:
            # Не удалось подключиться к серверу
            self.update_status("Ошибка: Сервер недоступен")

    @mainthread
    def update_status(self, text):
        """Безопасно обновляет GUI из любого потока."""
        self.root.ids.status_label.text = text

    def start_bot(self):
        """Запускает отправку команды /api/start в фоновом потоке."""
        self.update_status("Отправка команды на запуск...")
        threading.Thread(
            target=self.send_request, args=("/api/start",), daemon=True
        ).start()

    def stop_bot(self):
        """Запускает отправку команды /api/stop в фоновом потоке."""
        self.update_status("Отправка команды на остановку...")
        threading.Thread(
            target=self.send_request, args=("/api/stop",), daemon=True
        ).start()


if __name__ == "__main__":
    ScalpEXApp().run()
