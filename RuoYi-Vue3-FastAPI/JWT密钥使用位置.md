# 🔍 JWT 密钥在系统中的使用位置

## 📍 密钥定义和加载

### 1. 配置文件定义
**文件**: `ruoyi-fastapi-backend/config/env.py`

```python
class JwtSettings(BaseSettings):
    """Jwt配置"""
    jwt_secret_key: str = 'b01c66dc2c58dc6a0aabfe2144256be36226de378bf87f72c0c795dda67f4d55'
    jwt_algorithm: str = 'HS256'
    jwt_expire_minutes: int = 1440
    jwt_redis_expire_minutes: int = 30
```

### 2. 环境变量加载
**文件**: `ruoyi-fastapi-backend/config/env.py` (第 230-240 行)

```python
# 根据运行环境加载对应的 .env 文件
run_env = os.environ.get('APP_ENV', '')
env_file = '.env.dev'  # 默认开发环境
if run_env != '':
    env_file = f'.env.{run_env}'  # 如 .env.prod
load_dotenv(env_file)

# 实例化配置
JwtConfig = get_config.get_jwt_config()
```

**环境文件**:
- `.env.dev` → 开发环境
- `.env.prod` → 生产环境
- `.env.dockermy` → Docker MySQL 环境
- `.env.dockerpg` → Docker PostgreSQL 环境

---

## 🔐 密钥使用的 3 个核心场景

### 场景 1: 用户登录 - 生成 Token

**文件**: `module_admin/controller/login_controller.py` (第 30-90 行)

```python
@login_controller.post('/login')
async def login(request, form_data, query_db):
    # 1. 验证用户名密码
    result = await LoginService.authenticate_user(request, query_db, user)
    
    # 2. 生成 session_id
    session_id = str(uuid.uuid4())
    
    # 3. 创建 token（使用 JWT 密钥）
    access_token = await LoginService.create_access_token(
        data={
            'user_id': str(result[0].user_id),
            'user_name': result[0].user_name,
            'dept_name': result[1].dept_name,
            'session_id': session_id,
            'login_info': user.login_info,
        },
        expires_delta=timedelta(minutes=JwtConfig.jwt_expire_minutes)
    )
    
    # 4. 存储到 Redis
    await request.app.state.redis.set(
        f'access_token:{session_id}',
        access_token,
        ex=timedelta(minutes=JwtConfig.jwt_redis_expire_minutes)
    )
    
    # 5. 返回 token 给前端
    return {'token': access_token}
```

**实际调用**: `module_admin/service/login_service.py` (第 175-190 行)

```python
@classmethod
async def create_access_token(cls, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({'exp': expire})
    
    # 🔑 这里使用 JWT 密钥签名
    encoded_jwt = jwt.encode(
        to_encode, 
        JwtConfig.jwt_secret_key,  # ← 密钥在这里使用
        algorithm=JwtConfig.jwt_algorithm
    )
    return encoded_jwt
```

---

### 场景 2: 访问接口 - 验证 Token

**文件**: `module_admin/service/login_service.py` (第 195-250 行)

```python
@classmethod
async def get_current_user(cls, request, token, query_db):
    """根据 token 获取当前用户信息"""
    
    # 1. 处理 Bearer 前缀
    if token.startswith('Bearer'):
        token = token.split(' ')[1]
    
    # 2. 🔑 使用 JWT 密钥验证 token
    try:
        payload = jwt.decode(
            token, 
            JwtConfig.jwt_secret_key,  # ← 密钥在这里使用
            algorithms=[JwtConfig.jwt_algorithm]
        )
        user_id = payload.get('user_id')
        session_id = payload.get('session_id')
    except InvalidTokenError:
        raise AuthException(message='用户token已失效，请重新登录')
    
    # 3. 从 Redis 验证 token 是否有效
    redis_token = await request.app.state.redis.get(
        f'access_token:{session_id}'
    )
    
    # 4. 对比 token
    if token == redis_token:
        # 验证通过，返回用户信息
        return current_user
    else:
        raise AuthException(message='用户token已失效，请重新登录')
```

