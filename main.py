from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

# Импортируем наш модуль конфигурации, чтобы переменные окружения загрузились при старте
# Теперь мы импортируем его напрямую, так как он лежит в той же папке
import config

# Просто для демонстрации, что мы можем получить доступ к конфигу из любой точки программы
print(f"Загружен API ключ: {'Да' if config.BINANCE_API_KEY else 'Нет'}")

# Загружаем KV-файл для дизайна интерфейса
Builder.load_file('main_screen.kv')


class MainWidget(BoxLayout):
    """Главный виджет, чья структура описана в main_screen.kv"""
    pass


class ScalpEXApp(App):
    """Основной класс приложения Kivy"""
    def build(self):
        return MainWidget()

    def start_bot(self):
        print("Логика запуска бота будет здесь...")
        self.root.ids.status_label.text = "Статус: Работает"
        # В будущем здесь будет вызов основной логики

    def stop_bot(self):
        print("Логика остановки бота будет здесь...")
        self.root.ids.status_label.text = "Статус: Остановлен"
        # В будущем здесь будет вызов основной логики


if __name__ == '__main__':
    ScalpEXApp().run()