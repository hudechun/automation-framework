-- 大纲提示词模板管理菜单配置SQL
-- 适用于MySQL/PostgreSQL，parent_id=2000 为论文系统父菜单，请按实际调整

-- 1. 插入主菜单（大纲提示词模板）
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('大纲提示词模板', 2000, 6, 'outline-prompt-template', 'thesis/outline-prompt-template/index', 1, 0, 'C', '0', '0', 'thesis:outline-prompt-template:list', 'documentation', 'admin', NOW(), '', NULL, '大纲提示词模板管理菜单');

SET @menu_id = LAST_INSERT_ID();

-- 2. 插入按钮权限
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('大纲提示词模板查询', @menu_id, 1, '', '', 1, 0, 'F', '0', '0', 'thesis:outline-prompt-template:query', '#', 'admin', NOW(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('大纲提示词模板新增', @menu_id, 2, '', '', 1, 0, 'F', '0', '0', 'thesis:outline-prompt-template:add', '#', 'admin', NOW(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('大纲提示词模板修改', @menu_id, 3, '', '', 1, 0, 'F', '0', '0', 'thesis:outline-prompt-template:edit', '#', 'admin', NOW(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('大纲提示词模板删除', @menu_id, 4, '', '', 1, 0, 'F', '0', '0', 'thesis:outline-prompt-template:remove', '#', 'admin', NOW(), '', NULL, '');
