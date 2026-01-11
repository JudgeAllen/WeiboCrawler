@echo off
REM 微博归档系统 - Windows一键升级脚本
REM 用途：更新本地开发环境到最新版本

chcp 65001 > nul
setlocal enabledelayedexpansion

echo ==========================================
echo 微博归档系统 - 一键升级（Windows）
echo ==========================================
echo.

REM 检查Git
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未安装Git
    echo 请先安装Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM 获取当前目录
set PROJECT_DIR=%~dp0..
cd /d "%PROJECT_DIR%"

echo 项目目录: %CD%
echo.

REM 检查是否是Git仓库
if not exist ".git" (
    echo [错误] 不是Git仓库
    echo 无法自动升级，请手动下载最新代码
    pause
    exit /b 1
)

echo [1/6] 检查当前状态...

REM 获取当前版本
for /f "tokens=*" %%i in ('git rev-parse --short HEAD') do set CURRENT_COMMIT=%%i
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%i
echo 当前版本: %CURRENT_BRANCH% @ %CURRENT_COMMIT%

REM 检查未提交的更改
git diff-index --quiet HEAD -- >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [警告] 检测到本地未提交的更改
    echo.
    git status --short
    echo.
    set /p CONTINUE="是否继续升级？未提交的更改可能会丢失 (y/n): "
    if /i "!CONTINUE!" NEQ "y" (
        echo 升级已取消
        pause
        exit /b 0
    )
)

echo.
echo [2/6] 获取最新代码...

REM 拉取最新代码
git pull origin main
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 拉取代码失败
    pause
    exit /b 1
)

REM 检查是否有更新
for /f "tokens=*" %%i in ('git rev-parse --short HEAD') do set NEW_COMMIT=%%i
if "%CURRENT_COMMIT%" == "%NEW_COMMIT%" (
    echo [√] 已是最新版本，无需更新
    set SKIP_UPDATE=true
) else (
    echo [√] 代码已更新: %CURRENT_COMMIT% -^> %NEW_COMMIT%
    set SKIP_UPDATE=false
)

echo.
echo [3/6] 更新Python依赖...

REM 检查虚拟环境
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo 正在更新依赖包...
    python -m pip install --upgrade pip -q
    pip install -r requirements.txt -q
    if %ERRORLEVEL% EQU 0 (
        echo [√] Python依赖已更新
    ) else (
        echo [!] 依赖更新失败，但继续执行
    )
) else (
    echo [!] 虚拟环境不存在，跳过依赖更新
    echo 如需创建虚拟环境：python -m venv .venv
)

echo.
echo [4/6] 检查数据库...

if exist "data\database.db" (
    for %%A in ("data\database.db") do set DB_SIZE=%%~zA
    set /a DB_SIZE_MB=!DB_SIZE! / 1048576
    echo [√] 数据库正常 (大小: !DB_SIZE_MB! MB)
) else (
    echo [!] 数据库不存在，首次运行将创建
)

echo.
echo [5/6] 检查配置文件...

if exist "crawler\config.json" (
    echo [√] 配置文件存在
) else (
    if exist "crawler\config.json.example" (
        echo [!] 配置文件不存在，请复制config.json.example并配置
        echo    copy crawler\config.json.example crawler\config.json
    )
)

echo.
echo [6/6] 升级完成检查...

REM 显示更新日志
if "%SKIP_UPDATE%" == "false" (
    echo.
    echo 更新内容:
    git log --oneline --pretty=format:"  %%h - %%s" %CURRENT_COMMIT%..HEAD
    echo.
)

echo.
echo ==========================================
echo [√] 升级完成！
echo ==========================================
echo.

REM 获取新版本
for /f "tokens=*" %%i in ('git rev-parse --short HEAD') do set FINAL_COMMIT=%%i
echo 当前版本: %FINAL_COMMIT%
echo.

echo 下一步操作：
echo.
echo 【开发模式】
echo   1. 启动调度器: python scheduler.py
echo   2. 启动Web服务: python app.py
echo   3. 访问: http://localhost:5000
echo.
echo 【生成静态网站】
echo   1. cd generator
echo   2. python build.py
echo   3. cd ..\site
echo   4. python -m http.server 8000
echo.
echo 【查看文档】
echo   - README.md - 主文档
echo   - QUICKSTART.md - 快速开始
echo   - deploy\VPS_DEPLOYMENT.md - VPS部署
echo.

pause
