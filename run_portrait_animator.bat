@echo off
title 🎭 100%% Free LivePortrait Character Animator
chcp 65001 >nul
if exist "C:\OSPanel\addons\FFMpeg\bin" set PATH=C:\OSPanel\addons\FFMpeg\bin;%PATH%
cd /d "%~dp0"

set PYTHON=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe

if "%~1"=="" goto interactive
goto animate

:interactive
echo =======================================================
echo   🎭 100%% БЕСПЛАТНОЕ ОЖИВЛЕНИЕ ЛИЦ / ПЕРСОНАЖЕЙ (LivePortrait)
echo =======================================================
echo.
echo Перетащите файл изображения (JPG / PNG) в это окно и нажмите Enter.
echo Или нажмите Enter без ввода, чтобы оживить тестовый портрет персонажа:
set /p USER_IMG="Путь к изображению: "

if "%USER_IMG%"=="" (
    set USER_IMG=backend\app\cinematic\liveportrait\assets\examples\source\s12.jpg
)
goto do_run

:animate
set USER_IMG=%~1

:do_run
echo.
echo [1/2] Запуск LivePortrait нейросети для: %USER_IMG%
"%PYTHON%" run_cinematic.py --portrait "%USER_IMG%" --preset talking --duration 2.5 --open
echo.
echo =======================================================
echo Готово! Видео сохранено в папке output\cinematic_master\
echo =======================================================
pause
