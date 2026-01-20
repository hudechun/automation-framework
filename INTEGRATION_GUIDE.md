# RuoYi + Automation Framework 集成指南

## 概述

我们已经将Automation Framework与RuoYi-Vue3-FastAPI管理系统集成，使用统一的数据库`ruoyi-fastapi`。

## 数据库架构

### 统一数据库：ruoyi-fastapi

**位置**: 106.53.217.96:3306

#### RuoYi系统表（19个）
- `sys_user` - 用户表
- `sys_role` - 角色表
- `sys_menu` - 菜单权限表
- `sys_dept` - 部门表
- `sys_post` - 岗位表
- `sys_dict_type` - 字典类型表
- `sys_dict_data` - 字典数据表
- `sys_config` - 参数配置表
- `sys_notice` - 通知公告表
- `sys_oper_log` - 操作日志表
- `sys_logininfor` - 登录日志表
- `sys_user_role` - 用户角色关联表
- `sys_role_menu` - 角色菜单关联表
- `sys_role_dept` - 角色部门关联表
- `sys_user_post` - 用户岗位关联表
- `sys_job` - 定时任务表
- `sys_job_log` - 定时任务日志表
- `gen_table` - 代码生成业务表
- `gen_table_column` - 代码生成字段表

#### Automation业务表（5个）
- `tasks` - 自动化任务表
- `sessions` - 浏览器/桌面会话表
- `execution_records` - 任务执行记录表
- `model_configs` - AI模型配置表
- `aerich` - 数据库迁移记录表

## 项目结构

```
.
├── RuoYi-Vue3-FastAPI/          # RuoYi管理系统
│   ├── ruoyi-fastapi-backend/   # 后端API
│   └── ruoyi-fastapi-frontend/  # 前端界面
│
└── automation-framework/         # 自动化框架
    ├── src/                     # 源代码
    ├── examples/                # 示例代码
    └── database/                # 数据库脚本
```

## 配置文件

### RuoYi后端配置
**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/.env.dev`

```env
DB_HOST = '106.53.217.96'
DB_PORT = 3306
DB_USERNAME = 'root'
DB_PASSWORD = 'gyswxgyb7418!'
DB_DATABASE = 'ruoyi-fastapi'

REDIS_HOST = '106.53.217.96'
REDIS_PORT = 6379
```

### Automation Framework配置
**文件**: `automation-framework/.env`

```env
DB_HOST=106.53.217.96
DB_PORT=3306
DB_USER=root
DB_PASSWORD=gyswxgyb7418!
DB_NAME=ruoyi-fastapi

QWEN_API_KEY=sk-e6ca59a7391b49cc8d46af66e4e12c3b
```

## 启动步骤

### 1. 启动RuoYi管理系统

#### 后端
```powershell
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
py -3.10 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python app.py --env=dev
```

访问: http://localhost:9099/dev-api/docs

#### 前端
```powershell
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
npm install --registry=https://registry.npmmirror.com
npm run dev
```

访问: http://localhost:80

**默认账号**:
- 用户名: `admin`
- 密码: `admin123`

### 2. 启动Automation Framework

```powershell
cd automation-framework
.venv\Scripts\activate
python -m uvicorn src.api.main:app --reload
```

访问: http://localhost:8000/docs

## 功能集成

### 使用RuoYi管理Automation数据

1. **代码生成器**
   - 登录RuoYi管理后台
   - 进入"系统工具" -> "代码生成"
   - 导入`tasks`、`sessions`等业务表
   - 一键生成CRUD接口和前端页面

2. **权限控制**
   - 在RuoYi中创建"自动化管理"菜单
   - 为不同角色分配任务管理权限
   - 使用RuoYi的权限系统控制访问

3. **操作日志**
   - 所有操作自动记录到`sys_oper_log`
   - 在RuoYi后台查看操作历史

4. **定时任务**
   - 使用RuoYi的定时任务功能
   - 定时执行自动化任务

## 数据流转

```
用户 -> RuoYi前端 -> RuoYi后端API -> ruoyi-fastapi数据库
                                    ↓
                                  业务表
                                    ↓
Automation Framework <- 读取任务 <- tasks表
```

## API端点

### RuoYi API
- 基础路径: http://localhost:9099/dev-api
- 文档: http://localhost:9099/dev-api/docs
- 用户管理: `/dev-api/system/user`
- 角色管理: `/dev-api/system/role`
- 菜单管理: `/dev-api/system/menu`

### Automation API
- 基础路径: http://localhost:8000
- 文档: http://localhost:8000/docs
- 任务管理: `/api/tasks`
- 会话管理: `/api/sessions`
- 执行记录: `/api/executions`

## 优势

1. **统一管理**: 一个数据库管理所有数据
2. **权限控制**: 使用RuoYi成熟的权限系统
3. **快速开发**: 使用代码生成器快速创建CRUD
4. **完整日志**: 操作日志、登录日志统一记录
5. **企业级**: RuoYi提供企业级的管理功能

## 下一步

1. 使用RuoYi代码生成器为业务表生成管理界面
2. 配置菜单和权限
3. 开发自定义业务逻辑
4. 集成Qwen AI功能到RuoYi界面

## 技术栈

### RuoYi
- 后端: FastAPI + SQLAlchemy + MySQL
- 前端: Vue 3 + Element Plus
- 认证: OAuth2 + JWT

### Automation Framework
- 核心: Playwright + PyAutoGUI
- AI: Qwen (通义千问)
- 数据库: Tortoise ORM + MySQL
