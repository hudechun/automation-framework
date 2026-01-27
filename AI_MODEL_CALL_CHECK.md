# AI模型调用检查报告

## 问题描述
用户反馈：模板上传后，不能进行调用AI模型进行解析

## 代码分析结果

### 1. 模板上传流程 ✅
**文件**: `template_service.py` - `create_template` 方法

流程正确：
1. 模板创建时会检查 `file_path` 是否存在
2. 如果文件存在且没有 `format_data`，会触发格式解析
3. 当前代码已改为**同步执行**格式解析（用于调试）

```python
# 临时调试：改为同步执行以便立即看到结果和日志
if pending_format_parse:
    print("=" * 100)
    print(f"[调试模式] 同步执行格式解析 - 模板ID: {template_id}")
    print(f"  文件路径: {pending_format_parse}")
    print("=" * 100)
    import sys
    sys.stdout.flush()
    try:
        await cls._parse_template_format_in_background(template_id, pending_format_parse)
```

### 2. 格式解析流程 ✅
**文件**: `template_service.py` - `_parse_template_format_in_background` 方法

流程正确：
1. 创建独立的数据库会话
2. 调用 `FormatService.read_word_document_with_ai()` 读取Word文档
3. 使用AI分析格式并生成格式化指令
4. 将结果保存到数据库

### 3. AI模型调用流程 ✅
**文件**: `format_service.py` - `_analyze_format_with_ai` 方法

流程正确：
1. 构建格式分析提示词
2. 调用 `AiGenerationService._get_ai_provider()` 获取AI提供商
3. 使用 `llm_provider.chat()` 调用AI模型
4. 返回AI生成的格式化指令

### 4. AI提供商获取流程 ⚠️ **可能的问题点**
**文件**: `ai_generation_service.py` - `_get_ai_provider` 方法

```python
@classmethod
async def _get_ai_provider(cls, query_db: AsyncSession, config_id: Optional[int] = None, model_type: str = 'language'):
    """
    获取AI提供商实例
    
    注意：AI论文生成功能只使用语言模型（language），不使用视觉模型（vision）
    
    :param query_db: 数据库会话
    :param config_id: 配置ID（可选，不传则使用默认配置）
    :param model_type: 模型类型（language=语言模型/vision=视觉模型），默认为language
    :return: (LLM提供商实例, 配置信息) 元组
    """
    # 获取AI模型配置
    if config_id:
        config = await AiModelService.get_config_detail(query_db, config_id)
    else:
        # 根据模型类型获取默认配置
        config = await AiModelService.get_default_config(query_db, model_type)
```

**关键问题**：
- `_analyze_format_with_ai` 调用 `_get_ai_provider` 时**没有传递 `model_type` 参数**
- 默认使用 `model_type='language'`
- 如果数据库中没有 `is_default=1` 且 `model_type='language'` 的配置，会查找第一个启用的语言模型

### 5. 可能的失败原因

#### 原因1：没有启用的语言模型配置 ❌
- 数据库中没有 `is_enabled='1'` 且 `model_type='language'` 的AI模型配置
- 错误信息：`未配置language类型的AI模型，请先在AI模型管理中配置`

#### 原因2：AI模型配置不完整 ❌
- API Key未配置或为空
- 错误信息：`AI模型API Key未配置，请先配置`

#### 原因3：AI模型提供商不支持 ❌
- `provider` 字段为空或不是 `openai/anthropic/qwen`
- 错误信息：`不支持的AI模型提供商`

#### 原因4：AI API调用失败 ❌
- 网络连接问题
- API Key无效
- API端点配置错误
- 错误信息：`无法连接到AI服务` 或 `AI服务认证失败`

## 诊断步骤

### 步骤1：检查AI模型配置
```sql
-- 检查是否有启用的语言模型
SELECT 
    config_id,
    model_name,
    model_type,
    provider,
    is_enabled,
    is_default,
    api_key,
    api_base_url
FROM ai_write_ai_model_config
WHERE model_type = 'language'
  AND is_enabled = '1'
  AND del_flag = '0';
```

**预期结果**：至少有一条记录，且 `api_key` 不为空

### 步骤2：检查后端日志
查看后端控制台输出，搜索以下关键字：
- `[模板创建]` - 模板创建流程
- `[格式解析任务]` - 格式解析任务启动
- `[读取Word文档]` - Word文档读取流程
- `[AI格式分析]` - AI格式分析流程
- `ERROR` - 错误信息

### 步骤3：手动触发格式解析（测试）
使用测试接口手动触发格式解析：

```bash
POST /dev-api/thesis/template/{template_id}/parse-format
```

这个接口会：
1. 同步执行格式解析
2. 输出详细的调试信息到控制台
3. 返回解析结果或错误信息

### 步骤4：检查文件路径
确认模板文件路径是否正确：
1. 检查 `file_path` 字段是否包含完整路径
2. 检查文件是否实际存在于服务器上
3. 检查文件格式是否为 `.docx`（不支持 `.doc`）

## 解决方案

### 方案1：确保有启用的语言模型配置
1. 登录系统管理后台
2. 进入"AI模型管理"
3. 检查是否有语言模型配置
4. 确保至少有一个语言模型：
   - `is_enabled` = '1'（启用）
   - `model_type` = 'language'（语言模型）
   - `api_key` 已配置且有效
   - `provider` 为 `openai`/`anthropic`/`qwen` 之一

### 方案2：设置默认语言模型
1. 在AI模型列表中，选择一个语言模型
2. 点击"设为默认"按钮
3. 确保该模型的 `is_default` = '1'

### 方案3：检查API配置
1. 验证API Key是否有效
2. 检查API端点配置（如果使用自定义端点）
3. 测试网络连接

### 方案4：查看详细日志
1. 重启后端服务（确保代码更新生效）
2. 上传模板
3. 查看控制台输出的详细日志
4. 根据错误信息定位问题

## 测试建议

### 测试1：测试AI模型连接
使用AI模型测试接口：
```bash
POST /dev-api/admin/ai-model/test/{config_id}
```

### 测试2：手动触发格式解析
```bash
POST /dev-api/thesis/template/{template_id}/parse-format
```

### 测试3：查看模板详情
```bash
GET /dev-api/thesis/template/{template_id}
```
检查 `format_data` 字段是否有值

## 当前代码状态

✅ **已实现**：
- 模板上传时自动触发格式解析
- 格式解析使用AI模型分析Word文档
- 详细的日志输出（方便调试）
- 手动触发格式解析的测试接口

⚠️ **需要确认**：
- 数据库中是否有启用的语言模型配置
- AI模型配置是否完整（API Key、Provider等）
- 后端服务是否已重启（确保代码更新生效）

## 下一步操作

1. **检查数据库**：确认是否有启用的语言模型配置
2. **查看日志**：上传模板后查看后端控制台输出
3. **手动测试**：使用测试接口手动触发格式解析
4. **提供日志**：如果仍然失败，提供完整的错误日志

---

**生成时间**: 2026-01-27
**相关文件**:
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/service/template_service.py`
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/service/format_service.py`
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/service/ai_generation_service.py`
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/controller/template_controller.py`
