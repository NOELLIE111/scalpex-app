import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла из корневой директории проекта
load_dotenv()

# Получаем переменные окружения
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    print("ПРЕДУПРЕЖДЕНИЕ: API ключи биржи не заданы в .env файле.")