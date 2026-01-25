# FastAPI 认证机制说明

## 🤔 你的疑问

> "用户登录不是 FastAPI 已经自带了吗？"

**答案**: FastAPI 提供了**认证框架**，但**不提供完整的登录实现**。

---

## 📦 FastAPI 提供了什么？

### 1. OAuth2PasswordBearer - Token 提取工具

FastAPI 提供了 `OAuth2PasswordBearer` 类，它的作用是：

```python
from fastapi.security import OAuth2PasswordBearer

# 创建一个 token 提取器
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# 在路由中使用
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # oauth2_scheme 会自动从请求头中提取 token
    # Authorization: Bearer eyJhbGci...
    return {"token": token}
```

**它只做一件事**: 从 HTTP 请求头 `Authorization: Bearer xxx` 中提取 token。

**它不做的事**:
- ❌ 不验证 token 是否有效
- ❌ 不生成 token
- ❌ 不检查用户名密码
- ❌ 不管理用户数据

### 2. OAuth2PasswordRequestForm - 表单解析工具

```python
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 自动解析表单数据
    username = form_data.username
    password = form_data.password
    # 但你需要自己验证用户名密码！
```

**它只做一件事**: 解析登录表单（username, password, scope 等）。

**它不做的事**:
- ❌ 不验证用户名密码
- ❌ 不生成 token
- ❌ 不查询数据库

---

## 🔧 你的系统是如何实现的？

### RuoYi 系统 = FastAPI 框架 + 自定义实现

