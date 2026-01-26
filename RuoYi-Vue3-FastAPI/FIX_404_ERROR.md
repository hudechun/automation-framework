# AI模型配置404错误 - 诊断和修复指南

## 错误信息

```
Failed to load resource: the server responded with a status of 404 (Not Found)
AxiosError: Request failed with status code 404
```

## 快速诊断

### 步骤1: 测试路由注册

```bash
cd RuoYi-Vue3-FastAPI
python test_ai_model_routes.py
```

这个脚本会检查:
- ✅ 模块是否能正确导入
- ✅ 路由是否正确注册
- ✅ 路由数量和路径

### 步骤2: 检查后端启动日志

查看后端启动时的日志，确认是否有错误信息。

### 步骤3: 访问API文档

打开浏览器访问: http://localhost:9099/docs

在文档中搜索 "ai-model"，确认API是否存在。

## 常见原因和解决方案

### 原因1: 后端未重启 ⭐ 最常见

**症状**: 代码已更新，但API仍然404

**解决**:
```bash
# 停止后端（Ctrl+C）
# 重新启动
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

### 原因2: 导入错误

**症状**: 后端启动时有错误信息

**诊断**:
```bash
python test_ai_model_routes.py
```

**解决**: 根据错误信息修复导入问题

### 原因3: 路由未注册

**症状**: 测试脚本显示路由未找到

**检查**:
```python
# 检查 module_thesis/controller/__init__.py
# 应该包含:
from module_thesis.controller.ai_model_controller import ai_model_controller

__all__ = [
    'ai_model_controller',
    # ...
]
```

**解决**: 确保 `ai_model_controller` 已导出

### 原因4: 端口或路径错误

**症状**: 前端请求的URL不正确

**检查前端API配置**:
```javascript
// src/api/thesis/aiModel.js
// 应该使用相对路径
url: '/thesis/ai-model/list'  // ✅ 正确
url: 'http://localhost:9099/thesis/ai-model/list'  // ❌ 错误
```

**检查环境变量**:
```javascript
// .env.development
VITE_APP_BASE_API = '/dev-api'
```

### 原因5: 数据库表不存在

**症状**: 后端启动正常，但访问API时报错

**检查**:
```sql
SHOW TABLES LIKE 'ai_write_ai_model_config';
```

**解决**:
```bash
mysql -u root -p ry-vue < ruoyi-fastapi-backend/sql/ai_model_schema.sql
```

## 完整修复流程

### 1. 确认文件存在

```bash
# 检查后端文件
ls -la RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/controller/ai_model_controller.py
ls -la RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/service/ai_model_service.py
ls -la RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/dao/ai_model_dao.py

# 检查前端文件
ls -la RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/api/thesis/aiModel.js
ls -la RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/thesis/ai-model/config.vue
```

### 2. 测试导入

```bash
cd RuoYi-Vue3-FastAPI
python test_ai_model_routes.py
```

### 3. 重启后端

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend

# 停止现有进程（如果正在运行）
# Windows: Ctrl+C 或 taskkill /F /IM python.exe
# Linux/Mac: Ctrl+C 或 pkill -f "python app.py"

# 启动后端
python app.py
```

### 4. 检查启动日志

查看启动日志，确认:
- ✅ 没有导入错误
- ✅ 路由注册成功
- ✅ 服务器正常启动

### 5. 验证API

访问: http://localhost:9099/docs

搜索 "AI模型配置" 或 "ai-model"，确认API存在。

### 6. 测试API

在API文档中测试一个接口，例如:
```
GET /thesis/ai-model/list
```

### 7. 清除前端缓存

- 打开浏览器开发者工具（F12）
- 右键点击刷新按钮
- 选择"清空缓存并硬性重新加载"
- 或者: Ctrl+Shift+Delete 清除缓存

### 8. 重新访问前端

访问: http://localhost/thesis/ai-model

## 验证清单

- [ ] 后端文件存在
- [ ] 前端文件存在
- [ ] 数据库表存在
- [ ] 菜单已创建
- [ ] 测试脚本通过
- [ ] 后端已重启
- [ ] 启动日志无错误
- [ ] API文档中能看到接口
- [ ] 前端缓存已清除
- [ ] 能访问前端页面

## 调试技巧

### 1. 查看网络请求

打开浏览器开发者工具（F12）-> Network标签

查看实际请求的URL:
```
Request URL: http://localhost/dev-api/thesis/ai-model/list
```

### 2. 查看后端日志

后端应该会打印请求日志:
```
INFO: 127.0.0.1:xxxxx - "GET /thesis/ai-model/list HTTP/1.1" 200 OK
```

如果是404:
```
INFO: 127.0.0.1:xxxxx - "GET /thesis/ai-model/list HTTP/1.1" 404 Not Found
```

### 3. 直接访问API

使用curl或Postman测试:
```bash
curl http://localhost:9099/thesis/ai-model/list
```

### 4. 检查路由前缀

确认controller中的prefix设置:
```python
ai_model_controller = APIRouterPro(
    prefix='/thesis/ai-model',  # 应该是这个
    # ...
)
```

## 常见错误模式

### 错误1: 路径不匹配

```
前端请求: /dev-api/thesis/ai-model/list
后端路由: /thesis/ai-model/list
Nginx转发: /dev-api -> /
结果: ✅ 正确
```

### 错误2: 端口错误

```
前端请求: http://localhost:80/dev-api/thesis/ai-model/list
后端监听: http://localhost:9099
Nginx转发: 80 -> 9099
结果: ✅ 正确（如果Nginx配置正确）
```

### 错误3: 路由未注册

```
后端启动: ✅ 成功
API文档: ❌ 没有ai-model相关接口
原因: controller未导入或auto_register=False
```

## 获取帮助

如果问题仍然存在，请提供:

1. **测试脚本输出**:
   ```bash
   python test_ai_model_routes.py > test_output.txt 2>&1
   ```

2. **后端启动日志**:
   ```bash
   python app.py > backend.log 2>&1
   ```

3. **浏览器Network截图**:
   - 打开F12 -> Network
   - 重现错误
   - 截图请求详情

4. **API文档截图**:
   - 访问 http://localhost:9099/docs
   - 搜索 "thesis"
   - 截图所有论文系统相关的API

---

**更新时间**: 2026-01-25  
**状态**: 诊断指南
