# 论文格式模板上传与管理指南

## 1. 概述

本文档说明论文格式模板的上传、解析、存储和应用流程。支持用户和管理员上传.docx格式的论文模板。

## 2. 数据库设计

### 2.1 格式模板表 (ai_write_format_template)

```sql
CREATE TABLE ai_write_format_template (
  template_id       bigint(20)      NOT NULL AUTO_INCREMENT    COMMENT '模板ID',
  template_name     varchar(100)    NOT NULL                   COMMENT '模板名称',
  school_name       varchar(100)    NOT NULL                   COMMENT '学校名称',
  major             varchar(100)    DEFAULT ''                 COMMENT '专业',
  degree_level      varchar(20)     NOT NULL                   COMMENT '学位级别（本科/硕士/博士）',
  
  file_path         varchar(500)    NOT NULL                   COMMENT '模板文件路径',
  file_name         varchar(200)    NOT NULL                   COMMENT '原始文件名',
  file_size         bigint(20)      DEFAULT 0                  COMMENT '文件大小（字节）',
  
  format_data       json            DEFAULT NULL               COMMENT '格式数据（JSON格式，解析后的格式规则）',
  
  is_official       char(1)         DEFAULT '0'                COMMENT '是否官方模板（0否 1是）',
  usage_count       int(11)         DEFAULT 0                  COMMENT '使用次数',
  
  status            char(1)         DEFAULT '0'                COMMENT '状态（0正常 1停用）',
  del_flag          char(1)         DEFAULT '0'                COMMENT '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       datetime                                   COMMENT '创建时间',
  update_by         varchar(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       datetime                                   COMMENT '更新时间',
  remark            varchar(500)    DEFAULT NULL               COMMENT '备注',
  PRIMARY KEY (template_id),
  INDEX idx_school (school_name),
  INDEX idx_degree (degree_level),
  INDEX idx_official (is_official),
  INDEX idx_status (status, del_flag)
) ENGINE=InnoDB COMMENT='格式模板表';
```

### 2.2 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| template_id | bigint | 模板ID（主键） | 1 |
| template_name | varchar(100) | 模板名称 | "清华大学硕士论文模板" |
| school_name | varchar(100) | 学校名称 | "清华大学" |
| major | varchar(100) | 专业（可选） | "计算机科学与技术" |
| degree_level | varchar(20) | 学位级别 | "本科"/"硕士"/"博士" |
| file_path | varchar(500) | 文件存储路径 | "/uploads/templates/2024/01/xxx.docx" |
| file_name | varchar(200) | 原始文件名 | "清华大学硕士论文模板.docx" |
| file_size | bigint | 文件大小（字节） | 1048576 |
| format_data | json | 解析后的格式规则 | 见下文JSON结构 |
| is_official | char(1) | 是否官方模板 | "0"=用户上传, "1"=管理员上传 |
| usage_count | int | 使用次数 | 0 |

## 3. 模板上传流程

### 3.1 上传接口

**端点**: `POST /api/thesis/template/upload`

**权限**: 
- 普通用户: 可上传个人模板 (is_official=0)
- 管理员: 可上传官方模板 (is_official=1)

**请求参数**:
```json
{
  "template_name": "清华大学硕士论文模板",
  "school_name": "清华大学",
  "major": "计算机科学与技术",
  "degree_level": "硕士",
  "file": "<multipart/form-data>",
  "is_official": "0"  // 管理员可设置为1
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "上传成功",
  "data": {
    "template_id": 1,
    "template_name": "清华大学硕士论文模板",
    "file_path": "/uploads/templates/2024/01/xxx.docx",
    "parse_status": "pending"  // pending/parsing/completed/failed
  }
}
```

### 3.2 文件存储规则

**存储路径结构**:
```
/vf_admin/upload_path/templates/
  ├── 2024/
  │   ├── 01/
  │   │   ├── {uuid}_清华大学硕士论文模板.docx
  │   │   └── {uuid}_北京大学本科论文模板.docx
  │   └── 02/
  └── 2025/
```

**命名规则**:
- 格式: `{uuid}_{原始文件名}`
- UUID: 32位唯一标识符
- 保留原始文件名便于识别

## 4. 模板解析流程

### 4.1 解析器 (DocxParser)

使用 `python-docx` 库解析Word文档，提取格式信息。

