# 数据库初始化指南

## 📁 文件说明

- **`schema.sql`** - 完整的数据库表结构（包含所有表、索引、视图）
- **`schema_minimal.sql`** - 最小化表结构（仅核心表）
- **`README.md`** - 本文档

## 🚀 快速开始

### 方式1：使用完整SQL脚本

```bash
# 连接MySQL
mysql -u root -p

# 执行SQL脚本
source automation-framework/database/schema.sql

# 或使用命令行直接导入
mysql -u root -p < automation-framework/database/schema.sql
```

### 方式2：使用最小化SQL脚本

```bash
# 仅创建核心表
mysql -u root -p < automation-framework/database/schema_minimal.sql
```

### 方式3：使用Tortoise-ORM自动创建

```bash
# 进入项目目录
cd automation-framework

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 初始化Aerich
aerich init -t src.models.database.TORTOISE_ORM

# 创建初始迁移
aerich init-db

# 应用迁移（创建表）
aerich upgrade
```

## 📊 数据库表结构

### 核心表

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `tasks` | 任务表 | id, name, actions, status |
| `execution_records` | 执行记录表 | id, task_id, status, logs |
| `sessions` | 会话表 | id, session_id, state |
| `model_configs` | 模型配置表 | id, name, provider, model |

### 扩展表

| 表名 | 说明 |
|------|------|
| `schedules` | 调度表 |
| `session_checkpoints` | 会话检查点表 |
| `model_metrics` | 模型性能指标表 |
| `system_logs` | 系统日志表 |
| `notification_configs` | 通知配置表 |
| `file_storage` | 文件存储表 |
| `plugins` | 插件表 |
| `performance_metrics` | 性能指标表 |

## 🔧 配置数据库连接

### 方法1：使用环境变量

在 `.env` 文件中配置：

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=automation_framework
```

### 方法2：修改配置文件

编辑 `src/models/database.py`：

```python
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "your_password",
                "database": "automation_framework",
            }
        }
    },
    # ...
}
```

## 📝 创建数据库和用户

### 手动创建

```sql
-- 创建数据库
CREATE DATABASE automation_framework 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'automation'@'localhost' IDENTIFIED BY 'automation123';

-- 授予权限
GRANT ALL PRIVILEGES ON automation_framework.* TO 'automation'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;
```

### 使用脚本创建

```bash
# 创建数据库和用户
mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS automation_framework CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'automation'@'localhost' IDENTIFIED BY 'automation123';
GRANT ALL PRIVILEGES ON automation_framework.* TO 'automation'@'localhost';
FLUSH PRIVILEGES;
EOF
```

## 🔍 验证安装

### 检查表是否创建成功

```sql
USE automation_framework;

-- 显示所有表
SHOW TABLES;

-- 查看表结构
DESC tasks;
DESC execution_records;
DESC sessions;

-- 查看表统计
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    ROUND(DATA_LENGTH/1024/1024, 2) AS 'Size(MB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'automation_framework';
```

### 测试连接

```bash
# 使用Python测试
python << EOF
import asyncio
from src.models.database import init_db, close_db

async def test():
    await init_db()
    print("✅ 数据库连接成功！")
    await close_db()

asyncio.run(test())
EOF
```

## 🗄️ 数据库迁移

### 使用Aerich管理迁移

```bash
# 初始化Aerich（首次）
aerich init -t src.models.database.TORTOISE_ORM

# 初始化数据库
aerich init-db

# 创建新迁移（修改模型后）
aerich migrate --name "description"

# 应用迁移
aerich upgrade

# 回滚迁移
aerich downgrade

# 查看迁移历史
aerich history
```

## 🔄 数据备份和恢复

### 备份数据库

```bash
# 备份整个数据库
mysqldump -u root -p automation_framework > backup_$(date +%Y%m%d).sql

# 仅备份表结构
mysqldump -u root -p --no-data automation_framework > schema_backup.sql

# 仅备份数据
mysqldump -u root -p --no-create-info automation_framework > data_backup.sql
```

### 恢复数据库

```bash
# 恢复数据库
mysql -u root -p automation_framework < backup_20260119.sql
```

## 🐛 常见问题

### 1. 字符集问题

**错误**: `Incorrect string value`

**解决**:
```sql
ALTER DATABASE automation_framework CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE tasks CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 连接被拒绝

**错误**: `Can't connect to MySQL server`

**解决**:
- 检查MySQL服务是否启动
- 检查防火墙设置
- 检查用户权限

```sql
-- 允许远程连接
GRANT ALL PRIVILEGES ON automation_framework.* TO 'automation'@'%' IDENTIFIED BY 'automation123';
FLUSH PRIVILEGES;
```

### 3. 表已存在

**错误**: `Table 'tasks' already exists`

**解决**:
```sql
-- 删除所有表（谨慎使用！）
DROP DATABASE automation_framework;
CREATE DATABASE automation_framework CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 或使用 IF NOT EXISTS
CREATE TABLE IF NOT EXISTS tasks (...);
```

### 4. JSON字段不支持

**错误**: `Unknown column type 'JSON'`

**解决**: 升级MySQL到5.7+或使用TEXT类型替代

## 📚 相关文档

- [MySQL官方文档](https://dev.mysql.com/doc/)
- [Tortoise-ORM文档](https://tortoise.github.io/)
- [Aerich文档](https://github.com/tortoise/aerich)

## 🆘 获取帮助

如果遇到问题：
1. 检查MySQL版本（需要5.7+）
2. 检查字符集配置
3. 查看错误日志
4. 参考本文档的常见问题部分

---

**最后更新**: 2026-01-19
