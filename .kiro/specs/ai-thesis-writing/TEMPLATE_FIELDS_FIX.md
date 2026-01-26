# 模板字段修复总结

## 问题描述

保存模板时报错：
```
'FormatTemplateModel' object has no attribute 'school_name'
```

## 问题原因

### 1. 字段命名不一致

**数据库表结构**（`ai_write_format_template`）：
- `school_name` - 学校名称（必填）
- `degree_level` - 学位级别（必填）
- `major` - 专业（可选）

**后端VO模型**（原始错误）：
- ❌ `school` - 与数据库不匹配
- ❌ 缺少 `degree_level`

**前端表单**（原始错误）：
- ❌ `type` - 不存在的字段
- ❌ `description` - 不存在的字段
- ❌ 缺少 `schoolName`
- ❌ 缺少 `degreeLevel`

### 2. 字段缺失

前端表单缺少数据库必填字段，导致后端验证失败。

## 修复方案

### 1. 修复后端VO模型

将所有VO模型中的 `school` 改为 `school_name`：

```python
# template_vo.py

class FormatTemplateModel(BaseModel):
    template_id: Optional[int] = Field(default=None, description='模板ID')
    template_name: Optional[str] = Field(default=None, description='模板名称')
    school_name: Optional[str] = Field(default=None, description='学校名称')  # ✅ 修复
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')  # ✅ 添加
    file_path: Optional[str] = Field(default=None, description='模板文件路径')
    # ... 其他字段

class TemplateUploadModel(BaseModel):
    template_name: str = Field(description='模板名称')
    school_name: Optional[str] = Field(default=None, description='学校名称')  # ✅ 修复
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')  # ✅ 添加
    # ... 其他字段

class TemplateUpdateModel(BaseModel):
    template_id: int = Field(description='模板ID')
    template_name: Optional[str] = Field(default=None, description='模板名称')
    school_name: Optional[str] = Field(default=None, description='学校名称')  # ✅ 修复
    major: Optional[str] = Field(default=None, description='专业')
    degree_level: Optional[str] = Field(default=None, description='学历层次')  # ✅ 添加
    # ... 其他字段
```

### 2. 修复前端表单字段

```javascript
// 表单数据
const form = reactive({
  templateId: null,
  templateName: '',
  schoolName: '',      // ✅ 新增（对应后端 school_name）
  major: '',           // ✅ 新增
  degreeLevel: '',     // ✅ 新增（对应后端 degree_level）
  filePath: '',
  thumbnail: '',
  remark: ''
})

// 验证规则
const rules = {
  templateName: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  schoolName: [{ required: true, message: '请输入学校名称', trigger: 'blur' }],  // ✅ 新增
  degreeLevel: [{ required: true, message: '请选择学位级别', trigger: 'change' }]  // ✅ 新增
}
```

### 3. 更新表单HTML

```vue
<el-form-item label="模板名称" prop="templateName">
  <el-input v-model="form.templateName" placeholder="请输入模板名称" />
</el-form-item>

<!-- ✅ 新增：学校名称 -->
<el-form-item label="学校名称" prop="schoolName">
  <el-input v-model="form.schoolName" placeholder="请输入学校名称" />
</el-form-item>

<!-- ✅ 新增：专业 -->
<el-form-item label="专业" prop="major">
  <el-input v-model="form.major" placeholder="请输入专业（可选）" />
</el-form-item>

<!-- ✅ 新增：学位级别 -->
<el-form-item label="学位级别" prop="degreeLevel">
  <el-select v-model="form.degreeLevel" placeholder="请选择学位级别" style="width: 100%">
    <el-option label="本科" value="本科" />
    <el-option label="硕士" value="硕士" />
    <el-option label="博士" value="博士" />
  </el-select>
</el-form-item>
```

### 4. 更新搜索栏

```vue
<!-- 移除不存在的"模板类型"搜索 -->
<!-- 添加"学校名称"搜索 -->
<el-form-item label="学校名称" prop="schoolName">
  <el-input
    v-model="queryParams.schoolName"
    placeholder="请输入学校名称"
    clearable
    style="width: 240px"
  />
</el-form-item>
```

### 5. 更新模板卡片显示

```vue
<!-- 学位级别标签 -->
<el-tag
  class="type-tag"
  :type="template.degreeLevel === '博士' ? 'danger' : template.degreeLevel === '硕士' ? 'warning' : 'success'"
  size="small"
>
  {{ template.degreeLevel }}
</el-tag>

<!-- 模板信息 -->
<div class="template-name">{{ template.templateName }}</div>
<div class="template-desc">{{ template.schoolName }} - {{ template.major || '通用' }}</div>
```

## 字段映射关系

