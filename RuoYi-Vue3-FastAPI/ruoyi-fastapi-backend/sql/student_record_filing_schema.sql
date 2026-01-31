-- ----------------------------
-- 学籍备案表（教育部学历证书电子注册备案表，模板2）
-- 与 student_verification 独立，字段对应 layout_config2
-- ----------------------------
DROP TABLE IF EXISTS student_record_filing;
CREATE TABLE student_record_filing (
  id                   BIGINT(20)      NOT NULL AUTO_INCREMENT    COMMENT '主键ID',
  verification_code    VARCHAR(16)     NOT NULL                   COMMENT '在线验证码（16位，唯一）',
  update_date          VARCHAR(32)     DEFAULT ''                 COMMENT '更新日期',
  name                 VARCHAR(64)     NOT NULL                   COMMENT '姓名',
  gender               VARCHAR(8)      DEFAULT ''                 COMMENT '性别',
  birth_date           VARCHAR(32)     DEFAULT ''                 COMMENT '出生日期',
  enrollment_date      VARCHAR(32)     DEFAULT ''                 COMMENT '入学日期',
  graduation_date      VARCHAR(32)     DEFAULT ''                 COMMENT '毕（结）业日期',
  school_name          VARCHAR(200)    DEFAULT ''                 COMMENT '学校名称',
  major                VARCHAR(100)    DEFAULT ''                 COMMENT '专业',
  duration             VARCHAR(32)     DEFAULT ''                 COMMENT '学制',
  level                VARCHAR(32)     DEFAULT ''                 COMMENT '层次',
  education_type       VARCHAR(64)     DEFAULT ''                 COMMENT '学历类别',
  learning_form        VARCHAR(64)     DEFAULT ''                 COMMENT '学习形式',
  graduation_status    VARCHAR(32)     DEFAULT ''                 COMMENT '毕（结）业（毕业/结业）',
  certificate_no       VARCHAR(64)     DEFAULT ''                 COMMENT '证书编号',
  president_name       VARCHAR(64)     DEFAULT ''                 COMMENT '校（院）长姓名',
  valid_until          DATE            NOT NULL                   COMMENT '验证有效日期（截止日）',
  photo_blob           MEDIUMBLOB      DEFAULT NULL               COMMENT '学生照片（二进制）',
  del_flag             CHAR(1)         DEFAULT '0'                COMMENT '删除标志（0存在 2删除）',
  create_by            VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time          DATETIME                                   COMMENT '创建时间',
  update_by            VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time          DATETIME                                   COMMENT '更新时间',
  remark               VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE KEY uk_verification_code (verification_code),
  KEY idx_valid_until (valid_until),
  KEY idx_name (name)
) ENGINE=INNODB AUTO_INCREMENT=1 COMMENT = '学籍备案表（学历证书电子注册备案表）';
