# 清除Token快速指南

## 问题

"Signature verification failed" 错误导致无法进入登录页面。

## 原因

浏览器localStorage中存储了失效的Token，前端路由守卫尝试验证时失败。

## 解决方案

### 方法1：浏览器开发者工具（最快）

1. **打开开发者工具**
   - 按 `F12` 或 `Ctrl + Shift + I`

2. **打开Console标签**

3. **执行以下命令**
   ```javascript
   localStorage.clear()
   sessionStorage.clear()
   ```

4. **刷新页面**
   - 按 `F5` 或 `Ctrl + R`

5. **完成！** 现在可以正常访问登录页

### 方法2：浏览器设置清除

**Chrome/Edge**：
1. 按 `Ctrl + Shift + Delete`
2. 选择"Cookie和其他网站数据"
3. 选择"缓存的图片和文件"
4. 点击"清除数据"

**Firefox**：
1. 按 `Ctrl + Shift + Delete`
2. 选择"Cookie"和"缓存"
3. 点击"立即清除"

### 方法3：隐私模式（临时）

1. 打开隐私/无痕窗口
   - Chrome/Edge: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`

2. 访问系统并登录

## 已修复

我已经修改了前端路由守卫（`permission.js`），现在：

✅ **Token失效时自动处理**
- 自动清除失效的Token
- 显示友好的错误提示
- 自动跳转到登录页

✅ **不会再卡在错误页面**
- 即使Token失效也能访问登录页
- 用户体验更好

## 测试步骤

1. **清除当前Token**（使用上面的方法1）
2. **刷新页面**
3. **验证**：应该自动跳转到登录页
4. **登录系统**
5. **验证**：正常使用

## 下次遇到这个问题

如果将来再次遇到"Signature verification failed"错误：

1. 打开开发者工具（F12）
2. 在Console中执行：`localStorage.clear()`
3. 刷新页面

就这么简单！

## 预防措施

为了避免这个问题，我已经：

1. ✅ 延长Token有效期到7天
2. ✅ 修改路由守卫自动处理Token失效
3. ✅ 修改请求拦截器自动处理签名验证失败

现在系统会自动处理Token失效的情况，不需要手动清除Token了。
