-- ----------------------------
-- 大纲提示词模板表
-- 与格式模板（学校）关联，不同学校可配置不同提示词
-- ----------------------------
drop table if exists ai_write_outline_prompt_template;
create table ai_write_outline_prompt_template (
  prompt_template_id  bigint(20)      not null auto_increment    comment '主键ID',
  format_template_id  bigint(20)      default null                comment '关联格式模板ID（ai_write_format_template.template_id），NULL表示全局默认',
  name                varchar(100)    default ''                  comment '模板名称',
  template_content    text                                       comment '提示词全文（占位符：{{title}}、{{degree_level}}、{{major}}、{{research_direction}}、{{keywords}}、{{word_count}}、{{format_requirements}}）',
  remark              varchar(500)    default null                comment '备注（说明变量）',
  is_default          char(1)         default '0'                 comment '同一format_template_id下是否默认（0否 1是）',
  sort_order          int(4)          default 0                   comment '排序',
  status              char(1)         default '0'                 comment '状态（0正常 1停用）',
  del_flag            char(1)         default '0'                 comment '删除标志（0代表存在 2代表删除）',
  create_by           varchar(64)     default ''                  comment '创建者',
  create_time         datetime                                   comment '创建时间',
  update_by           varchar(64)     default ''                  comment '更新者',
  update_time         datetime                                   comment '更新时间',
  primary key (prompt_template_id),
  index idx_format_template (format_template_id),
  index idx_status_del (status, del_flag)
) engine=innodb auto_increment=1 comment = '大纲提示词模板表';
