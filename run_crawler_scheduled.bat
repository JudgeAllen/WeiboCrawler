@echo off
setlocal enabledelayedexpansion

REM 设置UTF-8编码
chcp 65001 >nul 2>&1

cd /d "%~dp0"

echo ========================================
echo       Weibo Crawler Scheduled Task
echo ========================================
echo.
echo Start Time: %date% %time%
echo.

cd crawler
python weibo_spider.py
cd ..

echo.
echo Completed: %date% %time%
echo ========================================
