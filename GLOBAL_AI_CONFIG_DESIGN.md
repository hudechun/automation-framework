# 全局AI配置系统设计方案

## 概述

将AI模型配置从论文模块提升为全局配置，支持语言模型和视觉模型，提供预设模型下拉选择。

## 设计目标

1. **全局化** - AI配置作为系统级配置，所有模块共享
2. **分类管理** - 区分语言模型（LLM）和视觉模型（Vision）
3. **易用性** - 提供常用模型下拉选择，减少手动输入
4. **扩展性** - 支持自定义模型配置
5. **复用性** - 其他模块（如自动化框架）也可以使用

## 数据库设计

### 1. 移动AI模型表到系统级

**原表位置：** `ai_write_ai_model_config`（论文模块）
**新表位置：** `sys_ai_model_config`（系统级）

```sql
-- 系统AI模型配置表
CREATE TABLE `sys_ai_model_config` (
  `config_id` bigint NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `model_name` varchar(100) NOT NULL COMMENT '模型名称',
  `model_code` varchar(100) NOT NULL COMMENT '模型代码',
  `model_type` varchar(20) NOT NULL DEFAULT 'language' COMMENT '模型类型（language/vision）',
  `provider` varchar(50) NOT NULL COMMENT '提供商（openai/anthropic/qwen等）',
  `api_key` varchar(500) DEFAULT NULL COMMENT 'API密钥',
  `api_endpoint` varchar(500) DEFAULT NULL COMMENT 'API端点',
  `model_version` varchar(50) DEFAULT NULL COMMENT '模型版本',
  `params` json DEFAULT NULL COMMENT '模型参数（JSON）',
  `capabilities` json DEFAULT NULL COMMENT '模型能力（JSON）',
  `priority` int DEFAULT '0' COMMENT '优先级',
  `is_enabled` char(1) DEFAULT '1' COMMENT '是否启用（0否 1是）',
  `is_default` char(1) DEFAULT '0' COMMENT '是否默认（0否 1是）',
  `is_preset` char(1) DEFAULT '0' COMMENT '是否预设（0否 1是）',
  `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0存在 2删除）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`config_id`),
  UNIQUE KEY `uk_model_code` (`model_code`),
  KEY `idx_provider` (`provider`),
  KEY `idx_model_type` (`model_type`),
  KEY `idx_is_enabled` (`is_enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统AI模型配置表';
```

### 2. 预设模型数据

```sql
-- 插入预设模型（语言模型）
INSERT INTO `sys_ai_model_config` VALUES
-- OpenAI 语言模型
(1, 'GPT-4 Turbo', 'gpt-4-turbo-preview', 'language', 'openai', NULL, 'https://api.openai.com/v1', 'gpt-4-turbo-preview', '{"temperature": 0.7, "max_tokens": 4096}', '{"text_generation": true, "code_generation": true, "reasoning": true}', 100, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'GPT-4 Turbo 最新版本'),
(2, 'GPT-4', 'gpt-4', 'language', 'openai', NULL, 'https://api.openai.com/v1', 'gpt-4-0613', '{"temperature": 0.7, "max_tokens": 8192}', '{"text_generation": true, "code_generation": true, "reasoning": true}', 95, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'GPT-4 标准版本'),
(3, 'GPT-3.5 Turbo', 'gpt-3.5-turbo', 'language', 'openai', NULL, 'https://api.openai.com/v1', 'gpt-3.5-turbo-0125', '{"temperature": 0.7, "max_tokens": 4096}', '{"text_generation": true, "code_generation": true}', 80, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'GPT-3.5 Turbo 高性价比'),

-- Anthropic 语言模型
(4, 'Claude 3 Opus', 'claude-3-opus-20240229', 'language', 'anthropic', NULL, 'https://api.anthropic.com', 'claude-3-opus-20240229', '{"temperature": 0.7, "max_tokens": 4096}', '{"text_generation": true, "code_generation": true, "reasoning": true, "long_context": true}', 98, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Claude 3 Opus 最强版本'),
(5, 'Claude 3 Sonnet', 'claude-3-sonnet-20240229', 'language', 'anthropic', NULL, 'https://api.anthropic.com', 'claude-3-sonnet-20240229', '{"temperature": 0.7, "max_tokens": 4096}', '{"text_generation": true, "code_generation": true, "reasoning": true}', 90, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Claude 3 Sonnet 平衡版本'),
(6, 'Claude 3 Haiku', 'claude-3-haiku-20240307', 'language', 'anthropic', NULL, 'https://api.anthropic.com', 'claude-3-haiku-20240307', '{"temperature": 0.7, "max_tokens": 4096}', '{"text_generation": true, "fast_response": true}', 85, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Claude 3 Haiku 快速版本'),

-- Qwen 语言模型
(7, '通义千问Max', 'qwen-max', 'language', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-max-latest', '{"temperature": 0.7}', '{"text_generation": true, "chinese_optimized": true}', 92, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, '通义千问Max 最强版本'),
(8, '通义千问Plus', 'qwen-plus', 'language', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-plus-latest', '{"temperature": 0.7}', '{"text_generation": true, "chinese_optimized": true}', 88, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, '通义千问Plus 平衡版本'),
(9, '通义千问Turbo', 'qwen-turbo', 'language', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-turbo-latest', '{"temperature": 0.7}', '{"text_generation": true, "fast_response": true, "chinese_optimized": true}', 82, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, '通义千问Turbo 快速版本'),

-- OpenAI 视觉模型
(10, 'GPT-4 Vision', 'gpt-4-vision-preview', 'vision', 'openai', NULL, 'https://api.openai.com/v1', 'gpt-4-vision-preview', '{"temperature": 0.7, "max_tokens": 4096}', '{"image_understanding": true, "ocr": true, "visual_reasoning": true}', 95, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'GPT-4 Vision 视觉理解'),

-- Anthropic 视觉模型
(11, 'Claude 3 Opus Vision', 'claude-3-opus-20240229', 'vision', 'anthropic', NULL, 'https://api.anthropic.com', 'claude-3-opus-20240229', '{"temperature": 0.7, "max_tokens": 4096}', '{"image_understanding": true, "ocr": true, "visual_reasoning": true, "document_analysis": true}', 98, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, 'Claude 3 Opus 视觉理解'),

-- Qwen 视觉模型
(12, '通义千问VL', 'qwen-vl-max', 'vision', 'qwen', NULL, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-vl-max-latest', '{"temperature": 0.7}', '{"image_understanding": true, "ocr": true, "chinese_optimized": true}', 90, '0', '0', '1', '0', '0', 'admin', NOW(), NULL, NULL, '通义千问VL 视觉理解');
```

## 后端实现

### 1. 移动到系统模块

**目录结构：**
```
ruoyi-fastapi-backend/
├── module_admin/
│   ├── controller/
│   │   └── ai_model_controller.py  # 移动到这里
│   ├── service/
│   │   └── ai_model_service.py     # 移动到这里
│   ├── dao/
│   │   └── ai_model_dao.py         # 移动到这里
│   └── entity/
│       ├── do/
│       │   └── ai_model_do.py      # 移动到这里
│       └── vo/
│           └── ai_model_vo.py      # 移动到这里
```

### 2. 添加预设模型接口

```python
# module_admin/controller/ai_model_controller.py

@router.get('/preset-models', summary='获取预设模型列表')
async def get_preset_models(
    model_type: Optional[str] = Query(None, description='模型类型（language/vision）'),
    provider: Optional[str] = Query(None, description='提供商'),
    query_db: AsyncSession = Depends(get_db)
):
    """获取预设模型列表（用于下拉选择）"""
    try:
        models = await AiModelService.get_preset_models(query_db, model_type, provider)
        return ResponseUtil.success(data=models)
    except Exception as e:
        return ResponseUtil.failure(msg=str(e))
```

### 3. 更新服务层

```python
# module_admin/service/ai_model_service.py

@classmethod
async def get_preset_models(
    cls,
    query_db: AsyncSession,
    model_type: Optional[str] = None,
    provider: Optional[str] = None
) -> List[Dict[str, Any]]:
    """获取预设模型列表"""
    return await AiModelDao.get_preset_models(query_db, model_type, provider)

@classmethod
async def get_models_by_type(
    cls,
    query_db: AsyncSession,
    model_type: str
) -> List[AiModelConfigModel]:
    """根据类型获取模型列表"""
    models = await AiModelDao.get_models_by_type(query_db, model_type)
    return [AiModelConfigModel(**CamelCaseUtil.transform_result(model)) for model in models]
```

## 前端实现

### 1. 移动到系统管理

**菜单位置：** 系统管理 > AI模型配置

**路由：** `/system/ai-model`

### 2. 改进配置表单

```vue
<template>
  <el-form-item label="模型类型" prop="modelType">
    <el-radio-group v-model="form.modelType" @change="handleModelTypeChange">
      <el-radio label="language">语言模型</el-radio>
      <el-radio label="vision">视觉模型</el-radio>
    </el-radio-group>
  </el-form-item>

  <el-form-item label="提供商" prop="provider">
    <el-select v-model="form.provider" placeholder="请选择提供商" @change="handleProviderChange">
      <el-option label="OpenAI" value="openai" />
      <el-option label="Anthropic (Claude)" value="anthropic" />
      <el-option label="Qwen (通义千问)" value="qwen" />
      <el-option label="自定义" value="custom" />
    </el-select>
  </el-form-item>

  <el-form-item label="选择模型" prop="modelCode">
    <el-select 
      v-model="form.modelCode" 
      placeholder="请选择模型或输入自定义模型代码"
      filterable
      allow-create
      @change="handleModelSelect"
    >
      <el-option
        v-for="model in presetModels"
        :key="model.modelCode"
        :label="`${model.modelName} - ${model.remark}`"
        :value="model.modelCode"
      >
        <span style="float: left">{{ model.modelName }}</span>
        <span style="float: right; color: #8492a6; font-size: 13px">
          {{ model.remark }}
        </span>
      </el-option>
    </el-select>
  </el-form-item>

  <!-- 自动填充的字段 -->
  <el-form-item label="模型名称" prop="modelName">
    <el-input v-model="form.modelName" placeholder="自动填充或手动输入" />
  </el-form-item>

  <el-form-item label="API端点" prop="apiEndpoint">
    <el-input v-model="form.apiEndpoint" placeholder="自动填充或手动输入" />
  </el-form-item>

  <el-form-item label="API密钥" prop="apiKey">
    <el-input 
      v-model="form.apiKey" 
      type="password" 
      placeholder="请输入API密钥"
      show-password
    />
  </el-form-item>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getPresetModels } from '@/api/system/aiModel'

const form = ref({
  modelType: 'language',
  provider: 'openai',
  modelCode: '',
  modelName: '',
  apiEndpoint: '',
  apiKey: ''
})

const presetModels = ref([])

// 加载预设模型
const loadPresetModels = async () => {
  const res = await getPresetModels({
    modelType: form.value.modelType,
    provider: form.value.provider
  })
  presetModels.value = res.data
}

// 模型类型改变
const handleModelTypeChange = () => {
  form.value.modelCode = ''
  loadPresetModels()
}

// 提供商改变
const handleProviderChange = () => {
  form.value.modelCode = ''
  loadPresetModels()
}

// 选择模型后自动填充
const handleModelSelect = (modelCode) => {
  const selected = presetModels.value.find(m => m.modelCode === modelCode)
  if (selected) {
    form.value.modelName = selected.modelName
    form.value.apiEndpoint = selected.apiEndpoint
    form.value.modelVersion = selected.modelVersion
    form.value.params = selected.params
  }
}

// 初始加载
loadPresetModels()
</script>
```

## 迁移方案

### 1. 数据迁移脚本

```sql
-- 迁移现有数据
INSERT INTO sys_ai_model_config (
  model_name, model_code, model_type, provider, api_key, api_endpoint,
  model_version, params, priority, is_enabled, is_default, is_preset,
  status, del_flag, create_by, create_time, update_by, update_time, remark
)
SELECT 
  model_name, model_code, 'language', provider, api_key, api_endpoint,
  model_version, params, priority, is_enabled, is_default, '0',
  status, del_flag, create_by, create_time, update_by, update_time, remark
FROM ai_write_ai_model_config
WHERE del_flag = '0';

-- 删除旧表（可选，建议先备份）
-- DROP TABLE ai_write_ai_model_config;
```

### 2. 代码迁移

1. 移动文件到 `module_admin`
2. 更新导入路径
3. 更新路由注册
4. 更新前端API路径

## 使用示例

### 论文模块使用

```python
# 论文生成时获取语言模型
from module_admin.service.ai_model_service import AiModelService

# 获取默认语言模型
config = await AiModelService.get_default_config(query_db, model_type='language')

# 获取所有启用的语言模型
models = await AiModelService.get_models_by_type(query_db, 'language')
```

### 自动化框架使用

```python
# 验证码识别时获取视觉模型
config = await AiModelService.get_default_config(query_db, model_type='vision')
```

## 优势

1. **统一管理** - 所有AI配置集中管理
2. **易于使用** - 下拉选择，无需记忆模型代码
3. **灵活扩展** - 支持自定义模型
4. **跨模块复用** - 论文、自动化等模块共享配置
5. **类型区分** - 语言模型和视觉模型分开管理

## 实施步骤

1. ✅ 创建新表 `sys_ai_model_config`
2. ✅ 插入预设模型数据
3. ⏳ 移动代码到 `module_admin`
4. ⏳ 更新前端页面
5. ⏳ 迁移现有数据
6. ⏳ 更新论文模块引用
7. ⏳ 测试功能

需要我开始实施吗？
