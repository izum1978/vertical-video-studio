@echo off
chcp 65001 >nul
echo ========================================================
echo  VERTICAL VIDEO STUDIO - НОВАЯ ИСТОРИЯ: АВТОСЕРВИС-ЛОВУШКА
echo ========================================================
echo.
set PYTHON_BIN=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe
"%PYTHON_BIN%" -c "from backend.app.cartoon.story_autoservice import render_all_autoservice_episodes; render_all_autoservice_episodes(speaker='f5', fps=30)"
echo.
echo [ГОТОВО] Все 5 серий сохранены в output\story_autoservice\
pause
