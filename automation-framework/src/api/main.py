"""
FastAPI主应用
"""
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from ..models.database import init_db, close_db
from .routers import tasks, executions, configs, notifications, auth, files, sessions, monitor
from .websocket import manager

logger = logging.getLogger(__name__)

# 尝试导入 admin，如果失败则跳过
try:
    from .admin import configure_admin
    ADMIN_AVAILABLE = True
except Exception as e:
    logger.warning(f"Admin module not available: {e}")
    ADMIN_AVAILABLE = False
    configure_admin = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    logger.info("Starting application...")
    await init_db()
    logger.info("Database initialized")
    
    # 配置管理后台（如果可用）
    if ADMIN_AVAILABLE and configure_admin:
        try:
            configure_admin(app)
            logger.info("Admin configured")
        except Exception as e:
            logger.warning(f"Admin configuration failed: {e}")
    else:
        logger.info("Admin not available, skipping")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Database closed")


# 创建FastAPI应用
app = FastAPI(
    title="Automation Framework API",
    description="""
    ## Browser and Desktop Automation Framework
    
    This API provides comprehensive automation capabilities for both browser and desktop applications.
    
    ### Features
    - **Task Management**: Create, execute, and manage automation tasks
    - **Session Management**: Handle browser and desktop sessions
    - **History Tracking**: Track execution history and statistics
    - **Real-time Monitoring**: WebSocket-based real-time updates
    - **AI Integration**: Natural language task processing with LLM
    - **Plugin System**: Extensible plugin architecture
    
    ### Authentication
    - **API Key**: Use `X-API-Key` header for API key authentication
    - **JWT Token**: Use `Authorization: Bearer <token>` for JWT authentication
    
    ### Rate Limiting
    API requests are rate-limited to ensure fair usage.
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Automation Framework Team",
        "email": "support@automation-framework.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# 注册路由
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(executions.router, prefix="/api/executions", tags=["executions"])
app.include_router(configs.router, prefix="/api/configs", tags=["configs"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["monitor"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

# 注册Admin API路由
try:
    from .routers import admin_api
    app.include_router(admin_api.router, tags=["admin"])
    logger.info("Admin API routes registered")
except Exception as e:
    logger.warning(f"Admin API routes not available: {e}")


# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            
            # 处理订阅请求
            if data.get("action") == "subscribe":
                task_id = data.get("task_id")
                if task_id:
                    manager.subscribe_task(websocket, task_id)
                    await manager.send_personal_message(
                        {"type": "subscribed", "task_id": task_id},
                        websocket
                    )
            
            # 处理取消订阅请求
            elif data.get("action") == "unsubscribe":
                task_id = data.get("task_id")
                if task_id:
                    manager.unsubscribe_task(websocket, task_id)
                    await manager.send_personal_message(
                        {"type": "unsubscribed", "task_id": task_id},
                        websocket
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Automation Framework API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