| 数据库字段 | 后端VO字段 | 前端字段 | 说明 |
|-----------|-----------|---------|------|
| `template_id` | `template_id` | `templateId` | 模板ID |
| `template_name` | `template_name` | `templateName` | 模板名称（必填） |
| `school_name` | `school_name` | `schoolName` | 学校名称（必填） |
| `major` | `major` | `major` | 专业（可选） |
| `degree_level` | `degree_level` | `degreeLevel` | 学位级别（必填） |
| `file_path` | `file_path` | `filePath` | 模板文件路径 |
| `file_name` | `file_name` | `fileName` | 原始文件名 |
| `file_size` | `file_size` | `fileSize` | 文件大小 |

**注意**：Pydantic的 `to_camel` 配置会自动将蛇形命名转换为驼峰命名：
- `school_name` → `schoolName`
- `degree_level` → `degreeLevel`
- `file_path` → `filePath`

## 修改的文件

### 后端文件
- ✅ `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/entity/vo/template_vo.py`

### 前端文件
- ✅ `RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/thesis/template/list.vue`

## 测试步骤

### 1. 重启后端服务
```bash
# 停止后端
# 重新启动后端
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
python app.py
```

### 2. 清除浏览器缓存
- 按 `Ctrl + Shift + Delete`
- 清除缓存

### 3. 测试新增模板
```
1. 登录系统
2. 进入模板管理页面
3. 点击"新增模板"
4. 填写表单：
   - 模板名称：测试模板
   - 学校名称：清华大学
   - 专业：计算机科学与技术
   - 学位级别：硕士
   - 上传Word模板文件
   - 上传缩略图
5. 点击"确定"
6. ✅ 应该成功保存
```

### 4. 验证数据
```sql
-- 查询最新添加的模板
SELECT 
  template_id,
  template_name,
  school_name,
  major,
  degree_level,
  file_path
FROM ai_write_format_template
ORDER BY create_time DESC
LIMIT 1;
```

## 功能改进

### 修复前
- ❌ 字段不匹配，无法保存
- ❌ 缺少必填字段
- ❌ 使用了不存在的字段

### 修复后
- ✅ 字段完全匹配数据库结构
- ✅ 包含所有必填字段
- ✅ 表单验证正确
- ✅ 显示学校名称和学位级别
- ✅ 支持按学校名称搜索

## 数据库表结构

```sql
CREATE TABLE ai_write_format_template (
  template_id       BIGINT(20)      NOT NULL AUTO_INCREMENT    COMMENT '模板ID',
  template_name     VARCHAR(100)    NOT NULL                   COMMENT '模板名称',
  school_name       VARCHAR(100)    NOT NULL                   COMMENT '学校名称',
  major             VARCHAR(100)    DEFAULT ''                 COMMENT '专业',
  degree_level      VARCHAR(20)     NOT NULL                   COMMENT '学位级别（本科/硕士/博士）',
  
  file_path         VARCHAR(500)    NOT NULL                   COMMENT '模板文件路径',
  file_name         VARCHAR(200)    NOT NULL                   COMMENT '原始文件名',
  file_size         BIGINT(20)      DEFAULT 0                  COMMENT '文件大小（字节）',
  
  format_data       JSON            DEFAULT NULL               COMMENT '格式数据',
  
  is_official       CHAR(1)         DEFAULT '0'                COMMENT '是否官方模板',
  usage_count       INT(11)         DEFAULT 0                  COMMENT '使用次数',
  
  status            CHAR(1)         DEFAULT '0'                COMMENT '状态',
  del_flag          CHAR(1)         DEFAULT '0'                COMMENT '删除标志',
  create_by         VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       DATETIME                                   COMMENT '创建时间',
  update_by         VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       DATETIME                                   COMMENT '更新时间',
  remark            VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  PRIMARY KEY (template_id)
) ENGINE=INNODB COMMENT = '格式模板表';
```

## 相关文档

- [模板上传修复](.kiro/specs/ai-thesis-writing/TEMPLATE_UPLOAD_FIX.md)
- [上传认证修复](.kiro/specs/ai-thesis-writing/UPLOAD_AUTH_FIX.md)
- [Session 12 总结](.kiro/specs/ai-thesis-writing/SESSION_12_TEMPLATE_UPLOAD_FIX.md)

## 总结

本次修复解决了前后端字段不匹配的问题，确保了：
1. ✅ 后端VO模型字段与数据库表结构完全一致
2. ✅ 前端表单包含所有必填字段
3. ✅ 字段命名遵循驼峰/蛇形转换规则
4. ✅ 表单验证规则正确
5. ✅ 用户界面显示正确的信息

现在用户可以正常新增和编辑模板，不再出现字段缺失的错误。
