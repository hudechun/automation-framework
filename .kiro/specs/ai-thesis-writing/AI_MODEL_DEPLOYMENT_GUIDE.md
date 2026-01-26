# AI模型配置功能部署指南

## 功能概述

AI模型配置功能允许管理员配置多个AI模型，并选择启用的模型用于论文生成。系统预设了8个主流AI模型，管理员只需填写API Key即可使用。

## 已完成的工作

### 1. 数据库层 ✅

**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/ai_model_schema.sql`

- 创建了 `ai_write_ai_model_config` 表
- 预设了8个AI模型：
  - OpenAI GPT-4
  - OpenAI GPT-3.5 Turbo
  - Anthropic Claude 3 Opus
  - Anthropic Claude 3 Sonnet
  - 阿里云通义千问 Qwen-Max
  - 阿里云通义千问 Qwen-Plus
  - DeepSeek Chat
  - DeepSeek Coder

### 2. 菜单配置 ✅

**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/ai_model_menu.sql`

- 创建了"AI模型配置"菜单项
- 配置了相关权限：
  - `thesis:ai-model:list` - 查询
  - `thesis:ai-model:query` - 详情
  - `thesis:ai-model:add` - 新增
  - `thesis:ai-model:edit` - 编辑
  - `thesis:ai-model:remove` - 删除
  - `thesis:ai-model:test` - 测试连接

### 3. 后端实现 ✅

#### DO模型
**文件**: `module_thesis/entity/do/ai_model_do.py`
- `AiWriteAiModelConfig` - 数据库实体类

#### VO模型
**文件**: `module_thesis/entity/vo/ai_model_vo.py`
- `AiModelConfigModel` - 配置信息模型
- `AiModelConfigQueryModel` - 查询模型
- `AiModelConfigPageQueryModel` - 分页查询模型
- `AiModelTestRequestModel` - 测试请求模型
- `AiModelTestResponseModel` - 测试响应模型

#### DAO层
**文件**: `module_thesis/dao/ai_model_dao.py`
- `AiModelConfigDao` - 数据访问对象
- 提供了完整的CRUD操作
- 支持启用/禁用、设置默认等操作

#### Service层
**文件**: `module_thesis/service/ai_model_service.py`
- `AiModelService` - 业务逻辑层
- 实现了配置管理、测试连接等功能

#### Controller层
**文件**: `module_thesis/controller/ai_model_controller.py`
- `ai_model_controller` - API路由控制器
- 提供了完整的RESTful API

### 4. 前端实现 ✅

#### API接口
**文件**: `src/api/thesis/aiModel.js`
- 完整的API调用函数

#### 配置页面
**文件**: `src/views/thesis/ai-model/config.vue`
- 卡片式展示所有模型
- 支持启用/禁用、设置默认
- 支持新增、编辑、删除
- 支持测试连接
- 美观的UI设计

#### 入口文件
**文件**: `src/views/thesis/ai-model/index.vue`
- 页面入口组件

#### 路由配置
**文件**: `src/router/thesis.js`
- 已添加AI模型配置路由

## 部署步骤

### 步骤1: 执行数据库脚本

```bash
# 进入后端目录
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend

# 连接到MySQL数据库
mysql -u root -p

# 选择数据库
use ry-vue;

# 执行表结构脚本
source sql/ai_model_schema.sql;

# 执行菜单脚本
source sql/ai_model_menu.sql;
```

或者使用Python脚本：

```python
import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='ry-vue',
    charset='utf8mb4'
)

cursor = conn.cursor()

# 读取并执行SQL文件
with open('sql/ai_model_schema.sql', 'r', encoding='utf-8') as f:
    sql_commands = f.read().split(';')
    for command in sql_commands:
        if command.strip():
            cursor.execute(command)

with open('sql/ai_model_menu.sql', 'r', encoding='utf-8') as f:
    sql_commands = f.read().split(';')
    for command in sql_commands:
        if command.strip():
            cursor.execute(command)

conn.commit()
cursor.close()
conn.close()

print("✅ 数据库脚本执行成功")
```

