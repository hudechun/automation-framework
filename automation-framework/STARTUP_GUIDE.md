# 项目启动指南

本指南将帮助你快速启动浏览器与桌面自动化框架。

## 📋 前置要求

### 必需
- **Python 3.11+**
- **MySQL 8.0+** 或 **Docker** + **Docker Compose**

### 可选
- **Redis** (用于缓存，可选)
- **Nginx** (用于生产环境部署)

## 🚀 启动方式

有三种启动方式可选：

### 方式1：使用Docker（推荐，最简单）

适合快速体验和生产部署。

```bash
# 1. 进入项目目录
cd automation-framework

# 2. 启动所有服务（包括MySQL、Redis、Nginx）
bash scripts/start.sh

# 3. 初始化数据库
bash scripts/init.sh

# 4. 查看服务状态
docker-compose ps
```

**访问地址：**
- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs
- 管理后台: http://localhost:8000/admin
- WebSocket: ws://localhost:8000/ws

**停止服务：**
```bash
bash scripts/stop.sh
# 或
docker-compose down
```

---

### 方式2：手动启动（开发环境）

适合开发和调试。

#### 步骤1：安装依赖

```bash
# 进入项目目录
cd automation-framework

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装Python依赖
$env:PYTHONUTF8=1
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
 

# 安装Playwright浏览器
python -m playwright install
```

#### 步骤2：配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，配置必要的参数
# 至少需要配置：
# - 数据库连接信息
# - API密钥（如果使用AI功能）
```

**最小配置示例（.env）：**
```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=automation_framework

# API配置
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key-change-this

# 日志配置
LOG_LEVEL=INFO

# 浏览器配置
BROWSER_HEADLESS=false
```

#### 步骤3：启动MySQL数据库

**选项A：使用Docker启动MySQL**
```bash
docker run -d \
  --name automation-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=automation_framework \
  -e MYSQL_USER=automation \
  -e MYSQL_PASSWORD=automation123 \
  -p 3306:3306 \
  mysql:8.0
```

**选项B：使用本地MySQL**
```sql
-- 创建数据库
CREATE DATABASE automation_framework CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'automation'@'localhost' IDENTIFIED BY 'automation123';
GRANT ALL PRIVILEGES ON automation_framework.* TO 'automation'@'localhost';
FLUSH PRIVILEGES;
```

#### 步骤4：初始化数据库

```bash
# 初始化Aerich（数据库迁移工具）
aerich init -t src.models.database.TORTOISE_ORM

# 创建数据库表
aerich init-db

# 如果已经初始化过，使用：
# aerich upgrade
```

#### 步骤5：启动API服务

```bash
# 开发模式（自动重载）
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**访问地址：**
- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs
- 管理后台: http://localhost:8000/admin

---

### 方式3：使用Python直接运行

最简单的方式，适合快速测试。

```bash
# 进入项目目录
cd automation-framework

# 安装依赖
pip install -r requirements.txt

# 直接运行（需要先配置数据库）
python -m uvicorn src.api.main:app --reload
```

---

## 🔧 配置AI模型（可选）

如果需要使用AI功能，需要配置模型API密钥。

### 配置Qwen（通义千问）

```bash
# 在.env文件中添加
QWEN_API_KEY=sk-your-dashscope-api-key
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo
QWEN_VISION_MODEL=qwen-vl-plus
```

**获取API密钥：**
1. 访问 https://dashscope.console.aliyun.com/
2. 注册并登录
3. 创建API密钥

### 配置OpenAI

```bash
# 在.env文件中添加
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4
```

### 配置Anthropic

```bash
# 在.env文件中添加
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-opus-20240229
```

---

## ✅ 验证安装

### 1. 检查API服务

```bash
# 健康检查
curl http://localhost:8000/health

# 预期输出：
# {"status":"healthy"}
```

### 2. 访问API文档

打开浏览器访问：http://localhost:8000/docs

你应该能看到完整的API文档界面（Swagger UI）。

### 3. 访问管理后台

打开浏览器访问：http://localhost:8000/admin

默认账号：`admin` / `admin`

### 4. 运行示例代码

```bash
# 浏览器自动化示例
python examples/browser_example.py

# AI Agent示例（需要配置API密钥）
python examples/ai_agent_example.py

# Qwen模型示例（需要配置Qwen API密钥）
python examples/qwen_example.py
```

