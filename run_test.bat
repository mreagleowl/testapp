@echo off
REM Устанавливаем кодировку UTF-8
chcp 65001 >nul

REM Переходим в папку со скриптом
cd /d "%~dp0"

REM ----------------------------------------------------------------
REM 1) Создаём виртуальное окружение, если его нет
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Виртуальное окружение не найдено. Создаём .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Не удалось создать виртуальное окружение!
        pause
        exit /b 1
    )
)

REM ----------------------------------------------------------------
REM 2) Активируем виртуальное окружение
call ".venv\Scripts\activate.bat"

REM ----------------------------------------------------------------
REM 3) Устанавливаем зависимости (опционально, если requirements.txt есть)
if exist requirements.txt (
    echo [INFO] Устанавливаем зависимости...
    pip install -r requirements.txt
)

REM ----------------------------------------------------------------
REM 4) Запускаем приложение
echo [INFO] Запускаем приложение...
python main.py

pause
