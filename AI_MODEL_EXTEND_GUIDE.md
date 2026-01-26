# AI模型配置扩展完成指南

## 概述

已完成AI模型配置表的字段扩展，添加了模型类型（language/vision）和提供商（provider）字段，并更新了前后端代码以支持这些新字段。

## 已完成的工作

### 1. 数据库扩展 ✅

**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/extend_ai_model_fields.sql`

添加的字段：
- `model_type` VARCHAR(20): 模型类型（language/vision）
- `provider` VARCHAR(50): 提供商（openai/anthropic/qwen/custom）
- `params` TEXT: 模型参数JSON
- `capabilities` TEXT: 模型能力JSON

创建的索引：
- `idx_model_type`: 模型类型索引
- `idx_provider`: 提供商索引

### 2. 后端实体类更新 ✅

**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/entity/do/ai_model_do.py`

添加的字段映射：
```python
model_type: Mapped[str] = mapped_column(String(20), nullable=True, server_default='language', comment='模型类型')
provider: Mapped[str] = mapped_column(String(50), nullable=True, server_default="''", comment='提供商')
params: Mapped[str] = mapped_column(Text, nullable=True, comment='模型参数JSON')
capabilities: Mapped[str] = mapped_column(Text, nullable=True, comment='模型能力JSON')
```

### 3. 后端VO模型更新 ✅

**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/entity/vo/ai_model_vo.py`

更新内容：
- `AiModelConfigModel` 添加了 `model_type`, `provider`, `params`, `capabilities` 字段
- `AiModelConfigQueryModel` 添加了 `model_type`, `provider` 查询字段
- 支持按模型类型和提供商筛选

### 4. 前端编辑对话框更新 ✅

**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/thesis/ai-model/config.vue`

新增的表单字段：

#### 模型类型选择（单选框）
```vue
<el-form-item label="模型类型" prop="modelType">
  <el-radio-group v-model="form.modelType">
    <el-radio label="language">语言模型</el-radio>
    <el-radio label="vision">视觉模型</el-radio>
  </el-radio-group>
  <div style="color: #909399; font-size: 12px; margin-top: 4px;">
    语言模型用于文本生成、论文写作；视觉模型用于图像识别、验证码识别
  </div>
</el-form-item>
```

#### 提供商选择（下拉框）
```vue
<el-form-item label="提供商" prop="provider">
  <el-select v-model="form.provider" placeholder="请选择提供商" style="width: 100%">
    <el-option label="OpenAI" value="openai" />
    <el-option label="Anthropic (Claude)" value="anthropic" />
    <el-option label="Qwen (通义千问)" value="qwen" />
    <el-option label="自定义" value="custom" />
  </el-select>
</el-form-item>
```

#### 表单验证规则
```javascript
const rules = {
  modelType: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }],
  modelName: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  modelCode: [{ required: true, message: '请输入模型代码', trigger: 'blur' }],
  modelVersion: [{ required: true, message: '请输入模型版本', trigger: 'blur' }],
  apiBaseUrl: [{ required: true, message: '请输入API地址', trigger: 'blur' }]
}
```

#### 表单默认值
```javascript
const form = reactive({
  configId: null,
  modelType: 'language',      // 默认语言模型
  provider: 'openai',          // 默认OpenAI
  modelName: '',
  modelCode: '',
  modelVersion: '',
  // ... 其他字段
})
```

### 5. 前端卡片显示更新 ✅

卡片中已显示：
- **模型类型标签**: 蓝色标签显示"语言模型"，橙色标签显示"视觉模型"
- **提供商标签**: 显示提供商名称

```vue
<div class="info-row">
  <span class="label">模型类型：</span>
  <el-tag :type="model.modelType === 'language' ? 'primary' : 'warning'" size="small">
    {{ model.modelType === 'language' ? '语言模型' : '视觉模型' }}
  </el-tag>
</div>
<div class="info-row">
  <span class="label">提供商：</span>
  <el-tag size="small">{{ model.provider || model.modelCode }}</el-tag>
</div>
```

