@echo off
echo ========================================
echo 启动Redis（带持久化配置）
echo ========================================
echo.

REM Redis安装路径
set REDIS_PATH=D:\Program Files\Redis
set REDIS_SERVER=%REDIS_PATH%\redis-server.exe

REM 检查Redis是否已安装
if not exist "%REDIS_SERVER%" (
    echo [错误] 未找到Redis安装
    echo 预期路径：%REDIS_SERVER%
    echo.
    echo 请检查Redis安装路径或修改此脚本中的REDIS_PATH变量
    echo 下载地址：https://github.com/tporadowski/redis/releases
    pause
    exit /b 1
)

REM 检查Redis服务是否正在运行
sc query Redis | find "RUNNING" >nul
if %ERRORLEVEL% EQU 0 (
    echo [警告] Redis服务正在运行
    echo 需要先停止Redis服务才能使用自定义配置启动
    echo.
    choice /C YN /M "是否停止Redis服务并使用新配置启动"
    if errorlevel 2 (
        echo 操作已取消
        pause
        exit /b 0
    )
    echo.
    echo [信息] 正在停止Redis服务...
    net stop Redis
    timeout /t 2 >nul
)

echo [信息] 使用配置文件启动Redis...
echo Redis路径：%REDIS_SERVER%
echo 配置文件：%cd%\redis.conf
echo 持久化：已启用（RDB + AOF）
echo Token过期时间：7天
echo.

"%REDIS_SERVER%" "%cd%\redis.conf"

pause
