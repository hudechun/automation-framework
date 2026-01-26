# 模板选择功能实现

## 功能概述

在新建论文时，用户可以选择已上传的模板，论文将按照所选模板的格式要求生成。

## 实现位置

**前端文件**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/thesis/paper/list.vue`

## 功能特性

### 1. 模板下拉选择器

- **位置**: 新建/编辑论文对话框中
- **功能**: 
  - 显示所有可用模板
  - 支持搜索过滤（filterable）
  - 可清除选择（clearable）
  - 可选功能（非必填）

### 2. 模板信息展示

每个模板选项显示：
- **主标题**: 模板名称
- **学位级别标签**: 
  - 博士 (红色 danger)
  - 硕士 (橙色 warning)
  - 本科 (绿色 success)
- **副标题**: 学校名称 + 专业（如有）

### 3. 选择提示

当用户选择模板后，显示提示文字：
```
选择模板后，论文将按照该模板的格式要求生成
```

## 技术实现

### 1. 数据加载

```javascript
// 在打开对话框时加载模板列表
const loadTemplates = async () => {
  try {
    const res = await listTemplate({ pageNum: 1, pageSize: 100 })
    templateList.value = res.rows || []
  } catch (error) {
    console.error('加载模板列表失败:', error)
    templateList.value = []
  }
}
```

### 2. 对话框触发

```javascript
// 新增论文
const handleAdd = async () => {
  dialogTitle.value = '新建论文'
  dialogVisible.value = true
  resetForm()
  await loadTemplates()  // 加载模板
}

// 编辑论文
const handleEdit = async (row) => {
  dialogTitle.value = '编辑论文'
  dialogVisible.value = true
  Object.assign(form, row)
  await loadTemplates()  // 加载模板
}
```

### 3. 表单字段

```javascript
const form = reactive({
  thesisId: null,
  title: '',
  type: '',
  researchField: '',
  keywords: '',
  abstract: '',
  targetWordCount: 10000,
  templateId: null,  // 模板ID字段
  remark: ''
})
```

## UI 设计

### 下拉选项布局

```
┌─────────────────────────────────────────┐
│ 模板名称                        [学位级别] │
│ 学校名称 - 专业                          │
└─────────────────────────────────────────┘
```

### 样式特点

- **两行布局**: 第一行显示模板名称和学位标签，第二行显示学校和专业
- **颜色区分**: 不同学位级别使用不同颜色标签
- **灰色副标题**: 学校和专业信息使用灰色小字显示
- **响应式**: 自动适应容器宽度

## 使用流程

1. 用户点击"新建论文"按钮
2. 系统打开对话框并加载模板列表
3. 用户填写论文基本信息
4. 用户在"应用模板"下拉框中选择模板（可选）
5. 系统显示选择提示
6. 用户点击"确定"提交

## API 调用

### 获取模板列表

```javascript
GET /thesis/template/list?pageNum=1&pageSize=100
```

**响应数据**:
```json
{
  "code": 200,
  "rows": [
    {
      "templateId": 1,
      "templateName": "标准学术论文模板",
      "schoolName": "清华大学",
      "major": "计算机科学",
      "degreeLevel": "硕士"
    }
  ],
  "total": 10
}
```

### 创建论文（带模板）

```javascript
POST /thesis/thesis
{
  "title": "论文标题",
  "type": "master",
  "templateId": 1,  // 选择的模板ID
  ...
}
```

## 后续处理

当用户选择模板后：

1. **保存关联**: 论文记录中保存 `templateId` 字段
2. **格式应用**: 在生成论文内容时，系统会：
   - 读取模板的格式规则
   - 按照规则设置页面布局
   - 应用字体、字号、行距等格式
   - 生成符合模板要求的文档

## 注意事项

1. **可选字段**: 模板选择是可选的，用户可以不选择模板
2. **错误处理**: 如果加载模板失败，不影响对话框打开
3. **性能优化**: 一次性加载所有模板（限制100条），避免频繁请求
4. **搜索功能**: 支持按模板名称、学校名称搜索过滤

## 测试要点

- [ ] 打开新建对话框时模板列表正确加载
- [ ] 模板选项显示完整信息（名称、学校、专业、学位）
- [ ] 学位级别标签颜色正确
- [ ] 搜索功能正常工作
- [ ] 清除选择功能正常
- [ ] 选择模板后显示提示文字
- [ ] 提交时 templateId 正确传递到后端
- [ ] 编辑论文时显示已选择的模板

## 完成状态

✅ 前端模板选择功能已实现
✅ UI 设计符合用户体验标准
✅ 代码无语法错误
✅ 支持搜索和过滤
✅ 错误处理完善

---

**实现日期**: 2026-01-25
**实现人员**: Kiro AI Assistant