### 6. AI生成服务更新 ✅

**文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/service/ai_generation_service.py`

`_get_ai_provider` 方法已支持 `model_type` 参数：
```python
@staticmethod
async def _get_ai_provider(
    query_db: AsyncSession,
    config_id: Optional[int] = None,
    model_type: str = 'language'  # 支持按类型选择模型
) -> BaseLLMProvider:
    """获取AI提供商实例"""
    # 如果指定了config_id，直接使用
    if config_id:
        config = await AiModelDao.select_ai_model_by_id(query_db, config_id)
    else:
        # 否则获取默认的指定类型模型
        config = await AiModelDao.select_default_ai_model(query_db, model_type)
```

### 7. 部署脚本 ✅

**文件**: 
- `RuoYi-Vue3-FastAPI/extend_ai_model_table.py` - Python部署脚本
- `RuoYi-Vue3-FastAPI/extend_ai_model_table.bat` - Windows批处理脚本

## 部署步骤

### 步骤1: 扩展数据库表

运行部署脚本：
```bash
cd RuoYi-Vue3-FastAPI
extend_ai_model_table.bat
```

或手动执行SQL：
```bash
mysql -u root -p ruoyi-vue-pro < ruoyi-fastapi-backend/sql/extend_ai_model_fields.sql
```

### 步骤2: 更新模型记录

运行更新脚本添加最新模型版本：
```bash
mysql -u root -p ruoyi-vue-pro < ruoyi-fastapi-backend/sql/ai_model_schema.sql
```

### 步骤3: 重启后端服务

```bash
cd ruoyi-fastapi-backend
# 停止现有服务
taskkill /F /IM python.exe

# 启动服务
python server.py
```

### 步骤4: 清除前端缓存

在浏览器中：
1. 按 `Ctrl + Shift + Delete` 打开清除浏览数据
2. 选择"缓存的图片和文件"
3. 点击"清除数据"
4. 刷新页面 `Ctrl + F5`

### 步骤5: 测试功能

1. 访问 `http://localhost/thesis/ai-model`
2. 点击"新增模型"按钮
3. 验证表单中有以下字段：
   - ✅ 模型类型（单选框：语言模型/视觉模型）
   - ✅ 提供商（下拉框：OpenAI/Anthropic/Qwen/自定义）
   - ✅ 模型名称
   - ✅ 模型代码
   - ✅ 模型版本
   - ✅ API Key
   - ✅ API地址
   - ✅ 其他参数

## 使用示例

### 添加语言模型

```javascript
// 前端表单数据
{
  modelType: 'language',
  provider: 'openai',
  modelName: 'GPT-4o',
  modelCode: 'openai',
  modelVersion: 'gpt-4o',
  apiKey: 'sk-xxx',
  apiBaseUrl: 'https://api.openai.com/v1',
  apiEndpoint: '/chat/completions',
  maxTokens: 4096,
  temperature: 0.7,
  topP: 0.9,
  priority: 100
}
```

### 添加视觉模型

```javascript
// 前端表单数据
{
  modelType: 'vision',
  provider: 'anthropic',
  modelName: 'Claude 3.5 Vision',
  modelCode: 'claude',
  modelVersion: 'claude-3-5-sonnet-20241022',
  apiKey: 'sk-ant-xxx',
  apiBaseUrl: 'https://api.anthropic.com',
  apiEndpoint: '/v1/messages',
  maxTokens: 4096,
  temperature: 0.7,
  topP: 0.9,
  priority: 90
}
```

### 在代码中使用

#### 论文系统使用语言模型
```python
from module_thesis.service.ai_generation_service import AiGenerationService

# 自动使用默认的语言模型
outline = await AiGenerationService.generate_outline(
    query_db=db,
    thesis_info=thesis_info
)
```

