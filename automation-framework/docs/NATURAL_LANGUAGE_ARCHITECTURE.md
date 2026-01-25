# 自然语言自动化架构说明

## 系统概述

本系统支持通过自然语言描述任务，自动利用大语言模型解析成可执行的指令序列。无论是浏览器自动化还是桌面自动化，都使用统一的自然语言接口。

## 核心设计理念

1. **自然语言输入**：用户只需用自然语言描述任务，无需编写代码
2. **场景自动识别**：系统自动识别任务场景（如微信聊天、浏览器登录等）
3. **场景化指令生成**：根据场景生成专业化的操作序列
4. **统一执行接口**：浏览器和桌面自动化使用相同的接口和流程

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    用户输入层                            │
│  "给张三发送消息：你好" 或 "登录网站，账号admin"        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 场景识别层                               │
│  ScenarioPlanner.detect_scenario()                       │
│  - 分析关键词                                            │
│  - 识别场景类型（微信/浏览器登录/数据采集等）            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 场景化规划层                             │
│  ScenarioPlanner.plan_with_scenario()                   │
│  - 获取场景模板                                          │
│  - 生成LLM提示词                                         │
│  - LLM生成操作序列                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 操作转换层                               │
│  ActionSerializer                                      │
│  - JSON → Action对象                                     │
│  - 验证参数                                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 任务执行层                               │
│  TaskExecutor                                            │
│  - 创建会话                                              │
│  - 创建驱动（Browser/Desktop）                           │
│  - 按顺序执行操作                                        │
└─────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. ScenarioPlanner（场景规划器）

**位置**：`automation-framework/src/ai/scenario_planner.py`

**功能**：
- 场景识别：通过关键词自动识别场景类型
- 场景化规划：使用场景模板生成优化的操作序列
- 场景模板管理：管理预定义的场景模板

**关键方法**：
- `detect_scenario(natural_language)`: 检测场景类型
- `plan_with_scenario(natural_language, scenario_type)`: 生成场景化计划
- `get_scenario_info(scenario_type)`: 获取场景信息
- `list_scenarios()`: 列出所有可用场景

### 2. Agent（智能代理）

**位置**：`automation-framework/src/ai/agent.py`

**功能**：
- 集成场景规划器
- 任务执行协调
- 记忆管理

**关键方法**：
- `execute_task(task, context, scenario_type)`: 执行任务（支持场景化）

### 3. 微信专用操作

**位置**：`automation-framework/src/core/wechat_actions.py`

**操作类型**：
- `OpenWeChat`: 打开微信
- `FindContact`: 查找联系人
- `FindGroup`: 查找群聊
- `SendMessage`: 发送消息
- `WaitForMessage`: 等待消息
- `SendFile`: 发送文件
- `SendImage`: 发送图片
- `GetChatHistory`: 获取聊天记录

### 4. Windows驱动增强

**位置**：`automation-framework/src/drivers/windows_driver.py`

**新增功能**：
- 支持微信专用操作的执行
- 微信窗口查找和操作
- 联系人/群聊查找
- 消息发送和接收

## 数据流

### 1. 自然语言输入 → 场景识别

```
输入: "给张三发送消息：你好"
    ↓
关键词匹配: "发送消息" → 微信场景
    ↓
场景类型: ScenarioType.WECHAT_CHAT
```

### 2. 场景识别 → 场景化规划

```
场景类型: WECHAT_CHAT
    ↓
获取场景模板（微信聊天模板）
    ↓
生成LLM提示词（包含微信专用操作说明）
    ↓
LLM生成操作序列
```

### 3. 操作序列 → Action对象

```
LLM返回JSON:
[
    {"action": "OpenWeChat", "params": {}},
    {"action": "FindContact", "params": {"contact_name": "张三"}},
    {"action": "SendMessage", "params": {"message": "你好", "contact_name": "张三"}}
]
    ↓
ActionSerializer反序列化
    ↓
Action对象列表:
[OpenWeChat(), FindContact("张三"), SendMessage("你好", "张三")]
```

