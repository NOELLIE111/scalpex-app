
from kivy.app import App
from dotenv import load_dotenv
import os

load_dotenv() # Загружает переменные из файла .env

# Создаем класс нашего приложения, наследуясь от App
class ScalpExApp(App):
    # Теперь метод build() может быть пустым.
    # Kivy автоматически загрузит файл scalpex.kv и использует его
    # как корневой виджет.
    def build(self):
        pass # Kivy загрузит scalpex.kv

    def handle_button_press(self):
        # self.root дает доступ к корневому виджету (нашему BoxLayout)
        # self.root.ids дает доступ ко всем виджетам внутри, у которых есть id        
        info_label = self.root.ids.info_label # Находим виджет по его id
        api_key = os.getenv("API_KEY", "Ключ не найден") # Безопасно получаем ключ
        
        print(f"Загружен API ключ: {api_key}")
        info_label.text = "Отлично! Текст изменен из Python!"

# Стандартная точка входа в Python-скрипт
if __name__ == '__main__':
    # Создаем экземпляр нашего приложения и запускаем его
    ScalpExApp().run()
