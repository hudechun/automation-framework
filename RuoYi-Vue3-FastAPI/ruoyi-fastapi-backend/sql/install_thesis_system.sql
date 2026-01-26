-- ========================================
-- AI论文写作系统完整安装脚本
-- ========================================
-- 执行顺序：
-- 1. thesis_schema.sql - 创建数据库表
-- 2. payment_schema.sql - 创建支付相关表
-- 3. thesis_menus.sql - 创建菜单和权限
-- 4. thesis_dicts.sql - 创建数据字典
-- ========================================

-- 步骤1：创建AI论文写作系统数据库表
SOURCE thesis_schema.sql;

-- 步骤2：创建支付系统数据库表
SOURCE payment_schema.sql;

-- 步骤3：创建菜单和权限配置
SOURCE thesis_menus.sql;

-- 步骤4：创建数据字典配置
SOURCE thesis_dicts.sql;

-- 完成提示
SELECT '========================================' AS '';
SELECT 'AI论文写作系统安装完成！' AS '';
SELECT '========================================' AS '';
SELECT '已创建：' AS '';
SELECT '- 13张业务表' AS '';
SELECT '- 2张支付表' AS '';
SELECT '- 1个一级菜单' AS '';
SELECT '- 5个二级菜单' AS '';
SELECT '- 35个按钮权限' AS '';
SELECT '- 11个数据字典类型' AS '';
SELECT '- 50+个数据字典项' AS '';
SELECT '========================================' AS '';
SELECT '下一步：' AS '';
SELECT '1. 重启后端服务' AS '';
SELECT '2. 登录系统查看菜单' AS '';
SELECT '3. 配置支付密钥' AS '';
SELECT '4. 测试API接口' AS '';
SELECT '========================================' AS '';
