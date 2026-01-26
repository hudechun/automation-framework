# 模板上传和AI模型配置功能实现方案

## 问题1: 模板上传404错误

### 问题描述
前端上传模板时报错：`POST http://localhost/api/upload 404 (Not Found)`

### 根本原因
前端代码中硬编码了 `/api/upload` 路径，但实际应该使用环境变量配置的基础路径 `/dev-api/upload`

### 解决方案

#### 修改文件
`RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/thesis/template/list.vue`

#### 修改内容
将所有硬编码的 `/api/` 路径改为使用环境变量：

```vue
<!-- 修改前 -->
<el-upload
  action="/api/upload"
  ...
/>

<el-upload
  action="/api/thesis/template/upload"
  ...
/>

<!-- 修改后 -->
<el-upload
  :action="uploadUrl"
  ...
/>

<el-upload
  :action="templateUploadUrl"
  ...
/>
```

在 `<script setup>` 中添加：
```javascript
// 上传地址
const uploadUrl = ref(import.meta.env.VITE_APP_BASE_API + '/upload')
const templateUploadUrl = ref(import.meta.env.VITE_APP_BASE_API + '/thesis/template/upload')
```

---

## 问题2: AI模型配置功能

### 需求描述
1. 支持配置多个AI模型（OpenAI、Claude、Qwen、DeepSeek等）
2. 预设常用模型，只需填写API Key即可启用
3. 支持启用/禁用模型
4. 支持设置默认模型
5. 支持测试模型连接

### 数据库设计

#### 创建AI模型配置表
```sql
CREATE TABLE ai_write_ai_model_config (
  config_id         BIGINT(20)      NOT NULL AUTO_INCREMENT    COMMENT '配置ID',
  model_name        VARCHAR(100)    NOT NULL                   COMMENT '模型名称',
  model_code        VARCHAR(50)     NOT NULL                   COMMENT '模型代码（openai/claude/qwen等）',
  model_version     VARCHAR(50)     NOT NULL                   COMMENT '模型版本（gpt-4/claude-3等）',
  
  api_key           VARCHAR(500)    DEFAULT ''                 COMMENT 'API密钥（加密存储）',
  api_base_url      VARCHAR(200)    DEFAULT ''                 COMMENT 'API基础URL',
  api_endpoint      VARCHAR(200)    DEFAULT ''                 COMMENT 'API端点',
  
  max_tokens        INT(11)         DEFAULT 4096               COMMENT '最大token数',
  temperature       DECIMAL(3,2)    DEFAULT 0.70               COMMENT '温度参数',
  top_p             DECIMAL(3,2)    DEFAULT 0.90               COMMENT 'Top P参数',
  
  is_enabled        CHAR(1)         DEFAULT '0'                COMMENT '是否启用（0否 1是）',
  is_default        CHAR(1)         DEFAULT '0'                COMMENT '是否默认（0否 1是）',
  is_preset         CHAR(1)         DEFAULT '0'                COMMENT '是否预设（0否 1是）',
  
  priority          INT(4)          DEFAULT 0                  COMMENT '优先级（数字越大越优先）',
  
  status            CHAR(1)         DEFAULT '0'                COMMENT '状态（0正常 1停用）',
  del_flag          CHAR(1)         DEFAULT '0'                COMMENT '删除标志（0存在 2删除）',
  create_by         VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       DATETIME                                   COMMENT '创建时间',
  update_by         VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       DATETIME                                   COMMENT '更新时间',
  remark            VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  
  PRIMARY KEY (config_id),
  UNIQUE KEY uk_model_version (model_code, model_version),
  INDEX idx_enabled (is_enabled, is_default),
  INDEX idx_status (status, del_flag)
) ENGINE=InnoDB AUTO_INCREMENT=100 COMMENT='AI模型配置表';
```