```
┌─────────────────────────────────────────────────────────┐
│                    你的 RuoYi 系统                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  FastAPI 提供的工具（框架层）                    │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  • OAuth2PasswordBearer  (提取 token)           │  │
│  │  • OAuth2PasswordRequestForm  (解析表单)        │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  RuoYi 自定义实现（业务层）                      │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  • CustomOAuth2PasswordRequestForm               │  │
│  │    (扩展表单，增加验证码字段)                    │  │
│  │                                                  │  │
│  │  • LoginService.authenticate_user()              │  │
│  │    (验证用户名密码、检查验证码)                  │  │
│  │                                                  │  │
│  │  • LoginService.create_access_token()            │  │
│  │    (生成 JWT token，使用密钥签名)               │  │
│  │                                                  │  │
│  │  • LoginService.get_current_user()               │  │
│  │    (验证 token，获取用户信息)                    │  │
│  │                                                  │  │
│  │  • 数据库查询 (UserDao)                         │  │
│  │  • Redis 缓存 (token 存储)                      │  │
│  │  • 密码加密 (PwdUtil)                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 具体对比

### FastAPI 官方示例（最简单的实现）

```python
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 假数据库
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "password": "secret"  # 明文密码（不安全！）
    }
}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. 简单验证（不安全！）
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    # 2. 返回 token（这里只是返回用户名，不是真正的 JWT！）
    return {"access_token": user["username"], "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # 3. 简单验证（不安全！）
    user = fake_users_db.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的 token")
    return user
```

**问题**:
- ❌ 密码明文存储
- ❌ Token 不是 JWT，只是用户名
- ❌ 没有过期时间
- ❌ 没有数据库
- ❌ 没有权限控制

---

### RuoYi 系统的实现（生产级）

```python
# 1. 扩展 FastAPI 的表单类，增加验证码
class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(self, ..., code: str = Form(), uuid: str = Form()):
        super().__init__(...)
        self.code = code  # 验证码
        self.uuid = uuid  # 验证码会话ID

# 2. 登录接口
@login_controller.post('/login')
async def login(form_data: CustomOAuth2PasswordRequestForm = Depends()):
    # 2.1 验证用户名密码（查询数据库）
    user = await LoginService.authenticate_user(request, query_db, user_login)
    
    # 2.2 生成真正的 JWT token（使用密钥签名）
    access_token = await LoginService.create_access_token(
        data={'user_id': user.user_id, 'username': user.username},
        expires_delta=timedelta(minutes=1440)
    )
    
    # 2.3 存储到 Redis（双重验证）
    await redis.set(f'access_token:{session_id}', access_token, ex=1800)
    
    return {'token': access_token}

# 3. 验证 token
@classmethod
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 3.1 使用 JWT 密钥验证签名
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    
    # 3.2 从 Redis 验证 token 是否有效
    redis_token = await redis.get(f'access_token:{session_id}')
    if token != redis_token:
        raise AuthException("token 已失效")
    
    # 3.3 从数据库获取用户完整信息
    user = await UserDao.get_user_by_id(user_id)
    
    return user
```

**优势**:
- ✅ 密码加密存储（bcrypt）
- ✅ 真正的 JWT token（带签名）
- ✅ Token 有过期时间
- ✅ 数据库存储用户
- ✅ Redis 缓存 token
- ✅ 验证码保护
- ✅ 权限控制
- ✅ 数据权限
- ✅ 登录日志

---

## 🎯 总结

### FastAPI 提供的（工具箱）

| 工具 | 作用 | 比喻 |
|------|------|------|
| `OAuth2PasswordBearer` | 从请求头提取 token | 🔧 扳手（只能拧螺丝） |
| `OAuth2PasswordRequestForm` | 解析登录表单 | 📋 表格（只能记录信息） |

### RuoYi 实现的（完整系统）

| 功能 | 实现 | 比喻 |
|------|------|------|
| 用户验证 | `authenticate_user()` | 🔐 门卫（检查身份证） |
| Token 生成 | `create_access_token()` | 🎫 售票员（发放门票） |
| Token 验证 | `get_current_user()` | 👮 保安（验证门票） |
| 密码加密 | `PwdUtil` | 🔒 保险箱（保护密码） |
| 数据库 | `UserDao` | 📚 档案室（存储用户） |
| 缓存 | `Redis` | 🗄️ 快速柜（临时存储） |

---

## 💡 类比理解

### FastAPI 就像提供了"建筑材料"

```
FastAPI 提供:
- 砖头（OAuth2PasswordBearer）
- 水泥（OAuth2PasswordRequestForm）
- 钢筋（Depends 依赖注入）

但你需要自己:
- 设计房子（登录流程）
- 建造房子（实现代码）
- 装修房子（权限控制）
- 安装门锁（JWT 密钥）
```

### RuoYi 是"建好的房子"

```
RuoYi 提供:
- 完整的房子（登录系统）
- 装修好的房间（用户管理）
- 安全的门锁（JWT 认证）
- 监控系统（日志审计）
```

---

## 🔍 你的系统中的实际使用

### 1. FastAPI 的部分（框架提供）

```python
# ruoyi-fastapi-backend/module_admin/service/login_service.py

# 使用 FastAPI 的 OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# 使用 FastAPI 的 OAuth2PasswordRequestForm
class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    # 扩展 FastAPI 的表单类
    pass
```

### 2. RuoYi 的部分（自己实现）

```python
# 所有业务逻辑都是 RuoYi 自己实现的：

class LoginService:
    # ✅ 自己实现：验证用户
    async def authenticate_user(...)
    
    # ✅ 自己实现：生成 token（使用 JWT 密钥）
    async def create_access_token(...)
    
    # ✅ 自己实现：验证 token（使用 JWT 密钥）
    async def get_current_user(...)
    
    # ✅ 自己实现：获取路由信息
    async def get_current_user_routers(...)
    
    # ✅ 自己实现：用户注册
    async def register_user_services(...)
    
    # ✅ 自己实现：忘记密码
    async def forget_user_services(...)
```

---

## 🎓 结论

**FastAPI 没有自带完整的登录系统**，它只提供了：
1. Token 提取工具（`OAuth2PasswordBearer`）
2. 表单解析工具（`OAuth2PasswordRequestForm`）

**RuoYi 系统自己实现了**：
1. ✅ 用户验证逻辑
2. ✅ JWT token 生成（使用密钥）
3. ✅ JWT token 验证（使用密钥）
4. ✅ 数据库操作
5. ✅ Redis 缓存
6. ✅ 密码加密
7. ✅ 权限控制
8. ✅ 验证码
9. ✅ 登录日志

**所以 JWT 密钥是 RuoYi 系统自己使用的，不是 FastAPI 提供的！**
