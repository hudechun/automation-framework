-- 学籍备案表菜单（与学籍验证同主菜单 6000，二级菜单 6200）
INSERT INTO sys_menu VALUES(
    6200, '学历备案表', 6000, 2, 'record-filing', 'student/record-filing/index', '', '', 1, 0, 'C', '0', '0',
    'student:recordFiling:list', 'document', 'admin', NOW(), '', NULL, '学历证书电子注册备案表'
);

INSERT INTO sys_menu VALUES(6201, '导入学生', 6200, 1, '', '', '', '', 1, 0, 'F', '0', '0',
    'student:recordFiling:import', '#', 'admin', NOW(), '', NULL, '');
