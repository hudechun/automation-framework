# 依赖检查报告

## ✅ 已添加的遗漏依赖

### 1. 核心依赖补充
- **`starlette==0.27.0`** - FastAPI的底层框架，WebSocket支持
- **`websockets==12.0`** - WebSocket协议实现
- **`aiohttp==3.9.1`** - 异步HTTP客户端（Ollama provider使用）

### 2. 认证和安全补充
- **`passlib[bcrypt]==1.7.4`** - 密码哈希库（管理后台用户密码加密）
- **`python-jose[cryptography]==3.3.0`** - JWT处理（可选，增强JWT功能）

### 3. 文件处理补充
- **`pillow==10.1.0`** - 图像处理库（截图处理、图像操作）

### 4. CLI工具补充
- **`typer==0.9.0`** - 现代CLI框架（可选，增强CLI功能）

### 5. 报告生成补充
- **`openpyxl==3.1.2`** - Excel文件生成（可选，用于导出Excel报告）

### 6. 缓存支持（可选）
- **`redis==5.0.1`** - Redis客户端
- **`aioredis==2.0.1`** - 异步Redis客户端

## 📊 依赖分类

### 必需依赖（核心功能）
```
playwright==1.40.0          # 浏览器自动化
fastapi==0.104.1            # Web框架
uvicorn[standard]==0.24.0   # ASGI服务器
tortoise-orm==0.20.0        # ORM
aiomysql==0.2.0             # MySQL驱动
aerich==0.7.2               # 数据库迁移
apscheduler==3.10.4         # 任务调度
starlette==0.27.0           # FastAPI底层
websockets==12.0            # WebSocket
pydantic==2.5.0             # 数据验证
python-dotenv==1.0.0        # 环境变量
httpx==0.25.2               # HTTP客户端
aiofiles==23.2.1            # 异步文件操作
psutil==5.9.6               # 系统监控
python-json-logger==2.0.7   # 结构化日志
pyjwt==2.8.0                # JWT认证
jinja2==3.1.2               # 模板引擎
python-multipart==0.0.6     # 文件上传
```

### AI功能依赖
```
openai==1.3.0               # OpenAI API
anthropic==0.7.0            # Anthropic API
aiohttp==3.9.1              # Ollama使用
```

### 桌面自动化依赖（平台特定）
```
pywinauto==0.6.8            # Windows
pyobjc-framework-Cocoa==10.0    # macOS
pyobjc-framework-Quartz==10.0   # macOS
python-xlib==0.33           # Linux
pyatspi==2.46.0             # Linux
```

### 安全依赖
```
keyring==24.3.0             # 系统密钥链
cryptography==41.0.7        # 加密
passlib[bcrypt]==1.7.4      # 密码哈希
```

### 管理后台依赖
```
fastapi-admin==1.0.4        # 管理后台框架
```

### 通知系统依赖
```
aiosmtplib==3.0.1           # 邮件发送
```

### CLI工具依赖
```
click==8.1.7                # CLI框架
rich==13.7.0                # 终端美化
typer==0.9.0                # 现代CLI（可选）
```

### 报告生成依赖（可选）
```
reportlab==4.0.7            # PDF生成
openpyxl==3.1.2             # Excel生成
pillow==10.1.0              # 图像处理
```

### 测试依赖
```
pytest==7.4.3               # 测试框架
pytest-asyncio==0.21.1      # 异步测试
pytest-cov==4.1.0           # 覆盖率
```

### 其他工具
```
pyyaml==6.0.1               # YAML解析
```

## 🔍 依赖检查命令

### 检查已安装的包
```bash
pip list
```

### 检查缺失的依赖
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

## 📦 安装指南

### 完整安装（所有功能）
```bash
pip install -r requirements.txt
```

### 最小安装（仅核心功能）
```bash
# 创建最小依赖文件
cat > requirements-minimal.txt << EOF
playwright==1.40.0
fastapi==0.104.1
uvicorn[standard]==0.24.0
tortoise-orm==0.20.0
aiomysql==0.2.0
aerich==0.7.2
apscheduler==3.10.4
starlette==0.27.0
websockets==12.0
pydantic==2.5.0
python-dotenv==1.0.0
httpx==0.25.2
aiofiles==23.2.1
psutil==5.9.6
python-json-logger==2.0.7
pyjwt==2.8.0
jinja2==3.1.2
python-multipart==0.0.6
EOF

pip install -r requirements-minimal.txt
```

### 按功能安装

#### 仅浏览器自动化
```bash
pip install playwright fastapi uvicorn tortoise-orm aiomysql
```

#### 添加AI功能
```bash
pip install openai anthropic aiohttp
```

#### 添加桌面自动化（Windows）
```bash
pip install pywinauto
```

#### 添加管理后台
```bash
pip install fastapi-admin
```

## ⚠️ 平台特定注意事项

### Windows
- `pywinauto` 仅在Windows上可用
- 某些包可能需要Visual C++编译器

### macOS
- `pyobjc-framework-*` 仅在macOS上可用
- 可能需要Xcode命令行工具

### Linux
- `python-xlib` 和 `pyatspi` 仅在Linux上可用
- 可能需要安装系统级依赖：
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-dev libdbus-1-dev
  
  # CentOS/RHEL
  sudo yum install python3-devel dbus-devel
  ```

## 🔧 常见问题

### 1. 安装失败

**问题**: `error: Microsoft Visual C++ 14.0 or greater is required`

**解决**: 
- Windows: 安装 [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- 或使用预编译的wheel: `pip install --only-binary :all: <package>`

### 2. 版本冲突

**问题**: `ERROR: pip's dependency resolver does not currently take into account all the packages that are installed`

**解决**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用新的依赖解析器
pip install --use-feature=2020-resolver -r requirements.txt
```

### 3. 网络问题

**问题**: 下载速度慢或超时

**解决**: 使用国内镜像
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. Playwright浏览器未安装

**问题**: `playwright._impl._api_types.Error: Executable doesn't exist`

**解决**:
```bash
python -m playwright install
```

## 📝 依赖更新建议

### 定期更新
```bash
# 查看过期的包
pip list --outdated

# 更新单个包
pip install --upgrade <package>

# 更新所有包（谨慎使用）
pip install --upgrade -r requirements.txt
```

### 锁定版本
建议使用 `pip freeze` 生成精确版本：
```bash
pip freeze > requirements-lock.txt
```

### 使用 pip-tools
```bash
pip install pip-tools

# 从 requirements.in 生成 requirements.txt
pip-compile requirements.in

# 同步环境
pip-sync requirements.txt
```

## 🎯 推荐的安装流程

### 1. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

### 2. 升级pip
```bash
python -m pip install --upgrade pip
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 安装Playwright浏览器
```bash
python -m playwright install
```

### 5. 验证安装
```bash
python -c "import fastapi; import playwright; print('✅ 安装成功')"
```

## 📚 相关文档

- [pip文档](https://pip.pypa.io/)
- [虚拟环境指南](https://docs.python.org/3/tutorial/venv.html)
- [requirements.txt格式](https://pip.pypa.io/en/stable/reference/requirements-file-format/)

---

**最后更新**: 2026-01-19
**检查状态**: ✅ 所有依赖已验证
