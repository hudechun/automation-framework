# RuoYi 安全功能检查报告

检查时间: 2026-01-21

## ✅ 已实现的安全功能

### 1. 输入验证 ✅ 已实现

**实现方式**: 使用 Pydantic 模型验证

**位置**: 
- `pydantic_validation_decorator` 库
- 各个 VO 模型中的 `@model_validator` 和 `@field_validator`

**示例**:
```python
# module_admin/entity/vo/user_vo.py
class UserModel(BaseModel):
    user_name: str = Field(description='用户账号')
    nick_name: str = Field(description='用户昵称')
    email: Optional[str] = Field(default=None, description='用户邮箱')
    phonenumber: Optional[str] = Field(default=None, description='手机号码')
    
    @model_validator(mode='after')
    def check_password(self) -> 'UserModel':
        pattern = r"""^[^<>"'|\\]+$"""
        if self.password is None or re.match(pattern, self.password):
            return self
        raise ModelValidatorException(message='密码不能包含非法字符：< > " \' \\ |')
    
    def validate_fields(self) -> None:
        self.get_user_name()
        self.get_nick_name()
```

**验证内容**:
- ✅ 密码非法字符检查
- ✅ 必填字段验证 (`@NotBlank`)
- ✅ 字段长度验证 (`@Size`)
- ✅ 邮箱格式验证 (`@Network`)
- ✅ XSS 防护 (`@Xss`)

**结论**: ✅ **已实现，无需修复**

---

### 2. 事务管理 ✅ 已实现

**实现方式**: 所有数据库操作都使用 try-except-commit-rollback 模式

**示例**:
```python
# module_admin/service/user_service.py
try:
    add_result = await UserDao.add_user_dao(query_db, add_user)
    if page_object.role_ids:
        for role in page_object.role_ids:
            await UserDao.add_user_role_dao(query_db, UserRoleModel(...))
    if page_object.post_ids:
        for post in page_object.post_ids:
            await UserDao.add_user_post_dao(query_db, UserPostModel(...))
    await query_db.commit()  # 统一提交
    return CrudResponseModel(is_success=True, message='新增成功')
except Exception as e:
    await query_db.rollback()  # 失败回滚
    raise e
```

**覆盖范围**:
- ✅ 用户管理
- ✅ 角色管理
- ✅ 部门管理
- ✅ 岗位管理
- ✅ 日志管理
- ✅ 定时任务
- ✅ 代码生成

**结论**: ✅ **已实现，无需修复**

---

### 3. CORS 配置 ✅ 已实现

**实现方式**: FastAPI CORSMiddleware

**位置**: `middlewares/cors_middleware.py`

```python
def add_cors_middleware(app: FastAPI) -> None:
    origins = [
        'http://localhost:80',
        'http://127.0.0.1:80',
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 限制来源
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
```

**安全性**: ⚠️ 开发环境配置，生产环境需要修改

**结论**: ✅ **已实现，但需要配置生产环境的 origins**

---

### 4. 密码加密 ✅ 已实现

**实现方式**: bcrypt 加密

**位置**: `utils/pwd_util.py`

```python
class PwdUtil:
    @staticmethod
    def get_password_hash(password: str) -> str:
        """密码加密"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """密码验证"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

**结论**: ✅ **已实现，无需修复**

---

### 5. 登录保护 ✅ 已实现

**实现方式**: 
- 密码错误次数限制
- 账号锁定机制
- 验证码保护
- IP 黑名单

**位置**: `module_admin/service/login_service.py`

```python
# 密码错误计数
password_error_count = int(password_error_counted) + 1
await request.app.state.redis.set(
    f'{RedisInitKeyConfig.PASSWORD_ERROR_COUNT.key}:{login_user.user_name}',
    password_error_count,
    ex=timedelta(minutes=10),
)

# 超过5次锁定账号
if password_error_count > CommonConstant.PASSWORD_ERROR_COUNT:
    await request.app.state.redis.set(
        f'{RedisInitKeyConfig.ACCOUNT_LOCK.key}:{login_user.user_name}',
        login_user.user_name,
        ex=timedelta(minutes=10),
    )
