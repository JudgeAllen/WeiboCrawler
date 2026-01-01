@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo 微博爬虫定时任务
echo 时间: %date% %time%
echo ========================================

python run.py

echo.
echo 任务完成: %date% %time%
echo ========================================
