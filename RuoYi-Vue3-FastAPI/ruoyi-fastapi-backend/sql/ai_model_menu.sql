-- ============================================================
-- AI模型配置菜单
-- 菜单ID: 5600系列（AI模型配置）
-- ============================================================

-- 删除旧菜单（如果存在）
DELETE FROM sys_menu WHERE menu_id >= 5600 AND menu_id < 5700;

-- ========================================
-- 二级菜单：AI模型配置
-- ========================================
INSERT INTO sys_menu VALUES(
    5600, 'AI模型配置', 5000, 6, 'ai-model', 'thesis/ai-model/index', '', '', 1, 0, 'C', '0', '0', 
    'thesis:ai-model:list', 'cpu', 'admin', NOW(), '', NULL, 'AI模型配置管理'
);

-- ========================================
-- AI模型配置按钮权限（5600系列）
-- ========================================

-- 查询AI模型
INSERT INTO sys_menu VALUES(
    5601, '查询AI模型', 5600, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:ai-model:query', '#', 'admin', NOW(), '', NULL, ''
);

-- 新增AI模型
INSERT INTO sys_menu VALUES(
    5602, '新增AI模型', 5600, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:ai-model:add', '#', 'admin', NOW(), '', NULL, ''
);

-- 修改AI模型
INSERT INTO sys_menu VALUES(
    5603, '修改AI模型', 5600, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:ai-model:edit', '#', 'admin', NOW(), '', NULL, ''
);

-- 删除AI模型
INSERT INTO sys_menu VALUES(
    5604, '删除AI模型', 5600, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:ai-model:remove', '#', 'admin', NOW(), '', NULL, ''
);

-- 测试AI模型连接
INSERT INTO sys_menu VALUES(
    5605, '测试连接', 5600, 5, '#', '', '', '', 1, 0, 'F', '0', '0', 
    'thesis:ai-model:test', '#', 'admin', NOW(), '', NULL, ''
);

-- 验证菜单已创建
SELECT menu_id, menu_name, parent_id, order_num, perms 
FROM sys_menu 
WHERE menu_id >= 5600 AND menu_id < 5700
ORDER BY menu_id;
