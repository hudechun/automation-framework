"""
学籍验证学生表实体
"""
from datetime import date, datetime

from sqlalchemy import CHAR, BigInteger, Column, Date, DateTime, LargeBinary, String

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class StudentVerification(Base):
    """
    学籍验证学生表：layout_config 字段 + 验证码 + 有效期 + 照片 BLOB
    """

    __tablename__ = "student_verification"
    __table_args__ = {"comment": "学籍验证学生表"}

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="主键ID")
    verification_code = Column(String(16), nullable=False, unique=True, comment="在线验证码（16位大写字母+数字）")
    update_date = Column(String(32), nullable=True, server_default="''", comment="更新日期")
    name = Column(String(64), nullable=False, comment="姓名")
    gender = Column(String(8), nullable=True, server_default="''", comment="性别")
    birth_date = Column(String(32), nullable=True, server_default="''", comment="出生日期")
    nation = Column(String(32), nullable=True, server_default="''", comment="民族")
    school_name = Column(String(200), nullable=True, server_default="''", comment="学校名称")
    level = Column(String(32), nullable=True, server_default="''", comment="层次")
    major = Column(String(100), nullable=True, server_default="''", comment="专业")
    duration = Column(String(32), nullable=True, server_default="''", comment="学制")
    education_type = Column(String(64), nullable=True, server_default="''", comment="学历类别")
    learning_form = Column(String(64), nullable=True, server_default="''", comment="学习形式")
    branch = Column(String(100), nullable=True, server_default="''", comment="分院")
    department = Column(String(100), nullable=True, server_default="''", comment="系所")
    enrollment_date = Column(String(32), nullable=True, server_default="''", comment="入学日期")
    graduation_date = Column(String(32), nullable=True, server_default="''", comment="预计毕业日期")
    valid_until = Column(Date, nullable=False, comment="验证有效日期（截止日）")
    photo_blob = Column(
        LargeBinary,
        nullable=True,
        comment="学生照片（二进制）",
    )
    del_flag = Column(CHAR(1), nullable=True, server_default="'0'", comment="删除标志（0存在 2删除）")
    create_by = Column(String(64), nullable=True, server_default="''", comment="创建者")
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), nullable=True, server_default="''", comment="更新者")
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment="备注",
    )
