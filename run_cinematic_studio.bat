@echo off
title 100%% Free Cinematic AI Video Studio
chcp 65001 >nul
if exist "C:\OSPanel\addons\FFMpeg\bin" set PATH=C:\OSPanel\addons\FFMpeg\bin;%PATH%
cd /d "%~dp0"

C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe run_cinematic.py %*
pause