---

## 📝 第一个任务

### 使用Python SDK

创建文件 `test_task.py`：

```python
import asyncio
from src.sdk.client import AutomationClient

async def main():
    # 创建客户端
    client = AutomationClient(base_url="http://localhost:8000")
    
    # 创建任务
    task = await client.tasks.create(
        name="测试任务",
        description="访问百度首页并截图",
        actions=[
            {
                "type": "goto",
                "url": "https://www.baidu.com"
            },
            {
                "type": "screenshot",
                "path": "baidu.png"
            }
        ]
    )
    
    print(f"任务已创建: {task['id']}")
    
    # 执行任务
    result = await client.tasks.execute(task['id'])
    print(f"任务执行结果: {result['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```

运行：
```bash
python test_task.py
```

### 使用CLI

```bash
# 初始化配置
python -m src.cli.main config init

# 创建任务
python -m src.cli.main task create "测试任务"

# 列出所有任务
python -m src.cli.main task list

# 执行任务
python -m src.cli.main task execute <task-id>
```

### 使用REST API

```bash
# 创建任务
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试任务",
    "description": "访问百度首页",
    "actions": [
      {"type": "goto", "url": "https://www.baidu.com"},
      {"type": "screenshot", "path": "baidu.png"}
    ]
  }'

# 执行任务（替换{task_id}为实际的任务ID）
curl -X POST http://localhost:8000/api/tasks/{task_id}/execute
```

---

## 🐛 常见问题

### 1. 数据库连接失败

**错误信息：** `Can't connect to MySQL server`

**解决方法：**
- 检查MySQL是否已启动
- 检查.env中的数据库配置是否正确
- 检查数据库用户权限

```bash
# 测试数据库连接
mysql -h localhost -u automation -p automation_framework
```

### 2. Playwright浏览器未安装

**错误信息：** `Executable doesn't exist`

**解决方法：**
```bash
python -m playwright install
```

### 3. 端口被占用

**错误信息：** `Address already in use`

**解决方法：**
```bash
# 查找占用端口的进程
# Windows:
netstat -ano | findstr :8000

# Linux/macOS:
lsof -i :8000

# 杀死进程或更改端口
```

### 4. 依赖安装失败

**错误信息：** `No matching distribution found`

**解决方法：**
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. Docker启动失败

**错误信息：** `Cannot connect to the Docker daemon`

**解决方法：**
- 确保Docker Desktop已启动
- 检查Docker服务状态
- 尝试重启Docker

---

## 📚 下一步

### 学习资源

1. **快速入门**: 查看 `docs/QUICKSTART.md`
2. **API参考**: 查看 `docs/API_REFERENCE.md`
3. **Qwen配置**: 查看 `docs/QWEN_SETUP.md`
4. **管理后台**: 查看 `docs/ADMIN_SETUP.md`
5. **示例代码**: 查看 `examples/` 目录

### 功能探索

- ✅ 创建和执行浏览器自动化任务
- ✅ 使用AI Agent进行自然语言任务
- ✅ 配置定时任务和调度
- ✅ 查看执行历史和统计
- ✅ 配置通知和告警
- ✅ 开发自定义插件

### 生产部署

查看 `DEPLOYMENT.md` 了解生产环境部署指南。

---

## 🆘 获取帮助

- **文档**: 查看 `docs/` 目录
- **示例**: 查看 `examples/` 目录
- **问题**: 查看 `TROUBLESHOOTING.md`

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     用户层                               │
│  Web UI  │  REST API  │  Python SDK  │  CLI             │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   FastAPI接口层                          │
│  路由  │  认证  │  WebSocket  │  管理后台                │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    业务逻辑层                            │
│  任务管理  │  会话管理  │  调度器  │  AI Agent          │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    驱动层                                │
│  浏览器驱动(Playwright)  │  桌面驱动(平台特定)          │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   数据存储层                             │
│  MySQL  │  Redis  │  文件系统                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🎉 启动成功！

如果你看到以下输出，说明项目已成功启动：

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

现在你可以：
1. 访问 http://localhost:8000/docs 查看API文档
2. 访问 http://localhost:8000/admin 使用管理后台
3. 运行示例代码开始自动化任务

祝你使用愉快！🚀
