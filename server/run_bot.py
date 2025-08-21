"""
Основной файл для запуска веб-сервера (API) на FastAPI.
"""

from contextlib import asynccontextmanager

# Стандартные и сторонние импорты
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from loguru import logger

# Импорты из нашего приложения
from .bot_logic import TradingBot
from managers.loguru_manager import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения FastAPI.
    Код перед `yield` выполняется при старте, код после `yield` - при остановке.
    """
    # --- Код при старте ---
    setup_logger("server")
    load_dotenv()
    logger.info("Initializing TradingBot...")
    app.state.bot = TradingBot()
    logger.info("Server startup complete.")
    yield
    # --- Код при остановке ---
    logger.info("Server shutting down.")


app = FastAPI(
    title="ScalpEX Trading Bot API",
    description="API для управления торговым ботом ScalpEX",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def read_root():
    """Корневой эндпоинт для проверки доступности сервера."""
    return {"status": "ok", "message": "ScalpEX Bot Server is running"}


@app.get("/api/pairs")
async def get_configured_pairs(request: Request):
    """Возвращает список торговых пар, настроенных на сервере."""
    return {"pairs": request.app.state.bot.trading_pairs}


@app.get("/api/status")
async def get_bot_status(request: Request):
    """Возвращает текущий статус работы бота по всем парам."""
    return request.app.state.bot.get_status()


@app.post("/api/pairs/{pair_symbol}/start")
async def start_bot_for_pair(pair_symbol: str, request: Request):
    """Запускает торговую логику для указанной пары."""
    bot = request.app.state.bot
    logger.info(f"Received a command to start the bot for {pair_symbol}.")
    try:
        bot.start_for_pair(pair_symbol.upper())
        return {"status": "ok", "message": f"Bot started for {pair_symbol}"}
    except ValueError as e:
        logger.error(f"Failed to start bot for {pair_symbol}: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/pairs/{pair_symbol}/stop")
async def stop_bot_for_pair(pair_symbol: str, request: Request):
    """Останавливает торговую логику для указанной пары."""
    bot = request.app.state.bot
    logger.info(f"Received a command to stop the bot for {pair_symbol}.")
    bot.stop_for_pair(pair_symbol.upper())
    return {"status": "ok", "message": f"Bot stopped for {pair_symbol}"}


if __name__ == "__main__":
    # Запускаем веб-сервер
    # host="0.0.0.0" делает сервер доступным в локальной сети
    # reload=True автоматически перезагружает сервер при изменениях в коде (удобно для разработки)
    uvicorn.run("server.run_bot:app", host="0.0.0.0", port=8000, reload=True)
