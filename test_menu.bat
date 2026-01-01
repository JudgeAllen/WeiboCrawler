@echo off
setlocal enabledelayedexpansion

REM Test menu display
chcp 65001 >nul 2>&1

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
echo Menu test successful!
echo.
pause
