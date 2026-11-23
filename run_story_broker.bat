@echo off
chcp 65001 >nul
echo ========================================================
echo  VERTICAL VIDEO STUDIO - НОВАЯ ИСТОРИЯ: ПРИГОН АВТО ИЗ КОРЕИ
echo ========================================================
echo.
set PYTHON_BIN=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe
"%PYTHON_BIN%" -c "from backend.app.cartoon.story_broker import render_all_broker_episodes; render_all_broker_episodes(speaker='f5', fps=30)"
echo.
echo [ГОТОВО] Все 5 серий сохранены в output\story_broker\
pause
