@echo off
chcp 65001 >nul
echo ========================================
echo 初始化支付配置
echo ========================================
echo.

cd /d "%~dp0"

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 执行初始化脚本
python init_payment_configs.py

echo.
pause