#### 自动化项目使用视觉模型
```python
from module_thesis.service.ai_generation_service import AiGenerationService

# 获取视觉模型提供商
vision_provider = await AiGenerationService._get_ai_provider(
    query_db=db,
    model_type='vision'
)

# 使用视觉模型识别图像
result = await vision_provider.recognize_image(image_data)
```

## 字段说明

| 字段名 | 类型 | 说明 | 可选值 |
|--------|------|------|--------|
| model_type | VARCHAR(20) | 模型类型 | language（语言模型）, vision（视觉模型） |
| provider | VARCHAR(50) | 提供商 | openai, anthropic, qwen, custom |
| model_code | VARCHAR(50) | 模型代码 | 如：openai, claude, qwen |
| model_version | VARCHAR(50) | 模型版本 | 如：gpt-4o, claude-3-5-sonnet-20241022 |
| params | TEXT | 模型参数JSON | 自定义参数配置 |
| capabilities | TEXT | 模型能力JSON | 模型支持的功能列表 |

## 验证清单

部署完成后，请验证以下功能：

### 前端验证
- [ ] 访问 `/thesis/ai-model` 页面正常加载
- [ ] 点击"新增模型"按钮，对话框正常打开
- [ ] 对话框中显示"模型类型"单选框（语言模型/视觉模型）
- [ ] 对话框中显示"提供商"下拉框（OpenAI/Anthropic/Qwen/自定义）
- [ ] 所有字段都有正确的验证规则
- [ ] 提交表单后数据正确保存
- [ ] 编辑现有模型时，字段值正确回显
- [ ] 卡片显示中正确显示模型类型和提供商标签

### 后端验证
- [ ] 数据库表成功添加新字段
- [ ] 索引创建成功
- [ ] API接口返回包含新字段
- [ ] 创建/更新操作正确处理新字段
- [ ] 按模型类型查询功能正常

### 功能验证
- [ ] 可以创建语言模型配置
- [ ] 可以创建视觉模型配置
- [ ] 论文生成功能使用语言模型
- [ ] 自动化项目可以获取视觉模型

## 常见问题

### Q1: 前端对话框中看不到新字段？
**A**: 清除浏览器缓存并强制刷新（Ctrl + F5）

### Q2: 提交表单时提示字段验证错误？
**A**: 检查 `rules` 对象是否包含 `modelType` 和 `provider` 的验证规则

### Q3: 后端返回数据中没有新字段？
**A**: 
1. 确认数据库表已成功扩展
2. 检查 VO 模型是否包含新字段
3. 重启后端服务

### Q4: 编辑现有模型时新字段为空？
**A**: 运行 SQL 更新脚本，为现有记录设置默认值：
```sql
UPDATE ai_write_ai_model_config 
SET model_type = 'language', provider = model_code 
WHERE model_type IS NULL OR model_type = '';
```

## 相关文档

- [AI_MODEL_TYPE_USAGE.md](./AI_MODEL_TYPE_USAGE.md) - 模型类型使用说明
- [AI_GENERATION_QUICK_START.md](./AI_GENERATION_QUICK_START.md) - AI生成快速开始
- [extend_ai_model_fields.sql](./RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/extend_ai_model_fields.sql) - 扩展字段SQL
- [ai_model_schema.sql](./RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/ai_model_schema.sql) - 完整表结构

## 总结

✅ **所有功能已完成**：
1. 数据库表扩展完成
2. 后端实体类和VO更新完成
3. 前端编辑对话框添加模型类型和提供商选择
4. 前端卡片显示更新完成
5. AI生成服务支持按类型选择模型
6. 部署脚本和文档完成

现在可以在编辑对话框中选择模型类型（语言模型/视觉模型）和提供商（OpenAI/Anthropic/Qwen/自定义），系统会根据模型类型自动选择合适的模型进行处理。