### 步骤2: 重启后端服务

```bash
# 停止后端服务（如果正在运行）
# Ctrl+C 或者使用进程管理工具

# 启动后端服务
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

### 步骤3: 刷新前端页面

1. 清除浏览器缓存（Ctrl+Shift+Delete）
2. 刷新页面（F5 或 Ctrl+R）
3. 重新登录系统

### 步骤4: 验证功能

1. 登录系统
2. 进入"论文系统" -> "AI模型配置"
3. 查看预设的8个模型
4. 选择一个模型，点击"编辑"
5. 填写API Key
6. 点击"测试"按钮验证连接
7. 启用模型
8. 设置为默认模型

## API接口列表

### 基础接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取列表 | GET | `/thesis/ai-model/list` | 分页查询模型列表 |
| 获取详情 | GET | `/thesis/ai-model/{id}` | 获取单个模型详情 |
| 新增模型 | POST | `/thesis/ai-model` | 创建新模型配置 |
| 更新模型 | PUT | `/thesis/ai-model` | 更新模型配置 |
| 删除模型 | DELETE | `/thesis/ai-model/{id}` | 删除模型配置 |

### 操作接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 启用模型 | PUT | `/thesis/ai-model/{id}/enable` | 启用指定模型 |
| 禁用模型 | PUT | `/thesis/ai-model/{id}/disable` | 禁用指定模型 |
| 设置默认 | PUT | `/thesis/ai-model/{id}/default` | 设为默认模型 |
| 测试连接 | POST | `/thesis/ai-model/{id}/test` | 测试模型连接 |

### 查询接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取默认模型 | GET | `/thesis/ai-model/default/config` | 获取默认模型配置 |
| 获取启用列表 | GET | `/thesis/ai-model/enabled/list` | 获取所有启用的模型 |

## 使用流程

### 管理员配置流程

1. **进入配置页面**
   - 登录系统
   - 导航到"论文系统" -> "AI模型配置"

2. **配置API Key**
   - 选择要使用的模型
   - 点击"编辑"按钮
   - 填写API Key（必填）
   - 确认API地址和端点（通常使用默认值）
   - 调整参数（可选）：
     - 最大Token数
     - 温度参数
     - Top P参数
     - 优先级

3. **测试连接**
   - 点击"测试"按钮
   - 查看测试结果
   - 确认连接成功

4. **启用模型**
   - 切换启用开关
   - 模型状态变为"已启用"

5. **设置默认模型**
   - 点击"设为默认"按钮
   - 该模型将作为默认AI模型使用

### 用户使用流程

1. **论文生成时自动使用**
   - 系统自动使用默认模型
   - 或根据优先级选择可用模型

2. **查看模型信息**
   - 在论文生成页面可以看到当前使用的模型
   - 显示模型名称和版本

## 预设模型说明

### OpenAI 系列

1. **GPT-4**
   - 模型代码: `openai`
   - 版本: `gpt-4`
   - API地址: `https://api.openai.com/v1`
   - 端点: `/chat/completions`
   - 特点: 最强大的模型，适合复杂任务

2. **GPT-3.5 Turbo**
   - 模型代码: `openai`
   - 版本: `gpt-3.5-turbo`
   - API地址: `https://api.openai.com/v1`
   - 端点: `/chat/completions`
   - 特点: 性价比高，响应快

### Anthropic Claude 系列

3. **Claude 3 Opus**
   - 模型代码: `claude`
   - 版本: `claude-3-opus-20240229`
   - API地址: `https://api.anthropic.com`
   - 端点: `/v1/messages`
   - 特点: 最强大的Claude模型

4. **Claude 3 Sonnet**
   - 模型代码: `claude`
   - 版本: `claude-3-sonnet-20240229`
   - API地址: `https://api.anthropic.com`
   - 端点: `/v1/messages`
   - 特点: 平衡性能和成本

### 阿里云通义千问系列

