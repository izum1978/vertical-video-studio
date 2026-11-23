@echo off
title ✨ 100%% Free Real-ESRGAN 4K UHD Upscaler (NVIDIA RTX 4050)
chcp 65001 >nul
cd /d "%~dp0"

set PYTHON=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe

if "%~1"=="" goto interactive
goto upscale

:interactive
echo =======================================================
echo   ✨ 100%% БЕСПЛАТНЫЙ НЕЙРОСЕТЕВОЙ 4K АПСКЕЙЛЕР (Real-ESRGAN)
echo =======================================================
echo.
echo Перетащите файл изображения (JPG / PNG) в это окно и нажмите Enter.
echo Или нажмите Enter без ввода, чтобы апскейлить тестовый кадр:
set /p USER_IMG="Путь к изображению: "

if "%USER_IMG%"=="" (
    set USER_IMG=backend\app\cinematic\realesrgan\input.jpg
)
goto do_run

:upscale
set USER_IMG=%~1

:do_run
echo.
echo [1/2] Запуск Real-ESRGAN x4plus на NVIDIA RTX GPU для: %USER_IMG%
"%PYTHON%" run_cinematic.py --upscale "%USER_IMG%" --open
echo.
echo =======================================================
echo Готово! 4K изображение сохранено в папке output\cinematic_master\
echo =======================================================
pause
