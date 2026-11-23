@echo off
title Vertical Video Studio - Launcher
chcp 65001 >nul

echo ================================================================
echo          VERTICAL VIDEO STUDIO — ЗАПУСК СТУДИИ
echo ================================================================
echo Запуск локального AI-движка на GPU (порт 8189)...
start "VVS AI Engine (GPU)" cmd /k "%~dp0run_ai_engine.bat"

echo Ожидание 3 секунды...
timeout /t 3 >nul

echo Запуск бэкенда в отдельном окне...
start "VVS Backend" cmd /k "%~dp0run_backend.bat"

echo Ожидание 3 секунды...
timeout /t 3 >nul

echo Запуск фронтенда в отдельном окне...
start "VVS Frontend" cmd /k "%~dp0run_frontend.bat"

echo.
echo ================================================================
echo  AI Engine (GPU): http://127.0.0.1:8189
echo  Бэкенд API:     http://127.0.0.1:8000
echo  Документация:   http://127.0.0.1:8000/docs
echo  Фронтенд UI:    http://localhost:5173
echo ================================================================
echo.
