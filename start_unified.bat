@echo off
chcp 65001 >nul
echo ============================================
echo 🚀 启动统一后端服务
echo    RuoYi + Automation Framework (单端口)
echo ============================================
echo.

REM 检查Python 3.10
py -3.10 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python 3.10
    pause
    exit /b 1
)
echo ✅ Python 3.10 已安装

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Node.js
    pause
    exit /b 1
)
echo ✅ Node.js 已安装
echo.

REM 启动统一后端（RuoYi + Automation）
echo [1/2] 启动统一后端服务...
cd RuoYi-Vue3-FastAPI\ruoyi-fastapi-backend

if not exist .venv (
    echo    创建虚拟环境...
    py -3.10 -m venv .venv
    call .venv\Scripts\activate
    echo    安装RuoYi依赖...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo    安装Automation依赖...
    pip install -r ..\..\automation-framework\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    python -m playwright install
) else (
    call .venv\Scripts\activate
)

echo    启动中...
start "Unified Backend" cmd /k "cd /d %CD% && .venv\Scripts\activate && python app.py --env=dev"

echo    等待后端启动...
timeout /t 10 >nul

cd ..\..
echo ✅ 统一后端已启动
echo.

REM 启动前端
echo [2/2] 启动前端服务...
cd RuoYi-Vue3-FastAPI\ruoyi-fastapi-frontend

if not exist node_modules (
    echo    安装依赖...
    call npm install --registry=https://registry.npmmirror.com
)

echo    启动中...
start "RuoYi Frontend" cmd /k "cd /d %CD% && npm run dev"
timeout /t 5 >nul

cd ..\..
echo ✅ 前端已启动
echo.

echo ============================================
echo ✅ 所有服务已启动！
echo ============================================
echo.
echo 📋 服务地址:
echo.
echo 🌐 开发环境（推荐用于开发调试）:
echo    - 前端界面: http://localhost:5173
echo    - 优化页面: http://localhost:5173/automation/task/create
echo    - 后端API: http://localhost:9099/dev-api
echo    - API文档: http://localhost:9099/dev-api/docs
echo.
echo 🌐 生产环境（如果已部署到 Nginx）:
echo    - 前端界面: http://localhost
echo    - 优化页面: http://localhost/automation/task/create
echo    - 后端API: http://localhost:9099/dev-api
echo.
echo 🤖 Automation Framework (已集成):
echo    - API路径: http://localhost:9099/automation/api/*
echo    - 任务管理: http://localhost:9099/automation/api/tasks
echo    - 会话管理: http://localhost:9099/automation/api/sessions
echo    - WebSocket: ws://localhost:9099/automation/ws
echo.
echo 👤 默认账号:
echo    - 用户名: admin
echo    - 密码: admin123
echo.
echo 💡 提示:
echo    - 开发时使用 5173 端口（实时热更新）
echo    - 生产部署需要运行: 重新构建并部署.bat
echo    - 如果访问 80 端口出现 404，说明需要重新构建前端
echo.
echo 按任意键打开浏览器...
pause >nul

REM 打开浏览器（开发环境）
start http://localhost:5173
timeout /t 2 >nul
start http://localhost:9099/dev-api/docs

echo.
echo 浏览器已打开，按任意键退出...
pause >nul