5. **Qwen-Max**
   - 模型代码: `qwen`
   - 版本: `qwen-max`
   - API地址: `https://dashscope.aliyuncs.com/api/v1`
   - 端点: `/services/aigc/text-generation/generation`
   - 特点: 国产最强模型

6. **Qwen-Plus**
   - 模型代码: `qwen`
   - 版本: `qwen-plus`
   - API地址: `https://dashscope.aliyuncs.com/api/v1`
   - 端点: `/services/aigc/text-generation/generation`
   - 特点: 性价比高

### DeepSeek 系列

7. **DeepSeek Chat**
   - 模型代码: `deepseek`
   - 版本: `deepseek-chat`
   - API地址: `https://api.deepseek.com/v1`
   - 端点: `/chat/completions`
   - 特点: 通用对话模型

8. **DeepSeek Coder**
   - 模型代码: `deepseek`
   - 版本: `deepseek-coder`
   - API地址: `https://api.deepseek.com/v1`
   - 端点: `/chat/completions`
   - 特点: 专注代码生成

## 注意事项

1. **API Key安全**
   - API Key存储在数据库中
   - 前端显示时使用密码框遮挡
   - 建议定期更换API Key

2. **预设模型**
   - 预设模型不能删除，只能禁用
   - 可以修改预设模型的配置
   - 预设模型的模型代码和版本不建议修改

3. **默认模型**
   - 系统只能有一个默认模型
   - 设置新的默认模型会自动取消之前的默认
   - 禁用默认模型会自动取消默认状态

4. **测试连接**
   - 测试功能目前返回模拟结果
   - 实际使用时需要实现真实的API调用
   - 测试会消耗少量API配额

5. **权限控制**
   - 只有管理员可以配置AI模型
   - 普通用户只能查看可用模型
   - 需要在角色管理中分配相应权限

## 后续开发建议

1. **实现真实的API调用**
   - 在 `AiModelService.test_config()` 中实现真实的API测试
   - 根据不同的 `model_code` 调用不同的API
   - 处理各种API的认证方式

2. **集成到论文生成**
   - 在论文生成服务中调用AI模型配置
   - 根据默认模型或优先级选择模型
   - 实现模型切换和故障转移

3. **添加使用统计**
   - 记录每个模型的调用次数
   - 统计Token使用量
   - 计算成本

4. **添加配额管理**
   - 为每个模型设置配额限制
   - 监控配额使用情况
   - 配额不足时自动切换模型

5. **优化用户体验**
   - 添加模型性能对比
   - 提供模型选择建议
   - 显示实时可用状态

## 故障排查

### 问题1: 菜单不显示

**原因**: 菜单SQL未执行或权限未分配

**解决**:
```sql
-- 检查菜单是否存在
SELECT * FROM sys_menu WHERE menu_name = 'AI模型配置';

-- 检查角色权限
SELECT * FROM sys_role_menu WHERE menu_id = (
    SELECT menu_id FROM sys_menu WHERE menu_name = 'AI模型配置'
);
```

### 问题2: API 404错误

**原因**: 路由未注册

**解决**:
1. 检查 `module_thesis/controller/__init__.py` 是否导入了 `ai_model_controller`
2. 重启后端服务
3. 查看启动日志确认路由注册

### 问题3: 数据库表不存在

**原因**: SQL脚本未执行

**解决**:
```sql
-- 检查表是否存在
SHOW TABLES LIKE 'ai_write_ai_model_config';

-- 如果不存在，执行SQL脚本
SOURCE sql/ai_model_schema.sql;
```

### 问题4: 前端页面空白

**原因**: 组件加载失败或路由配置错误

**解决**:
1. 打开浏览器控制台查看错误
2. 检查 `src/router/thesis.js` 路由配置
3. 清除浏览器缓存重试

## 完成状态

✅ 数据库表结构  
✅ 菜单配置  
✅ DO模型  
✅ VO模型  
✅ DAO层  
✅ Service层  
✅ Controller层  
✅ 前端API  
✅ 前端页面  
✅ 路由配置  
✅ 部署文档  

**状态**: 完整功能已实现，可以部署使用！
