# 统一架构说明

## 架构变更

我们已将Automation Framework集成到RuoYi后端中，实现**单端口部署**。

### 之前的架构（多端口）
```
RuoYi后端      → 端口 9099
Automation     → 端口 8000  ❌ 独立端口
前端           → 端口 80
```

### 现在的架构（统一端口）✅
```
统一后端       → 端口 9099
├── RuoYi API         (/dev-api/*)
└── Automation API    (/automation/api/*)

前端           → 端口 80
```

## 优势

### 1. 简化部署
- ✅ 只需启动一个后端服务
- ✅ 减少端口管理复杂度
- ✅ 统一的进程管理

### 2. 统一管理
- ✅ 共享数据库连接池
- ✅ 统一的日志系统
- ✅ 统一的配置管理
- ✅ 统一的认证系统

### 3. 更好的集成
- ✅ 在同一个API文档中查看所有接口
- ✅ 前端可以统一调用后端API
- ✅ 避免跨域问题

### 4. 资源优化
- ✅ 共享内存和连接
- ✅ 减少系统资源占用

## API路径映射

### RuoYi系统API
- 基础路径: `/dev-api`
- 用户管理: `/dev-api/system/user`
- 角色管理: `/dev-api/system/role`
- 菜单管理: `/dev-api/system/menu`
- 等等...

### Automation Framework API
- 基础路径: `/automation/api`
- 任务管理: `/automation/api/tasks`
- 会话管理: `/automation/api/sessions`
- 执行记录: `/automation/api/executions`
- 配置管理: `/automation/api/configs`
- 监控: `/automation/api/monitor`
- WebSocket: `/automation/ws`

## 启动方式

### 方式1: 使用统一启动脚本（推荐）
```powershell
start_unified.bat
```

这会启动：
1. 统一后端服务（包含RuoYi + Automation）- 端口9099
2. 前端服务 - 端口80

### 方式2: 手动启动

#### 启动后端
```powershell
cd RuoYi-Vue3-FastAPI\ruoyi-fastapi-backend
.venv\Scripts\activate
python app.py --env=dev
```

#### 启动前端
```powershell
cd RuoYi-Vue3-FastAPI\ruoyi-fastapi-frontend
npm run dev
```

## 访问地址

### 主要访问地址
- **前端界面**: http://localhost:80
- **API文档**: http://localhost:9099/dev-api/docs

### API端点示例

#### RuoYi API
```bash
# 登录
POST http://localhost:9099/dev-api/login

# 获取用户列表
GET http://localhost:9099/dev-api/system/user/list
```

#### Automation API
```bash
# 获取任务列表
GET http://localhost:9099/automation/api/tasks

# 创建任务
POST http://localhost:9099/automation/api/tasks

# 执行任务
POST http://localhost:9099/automation/api/tasks/{task_id}/execute

# WebSocket连接
ws://localhost:9099/automation/ws
```

## 配置说明

### 后端配置
**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/.env.dev`

```env
# 应用配置
APP_HOST = '0.0.0.0'
APP_PORT = 9099

# 数据库配置（共享）
DB_HOST = '106.53.217.96'
DB_DATABASE = 'ruoyi-fastapi'

# Redis配置（共享）
REDIS_HOST = '106.53.217.96'
```

### 前端配置
**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/.env.development`

前端会自动代理所有API请求到后端9099端口。

## 数据库

两个系统共享同一个数据库：`ruoyi-fastapi`

### 表结构
- **RuoYi系统表**: sys_*, gen_* (19个表)
- **Automation业务表**: tasks, sessions, execution_records, model_configs (5个表)

## 技术实现

### 挂载方式
Automation Framework作为子路由挂载到RuoYi的FastAPI应用中：

```python
# 在 server.py 中
from mount_automation import mount_automation_app

def create_app():
    app = FastAPI(...)
    
    # 挂载Automation Framework
    mount_automation_app(app)
    
    return app
```

### 路由注册
```python
# 在 mount_automation.py 中
app.include_router(tasks.router, prefix="/automation/api/tasks")
app.include_router(sessions.router, prefix="/automation/api/sessions")
# ...
```

## 迁移指南

如果你之前使用的是分离的两个服务，迁移步骤：

1. **停止旧服务**
   ```powershell
   stop_all.bat
   ```

2. **使用新的启动脚本**
   ```powershell
   start_unified.bat
   ```

3. **更新前端API调用**（如果有自定义代码）
   - 旧: `http://localhost:8000/api/tasks`
   - 新: `http://localhost:9099/automation/api/tasks`

## 故障排查

### 问题1: Automation功能不可用
**检查**: 查看后端启动日志，确认是否有"Automation Framework已成功挂载"的消息

**解决**: 
```powershell
cd RuoYi-Vue3-FastAPI\ruoyi-fastapi-backend
.venv\Scripts\activate
pip install -r ..\..\automation-framework\requirements.txt
```

### 问题2: 路径404
**检查**: 确认使用正确的路径前缀
- RuoYi: `/dev-api/*`
- Automation: `/automation/api/*`

### 问题3: 依赖冲突
**解决**: 两个项目的依赖都需要安装到同一个虚拟环境中

## 性能优势

### 资源使用对比

#### 之前（分离部署）
- Python进程: 2个
- 内存占用: ~400MB
- 数据库连接: 2个连接池

#### 现在（统一部署）
- Python进程: 1个
- 内存占用: ~250MB
- 数据库连接: 1个连接池（共享）

节省约40%的资源！

## 总结

统一架构带来的好处：
- ✅ 更简单的部署和管理
- ✅ 更少的资源占用
- ✅ 更好的系统集成
- ✅ 统一的API文档
- ✅ 避免端口冲突

推荐所有新部署都使用统一架构！
