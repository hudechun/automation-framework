# 清除浏览器缓存解决JWT签名验证失败

## 问题
`Signature verification failed` - JWT签名验证失败

## 原因
浏览器中存储的旧token与当前后端的JWT密钥不匹配

## 解决方案

### 方法1：清除浏览器存储（推荐）

1. 打开浏览器开发者工具（F12）
2. 切换到 **Application** 或 **应用程序** 标签
3. 左侧找到 **Local Storage**
4. 点击你的网站地址（如 http://localhost）
5. 右键 → **Clear** 或点击删除按钮
6. 刷新页面（F5）
7. 重新登录

### 方法2：使用浏览器隐私模式

1. 打开浏览器隐私/无痕模式
   - Chrome: Ctrl + Shift + N
   - Firefox: Ctrl + Shift + P
   - Edge: Ctrl + Shift + N
2. 访问系统
3. 登录

### 方法3：清除特定的token

在浏览器控制台（Console）执行：

```javascript
// 清除localStorage
localStorage.clear();

// 清除sessionStorage
sessionStorage.clear();

// 刷新页面
location.reload();
```

### 方法4：后端统一JWT密钥（治本）

如果经常遇到这个问题，可以统一所有环境的JWT密钥：

```bash
# 生成新密钥
python -c "import secrets; print(secrets.token_hex(32))"

# 将生成的密钥复制到所有 .env* 文件的 JWT_SECRET_KEY
```

## 预防措施

1. **开发环境固定密钥**：开发环境使用固定的JWT密钥，避免频繁更换
2. **生产环境独立密钥**：生产环境使用独立的强密钥
3. **Token过期时间**：设置合理的token过期时间
4. **自动刷新token**：前端实现token自动刷新机制

## 验证是否解决

清除缓存后，重新登录，如果能正常访问系统，说明问题已解决。
