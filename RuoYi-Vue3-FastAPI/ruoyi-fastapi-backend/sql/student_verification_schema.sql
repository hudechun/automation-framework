-- ----------------------------
-- 学籍验证学生表（一行一条记录，含照片BLOB、验证码、有效期）
-- ----------------------------
drop table if exists student_verification;
create table student_verification (
  id                   bigint(20)      not null auto_increment    comment '主键ID',
  verification_code    varchar(16)     not null                   comment '在线验证码（16位大写字母+数字，唯一）',
  update_date          varchar(32)     default ''                 comment '更新日期',
  name                 varchar(64)     not null                   comment '姓名',
  gender               varchar(8)      default ''                 comment '性别',
  birth_date           varchar(32)     default ''                 comment '出生日期',
  nation               varchar(32)     default ''                 comment '民族',
  school_name          varchar(200)    default ''                 comment '学校名称',
  level                varchar(32)     default ''                 comment '层次',
  major                varchar(100)   default ''                 comment '专业',
  duration             varchar(32)     default ''                 comment '学制',
  education_type       varchar(64)    default ''                 comment '学历类别',
  learning_form        varchar(64)    default ''                 comment '学习形式',
  branch               varchar(100)   default ''                 comment '分院',
  department           varchar(100)   default ''                 comment '系所',
  enrollment_date      varchar(32)    default ''                 comment '入学日期',
  graduation_date      varchar(32)    default ''                 comment '预计毕业日期',
  valid_until          date            not null                   comment '验证有效日期（截止日，超出则H5显示已过期）',
  photo_blob           mediumblob      default null               comment '学生照片（二进制）',
  del_flag             char(1)         default '0'                comment '删除标志（0存在 2删除）',
  create_by            varchar(64)     default ''                 comment '创建者',
  create_time          datetime                                   comment '创建时间',
  update_by            varchar(64)     default ''                 comment '更新者',
  update_time          datetime                                   comment '更新时间',
  remark               varchar(500)   default null                comment '备注',
  primary key (id),
  unique key uk_verification_code (verification_code),
  key idx_valid_until (valid_until),
  key idx_name (name)
) engine=innodb auto_increment=1 comment = '学籍验证学生表';
