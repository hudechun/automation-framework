# photo_blob 在 Navicat 中的查看说明

## 说明

`student_verification.photo_blob` 为 **MEDIUMBLOB** 类型，存储学生照片的二进制数据。渲染报告图时，照片即从此字段读取。

## 为什么在 Navicat 中“看不到”？

1. **BLOB 默认不直接显示**：Navicat 在数据网格中通常将 BLOB 显示为 `(BLOB)`、`(Binary)` 或空白，不会像图片那样预览。
2. **快速打开表不加载 BLOB**：使用「打开表(快速)」时，BLOB 列不会预加载，可能显示为空白或 NULL。

## 如何验证照片是否已存入

在 Navicat 中执行：

```sql
SELECT id, name, verification_code, LENGTH(photo_blob) AS photo_bytes
FROM student_verification
WHERE del_flag = '0'
ORDER BY id DESC;
```

- `photo_bytes > 0`：该行已存储照片
- `photo_bytes IS NULL` 或 `0`：该行未存照片（导入时可能未识别到图片）

## 在 Navicat 中查看 BLOB 内容

1. **显示 BLOB 数据**  
   - 菜单：工具 → 选项 → 外观 → 数据网格  
   - 勾选「在网格中显示 TEXT 和 Blob 字段的数据」

2. **使用“打开表”**  
   - 右键表 →「打开表」（不要用「打开表(快速）」）  
   - BLOB 会以十六进制等形式加载

3. **双击单元格**  
   - 在 `photo_blob` 单元格上双击，可打开二进制查看器

## 渲染有图但数据库“看不到”的说明

如果验证码查询能正常显示带照片的报告图，说明 `photo_blob` 中已有数据，渲染逻辑是直接从数据库读取的。  
Navicat 无法以图片形式预览 BLOB，这是显示限制，并不表示数据不存在。
