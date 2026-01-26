# 🔧 修复AI模型类型问题

## 问题

您看到的错误：
```
未配置language类型的AI模型，请先在AI模型管理中配置
```

## 原因

虽然您已经配置了AI模型，但数据库中现有记录的 `model_type` 字段还是空的，所以系统找不到语言模型。

## 快速解决（3步）

### 第1步：运行更新脚本

```bash
cd RuoYi-Vue3-FastAPI
update_model_type.bat
```

这个脚本会自动将所有现有模型设置为"语言模型"。

### 第2步：重启后端

```bash
cd ruoyi-fastapi-backend
taskkill /F /IM python.exe
python server.py
```

### 第3步：测试

访问 `http://localhost/thesis/ai-model`，确认模型显示正常。

## 如果还有问题

### 检查是否有默认模型

1. 访问 `http://localhost/thesis/ai-model`
2. 找到一个启用的模型
3. 点击"设为默认"按钮

### 检查模型是否启用

确保至少有一个模型的开关是打开的（绿色）。

## 验证是否修复成功

运行测试脚本：
```bash
cd RuoYi-Vue3-FastAPI
test_ai_model_fields.bat
```

应该看到：
- ✅ model_type 字段存在
- ✅ 所有记录的 model_type = 'language'
- ✅ 有默认语言模型

## 为什么会出现这个问题？

1. 我们刚刚添加了 `model_type` 字段到数据库
2. 代码已经更新支持这个字段
3. 但您之前配置的模型记录中这个字段还是空的
4. 所以需要运行更新脚本填充这个字段

## 更新脚本做了什么？

```sql
-- 将所有现有模型设置为语言模型
UPDATE ai_write_ai_model_config 
SET model_type = 'language' 
WHERE model_type IS NULL OR model_type = '';

-- 设置提供商字段
UPDATE ai_write_ai_model_config 
SET provider = model_code 
WHERE provider IS NULL OR provider = '';
```

## 完成后

✅ 所有现有模型都会被标记为"语言模型"
✅ 论文生成功能可以正常使用
✅ 以后添加新模型时可以选择类型（语言/视觉）

---

**现在就运行 `update_model_type.bat`，问题马上解决！** 🚀
