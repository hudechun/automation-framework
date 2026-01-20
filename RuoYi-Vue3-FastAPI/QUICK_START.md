# RuoYi-Vue3-FastAPI 快速启动指南

## 环境要求

- Python 3.10
- Node.js ≥ 18
- MySQL ≥ 5.7
- Redis

## 后端部署步骤

### 1. 安装依赖

在项目根目录运行：

```powershell
cd RuoYi-Vue3-FastAPI
setup_ruoyi.bat
```

或手动安装：

```powershell
cd ruoyi-fastapi-backend
py -3.10 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 初始化数据库

在项目根目录运行（确保虚拟环境已激活）：

```powershell
python init_database.py
```

### 3. 启动后端服务

```powershell
cd ruoyi-fastapi-backend
.venv\Scripts\activate
python app.py --env=dev
```

后端将运行在: http://localhost:9099

API文档: http://localhost:9099/dev-api/docs

### 4. 默认账号

- 用户名: `admin`
- 密码: `admin123`

## 前端部署步骤

### 1. 安装依赖

```powershell
cd ruoyi-fastapi-frontend
npm install --registry=https://registry.npmmirror.com
```

### 2. 启动前端服务

```powershell
npm run dev
```

前端将运行在: http://localhost:80

## 访问系统

打开浏览器访问: http://localhost:80

使用默认账号登录：
- 用户名: admin
- 密码: admin123

## 配置说明

### 后端配置

配置文件: `ruoyi-fastapi-backend/.env.dev`

已配置的数据库和Redis：
- 数据库: 106.53.217.96:3306
- Redis: 106.53.217.96:6379
- 数据库名: ruoyi-fastapi

### 前端配置

配置文件: `ruoyi-fastapi-frontend/.env.development`

后端API地址已配置为: http://localhost:9099/dev-api

## 功能特性

- ✅ 用户管理
- ✅ 角色管理
- ✅ 菜单管理
- ✅ 部门管理
- ✅ 岗位管理
- ✅ 字典管理
- ✅ 参数管理
- ✅ 通知公告
- ✅ 操作日志
- ✅ 登录日志
- ✅ 在线用户
- ✅ 定时任务
- ✅ 服务监控
- ✅ 缓存监控
- ✅ 在线构建器
- ✅ 系统接口
- ✅ 代码生成

## 常见问题

### 1. 数据库连接失败

检查 `.env.dev` 文件中的数据库配置是否正确。

### 2. Redis连接失败

确保Redis服务正在运行，或在 `.env.dev` 中配置正确的Redis地址。

### 3. 前端无法连接后端

检查前端配置文件中的API地址是否正确。

## 技术栈

### 后端
- FastAPI
- SQLAlchemy
- MySQL
- Redis
- OAuth2 & JWT

### 前端
- Vue 3
- Element Plus
- Vite
- Pinia

## 更多信息

查看项目README: [README.md](README.md)