**调用链**:
```
用户请求 → FastAPI 依赖注入 → get_current_user() → jwt.decode(密钥)
```

---

### 场景 3: 用户退出 - 解析 Token

**文件**: `module_admin/controller/login_controller.py` (第 170-180 行)

```python
@login_controller.post('/logout')
async def logout(request, token):
    # 🔑 解析 token 获取 session_id（不验证过期时间）
    payload = jwt.decode(
        token, 
        JwtConfig.jwt_secret_key,  # ← 密钥在这里使用
        algorithms=[JwtConfig.jwt_algorithm],
        options={'verify_exp': False}  # 不验证过期
    )
    
    # 从 Redis 删除 token
    if AppConfig.app_same_time_login:
        token_id = payload.get('session_id')
    else:
        token_id = payload.get('user_id')
    
    await request.app.state.redis.delete(f'access_token:{token_id}')
    return ResponseUtil.success(msg='退出成功')
```

---

### 场景 4: 在线用户列表 - 批量解析 Token

**文件**: `module_admin/service/online_service.py` (第 30-50 行)

```python
@classmethod
async def get_online_list_services(cls, request, query_object):
    # 1. 从 Redis 获取所有在线用户的 token
    access_token_keys = await request.app.state.redis.keys('access_token:*')
    access_token_values_list = await request.app.state.redis.mget(access_token_keys)
    
    # 2. 🔑 批量解析 token
    online_info_list = []
    for item in access_token_values_list:
        payload = jwt.decode(
            item, 
            JwtConfig.jwt_secret_key,  # ← 密钥在这里使用
            algorithms=[JwtConfig.jwt_algorithm]
        )
        
        online_dict = {
            'token_id': payload.get('session_id'),
            'user_name': payload.get('user_name'),
            'dept_name': payload.get('dept_name'),
            'ipaddr': payload.get('login_info').get('ipaddr'),
            'login_location': payload.get('login_info').get('login_location'),
            'browser': payload.get('login_info').get('browser'),
            'os': payload.get('login_info').get('os'),
            'login_time': payload.get('login_info').get('login_time'),
        }
        online_info_list.append(online_dict)
    
    return online_info_list
```

---

## 📊 完整的请求流程

### 流程 1: 用户登录

```
┌─────────────┐
│   前端      │
│ 输入用户名  │
│ 输入密码    │
└──────┬──────┘
       │ POST /login
       ↓
┌─────────────────────────────────────────┐
│  login_controller.py                    │
│  ┌────────────────────────────────────┐ │
│  │ 1. 验证用户名密码                  │ │
│  │ 2. 生成 session_id                 │ │
│  │ 3. 调用 create_access_token()      │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  login_service.py                       │
│  ┌────────────────────────────────────┐ │
│  │ create_access_token()              │ │
│  │                                    │ │
│  │ data = {                           │ │
│  │   user_id: 1,                      │ │
│  │   user_name: "admin",              │ │
│  │   session_id: "uuid-xxx"           │ │
│  │ }                                  │ │
│  │                                    │ │
│  │ 🔑 jwt.encode(                     │ │
│  │     data,                          │ │
│  │     JWT_SECRET_KEY,  ← 密钥使用   │ │
│  │     algorithm='HS256'              │ │
│  │ )                                  │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼─────────────────────────┘
                ↓
        生成的 Token:
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
                ↓
┌─────────────────────────────────────────┐
│  Redis                                  │
│  ┌────────────────────────────────────┐ │
│  │ SET access_token:uuid-xxx          │ │
│  │     eyJhbGciOiJIUzI1NiIsInR...     │ │
│  │     EX 1800 (30分钟)               │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                ↓
        返回给前端:
        { "token": "eyJhbGci..." }
```

