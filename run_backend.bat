@echo off
title Vertical Video Studio - Backend
chcp 65001 >nul
if exist "C:\OSPanel\addons\FFMpeg\bin" set PATH=C:\OSPanel\addons\FFMpeg\bin;%PATH%
cd /d "%~dp0backend"

echo [1/3] Проверка Python и venv...
if not exist ".venv" (
    echo Создание виртуального окружения Python (.venv)...
    python -m venv .venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать .venv. Убедитесь, что Python установлен.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate

echo [2/3] Проверка и установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Ошибка при установке pip пакетов.
    pause
    exit /b 1
)

echo [3/3] Запуск FastAPI сервера на http://127.0.0.1:8000 ...
echo Документация Swagger доступна по адресу: http://127.0.0.1:8000/docs
uvicorn app.main:app --port 8000 --reload
pause
