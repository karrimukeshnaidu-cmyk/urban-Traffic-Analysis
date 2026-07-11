@echo off
echo ===================================================
echo  TrafficWise AI - GitHub Upload Helper
echo ===================================================
echo.

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    :: Check if git exists in standard installation directories
    if exist "C:\Program Files\Git\cmd\git.exe" (
        set "PATH=%PATH%;C:\Program Files\Git\cmd"
    ) else if exist "C:\Program Files (x86)\Git\cmd\git.exe" (
        set "PATH=%PATH%;C:\Program Files (x86)\Git\cmd"
    ) else (
        echo [ERROR] Git is not installed or not in your system PATH.
        echo Please install Git from https://git-scm.com/ and try again.
        echo.
        pause
        exit /b
    )
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
echo [5/5] Pushing files to GitHub (overwriting remote with completed local version)...
git push -f -u origin main

echo.
echo ===================================================
echo  Upload completed successfully!
echo ===================================================
pause
