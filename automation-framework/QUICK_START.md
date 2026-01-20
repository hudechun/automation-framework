# ⚡ 快速启动

最快5分钟启动项目！

## 🎯 选择你的启动方式

### 方式1：Docker一键启动（推荐）⭐

**Windows用户：**
```cmd
cd automation-framework
scripts\start.bat
```

**Linux/macOS用户：**
```bash
cd automation-framework
bash scripts/start.sh
```

等待服务启动后，访问：
- 📖 API文档: http://localhost:8000/docs
- 🎛️ 管理后台: http://localhost:8000/admin (admin/admin)

---

### 方式2：开发模式启动

**Windows用户：**
```cmd
cd automation-framework
scripts\dev.bat
```

**Linux/macOS用户：**
```bash
cd automation-framework

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
python -m playwright install

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库连接

# 启动服务
uvicorn src.api.main:app --reload
```

---

## ✅ 验证安装

打开浏览器访问：http://localhost:8000/docs

如果看到API文档页面，说明启动成功！

---

## 🚀 运行第一个任务

### 方法1：使用API文档界面

1. 访问 http://localhost:8000/docs
2. 找到 `POST /api/tasks` 接口
3. 点击 "Try it out"
4. 输入以下JSON：
```json
{
  "name": "测试任务",
  "description": "访问百度首页",
  "actions": [
    {
      "type": "goto",
      "url": "https://www.baidu.com"
    },
    {
      "type": "screenshot",
      "path": "baidu.png"
    }
  ]
}
```
5. 点击 "Execute"
6. 复制返回的任务ID
7. 找到 `POST /api/tasks/{task_id}/execute` 接口
8. 输入任务ID并执行

### 方法2：使用Python代码

创建文件 `test.py`：
```python
import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # 创建任务
        response = await client.post(
            "http://localhost:8000/api/tasks",
            json={
                "name": "测试任务",
                "description": "访问百度首页",
                "actions": [
                    {"type": "goto", "url": "https://www.baidu.com"},
                    {"type": "screenshot", "path": "baidu.png"}
                ]
            }
        )
        task = response.json()
        print(f"任务已创建: {task['id']}")
        
        # 执行任务
        response = await client.post(
            f"http://localhost:8000/api/tasks/{task['id']}/execute"
        )
        result = response.json()
        print(f"执行结果: {result}")

asyncio.run(main())
```

运行：
```bash
pip install httpx
python test.py
```

### 方法3：使用示例代码

```bash
# 浏览器自动化示例
python examples/browser_example.py

# AI Agent示例（需要配置API密钥）
python examples/ai_agent_example.py
```

---

## 🔧 配置AI功能（可选）

如果要使用AI功能，需要配置API密钥。

### 配置Qwen（推荐，国内访问）

1. 访问 https://dashscope.console.aliyun.com/
2. 注册并创建API密钥
3. 在 `.env` 文件中添加：
```bash
QWEN_API_KEY=sk-your-api-key-here
QWEN_MODEL=qwen-turbo
```

4. 运行Qwen示例：
```bash
python examples/qwen_example.py
```

---

## 📚 详细文档

- 📖 **完整启动指南**: [STARTUP_GUIDE.md](STARTUP_GUIDE.md)
- 🔧 **Qwen配置**: [docs/QWEN_SETUP.md](docs/QWEN_SETUP.md)
- 🎛️ **管理后台**: [docs/ADMIN_SETUP.md](docs/ADMIN_SETUP.md)
- 📝 **API参考**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

---

## ❓ 遇到问题？

### 端口被占用
```bash
# 更改端口（在.env中）
API_PORT=8001
```

### 数据库连接失败
```bash
# 检查MySQL是否启动
docker ps | grep mysql

# 或使用SQLite（开发环境）
# 在.env中设置：
DB_TYPE=sqlite
```

### Playwright浏览器未安装
```bash
python -m playwright install
```

---

## 🎉 启动成功！

现在你可以：
- ✅ 创建自动化任务
- ✅ 使用AI Agent
- ✅ 查看执行历史
- ✅ 配置定时任务

**下一步**: 查看 [examples/](examples/) 目录学习更多用法！
