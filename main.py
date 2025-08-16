from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

# Импортируем наш модуль конфигурации
import config

# Импортируем класс нашего бота
from bot import TradingBot

# Просто для демонстрации, что мы можем получить доступ к конфигу из любой точки программы
print(f"Загружен API ключ: {'Да' if config.BINANCE_API_KEY else 'Нет'}")

# Загружаем KV-файл для дизайна интерфейса
Builder.load_file("main_screen.kv")


class MainWidget(BoxLayout):
    """Главный виджет, чья структура описана в main_screen.kv"""

    pass


class ScalpEXApp(App):
    """Основной класс приложения Kivy"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Создаем экземпляр бота при инициализации приложения
        self.bot = TradingBot()

    def build(self):
        return MainWidget()

    def start_bot(self):
        print("Получена команда на запуск бота...")
        self.bot.start()
        self.root.ids.status_label.text = "Статус: Работает"

    def stop_bot(self):
        print("Получена команда на остановку бота...")
        self.bot.stop()
        self.root.ids.status_label.text = "Статус: Остановлен"


if __name__ == "__main__":
    ScalpEXApp().run()
