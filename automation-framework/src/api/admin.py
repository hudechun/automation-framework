"""
简单的Web管理后台

提供基础的管理界面
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

# 创建路由
admin_router = APIRouter()

# 配置模板
templates_dir = os.path.join(os.path.dirname(__file__), "../../templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)


@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """管理后台首页"""
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "title": "管理后台"
    })


@admin_router.get("/tasks", response_class=HTMLResponse)
async def admin_tasks(request: Request):
    """任务管理页面"""
    return templates.TemplateResponse("admin/tasks.html", {
        "request": request,
        "title": "任务管理"
    })


@admin_router.get("/sessions", response_class=HTMLResponse)
async def admin_sessions(request: Request):
    """会话管理页面"""
    return templates.TemplateResponse("admin/sessions.html", {
        "request": request,
        "title": "会话管理"
    })


def configure_admin(app):
    """配置管理后台"""
    # 注册管理后台路由
    app.include_router(admin_router, prefix="/admin", tags=["admin"])
    return True


# 简化的管理路由（作为备用）
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

admin_router = APIRouter()


class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    username: str
    password: str


@admin_router.post("/api/login")
async def admin_login(request: AdminLoginRequest):
    """管理员登录API"""
    # TODO: 实现完整的管理员认证
    if request.username == "admin" and request.password == "admin":
        return {"message": "Login successful", "role": "admin"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@admin_router.get("/api/dashboard")
async def admin_dashboard():
    """管理仪表板API"""
    # TODO: 实现仪表板数据
    return {
        "system_status": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "active_tasks": 5
        },
        "task_statistics": {
            "total_tasks": 120,
            "success_rate": 95.5,
            "failed_tasks": 6
        },
        "recent_executions": []
    }


@admin_router.get("/api/tasks")
async def admin_list_tasks():
    """管理任务列表API"""
    # TODO: 实现任务管理界面数据
    return []


@admin_router.get("/api/users")
async def admin_list_users():
    """管理用户列表API"""
    # TODO: 实现用户管理界面数据
    return []

