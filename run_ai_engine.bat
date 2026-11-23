@echo off
title Vertical Video Studio - Local AI Engine (SD-Turbo / SDXL)
chcp 65001 >nul
cd /d "%~dp0ai_engine"

echo ================================================================
echo    ЛОКАЛЬНЫЙ НЕЙРОСЕТЕВОЙ ГЕНЕРАТОР КАДРОВ (RTX 4050 6GB)
echo ================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ОШИБКА] Окружение .venv не найдено.
    pause
    exit /b 1
)

echo Запуск FastAPI сервера AI-генератора на http://127.0.0.1:8189 ...
.venv\Scripts\python.exe server.py
pause
