-- 为已存在的 student_verification 表添加学习形式字段
-- 若表为新建（执行过 student_verification_schema.sql）可跳过此脚本
ALTER TABLE student_verification ADD COLUMN learning_form varchar(64) DEFAULT '' COMMENT '学习形式' AFTER education_type;
