@echo off

REM Определяем абсолютный путь к директории проекта (на один уровень выше папки scripts)
REM %~dp0 - это путь к текущему скрипту. `..` - переход на уровень выше.
cd /d "%~dp0.."
echo Switched to project root: %cd%

echo Starting ScalpEX Development Environment...

REM Активируем виртуальное окружение. Это ключ к решению проблемы!
echo Activating virtual environment...
call .\\venv\\Scripts\\activate.bat

REM Запускаем сервер в новом окне
echo Starting Server (as a module)...
start "ScalpEX Server" cmd /k "python -m server.run_bot"

REM Запускаем клиент в новом окне
echo Starting Client (as a module)...
start "ScalpEX Client" cmd /k "python -m client.main"

echo Both processes are running in separate windows.