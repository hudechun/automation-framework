@echo off
chcp 65001 >nul
echo ============================================
echo 🛑 停止所有服务
echo ============================================
echo.

echo 正在停止RuoYi后端...
taskkill /FI "WINDOWTITLE eq RuoYi Backend*" /F >nul 2>&1
if errorlevel 1 (
    echo    ⚠️  RuoYi后端未运行
) else (
    echo    ✅ RuoYi后端已停止
)

echo.
echo 正在停止Automation Framework...
taskkill /FI "WINDOWTITLE eq Automation Framework*" /F >nul 2>&1
if errorlevel 1 (
    echo    ⚠️  Automation Framework未运行
) else (
    echo    ✅ Automation Framework已停止
)

echo.
echo 正在停止前端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :80 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo    ✅ 前端服务已停止

echo.
echo ============================================
echo ✅ 所有服务已停止
echo ============================================
echo.
pause
