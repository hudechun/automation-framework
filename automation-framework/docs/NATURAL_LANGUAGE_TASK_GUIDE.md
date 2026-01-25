# 自然语言任务创建指南

## 概述

系统支持通过自然语言描述任务，自动利用大语言模型解析成可执行的指令序列。无论是浏览器自动化还是桌面自动化，都可以使用自然语言输入。

## 核心流程

```
用户输入自然语言
    ↓
场景识别（自动检测场景类型）
    ↓
场景化规划（使用场景模板生成指令）
    ↓
LLM解析生成操作序列
    ↓
转换为Action对象
    ↓
创建任务并执行
```

## 使用方式

### 方式1：通过API接口（推荐）

#### 1. 解析自然语言任务

```http
POST /dev-api/automation/task/parse
Content-Type: application/json

{
    "description": "给张三发送消息：你好，今天天气不错"
}
```

**响应示例**：
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "success": true,
        "scenario_type": "wechat_chat",
        "scenario_name": "微信聊天",
        "driver_type": "desktop",
        "task_description": {
            "goal": "给张三发送消息",
            "constraints": [],
            "parameters": {
                "contact": "张三",
                "message": "你好，今天天气不错"
            },
            "context": {}
        },
        "actions": [
            {
                "action": "OpenWeChat",
                "params": {},
                "description": "打开微信应用"
            },
            {
                "action": "FindContact",
                "params": {
                    "contact_name": "张三",
                    "search_type": "name"
                },
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
        ],
        "total_actions": 3,
        "common_actions": [
            "打开微信",
            "查找联系人",
            "发送消息",
            "接收消息",
            "发送文件",
            "发送图片",
            "查看聊天记录"
        ]
    }
}
```

#### 2. 创建任务

解析完成后，使用返回的 `actions` 创建任务：

```http
POST /dev-api/automation/task
Content-Type: application/json

{
    "name": "微信自动发送消息",
    "description": "给张三发送消息：你好，今天天气不错",
    "taskType": "desktop",
    "actions": [
        {
            "action": "OpenWeChat",
            "params": {}
        },
        {
            "action": "FindContact",
            "params": {
                "contact_name": "张三",
                "search_type": "name"
            }
        },
        {
            "action": "SendMessage",
            "params": {
                "message": "你好，今天天气不错",
                "contact_name": "张三"
            }
        }
    ],
    "config": {
        "driver_type": "desktop"
    }
}
```

### 方式2：直接创建任务（自动解析）

如果任务创建接口支持自然语言输入，可以直接传入：

```http
POST /dev-api/automation/task
Content-Type: application/json

