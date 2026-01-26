@echo off
chcp 65001 >nul
echo ========================================
echo 全局AI配置系统 - 快速部署
echo ========================================
echo.

cd /d %~dp0

echo [1/3] 部署数据库...
python deploy_global_ai_config.py
if errorlevel 1 (
    echo 数据库部署失败！
    pause
    exit /b 1
)
echo.

echo [2/3] 重启后端服务...
echo 请手动重启后端服务：
echo   cd ruoyi-fastapi-backend
echo   python server.py
echo.

echo [3/3] 清除前端缓存...
echo 请在浏览器中按 Ctrl+Shift+Delete 清除缓存
echo 或者按 Ctrl+F5 强制刷新页面
echo.

echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 访问路径：系统管理 ^> AI模型配置
echo API端点：/system/ai-model/list
echo.
pause
