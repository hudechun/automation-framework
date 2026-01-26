@echo off
chcp 65001 >nul
echo ========================================
echo 测试AI模型配置新字段
echo ========================================
echo.

cd /d "%~dp0"

echo 正在测试...
python test_ai_model_fields.py

echo.
echo 按任意键退出...
pause >nul