#### 初始化预设模型数据
```sql
-- OpenAI GPT-4
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint, 
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time)
VALUES 
('OpenAI GPT-4', 'openai', 'gpt-4', 'https://api.openai.com/v1', '/chat/completions',
 8192, 0.70, 0.90, '1', 100, '0', 'system', NOW());

-- OpenAI GPT-3.5 Turbo
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time)
VALUES 
('OpenAI GPT-3.5 Turbo', 'openai', 'gpt-3.5-turbo', 'https://api.openai.com/v1', '/chat/completions',
 4096, 0.70, 0.90, '1', 90, '0', 'system', NOW());

-- Claude 3 Opus
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time)
VALUES 
('Claude 3 Opus', 'claude', 'claude-3-opus-20240229', 'https://api.anthropic.com/v1', '/messages',
 4096, 0.70, 0.90, '1', 95, '0', 'system', NOW());

-- 通义千问
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time)
VALUES 
('通义千问 Turbo', 'qwen', 'qwen-turbo', 'https://dashscope.aliyuncs.com/api/v1', '/services/aigc/text-generation/generation',
 6000, 0.70, 0.90, '1', 85, '0', 'system', NOW());

-- DeepSeek
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time)
VALUES 
('DeepSeek Chat', 'deepseek', 'deepseek-chat', 'https://api.deepseek.com/v1', '/chat/completions',
 4096, 0.70, 0.90, '1', 80, '0', 'system', NOW());

-- 文心一言
INSERT INTO ai_write_ai_model_config 
(model_name, model_code, model_version, api_base_url, api_endpoint,
 max_tokens, temperature, top_p, is_preset, priority, status, create_by, create_time)
VALUES 
('文心一言 4.0', 'ernie', 'ernie-4.0', 'https://aip.baidubce.com/rpc/2.0', '/ai_custom/v1/wenxinworkshop/chat/completions_pro',
 2048, 0.70, 0.90, '1', 75, '0', 'system', NOW());
```

### 后端实现

#### 1. 创建数据模型
文件：`module_thesis/entity/do/ai_model_do.py`

#### 2. 创建VO模型
文件：`module_thesis/entity/vo/ai_model_vo.py`

#### 3. 创建DAO层
文件：`module_thesis/dao/ai_model_dao.py`

#### 4. 创建Service层
文件：`module_thesis/service/ai_model_service.py`
- 获取模型列表
- 添加/编辑/删除模型
- 启用/禁用模型
- 设置默认模型
- 测试模型连接
- 获取可用模型（用于论文生成）

#### 5. 创建Controller层
文件：`module_thesis/controller/ai_model_controller.py`
- GET /thesis/ai-model/list - 获取模型列表
- POST /thesis/ai-model - 添加模型
- PUT /thesis/ai-model - 更新模型
- DELETE /thesis/ai-model/{id} - 删除模型
- PUT /thesis/ai-model/{id}/enable - 启用模型
- PUT /thesis/ai-model/{id}/disable - 禁用模型
- PUT /thesis/ai-model/{id}/set-default - 设置为默认
- POST /thesis/ai-model/{id}/test - 测试连接

### 前端实现

#### 1. 创建API接口
文件：`src/api/thesis/aiModel.js`

#### 2. 创建管理页面
文件：`src/views/thesis/ai-model/config.vue`

功能：
- 模型列表展示（卡片式）
- 添加/编辑模型对话框
- 启用/禁用开关
- 设置默认模型
- 测试连接按钮
- API Key显示/隐藏切换

#### 3. 添加路由
文件：`src/router/thesis.js`

```javascript
{
  path: 'ai-model',
  name: 'ThesisAiModel',
  component: () => import('@/views/thesis/ai-model/config'),
  meta: { title: 'AI模型配置', icon: 'cpu' }
}
```

