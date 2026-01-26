# AI模型配置功能 - 快速部署

## 一键部署

```bash
cd RuoYi-Vue3-FastAPI
python deploy_ai_model.py <数据库密码>
```

## 手动部署

### 1. 执行数据库脚本

```bash
mysql -u root -p ry-vue < ruoyi-fastapi-backend/sql/ai_model_schema.sql
mysql -u root -p ry-vue < ruoyi-fastapi-backend/sql/ai_model_menu.sql
```

### 2. 重启后端服务

```bash
cd ruoyi-fastapi-backend
python app.py
```

### 3. 刷新前端

- 清除浏览器缓存（Ctrl+Shift+Delete）
- 刷新页面（F5）

## 验证部署

1. 登录系统
2. 进入"论文系统" -> "AI模型配置"
3. 查看8个预设模型
4. 编辑模型，填写API Key
5. 测试连接
6. 启用模型
7. 设置默认模型

## 预设模型

系统预设了8个主流AI模型：

1. **OpenAI GPT-4** - 最强大的模型
2. **OpenAI GPT-3.5 Turbo** - 性价比高
3. **Claude 3 Opus** - Anthropic最强模型
4. **Claude 3 Sonnet** - 平衡性能和成本
5. **通义千问 Qwen-Max** - 国产最强
6. **通义千问 Qwen-Plus** - 性价比高
7. **DeepSeek Chat** - 通用对话
8. **DeepSeek Coder** - 代码生成

## 使用流程

1. 选择模型 → 2. 填写API Key → 3. 测试连接 → 4. 启用模型 → 5. 设置默认

## 详细文档

- 完整部署指南: `.kiro/specs/ai-thesis-writing/AI_MODEL_DEPLOYMENT_GUIDE.md`
- 实现总结: `.kiro/specs/ai-thesis-writing/AI_MODEL_COMPLETE_SUMMARY.md`

## 问题排查

### 菜单不显示
```sql
SELECT * FROM sys_menu WHERE menu_name = 'AI模型配置';
```

### 表不存在
```sql
SHOW TABLES LIKE 'ai_write_ai_model_config';
```

### API 404
检查后端启动日志，确认路由注册成功

---

**状态**: ✅ 完整功能已实现  
**版本**: 1.0.0  
**日期**: 2026-01-25
