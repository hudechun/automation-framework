-- ----------------------------
-- AI论文写作系统数据库表设计
-- 表前缀: ai_write_
-- 符合RuoYi规范
-- ----------------------------

-- ----------------------------
-- 1、会员套餐表
-- ----------------------------
drop table if exists ai_write_member_package;
create table ai_write_member_package (
  package_id        bigint(20)      not null auto_increment    comment '套餐ID',
  package_name      varchar(50)     not null                   comment '套餐名称',
  package_desc      varchar(200)    default ''                 comment '套餐描述',
  price             decimal(10,2)   not null                   comment '套餐价格',
  duration_days     int(11)         not null                   comment '套餐时长（天）',
  
  word_quota        int(11)         not null                   comment '字数配额（-1表示无限）',
  usage_quota       int(11)         not null                   comment '使用次数配额（-1表示无限）',
  
  features          json            not null                   comment '功能权限配置（JSON格式）',
  
  is_recommended    char(1)         default '0'                comment '是否推荐（0否 1是）',
  badge             varchar(20)     default ''                 comment '徽章文字',
  sort_order        int(4)          default 0                  comment '显示顺序',
  
  status            char(1)         default '0'                comment '状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (package_id)
) engine=innodb auto_increment=100 comment = '会员套餐表';

-- ----------------------------
-- 初始化-会员套餐表数据
-- ----------------------------
insert into ai_write_member_package values(1, '免费体验版', '体验AI论文写作基础功能', 0.00, 30, 5000, 1, 
  '{"basic_generation": true, "de_ai": {"enabled": false, "quota": 0}, "polish": {"enabled": false, "quota": 0}, "aigc_detection": {"enabled": false, "quota": 0}, "plagiarism_check": {"enabled": false}, "manual_review": {"enabled": false, "count": 0}, "advanced_ai": false, "version_limit": 1, "priority_support": false}',
  '0', '', 1, '0', '0', 'admin', sysdate(), '', null, '免费体验版，限5000字');

insert into ai_write_member_package values(2, '专业版', '适合毕业论文写作', 199.00, 30, 100000, 30,
  '{"basic_generation": true, "de_ai": {"enabled": true, "quota": 50000}, "polish": {"enabled": true, "quota": 30000}, "aigc_detection": {"enabled": true, "quota": -1}, "plagiarism_check": {"enabled": false}, "manual_review": {"enabled": false, "count": 0}, "advanced_ai": false, "version_limit": 10, "priority_support": false}',
  '1', '最受欢迎', 2, '0', '0', 'admin', sysdate(), '', null, '专业版，10万字配额');

insert into ai_write_member_package values(3, '旗舰版', '无限使用，全功能开放', 499.00, 30, -1, -1,
  '{"basic_generation": true, "de_ai": {"enabled": true, "quota": -1}, "polish": {"enabled": true, "quota": -1}, "aigc_detection": {"enabled": true, "quota": -1}, "plagiarism_check": {"enabled": true, "quota": -1}, "manual_review": {"enabled": true, "count": 5}, "advanced_ai": true, "version_limit": -1, "priority_support": true}',
  '0', '性价比之选', 3, '0', '0', 'admin', sysdate(), '', null, '旗舰版，无限使用');


-- ----------------------------
-- 2、用户会员表
-- ----------------------------
drop table if exists ai_write_user_membership;
create table ai_write_user_membership (
  membership_id     bigint(20)      not null auto_increment    comment '会员ID',
  user_id           bigint(20)      not null                   comment '用户ID',
  package_id        bigint(20)      not null                   comment '套餐ID',
  
  total_word_quota  int(11)         not null                   comment '总字数配额',
  used_word_quota   int(11)         default 0                  comment '已使用字数',
  
  total_usage_quota int(11)         not null                   comment '总使用次数',
  used_usage_quota  int(11)         default 0                  comment '已使用次数',
  
  start_date        datetime        not null                   comment '开始时间',
  end_date          datetime        not null                   comment '结束时间',
  
  status            char(1)         default '0'                comment '状态（0正常 1停用 2过期）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (membership_id),
  index idx_user (user_id, status),
  index idx_expire (end_date, status)
) engine=innodb auto_increment=100 comment = '用户会员表';


