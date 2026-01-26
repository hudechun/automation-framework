-- AI论文写作系统数据字典配置

-- ========================================
-- 会员套餐类型
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '会员套餐类型', 'thesis_package_type', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统会员套餐类型'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '基础版', 'basic', 'thesis_package_type', '', 'default', 'N', '0', 
    'admin', NOW(), '', NULL, '基础版会员套餐'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '专业版', 'professional', 'thesis_package_type', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '专业版会员套餐'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 3, '旗舰版', 'flagship', 'thesis_package_type', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '旗舰版会员套餐'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 4, '企业版', 'enterprise', 'thesis_package_type', '', 'warning', 'N', '0', 
    'admin', NOW(), '', NULL, '企业版会员套餐'
);

-- ========================================
-- 会员状态
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '会员状态', 'thesis_member_status', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统会员状态'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '正常', 'active', 'thesis_member_status', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '会员正常'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '已过期', 'expired', 'thesis_member_status', '', 'danger', 'N', '0', 
    'admin', NOW(), '', NULL, '会员已过期'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 3, '已冻结', 'frozen', 'thesis_member_status', '', 'warning', 'N', '0', 
    'admin', NOW(), '', NULL, '会员已冻结'
);

-- ========================================
-- 论文状态
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '论文状态', 'thesis_status', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统论文状态'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '草稿', 'draft', 'thesis_status', '', 'info', 'N', '0', 
    'admin', NOW(), '', NULL, '论文草稿'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '大纲生成中', 'outline_generating', 'thesis_status', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '大纲生成中'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 3, '大纲已完成', 'outline_completed', 'thesis_status', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '大纲已完成'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 4, '内容生成中', 'content_generating', 'thesis_status', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '内容生成中'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 5, '已完成', 'completed', 'thesis_status', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '论文已完成'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 6, '生成失败', 'failed', 'thesis_status', '', 'danger', 'N', '0', 
    'admin', NOW(), '', NULL, '生成失败'
);

-- ========================================
-- 论文类型
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '论文类型', 'thesis_type', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统论文类型'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '学术论文', 'academic', 'thesis_type', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '学术论文'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '毕业论文', 'graduation', 'thesis_type', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '毕业论文'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 3, '研究报告', 'research', 'thesis_type', '', 'info', 'N', '0', 
    'admin', NOW(), '', NULL, '研究报告'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 4, '综述论文', 'review', 'thesis_type', '', 'warning', 'N', '0', 
    'admin', NOW(), '', NULL, '综述论文'
);

-- ========================================
-- 模板类型
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '模板类型', 'thesis_template_type', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统模板类型'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '官方模板', 'official', 'thesis_template_type', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '官方提供的模板'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '用户上传', 'user_upload', 'thesis_template_type', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '用户上传的模板'
);

-- ========================================
-- 订单类型
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '订单类型', 'thesis_order_type', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统订单类型'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '会员套餐', 'membership', 'thesis_order_type', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '购买会员套餐'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '配额充值', 'quota', 'thesis_order_type', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '配额充值'
);

-- ========================================
-- 订单状态
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '订单状态', 'thesis_order_status', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统订单状态'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '待支付', 'pending', 'thesis_order_status', '', 'info', 'N', '0', 
    'admin', NOW(), '', NULL, '订单待支付'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '已支付', 'paid', 'thesis_order_status', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '订单已支付'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 3, '已取消', 'cancelled', 'thesis_order_status', '', 'warning', 'N', '0', 
    'admin', NOW(), '', NULL, '订单已取消'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 4, '已退款', 'refunded', 'thesis_order_status', '', 'danger', 'N', '0', 
    'admin', NOW(), '', NULL, '订单已退款'
);

-- ========================================
-- 支付渠道
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '支付渠道', 'thesis_payment_channel', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统支付渠道'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '支付宝PC', 'alipay_pc', 'thesis_payment_channel', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '支付宝PC支付'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '支付宝手机', 'alipay_wap', 'thesis_payment_channel', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '支付宝手机支付'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 3, '支付宝扫码', 'alipay_qr', 'thesis_payment_channel', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '支付宝扫码支付'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 4, '微信公众号', 'wx_pub', 'thesis_payment_channel', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '微信公众号支付'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 5, '微信小程序', 'wx_lite', 'thesis_payment_channel', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '微信小程序支付'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 6, '微信H5', 'wx_wap', 'thesis_payment_channel', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '微信H5支付'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 7, '微信扫码', 'wx_pub_qr', 'thesis_payment_channel', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '微信扫码支付'
);

-- ========================================
-- 支付状态
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '支付状态', 'thesis_payment_status', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统支付状态'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '待支付', 'pending', 'thesis_payment_status', '', 'info', 'N', '0', 
    'admin', NOW(), '', NULL, '待支付'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '支付成功', 'success', 'thesis_payment_status', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '支付成功'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 3, '支付失败', 'failed', 'thesis_payment_status', '', 'danger', 'N', '0', 
    'admin', NOW(), '', NULL, '支付失败'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 4, '已退款', 'refunded', 'thesis_payment_status', '', 'warning', 'N', '0', 
    'admin', NOW(), '', NULL, '已退款'
);

-- ========================================
-- 配额类型
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '配额类型', 'thesis_quota_type', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统配额类型'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, '论文生成', 'thesis_generation', 'thesis_quota_type', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, '论文生成配额'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, '大纲生成', 'outline_generation', 'thesis_quota_type', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, '大纲生成配额'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 3, '章节生成', 'chapter_generation', 'thesis_quota_type', '', 'info', 'N', '0', 
    'admin', NOW(), '', NULL, '章节生成配额'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 4, '导出次数', 'export', 'thesis_quota_type', '', 'warning', 'N', '0', 
    'admin', NOW(), '', NULL, '导出次数配额'
);

-- ========================================
-- 导出格式
-- ========================================
INSERT INTO sys_dict_type VALUES(
    NULL, '导出格式', 'thesis_export_format', '0', 
    'admin', NOW(), '', NULL, 'AI论文写作系统导出格式'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 1, 'Word文档', 'docx', 'thesis_export_format', '', 'primary', 'N', '0', 
    'admin', NOW(), '', NULL, 'Word文档格式'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 2, 'PDF文档', 'pdf', 'thesis_export_format', '', 'danger', 'N', '0', 
    'admin', NOW(), '', NULL, 'PDF文档格式'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 3, 'Markdown', 'md', 'thesis_export_format', '', 'info', 'N', '0', 
    'admin', NOW(), '', NULL, 'Markdown格式'
);

INSERT INTO sys_dict_data VALUES(
    NULL, 4, 'LaTeX', 'tex', 'thesis_export_format', '', 'success', 'N', '0', 
    'admin', NOW(), '', NULL, 'LaTeX格式'
);
