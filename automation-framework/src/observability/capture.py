"""
截图和状态捕获
"""
import gzip
import json
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import base64


class ScreenshotCapture:
    """
    截图捕获管理器
    """
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    async def capture_screenshot(
        self,
        driver: Any,
        name: Optional[str] = None,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Optional[Path]:
        """
        捕获截图
        
        Args:
            driver: 驱动实例
            name: 截图名称
            task_id: 任务ID
            session_id: 会话ID
            
        Returns:
            截图文件路径
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{name or 'screenshot'}_{timestamp}.png"
            
            if task_id:
                filename = f"task_{task_id}_{filename}"
            if session_id:
                filename = f"session_{session_id}_{filename}"
            
            filepath = self.storage_dir / filename
            
            # 捕获截图（具体实现取决于驱动类型）
            if hasattr(driver, "screenshot"):
                await driver.screenshot(str(filepath))
            else:
                return None
            
            return filepath
            
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None
    
    async def capture_on_error(
        self,
        driver: Any,
        error: Exception,
        context: Dict[str, Any]
    ) -> Optional[Path]:
        """
        错误时自动截图
        
        Args:
            driver: 驱动实例
            error: 异常对象
            context: 错误上下文
            
        Returns:
            截图文件路径
        """
        error_name = type(error).__name__
        return await self.capture_screenshot(
            driver,
            name=f"error_{error_name}",
            task_id=context.get("task_id"),
            session_id=context.get("session_id")
        )
    
    async def capture_at_step(
        self,
        driver: Any,
        step_name: str,
        task_id: Optional[str] = None
    ) -> Optional[Path]:
        """
        在关键步骤捕获截图
        
        Args:
            driver: 驱动实例
            step_name: 步骤名称
            task_id: 任务ID
            
        Returns:
            截图文件路径
        """
        return await self.capture_screenshot(
            driver,
            name=f"step_{step_name}",
            task_id=task_id
        )
    
    def cleanup_old_screenshots(self, days: int = 7) -> int:
        """
        清理旧截图
        
        Args:
            days: 保留天数
            
        Returns:
            删除的文件数量
        """
        count = 0
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        for file in self.storage_dir.glob("*.png"):
            if file.stat().st_mtime < cutoff:
                file.unlink()
                count += 1
        
        return count


class StateCapture:
    """
    状态捕获管理器 - 捕获DOM/UI树快照
    """
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    async def capture_dom(
        self,
        driver: Any,
        task_id: Optional[str] = None,
        compress: bool = True
    ) -> Optional[Path]:
        """
        捕获DOM树
        
        Args:
            driver: 浏览器驱动
            task_id: 任务ID
            compress: 是否压缩
            
        Returns:
            文件路径
        """
        try:
            # 获取DOM树
            if not hasattr(driver, "get_dom"):
                return None
            
            dom_data = await driver.get_dom()
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"dom_{timestamp}"
            if task_id:
                filename = f"task_{task_id}_{filename}"
            
            if compress:
                filename += ".json.gz"
                filepath = self.storage_dir / filename
                
                # 压缩存储
                with gzip.open(filepath, "wt", encoding="utf-8") as f:
                    json.dump(dom_data, f)
            else:
                filename += ".json"
                filepath = self.storage_dir / filename
                
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(dom_data, f, indent=2)
            
            return filepath
            
        except Exception as e:
            print(f"Failed to capture DOM: {e}")
            return None
    
    async def capture_ui_tree(
        self,
        driver: Any,
        task_id: Optional[str] = None,
        compress: bool = True
    ) -> Optional[Path]:
        """
        捕获UI树（桌面应用）
        
        Args:
            driver: 桌面驱动
            task_id: 任务ID
            compress: 是否压缩
            
        Returns:
            文件路径
        """
        try:
            # 获取UI树
            if not hasattr(driver, "get_ui_tree"):
                return None
            
            ui_tree = await driver.get_ui_tree()
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"ui_tree_{timestamp}"
            if task_id:
                filename = f"task_{task_id}_{filename}"
            
            if compress:
                filename += ".json.gz"
                filepath = self.storage_dir / filename
                
                # 压缩存储
                with gzip.open(filepath, "wt", encoding="utf-8") as f:
                    json.dump(ui_tree, f)
            else:
                filename += ".json"
                filepath = self.storage_dir / filename
                
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(ui_tree, f, indent=2)
            
            return filepath
            
        except Exception as e:
            print(f"Failed to capture UI tree: {e}")
            return None
    
    async def capture_context(
        self,
        driver: Any,
        variables: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Optional[Path]:
        """
        捕获完整上下文（用于错误调试）
        
        Args:
            driver: 驱动实例
            variables: 变量字典
            task_id: 任务ID
            
        Returns:
            文件路径
        """
        try:
            context = {
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "variables": variables,
            }
            
            # 捕获DOM/UI树
            if hasattr(driver, "get_dom"):
                context["dom"] = await driver.get_dom()
            elif hasattr(driver, "get_ui_tree"):
                context["ui_tree"] = await driver.get_ui_tree()
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"context_{timestamp}.json.gz"
            if task_id:
                filename = f"task_{task_id}_{filename}"
            
            filepath = self.storage_dir / filename
            
            # 压缩存储
            with gzip.open(filepath, "wt", encoding="utf-8") as f:
                json.dump(context, f)
            
            return filepath
            
        except Exception as e:
            print(f"Failed to capture context: {e}")
            return None
    
    def cleanup_old_captures(self, days: int = 7) -> int:
        """
        清理旧捕获文件
        
        Args:
            days: 保留天数
            
        Returns:
            删除的文件数量
        """
        count = 0
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        for pattern in ["*.json", "*.json.gz"]:
            for file in self.storage_dir.glob(pattern):
                if file.stat().st_mtime < cutoff:
                    file.unlink()
                    count += 1
        
        return count
