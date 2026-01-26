-- AI论文写作系统菜单和权限配置
-- 菜单ID从5000开始，避免与系统菜单冲突

-- ========================================
-- 一级菜单：AI论文写作
-- ========================================
INSERT INTO sys_menu VALUES(
    5000, 'AI论文写作', 0, 5, 'thesis', NULL, '', '', 1, 0, 'M', '0', '0', '', 
    'documentation', 'admin', NOW(), '', NULL, 'AI论文写作系统'
);

-- ========================================
-- 二级菜单
-- ========================================

-- 会员管理
INSERT INTO sys_menu VALUES(
    5100, '会员管理', 5000, 1, 'member', 'thesis/member/index', '', '', 1, 0, 'C', '0', '0', 
    'thesis:member:list', 'peoples', 'admin', NOW(), '', NULL, '会员管理菜单'
);

-- 论文管理
INSERT INTO sys_menu VALUES(
    5200, '论文管理', 5000, 2, 'paper', 'thesis/paper/index', '', '', 1, 0, 'C', '0', '0', 
    'thesis:thesis:list', 'documentation', 'admin', NOW(), '', NULL, '论文管理菜单'
);

-- 模板管理
INSERT INTO sys_menu VALUES(
    5300, '模板管理', 5000, 3, 'template', 'thesis/template/index', '', '', 1, 0, 'C', '0', '0', 
    'thesis:template:list', 'form', 'admin', NOW(), '', NULL, '模板管理菜单'
);

-- 订单管理
INSERT INTO sys_menu VALUES(
    5400, '订单管理', 5000, 4, 'order', 'thesis/order/index', '', '', 1, 0, 'C', '0', '0', 
    'thesis:order:list', 'shopping', 'admin', NOW(), '', NULL, '订单管理菜单'
);

-- 支付管理
INSERT INTO sys_menu VALUES(
    5500, '支付管理', 5000, 5, 'payment', 'thesis/payment/index', '', '', 1, 0, 'C', '0', '0', 
    'thesis:payment:list', 'money', 'admin', NOW(), '', NULL, '支付管理菜单'
);

-- ========================================
-- 会员管理按钮权限（5100系列）
-- ========================================

-- 查询会员套餐
INSERT INTO sys_menu VALUES(
    5101, '查询会员套餐', 5100, 1, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:member:package:query', '#', 'admin', NOW(), '', NULL, ''
);

-- 新增会员套餐
INSERT INTO sys_menu VALUES(
    5102, '新增会员套餐', 5100, 2, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:member:package:add', '#', 'admin', NOW(), '', NULL, ''
);

-- 修改会员套餐
INSERT INTO sys_menu VALUES(
    5103, '修改会员套餐', 5100, 3, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:member:package:edit', '#', 'admin', NOW(), '', NULL, ''
);

-- 删除会员套餐
INSERT INTO sys_menu VALUES(
    5104, '删除会员套餐', 5100, 4, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:member:package:remove', '#', 'admin', NOW(), '', NULL, ''
);

-- 查询用户会员
INSERT INTO sys_menu VALUES(
    5105, '查询用户会员', 5100, 5, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:member:user:query', '#', 'admin', NOW(), '', NULL, ''
);

-- 激活会员
INSERT INTO sys_menu VALUES(
    5106, '激活会员', 5100, 6, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:member:activate', '#', 'admin', NOW(), '', NULL, ''
);

-- 查询配额
INSERT INTO sys_menu VALUES(
    5107, '查询配额', 5100, 7, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:member:quota:query', '#', 'admin', NOW(), '', NULL, ''
);

-- 增加配额
INSERT INTO sys_menu VALUES(
    5108, '增加配额', 5100, 8, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:member:quota:add', '#', 'admin', NOW(), '', NULL, ''
);

-- 配额补偿
INSERT INTO sys_menu VALUES(
    5109, '配额补偿', 5100, 9, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:member:quota:compensate', '#', 'admin', NOW(), '', NULL, ''
);

-- ========================================
-- 论文管理按钮权限（5200系列）
-- ========================================

-- 查询论文
INSERT INTO sys_menu VALUES(
    5201, '查询论文', 5200, 1, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:thesis:query', '#', 'admin', NOW(), '', NULL, ''
);

-- 新增论文
INSERT INTO sys_menu VALUES(
    5202, '新增论文', 5200, 2, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:thesis:add', '#', 'admin', NOW(), '', NULL, ''
);

