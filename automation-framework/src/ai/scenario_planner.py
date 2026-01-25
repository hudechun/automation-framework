"""
场景化任务规划器 - 支持特定场景的指令生成（如微信聊天、浏览器自动化等）
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .llm import LLMProvider
from .agent import TaskPlanner, TaskDescription


class ScenarioType(str, Enum):
    """场景类型"""
    WECHAT_CHAT = "wechat_chat"  # 微信聊天
    WECHAT_GROUP = "wechat_group"  # 微信群聊
    BROWSER_LOGIN = "browser_login"  # 浏览器登录
    BROWSER_SCRAPING = "browser_scraping"  # 浏览器数据采集
    DESKTOP_FILE = "desktop_file"  # 桌面文件操作
    DESKTOP_APP = "desktop_app"  # 桌面应用操作
    GENERIC = "generic"  # 通用场景


@dataclass
class ScenarioTemplate:
    """场景模板"""
    scenario_type: ScenarioType
    name: str
    description: str
    driver_type: str  # "browser" or "desktop"
    common_actions: List[str]  # 常用操作列表
    prompt_template: str  # LLM提示词模板


class ScenarioPlanner:
    """
    场景化任务规划器 - 根据场景类型生成特定指令
    """
    
    # 预定义场景模板
    SCENARIO_TEMPLATES = {
        ScenarioType.WECHAT_CHAT: ScenarioTemplate(
            scenario_type=ScenarioType.WECHAT_CHAT,
            name="微信聊天",
            description="自动化微信聊天场景，支持发送消息、接收消息、查找联系人等",
            driver_type="desktop",
            common_actions=[
                "打开微信",
                "查找联系人",
                "发送消息",
                "接收消息",
                "发送文件",
                "发送图片",
                "查看聊天记录"
            ],
            prompt_template="""你是一个微信自动化专家。根据用户需求生成微信聊天自动化指令。

用户需求：{task_description}

请生成微信自动化操作序列，包括：
1. 打开微信应用
2. 查找目标联系人/群聊
3. 执行聊天操作（发送消息、接收消息等）
4. 处理可能的异常情况（如联系人不存在、消息发送失败等）

可用操作类型：
- OpenApp: 打开应用（如微信）
- FindElement: 查找元素（如联系人、群聊）
- Click: 点击操作
- Type: 输入文本
- SendMessage: 发送消息（微信专用）
- WaitForMessage: 等待接收消息（微信专用）
- SendFile: 发送文件（微信专用）
- SendImage: 发送图片（微信专用）

返回JSON格式的操作序列：
[
    {{
        "action": "<action_type>",
        "params": {{"<key>": "<value>"}},
        "description": "<操作描述>"
    }}
]"""
        ),
        
        ScenarioType.BROWSER_LOGIN: ScenarioTemplate(
            scenario_type=ScenarioType.BROWSER_LOGIN,
            name="浏览器登录",
            description="自动化浏览器登录场景，支持各种登录方式",
            driver_type="browser",
            common_actions=[
                "打开登录页面",
                "输入账号密码",
                "处理验证码",
                "点击登录",
                "验证登录状态"
            ],
            prompt_template="""你是一个浏览器自动化专家。根据用户需求生成浏览器登录自动化指令。

用户需求：{task_description}

请生成浏览器登录操作序列，包括：
1. 打开登录页面
2. 输入账号和密码
3. 处理验证码（如果有）
4. 点击登录按钮
5. 验证登录是否成功

可用操作类型：
- GoToURL: 打开URL
- Type: 输入文本
- Click: 点击按钮
- WaitForElement: 等待元素出现
- Screenshot: 截图（用于验证码识别）
- HandleCaptcha: 处理验证码

返回JSON格式的操作序列。"""
        ),
        
        ScenarioType.BROWSER_SCRAPING: ScenarioTemplate(
            scenario_type=ScenarioType.BROWSER_SCRAPING,
            name="浏览器数据采集",
            description="自动化浏览器数据采集场景",
            driver_type="browser",
            common_actions=[
                "打开目标页面",
                "等待内容加载",
                "提取数据",
                "处理分页",
                "保存数据"
            ],
            prompt_template="""你是一个数据采集专家。根据用户需求生成浏览器数据采集自动化指令。

用户需求：{task_description}

请生成数据采集操作序列，包括：
1. 打开目标页面
2. 等待内容加载
3. 提取所需数据
4. 处理分页（如果有）
5. 保存数据

返回JSON格式的操作序列。"""
        ),
        
        ScenarioType.DESKTOP_FILE: ScenarioTemplate(
            scenario_type=ScenarioType.DESKTOP_FILE,
            name="桌面文件操作",
            description="自动化桌面文件操作场景",
            driver_type="desktop",
            common_actions=[
                "打开文件管理器",
                "创建文件夹",
                "复制文件",
                "移动文件",
                "删除文件",
                "重命名文件"
            ],
            prompt_template="""你是一个桌面自动化专家。根据用户需求生成桌面文件操作自动化指令。

