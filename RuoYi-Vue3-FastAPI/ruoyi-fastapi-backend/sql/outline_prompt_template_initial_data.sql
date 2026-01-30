-- ----------------------------
-- 大纲提示词模板表 - 初始数据（全局默认）
-- 执行前请先执行 outline_prompt_template_schema.sql 建表
-- ----------------------------
-- 说明：template_content 较长，若需从 Python 常量生成可运行：
--   cd sql && python -c "
--   import sys; sys.path.insert(0, '..');
--   from module_thesis.config.default_outline_prompt_template import DEFAULT_OUTLINE_PROMPT_TEMPLATE_CONTENT, DEFAULT_OUTLINE_PROMPT_TEMPLATE_REMARK;
--   c = DEFAULT_OUTLINE_PROMPT_TEMPLATE_CONTENT.replace(chr(39), chr(39)+chr(39));
--   r = (DEFAULT_OUTLINE_PROMPT_TEMPLATE_REMARK or '').replace(chr(39), chr(39)+chr(39));
--   print(\"INSERT INTO ai_write_outline_prompt_template (format_template_id, name, template_content, remark, is_default, sort_order, status, del_flag, create_by, create_time, update_by, update_time) VALUES (NULL, '全局默认大纲提示词', '\" + c + \"', '\" + r + \"', '1', 0, '0', '0', 'system', NOW(), 'system', NOW());\")
--   "
-- 下面为占位符版本的简化内容，保证系统可运行；完整内容见 default_outline_prompt_template.py
INSERT INTO ai_write_outline_prompt_template (
  format_template_id, name, template_content, remark, is_default, sort_order, status, del_flag, create_by, create_time, update_by, update_time
) VALUES (
  NULL,
  '全局默认大纲提示词',
  '## 论文信息\n论文标题：{{title}}\n专业：{{major}}\n学位级别：{{degree_level}}\n研究方向：{{research_direction}}\n关键词：{{keywords}}\n字数：{{word_count}}\n\n{{format_requirements}}\n\n## 内容要求\n生成完整的论文大纲，符合{{degree_level}}论文的学术规范。只返回JSON，含 title 与 chapters（含 chapter_title、chapter_number、sections）。结论的 chapter_number 必须为正文章节数+1，不能为null。',
  '{{title}}论文标题/论文表；{{degree_level}}学历/格式模板表；{{major}}专业/格式模板表；{{research_direction}}研究方向/论文表；{{keywords}}关键字/论文表；{{word_count}}字数/论文表；{{format_requirements}}格式要求/代码注入',
  '1',
  0,
  '0',
  '0',
  'system',
  NOW(),
  'system',
  NOW()
);
