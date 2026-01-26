-- ============================================================
-- 系统AI模型配置菜单
-- ============================================================

-- 删除旧的论文模块AI模型菜单（如果存在）
DELETE FROM sys_menu WHERE menu_name = 'AI模型配置' AND parent_id IN (
  SELECT menu_id FROM (SELECT menu_id FROM sys_menu WHERE menu_name = '论文管理') AS temp
);

-- 插入系统管理下的AI模型配置菜单
INSERT INTO sys_menu VALUES 
(NULL, 'AI模型配置', 1, 8, 'ai-model', 'system/ai-model/index', '', 1, 0, 'C', '0', '0', 'system:ai-model:list', 'robot', 'admin', NOW(), '', NULL, 'AI模型配置管理');

-- 获取刚插入的菜单ID
SET @ai_model_menu_id = LAST_INSERT_ID();

-- 插入子菜单（按钮权限）
INSERT INTO sys_menu VALUES 
(NULL, '查询AI模型', @ai_model_menu_id, 1, '', '', '', 1, 0, 'F', '0', '0', 'system:ai-model:query', '#', 'admin', NOW(), '', NULL, ''),
(NULL, '新增AI模型', @ai_model_menu_id, 2, '', '', '', 1, 0, 'F', '0', '0', 'system:ai-model:add', '#', 'admin', NOW(), '', NULL, ''),
(NULL, '修改AI模型', @ai_model_menu_id, 3, '', '', '', 1, 0, 'F', '0', '0', 'system:ai-model:edit', '#', 'admin', NOW(), '', NULL, ''),
(NULL, '删除AI模型', @ai_model_menu_id, 4, '', '', '', 1, 0, 'F', '0', '0', 'system:ai-model:remove', '#', 'admin', NOW(), '', NULL, ''),
(NULL, '测试AI模型', @ai_model_menu_id, 5, '', '', '', 1, 0, 'F', '0', '0', 'system:ai-model:test', '#', 'admin', NOW(), '', NULL, '');
