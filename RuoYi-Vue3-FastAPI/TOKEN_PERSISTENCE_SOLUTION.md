# Token持久化解决方案

## 问题分析

### 原始问题
后端重启后，用户Token失效，需要重新登录。

### 根本原因
1. **Redis数据丢失**：后端重启时，Redis中存储的Token数据被清空
2. **Token验证失败**：虽然JWT Token本身没过期，但Redis中找不到对应记录
3. **用户体验差**：开发时频繁重启后端，用户需要反复登录

## 解决方案

### 方案1：延长Token有效期（已实施）✅

**修改内容**：`.env.dev`

```bash
# 令牌过期时间（分钟）- 开发环境设置为7天
JWT_EXPIRE_MINUTES = 10080

# redis中令牌过期时间（分钟）- 开发环境设置为7天
JWT_REDIS_EXPIRE_MINUTES = 10080
```

**效果**：
- Token有效期从1天延长到7天
- Redis中的Token记录也保持7天
- 减少用户重新登录的频率

**局限性**：
- 后端重启时Redis数据仍会丢失
- 只是延长了有效期，没有解决根本问题

### 方案2：Redis持久化（推荐）✅

**配置文件**：`redis.conf`

启用两种持久化机制：

#### RDB持久化（快照）
```conf
# 900秒内至少1个key被修改，则触发保存
save 900 1
# 300秒内至少10个key被修改，则触发保存
save 300 10
# 60秒内至少10000个key被修改，则触发保存
save 60 10000

dbfilename dump.rdb
rdbcompression yes
```

**特点**：
- 定期保存Redis数据快照
- 恢复速度快
- 可能丢失最后一次快照后的数据

#### AOF持久化（追加日志）
```conf
# 启用AOF持久化
appendonly yes
appendfilename "appendonly.aof"

# 每秒同步一次（推荐）
appendfsync everysec
```

**特点**：
- 记录每个写操作
- 数据更安全，最多丢失1秒数据
- 文件较大，恢复较慢

#### 内存淘汰策略
```conf
maxmemory 256mb
# 不淘汰，内存满时返回错误（适合Token存储）
maxmemory-policy noeviction
```

### 方案3：使用数据库存储Token（备选）

如果Redis持久化仍不满足需求，可以将Token同时存储到MySQL：

```python
# 在登录时同时写入Redis和MySQL
await TokenDao.save_token(user_id, token, expire_time)
await redis.set(f"token:{user_id}", token, ex=expire_time)

# 验证时先查Redis，Redis没有则查MySQL
token = await redis.get(f"token:{user_id}")
if not token:
    token = await TokenDao.get_token(user_id)
    if token:
        # 重新写入Redis
        await redis.set(f"token:{user_id}", token, ex=expire_time)
```

## 使用方法

### 1. 启动Redis（带持久化）

**Windows**：
```bash
# 方法1：使用启动脚本
start_redis_persistent.bat

# 方法2：手动启动
redis-server redis.conf
```

**Linux/Mac**：
```bash
redis-server redis.conf
```

### 2. 验证Redis持久化

```bash
# 连接Redis
redis-cli

# 设置测试数据
SET test_key "test_value"

# 查看持久化文件
# Windows: dir dump.rdb appendonly.aof
# Linux/Mac: ls -lh dump.rdb appendonly.aof

# 重启Redis
# Windows: taskkill /F /IM redis-server.exe && redis-server redis.conf
# Linux/Mac: redis-cli shutdown && redis-server redis.conf

# 验证数据是否恢复
GET test_key
# 应该返回 "test_value"
```

### 3. 启动后端服务

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

## 配置对比

| 配置项 | 修改前 | 修改后 | 说明 |
|--------|--------|--------|------|
| JWT_EXPIRE_MINUTES | 1440 (1天) | 10080 (7天) | Token本身的有效期 |
| JWT_REDIS_EXPIRE_MINUTES | 30 (30分钟) | 10080 (7天) | Redis中Token的过期时间 |
| Redis持久化 | 未启用 | RDB + AOF | 后端重启后数据不丢失 |
| 内存淘汰策略 | 默认 | noeviction | 内存满时不淘汰Token |

## 测试步骤

### 测试1：Token长期有效性

1. 登录系统
2. 等待1小时
3. 刷新页面或执行操作
4. 验证：无需重新登录 ✅

### 测试2：后端重启后Token保持

1. 登录系统
2. 停止后端服务（Ctrl+C）
3. 重新启动后端服务
4. 刷新页面或执行操作
5. 验证：无需重新登录 ✅

### 测试3：Redis重启后Token保持

1. 登录系统
2. 停止Redis服务
3. 重新启动Redis（使用redis.conf）
4. 刷新页面或执行操作
5. 验证：无需重新登录 ✅

## 注意事项

### 开发环境 vs 生产环境

**开发环境**（当前配置）：
- Token有效期：7天
- Redis持久化：启用
- 目的：减少重复登录，提高开发效率

**生产环境**（建议配置）：
- Token有效期：1-2小时
- Redis持久化：必须启用
- 添加Token刷新机制
- 启用Redis密码认证
- 配置Redis主从复制或集群

### 安全建议

1. **生产环境必须设置Redis密码**
```conf
requirepass your_strong_password_here
```

2. **定期清理过期Token**
```python
# 定时任务：每天清理过期Token
@scheduler.scheduled_job('cron', hour=3)
async def clean_expired_tokens():
    await TokenDao.delete_expired_tokens()
```

3. **Token刷新机制**
```python
# Token即将过期时自动刷新
if token_expire_time - now < 5 * 60:  # 5分钟内过期
    new_token = generate_new_token(user_id)
    return {"token": new_token, "refresh": True}
```

## 故障排查

### 问题1：Redis启动失败

**错误**：`Creating Server TCP listening socket 127.0.0.1:6379: bind: No error`

**解决**：
```bash
# 查找占用6379端口的进程
netstat -ano | findstr :6379

# 结束进程
taskkill /F /PID <进程ID>

# 重新启动
redis-server redis.conf
```

### 问题2：持久化文件权限错误

**错误**：`Can't open the append-only file: Permission denied`

**解决**：
```bash
# Windows: 以管理员身份运行
# Linux/Mac: 修改文件权限
chmod 644 dump.rdb appendonly.aof
```

### 问题3：Token仍然失效

**检查清单**：
1. ✅ Redis是否使用redis.conf启动
2. ✅ 持久化文件是否生成（dump.rdb, appendonly.aof）
3. ✅ .env.dev中的过期时间是否已修改
4. ✅ 后端服务是否已重启
5. ✅ 浏览器是否清除了localStorage

## 总结

通过以下三个措施，彻底解决Token失效问题：

1. ✅ **延长Token有效期**：从1天延长到7天
2. ✅ **启用Redis持久化**：RDB + AOF双重保障
3. ✅ **前端自动处理**：Token失效时自动提示重新登录

现在即使后端重启，用户也无需重新登录！
