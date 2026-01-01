@echo off
setlocal enabledelayedexpansion

REM 设置UTF-8编码
chcp 65001 >nul 2>&1

:menu
cls
echo ==========================================
echo       Weibo Archive System
echo ==========================================
echo.
echo Please select an option:
echo   1. Run Crawler (Fetch Weibo posts)
echo   2. Build Website (Generate static site)
echo   3. Start Preview (View locally)
echo   4. Full Process (Crawl + Build + Preview)
echo   5. Exit
echo.
set /p choice="Enter option (1-5): "

if "%choice%"=="1" goto crawler
if "%choice%"=="2" goto build
if "%choice%"=="3" goto preview
if "%choice%"=="4" goto all
if "%choice%"=="5" goto end
goto menu

:crawler
echo.
echo [1/1] Running crawler...
cd crawler
python weibo_spider.py
cd ..
echo.
echo Crawler completed!
pause
goto menu

:build
echo.
echo [1/1] Building website...
cd generator
python build.py
cd ..
echo.
echo Website build completed!
pause
goto menu

:preview
echo.
echo [1/1] Starting preview server...
echo Open in browser: http://localhost:8000
echo Press Ctrl+C to stop server
echo.
cd site
python -m http.server 8000
cd ..
goto menu

:all
echo.
echo [1/3] Running crawler...
cd crawler
python weibo_spider.py
cd ..

echo.
echo [2/3] Building website...
cd generator
python build.py
cd ..

echo.
echo [3/3] Starting preview server...
echo Open in browser: http://localhost:8000
echo Press Ctrl+C to stop server
echo.
cd site
python -m http.server 8000
cd ..
goto menu

:end
cls
echo.
echo Thank you for using Weibo Archive System!
echo.
timeout /t 2 >nul
exit