用户需求：{task_description}

请生成文件操作序列，包括：
1. 打开文件管理器
2. 导航到目标目录
3. 执行文件操作（创建、复制、移动、删除等）

返回JSON格式的操作序列。"""
        ),
    }
    
    def __init__(self, llm: LLMProvider, base_planner: Optional[TaskPlanner] = None):
        """
        初始化场景规划器
        
        Args:
            llm: 大语言模型提供者
            base_planner: 基础任务规划器（可选）
        """
        self.llm = llm
        self.base_planner = base_planner or TaskPlanner(llm)
    
    def detect_scenario(self, natural_language: str) -> Optional[ScenarioType]:
        """
        检测任务场景类型
        
        Args:
            natural_language: 自然语言任务描述
            
        Returns:
            场景类型，如果无法识别则返回None
        """
        text_lower = natural_language.lower()
        
        # 微信相关关键词
        if any(keyword in text_lower for keyword in ["微信", "wechat", "聊天", "发送消息", "群聊"]):
            if "群" in text_lower or "group" in text_lower:
                return ScenarioType.WECHAT_GROUP
            return ScenarioType.WECHAT_CHAT
        
        # 浏览器登录相关
        if any(keyword in text_lower for keyword in ["登录", "login", "登陆", "账号", "密码"]):
            return ScenarioType.BROWSER_LOGIN
        
        # 浏览器数据采集相关
        if any(keyword in text_lower for keyword in ["采集", "爬取", "抓取", "scraping", "数据"]):
            return ScenarioType.BROWSER_SCRAPING
        
        # 桌面文件操作相关
        if any(keyword in text_lower for keyword in ["文件", "文件夹", "复制", "移动", "删除", "file", "folder"]):
            return ScenarioType.DESKTOP_FILE
        
        # 桌面应用操作相关
        if any(keyword in text_lower for keyword in ["打开", "应用", "程序", "app", "application"]):
            return ScenarioType.DESKTOP_APP
        
        return None
    
    async def plan_with_scenario(
        self,
        natural_language: str,
        scenario_type: Optional[ScenarioType] = None
    ) -> Dict[str, Any]:
        """
        使用场景化模板生成执行计划
        
        Args:
            natural_language: 自然语言任务描述
            scenario_type: 场景类型（如果为None则自动检测）
            
        Returns:
            包含场景信息和操作序列的字典
        """
        # 自动检测场景类型
        if scenario_type is None:
            scenario_type = self.detect_scenario(natural_language)
        
        # 如果没有检测到场景，使用通用规划器
        if scenario_type is None or scenario_type == ScenarioType.GENERIC:
            task_desc = await self.base_planner.parse_task(natural_language)
            plan = await self.base_planner.plan(task_desc)
            return {
                "scenario_type": ScenarioType.GENERIC.value,
                "driver_type": "browser",  # 默认浏览器
                "plan": plan,
                "task_description": task_desc
            }
        
        # 获取场景模板
        template = self.SCENARIO_TEMPLATES.get(scenario_type)
        if not template:
            # 如果模板不存在，回退到通用规划器
            task_desc = await self.base_planner.parse_task(natural_language)
            plan = await self.base_planner.plan(task_desc)
            return {
                "scenario_type": scenario_type.value,
                "driver_type": "browser",
                "plan": plan,
                "task_description": task_desc
            }
        
        # 使用场景模板生成计划
        prompt = template.prompt_template.format(task_description=natural_language)
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.chat(messages)
        
        # 解析响应
        import json
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            plan = json.loads(json_str)
            
            # 解析任务描述
            task_desc = await self.base_planner.parse_task(natural_language)
            
            return {
                "scenario_type": scenario_type.value,
                "scenario_name": template.name,
                "driver_type": template.driver_type,
                "plan": plan,
                "task_description": task_desc,
                "common_actions": template.common_actions
            }
        except Exception as e:
            print(f"Failed to parse scenario plan: {e}")
            # 回退到基础规划器
            task_desc = await self.base_planner.parse_task(natural_language)
            plan = await self.base_planner.plan(task_desc)
            return {
                "scenario_type": scenario_type.value,
                "driver_type": template.driver_type,
                "plan": plan,
                "task_description": task_desc
            }
    
    def get_scenario_info(self, scenario_type: ScenarioType) -> Optional[Dict[str, Any]]:
        """
        获取场景信息
        
        Args:
            scenario_type: 场景类型
            
        Returns:
            场景信息字典
        """
        template = self.SCENARIO_TEMPLATES.get(scenario_type)
        if not template:
            return None
        
        return {
            "type": scenario_type.value,
            "name": template.name,
            "description": template.description,
            "driver_type": template.driver_type,
            "common_actions": template.common_actions
        }
    
    def list_scenarios(self) -> List[Dict[str, Any]]:
        """
        列出所有可用场景
        
        Returns:
            场景列表
        """
        return [
            self.get_scenario_info(scenario_type)
            for scenario_type in self.SCENARIO_TEMPLATES.keys()
        ]
