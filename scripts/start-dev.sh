#!/bin/bash
echo "Starting ScalpEX Development Environment..."
echo "Logs from both processes will be mixed in this terminal."

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
python server/run_bot.py &
SERVER_PID=$!

# Запускаем клиент в фоновом режиме
python client/main.py &
CLIENT_PID=$!

# Ожидаем завершения обоих фоновых процессов
wait $SERVER_PID $CLIENT_PID