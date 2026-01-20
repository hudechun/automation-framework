@echo off
REM Windows启动脚本

echo Starting Automation Framework...

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker Compose is not installed
    pause
    exit /b 1
)

REM 创建必要的目录
if not exist "storage\screenshots" mkdir storage\screenshots
if not exist "storage\logs" mkdir storage\logs
if not exist "storage\videos" mkdir storage\videos
if not exist "storage\exports" mkdir storage\exports
if not exist "logs" mkdir logs
if not exist "nginx\ssl" mkdir nginx\ssl

REM 启动服务
docker-compose up -d

echo.
echo Services started successfully!
echo.
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Admin: http://localhost:8000/admin
echo.

REM 显示服务状态
docker-compose ps

pause
