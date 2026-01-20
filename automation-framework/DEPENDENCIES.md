# 依赖管理指南

## 当前状态

✅ **所有核心依赖已配置完成**  
⚠️ **Pillow在Windows上需要特殊处理**

## 快速安装

### 方式1：完整安装（推荐）

```bash
cd automation-framework
pip install -r requirements.txt
```

**注意**: Pillow已标记为可选依赖（已注释），如果需要图像处理功能，请参考下方的Pillow安装指南。

### 方式2：最小化安装（仅核心功能）

```bash
cd automation-framework
pip install -r requirements-minimal.txt
```

### 方式3：使用国内镜像（推荐中国用户）

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## Pillow安装指南（Windows）

Pillow在Windows上可能遇到编译错误。以下是解决方案：

### 方案1：使用预编译的wheel（推荐）

```bash
pip install pillow
```

大多数情况下，pip会自动下载预编译的wheel文件，无需编译。

### 方案2：从Christoph Gohlke的网站下载

如果方案1失败，访问：https://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow

1. 下载对应Python版本和系统架构的wheel文件
2. 安装：`pip install Pillow‑10.1.0‑cp311‑cp311‑win_amd64.whl`

### 方案3：安装Visual C++ Build Tools

如果需要从源码编译：

1. 下载并安装 [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. 重新运行：`pip install pillow==10.1.0`

### 方案4：跳过Pillow（如果不需要图像处理）

如果您不需要以下功能，可以跳过Pillow安装：
- 截图处理和优化
- 图像格式转换
- 图像缩放和裁剪

## 依赖分类

### 核心依赖（必需）

| 包名 | 版本 | 用途 |
|------|------|------|
| playwright | 1.40.0 | 浏览器自动化核心 |
| fastapi | 0.104.1 | Web API框架 |
| uvicorn | 0.24.0 | ASGI服务器 |
| tortoise-orm | 0.20.0 | 异步ORM |
| aiomysql | 0.2.0 | MySQL异步驱动 |
| aerich | 0.7.2 | 数据库迁移工具 |
| apscheduler | 3.10.4 | 任务调度 |
| starlette | 0.27.0 | FastAPI底层框架 |
| websockets | 12.0 | WebSocket支持 |
| pydantic | 2.5.0 | 数据验证 |
| python-dotenv | 1.0.0 | 环境变量管理 |
| httpx | 0.25.2 | HTTP客户端 |
| aiofiles | 23.2.1 | 异步文件操作 |
| psutil | 5.9.6 | 系统监控 |
| python-json-logger | 2.0.7 | 结构化日志 |
| pyjwt | 2.8.0 | JWT认证 |
| jinja2 | 3.1.2 | 模板引擎 |
| python-multipart | 0.0.6 | 文件上传支持 |

### AI功能依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| openai | 1.3.0 | OpenAI API客户端 |
| anthropic | 0.7.0 | Anthropic Claude API |
| aiohttp | 3.9.1 | Ollama本地模型支持 |

### 桌面自动化依赖（平台特定）

| 包名 | 版本 | 平台 | 用途 |
|------|------|------|------|
| pywinauto | 0.6.8 | Windows | Windows桌面自动化 |
| pyobjc-framework-Cocoa | 10.0 | macOS | macOS桌面自动化 |
| pyobjc-framework-Quartz | 10.0 | macOS | macOS屏幕捕获 |
| python-xlib | 0.33 | Linux | Linux X11支持 |
| pyatspi | 2.46.0 | Linux | Linux辅助功能 |

### 安全依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| keyring | 24.3.0 | 系统密钥链集成 |
| cryptography | 41.0.7 | 加密功能 |
| passlib[bcrypt] | 1.7.4 | 密码哈希 |
| python-jose[cryptography] | 3.3.0 | JWT增强功能（可选） |

### 管理后台依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi-admin | 1.0.4 | Web管理界面框架 |

### 通知系统依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| aiosmtplib | 3.0.1 | 异步邮件发送 |

### CLI工具依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| click | 8.1.7 | CLI框架 |
| rich | 13.7.0 | 终端美化输出 |
| typer | 0.9.0 | 现代CLI框架（可选） |

### 报告生成依赖（可选）

| 包名 | 版本 | 用途 |
|------|------|------|
| reportlab | 4.0.7 | PDF报告生成 |
| openpyxl | 3.1.2 | Excel报告生成 |
| pillow | 10.1.0 | 图像处理（已注释） |

### 测试依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| pytest | 7.4.3 | 测试框架 |
| pytest-asyncio | 0.21.1 | 异步测试支持 |
| pytest-cov | 4.1.0 | 代码覆盖率 |

### 缓存支持（可选）

| 包名 | 版本 | 用途 |
|------|------|------|
| redis | 5.0.1 | Redis客户端 |
| aioredis | 2.0.1 | 异步Redis客户端 |

## 安装后步骤

### 1. 安装Playwright浏览器

```bash
python -m playwright install
```

### 2. 验证安装

```bash
python -c "import fastapi; import playwright; print('✅ 核心依赖安装成功')"
```

### 3. 初始化数据库

```bash
# Windows
cd automation-framework\database
init_db.bat

# Linux/macOS
cd automation-framework/database
chmod +x init_db.sh
./init_db.sh
```

## 常见问题

### Q1: 安装时提示需要Visual C++编译器

**A**: 这通常是因为某些包需要从源码编译。解决方案：
1. 安装 [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. 或使用预编译的wheel：`pip install --only-binary :all: <package>`

### Q2: pip安装速度很慢

**A**: 使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 提示某个包版本冲突

**A**: 升级pip并使用新的依赖解析器：
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Q4: Playwright提示浏览器未安装

**A**: 运行浏览器安装命令：
```bash
python -m playwright install
```

### Q5: 在Linux上安装失败

**A**: 可能需要安装系统级依赖：
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libdbus-1-dev

# CentOS/RHEL
sudo yum install python3-devel dbus-devel
```

## 依赖检查命令

### 查看已安装的包
```bash
pip list
```

### 检查依赖完整性
```bash
pip check
```

### 查看依赖树
```bash
pip install pipdeptree
pipdeptree
```

### 检查过期的包
```bash
pip list --outdated
```

## 更新依赖

### 更新单个包
```bash
pip install --upgrade <package>
```

### 更新所有包（谨慎使用）
```bash
pip install --upgrade -r requirements.txt
```

### 生成锁定版本
```bash
pip freeze > requirements-lock.txt
```

## 虚拟环境管理

### 创建虚拟环境
```bash
python -m venv .venv
```

### 激活虚拟环境
```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 停用虚拟环境
```bash
deactivate
```

## 相关文档

- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 项目启动指南
- [QUICK_START.md](QUICK_START.md) - 快速开始
- [DEPENDENCIES_CHECK.md](DEPENDENCIES_CHECK.md) - 详细依赖检查报告
- [database/README.md](database/README.md) - 数据库设置指南

---

**最后更新**: 2026-01-19  
**状态**: ✅ 所有依赖已配置完成
