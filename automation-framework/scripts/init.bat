@echo off
REM Windows初始化脚本

echo Initializing Automation Framework...

REM 等待MySQL启动
echo Waiting for MySQL to be ready...
timeout /t 10 /nobreak >nul

REM 运行数据库迁移
echo Running database migrations...
docker-compose exec app aerich init -t src.models.database.TORTOISE_ORM
docker-compose exec app aerich init-db

echo.
echo Initialization complete!
echo.

pause
