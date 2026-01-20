@echo off
REM Windows停止脚本

echo Stopping Automation Framework...

docker-compose down

echo.
echo Services stopped successfully!
echo.

pause
