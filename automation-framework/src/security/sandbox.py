"""
沙箱隔离 - 限制文件系统和网络访问
"""
from typing import Set, Optional, List
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


class Sandbox:
    """
    沙箱管理器 - 限制访问范围
    """
    
    def __init__(
        self,
        allowed_paths: Optional[Set[Path]] = None,
        allowed_domains: Optional[Set[str]] = None,
        allowed_commands: Optional[Set[str]] = None
    ):
        self.allowed_paths = allowed_paths or set()
        self.allowed_domains = allowed_domains or set()
        self.allowed_commands = allowed_commands or set()
        
        # 默认禁止的路径
        self.forbidden_paths = {
            Path("/etc"),
            Path("/sys"),
            Path("/proc"),
            Path("C:\\Windows\\System32"),
            Path("C:\\Windows\\SysWOW64")
        }
    
    def check_file_access(self, path: Path, operation: str) -> bool:
        """
        检查文件访问权限
        
        Args:
            path: 文件路径
            operation: 操作类型
            
        Returns:
            是否允许
        """
        path = Path(path).resolve()
        
        # 检查是否在禁止列表中
        for forbidden in self.forbidden_paths:
            try:
                if path.is_relative_to(forbidden):
                    logger.warning(f"Access denied to forbidden path: {path}")
                    return False
            except (ValueError, AttributeError):
                pass
        
        # 检查是否在允许列表中
        if self.allowed_paths:
            allowed = any(
                path.is_relative_to(allowed_path)
                for allowed_path in self.allowed_paths
            )
            if not allowed:
                logger.warning(f"Access denied to path: {path}")
                return False
        
        return True

    def check_network_access(self, url: str) -> bool:
        """
        检查网络访问权限
        
        Args:
            url: URL地址
            
        Returns:
            是否允许
        """
        if not self.allowed_domains:
            return True
        
        # 提取域名
        domain_pattern = r"https?://([^/]+)"
        match = re.search(domain_pattern, url)
        if not match:
            return False
        
        domain = match.group(1)
        
        # 检查是否在允许列表中
        for allowed_domain in self.allowed_domains:
            if domain == allowed_domain or domain.endswith(f".{allowed_domain}"):
                return True
        
        logger.warning(f"Access denied to domain: {domain}")
        return False
    
    def check_command_execution(self, command: str) -> bool:
        """
        检查命令执行权限
        
        Args:
            command: 命令
            
        Returns:
            是否允许
        """
        if not self.allowed_commands:
            # 如果没有配置允许列表，默认禁止所有命令
            logger.warning(f"Command execution denied: {command}")
            return False
        
        # 提取命令名称
        cmd_name = command.split()[0] if command else ""
        
        # 检查是否在允许列表中
        if cmd_name in self.allowed_commands:
            return True
        
        logger.warning(f"Command execution denied: {command}")
        return False
    
    def add_allowed_path(self, path: Path) -> None:
        """添加允许的路径"""
        self.allowed_paths.add(Path(path).resolve())
    
    def remove_allowed_path(self, path: Path) -> None:
        """移除允许的路径"""
        self.allowed_paths.discard(Path(path).resolve())
    
    def add_allowed_domain(self, domain: str) -> None:
        """添加允许的域名"""
        self.allowed_domains.add(domain)
    
    def remove_allowed_domain(self, domain: str) -> None:
        """移除允许的域名"""
        self.allowed_domains.discard(domain)
    
    def add_allowed_command(self, command: str) -> None:
        """添加允许的命令"""
        self.allowed_commands.add(command)
    
    def remove_allowed_command(self, command: str) -> None:
        """移除允许的命令"""
        self.allowed_commands.discard(command)