-- ----------------------------
-- 3、用户功能配额表
-- ----------------------------
drop table if exists ai_write_user_feature_quota;
create table ai_write_user_feature_quota (
  quota_id          bigint(20)      not null auto_increment    comment '配额ID',
  user_id           bigint(20)      not null                   comment '用户ID',
  service_type      varchar(30)     not null                   comment '服务类型（de_ai/polish/aigc_detection/plagiarism_check）',
  
  total_quota       int(11)         not null                   comment '总配额（字数）',
  used_quota        int(11)         default 0                  comment '已使用配额',
  
  start_date        datetime        not null                   comment '开始时间',
  end_date          datetime        not null                   comment '结束时间',
  
  source            varchar(20)     not null                   comment '来源（package/purchase）',
  source_id         bigint(20)      default null               comment '来源ID（套餐ID或订单ID）',
  
  status            char(1)         default '0'                comment '状态（0正常 1停用 2过期）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (quota_id),
  index idx_user (user_id, service_type, status),
  index idx_expire (end_date, status)
) engine=innodb auto_increment=100 comment = '用户功能配额表';


-- ----------------------------
-- 4、配额使用记录表
-- ----------------------------
drop table if exists ai_write_quota_record;
create table ai_write_quota_record (
  record_id         bigint(20)      not null auto_increment    comment '记录ID',
  user_id           bigint(20)      not null                   comment '用户ID',
  thesis_id         bigint(20)      default null               comment '论文ID',
  
  word_count        int(11)         not null                   comment '字数变动（正数为扣减，负数为退还）',
  usage_count       int(11)         not null                   comment '次数变动',
  
  operation_type    varchar(20)     not null                   comment '操作类型（generate/refund）',
  
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (record_id),
  index idx_user (user_id, create_time),
  index idx_thesis (thesis_id)
) engine=innodb auto_increment=100 comment = '配额使用记录表';


-- ----------------------------
-- 5、论文表
-- ----------------------------
drop table if exists ai_write_thesis;
create table ai_write_thesis (
  thesis_id         bigint(20)      not null auto_increment    comment '论文ID',
  user_id           bigint(20)      not null                   comment '用户ID',
  template_id       bigint(20)      default null               comment '模板ID',
  
  title             varchar(200)    not null                   comment '论文标题',
  major             varchar(100)    default ''                 comment '专业',
  degree_level      varchar(20)     default ''                 comment '学位级别（本科/硕士/博士）',
  research_direction varchar(100)   default ''                 comment '研究方向',
  keywords          json            default null               comment '关键词（JSON数组）',
  thesis_type       varchar(50)     default ''                 comment '论文类型（理论研究/实证研究/综述）',
  
  status            varchar(20)     not null                   comment '状态（draft/generating/completed/exported）',
  
  total_words       int(11)         default 0                  comment '总字数',
  
  last_generated_at datetime        default null               comment '最后生成时间',
  
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (thesis_id),
  index idx_user (user_id, del_flag),
  index idx_status (status)
) engine=innodb auto_increment=100 comment = '论文表';


-- ----------------------------
-- 6、论文大纲表
-- ----------------------------
drop table if exists ai_write_thesis_outline;
create table ai_write_thesis_outline (
  outline_id        bigint(20)      not null auto_increment    comment '大纲ID',
  thesis_id         bigint(20)      not null                   comment '论文ID',
  structure_type    varchar(20)     default ''                 comment '结构类型（三段式/五段式）',
  
  outline_data      json            not null                   comment '大纲数据（JSON格式）',
  
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (outline_id),
  unique key uk_thesis (thesis_id)
) engine=innodb auto_increment=100 comment = '论文大纲表';


