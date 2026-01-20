"""
结构化日志系统
"""
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: str
    level: str
    message: str
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    action_type: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict())


class StructuredLogger:
    """
    结构化日志记录器
    """
    
    def __init__(
        self,
        name: str,
        log_file: Optional[Path] = None,
        log_to_db: bool = False
    ):
        self.logger = logging.getLogger(name)
        self.log_file = log_file
        self.log_to_db = log_to_db
        
        # 配置日志格式
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """配置日志记录器"""
        self.logger.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（JSON格式）
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
    
    def log(
        self,
        level: str,
        message: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        action_type: Optional[str] = None,
        duration: Optional[float] = None,
        error: Optional[str] = None,
        **extra
    ) -> None:
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
            task_id: 任务ID
            session_id: 会话ID
            action_type: 操作类型
            duration: 持续时间
            error: 错误信息
            **extra: 额外字段
        """
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            message=message,
            task_id=task_id,
            session_id=session_id,
            action_type=action_type,
            duration=duration,
            error=error,
            extra=extra if extra else None
        )
        
        # 记录到日志文件
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(entry.to_json())
        
        # 记录到数据库
        if self.log_to_db:
            self._log_to_db(entry)
    
    def _log_to_db(self, entry: LogEntry) -> None:
        """
        记录到数据库
        
        Args:
            entry: 日志条目
        """
        # TODO: 实现数据库记录
        pass
    
    def debug(self, message: str, **kwargs) -> None:
        """记录DEBUG级别日志"""
        self.log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """记录INFO级别日志"""
        self.log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """记录WARNING级别日志"""
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """记录ERROR级别日志"""
        self.log("ERROR", message, **kwargs)
    
    def log_action(
        self,
        action_type: str,
        params: Dict[str, Any],
        result: Any,
        duration: float,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        记录操作日志
        
        Args:
            action_type: 操作类型
            params: 操作参数
            result: 操作结果
            duration: 执行时间
            task_id: 任务ID
            session_id: 会话ID
        """
        self.info(
            f"Action executed: {action_type}",
            task_id=task_id,
            session_id=session_id,
            action_type=action_type,
            duration=duration,
            params=params,
            result=str(result)
        )
    
    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        task_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        记录错误日志
        
        Args:
            error: 异常对象
            context: 错误上下文
            task_id: 任务ID
            session_id: 会话ID
        """
        self.error(
            f"Error occurred: {str(error)}",
            task_id=task_id,
            session_id=session_id,
            error=str(error),
            error_type=type(error).__name__,
            context=context
        )


class LogQuery:
    """
    日志查询接口
    """
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file
    
    def query_logs(
        self,
        level: Optional[str] = None,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[LogEntry]:
        """
        查询日志
        
        Args:
            level: 日志级别过滤
            task_id: 任务ID过滤
            session_id: 会话ID过滤
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数量限制
            
        Returns:
            日志条目列表
        """
        if not self.log_file or not self.log_file.exists():
            return []
        
        entries = []
        
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    entry = LogEntry(**data)
                    
                    # 应用过滤条件
                    if level and entry.level != level:
                        continue
                    if task_id and entry.task_id != task_id:
                        continue
                    if session_id and entry.session_id != session_id:
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
    
    async def query_logs_from_db(
        self,
        level: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        从数据库查询日志
        
        Args:
            level: 日志级别
            task_id: 任务ID
            limit: 数量限制
            
        Returns:
            日志列表
        """
        # TODO: 实现数据库查询
        return []