**解析内容**:
1. **页面设置**: 页边距、纸张大小、方向
2. **样式信息**: 字体、字号、行距、对齐方式
3. **章节结构**: 标题层级、编号格式
4. **页眉页脚**: 格式和内容
5. **段落格式**: 首行缩进、段前段后间距

**实现位置**: `module_thesis/utils/docx_parser.py`

```python
class DocxParser:
    """Word文档格式解析器"""
    
    def parse_template(self, file_path: str) -> dict:
        """
        解析Word模板文件
        
        Args:
            file_path: 模板文件路径
            
        Returns:
            格式数据字典
        """
        doc = Document(file_path)
        
        return {
            "page_setup": self._parse_page_setup(doc),
            "styles": self._parse_styles(doc),
            "numbering": self._parse_numbering(doc),
            "header_footer": self._parse_header_footer(doc)
        }
```

### 4.2 格式数据JSON结构

```json
{
  "page_setup": {
    "page_width": "21cm",
    "page_height": "29.7cm",
    "orientation": "portrait",
    "margins": {
      "top": "2.54cm",
      "bottom": "2.54cm",
      "left": "3.17cm",
      "right": "3.17cm"
    }
  },
  "styles": {
    "heading1": {
      "font_name": "黑体",
      "font_size": "16pt",
      "bold": true,
      "alignment": "center",
      "line_spacing": 1.5
    },
    "heading2": {
      "font_name": "黑体",
      "font_size": "14pt",
      "bold": true,
      "alignment": "left",
      "line_spacing": 1.5
    },
    "normal": {
      "font_name": "宋体",
      "font_size": "12pt",
      "bold": false,
      "alignment": "justify",
      "line_spacing": 1.5,
      "first_line_indent": "2em"
    }
  },
  "numbering": {
    "heading1": "第{n}章",
    "heading2": "{n}.{m}",
    "heading3": "{n}.{m}.{k}"
  },
  "header_footer": {
    "header": {
      "content": "{school_name}硕士学位论文",
      "alignment": "center",
      "font_size": "10pt"
    },
    "footer": {
      "content": "第{page}页 共{total}页",
      "alignment": "center",
      "font_size": "10pt"
    }
  }
}
```

## 5. 模板管理功能

### 5.1 模板列表查询

**端点**: `GET /api/thesis/template/list`

**查询参数**:
```json
{
  "school_name": "清华大学",      // 可选
  "degree_level": "硕士",         // 可选
  "major": "计算机",              // 可选，模糊查询
  "is_official": "1",             // 可选，筛选官方模板
  "page_num": 1,
  "page_size": 10
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "total": 50,
    "rows": [
      {
        "template_id": 1,
        "template_name": "清华大学硕士论文模板",
        "school_name": "清华大学",
        "major": "计算机科学与技术",
        "degree_level": "硕士",
        "file_name": "清华大学硕士论文模板.docx",
        "file_size": 1048576,
        "is_official": "1",
        "usage_count": 150,
        "create_time": "2024-01-01 10:00:00"
      }
    ]
  }
}
```

### 5.2 模板详情查询

**端点**: `GET /api/thesis/template/{template_id}`