-- ----------------------------
-- 7、论文章节表
-- ----------------------------
drop table if exists ai_write_thesis_chapter;
create table ai_write_thesis_chapter (
  chapter_id        bigint(20)      not null auto_increment    comment '章节ID',
  thesis_id         bigint(20)      not null                   comment '论文ID',
  outline_chapter_id bigint(20)     default null               comment '大纲章节ID',
  
  title             varchar(200)    not null                   comment '章节标题',
  level             int(4)          not null                   comment '章节级别（1-6）',
  order_num         int(4)          not null                   comment '显示顺序',
  
  content           longtext        default null               comment '章节内容',
  word_count        int(11)         default 0                  comment '字数统计',
  
  status            varchar(20)     not null                   comment '状态（pending/generating/completed/edited）',
  
  generation_prompt text            default null               comment 'AI生成提示词',
  generation_model  varchar(50)     default ''                 comment 'AI生成模型',
  
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (chapter_id),
  index idx_thesis (thesis_id, order_num)
) engine=innodb auto_increment=100 comment = '论文章节表';


-- ----------------------------
-- 8、格式模板表
-- ----------------------------
drop table if exists ai_write_format_template;
create table ai_write_format_template (
  template_id       bigint(20)      not null auto_increment    comment '模板ID',
  template_name     varchar(100)    not null                   comment '模板名称',
  school_name       varchar(100)    not null                   comment '学校名称',
  major             varchar(100)    default ''                 comment '专业',
  degree_level      varchar(20)     not null                   comment '学位级别（本科/硕士/博士）',
  
  file_path         varchar(500)    not null                   comment '模板文件路径',
  file_name         varchar(200)    not null                   comment '原始文件名',
  file_size         bigint(20)      default 0                  comment '文件大小（字节）',
  
  format_data       json            default null               comment '格式数据（JSON格式，解析后的格式规则）',
  
  is_official       char(1)         default '0'                comment '是否官方模板（0否 1是）',
  usage_count       int(11)         default 0                  comment '使用次数',
  
  status            char(1)         default '0'                comment '状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (template_id),
  index idx_school (school_name),
  index idx_degree (degree_level),
  index idx_official (is_official),
  index idx_status (status, del_flag)
) engine=innodb auto_increment=100 comment = '格式模板表';


-- ----------------------------
-- 9、模板格式规则表
-- ----------------------------
drop table if exists ai_write_template_format_rule;
create table ai_write_template_format_rule (
  rule_id           bigint(20)      not null auto_increment    comment '规则ID',
  template_id       bigint(20)      not null                   comment '模板ID',
  
  rule_type         varchar(50)     not null                   comment '规则类型（page_margin/font/line_spacing/numbering）',
  rule_name         varchar(100)    not null                   comment '规则名称',
  rule_value        json            not null                   comment '规则值（JSON格式）',
  
  sort_order        int(4)          default 0                  comment '显示顺序',
  
  status            char(1)         default '0'                comment '状态（0正常 1停用）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (rule_id),
  index idx_template (template_id)
) engine=innodb auto_increment=100 comment = '模板格式规则表';


-- ----------------------------
-- 10、导出记录表
-- ----------------------------
drop table if exists ai_write_export_record;
create table ai_write_export_record (
  record_id         bigint(20)      not null auto_increment    comment '记录ID',
  user_id           bigint(20)      not null                   comment '用户ID',
  thesis_id         bigint(20)      not null                   comment '论文ID',
  
  file_name         varchar(200)    not null                   comment '文件名',
  file_path         varchar(500)    not null                   comment '文件路径',
  file_size         bigint(20)      not null                   comment '文件大小（字节）',
  
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (record_id),
  index idx_user (user_id, del_flag),
  index idx_thesis (thesis_id)
) engine=innodb auto_increment=100 comment = '导出记录表';


