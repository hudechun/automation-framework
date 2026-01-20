@echo off
REM Windows开发环境启动脚本（不使用Docker）

echo Starting Automation Framework in Development Mode...

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 安装依赖
echo Installing dependencies...
pip install -r requirements.txt

REM 安装Playwright浏览器
echo Installing Playwright browsers...
python -m playwright install

REM 检查.env文件
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration
    pause
)

REM 启动服务
echo Starting API server...
echo.
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Admin: http://localhost:8000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