**响应**:
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "template_id": 1,
    "template_name": "清华大学硕士论文模板",
    "school_name": "清华大学",
    "major": "计算机科学与技术",
    "degree_level": "硕士",
    "file_path": "/uploads/templates/2024/01/xxx.docx",
    "file_name": "清华大学硕士论文模板.docx",
    "file_size": 1048576,
    "format_data": { /* 完整的格式数据 */ },
    "is_official": "1",
    "usage_count": 150,
    "status": "0",
    "create_time": "2024-01-01 10:00:00"
  }
}
```

### 5.3 模板下载

**端点**: `GET /api/thesis/template/{template_id}/download`

**响应**: 直接返回文件流

### 5.4 模板删除（管理员）

**端点**: `DELETE /api/thesis/template/{template_id}`

**权限**: 仅管理员

**响应**:
```json
{
  "code": 200,
  "msg": "删除成功"
}
```

## 6. 模板应用流程

### 6.1 创建论文时选择模板

**端点**: `POST /api/thesis/paper/create`

**请求参数**:
```json
{
  "title": "基于深度学习的图像识别研究",
  "template_id": 1,  // 选择的模板ID
  "thesis_type": "硕士论文",
  "keywords": "深度学习,图像识别",
  "abstract": "本文研究..."
}
```

**处理流程**:
1. 查询模板的 `format_data`
2. 将格式规则应用到论文
3. 模板的 `usage_count` +1

### 6.2 导出时应用格式

**端点**: `POST /api/thesis/paper/{thesis_id}/export`

**请求参数**:
```json
{
  "format": "docx",
  "template_id": 1  // 可选，不传则使用论文创建时的模板
}
```

**处理流程**:
1. 读取论文内容和章节
2. 读取模板的 `format_data`
3. 使用 `DocxFormatter` 生成Word文档
4. 应用所有格式规则
5. 返回下载链接

## 7. 权限控制

### 7.1 用户权限

| 操作 | 普通用户 | 管理员 |
|------|---------|--------|
| 上传个人模板 | ✓ | ✓ |
| 上传官方模板 | ✗ | ✓ |
| 查看所有模板 | ✓ | ✓ |
| 下载模板 | ✓ | ✓ |
| 删除自己的模板 | ✓ | ✓ |
| 删除他人的模板 | ✗ | ✓ |
| 编辑模板信息 | 仅自己的 | 所有 |

### 7.2 权限验证

```python
# 检查是否为管理员
def check_admin_permission(user_id: int) -> bool:
    # 查询用户角色
    # 返回是否为管理员
    pass

# 检查模板所有权
def check_template_owner(user_id: int, template_id: int) -> bool:
    # 查询模板创建者
    # 返回是否为所有者
    pass
```

## 8. 前端实现要点

### 8.1 模板上传页面

**组件**: `TemplateUpload.vue`

**功能**:
- 文件选择（限制.docx格式）
- 表单填写（模板名称、学校、专业、学历）
- 上传进度显示
- 解析状态提示

**示例代码**:
```vue
<template>
  <el-form :model="form" :rules="rules">
    <el-form-item label="模板名称" prop="template_name">
      <el-input v-model="form.template_name" />
    </el-form-item>
    
    <el-form-item label="学校名称" prop="school_name">
      <el-input v-model="form.school_name" />
    </el-form-item>
    
    <el-form-item label="专业" prop="major">
      <el-input v-model="form.major" />
    </el-form-item>
    
    <el-form-item label="学历层次" prop="degree_level">
      <el-select v-model="form.degree_level">
        <el-option label="本科" value="本科" />
        <el-option label="硕士" value="硕士" />
        <el-option label="博士" value="博士" />
      </el-select>
    </el-form-item>
    
    <el-form-item label="模板文件" prop="file">
      <el-upload
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".docx"
      >
        <el-button type="primary">选择文件</el-button>
      </el-upload>
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="submitUpload">上传</el-button>
    </el-form-item>
  </el-form>
</template>
```

### 8.2 模板列表页面

**组件**: `TemplateList.vue`

**功能**:
- 筛选器（学校、专业、学历）
- 模板卡片展示
- 预览、下载、应用按钮
- 官方模板标识

### 8.3 模板选择器

**组件**: `TemplateSelector.vue`

**功能**:
- 在创建论文时选择模板
- 模板预览
- 热门推荐

## 9. 注意事项

### 9.1 文件安全

1. **文件类型验证**: 仅允许.docx格式
2. **文件大小限制**: 最大10MB
3. **病毒扫描**: 上传后进行病毒扫描
4. **存储隔离**: 用户文件和官方文件分开存储

### 9.2 解析异常处理

1. **格式不规范**: 提示用户修改模板
2. **解析失败**: 记录错误日志，通知管理员
3. **部分解析**: 保存已解析的部分，标记未解析项

### 9.3 性能优化

1. **异步解析**: 上传后异步解析，不阻塞用户
2. **缓存**: 解析结果缓存到Redis
3. **CDN**: 官方模板使用CDN加速下载

## 10. 开发任务清单

- [ ] 创建模板上传接口
- [ ] 实现DocxParser解析器
- [ ] 实现DocxFormatter格式化器
- [ ] 创建模板管理CRUD接口
- [ ] 实现权限验证中间件
- [ ] 前端模板上传页面
- [ ] 前端模板列表页面
- [ ] 前端模板选择器组件
- [ ] 编写单元测试
- [ ] 编写集成测试

---

**最后更新**: 2026-01-25  
**文档版本**: v1.0
