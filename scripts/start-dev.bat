@echo off
TITLE ScalpEX Development Launcher

echo Starting ScalpEX Development Environment...
echo This will open two new terminal windows for the Server and the Client.

REM Этот скрипт предполагает, что вы запускаете его из корневой папки проекта,
REM где уже активировано ваше виртуальное окружение (venv).

start "ScalpEX Server" cmd /k "python server/run_bot.py"

start "ScalpEX Client" cmd /k "python client/main.py"

echo Done.