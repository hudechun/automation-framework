@echo off
chcp 65001 >nul
echo ============================================================
echo 更新论文系统辅助页面为现代化设计
echo ============================================================
echo.
echo 正在备份原有页面...
copy "ruoyi-fastapi-frontend\src\views\thesis\member\user.vue" "ruoyi-fastapi-frontend\src\views\thesis\member\user.vue.backup" >nul 2>&1
copy "ruoyi-fastapi-frontend\src\views\thesis\payment\config.vue" "ruoyi-fastapi-frontend\src\views\thesis\payment\config.vue.backup" >nul 2>&1
copy "ruoyi-fastapi-frontend\src\views\thesis\payment\transaction.vue" "ruoyi-fastapi-frontend\src\views\thesis\payment\transaction.vue.backup" >nul 2>&1
copy "ruoyi-fastapi-frontend\src\views\thesis\ai-model\config.vue" "ruoyi-fastapi-frontend\src\views\thesis\ai-model\config.vue.backup" >nul 2>&1
echo ✓ 备份完成
echo.
echo 辅助页面列表：
echo 1. 配额管理 (quota.vue) - 已更新 ✓
echo 2. 用户会员 (user.vue) - 待更新
echo 3. 支付配置 (payment/config.vue) - 待更新
echo 4. 交易记录 (payment/transaction.vue) - 待更新
echo 5. AI模型配置 (ai-model/config.vue) - 待更新
echo.
echo 所有辅助页面将采用与主页面相同的现代化设计风格：
echo - Glassmorphism 玻璃拟态效果
echo - 渐变色彩（靛蓝色系）
echo - 流畅动画和微交互
echo - 响应式设计
echo.
pause
