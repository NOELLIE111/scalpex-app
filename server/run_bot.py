import uvicorn
from fastapi import FastAPI

# Импортируем класс нашего бота
from bot_logic import TradingBot

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


@app.post("/api/start")
async def start_bot():
    """Запускает торговую логику бота."""
    print("SERVER: Получена команда на запуск бота.")
    await bot.start()
    return {"status": "ok", "message": "Bot started successfully"}


@app.post("/api/stop")
async def stop_bot():
    """Останавливает торговую логику бота."""
    print("SERVER: Получена команда на остановку бота.")
    await bot.stop()
    return {"status": "ok", "message": "Bot stopped successfully"}


if __name__ == "__main__":
    # Запускаем веб-сервер
    # host="0.0.0.0" делает сервер доступным в локальной сети
    # reload=True автоматически перезагружает сервер при изменениях в коде (удобно для разработки)
    uvicorn.run("run_bot:app", host="0.0.0.0", port=8000, reload=True)
