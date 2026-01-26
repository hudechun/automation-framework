# 论文模块依赖安装指南

## Python 依赖（后端）

### 1. 核心依赖（已在 requirements.txt 中）

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
pip install -r requirements.txt
```

当前 requirements.txt 包含：
- FastAPI 及相关组件
- SQLAlchemy（数据库ORM）
- Redis（缓存）
- 其他基础依赖

### 2. AI生成功能依赖（新增）

```bash
# AI模型调用
pip install openai>=1.0.0
pip install anthropic>=0.18.0
pip install aiohttp>=3.9.0
```

或者已经更新到 requirements.txt 中，直接：
```bash
pip install -r requirements.txt
```

### 3. Word文档导出依赖（可选）

如果需要Word导出功能：

```bash
# Python-docx（备选方案，如果不使用Node.js）
pip install python-docx>=0.8.11

# 或者使用 docx2pdf（PDF转换）
pip install docx2pdf
```

### 4. 支付网关依赖（可选）

如果使用Ping++聚合支付：
```bash
pip install pingpp>=2.2.5
```

如果直接对接支付宝/微信：
```bash
pip install alipay-sdk-python>=3.3.0
pip install wechatpy>=1.8.18
```

## Node.js 依赖（Word导出）

### 1. 安装 Node.js

确保已安装 Node.js（建议 v16+）：
```bash
node --version
npm --version
```

如果未安装，访问 https://nodejs.org/ 下载安装。

### 2. 安装 docx 库

**方式一：全局安装（推荐用于服务器）**
```bash
npm install -g docx
```

**方式二：项目本地安装**
```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
npm init -y  # 如果没有 package.json
npm install docx
```

### 3. 其他文档处理工具（可选）

如果需要更多文档处理功能：

```bash
# Pandoc（文档格式转换）
# Windows: 下载安装包 https://pandoc.org/installing.html
# Linux:
sudo apt-get install pandoc

# LibreOffice（PDF转换）
# Windows: 下载安装包 https://www.libreoffice.org/
# Linux:
sudo apt-get install libreoffice

# Poppler（PDF处理）
# Windows: 下载 https://github.com/oschwartz10612/poppler-windows/releases/
# Linux:
sudo apt-get install poppler-utils
```

## 数据库依赖

### MySQL（主数据库）

确保 MySQL 8.0+ 已安装并运行：
```bash
mysql --version
```

### Redis（缓存）

确保 Redis 已安装并运行：
```bash
redis-cli --version
redis-cli ping  # 应返回 PONG
```

如果未安装：
```bash
# Windows: 下载 https://github.com/tporadowski/redis/releases
# Linux:
sudo apt-get install redis-server
```

## 完整安装脚本

### Windows 环境

创建 `install_thesis_deps.bat`:

```batch
@echo off
echo ========================================
echo 论文模块依赖安装脚本
echo ========================================

echo.
echo [1/4] 安装 Python 依赖...
cd RuoYi-Vue3-FastAPI\ruoyi-fastapi-backend
pip install -r requirements.txt
pip install openai anthropic aiohttp

echo.
echo [2/4] 检查 Node.js...
node --version
if %errorlevel% neq 0 (
    echo 错误: Node.js 未安装，请先安装 Node.js
    pause
    exit /b 1
)

echo.
echo [3/4] 安装 docx 库...
npm install -g docx

