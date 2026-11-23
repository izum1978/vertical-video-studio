@echo off
chcp 65001 >nul
echo ========================================================
echo  VERTICAL VIDEO STUDIO - SEASON 2: АВТОПОДСТАВА (5 EP)
echo ========================================================
echo.
set PYTHON_BIN=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe
"%PYTHON_BIN%" -c "from backend.app.cartoon.season2_podstava import render_full_season2; render_full_season2(speaker='f5', fps=30)"
echo.
echo [ГОТОВО] Все 5 серий сохранены в output\season2_podstava\
pause
