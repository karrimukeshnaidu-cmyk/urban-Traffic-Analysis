@echo off
echo ===================================================
echo  TrafficWise AI - GitHub Upload Helper
echo ===================================================
echo.

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your system PATH.
    echo Please install Git from https://git-scm.com/ and try again.
    echo.
    pause
    exit /b
)

echo [1/5] Initializing Git repository...
git init

echo.
echo [2/5] Adding project files...
git add .

echo.
echo [3/5] Committing changes...
git commit -m "Refactor Traffic Dashboard into Industry-Grade Analytics and Prediction Application"

echo.
echo [4/5] Configuring main branch and remote URL...
git branch -M main
git remote remove origin >nul 2>nul
git remote add origin https://github.com/karrimukeshnaidu-cmyk/urban-Traffic-Analysis.git

echo.
echo [5/5] Pushing files to GitHub...
git push -u origin main

echo.
echo ===================================================
echo  Upload completed successfully!
echo ===================================================
pause
