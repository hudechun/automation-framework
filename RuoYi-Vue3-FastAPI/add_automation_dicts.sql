-- ============================================
-- 自动化管理模块数据字典
-- ============================================
-- 说明：
-- 1. 此脚本会在sys_dict_type和sys_dict_data表中插入数据字典
-- 2. 包含任务状态、任务类型等字典
-- ============================================

USE `ruoyi-fastapi`;

-- ----------------------------
-- 字典类型：任务状态
-- ----------------------------
INSERT INTO sys_dict_type VALUES(
    NULL,                            -- dict_id: 字典主键（自增）
    '任务状态',                       -- dict_name: 字典名称
    'automation_task_status',        -- dict_type: 字典类型
    '0',                             -- status: 状态（0正常 1停用）
    'admin',                         -- create_by: 创建者
    sysdate(),                       -- create_time: 创建时间
    '',                              -- update_by: 更新者
    NULL,                            -- update_time: 更新时间
    '自动化任务状态列表'              -- remark: 备注
);

-- 获取刚插入的字典类型ID
SET @dict_type_id = LAST_INSERT_ID();

-- 任务状态字典数据
INSERT INTO sys_dict_data VALUES(NULL, 1, '待执行', 'pending', 'automation_task_status', '', 'default', 'N', '0', 'admin', sysdate(), '', NULL, '任务已创建，等待执行');
INSERT INTO sys_dict_data VALUES(NULL, 2, '执行中', 'running', 'automation_task_status', '', 'warning', 'N', '0', 'admin', sysdate(), '', NULL, '任务正在执行中');
INSERT INTO sys_dict_data VALUES(NULL, 3, '已完成', 'completed', 'automation_task_status', '', 'success', 'N', '0', 'admin', sysdate(), '', NULL, '任务执行成功');
INSERT INTO sys_dict_data VALUES(NULL, 4, '失败', 'failed', 'automation_task_status', '', 'danger', 'N', '0', 'admin', sysdate(), '', NULL, '任务执行失败');
INSERT INTO sys_dict_data VALUES(NULL, 5, '已取消', 'cancelled', 'automation_task_status', '', 'info', 'N', '0', 'admin', sysdate(), '', NULL, '任务已被取消');

-- ----------------------------
-- 字典类型：任务类型
-- ----------------------------
INSERT INTO sys_dict_type VALUES(
    NULL,
    '任务类型',
    'automation_task_type',
    '0',
    'admin',
    sysdate(),
    '',
    NULL,
    '自动化任务类型列表'
);

-- 任务类型字典数据
INSERT INTO sys_dict_data VALUES(NULL, 1, '浏览器自动化', 'browser', 'automation_task_type', '', 'primary', 'N', '0', 'admin', sysdate(), '', NULL, '基于浏览器的自动化任务');
INSERT INTO sys_dict_data VALUES(NULL, 2, '桌面自动化', 'desktop', 'automation_task_type', '', 'success', 'N', '0', 'admin', sysdate(), '', NULL, '基于桌面的自动化任务');
INSERT INTO sys_dict_data VALUES(NULL, 3, 'API自动化', 'api', 'automation_task_type', '', 'info', 'N', '0', 'admin', sysdate(), '', NULL, '基于API的自动化任务');
INSERT INTO sys_dict_data VALUES(NULL, 4, '混合任务', 'hybrid', 'automation_task_type', '', 'warning', 'N', '0', 'admin', sysdate(), '', NULL, '混合多种自动化方式');

-- ----------------------------
-- 字典类型：会话状态
-- ----------------------------
INSERT INTO sys_dict_type VALUES(
    NULL,
    '会话状态',
    'automation_session_state',
    '0',
    'admin',
    sysdate(),
    '',
    NULL,
    '自动化会话状态列表'
);

