"""
文件存储管理
"""
import os
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
import hashlib


class FileStorageManager:
    """文件存储管理器"""
    
    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.screenshots_path = self.base_path / "screenshots"
        self.logs_path = self.base_path / "logs"
        self.videos_path = self.base_path / "videos"
        self.exports_path = self.base_path / "exports"
        
        for path in [self.screenshots_path, self.logs_path, self.videos_path, self.exports_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, file_type: str, filename: str) -> Path:
        """获取文件路径"""
        type_map = {
            "screenshot": self.screenshots_path,
            "log": self.logs_path,
            "video": self.videos_path,
            "export": self.exports_path
        }
        base = type_map.get(file_type, self.base_path)
        return base / filename
    
    async def save_file(
        self,
        file_data: bytes,
        filename: str,
        file_type: str = "screenshot",
        metadata: Optional[dict] = None
    ) -> dict:
        """保存文件"""
        file_path = self._get_file_path(file_type, filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        # 计算文件哈希
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # 创建文件记录
        file_record = {
            "id": file_hash[:16],
            "filename": filename,
            "file_type": file_type,
            "path": str(file_path),
            "size": len(file_data),
            "hash": file_hash,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # TODO: 保存到数据库
        return file_record
    
    async def get_file(self, file_id: str) -> Optional[bytes]:
        """获取文件"""
        # TODO: 从数据库查询文件路径
        # 这里简化实现
        for path in [self.screenshots_path, self.logs_path, self.videos_path, self.exports_path]:
            for file_path in path.glob("*"):
                if file_id in str(file_path):
                    with open(file_path, "rb") as f:
                        return f.read()
        return None
    
    async def delete_file(self, file_id: str) -> bool:
        """删除文件"""
        # TODO: 从数据库查询并删除
        for path in [self.screenshots_path, self.logs_path, self.videos_path, self.exports_path]:
            for file_path in path.glob("*"):
                if file_id in str(file_path):
                    file_path.unlink()
                    return True
        return False
    
    async def list_files(
        self,
        file_type: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """列出文件"""
        files = []
        
        if file_type:
            search_paths = [self._get_file_path(file_type, "").parent]
        else:
            search_paths = [self.screenshots_path, self.logs_path, self.videos_path, self.exports_path]
        
        for path in search_paths:
            for file_path in path.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
        
        return files[:limit]
    
    async def cleanup_old_files(self, days: int = 30):
        """清理过期文件"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for path in [self.screenshots_path, self.logs_path, self.videos_path, self.exports_path]:
            for file_path in path.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    file_date = datetime.fromtimestamp(stat.st_ctime)
                    if file_date < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
        
        return deleted_count
    
    async def get_storage_stats(self) -> dict:
        """获取存储统计"""
        stats = {
            "total_size": 0,
            "file_count": 0,
            "by_type": {}
        }
        
        for type_name, path in [
            ("screenshots", self.screenshots_path),
            ("logs", self.logs_path),
            ("videos", self.videos_path),
            ("exports", self.exports_path)
        ]:
            type_size = 0
            type_count = 0
            
            for file_path in path.glob("*"):
                if file_path.is_file():
                    type_size += file_path.stat().st_size
                    type_count += 1
            
            stats["by_type"][type_name] = {
                "size": type_size,
                "count": type_count
            }
            stats["total_size"] += type_size
            stats["file_count"] += type_count
        
        return stats


# 全局文件存储管理器
file_storage = FileStorageManager()
