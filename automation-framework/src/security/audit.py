"""
审计日志系统
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """审计日志条目"""
    timestamp: str
    user_id: str
    operation: str
    resource_type: str
    resource_id: Optional[str]
    action: str
    result: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    审计日志记录器
    """
    
    def __init__(
        self,
        log_file: Optional[Path] = None,
        log_to_db: bool = True
    ):
        self.log_file = log_file
        self.log_to_db = log_to_db
        
        # 创建日志文件
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(
        self,
        user_id: str,
        operation: str,
        resource_type: str,
        action: str,
        result: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        记录审计日志
        
        Args:
            user_id: 用户ID
            operation: 操作名称
            resource_type: 资源类型
            action: 操作动作
            result: 操作结果
            resource_id: 资源ID
            details: 详细信息
            ip_address: IP地址
        """
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            operation=operation,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            details=details,
            ip_address=ip_address
        )
        
        # 记录到文件
        if self.log_file:
            self._log_to_file(entry)
        
        # 记录到数据库
        if self.log_to_db:
            self._log_to_db(entry)
        
        # 记录到标准日志
        logger.info(f"Audit: {entry.to_json()}")
    
    def _log_to_file(self, entry: AuditEntry) -> None:
        """
        记录到文件
        
        Args:
            entry: 审计条目
        """
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(entry.to_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log to file: {e}")
    
    def _log_to_db(self, entry: AuditEntry) -> None:
        """
        记录到数据库
        
        Args:
            entry: 审计条目
        """
        # TODO: 实现数据库记录
        pass
    
    def log_task_create(
        self,
        user_id: str,
        task_id: str,
        task_name: str,
        ip_address: Optional[str] = None
    ) -> None:
        """
        记录任务创建
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            task_name: 任务名称
            ip_address: IP地址
        """
        self.log(
            user_id=user_id,
            operation="task_create",
            resource_type="task",
            resource_id=task_id,
            action="create",
            result="success",
            details={"task_name": task_name},
            ip_address=ip_address
        )
    
    def log_task_execute(
        self,
        user_id: str,
        task_id: str,
        result: str,
        ip_address: Optional[str] = None
    ) -> None:
        """
        记录任务执行
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            result: 执行结果
            ip_address: IP地址
        """
        self.log(
            user_id=user_id,
            operation="task_execute",
            resource_type="task",
            resource_id=task_id,
            action="execute",
            result=result,
            ip_address=ip_address
        )
    
    def log_task_delete(
        self,
        user_id: str,
        task_id: str,
        ip_address: Optional[str] = None
    ) -> None:
        """
        记录任务删除
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            ip_address: IP地址
        """
        self.log(
            user_id=user_id,
            operation="task_delete",
            resource_type="task",
            resource_id=task_id,
            action="delete",
            result="success",
            ip_address=ip_address
        )
    
    def log_config_change(
        self,
        user_id: str,
        config_key: str,
        old_value: Any,
        new_value: Any,
        ip_address: Optional[str] = None
    ) -> None:
        """
        记录配置更改
        
        Args:
            user_id: 用户ID
            config_key: 配置键
            old_value: 旧值
            new_value: 新值
            ip_address: IP地址
        """
        self.log(
            user_id=user_id,
            operation="config_change",
            resource_type="config",
            resource_id=config_key,
            action="update",
            result="success",
            details={
                "old_value": str(old_value),
                "new_value": str(new_value)
            },
            ip_address=ip_address
        )
    
    def log_permission_change(
        self,
        user_id: str,
        target_user_id: str,
        permission: str,
        action: str,
        ip_address: Optional[str] = None
    ) -> None:
        """
        记录权限更改
        
        Args:
            user_id: 操作用户ID
            target_user_id: 目标用户ID
            permission: 权限
            action: 操作（grant/revoke）
            ip_address: IP地址
        """
        self.log(
            user_id=user_id,
            operation="permission_change",
            resource_type="user",
            resource_id=target_user_id,
            action=action,
            result="success",
            details={"permission": permission},
            ip_address=ip_address
        )
    
    def log_file_operation(
        self,
        user_id: str,
        file_path: str,
        action: str,
        result: str,
        ip_address: Optional[str] = None
    ) -> None:
        """
        记录文件操作
        
        Args:
            user_id: 用户ID
            file_path: 文件路径
            action: 操作（read/write/delete）
            result: 结果
            ip_address: IP地址
        """
        self.log(
            user_id=user_id,
            operation="file_operation",
            resource_type="file",
            resource_id=file_path,
            action=action,
            result=result,
            ip_address=ip_address
        )
    
    def query_logs(
        self,
        user_id: Optional[str] = None,
        operation: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        查询审计日志
        
        Args:
            user_id: 用户ID过滤
            operation: 操作过滤
            resource_type: 资源类型过滤
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数量限制
            
        Returns:
            审计条目列表
        """
        if not self.log_file or not self.log_file.exists():
            return []
        
        entries = []
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    entry = AuditEntry(**data)
                    
                    # 应用过滤条件
                    if user_id and entry.user_id != user_id:
                        continue
                    if operation and entry.operation != operation:
                        continue
                    if resource_type and entry.resource_type != resource_type:
                        continue
                    
                    # 时间过滤
                    entry_time = datetime.fromisoformat(entry.timestamp)
                    if start_time and entry_time < start_time:
                        continue
                    if end_time and entry_time > end_time:
                        continue
                    
                    entries.append(entry)
                    
                    if len(entries) >= limit:
                        break
                        
                except Exception:
                    continue
        
        return entries
