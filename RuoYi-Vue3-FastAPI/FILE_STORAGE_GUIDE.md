# 文件存储位置说明

## 📁 上传文件存储位置

### 默认配置

**配置文件**：`ruoyi-fastapi-backend/config/env.py`

```python
class UploadSettings:
    UPLOAD_PREFIX = '/profile'           # URL前缀
    UPLOAD_PATH = 'vf_admin/upload_path' # 物理存储路径
```

### 实际存储路径

**根目录**：
```
RuoYi-Vue3-FastAPI/vf_admin/upload_path/
```

**按日期分类**：
```
vf_admin/upload_path/
├── 2026/
│   ├── 01/
│   │   ├── 25/
│   │   │   ├── 文件1.doc
│   │   │   ├── 文件2.docx
│   │   │   └── 图片.jpg
│   │   └── 26/
│   └── 02/
└── avatar/          # 用户头像单独存储
    └── 2026/
        └── 01/
```

### URL访问路径

**格式**：
```
http://127.0.0.1:9099/dev-api/profile/upload/YYYY/MM/DD/文件名
```

**示例**：
```
http://127.0.0.1:9099/dev-api/profile/upload/2026/01/25/附件5：中南林业科技大学高等学历继续教育(毕业论文)格式_20260125204223A047.doc
```

**对应物理路径**：
```
RuoYi-Vue3-FastAPI/vf_admin/upload_path/2026/01/25/附件5：中南林业科技大学高等学历继续教育(毕业论文)格式_20260125204223A047.doc
```

## 📂 目录结构

### 完整目录
```
RuoYi-Vue3-FastAPI/
├── vf_admin/
│   ├── upload_path/      # 上传文件存储
│   │   ├── upload/       # 通用上传
│   │   │   └── YYYY/MM/DD/
│   │   └── avatar/       # 用户头像
│   │       └── YYYY/MM/DD/
│   ├── download_path/    # 下载文件存储
│   └── gen_path/         # 代码生成文件
└── ruoyi-fastapi-backend/
    └── config/
        └── env.py        # 配置文件
```

## 🔧 支持的文件类型

### 图片
- `bmp`, `gif`, `jpg`, `jpeg`, `png`

### 文档
- `doc`, `docx` - Word文档
- `xls`, `xlsx` - Excel表格
- `ppt`, `pptx` - PowerPoint演示
- `pdf` - PDF文档
- `txt`, `html`, `htm` - 文本文件

### 压缩文件
- `rar`, `zip`, `gz`, `bz2`

### 视频
- `mp4`, `avi`, `rmvb`

## 📊 数据库存储

### 模板文件信息

**表**：`ai_write_format_template`

```sql
SELECT 
  template_id,
  template_name,
  file_path,      -- 完整URL路径
  file_name,      -- 原始文件名
  file_size       -- 文件大小（字节）
FROM ai_write_format_template;
```

**示例数据**：
```
template_id: 102
template_name: 测试模板
file_path: http://127.0.0.1:9099/dev-api/profile/upload/2026/01/25/附件5_20260125204223A047.doc
file_name: 附件5：中南林业科技大学高等学历继续教育(毕业论文)格式_20260125204223A047.doc
file_size: 245760
```

## 🔍 查找文件

### 方法1：通过数据库查询

```sql
-- 查询最近上传的文件
SELECT 
  template_name,
  file_path,
  file_name,
  create_time
FROM ai_write_format_template
ORDER BY create_time DESC
LIMIT 10;
```

### 方法2：直接查看目录

```bash
# Windows
cd RuoYi-Vue3-FastAPI\vf_admin\upload_path
dir /s

# 查看今天上传的文件
cd 2026\01\25
dir
```

### 方法3：通过URL访问

直接在浏览器中访问文件URL：
```
http://127.0.0.1:9099/dev-api/profile/upload/2026/01/25/文件名.doc
```

## ⚙️ 修改存储路径

如果需要修改存储路径，编辑配置文件：

**文件**：`ruoyi-fastapi-backend/config/env.py`

```python
class UploadSettings:
    UPLOAD_PREFIX = '/profile'
    UPLOAD_PATH = 'vf_admin/upload_path'  # 修改这里
    # 例如改为：
    # UPLOAD_PATH = 'D:/uploads'  # Windows绝对路径
    # UPLOAD_PATH = '/var/uploads'  # Linux绝对路径
```

**注意**：修改后需要重启后端服务。

## 🗑️ 清理文件

### 手动清理

直接删除目录中的文件：
```bash
cd RuoYi-Vue3-FastAPI\vf_admin\upload_path
# 删除指定日期的文件
rmdir /s 2026\01\25
```

### 注意事项

⚠️ 删除物理文件前，应该先删除数据库记录，否则会导致：
- 数据库中有记录但文件不存在
- 用户访问时出现404错误

**正确流程**：
1. 在系统中删除模板（会删除数据库记录）
2. 系统自动删除物理文件（如果实现了）
3. 或手动清理孤立文件

## 📈 磁盘空间管理

### 查看存储空间

```bash
# Windows
dir RuoYi-Vue3-FastAPI\vf_admin\upload_path /s

# 查看文件数量和总大小
```

### 建议

- 定期清理旧文件
- 监控磁盘空间使用
- 考虑使用对象存储（OSS、S3等）存储大文件
- 实现文件自动清理策略

## 🔐 安全建议

1. **限制文件类型**：只允许必要的文件类型
2. **文件大小限制**：当前限制10MB
3. **文件名处理**：自动添加时间戳避免重名
4. **访问控制**：确保只有授权用户可以访问
5. **病毒扫描**：对上传文件进行安全检查

## 📝 相关文档

- [模板上传功能](TEMPLATE_UPLOAD_QUICK_TEST.md)
- [上传认证修复](UPLOAD_AUTH_QUICK_FIX.md)
- [文件名修复](TEMPLATE_FILENAME_FIX.md)