echo.
echo [4/4] 检查 Redis...
redis-cli ping
if %errorlevel% neq 0 (
    echo 警告: Redis 未运行，请启动 Redis 服务
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
pause
```

### Linux/Mac 环境

创建 `install_thesis_deps.sh`:

```bash
#!/bin/bash

echo "========================================"
echo "论文模块依赖安装脚本"
echo "========================================"

echo ""
echo "[1/4] 安装 Python 依赖..."
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
pip install -r requirements.txt
pip install openai anthropic aiohttp

echo ""
echo "[2/4] 检查 Node.js..."
if ! command -v node &> /dev/null; then
    echo "错误: Node.js 未安装"
    echo "请访问 https://nodejs.org/ 安装 Node.js"
    exit 1
fi
node --version

echo ""
echo "[3/4] 安装 docx 库..."
npm install -g docx

echo ""
echo "[4/4] 检查 Redis..."
if ! redis-cli ping &> /dev/null; then
    echo "警告: Redis 未运行，请启动 Redis 服务"
fi

echo ""
echo "========================================"
echo "安装完成！"
echo "========================================"
```

## 依赖检查脚本

创建 `check_thesis_deps.py`:

```python
"""
检查论文模块依赖是否已安装
"""
import sys
import subprocess

def check_python_package(package_name):
    """检查Python包是否已安装"""
    try:
        __import__(package_name)
        print(f"✓ {package_name} 已安装")
        return True
    except ImportError:
        print(f"✗ {package_name} 未安装")
        return False

def check_command(command, name):
    """检查命令是否可用"""
    try:
        result = subprocess.run(
            [command, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✓ {name} 已安装: {version}")
            return True
        else:
            print(f"✗ {name} 未安装")
            return False
    except Exception as e:
        print(f"✗ {name} 未安装或不可用")
        return False

def check_redis():
    """检查Redis是否运行"""
    try:
        result = subprocess.run(
            ['redis-cli', 'ping'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and 'PONG' in result.stdout:
            print(f"✓ Redis 正在运行")
            return True
        else:
            print(f"✗ Redis 未运行")
            return False
    except Exception:
        print(f"✗ Redis 未安装或未运行")
        return False

def main():
    print("=" * 50)
    print("论文模块依赖检查")
    print("=" * 50)
    
    all_ok = True
    
    print("\n[Python 依赖]")
    packages = [
        'fastapi',
        'sqlalchemy',
        'redis',
        'openai',
        'anthropic',
        'aiohttp'
    ]
    for package in packages:
        if not check_python_package(package):
            all_ok = False
    
    print("\n[Node.js 依赖]")
    if not check_command('node', 'Node.js'):
        all_ok = False
    if not check_command('npm', 'npm'):
        all_ok = False
    
    # 检查 docx 是否全局安装
    try:
        result = subprocess.run(
            ['npm', 'list', '-g', 'docx'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'docx@' in result.stdout:
            print(f"✓ docx 已全局安装")
        else:
            print(f"✗ docx 未全局安装")
            all_ok = False
    except Exception:
        print(f"✗ 无法检查 docx 安装状态")
        all_ok = False
    
    print("\n[数据库服务]")
    if not check_command('mysql', 'MySQL'):
        all_ok = False
    if not check_redis():
        all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✓ 所有依赖已正确安装")
    else:
        print("✗ 部分依赖缺失，请安装缺失的依赖")
        sys.exit(1)
    print("=" * 50)

if __name__ == '__main__':
    main()
```

运行检查：
```bash
python check_thesis_deps.py
```

## 依赖版本要求

| 依赖 | 最低版本 | 推荐版本 | 说明 |
|------|---------|---------|------|
| Python | 3.9+ | 3.11+ | 后端运行环境 |
| FastAPI | 0.100+ | 0.125.0 | Web框架 |
| SQLAlchemy | 2.0+ | 2.0.45 | ORM |
| Redis | 6.0+ | 7.0+ | 缓存服务 |
| MySQL | 8.0+ | 8.0+ | 数据库 |
| Node.js | 16+ | 18+ | Word导出 |
| docx | 7.0+ | 最新 | Word文档生成 |
| openai | 1.0+ | 最新 | OpenAI API |
| anthropic | 0.18+ | 最新 | Anthropic API |

## 可选依赖

### 1. 文档处理增强

```bash
# Python-docx（备选Word处理）
pip install python-docx

# Markdown处理
pip install markdown
pip install markdown2

# PDF生成
pip install reportlab
pip install weasyprint
```

### 2. 图片处理

```bash
# Pillow（图片处理）
pip install Pillow

# 二维码生成
pip install qrcode
```

### 3. 数据导出

```bash
# Excel导出
pip install openpyxl  # 已在 requirements.txt

# CSV处理
# 内置，无需安装
```

### 4. 性能优化

```bash
# 异步HTTP客户端
pip install httpx

# 缓存加速
pip install aiocache

# 任务队列
pip install celery
pip install redis  # Celery broker
```

## 安装顺序建议

1. **基础环境**
   - Python 3.11+
   - Node.js 18+
   - MySQL 8.0+
   - Redis 7.0+

2. **Python 依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **AI 依赖**
   ```bash
   pip install openai anthropic aiohttp
   ```

4. **Node.js 依赖**
   ```bash
   npm install -g docx
   ```

5. **验证安装**
   ```bash
   python check_thesis_deps.py
   ```

## 常见问题

### Q1: pip 安装速度慢
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: npm 安装速度慢
```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com
npm install -g docx
```

### Q3: Redis 连接失败
```bash
# Windows: 启动 Redis
redis-server

# Linux: 启动 Redis 服务
sudo systemctl start redis
```

### Q4: MySQL 连接失败
检查 `.env.dev` 中的数据库配置：
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_DATABASE=ry-vue
```

### Q5: Node.js 版本过低
```bash
# 使用 nvm 升级
nvm install 18
nvm use 18
```

## 生产环境建议

### Docker 部署

创建 `Dockerfile.thesis`:
```dockerfile
FROM python:3.11-slim

# 安装 Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install openai anthropic aiohttp

# 安装 Node.js 依赖
RUN npm install -g docx

# 复制应用代码
COPY . /app
WORKDIR /app

CMD ["python", "server.py"]
```

### 虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 总结

**必需依赖：**
- ✅ Python 3.11+
- ✅ FastAPI + SQLAlchemy + Redis（已在 requirements.txt）
- ✅ MySQL 8.0+
- ✅ Redis 7.0+

**AI功能依赖：**
- ✅ openai
- ✅ anthropic
- ✅ aiohttp

**Word导出依赖：**
- ✅ Node.js 18+
- ✅ docx (npm)

**可选依赖：**
- ⭕ python-docx（备选Word处理）
- ⭕ Pandoc（文档转换）
- ⭕ LibreOffice（PDF转换）
- ⭕ 支付SDK（Ping++/支付宝/微信）

运行 `python check_thesis_deps.py` 检查所有依赖是否已正确安装。
