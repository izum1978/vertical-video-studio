@echo off
chcp 65001 > nul
set GIT_DIR=.git_repo

if "%~1"=="" goto usage

echo >>> Setting remote to: %1
git remote remove origin 2>nul
git remote add origin %1
echo >>> Pushing to GitHub (main branch)...
git push -u origin main
echo.
echo 🎉 Push complete!
pause
exit /b 0

:usage
echo =======================================================
echo Использование: push_to_github.bat ^<URL_РЕПОЗИТОРИЯ^>
echo Пример:
echo   push_to_github.bat https://github.com/ваш_логин/vertical-video-studio.git
echo =======================================================
pause