{
    "name": "微信自动发送消息",
    "description": "给张三发送消息：你好，今天天气不错",
    "natural_language": "给张三发送消息：你好，今天天气不错",
    "taskType": "desktop"
}
```

系统会自动：
1. 识别场景（微信聊天）
2. 生成操作序列
3. 创建任务

## 场景示例

### 微信聊天场景

#### 示例1：发送消息给联系人

**输入**：
```
给张三发送消息：你好，今天天气不错
```

**生成的指令**：
1. 打开微信
2. 查找联系人"张三"
3. 发送消息"你好，今天天气不错"

#### 示例2：群聊消息

**输入**：
```
在'项目组'群里发送消息：明天开会
```

**生成的指令**：
1. 打开微信
2. 查找群聊"项目组"
3. 发送消息"明天开会"

#### 示例3：发送文件

**输入**：
```
给张三发送文件：C:/documents/report.pdf
```

**生成的指令**：
1. 打开微信
2. 查找联系人"张三"
3. 发送文件"C:/documents/report.pdf"

#### 示例4：发送图片

**输入**：
```
给张三发送图片：C:/images/photo.jpg
```

**生成的指令**：
1. 打开微信
2. 查找联系人"张三"
3. 发送图片"C:/images/photo.jpg"

#### 示例5：等待并回复消息

**输入**：
```
等待张三发消息，如果收到'你好'就回复'你好，有什么可以帮你的吗？'
```

**生成的指令**：
1. 打开微信
2. 查找联系人"张三"
3. 等待消息（过滤条件：包含"你好"）
4. 发送回复"你好，有什么可以帮你的吗？"

### 浏览器自动化场景

#### 示例1：登录网站

**输入**：
```
登录 https://example.com，账号是admin，密码是123456，如果有验证码就自动处理
```

**生成的指令**：
1. 打开URL: https://example.com
2. 输入账号"admin"
3. 输入密码"123456"
4. 检测验证码（如果有）
5. 处理验证码
6. 点击登录按钮
7. 验证登录状态

#### 示例2：数据采集

**输入**：
```
采集 https://example.com/products 页面的所有商品名称和价格
```

**生成的指令**：
1. 打开URL: https://example.com/products
2. 等待页面加载
3. 提取商品名称列表
4. 提取商品价格列表
5. 保存数据

### 桌面自动化场景

#### 示例1：文件操作

**输入**：
```
在桌面创建一个名为'项目文档'的文件夹，然后把所有.docx文件移动进去
```

**生成的指令**：
1. 打开文件管理器
2. 导航到桌面
3. 创建文件夹"项目文档"
4. 查找所有.docx文件
5. 移动文件到"项目文档"文件夹

## 场景识别规则

系统通过关键词自动识别场景：

| 场景 | 关键词 | 驱动类型 |
|------|--------|----------|
| 微信聊天 | 微信、wechat、聊天、发送消息、群聊 | desktop |
| 浏览器登录 | 登录、login、登陆、账号、密码 | browser |
| 浏览器数据采集 | 采集、爬取、抓取、scraping、数据 | browser |
| 桌面文件操作 | 文件、文件夹、复制、移动、删除 | desktop |
| 桌面应用操作 | 打开、应用、程序、app | desktop |

## 最佳实践

### 1. 明确描述任务

✅ **好的描述**：
- "给张三发送消息：你好"
- "登录 https://example.com，账号admin，密码123456"
- "在'项目组'群里发送消息：明天开会"

❌ **不好的描述**：
- "发送消息"（缺少关键信息）
- "登录"（缺少URL和账号密码）
- "处理文件"（太模糊）

### 2. 包含关键参数

在描述中包含所有必要的参数：
- 联系人/群聊名称
- 消息内容
- 文件路径
- URL地址
- 账号密码

### 3. 说明异常处理

在描述中说明如何处理异常情况：
- "如果有验证码就自动处理"
- "如果联系人不存在就跳过"
- "如果发送失败就重试3次"

### 4. 使用场景关键词

在描述中使用场景相关的关键词，帮助系统识别：
- "微信给张三发送消息"（明确指定微信）
- "浏览器登录网站"（明确指定浏览器）

## 技术实现

### 场景规划器工作流程

1. **场景检测** (`detect_scenario`)
   - 分析自然语言文本
   - 匹配关键词
   - 返回场景类型

2. **场景化规划** (`plan_with_scenario`)
   - 获取场景模板
   - 使用模板生成LLM提示词
   - LLM生成操作序列
   - 返回结构化计划

3. **操作转换**
   - 将LLM返回的JSON转换为Action对象
   - 验证操作参数
   - 创建任务

### 支持的Action类型

#### 微信专用操作
- `OpenWeChat`: 打开微信
- `FindContact`: 查找联系人
- `FindGroup`: 查找群聊
- `SendMessage`: 发送消息
- `WaitForMessage`: 等待消息
- `SendFile`: 发送文件
- `SendImage`: 发送图片
- `GetChatHistory`: 获取聊天记录

#### 浏览器通用操作
- `GoToURL`: 打开URL
- `Click`: 点击元素
- `Type`: 输入文本
- `WaitForElement`: 等待元素
- `GetText`: 获取文本
- `Screenshot`: 截图

#### 桌面通用操作
- `StartApp`: 启动应用
- `SwitchWindow`: 切换窗口
- `ClickCoordinate`: 坐标点击
- `Type`: 输入文本
- `Press`: 按键
- `PressCombo`: 组合键

## 注意事项

1. **微信自动化限制**：
   - 需要微信客户端已安装并登录
   - 某些操作可能需要管理员权限
   - UI结构可能因微信版本而异

2. **LLM配置**：
   - 需要配置有效的LLM模型
   - 建议使用GPT-4或类似的高性能模型
   - 确保API密钥有效

3. **场景识别准确性**：
   - 如果自动识别不准确，可以手动指定场景
   - 复杂任务建议分步骤描述

4. **操作执行顺序**：
   - 系统会按照生成的顺序执行操作
   - 某些操作可能需要等待时间
   - 建议在描述中说明等待条件

## 常见问题

**Q: 如何知道系统识别到了哪个场景？**
A: 查看解析接口返回的 `scenario_type` 和 `scenario_name` 字段。

**Q: 可以手动指定场景吗？**
A: 可以，在调用Agent时指定 `scenario_type` 参数。

**Q: 场景识别失败怎么办？**
A: 系统会回退到通用规划器，仍然可以生成操作序列。

**Q: 如何添加新的场景类型？**
A: 参考 `ScenarioPlanner.SCENARIO_TEMPLATES` 的定义，添加新的场景模板。

**Q: 生成的指令可以修改吗？**
A: 可以，在创建任务前可以手动编辑 `actions` 数组。

## 更新日志

- 2026-01-24: 初始版本，支持场景化自然语言任务创建
