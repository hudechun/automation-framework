# AI论文生成功能快速开始指南

## 1. 安装依赖

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
pip install openai anthropic aiohttp
```

或者使用requirements.txt：
```bash
pip install -r requirements.txt
```

## 2. 配置AI模型

### 方式一：通过前端界面配置（推荐）

1. 登录系统（管理员账号）
2. 进入 **论文系统 > AI模型管理**
3. 点击 **新增** 按钮
4. 填写配置信息：

#### OpenAI配置示例
```
模型名称: GPT-4
模型代码: gpt-4
提供商: openai
API密钥: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API端点: https://api.openai.com/v1 (可选)
模型版本: gpt-4-0613
参数配置: {"temperature": 0.7, "top_p": 1}
优先级: 100
是否启用: 是
是否默认: 是
```

#### Anthropic配置示例
```
模型名称: Claude 3 Opus
模型代码: claude-3-opus-20240229
提供商: anthropic
API密钥: sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API端点: https://api.anthropic.com (可选)
模型版本: claude-3-opus-20240229
参数配置: {"temperature": 0.7}
优先级: 90
是否启用: 是
是否默认: 否
```

#### Qwen配置示例
```
模型名称: 通义千问Max
模型代码: qwen-max
提供商: qwen
API密钥: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API端点: https://dashscope.aliyuncs.com/compatible-mode/v1
模型版本: qwen-max-latest
参数配置: {"temperature": 0.7}
优先级: 80
是否启用: 是
是否默认: 否
```

5. 点击 **测试连接** 验证配置
6. 保存配置

### 方式二：通过SQL直接插入

```sql
-- OpenAI GPT-4
INSERT INTO ai_write_ai_model_config (
    model_name, model_code, provider, api_key, api_endpoint,
    model_version, params, priority, is_enabled, is_default,
    status, create_time
) VALUES (
    'GPT-4', 'gpt-4', 'openai', 'sk-your-api-key-here',
    'https://api.openai.com/v1', 'gpt-4-0613',
    '{"temperature": 0.7, "top_p": 1}', 100, '1', '1',
    '0', NOW()
);

-- Anthropic Claude 3
INSERT INTO ai_write_ai_model_config (
    model_name, model_code, provider, api_key, api_endpoint,
    model_version, params, priority, is_enabled, is_default,
    status, create_time
) VALUES (
    'Claude 3 Opus', 'claude-3-opus-20240229', 'anthropic', 'sk-ant-your-api-key-here',
    'https://api.anthropic.com', 'claude-3-opus-20240229',
    '{"temperature": 0.7}', 90, '1', '0',
    '0', NOW()
);

-- Qwen通义千问
INSERT INTO ai_write_ai_model_config (
    model_name, model_code, provider, api_key, api_endpoint,
    model_version, params, priority, is_enabled, is_default,
    status, create_time
) VALUES (
    '通义千问Max', 'qwen-max', 'qwen', 'sk-your-api-key-here',
    'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-max-latest',
    '{"temperature": 0.7}', 80, '1', '0',
    '0', NOW()
);
```

## 3. 测试AI连接

### 通过前端测试
1. 在AI模型管理页面
2. 找到配置的模型
3. 点击 **测试连接** 按钮
4. 查看测试结果

### 通过API测试
```bash
curl -X POST "http://localhost:8000/thesis/ai-model/test/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test_prompt": "你好，请简单介绍一下你自己"}'
```

## 4. 使用论文生成功能

### 步骤1：创建论文
1. 进入 **论文系统 > 论文管理**
2. 点击 **新增论文**
3. 填写论文信息：
   - 论文标题
   - 专业
   - 学位级别（本科/硕士/博士）
   - 研究方向
   - 关键词
4. 提交创建

### 步骤2：生成大纲
1. 在论文列表中找到刚创建的论文
2. 点击 **生成大纲** 按钮
3. 等待AI生成（通常需要5-15秒）
4. 查看生成的大纲
5. 可以编辑修改大纲

### 步骤3：生成章节
1. 在论文详情页
2. 选择要生成的章节
3. 点击 **生成章节** 按钮
4. 等待AI生成（通常需要10-30秒）
5. 查看生成的章节内容
6. 可以编辑修改章节

### 步骤4：批量生成（可选）
1. 在论文详情页
2. 点击 **批量生成章节** 按钮
3. 选择要生成的章节
4. 等待AI批量生成
5. 查看所有生成的章节

## 5. 配额管理

### 查看配额
1. 进入 **论文系统 > 会员管理 > 用户配额**
2. 查看当前用户的配额使用情况

### 充值配额（管理员）
1. 进入 **论文系统 > 会员管理 > 套餐管理**
2. 创建套餐或直接给用户充值配额

### 配额消耗规则
- 创建论文：1次论文生成配额
- 生成大纲：1次大纲生成配额
- 生成章节：每章1次章节生成配额

## 6. 常见问题

### Q1: 提示"未配置AI模型"
**A**: 请先在AI模型管理中配置至少一个AI模型，并设置为启用状态。

### Q2: 提示"API Key未配置"
**A**: 请在AI模型配置中填写正确的API Key。

### Q3: 提示"Rate limit exceeded"
**A**: API调用频率过高，系统会自动重试。如果持续失败，请稍后再试或联系API提供商。

### Q4: 生成的内容质量不好
**A**: 可以尝试：
- 调整提示词模板
- 修改temperature参数（0.7-0.9之间）
- 使用更强大的模型（如GPT-4或Claude 3 Opus）
- 提供更详细的论文信息

### Q5: 生成速度慢
**A**: 
- AI生成需要时间，通常5-30秒
- 章节越长，生成时间越长
- 可以考虑使用更快的模型（如GPT-3.5）

### Q6: 配额不足
**A**: 
- 联系管理员充值配额
- 或购买会员套餐

## 7. API密钥获取

### OpenAI
1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的API Key
5. 复制密钥（只显示一次）

### Anthropic
1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的API Key
5. 复制密钥

### Qwen（通义千问）
1. 访问 https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 开通DashScope服务
4. 创建API Key
5. 复制密钥

## 8. 成本估算

### OpenAI GPT-4
- 输入：$0.03 / 1K tokens
- 输出：$0.06 / 1K tokens
- 生成一篇论文大纲：约$0.10-0.20
- 生成一个章节：约$0.20-0.50

### Anthropic Claude 3 Opus
- 输入：$0.015 / 1K tokens
- 输出：$0.075 / 1K tokens
- 生成一篇论文大纲：约$0.08-0.15
- 生成一个章节：约$0.15-0.40

### Qwen通义千问
- 按调用次数计费
- 具体价格参考阿里云官网

## 9. 安全建议

1. **API Key安全**
   - 不要在代码中硬编码API Key
   - 不要提交API Key到版本控制
   - 定期轮换API Key
   - 使用环境变量或密钥管理服务

2. **访问控制**
   - 只有管理员可以配置AI模型
   - 普通用户只能使用已配置的模型
   - 使用配额系统限制使用量

3. **内容审核**
   - AI生成的内容需要人工审核
   - 不要直接发布AI生成的内容
   - 注意学术诚信和版权问题

## 10. 技术支持

如有问题，请联系技术支持或查看详细文档：
- `AI_GENERATION_INTEGRATION_COMPLETE.md` - 完整技术文档
- `module_thesis/service/ai_generation_service.py` - 源代码

---

**祝使用愉快！** 🎉
