-- 指令系统管理菜单配置SQL
-- 适用于MySQL/PostgreSQL

-- 1. 插入主菜单（指令系统管理）
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('指令系统管理', 2000, 5, 'instruction-system', 'thesis/instruction-system/index', 1, 0, 'C', '0', '0', 'thesis:instruction-system:list', 'guide', 'admin', NOW(), '', NULL, '指令系统管理菜单');

-- 获取刚插入的菜单ID（MySQL使用LAST_INSERT_ID()，PostgreSQL使用RETURNING）
-- MySQL
SET @menu_id = LAST_INSERT_ID();

-- PostgreSQL（需要手动替换@menu_id为实际ID）
-- SELECT currval('sys_menu_id_seq') INTO @menu_id;

-- 2. 插入按钮权限
-- 查询按钮
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('指令系统查询', @menu_id, 1, '', '', 1, 0, 'F', '0', '0', 'thesis:instruction-system:query', '#', 'admin', NOW(), '', NULL, '');

-- 新增按钮
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('指令系统新增', @menu_id, 2, '', '', 1, 0, 'F', '0', '0', 'thesis:instruction-system:add', '#', 'admin', NOW(), '', NULL, '');

-- 修改按钮
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('指令系统修改', @menu_id, 3, '', '', 1, 0, 'F', '0', '0', 'thesis:instruction-system:edit', '#', 'admin', NOW(), '', NULL, '');

-- 删除按钮
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('指令系统删除', @menu_id, 4, '', '', 1, 0, 'F', '0', '0', 'thesis:instruction-system:remove', '#', 'admin', NOW(), '', NULL, '');

-- PostgreSQL版本（如果使用PostgreSQL，请使用以下SQL并手动替换@menu_id）
/*
-- 插入主菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('指令系统管理', 2000, 5, 'instruction-system', 'thesis/instruction-system/index', 1, 0, 'C', '0', '0', 'thesis:instruction-system:list', 'guide', 'admin', NOW(), '', NULL, '指令系统管理菜单')
RETURNING menu_id;

-- 假设返回的menu_id是2001，则使用以下SQL插入按钮
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('指令系统查询', 2001, 1, '', '', 1, 0, 'F', '0', '0', 'thesis:instruction-system:query', '#', 'admin', NOW(), '', NULL, ''),
('指令系统新增', 2001, 2, '', '', 1, 0, 'F', '0', '0', 'thesis:instruction-system:add', '#', 'admin', NOW(), '', NULL, ''),
('指令系统修改', 2001, 3, '', '', 1, 0, 'F', '0', '0', 'thesis:instruction-system:edit', '#', 'admin', NOW(), '', NULL, ''),
('指令系统删除', 2001, 4, '', '', 1, 0, 'F', '0', '0', 'thesis:instruction-system:remove', '#', 'admin', NOW(), '', NULL, '');
*/
