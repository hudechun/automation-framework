"""
检查点和状态持久化模块
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
import pickle
import gzip

from .session import Session


class CheckpointManager:
    """
    检查点管理器 - 管理会话状态的保存和恢复
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        初始化检查点管理器
        
        Args:
            storage_path: 检查点存储路径，默认为 ./checkpoints
        """
        self.storage_path = storage_path or Path("./checkpoints")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def create_checkpoint(
        self,
        session: Session,
        checkpoint_name: Optional[str] = None,
        format: str = "json"
    ) -> str:
        """
        创建检查点
        
        Args:
            session: 要保存的会话
            checkpoint_name: 检查点名称，默认使用时间戳
            format: 存储格式，支持 'json' 或 'pickle'
            
        Returns:
            检查点ID
        """
        if checkpoint_name is None:
            checkpoint_name = f"{session.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        checkpoint_id = checkpoint_name
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "session_id": session.id,
            "created_at": datetime.now().isoformat(),
            "session_data": session.to_dict(),
        }
        
        # 保存到文件
        if format == "json":
            file_path = self.storage_path / f"{checkpoint_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        elif format == "pickle":
            file_path = self.storage_path / f"{checkpoint_id}.pkl.gz"
            with gzip.open(file_path, "wb") as f:
                pickle.dump(checkpoint_data, f)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return checkpoint_id
        
    def restore_checkpoint(
        self,
        checkpoint_id: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        恢复检查点
        
        Args:
            checkpoint_id: 检查点ID
            format: 存储格式
            
        Returns:
            检查点数据
        """
        if format == "json":
            file_path = self.storage_path / f"{checkpoint_id}.json"
            if not file_path.exists():
                raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found")
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif format == "pickle":
            file_path = self.storage_path / f"{checkpoint_id}.pkl.gz"
            if not file_path.exists():
                raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found")
            with gzip.open(file_path, "rb") as f:
                return pickle.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
    def list_checkpoints(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出检查点
        
        Args:
            session_id: 可选的会话ID过滤
            
        Returns:
            检查点列表
        """
        checkpoints = []
        
        # 扫描JSON文件
        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if session_id is None or data.get("session_id") == session_id:
                        checkpoints.append({
                            "checkpoint_id": data["checkpoint_id"],
                            "session_id": data["session_id"],
                            "created_at": data["created_at"],
                            "format": "json",
                        })
            except Exception:
                continue
        
        # 扫描Pickle文件
        for file_path in self.storage_path.glob("*.pkl.gz"):
            try:
                with gzip.open(file_path, "rb") as f:
                    data = pickle.load(f)
                    if session_id is None or data.get("session_id") == session_id:
                        checkpoints.append({
                            "checkpoint_id": data["checkpoint_id"],
                            "session_id": data["session_id"],
                            "created_at": data["created_at"],
                            "format": "pickle",
                        })
            except Exception:
                continue
        
        # 按创建时间排序
        checkpoints.sort(key=lambda x: x["created_at"], reverse=True)
        return checkpoints
        
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        删除检查点
        
        Args:
            checkpoint_id: 检查点ID
            
        Returns:
            是否删除成功
        """
        # 尝试删除JSON文件
        json_path = self.storage_path / f"{checkpoint_id}.json"
        if json_path.exists():
            json_path.unlink()
            return True
        
        # 尝试删除Pickle文件
        pickle_path = self.storage_path / f"{checkpoint_id}.pkl.gz"
        if pickle_path.exists():
            pickle_path.unlink()
            return True
        
        return False


class SessionExporter:
    """
    会话导出器 - 导出和导入会话
    """
    
    @staticmethod
    def export_session(
        session: Session,
        file_path: Path,
        format: str = "json",
        include_metadata: bool = True
    ) -> None:
        """
        导出会话到文件
        
        Args:
            session: 要导出的会话
            file_path: 导出文件路径
            format: 导出格式
            include_metadata: 是否包含元数据
        """
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "session": session.to_dict(),
        }
        
        if not include_metadata:
            export_data["session"].pop("metadata", None)
        
        if format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        elif format == "pickle":
            with gzip.open(file_path, "wb") as f:
                pickle.dump(export_data, f)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def import_session(
        file_path: Path,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        从文件导入会话
        
        Args:
            file_path: 导入文件路径
            format: 导入格式
            
        Returns:
            会话数据
        """
        if format == "json":
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif format == "pickle":
            with gzip.open(file_path, "rb") as f:
                return pickle.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")


# 全局检查点管理器实例
_global_checkpoint_manager: Optional[CheckpointManager] = None


def get_global_checkpoint_manager() -> CheckpointManager:
    """获取全局检查点管理器"""
    global _global_checkpoint_manager
    if _global_checkpoint_manager is None:
        _global_checkpoint_manager = CheckpointManager()
    return _global_checkpoint_manager
