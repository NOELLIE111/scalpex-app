#!/bin/bash

# Определяем абсолютный путь к директории, где находится скрипт
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Переходим в корневую директорию проекта (на один уровень выше папки scripts)
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

echo "Starting ScalpEX Development Environment from project root: $PROJECT_ROOT"
echo "Logs from both processes will be mixed in this terminal."

# Активируем виртуальное окружение. Это ключ к решению проблемы!
echo "Activating virtual environment..."
source ./venv/bin/activate

# Эта функция будет вызвана при нажатии Ctrl+C
cleanup() {
    echo -e "\nStopping processes..."
    kill $CLIENT_PID
    kill $SERVER_PID
    echo "All processes stopped."
}

# "Ловим" сигнал прерывания (Ctrl+C) и вызываем функцию очистки
trap cleanup INT

# Запускаем сервер в фоновом режиме
python -m server.run_bot &
SERVER_PID=$!

# Запускаем клиент в фоновом режиме
python -m client.main &
CLIENT_PID=$!

# Ожидаем завершения обоих фоновых процессов
wait $SERVER_PID $CLIENT_PID