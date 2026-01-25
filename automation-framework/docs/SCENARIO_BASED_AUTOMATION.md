# 场景化自动化使用指南

## 概述

系统支持基于场景的自动化指令生成，可以根据特定场景（如微信聊天、浏览器登录等）自动生成优化的操作序列。

## 核心特性

1. **自然语言输入**：用户只需用自然语言描述任务
2. **场景自动识别**：系统自动识别任务场景类型
3. **场景化指令生成**：根据场景生成专业化的操作序列
4. **支持浏览器和桌面自动化**：统一接口，支持两种自动化方式

## 支持的场景

### 1. 微信聊天场景 (wechat_chat)

**适用场景**：
- 自动发送消息给联系人
- 自动回复消息
- 群聊消息管理
- 文件/图片发送

**示例**：
```python
# 自然语言输入
task = "给张三发送消息：你好，今天天气不错"

# 系统自动生成：
# 1. 打开微信
# 2. 查找联系人"张三"
# 3. 发送消息"你好，今天天气不错"
```

**常用操作**：
- `OpenWeChat`: 打开微信
- `FindContact`: 查找联系人
- `SendMessage`: 发送消息
- `WaitForMessage`: 等待接收消息
- `SendFile`: 发送文件
- `SendImage`: 发送图片
- `GetChatHistory`: 获取聊天记录

### 2. 浏览器登录场景 (browser_login)

**适用场景**：
- 自动登录网站
- 处理验证码
- 登录状态验证

**示例**：
```python
task = "登录 https://example.com，账号是admin，密码是123456，如果有验证码就自动处理"
```

### 3. 浏览器数据采集场景 (browser_scraping)

**适用场景**：
- 网页数据抓取
- 批量数据采集
- 分页数据处理

**示例**：
```python
task = "采集 https://example.com/products 页面的所有商品名称和价格"
```

### 4. 桌面文件操作场景 (desktop_file)

**适用场景**：
- 文件管理
- 批量文件操作
- 文件整理

**示例**：
```python
task = "在桌面创建一个名为'项目文档'的文件夹，然后把所有.docx文件移动进去"
```

## 使用方法

### 方法1：通过API创建任务（推荐）

```python
# 创建任务时直接使用自然语言
POST /api/automation/tasks
{
    "name": "微信自动回复",
    "description": "给张三发送消息：你好",
    "driver_type": "desktop",  # 可选，系统会自动识别
    "natural_language": "给张三发送消息：你好，今天天气不错"
}
```

系统会自动：
1. 识别场景类型（微信聊天）
2. 生成操作序列
3. 创建任务并准备执行

### 方法2：使用Agent类

```python
from automation_framework.src.ai.agent import Agent
from automation_framework.src.ai.config import ModelConfig

# 创建Agent
llm_config = ModelConfig(
    provider="openai",
    model="gpt-4",
    api_key="your-api-key"
)

agent = Agent(llm_config, enable_scenario=True)

# 执行任务
result = await agent.execute_task(
    "给张三发送消息：你好，今天天气不错"
)

print(result)
# {
#     "scenario_type": "wechat_chat",
#     "scenario_name": "微信聊天",
#     "driver_type": "desktop",
#     "plan": [
#         {"action": "OpenWeChat", "params": {}, ...},
#         {"action": "FindContact", "params": {"contact_name": "张三"}, ...},
#         {"action": "SendMessage", "params": {"message": "你好，今天天气不错", "contact_name": "张三"}, ...}
#     ],
#     "status": "planned"
# }
```

### 方法3：手动指定场景

```python
from automation_framework.src.ai.scenario_planner import ScenarioType

result = await agent.execute_task(
    "发送消息给张三",
    scenario_type=ScenarioType.WECHAT_CHAT
)
```

## 微信聊天场景详细示例

### 示例1：发送消息给联系人

```python
task = "给张三发送消息：你好，今天天气不错"

# 系统生成的指令序列：
[
    {
        "action": "OpenWeChat",
        "params": {},
        "description": "打开微信应用"
    },
    {
        "action": "FindContact",
        "params": {"contact_name": "张三", "search_type": "name"},
        "description": "查找联系人张三"
    },
    {
        "action": "SendMessage",
        "params": {
            "message": "你好，今天天气不错",
            "contact_name": "张三"
        },
        "description": "发送消息给张三"
    }
]
```

### 示例2：群聊消息

```python
task = "在'项目组'群里发送消息：明天开会"

# 系统生成的指令序列：
[
    {
        "action": "OpenWeChat",
        "params": {},
        "description": "打开微信应用"
    },
    {
        "action": "FindGroup",
        "params": {"group_name": "项目组"},
        "description": "查找群聊'项目组'"
    },
    {
        "action": "SendMessage",
        "params": {
            "message": "明天开会",
            "group_name": "项目组"
        },
        "description": "在群里发送消息"
    }
]
```

### 示例3：发送文件

