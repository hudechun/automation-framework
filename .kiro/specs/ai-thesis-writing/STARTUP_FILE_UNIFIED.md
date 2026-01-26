# 启动文件统一说明

## 修改时间
2026-01-25

## 修改内容

### 统一启动入口
将原来分散的 `app.py` 和 `server.py` 统一为单一的 `app.py` 启动文件。

### 文件说明

#### 1. app.py（统一启动文件）✅
**位置**：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/app.py`

**功能**：
- 创建FastAPI应用实例
- 配置生命周期事件
- 注册路由、中间件、异常处理
- 挂载子应用和Automation Framework
- 提供uvicorn启动配置

**使用方法**：
```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

**特点**：
- 包含完整的应用创建逻辑
- 可以直接运行启动服务
- 支持热重载（开发模式）
- 统一的配置管理

#### 2. server.py（已弃用）⚠️
**位置**：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/server.py`

**状态**：保留仅为向后兼容

**说明**：
- 包含 `create_app()` 函数供其他模块导入
- 如果直接运行会提示使用 `app.py`
- 建议所有启动操作都使用 `app.py`

## 启动方式对比

### ✅ 推荐方式（统一）
```bash
# 开发环境
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py

# 生产环境
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
uvicorn app:app --host 0.0.0.0 --port 8000
```

### ❌ 旧方式（已弃用）
```bash
# 不再推荐
python server.py  # 会提示错误
```

## 配置说明

启动配置在 `.env` 文件中：

```env
# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
APP_RELOAD=true  # 开发模式热重载
APP_ROOT_PATH=   # 根路径前缀
```

## 开发模式 vs 生产模式

### 开发模式
```bash
# 使用 app.py（自动热重载）
python app.py
```

特点：
- 代码修改自动重启
- 详细的错误信息
- 开启调试模式

### 生产模式
```bash
# 使用 uvicorn 多进程
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

特点：
- 多进程提高性能
- 关闭热重载
- 优化的错误处理

## Docker 部署

Dockerfile 中的启动命令也应该使用 `app.py`：

```dockerfile
# 开发环境
CMD ["python", "app.py"]

# 生产环境
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 迁移指南

如果你的脚本或文档中使用了 `server.py`，请按以下方式修改：

### 1. 启动脚本
```bash
# 旧方式
python server.py

# 新方式
python app.py
```

### 2. 导入 create_app
```python
# 旧方式
from server import create_app

# 新方式
from app import create_app
```

### 3. 测试脚本
```python
# 旧方式
from server import create_app
app = create_app()

# 新方式
from app import app
# 或
from app import create_app
app = create_app()
```

## 优势

### 1. 简化项目结构
- 只有一个启动文件
- 减少混淆
- 更容易维护

### 2. 统一入口
- 所有启动都使用 `app.py`
- 配置集中管理
- 减少重复代码

### 3. 更好的可读性
- 文件名清晰表明用途
- 代码组织更合理
- 注释更完整

## 注意事项

1. **向后兼容**：`server.py` 保留了 `create_app()` 函数，现有的导入不会报错
2. **直接运行**：如果直接运行 `python server.py` 会提示使用 `app.py`
3. **测试脚本**：建议更新测试脚本使用 `from app import app`

## 总结

- ✅ 统一使用 `app.py` 启动应用
- ✅ `server.py` 保留仅为向后兼容
- ✅ 所有文档和脚本都应该引用 `app.py`
- ✅ 简化了项目结构，提高了可维护性

现在启动后端服务只需要：
```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

就这么简单！🚀
