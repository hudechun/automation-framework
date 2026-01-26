# 重启后端服务 - 简单指南

## 问题已修复 ✅

导入错误已修复：
- ❌ `from module_admin.entity.do.base_do import Base`
- ✅ `from config.database import Base`

- ❌ `from utils.sqlalchemy_util import SqlalchemyUtil`
- ✅ `from utils.common_util import SqlalchemyUtil`

## 现在需要重启后端

### Windows系统

#### 方法1: 使用命令行

1. **找到正在运行的Python进程**
   ```cmd
   tasklist | findstr python
   ```

2. **停止Python进程**
   ```cmd
   taskkill /F /IM python.exe
   ```
   或者在运行后端的命令行窗口按 `Ctrl+C`

3. **重新启动后端**
   ```cmd
   cd RuoYi-Vue3-FastAPI\ruoyi-fastapi-backend
   python app.py
   ```

#### 方法2: 使用任务管理器

1. 按 `Ctrl+Shift+Esc` 打开任务管理器
2. 找到 `python.exe` 进程
3. 右键 -> 结束任务
4. 重新运行 `python app.py`

### Linux/Mac系统

```bash
# 停止后端（在运行的终端按 Ctrl+C）
# 或者
pkill -f "python app.py"

# 重新启动
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

## 验证后端启动成功

### 1. 查看启动日志

应该看到类似的输出：
```
INFO: ⏰️ RuoYi-FastAPI开始启动
INFO: 🚀 RuoYi-FastAPI启动成功
INFO: Uvicorn running on http://0.0.0.0:9099
```

### 2. 访问API文档

打开浏览器访问: **http://localhost:9099/docs**

搜索 "ai-model"，应该能看到11个API接口。

### 3. 测试一个API

在API文档中测试 `GET /thesis/ai-model/list`

如果返回401（未授权），说明API存在，只是需要登录。  
如果返回404，说明后端还没有重启。

## 前端操作

### 1. 清除浏览器缓存

- 按 `Ctrl+Shift+Delete`
- 选择"清除缓存"
- 点击"清除数据"

### 2. 强制刷新

- 按 `Ctrl+F5`
- 或者 `Ctrl+Shift+R`

### 3. 重新登录

- 访问 http://localhost
- 登录系统
- 进入 "AI论文写作" -> "AI模型配置"

## 完整流程

```bash
# 1. 停止后端
Ctrl+C

# 2. 重新启动后端
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py

# 3. 等待启动完成（看到 "启动成功"）

# 4. 访问API文档验证
# 浏览器打开: http://localhost:9099/docs

# 5. 清除前端缓存
# 浏览器按 Ctrl+Shift+Delete

# 6. 访问前端
# 浏览器打开: http://localhost/thesis/ai-model
```

## 常见问题

### Q: 端口被占用

**错误**: `Address already in use`

**解决**:
```cmd
# Windows
netstat -ano | findstr :9099
taskkill /F /PID <进程ID>

# Linux/Mac
lsof -i :9099
kill -9 <进程ID>
```

### Q: 模块导入错误

**错误**: `ModuleNotFoundError`

**解决**: 确保在正确的目录启动
```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

### Q: 数据库连接失败

**错误**: `Can't connect to MySQL server`

**解决**: 确保MySQL服务正在运行
```cmd
# Windows
net start MySQL

# Linux
sudo systemctl start mysql
```

---

**重要**: 修复了导入错误后，**必须重启后端**才能生效！