```python
task = "给张三发送文件：C:/documents/report.pdf"

# 系统生成的指令序列：
[
    {
        "action": "OpenWeChat",
        "params": {},
        "description": "打开微信应用"
    },
    {
        "action": "FindContact",
        "params": {"contact_name": "张三"},
        "description": "查找联系人张三"
    },
    {
        "action": "SendFile",
        "params": {
            "file_path": "C:/documents/report.pdf",
            "contact_name": "张三"
        },
        "description": "发送文件给张三"
    }
]
```

### 示例4：等待并回复消息

```python
task = "等待张三发消息，如果收到'你好'就回复'你好，有什么可以帮你的吗？'"

# 系统生成的指令序列：
[
    {
        "action": "OpenWeChat",
        "params": {},
        "description": "打开微信应用"
    },
    {
        "action": "FindContact",
        "params": {"contact_name": "张三"},
        "description": "查找联系人张三"
    },
    {
        "action": "WaitForMessage",
        "params": {
            "contact_name": "张三",
            "message_filter": "你好",
            "timeout": 60000
        },
        "description": "等待张三发送包含'你好'的消息"
    },
    {
        "action": "SendMessage",
        "params": {
            "message": "你好，有什么可以帮你的吗？",
            "contact_name": "张三"
        },
        "description": "回复消息"
    }
]
```

## 场景识别规则

系统通过关键词自动识别场景：

| 场景类型 | 关键词 |
|---------|--------|
| 微信聊天 | 微信、wechat、聊天、发送消息、群聊 |
| 浏览器登录 | 登录、login、登陆、账号、密码 |
| 浏览器数据采集 | 采集、爬取、抓取、scraping、数据 |
| 桌面文件操作 | 文件、文件夹、复制、移动、删除、file、folder |
| 桌面应用操作 | 打开、应用、程序、app、application |

## 扩展场景

### 添加自定义场景

```python
from automation_framework.src.ai.scenario_planner import ScenarioPlanner, ScenarioType, ScenarioTemplate

# 创建自定义场景模板
custom_template = ScenarioTemplate(
    scenario_type=ScenarioType.GENERIC,
    name="自定义场景",
    description="自定义场景描述",
    driver_type="desktop",
    common_actions=["操作1", "操作2"],
    prompt_template="自定义提示词模板：{task_description}"
)

# 注册场景
planner = ScenarioPlanner(llm)
planner.SCENARIO_TEMPLATES[ScenarioType.GENERIC] = custom_template
```

## 最佳实践

1. **明确描述任务**：使用清晰的自然语言描述，包含关键信息
   - ✅ 好："给张三发送消息：你好"
   - ❌ 差："发送消息"

2. **指定关键参数**：在描述中包含必要的参数
   - ✅ 好："在'项目组'群里发送消息：明天开会"
   - ❌ 差："发送消息"

3. **使用场景关键词**：在描述中使用场景相关的关键词，帮助系统识别
   - ✅ 好："微信给张三发送消息"
   - ❌ 差："发送消息给张三"（可能被识别为其他场景）

4. **处理异常情况**：在描述中说明如何处理异常
   - ✅ 好："登录网站，如果有验证码就自动处理"
   - ❌ 差："登录网站"

## 注意事项

1. **微信自动化限制**：
   - 需要微信客户端已安装
   - 需要微信已登录
   - 某些操作可能需要管理员权限

2. **场景识别准确性**：
   - 如果自动识别不准确，可以手动指定场景类型
   - 复杂任务建议分步骤描述

3. **操作执行顺序**：
   - 系统会按照生成的顺序执行操作
   - 某些操作可能需要等待时间

4. **错误处理**：
   - 如果操作失败，系统会尝试重新规划
   - 建议在任务描述中包含错误处理策略

## 技术实现

### 架构流程

```
用户输入自然语言
    ↓
场景识别（ScenarioPlanner.detect_scenario）
    ↓
场景化规划（ScenarioPlanner.plan_with_scenario）
    ↓
LLM生成操作序列
    ↓
转换为Action对象
    ↓
TaskExecutor执行
```

### 关键组件

1. **ScenarioPlanner**：场景规划器
   - 场景识别
   - 场景化指令生成
   - 场景模板管理

2. **Agent**：智能代理
   - 集成场景规划器
   - 任务执行协调

3. **TaskExecutor**：任务执行器
   - 执行操作序列
   - 状态管理
   - 错误处理

## 常见问题

**Q: 如何知道系统识别到了哪个场景？**
A: 查看返回结果中的 `scenario_type` 和 `scenario_name` 字段。

**Q: 可以同时使用多个场景吗？**
A: 目前不支持，一个任务只能使用一个场景。复杂任务建议拆分为多个子任务。

**Q: 如何添加新的场景类型？**
A: 参考 `ScenarioPlanner.SCENARIO_TEMPLATES` 的定义，添加新的场景模板。

**Q: 场景识别失败怎么办？**
A: 系统会回退到通用规划器，仍然可以生成操作序列，但可能不够优化。

## 更新日志

- 2026-01-24: 初始版本，支持微信聊天、浏览器登录等场景
