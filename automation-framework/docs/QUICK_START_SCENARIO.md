# 场景化自动化快速开始

## 概述

本指南演示如何使用自然语言创建自动化任务，系统会自动识别场景并生成优化的操作序列。

## 快速示例

### 示例1：微信自动发送消息

**步骤1：解析自然语言任务**

```http
POST /dev-api/automation/task/parse
Content-Type: application/json

{
    "description": "给张三发送消息：你好，今天天气不错"
}
```

**步骤2：查看解析结果**

系统返回：
- 场景类型：`wechat_chat`（微信聊天）
- 驱动类型：`desktop`（桌面自动化）
- 操作序列：3个操作（打开微信、查找联系人、发送消息）

**步骤3：创建并执行任务**

使用返回的 `actions` 创建任务，然后执行。

### 示例2：浏览器自动登录

**输入**：
```json
{
    "description": "登录 https://example.com，账号是admin，密码是123456，如果有验证码就自动处理"
}
```

**系统自动**：
1. 识别场景：`browser_login`（浏览器登录）
2. 生成操作序列：打开URL → 输入账号 → 输入密码 → 处理验证码 → 点击登录
3. 驱动类型：`browser`（浏览器自动化）

## 完整工作流程

### 1. 自然语言输入

用户只需用自然语言描述任务，例如：
- "给张三发送消息：你好"
- "登录网站，账号admin，密码123456"
- "在'项目组'群里发送消息：明天开会"

### 2. 场景自动识别

系统通过关键词自动识别场景：
- 包含"微信"、"聊天" → 微信聊天场景
- 包含"登录"、"账号" → 浏览器登录场景
- 包含"采集"、"爬取" → 数据采集场景

### 3. 生成操作序列

系统使用场景模板和LLM生成操作序列：
- 微信场景：使用微信专用操作（OpenWeChat, FindContact, SendMessage等）
- 浏览器场景：使用浏览器通用操作（GoToURL, Type, Click等）

### 4. 执行任务

TaskExecutor按照生成的序列执行操作。

## 支持的场景

### 微信聊天场景

**关键词**：微信、wechat、聊天、发送消息、群聊

**示例任务**：
- "给张三发送消息：你好"
- "在'项目组'群里发送消息：明天开会"
- "给张三发送文件：C:/documents/report.pdf"
- "等待张三发消息，如果收到'你好'就回复'你好'"

**生成的专用操作**：
- `OpenWeChat`: 打开微信
- `FindContact`: 查找联系人
- `FindGroup`: 查找群聊
- `SendMessage`: 发送消息
- `SendFile`: 发送文件
- `SendImage`: 发送图片
- `WaitForMessage`: 等待消息
- `GetChatHistory`: 获取聊天记录

### 浏览器登录场景

**关键词**：登录、login、登陆、账号、密码

**示例任务**：
- "登录 https://example.com，账号admin，密码123456"
- "登录网站，如果有验证码就自动处理"

**生成的通用操作**：
- `GoToURL`: 打开登录页面
- `Type`: 输入账号密码
- `HandleCaptcha`: 处理验证码
- `Click`: 点击登录按钮

### 浏览器数据采集场景

**关键词**：采集、爬取、抓取、scraping、数据

**示例任务**：
- "采集 https://example.com/products 页面的所有商品名称和价格"

### 桌面文件操作场景

**关键词**：文件、文件夹、复制、移动、删除

**示例任务**：
- "在桌面创建一个名为'项目文档'的文件夹，然后把所有.docx文件移动进去"

## API使用示例

### Python示例

```python
import requests

# 1. 解析自然语言任务
response = requests.post(
    "http://localhost:9099/dev-api/automation/task/parse",
    json={
        "description": "给张三发送消息：你好，今天天气不错"
    },
    headers={"Authorization": "Bearer your-token"}
)

result = response.json()
print(f"场景类型: {result['data']['scenario_type']}")
print(f"操作数量: {result['data']['total_actions']}")

# 2. 创建任务
task_response = requests.post(
    "http://localhost:9099/dev-api/automation/task",
    json={
        "name": "微信自动发送消息",
        "description": "给张三发送消息：你好，今天天气不错",
        "taskType": result['data']['driver_type'],
        "actions": result['data']['actions']
    },
    headers={"Authorization": "Bearer your-token"}
)

task_id = task_response.json()['data']['id']

# 3. 执行任务
execute_response = requests.post(
    f"http://localhost:9099/dev-api/automation/task/{task_id}/execute",
    headers={"Authorization": "Bearer your-token"}
)
```

### JavaScript示例

```javascript
// 1. 解析自然语言任务
const parseResponse = await fetch('/dev-api/automation/task/parse', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token'
    },
    body: JSON.stringify({
        description: '给张三发送消息：你好，今天天气不错'
    })
});

const parseResult = await parseResponse.json();
console.log('场景类型:', parseResult.data.scenario_type);
console.log('操作数量:', parseResult.data.total_actions);

// 2. 创建任务
const taskResponse = await fetch('/dev-api/automation/task', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token'
    },
    body: JSON.stringify({
        name: '微信自动发送消息',
        description: '给张三发送消息：你好，今天天气不错',
        taskType: parseResult.data.driver_type,
        actions: parseResult.data.actions
    })
});

const task = await taskResponse.json();
const taskId = task.data.id;

// 3. 执行任务
await fetch(`/dev-api/automation/task/${taskId}/execute`, {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer your-token'
    }
});
```

## 注意事项

1. **LLM配置**：确保已配置有效的LLM模型
2. **微信自动化**：需要微信客户端已安装并登录
3. **场景识别**：如果自动识别不准确，可以手动指定场景
4. **操作执行**：某些操作可能需要等待时间，系统会自动处理

## 更多信息

- 详细文档：[场景化自动化使用指南](./SCENARIO_BASED_AUTOMATION.md)
- 自然语言任务指南：[自然语言任务创建指南](./NATURAL_LANGUAGE_TASK_GUIDE.md)
- API文档：http://localhost:9099/dev-api/docs
