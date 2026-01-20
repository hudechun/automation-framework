autoflow-platform 自动化平台

企业级浏览器自动化平台，集成 RuoYi-Vue3-FastAPI 后台管理系统和 Automation Framework 自动化框架。

## 项目结构

```
autoflow-platform /
├── RuoYi-Vue3-FastAPI/          # 后台管理系统
│   ├── ruoyi-fastapi-backend/   # FastAPI 后端
│   │   ├── module_automation/   # 自动化模块
│   │   ├── module_admin/        # 系统管理模块
│   │   └── ...
│   └── ruoyi-fastapi-frontend/  # Vue3 前端
│       └── src/
│           └── views/automation/ # 自动化管理页面
├── automation-framework/         # 自动化框架核心
│   ├── src/                     # 源代码
│   ├── database/                # 数据库脚本
│   └── docs/                    # 文档
└── config/                      # 全局配置
```

## 核心功能

### 1. 任务管理
- 创建和管理自动化任务
- 支持浏览器自动化、桌面自动化
- 定时任务调度
- 任务执行监控

### 2. 会话管理
- 浏览器会话管理
- 会话状态跟踪
- 会话录制和回放

### 3. 执行记录
- 任务执行历史
- 执行日志查看
- 错误追踪和分析

### 4. 模型配置
- AI 模型配置管理
- 支持多种 LLM 模型
- 模型参数调优

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd TuriX-CUA-main
```

2. **启动服务**
```bash
# Windows
start_unified.bat

# Linux/Mac
./start_unified.sh
```

3. **访问系统**
- 前端界面: http://localhost:5173
- 后端API: http://localhost:9099/dev-api
- API文档: http://localhost:9099/dev-api/docs

### 默认账号

- 用户名: `admin`
- 密码: `admin123`

## 配置说明

### 后端配置

复制环境配置文件：
```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
cp .env.example .env.dev
```

编辑 `.env.dev` 配置数据库和 Redis 连接信息。

### 前端配置

前端配置文件位于：
```
RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/vite.config.js
```

### 自动化框架配置

复制配置文件：
```bash
cd automation-framework
cp .env.example .env
```

## 数据库初始化

1. **创建数据库**
```sql
CREATE DATABASE ruoyi_vue3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **导入表结构**
```bash
cd RuoYi-Vue3-FastAPI
mysql -u root -p ruoyi_vue3 < add_automation_tables.sql
```

3. **导入菜单和字典数据**
```bash
mysql -u root -p ruoyi_vue3 < add_automation_menus.sql
mysql -u root -p ruoyi_vue3 < add_automation_dicts.sql
```

## 开发指南

### 后端开发

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
python app.py --env=dev
```

### 前端开发

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
npm install
npm run dev
```

### 自动化框架开发

```bash
cd automation-framework
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
python -m src.api.main
```

## 技术栈

### 后端
- FastAPI - 现代化 Python Web 框架
- SQLAlchemy - ORM 框架
- MySQL - 关系型数据库
- Redis - 缓存和消息队列
- Playwright - 浏览器自动化

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- Element Plus - UI 组件库
- Vite - 前端构建工具
- Pinia - 状态管理

### 自动化框架
- Playwright - 浏览器自动化
- PyAutoGUI - 桌面自动化
- OpenAI API - AI 能力集成

## 文档

- [快速开始](RuoYi-Vue3-FastAPI/QUICK_START.md)
- [集成指南](INTEGRATION_GUIDE.md)
- [统一架构](UNIFIED_ARCHITECTURE.md)
- [代码生成指南](CODE_GENERATION_GUIDE.md)
- [自动化框架文档](automation-framework/README.md)

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