-- 修改论文
INSERT INTO sys_menu VALUES(
    5203, '修改论文', 5200, 3, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:thesis:edit', '#', 'admin', NOW(), '', NULL, ''
);

-- 删除论文
INSERT INTO sys_menu VALUES(
    5204, '删除论文', 5200, 4, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:thesis:remove', '#', 'admin', NOW(), '', NULL, ''
);

-- 生成大纲
INSERT INTO sys_menu VALUES(
    5205, '生成大纲', 5200, 5, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:thesis:outline', '#', 'admin', NOW(), '', NULL, ''
);

-- 生成章节
INSERT INTO sys_menu VALUES(
    5206, '生成章节', 5200, 6, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:thesis:chapter', '#', 'admin', NOW(), '', NULL, ''
);

-- 导出论文
INSERT INTO sys_menu VALUES(
    5207, '导出论文', 5200, 7, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:thesis:export', '#', 'admin', NOW(), '', NULL, ''
);

-- ========================================
-- 模板管理按钮权限（5300系列）
-- ========================================

-- 查询模板
INSERT INTO sys_menu VALUES(
    5301, '查询模板', 5300, 1, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:template:query', '#', 'admin', NOW(), '', NULL, ''
);

-- 新增模板
INSERT INTO sys_menu VALUES(
    5302, '新增模板', 5300, 2, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:template:add', '#', 'admin', NOW(), '', NULL, ''
);

-- 修改模板
INSERT INTO sys_menu VALUES(
    5303, '修改模板', 5300, 3, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:template:edit', '#', 'admin', NOW(), '', NULL, ''
);

-- 删除模板
INSERT INTO sys_menu VALUES(
    5304, '删除模板', 5300, 4, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:template:remove', '#', 'admin', NOW(), '', NULL, ''
);

-- 上传模板
INSERT INTO sys_menu VALUES(
    5305, '上传模板', 5300, 5, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:template:upload', '#', 'admin', NOW(), '', NULL, ''
);

-- 应用模板
INSERT INTO sys_menu VALUES(
    5306, '应用模板', 5300, 6, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:template:apply', '#', 'admin', NOW(), '', NULL, ''
);

-- ========================================
-- 订单管理按钮权限（5400系列）
-- ========================================

-- 查询订单
INSERT INTO sys_menu VALUES(
    5401, '查询订单', 5400, 1, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:order:query', '#', 'admin', NOW(), '', NULL, ''
);

-- 新增订单
INSERT INTO sys_menu VALUES(
    5402, '新增订单', 5400, 2, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:order:add', '#', 'admin', NOW(), '', NULL, ''
);

-- 取消订单
INSERT INTO sys_menu VALUES(
    5403, '取消订单', 5400, 3, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:order:cancel', '#', 'admin', NOW(), '', NULL, ''
);

-- 退款
INSERT INTO sys_menu VALUES(
    5404, '退款', 5400, 4, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:order:refund', '#', 'admin', NOW(), '', NULL, ''
);

-- 导出记录
INSERT INTO sys_menu VALUES(
    5405, '导出记录', 5400, 5, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:order:export:query', '#', 'admin', NOW(), '', NULL, ''
);

-- ========================================
-- 支付管理按钮权限（5500系列）
-- ========================================

-- 查询支付渠道
INSERT INTO sys_menu VALUES(
    5501, '查询支付渠道', 5500, 1, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:payment:channel:query', '#', 'admin', NOW(), '', NULL, ''
);

-- 创建支付
INSERT INTO sys_menu VALUES(
    5502, '创建支付', 5500, 2, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:payment:create', '#', 'admin', NOW(), '', NULL, ''
);

-- 查询支付
INSERT INTO sys_menu VALUES(
    5503, '查询支付', 5500, 3, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:payment:query', '#', 'admin', NOW(), '', NULL, ''
);

-- 退款
INSERT INTO sys_menu VALUES(
    5504, '退款', 5500, 4, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:payment:refund', '#', 'admin', NOW(), '', NULL, ''
);

-- 配置管理
INSERT INTO sys_menu VALUES(
    5505, '配置管理', 5500, 5, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:payment:config', '#', 'admin', NOW(), '', NULL, ''
);

-- 配置编辑
INSERT INTO sys_menu VALUES(
    5506, '配置编辑', 5500, 6, '', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:payment:config:edit', '#', 'admin', NOW(), '', NULL, ''
);
