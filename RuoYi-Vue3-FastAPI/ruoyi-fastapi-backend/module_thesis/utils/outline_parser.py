"""
大纲数据解析工具
用于统一处理不同格式的大纲数据
"""
import json
from typing import Dict, Any, Optional, Union


def parse_outline_data(outline_data: Union[dict, str, None]) -> tuple[Optional[dict], Optional[str]]:
    """
    解析大纲数据，支持多种格式
    
    支持的格式：
    1. 直接格式：{"chapters": [...]}
    2. 包装格式：{"title": "...", "content": "{...JSON字符串...}", "chapters": []}
    3. JSON字符串格式
    
    :param outline_data: 大纲数据（字典或字符串）
    :return: (outline_data_dict, outline_context) 元组
    """
    if not outline_data:
        return None, None
    
    outline_data_dict = None
    outline_context = None
    
    try:
        # 如果是字符串，先解析为字典
        if isinstance(outline_data, str):
            try:
                outline_data_dict = json.loads(outline_data)
            except json.JSONDecodeError:
                outline_context = outline_data
                return None, outline_context
        else:
            outline_data_dict = outline_data
        
        # 检查是否有 content 字段（大纲数据可能在 content 中）
        if isinstance(outline_data_dict, dict):
            if 'content' in outline_data_dict:
                content_value = outline_data_dict['content']
                
                # 如果 content 是字符串，尝试解析
                if isinstance(content_value, str):
                    try:
                        content_data = json.loads(content_value)
                        if isinstance(content_data, dict):
                            # 如果 content 中有 chapters，优先使用 content 的数据
                            if 'chapters' in content_data:
                                outline_data_dict = content_data
                            # 如果 content 是字典但没有 chapters，尝试合并到外层
                            elif 'chapters' not in outline_data_dict:
                                outline_data_dict = {**outline_data_dict, **content_data}
                    except (json.JSONDecodeError, TypeError):
                        pass  # 如果解析失败，继续使用原始数据
            
            # 生成上下文字符串（用于AI提示词）
            outline_context = json.dumps(outline_data_dict, ensure_ascii=False, indent=2)
        else:
            outline_context = str(outline_data_dict)
            
    except Exception as e:
        # 如果解析失败，返回原始数据
        outline_context = str(outline_data) if isinstance(outline_data, str) else json.dumps(outline_data, ensure_ascii=False)
        outline_data_dict = None
    
    return outline_data_dict, outline_context


def extract_chapters_from_outline(outline_data_dict: Optional[dict]) -> list:
    """
    从大纲数据中提取章节列表
    
    :param outline_data_dict: 解析后的大纲字典
    :return: 章节列表
    """
    if not outline_data_dict or not isinstance(outline_data_dict, dict):
        return []
    
    # 直接查找 chapters
    if 'chapters' in outline_data_dict:
        chapters = outline_data_dict['chapters']
        if isinstance(chapters, list):
            return chapters
    
    return []
