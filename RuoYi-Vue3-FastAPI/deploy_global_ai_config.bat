@echo off
chcp 65001 >nul
echo ============================================================
echo 部署全局AI配置系统
echo ============================================================
echo.

cd ruoyi-fastapi-backend

echo 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 开始部署...
python ..\deploy_global_ai_config.py

echo.
echo 按任意键退出...
pause >nul
