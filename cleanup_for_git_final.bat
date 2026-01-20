@echo off
chcp 65001 >nul
echo ============================================
echo 🧹 清理项目文件（准备上传 Git）
echo ============================================
echo.

echo 📋 将要删除的内容:
echo    • 临时测试文件
echo    • 临时文档和说明
echo    • 临时批处理脚本
echo    • 备份文件
echo    • Python 缓存
echo    • 运行时目录 (vf_admin, logs)
echo    • ui-ux-pro-max-skill-main (已集成到 .kiro)
echo    • config 目录 (未使用，已被 RuoYi 配置替代)
echo.
echo 按任意键开始清理，或 Ctrl+C 取消...
pause >nul
echo.

echo [1/8] 删除临时测试文件...
del /Q RuoYi-Vue3-FastAPI\test_*.py 2>nul
del /Q RuoYi-Vue3-FastAPI\check_*.py 2>nul
del /Q RuoYi-Vue3-FastAPI\list_*.py 2>nul
del /Q RuoYi-Vue3-FastAPI\验证*.py 2>nul
del /Q RuoYi-Vue3-FastAPI\测试*.html 2>nul
del /Q automation-framework\test_*.py 2>nul
del /Q automation-framework\debug_*.py 2>nul
echo ✅ 完成

echo.
echo [2/8] 删除临时文档和说明文件...
del /Q RuoYi-Vue3-FastAPI\访问*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\如何*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\UI优化*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\任务创建*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\重新构建*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\部署模式*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\解决404*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\生产环境*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\访问方式*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\在后台*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\快速修复*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\菜单配置*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\API接口*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\测试指南.md 2>nul
del /Q RuoYi-Vue3-FastAPI\前端页面*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\错误修复*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\手动配置*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\UI设计*.md 2>nul
del /Q RuoYi-Vue3-FastAPI\自动化平台*.md 2>nul
del /Q automation-framework\CONTEXT_TRANSFER*.md 2>nul
del /Q automation-framework\GETTING_STARTED*.md 2>nul
del /Q automation-framework\INSTALLATION_TROUBLESHOOTING.md 2>nul
del /Q automation-framework\STATUS_*.md 2>nul
del /Q automation-framework\IMPLEMENTATION_STATUS.md 2>nul
del /Q automation-framework\PROGRESS.md 2>nul
del /Q automation-framework\PROJECT_COMPLETE.md 2>nul
del /Q automation-framework\FINAL_CHECKLIST.md 2>nul
del /Q 工作总结.md 2>nul
del /Q 快速参考卡.md 2>nul
del /Q NEXT_STEPS.md 2>nul
del /Q STARTUP_TROUBLESHOOTING.md 2>nul
del /Q START_GUIDE.md 2>nul
echo ✅ 完成

echo.
echo [3/8] 删除临时批处理脚本...
del /Q RuoYi-Vue3-FastAPI\启动*.bat 2>nul
del /Q RuoYi-Vue3-FastAPI\检查*.bat 2>nul
del /Q RuoYi-Vue3-FastAPI\重新构建*.bat 2>nul
del /Q RuoYi-Vue3-FastAPI\一键*.bat 2>nul
del /Q RuoYi-Vue3-FastAPI\执行*.bat 2>nul
del /Q RuoYi-Vue3-FastAPI\restart_backend.bat 2>nul
del /Q 诊断*.bat 2>nul
del /Q check_redis.bat 2>nul
echo ✅ 完成

echo.
echo [4/8] 删除备份文件...
del /Q /S *.bak 2>nul
del /Q /S *.backup 2>nul
del /Q /S *111 2>nul
echo ✅ 完成

echo.
echo [5/8] 清理 Python 缓存...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /Q /S *.pyc 2>nul
echo ✅ 完成

echo.
echo [6/8] 清理 Node.js 缓存...
del /Q RuoYi-Vue3-FastAPI\ruoyi-fastapi-frontend\package-lock.json 2>nul
echo ✅ 完成

echo.
echo [7/8] 删除运行时目录...
rd /s /q vf_admin 2>nul
rd /s /q logs 2>nul
rd /s /q automation-framework\storage 2>nul
rd /s /q automation-framework\uploads 2>nul
echo ✅ 完成

echo.
echo [8/9] 删除 UI/UX 工具包（已集成）...
rd /s /q ui-ux-pro-max-skill-main 2>nul
echo ✅ 完成

echo.
echo [9/9] 删除未使用的 config 目录（已被 RuoYi 配置替代）...
rd /s /q config 2>nul
echo ✅ 完成

echo.
echo ============================================
echo ✅ 清理完成！
echo ============================================
echo.
echo 📋 已清理的内容:
echo    ✓ 临时测试文件 (test_*.py, check_*.py, debug_*.py)
echo    ✓ 临时文档和说明文件
echo    ✓ 临时批处理脚本
echo    ✓ 备份文件 (*.bak, *111)
echo    ✓ Python 缓存 (__pycache__, *.pyc)
echo    ✓ Node.js 缓存文件
echo    ✓ 运行时目录 (vf_admin, logs, storage, uploads)
echo    ✓ UI/UX 工具包 (ui-ux-pro-max-skill-main)
echo    ✓ 未使用的 config 目录
echo.
echo 📋 保留的重要文件:
echo    ✓ 源代码文件
echo    ✓ 配置示例 (.env.example, config.example.json)
echo    ✓ 数据库脚本 (*.sql)
echo    ✓ 启动脚本 (start_*.bat)
echo    ✓ 核心文档 (README.md, QUICK_START.md)
echo    ✓ .kiro 配置（包含 UI/UX steering）
echo.
echo 💡 下一步:
echo    1. 检查 .gitignore 文件
echo    2. git status （查看将要提交的文件）
echo    3. git add .
echo    4. git commit -m "Initial commit"
echo    5. git push
echo.
pause
