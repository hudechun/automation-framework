# Redis持久化配置指南

## Redis安装位置

✅ **已找到Redis安装路径**：`D:\Program Files\Redis\`

## 当前状态

- Redis服务：正在运行
- 进程ID：5668
- 端口：6379
- 运行模式：Windows服务

## 配置步骤

### 方法1：停止服务并使用自定义配置（推荐）

这样可以启用持久化功能，后端重启后Token不会丢失。

**步骤**：

1. **双击运行启动脚本**
   ```
   start_redis_persistent.bat
   ```

2. **脚本会自动**：
   - 检测Redis服务是否运行
   - 询问是否停止服务
   - 使用redis.conf配置启动Redis
   - 启用RDB和AOF持久化

3. **验证持久化**
   ```bash
   # 连接Redis
   redis-cli
   
   # 设置测试数据
   SET test_persist "hello"
   
   # 查看持久化文件
   dir dump.rdb
   dir appendonly.aof
   ```

### 方法2：修改Redis服务配置（永久生效）

如果希望Redis服务也使用持久化配置：

**步骤**：

1. **停止Redis服务**
   ```bash
   net stop Redis
   ```

2. **备份原配置**
   ```bash
   copy "D:\Program Files\Redis\redis.windows.conf" "D:\Program Files\Redis\redis.windows.conf.bak"
   ```

3. **复制新配置**
   ```bash
   copy redis.conf "D:\Program Files\Redis\redis.windows.conf"
   ```

4. **修改服务配置**
   - 打开服务管理器（services.msc）
   - 找到Redis服务
   - 右键 → 属性
   - 修改"可执行文件的路径"为：
     ```
     "D:\Program Files\Redis\redis-server.exe" "D:\Program Files\Redis\redis.windows.conf"
     ```

5. **启动服务**
   ```bash
   net start Redis
   ```

### 方法3：仅延长Token时间（最简单）

如果不想修改Redis配置，只延长Token有效期：

**已完成**：
- ✅ Token有效期：7天
- ✅ Redis中Token过期时间：7天
- ✅ 前端自动处理Token失效

**效果**：
- 7天内无需重新登录
- 后端重启后需要重新登录（但有友好提示）

## 推荐方案

### 开发环境（当前）

**推荐：方法3（仅延长Token时间）**

**理由**：
- 最简单，无需修改Redis配置
- 7天有效期足够开发使用
- 前端已有自动处理机制
- 即使需要重新登录，也有友好提示

**操作**：
- 无需任何操作，已经配置完成
- 后端重启后，系统会自动提示重新登录

### 生产环境

**推荐：方法2（修改服务配置）**

**理由**：
- Redis持久化保证数据安全
- 服务器重启后Token不丢失
- 用户体验最好

## 验证配置

### 1. 检查Token配置

```bash
# 查看.env.dev文件
type RuoYi-Vue3-FastAPI\ruoyi-fastapi-backend\.env.dev | findstr JWT
```

应该显示：
```
JWT_EXPIRE_MINUTES = 10080
JWT_REDIS_EXPIRE_MINUTES = 10080
```

### 2. 测试Token有效期

1. 登录系统
2. 记录当前时间
3. 1小时后刷新页面
4. 验证：无需重新登录 ✅

### 3. 测试后端重启

**使用方法3（当前配置）**：
1. 登录系统
2. 重启后端服务
3. 刷新页面
4. 预期：弹出"登录状态已失效"提示
5. 点击"重新登录"即可

**使用方法1或方法2（持久化）**：
1. 登录系统
2. 重启后端服务
3. 刷新页面
4. 预期：无需重新登录 ✅

## 常见问题

### Q1: 为什么不直接使用持久化？

**A**: 对于开发环境，方法3（延长Token时间）已经足够：
- 7天有效期覆盖大部分开发场景
- 配置简单，无需修改Redis
- 前端有自动处理机制
- 重新登录只需点击一次

### Q2: 持久化文件会占用多少空间？

**A**: 
- RDB文件：取决于Redis数据量，通常几MB
- AOF文件：记录所有写操作，可能较大
- 建议定期清理：`redis-cli BGREWRITEAOF`

### Q3: 如何查看Redis数据？

```bash
# 连接Redis
redis-cli

# 查看所有key
KEYS *

# 查看Token相关key
KEYS *token*

# 查看key的过期时间（秒）
TTL key_name

# 查看key的值
GET key_name
```

### Q4: 如何清除所有Token？

```bash
# 连接Redis
redis-cli

# 清除所有Token
KEYS *token* | xargs redis-cli DEL

# 或清除整个数据库（谨慎使用）
FLUSHDB
```

## 总结

✅ **已完成配置**：
- Token有效期延长到7天
- 前端自动处理Token失效
- Redis安装路径已确认

📝 **当前方案**：
- 使用方法3（仅延长Token时间）
- 适合开发环境
- 简单有效

🚀 **如需更好体验**：
- 可选择方法1或方法2启用持久化
- 后端重启后Token不会丢失
- 用户体验最佳

现在可以正常使用系统，7天内无需重新登录！
