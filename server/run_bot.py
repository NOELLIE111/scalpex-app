"""
Основной файл для запуска веб-сервера (API) на FastAPI.
"""

# Стандартные и сторонние импорты
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger

# Импорты из нашего приложения
from bot_logic import TradingBot
from managers.loguru_manager import setup_logger

# --- Настройка и запуск ---
# Функции настройки должны вызываться после всех импортов,
# но до инициализации компонентов, которые от них зависят.

setup_logger()

# Загружаем переменные окружения из .env файла в самом начале.
# Это нужно сделать до импорта других наших модулей, которые могут их использовать.
load_dotenv()

app = FastAPI(
    title="ScalpEX Trading Bot API",
    description="API для управления торговым ботом ScalpEX",
    version="0.1.0",
)

# Создаем единственный экземпляр бота, который будет жить, пока работает сервер
bot = TradingBot()


@app.get("/")
async def read_root():
    """Корневой эндпоинт для проверки доступности сервера."""
    return {"status": "ok", "message": "ScalpEX Bot Server is running"}


@app.get("/api/pairs")
async def get_configured_pairs():
    """Возвращает список торговых пар, настроенных на сервере."""
    return {"pairs": bot.trading_pairs}


@app.get("/api/status")
async def get_bot_status():
    """Возвращает текущий статус работы бота по всем парам."""
    return bot.get_status()


@app.post("/api/pairs/{pair_symbol}/start")
async def start_bot_for_pair(pair_symbol: str):
    """Запускает торговую логику для указанной пары."""
    logger.info(f"Received a command to start the bot for {pair_symbol}.")
    try:
        bot.start_for_pair(pair_symbol.upper())
        return {"status": "ok", "message": f"Bot started for {pair_symbol}"}
    except ValueError as e:
        logger.error(f"Failed to start bot for {pair_symbol}: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/pairs/{pair_symbol}/stop")
async def stop_bot_for_pair(pair_symbol: str):
    """Останавливает торговую логику для указанной пары."""
    logger.info(f"Received a command to stop the bot for {pair_symbol}.")
    bot.stop_for_pair(pair_symbol.upper())
    return {"status": "ok", "message": f"Bot stopped for {pair_symbol}"}


if __name__ == "__main__":
    # Запускаем веб-сервер
    # host="0.0.0.0" делает сервер доступным в локальной сети
    # reload=True автоматически перезагружает сервер при изменениях в коде (удобно для разработки)
    uvicorn.run("run_bot:app", host="0.0.0.0", port=8000, reload=True)