#### 4. 添加菜单
SQL：
```sql
INSERT INTO sys_menu VALUES (
  NULL, 'AI模型配置', 论文系统菜单ID, 6, 'ai-model', 
  'thesis/ai-model/config', NULL, 1, 0, 'C', '0', '0', 
  'thesis:ai-model:list', 'cpu', 'admin', NOW(), '', NULL, 
  'AI模型配置管理'
);
```

### UI设计

#### 模型卡片布局
```
┌─────────────────────────────────────┐
│ [图标] OpenAI GPT-4        [启用开关] │
│                                     │
│ 版本：gpt-4                         │
│ 状态：✓ 已配置  ⭐ 默认              │
│                                     │
│ [编辑] [测试连接] [设为默认]         │
└─────────────────────────────────────┘
```

#### 编辑对话框
```
┌─ 编辑AI模型 ──────────────────────┐
│                                   │
│ 模型名称：[OpenAI GPT-4        ]  │
│ 模型代码：[openai              ]  │
│ 模型版本：[gpt-4               ]  │
│                                   │
│ API Key：  [••••••••••••••••••] 👁 │
│ API URL：  [https://api.openai...] │
│                                   │
│ 最大Token：[8192               ]  │
│ 温度参数： [0.70               ]  │
│ Top P：    [0.90               ]  │
│                                   │
│ 优先级：   [100                ]  │
│ 备注：     [                   ]  │
│                                   │
│         [取消]  [保存]             │
└───────────────────────────────────┘
```

### 安全考虑

1. **API Key加密存储**
   - 使用AES加密存储API Key
   - 前端显示时脱敏（显示前4位和后4位）

2. **权限控制**
   - 只有管理员可以配置AI模型
   - 普通用户只能查看可用模型列表

3. **测试连接**
   - 测试时不保存API Key
   - 测试结果显示连接状态和响应时间

### 集成到论文生成

修改 `thesis_service.py`，使用配置的AI模型：

```python
async def generate_thesis_content(self, thesis_id: int):
    # 获取默认或优先级最高的可用模型
    model_config = await AiModelService.get_default_model()
    
    if not model_config:
        raise Exception("未配置可用的AI模型")
    
    # 使用配置的模型生成内容
    client = self._create_ai_client(model_config)
    response = await client.generate(...)
    
    return response
```

---

## 实施步骤

### 第一阶段：修复上传问题（立即）
1. 修改 `template/list.vue` 的上传路径
2. 测试模板上传功能

### 第二阶段：创建数据库表（立即）
1. 执行AI模型配置表创建SQL
2. 执行预设模型数据初始化SQL

### 第三阶段：后端实现（1-2小时）
1. 创建DO、VO模型
2. 创建DAO层
3. 创建Service层
4. 创建Controller层
5. 测试API接口

### 第四阶段：前端实现（1-2小时）
1. 创建API接口文件
2. 创建管理页面
3. 添加路由和菜单
4. 测试功能

### 第五阶段：集成测试（30分钟）
1. 配置一个AI模型
2. 测试论文生成功能
3. 验证模型切换

---

## 相关文件清单

### SQL文件
- `sql/ai_model_schema.sql` - 表结构
- `sql/ai_model_init_data.sql` - 初始化数据

### 后端文件
- `entity/do/ai_model_do.py`
- `entity/vo/ai_model_vo.py`
- `dao/ai_model_dao.py`
- `service/ai_model_service.py`
- `controller/ai_model_controller.py`

### 前端文件
- `api/thesis/aiModel.js`
- `views/thesis/ai-model/config.vue`
- `router/thesis.js` (修改)

### 修改文件
- `views/thesis/template/list.vue` (修复上传路径)
- `service/thesis_service.py` (集成AI模型)

---

## 预期效果

1. ✅ 模板上传功能正常工作
2. ✅ 可以配置多个AI模型
3. ✅ 可以启用/禁用模型
4. ✅ 可以设置默认模型
5. ✅ 可以测试模型连接
6. ✅ 论文生成使用配置的模型
7. ✅ API Key安全存储和显示
