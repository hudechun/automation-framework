@echo off
chcp 65001 >nul
echo ========================================
echo 更新AI模型记录的model_type字段
echo ========================================
echo.

cd /d "%~dp0"

echo 正在更新...
python update_model_type.py

echo.
echo 按任意键退出...
pause >nul
