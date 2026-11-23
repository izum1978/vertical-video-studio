@echo off
chcp 65001 >nul
echo ========================================================
echo  VERTICAL VIDEO STUDIO - 2D CARTOON EXPLAINER GENERATOR
echo ========================================================
echo.

set PYTHON_BIN=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PYTHON_BIN%" (
    echo [ERROR] Python not found at %PYTHON_BIN%
    pause
    exit /b 1
)

echo [INFO] Запуск генерации 2D мультфильма...
"%PYTHON_BIN%" -c "from pathlib import Path; from backend.app.cartoon.assembler import render_cartoon_video; render_cartoon_video(output_path=Path('output/cartoon_master/cartoon_scene_latest.mp4'))"

echo.
echo ========================================================
echo [ГОТОВО] Видео сохранено в output\cartoon_master\
echo ========================================================
pause
