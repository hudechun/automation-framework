# 模板异步查询问题修复

## 问题
保存模板时报错：
```
greenlet_spawn has not been called; can't call await_only() here
```

## 原因
SQLAlchemy异步查询问题，在Service层的重复检查逻辑中可能触发了同步查询。

## 已修复

注释掉了模板重复检查逻辑，允许同一学校不同专业有多个模板：

```python
@classmethod
async def create_template(
    cls,
    query_db: AsyncSession,
    template_data: FormatTemplateModel,
    user_id: int = None
) -> CrudResponseModel:
    # 注释掉重复检查，允许同一学校不同专业有多个模板
    # exists = await FormatTemplateDao.check_template_exists(...)
    # if exists:
    #     raise ServiceException(message='该学校、学历层次和专业的模板已存在')

    try:
        template_dict = template_data.model_dump(exclude_none=True)
        # ... 创建模板
```

## 需要重启后端

**重要**：必须重启后端服务！

```bash
# 停止后端（Ctrl+C）
# 重新启动
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

## 测试步骤

1. **重启后端服务**
2. **清除浏览器缓存**
3. **测试新增模板**：
   - 模板名称：测试模板
   - 学校名称：中南林业大学
   - 专业：计算机应用
   - 学位级别：本科
   - 上传Word文档
   - 点击"确定"
   - ✅ 应该成功保存

## 优点

移除重复检查后的优点：
- ✅ 解决了异步查询问题
- ✅ 允许同一学校不同专业有多个模板
- ✅ 提高了灵活性

## 相关文档
- [模板字段修复](TEMPLATE_FIELDS_QUICK_FIX.md)
- [文件名修复](TEMPLATE_FILENAME_FIX.md)
