"""
API认证和授权
"""
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime, timedelta

# API Key认证
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# JWT Token认证
bearer_scheme = HTTPBearer(auto_error=False)

# 配置
SECRET_KEY = "your-secret-key-here"  # TODO: 从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.api_keys = {}  # TODO: 从数据库加载
        self.users = {}  # TODO: 从数据库加载
    
    async def verify_api_key(self, api_key: str) -> bool:
        """验证API Key"""
        # TODO: 从数据库验证
        return api_key in self.api_keys
    
    async def verify_token(self, token: str) -> dict:
        """验证JWT Token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


auth_manager = AuthManager()


async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """获取并验证API Key"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key required")
    
    if not await auth_manager.verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    return api_key


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> dict:
    """获取当前用户（通过JWT Token）"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    user = await auth_manager.verify_token(token)
    return user


# 权限装饰器
def require_permission(permission: str):
    """要求特定权限"""
    async def permission_checker(user: dict = Depends(get_current_user)):
        permissions = user.get("permissions", [])
        if permission not in permissions:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return permission_checker
