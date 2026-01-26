# JWT签名验证失败 - 完整解决方案

## 问题现象
```
Signature verification failed
```

## 解决步骤

### 步骤1：完全清除浏览器数据

在浏览器控制台（F12 → Console）执行以下代码：

```javascript
// 清除所有存储
localStorage.clear();
sessionStorage.clear();
document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
});

// 刷新页面
location.reload();
```

### 步骤2：检查后端是否正常运行

访问：http://localhost:9099/docs

如果能看到API文档页面，说明后端正常。

### 步骤3：重新登录

1. 访问：http://localhost（或你的前端地址）
2. 输入用户名：`admin`
3. 输入密码：`admin123`
4. 点击登录

### 步骤4：如果还是不行，检查环境配置

检查前端的API地址配置：

**文件**：`ruoyi-fastapi-frontend/.env.development`

```env
# 应该指向后端地址
VITE_APP_BASE_API = '/dev-api'
```

**文件**：`ruoyi-fastapi-frontend/vite.config.js`

检查proxy配置：

```javascript
proxy: {
  '/dev-api': {
    target: 'http://localhost:9099',  // 确保端口正确
    changeOrigin: true,
    rewrite: (p) => p.replace(/^\/dev-api/, '')
  }
}
```

### 步骤5：重启前后端服务

**后端**：
```bash
# 停止后端（Ctrl+C）
# 重新启动
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

**前端**：
```bash
# 停止前端（Ctrl+C）
# 重新启动
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
npm run dev
```

### 步骤6：使用隐私模式测试

打开浏览器隐私/无痕模式：
- Chrome: Ctrl + Shift + N
- Firefox: Ctrl + Shift + P
- Edge: Ctrl + Shift + N

在隐私模式下访问系统并登录，看是否正常。

## 如果以上都不行

### 检查JWT配置是否一致

**后端配置**：`ruoyi-fastapi-backend/.env.dev`

```env
JWT_SECRET_KEY = 'b59c07901216ccade53f8f06a8d654395ed969aef23084fe55916df8927087b5'
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 720
```

### 查看后端实时日志

```bash
# Windows PowerShell
Get-Content RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/logs/2026-01-25_error.log -Wait -Tail 20
```

### 测试登录API

在浏览器访问：http://localhost:9099/docs

找到 `/login` 接口，点击 "Try it out"，输入：

```json
{
  "username": "admin",
  "password": "admin123"
}
```

点击 Execute，查看返回结果。

如果返回成功并包含token，说明后端正常，问题在前端。

## 常见原因

1. **浏览器缓存了旧token** - 清除缓存解决
2. **前后端端口不匹配** - 检查proxy配置
3. **JWT密钥不一致** - 重启后端
4. **Token已过期** - 重新登录
5. **CORS问题** - 检查后端CORS配置

## 最终解决方案

如果以上都不行，执行以下操作：

1. **停止所有服务**
2. **清除浏览器所有数据**
3. **重启后端**
4. **重启前端**
5. **使用隐私模式访问**
6. **重新登录**

这样应该能解决问题！
