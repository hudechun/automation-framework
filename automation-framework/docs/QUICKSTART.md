# 快速入门指南

## 安装

### 使用Docker（推荐）

```bash
# 克隆仓库
git clone <repository-url>
cd automation-framework

# 启动服务
bash scripts/start.sh

# 初始化数据库
bash scripts/init.sh
```

### 手动安装

```bash
# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
python -m playwright install

# 配置数据库
# 编辑 .env 文件

# 运行数据库迁移
aerich init -t src.models.database.TORTOISE_ORM
aerich init-db

# 启动服务
uvicorn src.api.main:app --reload
```

## 第一个任务

### 使用Python SDK

```python
import asyncio
from src.sdk import AutomationClient

async def main():
    async with AutomationClient() as client:
        # 创建任务
        task = await client.tasks.create(
            name="My First Task",
            description="Navigate to example.com",
            actions=[
                {
                    "type": "goto",
                    "url": "https://example.com"
                },
                {
                    "type": "screenshot",
                    "path": "example.png"
                }
            ]
        )
        
        # 执行任务
        result = await client.tasks.execute_and_wait(task["id"])
        print(f"Task completed: {result['status']}")

asyncio.run(main())
```

### 使用CLI

```bash
# 初始化配置
python -m src.cli.main config init

# 创建任务
python -m src.cli.main task create "My First Task"

# 列出任务
python -m src.cli.main task list

# 执行任务
python -m src.cli.main task execute <task-id> --wait
```

### 使用REST API

```bash
# 创建任务
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Task",
    "description": "Navigate to example.com",
    "actions": [
      {"type": "goto", "url": "https://example.com"},
      {"type": "screenshot", "path": "example.png"}
    ]
  }'

# 执行任务
curl -X POST http://localhost:8000/api/tasks/{task_id}/execute
```

## 访问管理界面

打开浏览器访问：
- API文档: http://localhost:8000/docs
- 管理后台: http://localhost:8000/admin

## 下一步

- 查看[API参考文档](API_REFERENCE.md)
- 查看[示例代码](../examples/)
- 查看[配置指南](CONFIGURATION.md)