-- ----------------------------
-- 11、订单表
-- ----------------------------
drop table if exists ai_write_order;
create table ai_write_order (
  order_id          bigint(20)      not null auto_increment    comment '订单ID',
  order_no          varchar(64)     not null                   comment '订单号',
  user_id           bigint(20)      not null                   comment '用户ID',
  package_id        bigint(20)      not null                   comment '套餐ID',
  
  amount            decimal(10,2)   not null                   comment '订单金额',
  
  payment_method    varchar(20)     not null                   comment '支付方式（wechat/alipay）',
  payment_time      datetime        default null               comment '支付时间',
  transaction_id    varchar(64)     default ''                 comment '第三方交易号',
  
  status            varchar(20)     not null                   comment '订单状态（pending/paid/refunded/cancelled）',
  
  expired_at        datetime        not null                   comment '订单过期时间',
  
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (order_id),
  unique key uk_order_no (order_no),
  index idx_user (user_id),
  index idx_status (status),
  index idx_expire (expired_at, status)
) engine=innodb auto_increment=100 comment = '订单表';


-- ----------------------------
-- 12、功能服务表
-- ----------------------------
drop table if exists ai_write_feature_service;
create table ai_write_feature_service (
  service_id        bigint(20)      not null auto_increment    comment '服务ID',
  service_name      varchar(50)     not null                   comment '服务名称',
  service_type      varchar(30)     not null                   comment '服务类型（de_ai/polish/aigc_detection/plagiarism_check/manual_review）',
  
  price             decimal(10,2)   not null                   comment '服务价格',
  billing_unit      varchar(20)     not null                   comment '计费单位（per_word/per_thousand_words/per_paper）',
  
  service_desc      text            default null               comment '服务描述',
  
  sort_order        int(4)          default 0                  comment '显示顺序',
  
  status            char(1)         default '0'                comment '状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (service_id),
  index idx_type (service_type),
  index idx_status (status, del_flag)
) engine=innodb auto_increment=100 comment = '功能服务表';

-- ----------------------------
-- 初始化-功能服务表数据
-- ----------------------------
insert into ai_write_feature_service values(1, '去AI化处理', 'de_ai', 0.05, 'per_thousand_words', '改写AI痕迹明显的句子，增加人性化表达', 1, '0', '0', 'admin', sysdate(), '', null, '');
insert into ai_write_feature_service values(2, '内容润色', 'polish', 0.08, 'per_thousand_words', '语法检查、逻辑优化、表达优化', 2, '0', '0', 'admin', sysdate(), '', null, '');
insert into ai_write_feature_service values(3, 'AIGC检测预估', 'aigc_detection', 0.02, 'per_thousand_words', '预估AI生成概率，标注高风险句子', 3, '0', '0', 'admin', sysdate(), '', null, '');
insert into ai_write_feature_service values(4, '查重率预估', 'plagiarism_check', 0.10, 'per_thousand_words', '与文献库对比，计算相似度', 4, '0', '0', 'admin', sysdate(), '', null, '');
insert into ai_write_feature_service values(5, '人工审核服务', 'manual_review', 50.00, 'per_paper', '专业编辑审核，提供修改建议（3-5个工作日）', 5, '0', '0', 'admin', sysdate(), '', null, '');


-- ----------------------------
-- 13、论文版本历史表
-- ----------------------------
drop table if exists ai_write_thesis_version;
create table ai_write_thesis_version (
  version_id        bigint(20)      not null auto_increment    comment '版本ID',
  thesis_id         bigint(20)      not null                   comment '论文ID',
  version_number    int(11)         not null                   comment '版本号',
  
  snapshot_data     json            not null                   comment '快照数据（JSON格式）',
  
  change_desc       varchar(200)    default ''                 comment '变更描述',
  changed_by        varchar(64)     default ''                 comment '变更人',
  
  create_time       datetime                                   comment '创建时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (version_id),
  index idx_thesis (thesis_id, version_number)
) engine=innodb auto_increment=100 comment = '论文版本历史表';
