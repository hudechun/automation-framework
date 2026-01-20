# 从 Tortoise ORM 迁移到 SQLAlchemy

## 迁移概述

我们已经将 automation-framework 从 Tortoise ORM 迁移到 SQLAlchemy，与 RuoYi 后端统一使用相同的 ORM 框架。

## 主要变更

### 1. 数据模型

**之前（Tortoise ORM）:**
- `src/models/task.py` - Tortoise 模型
- `src/models/session.py` - Tortoise 模型
- `src/models/config.py` - Tortoise 模型
- `src/models/file.py` - Tortoise 模型

**现在（SQLAlchemy）:**
- `src/models/sqlalchemy_models.py` - 所有 SQLAlchemy 模型
- 统一使用 RuoYi 的 `Base` 类

### 2. 数据库连接

**之前:**
- 独立的 Tortoise 数据库连接
- 使用 `TORTOISE_ORM` 配置

**现在:**
- 统一使用 RuoYi 的数据库连接池
- 自动检测是否已挂载到 RuoYi
- 如果独立运行，创建独立的连接

### 3. 路径管理

**之前:**
- `mount_automation.py` 直接修改 `sys.path`

**现在:**
- 使用 `AutomationFrameworkPathManager` 类
- 支持环境变量配置
- 自动路径查找
- 更好的错误处理

### 4. 依赖变更

**移除:**
- `tortoise-orm`
- `aiomysql`
- `aerich`

**新增:**
- `sqlalchemy>=2.0.0`
- `asyncmy>=0.2.9` (MySQL 异步驱动)

## 使用方式

### 导入模型

```python
# 新的导入方式
from src.models import Task, Session, ModelConfig

# 或者
from src.models.sqlalchemy_models import Task, Session, ModelConfig
```

### 数据库会话

```python
from src.models.database import get_db_session

# 获取数据库会话
async def some_function():
    async for db in get_db_session():
        # 使用 db 进行数据库操作
        result = await db.execute(select(Task))
        tasks = result.scalars().all()
```

### 在 RuoYi 中挂载

挂载方式保持不变，但路径管理更优雅：

```python
from mount_automation import mount_automation_app

app = FastAPI(...)
mount_automation_app(app)
```

## 环境变量

可以通过环境变量配置 automation-framework 路径：

```bash
export AUTOMATION_FRAMEWORK_PATH=/path/to/automation-framework
```

## 向后兼容

- 旧的 Tortoise 模型文件仍然存在（但已标记为废弃）
- `TORTOISE_ORM` 变量保留（但值为 None）
- 导入旧模型会失败，提示迁移到 SQLAlchemy

## 迁移检查清单

- [x] 创建 SQLAlchemy 模型
- [x] 更新数据库连接管理
- [x] 优化路径管理
- [x] 更新依赖配置
- [x] 更新 API 路由导入
- [ ] 更新所有使用 Tortoise 模型的代码（如果有）
- [ ] 运行测试验证
- [ ] 更新文档

## 注意事项

1. **数据库迁移**: 如果使用 Aerich，需要迁移到 Alembic（与 RuoYi 统一）
2. **查询语法**: SQLAlchemy 的查询语法与 Tortoise 不同，需要更新相关代码
3. **关系定义**: SQLAlchemy 使用 `relationship()` 定义关系，与 Tortoise 的 `ForeignKeyField` 不同

## 问题排查

### 导入错误

如果遇到导入错误，检查：
1. automation-framework 路径是否正确
2. 环境变量 `AUTOMATION_FRAMEWORK_PATH` 是否设置
3. RuoYi 后端路径是否正确

### 数据库连接错误

如果遇到数据库连接错误：
1. 检查是否已挂载到 RuoYi（使用统一连接池）
2. 检查独立运行时的数据库配置（`.env` 文件）

## 相关文件

- `src/models/sqlalchemy_models.py` - SQLAlchemy 模型定义
- `src/models/database.py` - 数据库连接管理
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/mount_automation.py` - 挂载逻辑
- `requirements.txt` - 依赖配置
- `pyproject.toml` - 项目配置
