# 模板上传修复和AI模型配置快速指南

## 问题1: 模板上传404错误 ✅ 已修复

### 修复内容
修改了 `RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/thesis/template/list.vue`

**修改点：**
1. 添加了上传URL变量：
   ```javascript
   const uploadUrl = ref(import.meta.env.VITE_APP_BASE_API + '/upload')
   const templateUploadUrl = ref(import.meta.env.VITE_APP_BASE_API + '/thesis/template/upload')
   ```

2. 修改了两个上传组件的action属性：
   - 缩略图上传：`action="/api/upload"` → `:action="uploadUrl"`
   - 模板文件上传：`action="/api/thesis/template/upload"` → `:action="templateUploadUrl"`

### 验证方法
1. 刷新前端页面
2. 进入"论文系统" → "模板管理"
3. 点击"上传模板"按钮
4. 选择Word文档上传
5. 应该不再出现404错误

---

## 问题2: AI模型配置功能

### 第一步：创建数据库表（立即执行）

使用MySQL客户端工具执行：
```
RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/ai_model_schema.sql
```

这将：
1. 创建 `ai_write_ai_model_config` 表
2. 初始化8个预设AI模型：
   - OpenAI GPT-4
   - OpenAI GPT-3.5 Turbo
   - Claude 3 Opus
   - 通义千问 Turbo
   - DeepSeek Chat
   - 文心一言 4.0
   - 智谱 GLM-4
   - Moonshot AI (Kimi)

### 第二步：配置AI模型（通过数据库）

#### 方法1: 直接更新API Key（最快）

```sql
-- 配置OpenAI GPT-4（示例）
UPDATE ai_write_ai_model_config 
SET api_key = 'sk-your-openai-api-key-here',
    is_enabled = '1',
    is_default = '1',
    update_time = NOW()
WHERE model_code = 'openai' AND model_version = 'gpt-4';

-- 配置通义千问（示例）
UPDATE ai_write_ai_model_config 
SET api_key = 'your-qwen-api-key-here',
    is_enabled = '1',
    update_time = NOW()
WHERE model_code = 'qwen' AND model_version = 'qwen-turbo';
```

#### 方法2: 查看所有预设模型

```sql
SELECT 
    config_id,
    model_name,
    model_code,
    model_version,
    CASE WHEN api_key != '' THEN '已配置' ELSE '未配置' END AS key_status,
    is_enabled,
    is_default,
    priority,
    remark
FROM ai_write_ai_model_config
WHERE del_flag = '0'
ORDER BY priority DESC;
```

### 第三步：验证配置

```sql
-- 查看已启用的模型
SELECT 
    model_name,
    model_version,
    is_default,
    priority
FROM ai_write_ai_model_config
WHERE is_enabled = '1' AND del_flag = '0'
ORDER BY priority DESC;

-- 查看默认模型
SELECT 
    model_name,
    model_version,
    api_base_url
FROM ai_write_ai_model_config
WHERE is_default = '1' AND is_enabled = '1' AND del_flag = '0';
```

---

## 临时使用方案（在前端界面完成前）

### 配置步骤

1. **选择要使用的AI模型**
   - 推荐：DeepSeek Chat（性价比最高）
   - 或者：通义千问 Turbo（中文优化）
   - 或者：OpenAI GPT-3.5 Turbo（稳定可靠）

2. **获取API Key**
   - DeepSeek: https://platform.deepseek.com/
   - 通义千问: https://dashscope.aliyun.com/
   - OpenAI: https://platform.openai.com/

3. **配置到数据库**
   ```sql
   -- 示例：配置DeepSeek
   UPDATE ai_write_ai_model_config 
   SET api_key = 'sk-your-deepseek-key',
       is_enabled = '1',
       is_default = '1',
       update_time = NOW()
   WHERE model_code = 'deepseek';
   ```

4. **重启后端服务**
   ```bash
   # 停止服务
   # Ctrl+C
   
   # 启动服务
   cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
   python app.py
   ```

---

## 后续开发计划

### 前端管理界面（待开发）

将创建以下页面和功能：

1. **AI模型配置页面** (`src/views/thesis/ai-model/config.vue`)
   - 模型列表展示（卡片式）
   - 添加/编辑模型
   - 启用/禁用开关
   - 设置默认模型
   - 测试连接功能
   - API Key安全显示

2. **菜单项**
   - 路径：论文系统 → AI模型配置
   - 权限：thesis:ai-model:list

3. **API接口** (`src/api/thesis/aiModel.js`)
   - listAiModel - 获取模型列表
   - getAiModel - 获取模型详情
   - addAiModel - 添加模型
   - updateAiModel - 更新模型
   - deleteAiModel - 删除模型
   - enableAiModel - 启用模型
   - disableAiModel - 禁用模型
   - setDefaultAiModel - 设置默认
   - testAiModel - 测试连接

### 后端实现（待开发）

1. **数据模型**
   - `entity/do/ai_model_do.py` - 数据库模型
   - `entity/vo/ai_model_vo.py` - 视图模型

2. **业务层**
   - `dao/ai_model_dao.py` - 数据访问
   - `service/ai_model_service.py` - 业务逻辑
   - `controller/ai_model_controller.py` - 接口控制器

3. **集成到论文生成**
   - 修改 `service/thesis_service.py`
   - 使用配置的AI模型生成内容
   - 支持模型切换和降级

---

## 当前状态

### ✅ 已完成
1. 模板上传路径修复
2. AI模型配置表创建
3. 预设8个常用AI模型
4. 数据库初始化SQL

### 🔄 进行中
1. 通过SQL配置AI模型（临时方案）

### 📋 待开发
1. 前端管理界面
2. 后端API接口
3. 集成到论文生成流程

---

## 快速测试

### 测试模板上传
1. 刷新前端页面
2. 进入"模板管理"
3. 点击"上传模板"
4. 上传Word文档
5. 检查是否成功

### 测试AI模型配置
1. 执行 `ai_model_schema.sql`
2. 配置一个模型的API Key
3. 查询验证配置成功
4. 等待后端集成后测试论文生成

---

## 相关文件

### 已修改
- `ruoyi-fastapi-frontend/src/views/thesis/template/list.vue` - 修复上传路径

### 已创建
- `ruoyi-fastapi-backend/sql/ai_model_schema.sql` - AI模型表结构和初始数据
- `.kiro/specs/ai-thesis-writing/UPLOAD_AND_AI_MODEL_FIX.md` - 详细实现方案
- `.kiro/specs/ai-thesis-writing/UPLOAD_FIX_AND_AI_MODEL_QUICK_START.md` - 本文档

### 待创建（后续开发）
- `module_thesis/entity/do/ai_model_do.py`
- `module_thesis/entity/vo/ai_model_vo.py`
- `module_thesis/dao/ai_model_dao.py`
- `module_thesis/service/ai_model_service.py`
- `module_thesis/controller/ai_model_controller.py`
- `ruoyi-fastapi-frontend/src/api/thesis/aiModel.js`
- `ruoyi-fastapi-frontend/src/views/thesis/ai-model/config.vue`

---

## 下一步行动

1. **立即执行**：
   - ✅ 刷新前端，测试模板上传
   - 📋 执行 `ai_model_schema.sql`
   - 📋 配置一个AI模型的API Key

2. **短期计划**（1-2天）：
   - 开发后端AI模型管理API
   - 开发前端AI模型配置界面
   - 集成到论文生成流程

3. **长期优化**：
   - 添加模型使用统计
   - 实现智能模型选择
   - 支持模型负载均衡
   - 添加成本控制功能
