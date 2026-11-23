@echo off
chcp 65001 >nul
echo ========================================================
echo  VERTICAL VIDEO STUDIO - 2D CARTOON AUTOPILOT v2 (GPU)
echo ========================================================
echo.
echo Введите тему ролика (или нажмите Enter для темы по умолчанию):
echo Примеры:
echo   - Как меня кинул автодилер
echo   - Парень пришёл просить прибавку к зарплате
echo   - Как я открыл кофейню в спальнике
echo.
set /p TOPIC="Тема: "

if "%TOPIC%"=="" (
    set TOPIC=Как меня кинул автодилер
)

echo.
echo Выберите озвучку (Enter = f5 - живой клонированный голос на RTX 4050):
echo   f5     - F5-TTS Russian GPU (уровень ElevenLabs, клон голоса)
echo   eugene - Silero v5.6 Евгений
echo   aidar  - Silero v5.6 Айдар
echo   xenia  - Silero v5.6 Ксения
set /p VOICE="Озвучка [f5]: "

if "%VOICE%"=="" (
    set VOICE=f5
)

echo.
echo [AUTOPILOT v2] Запуск генерации ролика по теме: "%TOPIC%" (голос: %VOICE%)...
echo.

set PYTHON_BIN=C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe

"%PYTHON_BIN%" -c "from pathlib import Path; from backend.app.cartoon.autopilot import render_autopilot_video; render_autopilot_video(topic='''%TOPIC%''', output_path=Path('output/cartoon_master/autopilot_latest.mp4'), speaker='%VOICE%')"

echo.
echo ========================================================
echo [ГОТОВО] Ролик собран и сохранён:
echo output\cartoon_master\autopilot_latest.mp4
echo ========================================================
pause
