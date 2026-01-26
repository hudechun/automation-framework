# 数据库表快速参考

## 表前缀
所有表使用 `ai_write_` 前缀

## 表清单（13张）

### 1. 会员套餐表 (ai_write_member_package)
```sql
主键: package_id (bigint)
核心字段:
  - package_name (varchar50) - 套餐名称
  - price (decimal10,2) - 价格
  - duration_days (int) - 时长（天）
  - word_quota (int) - 字数配额（-1无限）
  - usage_quota (int) - 使用次数（-1无限）
  - features (json) - 功能权限配置
  - is_recommended (char1) - 是否推荐
  - badge (varchar20) - 徽章文字
索引: idx_active(status, del_flag)
```

### 2. 用户会员表 (ai_write_user_membership)
```sql
主键: membership_id (bigint)
核心字段:
  - user_id (bigint) - 用户ID
  - package_id (bigint) - 套餐ID
  - total_word_quota (int) - 总字数配额
  - used_word_quota (int) - 已使用字数
  - total_usage_quota (int) - 总使用次数
  - used_usage_quota (int) - 已使用次数
  - start_date (datetime) - 开始时间
  - end_date (datetime) - 结束时间
索引: idx_user(user_id, status), idx_expire(end_date, status)
```

### 3. 用户功能配额表 (ai_write_user_feature_quota)
```sql
主键: quota_id (bigint)
核心字段:
  - user_id (bigint) - 用户ID
  - service_type (varchar30) - 服务类型
  - total_quota (int) - 总配额（字数）
  - used_quota (int) - 已使用配额
  - start_date (datetime) - 开始时间
  - end_date (datetime) - 结束时间
  - source (varchar20) - 来源（package/purchase）
  - source_id (bigint) - 来源ID
索引: idx_user(user_id, service_type, status), idx_expire(end_date, status)
```

### 4. 配额使用记录表 (ai_write_quota_record)
```sql
主键: record_id (bigint)
核心字段:
  - user_id (bigint) - 用户ID
  - thesis_id (bigint) - 论文ID
  - word_count (int) - 字数变动
  - usage_count (int) - 次数变动
  - operation_type (varchar20) - 操作类型
索引: idx_user(user_id, create_time), idx_thesis(thesis_id)
```

### 5. 论文表 (ai_write_thesis)
```sql
主键: thesis_id (bigint)
核心字段:
  - user_id (bigint) - 用户ID
  - template_id (bigint) - 模板ID
  - title (varchar200) - 论文标题
  - major (varchar100) - 专业
  - degree_level (varchar20) - 学位级别
  - research_direction (varchar100) - 研究方向
  - keywords (json) - 关键词
  - thesis_type (varchar50) - 论文类型
  - status (varchar20) - 状态
  - total_words (int) - 总字数
  - last_generated_at (datetime) - 最后生成时间
索引: idx_user(user_id, del_flag), idx_status(status)
```

### 6. 论文大纲表 (ai_write_thesis_outline)
```sql
主键: outline_id (bigint)
核心字段:
  - thesis_id (bigint) - 论文ID
  - structure_type (varchar20) - 结构类型
  - outline_data (json) - 大纲数据
唯一索引: uk_thesis(thesis_id)
```

### 7. 论文章节表 (ai_write_thesis_chapter)
```sql
主键: chapter_id (bigint)
核心字段:
  - thesis_id (bigint) - 论文ID
  - outline_chapter_id (bigint) - 大纲章节ID
  - title (varchar200) - 章节标题
  - level (int) - 章节级别（1-6）
  - order_num (int) - 显示顺序
  - content (longtext) - 章节内容
  - word_count (int) - 字数统计
  - status (varchar20) - 状态
  - generation_prompt (text) - AI生成提示词
  - generation_model (varchar50) - AI生成模型
索引: idx_thesis(thesis_id, order_num)
```

### 8. 论文版本历史表 (ai_write_thesis_version)
```sql
主键: version_id (bigint)
核心字段:
  - thesis_id (bigint) - 论文ID
  - version_number (int) - 版本号
  - snapshot_data (json) - 快照数据
  - change_desc (varchar200) - 变更描述
  - changed_by (varchar64) - 变更人
索引: idx_thesis(thesis_id, version_number)
```

### 9. 格式模板表 (ai_write_format_template)
```sql
主键: template_id (bigint)
核心字段:
  - school_name (varchar100) - 学校名称
  - major (varchar100) - 专业
  - degree_level (varchar20) - 学位级别
  - format_data (json) - 格式数据
  - usage_count (int) - 使用次数
索引: idx_school(school_name), idx_degree(degree_level), idx_status(status, del_flag)
```

### 10. 模板格式规则表 (ai_write_template_format_rule)
```sql
主键: rule_id (bigint)
核心字段:
  - template_id (bigint) - 模板ID
  - rule_type (varchar50) - 规则类型
  - rule_name (varchar100) - 规则名称
  - rule_value (json) - 规则值
  - sort_order (int) - 显示顺序
索引: idx_template(template_id)
```

### 11. 导出记录表 (ai_write_export_record)
```sql
主键: record_id (bigint)
核心字段:
  - user_id (bigint) - 用户ID
  - thesis_id (bigint) - 论文ID
  - file_name (varchar200) - 文件名
  - file_path (varchar500) - 文件路径
  - file_size (bigint) - 文件大小（字节）
索引: idx_user(user_id, del_flag), idx_thesis(thesis_id)
```

