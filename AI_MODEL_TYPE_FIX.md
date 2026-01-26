# AI模型类型字段修复指南

## 问题描述

错误信息：
```json
{
  "code": 500,
  "msg": "未配置language类型的AI模型，请先在AI模型管理中配置",
  "success": false
}
```

## 原因分析

虽然您已经配置了AI模型，但是现有的数据库记录中 `model_type` 字段还是 `NULL` 或空值。系统在查询默认语言模型时，会过滤 `model_type = 'language'` 的记录，所以找不到任何模型。

## 解决方案

### 方法1: 运行更新脚本（推荐）

**步骤1**: 运行更新脚本
```bash
cd RuoYi-Vue3-FastAPI
update_model_type.bat
```

这个脚本会：
- ✅ 将所有现有记录的 `model_type` 设置为 `'language'`
- ✅ 将所有现有记录的 `provider` 设置为 `model_code` 的值
- ✅ 显示更新后的记录
- ✅ 检查是否有默认语言模型

**步骤2**: 重启后端服务
```bash
cd ruoyi-fastapi-backend
# 停止服务
taskkill /F /IM python.exe
# 启动服务
python server.py
```

**步骤3**: 测试功能
访问 `http://localhost/thesis/ai-model`，确认模型显示正常

### 方法2: 手动执行SQL

如果脚本无法运行，可以手动执行SQL：

```sql
-- 1. 更新model_type字段
UPDATE ai_write_ai_model_config 
SET model_type = 'language' 
WHERE model_type IS NULL OR model_type = '';

-- 2. 更新provider字段
UPDATE ai_write_ai_model_config 
SET provider = model_code 
WHERE provider IS NULL OR provider = '';

-- 3. 验证更新结果
SELECT 
    config_id,
    model_name,
    model_type,
    provider,
    is_enabled,
    is_default
FROM ai_write_ai_model_config
WHERE del_flag = '0'
ORDER BY priority DESC;
```

### 方法3: 在前端重新编辑模型

1. 访问 `http://localhost/thesis/ai-model`
2. 点击每个模型的"编辑"按钮
3. 选择"模型类型"（语言模型）
4. 选择"提供商"（如：OpenAI）
5. 点击"确定"保存

## 验证步骤

### 1. 检查数据库

运行以下SQL查询：
```sql
SELECT 
    config_id,
    model_name,
    model_type,
    provider,
    is_enabled,
    is_default
FROM ai_write_ai_model_config
WHERE del_flag = '0';
```

确认：
- ✅ `model_type` 字段不为空（应该是 'language' 或 'vision'）
- ✅ `provider` 字段不为空（应该是 'openai', 'anthropic', 'qwen' 等）
- ✅ 至少有一个记录的 `is_default = '1'` 且 `is_enabled = '1'`

### 2. 检查默认语言模型

运行以下SQL查询：
```sql
SELECT 
    model_name,
    model_type,
    provider,
    is_enabled,
    is_default
FROM ai_write_ai_model_config
WHERE model_type = 'language'
  AND is_default = '1'
  AND is_enabled = '1'
  AND del_flag = '0';
```

应该返回至少一条记录。

### 3. 测试API

使用测试脚本：
```bash
cd RuoYi-Vue3-FastAPI
test_ai_model_fields.bat
```

或者手动测试API：
```bash
curl http://localhost:8000/thesis/ai-model/list
```

## 常见问题

### Q1: 运行脚本后还是报错？
**A**: 
1. 确认后端服务已重启
2. 检查数据库连接配置（`.env.dev` 文件）
3. 运行 `test_ai_model_fields.bat` 查看详细信息

### Q2: 没有默认模型？
**A**: 
1. 访问 `http://localhost/thesis/ai-model`
2. 找到一个启用的语言模型
3. 点击"设为默认"按钮

### Q3: 所有模型都是禁用状态？
**A**: 
1. 点击模型卡片右上角的开关
2. 将至少一个模型设置为启用状态
3. 然后设置为默认

### Q4: 更新脚本报错？
**A**: 
1. 检查Python环境是否正确
2. 检查数据库是否正在运行
3. 检查 `.env.dev` 中的数据库配置
4. 尝试手动执行SQL（方法2）

## 代码修改说明

为了支持 `model_type` 参数，我们修改了以下文件：

### 1. DAO层 (ai_model_dao.py)
```python
@classmethod
async def get_default_config(cls, db: AsyncSession, model_type: str = 'language'):
    """获取默认模型配置"""
    config_info = (
        await db.execute(
            select(AiWriteAiModelConfig)
            .where(
                AiWriteAiModelConfig.model_type == model_type,  # 新增过滤条件
                AiWriteAiModelConfig.is_default == '1',
                AiWriteAiModelConfig.is_enabled == '1',
                AiWriteAiModelConfig.status == '0',
                AiWriteAiModelConfig.del_flag == '0',
            )
            .order_by(AiWriteAiModelConfig.priority.desc())
        )
    ).scalars().first()
    return config_info
```

### 2. Service层 (ai_model_service.py)
```python
@classmethod
async def get_default_config(cls, query_db: AsyncSession, model_type: str = 'language'):
    """获取默认AI模型配置"""
    config = await AiModelConfigDao.get_default_config(query_db, model_type)
    if config:
        return AiModelConfigModel(**CamelCaseUtil.transform_result(config))
    return None
```

## 完整流程

```
1. 运行更新脚本
   ↓
2. 数据库记录更新
   - model_type = 'language'
   - provider = model_code
   ↓
3. 重启后端服务
   ↓
4. 系统查询默认语言模型
   - WHERE model_type = 'language'
   - AND is_default = '1'
   - AND is_enabled = '1'
   ↓
5. 找到默认模型
   ↓
6. 论文生成功能正常工作
```

## 相关文件

- `update_model_type.py` - Python更新脚本
- `update_model_type.bat` - Windows批处理脚本
- `update_model_type.sql` - SQL更新脚本
- `test_ai_model_fields.py` - 测试脚本
- `test_ai_model_fields.bat` - 测试批处理脚本

## 总结

问题的根本原因是：
1. ✅ 数据库表已经添加了 `model_type` 字段
2. ✅ 代码已经支持按 `model_type` 查询
3. ❌ 但现有记录的 `model_type` 字段还是空值

解决方法：
1. 运行 `update_model_type.bat` 更新现有记录
2. 重启后端服务
3. 确保至少有一个默认的语言模型

现在运行更新脚本，问题就会解决！
