@echo off
chcp 65001 >nul
echo ========================================================
echo  VERTICAL VIDEO STUDIO - 30s CRYPTO TRADER CARTOON
echo ========================================================
echo.

set PYTHON_BIN=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PYTHON_BIN%" (
    echo [ERROR] Python not found at %PYTHON_BIN%
    pause
    exit /b 1
)

echo [INFO] Генерация мультфильма с живым голосом Евгения (Eugene)...
"%PYTHON_BIN%" -c "from pathlib import Path; from backend.app.cartoon.crypto_scene import render_crypto_trader_video; render_crypto_trader_video(output_path=Path('output/cartoon_master/crypto_trader_eugene.mp4'), speaker='eugene', voice_engine='silero')"

echo.
echo ========================================================
echo [ГОТОВО] Видео сохранено в output\cartoon_master\crypto_trader_eugene.mp4
echo ========================================================
pause
