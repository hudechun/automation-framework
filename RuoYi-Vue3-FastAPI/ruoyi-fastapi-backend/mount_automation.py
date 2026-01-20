"""
将Automation Framework挂载到RuoYi后端
使用优雅的路径管理方式，不依赖 sys.path 修改
"""
import os
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class AutomationFrameworkPathManager:
    """Automation Framework 路径管理器"""
    
    _automation_path: Optional[Path] = None
    _initialized: bool = False
    
    @classmethod
    def find_automation_path(cls) -> Path:
        """
        查找 automation-framework 路径
        
        查找顺序：
        1. 环境变量 AUTOMATION_FRAMEWORK_PATH
        2. 相对于当前文件的相对路径（../../automation-framework）
        3. 项目根目录下的 automation-framework
        
        Returns:
            automation-framework 的路径
            
        Raises:
            FileNotFoundError: 如果找不到路径
        """
        if cls._automation_path and cls._automation_path.exists():
            return cls._automation_path
        
        # 1. 从环境变量获取
        env_path = os.getenv("AUTOMATION_FRAMEWORK_PATH")
        if env_path:
            path = Path(env_path).resolve()
            if path.exists():
                cls._automation_path = path
                return path
        
        # 2. 相对于当前文件的路径
        current_file = Path(__file__).resolve()
        relative_path = current_file.parent.parent.parent / "automation-framework"
        if relative_path.exists():
            cls._automation_path = relative_path
            return relative_path
        
        # 3. 项目根目录
        project_root = current_file.parent.parent
        project_path = project_root / "automation-framework"
        if project_path.exists():
            cls._automation_path = project_path
            return project_path
        
        raise FileNotFoundError(
            "无法找到 automation-framework 目录。"
            "请设置环境变量 AUTOMATION_FRAMEWORK_PATH 或确保 automation-framework 在正确的位置。"
        )
    
    @classmethod
    def setup_path(cls) -> Path:
        """
        设置 Python 路径（仅在必要时）
        
        Returns:
            automation-framework 的路径
        """
        automation_path = cls.find_automation_path()
        
        # 验证路径
        if not (automation_path / "src").exists():
            raise ValueError(f"无效的 automation-framework 路径: {automation_path}")
        
        # 添加到 sys.path（仅在未添加时）
        import sys
        automation_path_str = str(automation_path)
        if automation_path_str not in sys.path:
            sys.path.insert(0, automation_path_str)
            logger.info(f"已添加 automation-framework 到 Python 路径: {automation_path}")
        
        cls._initialized = True
        return automation_path
    
    @classmethod
    def get_automation_path(cls) -> Path:
        """获取 automation-framework 路径"""
        if not cls._initialized:
            return cls.setup_path()
        return cls._automation_path or cls.find_automation_path()


def mount_automation_app(main_app: FastAPI) -> bool:
    """
    将Automation Framework挂载到RuoYi主应用
    
    使用优雅的路径管理，支持：
    - 环境变量配置
    - 自动路径查找
    - 错误处理和日志记录
    
    Args:
        main_app: RuoYi的FastAPI主应用
        
    Returns:
        是否挂载成功
    """
    try:
        # 设置路径
        automation_path = AutomationFrameworkPathManager.setup_path()
        logger.info(f"正在挂载 Automation Framework，路径: {automation_path}")
        
        # 导入 automation-framework 的路由
        # 注意：由于路径已设置，可以直接导入
        from src.api.routers import tasks, executions, configs, sessions, monitor
        from src.api.websocket import manager
        
        # 将 automation 的路由挂载到 RuoYi 应用
        # 使用 /automation 前缀避免路径冲突
        main_app.include_router(
            tasks.router,
            prefix="/automation/api/tasks",
            tags=["automation-tasks"]
        )
        main_app.include_router(
            sessions.router,
            prefix="/automation/api/sessions",
            tags=["automation-sessions"]
        )
        main_app.include_router(
            executions.router,
            prefix="/automation/api/executions",
            tags=["automation-executions"]
        )
        main_app.include_router(
            configs.router,
            prefix="/automation/api/configs",
            tags=["automation-configs"]
        )
        main_app.include_router(
            monitor.router,
            prefix="/automation/api/monitor",
            tags=["automation-monitor"]
        )
        
        # 添加 WebSocket 端点
        @main_app.websocket("/automation/ws")
        async def automation_websocket_endpoint(websocket: WebSocket):
            """Automation Framework WebSocket端点"""
            await manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_json()
                    
                    if data.get("action") == "subscribe":
                        task_id = data.get("task_id")
                        if task_id:
                            manager.subscribe_task(websocket, task_id)
                            await manager.send_personal_message(
                                {"type": "subscribed", "task_id": task_id},
                                websocket
                            )
                    
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
                logger.error(f"WebSocket error: {e}", exc_info=True)
                manager.disconnect(websocket)
        
        # 添加 automation 的根路径
        @main_app.get("/automation")
        async def automation_root():
            """Automation Framework根路径"""
            return {
                "name": "Automation Framework",
                "version": "0.1.0",
                "status": "running",
                "mounted_on": "RuoYi-FastAPI",
                "path": str(automation_path)
            }
        
        logger.info("✅ Automation Framework已成功挂载到 /automation 路径")
        logger.info("   - API: /automation/api/*")
        logger.info("   - WebSocket: /automation/ws")
        
        return True
        
    except FileNotFoundError as e:
        logger.warning(f"⚠️  Automation Framework挂载失败（路径未找到）: {e}")
        logger.warning("   提示：设置环境变量 AUTOMATION_FRAMEWORK_PATH 或确保 automation-framework 在正确位置")
        return False
    except ImportError as e:
        logger.error(f"⚠️  Automation Framework挂载失败（导入错误）: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"⚠️  Automation Framework挂载失败: {e}", exc_info=True)
        return False
