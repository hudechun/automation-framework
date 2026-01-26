# JWT签名验证失败问题解决方案

## 问题现象
```
Error: Signature verification failed
```

## 原因分析

1. **后端服务重启** - 修改代码后重启服务，Redis中的旧Token失效
2. **浏览器缓存了旧Token** - 浏览器localStorage中存储的Token已过期
3. **JWT密钥不匹配** - 前后端使用的JWT密钥不一致（本项目已确认一致）

## 解决步骤

### 方法1：清除浏览器缓存（推荐）

1. **打开浏览器开发者工具**
   - 按 `F12` 或 `Ctrl+Shift+I`

2. **清除localStorage**
   - 切换到 `Console` 标签
   - 输入并执行：
     ```javascript
     localStorage.clear()
     ```

3. **清除sessionStorage**
   ```javascript
   sessionStorage.clear()
   ```

4. **刷新页面**
   - 按 `Ctrl+F5` 强制刷新
   - 或按 `F5` 普通刷新

5. **重新登录**
   - 使用账号密码重新登录系统

### 方法2：使用浏览器隐私模式

1. 打开新的隐私/无痕窗口
   - Chrome: `Ctrl+Shift+N`
   - Firefox: `Ctrl+Shift+P`
   - Edge: `Ctrl+Shift+N`

2. 访问系统并登录

### 方法3：清除浏览器所有数据

1. **Chrome浏览器**
   - 按 `Ctrl+Shift+Delete`
   - 选择"Cookie和其他网站数据"
   - 选择"缓存的图片和文件"
   - 点击"清除数据"

2. **Firefox浏览器**
   - 按 `Ctrl+Shift+Delete`
   - 选择"Cookie"和"缓存"
   - 点击"立即清除"

## 预防措施

### 1. 开发环境配置

在 `.env.dev` 中设置较长的Token过期时间：

```bash
# 令牌过期时间（分钟）
JWT_EXPIRE_MINUTES = 1440  # 24小时

# Redis中令牌过期时间（分钟）
JWT_REDIS_EXPIRE_MINUTES = 30
```

### 2. 后端重启后的操作

每次修改后端代码并重启服务后：
1. 清除浏览器localStorage
2. 重新登录系统

### 3. 前端开发建议

在前端请求拦截器中添加Token过期处理：

```javascript
// src/utils/request.js
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // Token过期或签名验证失败
    if (res.code === 401 || response.status === 401) {
      // 清除本地Token
      removeToken()
      // 跳转到登录页
      router.push('/login')
      return Promise.reject(new Error('Token已过期，请重新登录'))
    }
    
    return res
  },
  error => {
    // 处理签名验证失败
    if (error.message.includes('Signature verification failed')) {
      removeToken()
      router.push('/login')
      Message.error('登录已过期，请重新登录')
    }
    return Promise.reject(error)
  }
)
```

## 当前状态

✅ 后端服务已正常启动（http://0.0.0.0:9099）
✅ JWT配置正确
✅ 数据库连接正常
✅ Redis连接正常

## 下一步操作

1. 打开浏览器开发者工具（F12）
2. 在Console中执行：`localStorage.clear()`
3. 刷新页面（Ctrl+F5）
4. 重新登录系统
5. 测试模板上传功能

## 注意事项

- 每次后端重启后都需要重新登录
- 开发时建议使用浏览器的"保持登录"功能
- 生产环境应设置合理的Token过期时间
- 建议在前端添加Token自动刷新机制