### 12. 订单表 (ai_write_order)
```sql
主键: order_id (bigint)
核心字段:
  - order_no (varchar64) - 订单号
  - user_id (bigint) - 用户ID
  - package_id (bigint) - 套餐ID
  - amount (decimal10,2) - 订单金额
  - payment_method (varchar20) - 支付方式
  - payment_time (datetime) - 支付时间
  - transaction_id (varchar64) - 第三方交易号
  - status (varchar20) - 订单状态
  - expired_at (datetime) - 订单过期时间
唯一索引: uk_order_no(order_no)
索引: idx_user(user_id), idx_status(status), idx_expire(expired_at, status)
```

### 13. 功能服务表 (ai_write_feature_service)
```sql
主键: service_id (bigint)
核心字段:
  - service_name (varchar50) - 服务名称
  - service_type (varchar30) - 服务类型
  - price (decimal10,2) - 服务价格
  - billing_unit (varchar20) - 计费单位
  - service_desc (text) - 服务描述
  - sort_order (int) - 显示顺序
索引: idx_type(service_type), idx_status(status, del_flag)
```

## 枚举值参考

### 状态字段 (status)
- `0` - 正常
- `1` - 停用
- `2` - 过期（仅用于会员表）

### 删除标志 (del_flag)
- `0` - 存在
- `2` - 已删除

### 论文状态 (thesis.status)
- `draft` - 草稿
- `generating` - 生成中
- `completed` - 已完成
- `exported` - 已导出

### 章节状态 (chapter.status)
- `pending` - 待生成
- `generating` - 生成中
- `completed` - 已完成
- `edited` - 已编辑

### 订单状态 (order.status)
- `pending` - 待支付
- `paid` - 已支付
- `refunded` - 已退款
- `cancelled` - 已取消

### 服务类型 (service_type)
- `de_ai` - 去AI化处理
- `polish` - 内容润色
- `aigc_detection` - AIGC检测预估
- `plagiarism_check` - 查重率预估
- `manual_review` - 人工审核服务

### 支付方式 (payment_method)
- `wechat` - 微信支付
- `alipay` - 支付宝

### 计费单位 (billing_unit)
- `per_word` - 按字计费
- `per_thousand_words` - 按千字计费
- `per_paper` - 按篇计费

### 配额来源 (source)
- `package` - 来自套餐
- `purchase` - 单独购买

### 操作类型 (operation_type)
- `generate` - 生成扣减
- `refund` - 退还

## RuoYi标准字段

所有表都包含以下标准字段：
```sql
create_by     varchar(64)   - 创建者
create_time   datetime      - 创建时间
update_by     varchar(64)   - 更新者
update_time   datetime      - 更新时间
remark        varchar(500)  - 备注
```

部分表包含：
```sql
del_flag      char(1)       - 删除标志（0存在 2删除）
status        char(1)       - 状态（0正常 1停用）
sort_order    int(4)        - 显示顺序
```

## JSON字段说明

### features (会员套餐功能配置)
```json
{
  "basic_generation": true,
  "de_ai": {"enabled": true, "quota": 50000},
  "polish": {"enabled": true, "quota": 30000},
  "aigc_detection": {"enabled": true, "quota": -1},
  "plagiarism_check": {"enabled": false},
  "manual_review": {"enabled": true, "count": 2},
  "advanced_ai": false,
  "version_limit": 10,
  "priority_support": false
}
```

### keywords (论文关键词)
```json
["人工智能", "机器学习", "深度学习"]
```

### outline_data (大纲数据)
```json
{
  "structure_type": "五段式",
  "chapters": [
    {
      "chapter_id": "1",
      "title": "引言",
      "level": 1,
      "order": 1,
      "description": "研究背景和意义"
    }
  ]
}
```

### format_data (格式数据)
```json
{
  "page_margins": {"top": 2.54, "bottom": 2.54, "left": 3.17, "right": 3.17},
  "page_size": {"width": 21.0, "height": 29.7},
  "styles": {
    "Heading 1": {
      "font_name": "黑体",
      "font_size": 16,
      "bold": true,
      "alignment": "center"
    }
  }
}
```

## 常用查询示例

### 查询用户当前会员信息
```sql
SELECT * FROM ai_write_user_membership 
WHERE user_id = ? AND status = '0' AND del_flag = '0'
AND end_date > NOW()
ORDER BY end_date DESC LIMIT 1;
```

### 查询用户剩余配额
```sql
SELECT 
  total_word_quota - used_word_quota AS remaining_words,
  total_usage_quota - used_usage_quota AS remaining_usage
FROM ai_write_user_membership
WHERE user_id = ? AND status = '0';
```

### 查询用户论文列表
```sql
SELECT * FROM ai_write_thesis
WHERE user_id = ? AND del_flag = '0'
ORDER BY update_time DESC;
```

### 查询论文章节（按顺序）
```sql
SELECT * FROM ai_write_thesis_chapter
WHERE thesis_id = ?
ORDER BY order_num ASC;
```

### 查询待支付订单
```sql
SELECT * FROM ai_write_order
WHERE user_id = ? AND status = 'pending'
AND expired_at > NOW()
ORDER BY create_time DESC;
```

---

**文件位置**: `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_schema.sql`  
**最后更新**: 2026-01-25