-- 会话状态字典数据
INSERT INTO sys_dict_data VALUES(NULL, 1, '已创建', 'created', 'automation_session_state', '', 'default', 'N', '0', 'admin', sysdate(), '', NULL, '会话已创建');
INSERT INTO sys_dict_data VALUES(NULL, 2, '运行中', 'running', 'automation_session_state', '', 'warning', 'N', '0', 'admin', sysdate(), '', NULL, '会话正在运行');
INSERT INTO sys_dict_data VALUES(NULL, 3, '已暂停', 'paused', 'automation_session_state', '', 'info', 'N', '0', 'admin', sysdate(), '', NULL, '会话已暂停');
INSERT INTO sys_dict_data VALUES(NULL, 4, '已完成', 'completed', 'automation_session_state', '', 'success', 'N', '0', 'admin', sysdate(), '', NULL, '会话已完成');
INSERT INTO sys_dict_data VALUES(NULL, 5, '已失败', 'failed', 'automation_session_state', '', 'danger', 'N', '0', 'admin', sysdate(), '', NULL, '会话执行失败');

-- ----------------------------
-- 字典类型：驱动类型
-- ----------------------------
INSERT INTO sys_dict_type VALUES(
    NULL,
    '驱动类型',
    'automation_driver_type',
    '0',
    'admin',
    sysdate(),
    '',
    NULL,
    '自动化驱动类型列表'
);

-- 驱动类型字典数据
INSERT INTO sys_dict_data VALUES(NULL, 1, 'Chrome浏览器', 'chrome', 'automation_driver_type', '', 'primary', 'N', '0', 'admin', sysdate(), '', NULL, 'Chrome浏览器驱动');
INSERT INTO sys_dict_data VALUES(NULL, 2, 'Firefox浏览器', 'firefox', 'automation_driver_type', '', 'warning', 'N', '0', 'admin', sysdate(), '', NULL, 'Firefox浏览器驱动');
INSERT INTO sys_dict_data VALUES(NULL, 3, 'Edge浏览器', 'edge', 'automation_driver_type', '', 'info', 'N', '0', 'admin', sysdate(), '', NULL, 'Edge浏览器驱动');
INSERT INTO sys_dict_data VALUES(NULL, 4, 'Windows桌面', 'windows', 'automation_driver_type', '', 'success', 'N', '0', 'admin', sysdate(), '', NULL, 'Windows桌面驱动');
INSERT INTO sys_dict_data VALUES(NULL, 5, 'MacOS桌面', 'macos', 'automation_driver_type', '', 'default', 'N', '0', 'admin', sysdate(), '', NULL, 'MacOS桌面驱动');
INSERT INTO sys_dict_data VALUES(NULL, 6, 'Linux桌面', 'linux', 'automation_driver_type', '', 'default', 'N', '0', 'admin', sysdate(), '', NULL, 'Linux桌面驱动');

-- ----------------------------
-- 字典类型：模型提供商
-- ----------------------------
INSERT INTO sys_dict_type VALUES(
    NULL,
    '模型提供商',
    'automation_model_provider',
    '0',
    'admin',
    sysdate(),
    '',
    NULL,
    'AI模型提供商列表'
);

-- 模型提供商字典数据
INSERT INTO sys_dict_data VALUES(NULL, 1, '通义千问', 'qwen', 'automation_model_provider', '', 'primary', 'N', '0', 'admin', sysdate(), '', NULL, '阿里云通义千问');
INSERT INTO sys_dict_data VALUES(NULL, 2, 'OpenAI', 'openai', 'automation_model_provider', '', 'success', 'N', '0', 'admin', sysdate(), '', NULL, 'OpenAI GPT系列');
INSERT INTO sys_dict_data VALUES(NULL, 3, '文心一言', 'ernie', 'automation_model_provider', '', 'warning', 'N', '0', 'admin', sysdate(), '', NULL, '百度文心一言');
INSERT INTO sys_dict_data VALUES(NULL, 4, '讯飞星火', 'spark', 'automation_model_provider', '', 'info', 'N', '0', 'admin', sysdate(), '', NULL, '讯飞星火认知大模型');
INSERT INTO sys_dict_data VALUES(NULL, 5, '智谱AI', 'zhipu', 'automation_model_provider', '', 'default', 'N', '0', 'admin', sysdate(), '', NULL, '智谱AI GLM系列');

-- ============================================
-- 验证查询
-- ============================================
-- 查看插入的字典类型：
-- SELECT * FROM sys_dict_type WHERE dict_type LIKE 'automation_%';
--
-- 查看插入的字典数据：
-- SELECT * FROM sys_dict_data WHERE dict_type LIKE 'automation_%' ORDER BY dict_type, dict_sort;
-- ============================================