```

**结论**: ⚠️ **已实现，但存在竞态条件（见下文）**

---

### 6. 权限控制 ✅ 已实现

**实现方式**: 
- 基于角色的访问控制 (RBAC)
- 数据权限控制
- 菜单权限控制

**位置**: 
- `common/aspect/pre_auth.py` - 权限装饰器
- `common/aspect/data_scope.py` - 数据权限

```python
@RequiresPermissions('system:user:add')
async def add_user(...):
    pass

@RequiresRoles('admin')
async def admin_function(...):
    pass
```

**结论**: ✅ **已实现，无需修复**

---

### 7. 日志审计 ✅ 已实现

**实现方式**: 操作日志和登录日志

**位置**: 
- `common/annotation/log_annotation.py`
- `module_admin/service/log_service.py`

```python
@Log(title='用户管理', business_type=BusinessType.INSERT)
async def add_user(...):
    pass
```

**结论**: ✅ **已实现，无需修复**

---

## ❌ 未实现的安全功能

### 1. CSRF 保护 ❌ 未实现

**状态**: 完全未实现

**风险**: 中等

**原因**: 
- FastAPI 默认不提供 CSRF 保护
- 需要手动实现或使用第三方库

**建议**: 
- 对于前后端分离的 SPA 应用，CSRF 风险较低
- 如果使用 Cookie 存储 token，需要实现 CSRF 保护
- 当前使用 Bearer token，风险可控

**优先级**: P2（计划修复）

---

### 2. 速率限制 ❌ 未实现

**状态**: 完全未实现

**风险**: 高

**影响**: 
- 暴力破解攻击
- DDoS 攻击
- API 滥用

**建议**: 使用 `slowapi` 库实现

**优先级**: P1（尽快修复）

---

## ⚠️ 需要修复的问题

### P0 - 立即修复

#### 1. ✅ 硬编码凭证 - 已修复

**状态**: ✅ 已修复
- JWT 密钥已更新
- `init_database.py` 已改为读取环境变量

#### 2. ❌ 密码错误计数竞态条件

**位置**: `module_admin/service/login_service.py` (第 115-130 行)

**问题**:
```python
# 当前实现（有问题）
cache_password_error_count = await request.app.state.redis.get(...)
password_error_count = int(password_error_counted) + 1
await request.app.state.redis.set(...)
```

**风险**: 并发请求可能导致计数不准确

**修复方案**: 使用 Redis INCR 命令（原子操作）

**优先级**: P0

---

#### 3. ❌ 空值检查缺失

**位置**: `module_admin/service/user_service.py` (第 355 行)

**问题**:
```python
user = (await UserDao.get_user_detail_by_id(...)).get('user_basic_info')
if not PwdUtil.verify_password(page_object.old_password, user.password):
    # 如果 user 为 None，这里会报错
```

**修复方案**: 添加空值检查

**优先级**: P0

---

#### 4. ⚠️ 数据权限逻辑

**位置**: `common/aspect/data_scope.py` (第 48-52 行)

**问题**:
```python
if current_user.user.admin or role.data_scope == self.DATA_SCOPE_ALL:
    param_sql_list = [True]
    break
```

**风险**: 只要有一个角色是 DATA_SCOPE_ALL，就能访问所有数据

**状态**: 这可能是设计行为，需要确认业务需求

**优先级**: P0（需要确认）

---

### P1 - 尽快修复

#### 5. ⚠️ 输入验证不完整

**位置**: `module_admin/service/user_service.py` Excel 导入

**问题**:
- dept_id 没有验证是否存在
- email 只检查唯一性，不检查格式（Pydantic 已验证）
- phonenumber 只检查唯一性，不检查格式

**状态**: 部分已实现（Pydantic 验证），但业务逻辑验证不完整

**优先级**: P1

---

#### 6. ✅ 批量导入事务 - 已实现

**位置**: `module_admin/service/user_service.py` (第 488 行)

**当前实现**:
```python
try:
    for _index, row in df.iterrows():
        # 处理每一行
        if user_info:
            if update_support:
                await UserDao.edit_user_dao(query_db, edit_user)
        else:
            await UserDao.add_user_dao(query_db, add_user)
    await query_db.commit()  # 统一提交
    return CrudResponseModel(is_success=True, message='\n'.join(add_error_result))
except Exception as e:
    await query_db.rollback()  # 失败回滚
    raise e
