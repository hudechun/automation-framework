"""
微信专用操作类 - 用于微信自动化场景
"""
from typing import Any, Optional, List
from .interfaces import Action, Driver
from .types import ActionType


class OpenWeChat(Action):
    """打开微信应用"""
    
    def __init__(self, wechat_path: Optional[str] = None):
        """
        初始化打开微信操作
        
        Args:
            wechat_path: 微信安装路径（可选，如果不提供则自动查找）
        """
        super().__init__(ActionType.NAVIGATION, wechat_path=wechat_path)
        self.wechat_path = wechat_path
    
    async def execute(self, driver: Driver) -> Any:
        """执行打开微信操作"""
        return await driver.execute_action(self)


class FindContact(Action):
    """查找微信联系人"""
    
    def __init__(self, contact_name: str, search_type: str = "name"):
        """
        初始化查找联系人操作
        
        Args:
            contact_name: 联系人名称或备注
            search_type: 搜索类型（name: 按名称, remark: 按备注, phone: 按手机号）
        """
        super().__init__(
            ActionType.QUERY,
            contact_name=contact_name,
            search_type=search_type
        )
        self.contact_name = contact_name
        self.search_type = search_type
    
    def validate(self) -> bool:
        """验证参数"""
        return bool(self.contact_name and isinstance(self.contact_name, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行查找联系人操作"""
        if not self.validate():
            raise ValueError("Invalid contact_name parameter")
        return await driver.execute_action(self)


class FindGroup(Action):
    """查找微信群聊"""
    
    def __init__(self, group_name: str):
        """
        初始化查找群聊操作
        
        Args:
            group_name: 群聊名称
        """
        super().__init__(ActionType.QUERY, group_name=group_name)
        self.group_name = group_name
    
    def validate(self) -> bool:
        """验证参数"""
        return bool(self.group_name and isinstance(self.group_name, str))
    
    async def execute(self, driver: Driver) -> Any:
        """执行查找群聊操作"""
        if not self.validate():
            raise ValueError("Invalid group_name parameter")
        return await driver.execute_action(self)


class SendMessage(Action):
    """发送微信消息"""
    
    def __init__(
        self,
        message: str,
        contact_name: Optional[str] = None,
        group_name: Optional[str] = None
    ):
        """
        初始化发送消息操作
        
        Args:
            message: 消息内容
            contact_name: 联系人名称（如果发送给联系人）
            group_name: 群聊名称（如果发送到群聊）
        """
        super().__init__(
            ActionType.INPUT,
            message=message,
            contact_name=contact_name,
            group_name=group_name
        )
        self.message = message
        self.contact_name = contact_name
        self.group_name = group_name
    
    def validate(self) -> bool:
        """验证参数"""
        if not self.message:
            return False
        # 必须指定联系人或群聊之一
        return bool(self.contact_name or self.group_name)
    
    async def execute(self, driver: Driver) -> Any:
        """执行发送消息操作"""
        if not self.validate():
            raise ValueError("Invalid message parameters")
        return await driver.execute_action(self)


class WaitForMessage(Action):
    """等待接收微信消息"""
    
    def __init__(
        self,
        timeout: int = 30000,
        contact_name: Optional[str] = None,
        group_name: Optional[str] = None,
        message_filter: Optional[str] = None
    ):
        """
        初始化等待消息操作
        
        Args:
            timeout: 超时时间（毫秒）
            contact_name: 联系人名称（如果只等待特定联系人）
            group_name: 群聊名称（如果只等待特定群聊）
            message_filter: 消息过滤条件（可选，如包含特定关键词）
        """
        super().__init__(
            ActionType.WAIT,
            timeout=timeout,
            contact_name=contact_name,
            group_name=group_name,
            message_filter=message_filter
        )
        self.timeout = timeout
        self.contact_name = contact_name
        self.group_name = group_name
        self.message_filter = message_filter
    
    def validate(self) -> bool:
        """验证参数"""
        return isinstance(self.timeout, int) and self.timeout > 0
    
    async def execute(self, driver: Driver) -> Any:
        """执行等待消息操作"""
        if not self.validate():
            raise ValueError("Invalid timeout parameter")
        return await driver.execute_action(self)


class SendFile(Action):
    """发送文件（微信专用）"""
    
    def __init__(
        self,
        file_path: str,
        contact_name: Optional[str] = None,
        group_name: Optional[str] = None
    ):
        """
        初始化发送文件操作
        
        Args:
            file_path: 文件路径
            contact_name: 联系人名称
            group_name: 群聊名称
        """
        super().__init__(
            ActionType.INPUT,
            file_path=file_path,
            contact_name=contact_name,
            group_name=group_name
        )
        self.file_path = file_path
        self.contact_name = contact_name
        self.group_name = group_name
    
    def validate(self) -> bool:
        """验证参数"""
        import os
        if not self.file_path or not os.path.exists(self.file_path):
            return False
        return bool(self.contact_name or self.group_name)
    
    async def execute(self, driver: Driver) -> Any:
        """执行发送文件操作"""
        if not self.validate():
            raise ValueError("Invalid file_path or contact/group parameter")
        return await driver.execute_action(self)


class SendImage(Action):
    """发送图片（微信专用）"""
    
    def __init__(
        self,
        image_path: str,
        contact_name: Optional[str] = None,
        group_name: Optional[str] = None
    ):
        """
        初始化发送图片操作
        
        Args:
            image_path: 图片路径
            contact_name: 联系人名称
            group_name: 群聊名称
        """
        super().__init__(
            ActionType.INPUT,
            image_path=image_path,
            contact_name=contact_name,
            group_name=group_name
        )
        self.image_path = image_path
        self.contact_name = contact_name
        self.group_name = group_name
    
    def validate(self) -> bool:
        """验证参数"""
        import os
        if not self.image_path or not os.path.exists(self.image_path):
            return False
        # 检查是否为图片文件
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        ext = os.path.splitext(self.image_path)[1].lower()
        if ext not in valid_extensions:
            return False
        return bool(self.contact_name or self.group_name)
    
    async def execute(self, driver: Driver) -> Any:
        """执行发送图片操作"""
        if not self.validate():
            raise ValueError("Invalid image_path or contact/group parameter")
        return await driver.execute_action(self)


class GetChatHistory(Action):
    """获取聊天记录（微信专用）"""
    
    def __init__(
        self,
        contact_name: Optional[str] = None,
        group_name: Optional[str] = None,
        limit: int = 50
    ):
        """
        初始化获取聊天记录操作
        
        Args:
            contact_name: 联系人名称
            group_name: 群聊名称
            limit: 获取记录数量限制
        """
        super().__init__(
            ActionType.QUERY,
            contact_name=contact_name,
            group_name=group_name,
            limit=limit
        )
        self.contact_name = contact_name
        self.group_name = group_name
        self.limit = limit
    
    def validate(self) -> bool:
        """验证参数"""
        return bool(self.contact_name or self.group_name) and isinstance(self.limit, int) and self.limit > 0
    
    async def execute(self, driver: Driver) -> Any:
        """执行获取聊天记录操作"""
        if not self.validate():
            raise ValueError("Invalid parameters")
        return await driver.execute_action(self)
