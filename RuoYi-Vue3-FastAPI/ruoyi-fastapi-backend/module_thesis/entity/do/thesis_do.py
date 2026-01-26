"""
论文管理相关实体类
"""
from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String, Text, JSON

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class AiWriteThesis(Base):
    """
    论文表
    """

    __tablename__ = 'ai_write_thesis'
    __table_args__ = {'comment': '论文表'}

    thesis_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='论文ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    template_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='模板ID',
    )
    
    title = Column(String(200), nullable=False, comment='论文标题')
    major = Column(String(100), nullable=True, server_default="''", comment='专业')
    degree_level = Column(String(20), nullable=True, server_default="''", comment='学位级别（本科/硕士/博士）')
    research_direction = Column(String(100), nullable=True, server_default="''", comment='研究方向')
    keywords = Column(
        JSON,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='关键词（JSON数组）',
    )
    thesis_type = Column(String(50), nullable=True, server_default="''", comment='论文类型（理论研究/实证研究/综述）')
    
    status = Column(String(20), nullable=False, comment='状态（draft/generating/completed/exported/formatted）')
    
    total_words = Column(Integer, nullable=True, server_default='0', comment='总字数')
    
    last_generated_at = Column(
        DateTime,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='最后生成时间',
    )
    
    del_flag = Column(CHAR(1), nullable=True, server_default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )


class AiWriteThesisOutline(Base):
    """
    论文大纲表
    """

    __tablename__ = 'ai_write_thesis_outline'
    __table_args__ = {'comment': '论文大纲表'}

    outline_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='大纲ID')
    thesis_id = Column(BigInteger, nullable=False, unique=True, comment='论文ID')
    structure_type = Column(String(20), nullable=True, server_default="''", comment='结构类型（三段式/五段式）')
    
    outline_data = Column(JSON, nullable=False, comment='大纲数据（JSON格式）')
    
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )


class AiWriteThesisChapter(Base):
    """
    论文章节表
    """

    __tablename__ = 'ai_write_thesis_chapter'
    __table_args__ = {'comment': '论文章节表'}

    chapter_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='章节ID')
    thesis_id = Column(BigInteger, nullable=False, comment='论文ID')
    outline_chapter_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='大纲章节ID',
    )
    
    title = Column(String(200), nullable=False, comment='章节标题')
    level = Column(Integer, nullable=False, comment='章节级别（1-6）')
    order_num = Column(Integer, nullable=False, comment='显示顺序')
    
    content = Column(
        Text,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='章节内容',
    )
    word_count = Column(Integer, nullable=True, server_default='0', comment='字数统计')
    
    status = Column(String(20), nullable=False, comment='状态（pending/generating/completed/edited）')
    
    generation_prompt = Column(
        Text,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='AI生成提示词',
    )
    generation_model = Column(String(50), nullable=True, server_default="''", comment='AI生成模型')
    
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )


class AiWriteThesisVersion(Base):
    """
    论文版本历史表
    """

    __tablename__ = 'ai_write_thesis_version'
    __table_args__ = {'comment': '论文版本历史表'}

    version_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='版本ID')
    thesis_id = Column(BigInteger, nullable=False, comment='论文ID')
    version_number = Column(Integer, nullable=False, comment='版本号')
    
    snapshot_data = Column(JSON, nullable=False, comment='快照数据（JSON格式）')
    
    change_desc = Column(String(200), nullable=True, server_default="''", comment='变更描述')
    changed_by = Column(String(64), nullable=True, server_default="''", comment='变更人')
    
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )
