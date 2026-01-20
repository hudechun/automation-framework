# 本地智能体开发规范

## 一、概述

本文档定义了如何开发自定义智能体（Agent），包括接口规范、开发流程和最佳实践。

---

## 二、智能体基类

### BaseAgent接口定义

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class BaseAgent(ABC):
    """
    智能体基类 - 所有自定义智能体必须继承此类
    """
    
    # 必须定义的类属性
    agent_id: str           # 智能体唯一标识
    name: str              # 智能体名称
    version: str           # 版本号
    description: str       # 描述
    agent_type: str        # 类型：shopping/scraping/monitoring/analysis
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化智能体
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.memory = []  # 对话记忆
        self.context = {}  # 执行上下文
        
    @abstractmethod
    async def understand_task(self, task_description: str) -> Dict[str, Any]:
        """
        理解任务并生成执行计划
        
        Args:
            task_description: 任务描述（自然语言）
            
        Returns:
            执行计划字典，必须包含：
            {
                "task_type": "browser" | "desktop",
                "platforms": ["platform1", "platform2"],
                "actions": [action1, action2, ...],
                "parallel": True | False,
                "expected_data": ["field1", "field2"]
            }
        """
        pass
    
    @abstractmethod
    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行计划
        
        Args:
            plan: 执行计划
            
        Returns:
            执行结果
        """
        pass
    
    async def on_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        错误处理（可选重写）
        
        Args:
            error: 错误对象
            context: 错误上下文
            
        Returns:
            恢复策略或错误信息
        """
        return {
            "success": False,
            "error": str(error),
            "recovery_strategy": None
        }
    
    async def validate_result(self, result: Dict[str, Any]) -> bool:
        """
        验证结果（可选重写）
        
        Args:
            result: 执行结果
            
        Returns:
            是否有效
        """
        return True
    
    def get_capabilities(self) -> List[str]:
        """
        获取智能体能力列表（可选重写）
        
        Returns:
            能力列表
        """
        return []
    
    def get_required_plugins(self) -> List[str]:
        """
        获取所需插件列表（可选重写）
        
        Returns:
            插件名称列表
        """
        return []
```

---

## 三、开发示例

### 示例1：价格比较智能体

```python
from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..ai.llm import QwenLLM
import json

class PriceComparisonAgent(BaseAgent):
    """价格比较智能体"""
    
    # 类属性
    agent_id = "price_comparison_agent"
    name = "价格比较助手"
    version = "1.0.0"
    description = "比较多个电商平台的商品价格"
    agent_type = "shopping"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.llm = QwenLLM(
            api_key=config.get("qwen_api_key"),
            model=config.get("model", "qwen-max")
        )
        self.supported_platforms = [
            "jd.com",
            "taobao.com",
            "tmall.com",
            "pinduoduo.com",
            "suning.com"
        ]
    
    async def understand_task(self, task_description: str) -> Dict[str, Any]:
        """
        理解任务并生成执行计划
        
        示例输入：
        "比较京东和淘宝的iPhone 15价格"
        
        示例输出：
        {
            "task_type": "browser",
            "product": "iPhone 15",
            "platforms": ["jd.com", "taobao.com"],
            "actions": [...],
            "parallel": True,
            "expected_data": ["price", "title", "shop"]
        }
        """
        # 构造提示词
        prompt = f"""
        分析以下电商价格比较任务，提取关键信息：
        
        任务：{task_description}
        
        支持的平台：{', '.join(self.supported_platforms)}
        
        请以JSON格式返回：
        {{
            "product": "商品名称",
            "platforms": ["平台1", "平台2"],
            "price_range": "价格范围（如果有）",
            "other_requirements": "其他要求"
        }}
        """
        
        # 调用LLM理解任务
        response = await self.llm.generate(prompt)
        task_info = self._parse_json(response)
        
        # 生成执行计划
        plan = {
            "task_type": "browser",
            "product": task_info["product"],
            "platforms": task_info["platforms"],
            "parallel": True,
            "sub_tasks": []
        }
        
        # 为每个平台生成子任务
        for platform in task_info["platforms"]:
            sub_task = await self._generate_platform_task(
                platform, 
                task_info["product"]
            )
            plan["sub_tasks"].append(sub_task)
        
        # 添加聚合步骤
        plan["aggregation"] = {
            "type": "price_comparison",
            "output_format": "table"
        }
        
        return plan
    
    async def _generate_platform_task(
        self, 
        platform: str, 
        product: str
    ) -> Dict[str, Any]:
        """为特定平台生成任务"""
        
        # 平台特定的配置
        platform_configs = {
            "jd.com": {
                "url": "https://www.jd.com",
                "search_selector": "#key",
                "search_button": ".button",
                "price_selector": ".p-price",
                "title_selector": ".p-name"
            },
            "taobao.com": {
                "url": "https://www.taobao.com",
                "search_selector": "#q",
                "search_button": ".btn-search",
                "price_selector": ".price",
                "title_selector": ".title"
            }
        }
        
        config = platform_configs.get(platform, {})
        
        return {
            "platform": platform,
            "actions": [
                {
                    "type": "goto",
                    "url": config["url"]
                },
                {
                    "type": "fill",
                    "selector": config["search_selector"],
                    "value": product
                },
                {
                    "type": "click",
                    "selector": config["search_button"]
                },
                {
                    "type": "wait_for_selector",
                    "selector": config["price_selector"],
                    "timeout": 5000
                },
                {
                    "type": "extract",
                    "fields": {
                        "price": config["price_selector"],
                        "title": config["title_selector"],
                        "platform": platform
                    }
                }
            ]
        }
    
    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行计划（由框架调用浏览器自动化引擎）
        
        注意：此方法通常由框架自动调用，Agent只需生成计划
        """
        # 框架会自动执行plan中的actions
        # Agent可以在这里添加额外的逻辑
        return {
            "success": True,
            "message": "计划已生成，等待执行"
        }
    
    async def on_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """错误处理"""
        error_type = type(error).__name__
        
        # 根据错误类型提供恢复策略
        if "TimeoutError" in error_type:
            return {
                "success": False,
                "error": "页面加载超时",
                "recovery_strategy": {
                    "action": "retry",
                    "max_attempts": 3,
                    "delay": 2000
                }
            }
        elif "ElementNotFound" in error_type:
            return {
                "success": False,
                "error": "元素未找到",
                "recovery_strategy": {
                    "action": "use_alternative_selector",
                    "fallback": "vision_model"
                }
            }
        else:
            return {
                "success": False,
                "error": str(error),
                "recovery_strategy": None
            }
    
    def get_capabilities(self) -> List[str]:
        """获取能力列表"""
        return [
            "multi_platform_search",
            "price_extraction",
            "price_comparison",
            "parallel_execution"
        ]
    
    def get_required_plugins(self) -> List[str]:
        """获取所需插件"""
        return [
            "price_extractor",
            "data_analyzer"
        ]
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        """从文本中提取JSON"""
        import re
        
        # 尝试直接解析
        try:
            return json.loads(text)
        except:
            pass
        
        # 提取代码块
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        
        # 提取{}内容
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        
        raise ValueError("无法解析JSON")
```

### 示例2：数据爬取智能体

```python
class WebScrapingAgent(BaseAgent):
    """数据爬取智能体"""
    
    agent_id = "web_scraping_agent"
    name = "数据爬取助手"
    version = "1.0.0"
    description = "智能爬取网页数据"
    agent_type = "scraping"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.llm = QwenLLM(config.get("qwen_api_key"))
    
    async def understand_task(self, task_description: str) -> Dict[str, Any]:
        """
        理解爬取任务
        
        示例输入：
        "爬取豆瓣电影Top250的所有电影信息"
        """
        prompt = f"""
        分析以下数据爬取任务：
        
        任务：{task_description}
        
        请分析：
        1. 目标网站URL
        2. 需要爬取的数据字段
        3. 是否有分页
        4. 数据保存格式
        
        以JSON格式返回。
        """
        
        response = await self.llm.generate(prompt)
        task_info = self._parse_json(response)
        
        # 生成爬取计划
        plan = {
            "task_type": "browser",
            "target_url": task_info["url"],
            "data_fields": task_info["fields"],
            "pagination": task_info.get("pagination", False),
            "actions": await self._generate_scraping_actions(task_info)
        }
        
        return plan
    
    async def _generate_scraping_actions(self, task_info: Dict) -> List[Dict]:
        """生成爬取操作序列"""
        actions = [
            {"type": "goto", "url": task_info["url"]},
            {"type": "wait_for_selector", "selector": ".item"},
        ]
        
        # 如果有分页
        if task_info.get("pagination"):
            actions.append({
                "type": "loop",
                "condition": "has_next_page",
                "actions": [
                    {"type": "extract_list", "selector": ".item"},
                    {"type": "click", "selector": ".next-page"}
                ]
            })
        else:
            actions.append({
                "type": "extract_list",
                "selector": ".item",
                "fields": task_info["fields"]
            })
        
        return actions
    
    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "计划已生成"}
    
    def get_capabilities(self) -> List[str]:
        return [
            "page_analysis",
            "data_extraction",
            "pagination_handling",
            "data_cleaning"
        ]
```

---

## 四、注册和使用

### 注册智能体

```python
# agents/__init__.py
from .price_comparison_agent import PriceComparisonAgent
from .web_scraping_agent import WebScrapingAgent

# 智能体注册表
AGENT_REGISTRY = {
    "price_comparison_agent": PriceComparisonAgent,
    "web_scraping_agent": WebScrapingAgent,
}

def get_agent(agent_id: str, config: Dict = None):
    """获取智能体实例"""
    agent_class = AGENT_REGISTRY.get(agent_id)
    if not agent_class:
        raise ValueError(f"Agent {agent_id} not found")
    return agent_class(config)
```

### 使用智能体

```python
# 创建智能体实例
agent = get_agent("price_comparison_agent", {
    "qwen_api_key": "your-api-key",
    "model": "qwen-max"
})

# 理解任务
plan = await agent.understand_task("比较京东和淘宝的iPhone 15价格")

# 执行任务（由框架自动执行）
result = await framework.execute_plan(plan)
```

---

## 五、最佳实践

### 1. 提示词工程

```python
# 好的提示词示例
prompt = f"""
你是一个专业的电商价格分析助手。

任务：{task_description}

请分析任务并提取以下信息：
1. 商品名称（必须）
2. 需要比较的平台（必须）
3. 价格范围（可选）
4. 其他筛选条件（可选）

返回JSON格式：
{{
    "product": "商品名称",
    "platforms": ["平台1", "平台2"],
    "price_range": {{"min": 0, "max": 10000}},
    "filters": {{"brand": "品牌", "model": "型号"}}
}}

注意：
- 平台名称必须是完整域名（如jd.com）
- 价格范围单位为元
- 如果没有明确要求，返回null
"""
```

### 2. 错误处理

```python
async def on_error(self, error: Exception, context: Dict) -> Dict:
    """完善的错误处理"""
    
    # 记录错误
    self.log_error(error, context)
    
    # 分类处理
    if isinstance(error, TimeoutError):
        return self._handle_timeout(context)
    elif isinstance(error, ElementNotFoundError):
        return self._handle_element_not_found(context)
    elif isinstance(error, NetworkError):
        return self._handle_network_error(context)
    else:
        return self._handle_unknown_error(error, context)
```

### 3. 结果验证

```python
async def validate_result(self, result: Dict) -> bool:
    """验证结果完整性"""
    
    # 检查必需字段
    required_fields = ["price", "title", "platform"]
    for field in required_fields:
        if field not in result:
            return False
    
    # 检查数据有效性
    if not isinstance(result["price"], (int, float)):
        return False
    
    if result["price"] <= 0:
        return False
    
    return True
```

---

## 六、测试

### 单元测试示例

```python
import pytest
from agents import PriceComparisonAgent

@pytest.mark.asyncio
async def test_understand_task():
    """测试任务理解"""
    agent = PriceComparisonAgent({
        "qwen_api_key": "test-key"
    })
    
    plan = await agent.understand_task(
        "比较京东和淘宝的iPhone 15价格"
    )
    
    assert plan["task_type"] == "browser"
    assert "jd.com" in plan["platforms"]
    assert "taobao.com" in plan["platforms"]
    assert plan["parallel"] == True

@pytest.mark.asyncio
async def test_error_handling():
    """测试错误处理"""
    agent = PriceComparisonAgent()
    
    result = await agent.on_error(
        TimeoutError("Page load timeout"),
        {"url": "https://jd.com"}
    )
    
    assert result["success"] == False
    assert result["recovery_strategy"]["action"] == "retry"
```

---

## 七、部署

### 配置文件

```json
{
  "agent_id": "price_comparison_agent",
  "config": {
    "qwen_api_key": "${QWEN_API_KEY}",
    "model": "qwen-max",
    "max_retries": 3,
    "timeout": 30000,
    "supported_platforms": [
      "jd.com",
      "taobao.com",
      "tmall.com"
    ]
  }
}
```

### 环境变量

```bash
export QWEN_API_KEY="your-api-key"
export AGENT_LOG_LEVEL="INFO"
export AGENT_MAX_CONCURRENT=5
```

---

## 八、文档要求

每个智能体必须包含：

1. **README.md**：功能说明、使用示例
2. **CHANGELOG.md**：版本更新记录
3. **API文档**：方法说明、参数定义
4. **测试用例**：单元测试、集成测试

---

## 九、提交规范

### 目录结构

```
agents/
├── __init__.py
├── base_agent.py
├── price_comparison_agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── README.md
│   ├── config.example.json
│   └── tests/
│       └── test_agent.py
└── web_scraping_agent/
    ├── __init__.py
    ├── agent.py
    ├── README.md
    └── tests/
```

### 代码规范

- 遵循PEP 8
- 类型注解
- 文档字符串
- 单元测试覆盖率 > 80%

---

## 十、常见问题

**Q: 如何调试智能体？**
A: 使用日志记录和断点调试，查看LLM返回的原始响应。

**Q: 如何优化LLM调用成本？**
A: 缓存常见任务的执行计划，减少重复调用。

**Q: 如何处理平台反爬虫？**
A: 使用代理、延迟、User-Agent轮换等策略。

**Q: 智能体可以调用其他智能体吗？**
A: 可以，通过Agent Router实现智能体协作。
