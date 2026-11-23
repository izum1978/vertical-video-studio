@echo off
title Vertical Video Studio - Frontend
chcp 65001 >nul
cd /d "%~dp0frontend"

where npm >nul 2>nul
if errorlevel 1 (
    echo [ОШИБКА] Node.js и npm не найдены в PATH!
    echo Установите Node.js (v18+) с официального сайта: https://nodejs.org/
    echo или через winget: winget install OpenJS.NodeJS.LTS
    pause
    exit /b 1
)

echo [1/2] Проверка зависимостей фронтенда...
if not exist "node_modules" (
    echo Установка npm пакетов...
    call npm install
    if errorlevel 1 (
        echo [ОШИБКА] Сбой при установке npm пакетов.
        pause
        exit /b 1
    )
)

echo [2/2] Запуск Vite Dev Server (http://localhost:5173)...
call npm run dev
pause
