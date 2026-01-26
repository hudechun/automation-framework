-- 更新AI论文写作系统菜单组件路径
-- 修复组件路径不匹配的问题

-- 更新会员管理组件路径
UPDATE sys_menu SET component = 'thesis/member/index' WHERE menu_id = 5100;

-- 更新论文管理组件路径
UPDATE sys_menu SET component = 'thesis/paper/index' WHERE menu_id = 5200;

-- 更新模板管理组件路径
UPDATE sys_menu SET component = 'thesis/template/index' WHERE menu_id = 5300;

-- 更新订单管理组件路径
UPDATE sys_menu SET component = 'thesis/order/index' WHERE menu_id = 5400;

-- 更新支付管理组件路径
UPDATE sys_menu SET component = 'thesis/payment/index' WHERE menu_id = 5500;
