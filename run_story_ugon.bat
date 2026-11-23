@echo off
chcp 65001 >nul
echo ========================================================
echo  VERTICAL VIDEO STUDIO - НОВАЯ ИСТОРИЯ: УГОН НА УДОЧКУ
echo ========================================================
echo.
set PYTHON_BIN=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe
"%PYTHON_BIN%" -c "from backend.app.cartoon.story_ugon import render_all_ugon_episodes; render_all_ugon_episodes(speaker='f5', fps=30)"
echo.
echo [ГОТОВО] Все 5 серий сохранены в output\story_ugon_udochka\
pause
