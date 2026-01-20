@echo off
echo ============================================
echo RuoYi-Vue3-FastAPI 安装脚本
echo ============================================
echo.

cd ruoyi-fastapi-backend

echo 1. 创建Python虚拟环境...
py -3.10 -m venv .venv
if errorlevel 1 (
    echo 错误：无法创建虚拟环境
    pause
    exit /b 1
)
echo    ✅ 虚拟环境创建成功

echo.
echo 2. 激活虚拟环境...
call .venv\Scripts\activate
echo    ✅ 虚拟环境已激活

echo.
echo 3. 安装Python依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 错误：依赖安装失败
    pause
    exit /b 1
)
echo    ✅ 依赖安装成功

echo.
echo ============================================
echo ✅ 安装完成！
echo ============================================
echo.
echo 下一步：
echo 1. 导入SQL文件到数据库
echo 2. 运行: python app.py --env=dev
echo.
pause
