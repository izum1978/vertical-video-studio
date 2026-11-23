@echo off
chcp 65001 >nul
echo ========================================================
echo  VERTICAL VIDEO STUDIO - НОВАЯ ИСТОРИЯ: ФАЛЬШИВЫЙ ЭВАКУАТОР
echo ========================================================
echo.
set PYTHON_BIN=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe
"%PYTHON_BIN%" -c "from backend.app.cartoon.story_evacuator import render_all_evacuator_episodes; render_all_evacuator_episodes(speaker='f5', fps=30)"
echo.
echo [ГОТОВО] Все 5 серий сохранены в output\story_evacuator\
pause
