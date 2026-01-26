# 模板文件名缺失修复

## 问题
保存模板时报错：
```
Column 'file_name' cannot be null
```

## 原因
上传文件后，只保存了 `file_path`，没有保存 `file_name`。

## 已修复

### 1. 添加fileName字段
```javascript
const form = reactive({
  templateId: null,
  templateName: '',
  schoolName: '',
  major: '',
  degreeLevel: '',
  filePath: '',
  fileName: '',      // ✅ 新增
  thumbnail: '',
  remark: ''
})
```

### 2. 上传成功时提取文件名
```javascript
const handleTemplateFileSuccess = (response, file) => {
  if (response.code === 200) {
    form.filePath = response.url
    // 优先使用原始文件名
    form.fileName = file.name || response.fileName || response.url.split('/').pop()
    ElMessage.success('模板文件上传成功')
  }
}
```

## 测试步骤

### 1. 清除浏览器缓存
- 按 `Ctrl + Shift + Delete`
- 清除缓存

### 2. 测试上传
```
1. 进入模板管理页面
2. 点击"新增模板"
3. 填写所有必填字段：
   - 模板名称
   - 学校名称
   - 学位级别
4. 上传Word文档
5. 点击"确定"
6. ✅ 应该成功保存
```

## 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `filePath` | 文件完整URL | `http://127.0.0.1:9099/dev-api/profile/upload/2026/01/25/xxx.doc` |
| `fileName` | 原始文件名 | `附件5：中南林业科技大学高等学历继续教育(毕业论文)格式_20260125204223A047.doc` |

## 如果还是失败

检查浏览器控制台（F12），查看提交的数据是否包含 `fileName` 字段。

## 相关文档
- [模板字段修复](.kiro/specs/ai-thesis-writing/TEMPLATE_FIELDS_FIX.md)
- [上传认证修复](UPLOAD_AUTH_QUICK_FIX.md)
