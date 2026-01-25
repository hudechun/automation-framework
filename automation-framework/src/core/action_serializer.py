"""
Action序列化和反序列化辅助模块
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from .interfaces import Action
from .types import ActionType
from .actions import (
    GoToURL, GoBack, GoForward, Refresh, WaitForLoad,
    Click, DoubleClick, RightClick, Hover, Drag,
    Type, Press, PressCombo, Upload, Clear,
    GetText, GetAttribute, Screenshot, GetUITree, IsVisible,
    WaitForElement, WaitForText, WaitForCondition, Sleep,
    StartApp, SwitchWindow, CloseWindow,
    Copy, Paste, Cut,
    OpenFile, SaveFile, SaveAs,
    ClickCoordinate,
)
from .wechat_actions import (
    OpenWeChat, FindContact, FindGroup, SendMessage,
    WaitForMessage, SendFile, SendImage, GetChatHistory
)
from .smart_wait import SmartWait, wait_for_element_visible, wait_for_text, wait_for_network_idle
from .control_flow import Loop, If, While


# Action类名到Action类的映射
ACTION_CLASS_MAP: Dict[str, type] = {
    "GoToURL": GoToURL,
    "GoBack": GoBack,
    "GoForward": GoForward,
    "Refresh": Refresh,
    "WaitForLoad": WaitForLoad,
    "Click": Click,
    "DoubleClick": DoubleClick,
    "RightClick": RightClick,
    "Hover": Hover,
    "Drag": Drag,
    "Type": Type,
    "Press": Press,
    "PressCombo": PressCombo,
    "Upload": Upload,
    "Clear": Clear,
    "GetText": GetText,
    "GetAttribute": GetAttribute,
    "Screenshot": Screenshot,
    "GetUITree": GetUITree,
    "IsVisible": IsVisible,
    "WaitForElement": WaitForElement,
    "WaitForText": WaitForText,
    "WaitForCondition": WaitForCondition,
    "Sleep": Sleep,
    # 桌面专用操作
    "StartApp": StartApp,
    "SwitchWindow": SwitchWindow,
    "CloseWindow": CloseWindow,
    "Copy": Copy,
    "Paste": Paste,
    "Cut": Cut,
    "OpenFile": OpenFile,
    "SaveFile": SaveFile,
    "SaveAs": SaveAs,
    "ClickCoordinate": ClickCoordinate,
    # 智能等待
    "SmartWait": SmartWait,
    # 控制流
    "Loop": Loop,
    "If": If,
    "While": While,
    # 微信专用操作
    "OpenWeChat": OpenWeChat,
    "FindContact": FindContact,
    "FindGroup": FindGroup,
    "SendMessage": SendMessage,
    "WaitForMessage": WaitForMessage,
    "SendFile": SendFile,
    "SendImage": SendImage,
    "GetChatHistory": GetChatHistory,
}


def serialize_action(action: Action) -> Dict[str, Any]:
    """
    序列化Action对象为字典
    
    Args:
        action: Action对象
        
    Returns:
        序列化后的字典
    """
    """
    序列化Action对象为字典
    
    Args:
        action: Action对象
        
    Returns:
        字典表示，包含class_name用于反序列化
    """
    # 使用Action的to_dict方法
    data = action.to_dict()
    # 添加class_name用于反序列化
    data["class_name"] = action.__class__.__name__
    
    # 对于有特殊属性的Action，确保参数完整
    if hasattr(action, 'selector'):
        data["params"]["selector"] = action.selector
    if hasattr(action, 'url'):
        data["params"]["url"] = action.url
    if hasattr(action, 'text'):
        data["params"]["text"] = action.text
    if hasattr(action, 'key'):
        data["params"]["key"] = action.key
    if hasattr(action, 'keys'):
        data["params"]["keys"] = action.keys
    if hasattr(action, 'button'):
        data["params"]["button"] = action.button
    if hasattr(action, 'timeout'):
        data["params"]["timeout"] = action.timeout
    if hasattr(action, 'delay'):
        data["params"]["delay"] = action.delay
    if hasattr(action, 'duration'):
        data["params"]["duration"] = action.duration
    if hasattr(action, 'file_path'):
        data["params"]["file_path"] = action.file_path
    if hasattr(action, 'from_selector'):
        data["params"]["from_selector"] = action.from_selector
    if hasattr(action, 'to_selector'):
        data["params"]["to_selector"] = action.to_selector
    if hasattr(action, 'attribute'):
        data["params"]["attribute"] = action.attribute
    if hasattr(action, 'path'):
        data["params"]["path"] = action.path
    if hasattr(action, 'full_page'):
        data["params"]["full_page"] = action.full_page
    if hasattr(action, 'depth'):
        data["params"]["depth"] = action.depth
    if hasattr(action, 'condition'):
        data["params"]["condition"] = action.condition
    
    return data


def deserialize_action(data: Dict[str, Any]) -> Optional[Action]:
    """
    从字典反序列化Action对象
    
    Args:
        data: 字典数据，必须包含class_name和action_type
        
    Returns:
        Action对象，如果无法反序列化返回None
    """
    class_name = data.get("class_name")
    if not class_name:
        # 如果没有class_name，尝试从action_type推断
        action_type = ActionType(data.get("action_type"))
        # 这里可以根据action_type推断，但最好有class_name
        return None
    
    action_class = ACTION_CLASS_MAP.get(class_name)
    if not action_class:
        return None
    
    # 获取参数
    params = data.get("params", {})
    
    # 根据不同的Action类创建实例
    try:
        if class_name == "GoToURL":
            return GoToURL(url=params.get("url", ""))
        elif class_name == "WaitForLoad":
            return WaitForLoad(timeout=params.get("timeout", 30000))
        elif class_name == "Click":
            return Click(selector=params.get("selector", ""), button=params.get("button", "left"))
        elif class_name == "DoubleClick":
            return DoubleClick(selector=params.get("selector", ""))
        elif class_name == "RightClick":
            return RightClick(selector=params.get("selector", ""))
        elif class_name == "Hover":
            return Hover(selector=params.get("selector", ""))
        elif class_name == "Drag":
            return Drag(
                from_selector=params.get("from_selector", ""),
                to_selector=params.get("to_selector", "")
            )
        elif class_name == "Type":
            return Type(
                selector=params.get("selector", ""),
                text=params.get("text", ""),
                delay=params.get("delay", 0)
            )
        elif class_name == "Press":
            return Press(key=params.get("key", ""))
        elif class_name == "PressCombo":
            return PressCombo(keys=params.get("keys", []))
        elif class_name == "Upload":
            return Upload(
                selector=params.get("selector", ""),
                file_path=params.get("file_path", "")
            )
        elif class_name == "Clear":
            return Clear(selector=params.get("selector", ""))
        elif class_name == "GetText":
            return GetText(selector=params.get("selector", ""))
        elif class_name == "GetAttribute":
            return GetAttribute(
                selector=params.get("selector", ""),
                attribute=params.get("attribute", "")
            )
        elif class_name == "Screenshot":
            return Screenshot(
                path=params.get("path"),
                full_page=params.get("full_page", False)
            )
        elif class_name == "GetUITree":
            return GetUITree(depth=params.get("depth", 10))
        elif class_name == "IsVisible":
            return IsVisible(selector=params.get("selector", ""))
        elif class_name == "WaitForElement":
            return WaitForElement(
                selector=params.get("selector", ""),
                timeout=params.get("timeout", 30000)
            )
        elif class_name == "WaitForText":
            return WaitForText(
                text=params.get("text", ""),
                timeout=params.get("timeout", 30000)
            )
        elif class_name == "WaitForCondition":
            return WaitForCondition(
                condition=params.get("condition", ""),
                timeout=params.get("timeout", 30000)
            )
        elif class_name == "Sleep":
            return Sleep(duration=params.get("duration", 1000))
        elif class_name == "StartApp":
            return StartApp(
                app_path=params.get("app_path", ""),
                window_title=params.get("window_title"),
                **params.get("kwargs", {})
            )
        elif class_name == "SwitchWindow":
            return SwitchWindow(window_title=params.get("window_title", ""))
        elif class_name == "CloseWindow":
            return CloseWindow(window_title=params.get("window_title"))
        elif class_name == "Copy":
            return Copy(selector=params.get("selector"))
        elif class_name == "Paste":
            return Paste(selector=params.get("selector"))
        elif class_name == "Cut":
            return Cut(selector=params.get("selector"))
        elif class_name == "OpenFile":
            return OpenFile(
                file_path=params.get("file_path", ""),
                app_path=params.get("app_path")
            )
        elif class_name == "SaveFile":
            return SaveFile(file_path=params.get("file_path"))
        elif class_name == "SaveAs":
            return SaveAs(file_path=params.get("file_path", ""))
        elif class_name == "ClickCoordinate":
            return ClickCoordinate(
                x=params.get("x", 0),
                y=params.get("y", 0),
                button=params.get("button", "left")
            )
        # 微信专用操作
        elif class_name == "OpenWeChat":
            return OpenWeChat(wechat_path=params.get("wechat_path"))
        elif class_name == "FindContact":
            return FindContact(
                contact_name=params.get("contact_name", ""),
                search_type=params.get("search_type", "name")
            )
        elif class_name == "FindGroup":
            return FindGroup(group_name=params.get("group_name", ""))
        elif class_name == "SendMessage":
            return SendMessage(
                message=params.get("message", ""),
                contact_name=params.get("contact_name"),
                group_name=params.get("group_name")
            )
        elif class_name == "WaitForMessage":
            return WaitForMessage(
                timeout=params.get("timeout", 30000),
                contact_name=params.get("contact_name"),
                group_name=params.get("group_name"),
                message_filter=params.get("message_filter")
            )
        elif class_name == "SendFile":
            return SendFile(
                file_path=params.get("file_path", ""),
                contact_name=params.get("contact_name"),
                group_name=params.get("group_name")
            )
        elif class_name == "SendImage":
            return SendImage(
                image_path=params.get("image_path", ""),
                contact_name=params.get("contact_name"),
                group_name=params.get("group_name")
            )
        elif class_name == "GetChatHistory":
            return GetChatHistory(
                contact_name=params.get("contact_name"),
                group_name=params.get("group_name"),
                limit=params.get("limit", 50)
            )
        elif class_name in ["GoBack", "GoForward", "Refresh"]:
            # 这些操作不需要参数
            return action_class()
        else:
            # 通用方式：使用params创建
            return action_class(**params)
    except Exception as e:
        print(f"Failed to deserialize action {class_name}: {e}")
        return None


def serialize_actions(actions: List[Action]) -> List[Dict[str, Any]]:
    """
    序列化Action列表
    
    Args:
        actions: Action对象列表
        
    Returns:
        字典列表
    """
    return [serialize_action(action) for action in actions]


def deserialize_actions(data_list: List[Dict[str, Any]]) -> List[Action]:
    """
    从字典列表反序列化Action列表
    
    Args:
        data_list: 字典列表
        
    Returns:
        Action对象列表（过滤掉None）
    """
    actions = []
    for data in data_list:
        action = deserialize_action(data)
        if action:
            actions.append(action)
    return actions