### 4. Action对象 → 执行

```
TaskExecutor
    ↓
创建Session
    ↓
创建Driver（根据driver_type: desktop）
    ↓
按顺序执行Action
    ↓
WindowsDriver.execute_action()
    ↓
调用对应的处理方法（_handle_open_wechat, _handle_find_contact等）
```

## 使用示例

### 完整流程示例

```python
# 1. 用户输入自然语言
task_description = "给张三发送消息：你好，今天天气不错"

# 2. 创建Agent（启用场景化）
agent = Agent(llm_config, enable_scenario=True)

# 3. 执行任务（自动识别场景并生成计划）
result = await agent.execute_task(task_description)

# 结果：
# {
#     "scenario_type": "wechat_chat",
#     "scenario_name": "微信聊天",
#     "driver_type": "desktop",
#     "plan": [
#         {"action": "OpenWeChat", ...},
#         {"action": "FindContact", "params": {"contact_name": "张三"}, ...},
#         {"action": "SendMessage", "params": {"message": "你好，今天天气不错", ...}, ...}
#     ]
# }

# 4. 创建任务
task = await task_manager.create_task(
    name="微信自动发送消息",
    description=task_description,
    driver_type=result["driver_type"],
    actions=result["plan"]
)

# 5. 执行任务
executor = TaskExecutor()
await executor.execute_task(task.id)
```

## 场景模板系统

### 场景模板结构

```python
ScenarioTemplate(
    scenario_type=ScenarioType.WECHAT_CHAT,
    name="微信聊天",
    description="自动化微信聊天场景",
    driver_type="desktop",
    common_actions=["打开微信", "查找联系人", "发送消息", ...],
    prompt_template="你是一个微信自动化专家。根据用户需求生成微信聊天自动化指令。..."
)
```

### 添加新场景

1. 定义场景类型（在 `ScenarioType` 枚举中添加）
2. 创建场景模板（添加到 `ScenarioPlanner.SCENARIO_TEMPLATES`）
3. 更新场景识别逻辑（在 `detect_scenario` 方法中添加关键词）
4. 创建专用操作（如果需要，如微信操作）

## 扩展性

### 1. 添加新场景

参考 `ScenarioPlanner.SCENARIO_TEMPLATES` 的定义，添加新的场景模板。

### 2. 添加新操作

1. 在 `actions.py` 或创建新的操作文件（如 `wechat_actions.py`）中定义操作类
2. 在对应的驱动中实现处理方法
3. 在 `action_serializer.py` 中注册操作类

### 3. 自定义场景识别

重写 `ScenarioPlanner.detect_scenario` 方法，实现自定义的场景识别逻辑。

## 技术栈

- **LLM**: OpenAI GPT-4 / Qwen / 其他支持的模型
- **浏览器自动化**: Playwright
- **桌面自动化**: pywinauto (Windows)
- **任务管理**: SQLAlchemy (ORM)
- **API框架**: FastAPI

## 性能考虑

1. **LLM调用**：场景化规划需要调用LLM，建议使用高性能模型
2. **操作执行**：某些操作可能需要等待时间，系统会自动处理
3. **并发控制**：多用户执行任务时，系统会确保不冲突

## 安全考虑

1. **敏感信息**：账号密码等敏感信息不应直接写在自然语言描述中
2. **权限控制**：桌面自动化可能需要管理员权限
3. **操作验证**：重要操作建议添加确认机制

## 未来改进

1. **更多场景支持**：钉钉、企业微信、QQ等
2. **场景组合**：支持多场景组合的任务
3. **智能优化**：根据执行结果自动优化操作序列
4. **可视化编辑**：支持可视化编辑生成的操作序列

## 相关文档

- [场景化自动化使用指南](./SCENARIO_BASED_AUTOMATION.md)
- [自然语言任务创建指南](./NATURAL_LANGUAGE_TASK_GUIDE.md)
- [快速开始指南](./QUICK_START_SCENARIO.md)
