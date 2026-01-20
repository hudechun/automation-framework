# FastAPI-Admin 管理后台设置指南

## 概述

项目已集成FastAPI-Admin框架，提供完整的Web管理界面。

## 功能特性

- ✅ 完整的Web UI界面
- ✅ 任务管理（CRUD操作）
- ✅ 会话管理
- ✅ 模型配置管理
- ✅ 用户认证和权限管理
- ✅ 文件上传功能
- ✅ 搜索和过滤
- ✅ 响应式设计

## 访问管理后台

启动服务后，访问：

```
http://localhost:8000/admin
```

## 默认登录

**用户名**: admin  
**密码**: admin

⚠️ **重要**: 首次使用后请立即修改默认密码！

## 配置说明

### 1. 静态文件

静态文件存储在 `static/` 目录：
```bash
mkdir -p static
```

### 2. 上传文件

上传的文件存储在 `uploads/` 目录：
```bash
mkdir -p uploads
```

### 3. 数据库模型

管理后台自动注册以下模型：
- **Task**: 任务管理
- **Session**: 会话管理
- **ModelConfig**: 模型配置

### 4. 自定义资源

要添加新的管理资源，编辑 `src/api/admin.py`：

```python
@admin_app.register(
    YourModel,
    label="资源名称",
    icon="fas fa-icon",
)
class YourResource:
    label = "资源"
    model = YourModel
    page_size = 20
    fields = ["id", "name", "created_at"]
    search_fields = ["name"]
    ordering = ["-created_at"]
```

## 功能说明

### 任务管理

- 查看所有任务
- 创建新任务
- 编辑任务配置
- 删除任务
- 搜索任务（按名称、描述）
- 按创建时间排序

### 会话管理

- 查看所有会话
- 查看会话详情
- 按会话ID搜索
- 按创建时间排序

### 模型配置

- 管理AI模型配置
- 启用/禁用模型
- 搜索配置（按名称、提供商、模型）
- 按创建时间排序

## 权限管理

### 创建管理员用户

```python
from src.api.admin import AdminConfig

admin_config = AdminConfig(app)
await admin_config.create_admin_user(
    username="newadmin",
    password="secure_password",
    role="admin"
)
```

### 角色说明

- **admin**: 完全访问权限
- **editor**: 编辑权限
- **viewer**: 只读权限

## 自定义配置

### 修改登录Logo

编辑 `src/api/admin.py`：

```python
UsernamePasswordProvider(
    login_logo_url="https://your-logo-url.com/logo.svg",
    admin_model=None,
)
```

### 修改页面大小

```python
class TaskResource:
    page_size = 50  # 每页显示50条记录
```

### 添加自定义操作

```python
class TaskResource:
    # 添加自定义按钮
    actions = [
        {
            "label": "执行任务",
            "icon": "fas fa-play",
            "method": Method.POST,
            "ajax": True,
        }
    ]
```

## 主题定制

FastAPI-Admin支持主题定制，可以修改：
- 颜色方案
- 字体
- 布局
- 图标

参考官方文档：https://github.com/fastapi-admin/fastapi-admin

## 备用API

如果不使用Web界面，可以使用备用REST API：

```bash
# 登录
POST /admin/api/login

# 获取仪表板数据
GET /admin/api/dashboard

# 获取任务列表
GET /admin/api/tasks

# 获取用户列表
GET /admin/api/users
```

## 故障排除

### 问题1: 静态文件404

**解决方案**: 确保 `static/` 目录存在
```bash
mkdir -p static
```

### 问题2: 上传失败

**解决方案**: 确保 `uploads/` 目录存在且有写权限
```bash
mkdir -p uploads
chmod 755 uploads
```

### 问题3: 登录失败

**解决方案**: 检查数据库连接和Admin用户表

### 问题4: 模型未显示

**解决方案**: 确保模型已在 `admin.py` 中注册

## 安全建议

1. ✅ 修改默认密码
2. ✅ 使用HTTPS
3. ✅ 启用CSRF保护
4. ✅ 限制管理后台访问IP
5. ✅ 定期备份数据库
6. ✅ 启用审计日志

## 性能优化

1. 启用分页（已默认启用）
2. 添加数据库索引
3. 使用缓存
4. 优化查询

## 更多资源

- [FastAPI-Admin官方文档](https://github.com/fastapi-admin/fastapi-admin)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Tortoise-ORM文档](https://tortoise.github.io/)

---

**最后更新**: 2026年1月19日