```

**状态**: ✅ 已正确实现事务

**优先级**: 无需修复

---

#### 7. ❌ IP 黑名单检查不完整

**位置**: `module_admin/service/login_service.py` (第 155 行)

**问题**:
```python
if request.headers.get('X-Forwarded-For') in black_ip_list:
    raise LoginException(message='当前IP禁止登录')
```

**风险**:
- `X-Forwarded-For` 可能包含多个 IP（逗号分隔）
- 客户端可以伪造这个头
- 没有检查 `X-Real-IP`

**优先级**: P1

---

#### 8. ❌ 密码重置验证逻辑

**位置**: `module_admin/service/user_service.py` (第 350-363 行)

**问题**:
```python
if page_object.sms_code and page_object.session_id:
    del reset_user['sms_code']
    del reset_user['session_id']
```

**风险**: 没有验证 SMS 验证码是否正确，只是删除了字段

**优先级**: P1

---

### P2 - 计划修复

#### 9. ❌ CSRF 保护

**状态**: 未实现

**优先级**: P2（前后端分离，风险较低）

---

#### 10. ❌ 速率限制

**状态**: 未实现

**优先级**: P1（应提升到 P1）

---

#### 11. ⚠️ Token 验证

**位置**: `module_admin/service/login_service.py` (第 210 行)

**当前实现**:
```python
payload = jwt.decode(token, JwtConfig.jwt_secret_key, algorithms=[JwtConfig.jwt_algorithm])
```

**状态**: JWT 库会自动验证过期时间，但没有显式检查

**优先级**: P2（当前实现可接受）

---

#### 12. ⚠️ 配置管理

**位置**: `config/env.py`

**问题**: 
- 没有验证必需的环境变量
- 默认值可能不安全

**优先级**: P2

---

## 📊 安全功能总结

| 功能 | 状态 | 优先级 | 说明 |
|------|------|--------|------|
| 输入验证 | ✅ 已实现 | - | Pydantic 模型验证 |
| 事务管理 | ✅ 已实现 | - | 所有操作都有事务保护 |
| CORS 配置 | ✅ 已实现 | P2 | 需要配置生产环境 |
| 密码加密 | ✅ 已实现 | - | bcrypt 加密 |
| 登录保护 | ⚠️ 部分实现 | P0 | 存在竞态条件 |
| 权限控制 | ✅ 已实现 | - | RBAC + 数据权限 |
| 日志审计 | ✅ 已实现 | - | 操作日志 + 登录日志 |
| CSRF 保护 | ❌ 未实现 | P2 | 前后端分离，风险较低 |
| 速率限制 | ❌ 未实现 | P1 | 需要实现 |
| 硬编码凭证 | ✅ 已修复 | - | JWT 密钥已更新 |
| 空值检查 | ❌ 部分缺失 | P0 | 需要添加 |
| IP 黑名单 | ⚠️ 不完整 | P1 | 需要改进 |
| 密码重置 | ❌ 验证缺失 | P1 | 需要修复 |

---

## 🎯 修复建议

### 必须修复（P0）

1. ✅ **硬编码凭证** - 已完成
2. ❌ **密码错误计数竞态条件** - 需要修复
3. ❌ **空值检查** - 需要添加
4. ⚠️ **数据权限逻辑** - 需要确认业务需求

### 应该修复（P1）

5. ❌ **速率限制** - 使用 slowapi 实现
6. ❌ **IP 黑名单检查** - 改进实现
7. ❌ **密码重置验证** - 添加 SMS 验证

### 可以修复（P2）

8. ⚠️ **CORS 配置** - 配置生产环境
9. ❌ **CSRF 保护** - 可选实现
10. ⚠️ **配置管理** - 改进验证

---

## 📝 结论

**RuoYi 已经实现了大部分安全功能**，包括：
- ✅ 完整的输入验证
- ✅ 事务管理
- ✅ 密码加密
- ✅ 权限控制
- ✅ 日志审计

**需要修复的主要问题**：
1. 密码错误计数的竞态条件（P0）
2. 空值检查（P0）
3. 速率限制（P1）
4. IP 黑名单检查（P1）
5. 密码重置验证（P1）

**不需要修复的**：
- ✅ 输入验证（已实现）
- ✅ 事务管理（已实现）
- ✅ 批量导入事务（已实现）
- ✅ 硬编码凭证（已修复）
