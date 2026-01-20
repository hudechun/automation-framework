# 桌面与浏览器自动化框架

一个强大的、可扩展的自动化框架，支持浏览器和桌面应用程序的自动化操作。

## 特性

- 🌐 **浏览器自动化**: 基于Playwright，支持Chromium、Firefox和WebKit
- 🖥️ **桌面自动化**: 支持Windows、macOS和Linux桌面应用
- 🤖 **AI智能**: 集成GPT-4、Claude和Qwen（通义千问），支持自然语言任务解析
- 📅 **任务调度**: 支持定时任务和周期性任务
- 🔄 **并发执行**: 浏览器任务并发，桌面任务串行
- 💾 **状态持久化**: 会话管理和检查点恢复
- 🔌 **插件系统**: 可扩展的插件架构
- 📊 **可观测性**: 完整的日志、监控和调试支持
- 🔒 **安全性**: 凭证管理、会话隔离和权限控制
- 🌐 **REST API**: 完整的FastAPI接口

## 快速开始

### 🎯 首次使用？

**完整的分步指南**: 查看 [GETTING_STARTED_CHECKLIST.md](GETTING_STARTED_CHECKLIST.md) ⭐

这个检查清单会引导您完成：
1. ✅ 环境准备
2. ✅ 依赖安装
3. ✅ 环境配置
4. ✅ 数据库初始化
5. ✅ 服务启动
6. ✅ 运行示例
7. ✅ 开发使用

### 🚀 已经设置好？一键启动

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

访问：
- 📖 API文档: http://localhost:8000/docs
- 🎛️ 管理后台: http://localhost:8000/admin

### 📚 详细指南

- **⭐ 开始使用检查清单**: [GETTING_STARTED_CHECKLIST.md](GETTING_STARTED_CHECKLIST.md) - 首次使用必读
- **快速启动**: [QUICK_START.md](QUICK_START.md) - 5分钟快速开始
- **完整指南**: [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 详细启动说明
- **依赖管理**: [DEPENDENCIES.md](DEPENDENCIES.md) - 依赖安装和管理
- **安装故障排除**: [INSTALLATION_TROUBLESHOOTING.md](INSTALLATION_TROUBLESHOOTING.md) - 解决安装问题
- **项目状态**: [STATUS_SUMMARY.md](STATUS_SUMMARY.md) - 项目完成状态
- **Qwen配置**: [docs/QWEN_SETUP.md](docs/QWEN_SETUP.md) - Qwen模型配置

## 项目结构

```
automation-framework/
├── src/
│   ├── core/          # 核心抽象层
│   ├── drivers/       # 浏览器和桌面驱动
│   ├── agent/         # AI智能层
│   ├── api/           # FastAPI接口层
│   ├── models/        # 数据模型
│   └── utils/         # 工具函数
├── tests/             # 测试文件
├── plugins/           # 插件目录
├── config/            # 配置文件
└── docs/              # 文档
```

## 安装

### 前置要求

- Python 3.8+
- MySQL 5.7+ 或 8.0+
- 虚拟环境（推荐）

### 安装步骤

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装Playwright浏览器
python -m playwright install

# 5. 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库和API密钥

# 6. 初始化数据库
# Windows
cd database
init_db.bat
# Linux/macOS
cd database
chmod +x init_db.sh
./init_db.sh
```

### 遇到安装问题？

如果遇到依赖安装问题（特别是Windows上的Pillow编译错误），请查看：
- [INSTALLATION_TROUBLESHOOTING.md](INSTALLATION_TROUBLESHOOTING.md) - 详细的故障排除指南
- [DEPENDENCIES.md](DEPENDENCIES.md) - 依赖管理和安装说明

## 文档

### 核心文档
- ⭐ [GETTING_STARTED_CHECKLIST.md](GETTING_STARTED_CHECKLIST.md) - 开始使用检查清单（首次使用必读）
- [README.md](README.md) - 项目主文档（本文件）
- [STATUS_SUMMARY.md](STATUS_SUMMARY.md) - 项目完成状态总结
- [QUICK_START.md](QUICK_START.md) - 5分钟快速开始
- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 详细启动指南

### 安装和配置
- [DEPENDENCIES.md](DEPENDENCIES.md) - 依赖管理指南
- [INSTALLATION_TROUBLESHOOTING.md](INSTALLATION_TROUBLESHOOTING.md) - 安装故障排除
- [DEPENDENCIES_CHECK.md](DEPENDENCIES_CHECK.md) - 依赖检查报告
- [docs/QWEN_SETUP.md](docs/QWEN_SETUP.md) - Qwen模型配置指南
- [docs/ADMIN_SETUP.md](docs/ADMIN_SETUP.md) - 管理后台设置指南

### API和开发
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md) - API参考文档
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - 开发快速开始
- [SDK_README.md](SDK_README.md) - SDK使用指南

### 数据库
- [database/README.md](database/README.md) - 数据库设置和管理

### 项目状态
- [QWEN_INTEGRATION.md](QWEN_INTEGRATION.md) - Qwen集成报告
- [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) - 项目完成报告
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - 实现状态

## 许可证

MIT License
