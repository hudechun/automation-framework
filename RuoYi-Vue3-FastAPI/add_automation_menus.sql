-- ============================================
-- 自动化管理模块菜单数据
-- ============================================
-- 说明：
-- 1. 此脚本会在sys_menu表中插入自动化管理的菜单数据
-- 2. 包含一级菜单、二级菜单和按钮权限
-- 3. 执行后需要在角色管理中分配权限
-- ============================================

USE `ruoyi-fastapi`;

-- ----------------------------
-- 一级菜单：自动化管理
-- ----------------------------
INSERT INTO sys_menu (
    menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES (
    '自动化管理',                     -- menu_name: 菜单名称
    0,                               -- parent_id: 父菜单ID (0表示一级菜单)
    5,                               -- order_num: 显示顺序
    'automation',                    -- path: 路由地址
    NULL,                            -- component: 组件路径 (目录类型为NULL)
    '',                              -- query: 路由参数
    '',                              -- route_name: 路由名称
    1,                               -- is_frame: 是否为外链 (0是 1否)
    0,                               -- is_cache: 是否缓存 (0缓存 1不缓存)
    'M',                             -- menu_type: 菜单类型 (M目录 C菜单 F按钮)
    '0',                             -- visible: 菜单状态 (0显示 1隐藏)
    '0',                             -- status: 菜单状态 (0正常 1停用)
    '',                              -- perms: 权限标识
    'robot',                         -- icon: 菜单图标
    'admin',                         -- create_by: 创建者
    sysdate(),                       -- create_time: 创建时间
    '',                              -- update_by: 更新者
    NULL,                            -- update_time: 更新时间
    '自动化管理目录'                  -- remark: 备注
);

-- 获取刚插入的一级菜单ID
SET @automation_menu_id = LAST_INSERT_ID();

-- ----------------------------
-- 二级菜单：任务管理
-- ----------------------------
INSERT INTO sys_menu (
    menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES (
    '任务管理',                       -- menu_name: 菜单名称
    @automation_menu_id,             -- parent_id: 父菜单ID (使用变量)
    1,                               -- order_num: 显示顺序
    'task',                          -- path: 路由地址
    'automation/task/index',         -- component: 组件路径
    '',                              -- query: 路由参数
    '',                              -- route_name: 路由名称
    1,                               -- is_frame: 是否为外链
    0,                               -- is_cache: 是否缓存
    'C',                             -- menu_type: 菜单类型 (C菜单)
    '0',                             -- visible: 菜单状态
    '0',                             -- status: 菜单状态
    'automation:task:list',          -- perms: 权限标识
    'list',                          -- icon: 菜单图标
    'admin',                         -- create_by: 创建者
    sysdate(),                       -- create_time: 创建时间
    '',                              -- update_by: 更新者
    NULL,                            -- update_time: 更新时间
    '任务管理菜单'                    -- remark: 备注
);

-- 获取任务管理菜单ID
SET @task_menu_id = LAST_INSERT_ID();

-- ----------------------------
-- 任务管理按钮权限
-- ----------------------------
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('任务查询', @task_menu_id, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:task:query', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('任务新增', @task_menu_id, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:task:add', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('任务修改', @task_menu_id, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:task:edit', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('任务删除', @task_menu_id, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:task:remove', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('任务执行', @task_menu_id, 5, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:task:execute', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('任务导出', @task_menu_id, 6, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:task:export', '#', 'admin', sysdate(), '', NULL, '');

-- ----------------------------
-- 二级菜单：会话管理
-- ----------------------------
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('会话管理', @automation_menu_id, 2, 'session', 'automation/session/index', '', '', 1, 0, 'C', '0', '0', 'automation:session:list', 'connection', 'admin', sysdate(), '', NULL, '会话管理菜单');

SET @session_menu_id = LAST_INSERT_ID();

-- 会话管理按钮权限
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('会话查询', @session_menu_id, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:session:query', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('会话删除', @session_menu_id, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:session:remove', '#', 'admin', sysdate(), '', NULL, '');

-- ----------------------------
-- 二级菜单：执行记录
-- ----------------------------
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('执行记录', @automation_menu_id, 3, 'execution', 'automation/execution/index', '', '', 1, 0, 'C', '0', '0', 'automation:execution:list', 'documentation', 'admin', sysdate(), '', NULL, '执行记录菜单');

SET @execution_menu_id = LAST_INSERT_ID();

-- 执行记录按钮权限
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('记录查询', @execution_menu_id, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:execution:query', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('记录删除', @execution_menu_id, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:execution:remove', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('记录导出', @execution_menu_id, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:execution:export', '#', 'admin', sysdate(), '', NULL, '');

-- ----------------------------
-- 二级菜单：模型配置
-- ----------------------------
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('模型配置', @automation_menu_id, 4, 'config', 'automation/config/index', '', '', 1, 0, 'C', '0', '0', 'automation:config:list', 'skill', 'admin', sysdate(), '', NULL, '模型配置菜单');

SET @config_menu_id = LAST_INSERT_ID();

-- 模型配置按钮权限
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('配置查询', @config_menu_id, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:config:query', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('配置新增', @config_menu_id, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:config:add', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('配置修改', @config_menu_id, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:config:edit', '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('配置删除', @config_menu_id, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'automation:config:remove', '#', 'admin', sysdate(), '', NULL, '');

-- ----------------------------
-- 自动分配权限给超级管理员
-- ----------------------------
-- 为角色ID=1（超级管理员）分配所有自动化管理权限
INSERT IGNORE INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu 
WHERE menu_name IN ('自动化管理', '任务管理', '会话管理', '执行记录', '模型配置')
   OR perms LIKE 'automation:%';

-- ============================================
-- 执行完成后的操作
-- ============================================
-- 1. 查看插入的菜单：
--    SELECT menu_id, menu_name, parent_id, perms FROM sys_menu 
--    WHERE menu_name LIKE '%自动化%' OR menu_name LIKE '%任务%' 
--       OR menu_name LIKE '%会话%' OR menu_name LIKE '%执行%' OR menu_name LIKE '%模型%'
--    ORDER BY menu_id;
--
-- 2. 权限已自动分配给超级管理员
--
-- 3. 刷新浏览器查看菜单（Ctrl+Shift+R）
-- ============================================
