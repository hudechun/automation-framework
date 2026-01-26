# 前端缓存问题修复指南

## 问题描述

访问AI模型配置页面时出现错误：
```
Failed to fetch dynamically imported module: http://localhost/src/views/thesis/ai-model/index.vue
```

## 原因

这是前端开发服务器的缓存问题，路由配置已更新但浏览器或开发服务器仍在使用旧的缓存。

## 解决方案

### 方案1：清除浏览器缓存并重启前端（推荐）

1. **停止前端开发服务器**
   - 在运行 `npm run dev` 的终端按 `Ctrl+C`

2. **清除浏览器缓存**
   - Chrome: `Ctrl+Shift+Delete` → 选择"缓存的图片和文件" → 清除数据
   - 或者使用无痕模式：`Ctrl+Shift+N`

3. **清除前端构建缓存**
   ```bash
   cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
   
   # 删除缓存目录
   rmdir /s /q node_modules\.vite
   rmdir /s /q dist
   ```

4. **重启前端开发服务器**
   ```bash
   npm run dev
   ```

5. **强制刷新浏览器**
   - `Ctrl+F5` 或 `Ctrl+Shift+R`

### 方案2：使用硬刷新

1. 打开浏览器开发者工具（F12）
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

### 方案3：修改路由配置（如果上述方案无效）

如果问题仍然存在，可能是路由配置被缓存。尝试修改路由文件触发重新加载：

```javascript
// RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/router/thesis.js

// 在文件末尾添加一个注释来触发更新
// Updated: 2026-01-26
```

然后保存文件，前端开发服务器会自动重新加载。

## 验证修复

1. 访问：http://localhost/thesis/ai-model/config
2. 应该能看到AI模型配置页面
3. 页面显示模型列表，支持下拉选择

## 如果仍然有问题

### 检查文件是否存在

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
dir src\views\thesis\ai-model\config.vue
```

应该显示文件存在。

### 检查路由配置

打开 `src/router/thesis.js`，确认有以下配置：

```javascript
'thesis/ai-model/config': () => import('@/views/thesis/ai-model/config')
```

### 检查API配置

确认 `src/api/system/aiModel.js` 文件存在并且内容正确。

## 后续建议

为避免类似问题，建议：

1. **开发时使用无痕模式**：避免缓存问题
2. **定期清理缓存**：`npm run dev` 前清理 `.vite` 目录
3. **使用硬刷新**：修改代码后使用 `Ctrl+F5` 刷新

## 完整重启流程

如果所有方案都无效，执行完整重启：

```bash
# 1. 停止所有服务
# 前端：Ctrl+C
# 后端：Ctrl+C

# 2. 清理前端缓存
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
rmdir /s /q node_modules\.vite
rmdir /s /q dist

# 3. 重启后端
cd ..\ruoyi-fastapi-backend
python app.py

# 4. 重启前端（新终端）
cd ..\ruoyi-fastapi-frontend
npm run dev

# 5. 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete

# 6. 访问页面
# http://localhost/thesis/ai-model/config
```

## 注意事项

- 确保后端服务正在运行
- 确保前端开发服务器正在运行
- 确保没有端口冲突
- 确保已部署全局AI配置系统（运行 `deploy_global_ai_config.bat`）