### 流程 2: 访问受保护接口

```
┌─────────────┐
│   前端      │
│ 携带 Token  │
└──────┬──────┘
       │ GET /system/user/list
       │ Header: Authorization: Bearer eyJhbGci...
       ↓
┌─────────────────────────────────────────┐
│  FastAPI 依赖注入                       │
│  CurrentUserDependency()                │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  login_service.py                       │
│  ┌────────────────────────────────────┐ │
│  │ get_current_user()                 │ │
│  │                                    │ │
│  │ 1. 提取 token                      │ │
│  │    token = "eyJhbGci..."           │ │
│  │                                    │ │
│  │ 2. 🔑 验证 token                   │ │
│  │    payload = jwt.decode(           │ │
│  │        token,                      │ │
│  │        JWT_SECRET_KEY,  ← 密钥使用│ │
│  │        algorithms=['HS256']        │ │
│  │    )                               │ │
│  │                                    │ │
│  │ 3. 获取用户信息                    │ │
│  │    user_id = payload['user_id']    │ │
│  │    session_id = payload['session_id']│ │
│  └────────────┬───────────────────────┘ │
└───────────────┼─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  Redis                                  │
│  ┌────────────────────────────────────┐ │
│  │ GET access_token:uuid-xxx          │ │
│  │ 对比 token 是否一致                │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼─────────────────────────┘
                ↓
        验证通过 ✅
                ↓
┌─────────────────────────────────────────┐
│  数据库                                 │
│  查询用户详细信息、权限、角色           │
└───────────────┬─────────────────────────┘
                ↓
        返回用户列表数据
```

---

## 🎯 密钥使用总结

| 场景 | 文件 | 函数 | 操作 | 密钥作用 |
|------|------|------|------|----------|
| **登录** | `login_controller.py` | `login()` | `jwt.encode()` | 生成 token |
| **访问接口** | `login_service.py` | `get_current_user()` | `jwt.decode()` | 验证 token |
| **退出登录** | `login_controller.py` | `logout()` | `jwt.decode()` | 解析 token |
| **在线用户** | `online_service.py` | `get_online_list_services()` | `jwt.decode()` | 批量解析 token |

---

## 🔍 如何追踪密钥使用

### 方法 1: 搜索代码
```bash
# 搜索密钥定义
grep -r "JWT_SECRET_KEY" ruoyi-fastapi-backend/

# 搜索 token 生成
grep -r "jwt.encode" ruoyi-fastapi-backend/

# 搜索 token 验证
grep -r "jwt.decode" ruoyi-fastapi-backend/
```

### 方法 2: 查看日志
在 `login_service.py` 中添加日志：
```python
logger.info(f"使用密钥验证 token: {JwtConfig.jwt_secret_key[:10]}...")
```

### 方法 3: 调试断点
在以下位置设置断点：
- `login_service.py` 第 188 行 (生成 token)
- `login_service.py` 第 210 行 (验证 token)

---

## 💡 关键点

1. **密钥只在后端使用**
   - 前端永远不知道密钥
   - 前端只存储和传递 token

2. **密钥用于两个操作**
   - `jwt.encode()` - 生成 token（登录时）
   - `jwt.decode()` - 验证 token（每次请求时）

3. **密钥从环境变量加载**
   - 根据 `APP_ENV` 加载对应的 `.env` 文件
   - 开发/生产/Docker 环境使用不同的密钥

4. **Token 双重验证**
   - JWT 签名验证（使用密钥）
   - Redis 存储验证（防止 token 被盗用）

---

## 🔗 相关文件

- **配置**: `config/env.py`
- **登录**: `module_admin/controller/login_controller.py`
- **服务**: `module_admin/service/login_service.py`
- **在线用户**: `module_admin/service/online_service.py`
- **环境变量**: `.env.dev`, `.env.prod`, `.env.dockermy`, `.env.dockerpg`
