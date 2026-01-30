-- 学籍验证菜单（菜单ID 6000 系列，避免与系统/论文冲突）
-- 一级菜单：学籍验证
INSERT INTO sys_menu VALUES(
    6000, '学籍验证', 0, 6, 'student', NULL, '', '', 1, 0, 'M', '0', '0', '',
    'education', 'admin', NOW(), '', NULL, '学籍验证系统'
);

-- 二级菜单：学生验证
INSERT INTO sys_menu VALUES(
    6100, '学生验证', 6000, 1, 'verification', 'student/verification/index', '', '', 1, 0, 'C', '0', '0',
    'student:verification:list', 'user', 'admin', NOW(), '', NULL, '学籍学生列表与导入'
);

-- 按钮权限（可选）
INSERT INTO sys_menu VALUES(
    6101, '导入学生', 6100, 1, '', '', '', '', 1, 0, 'F', '0', '0',
    'student:verification:import', '#', 'admin', NOW(), '', NULL, ''
);
