"""
学籍备案表实体（学历证书电子注册备案表，模板2）
"""
from datetime import date, datetime

from sqlalchemy import CHAR, BigInteger, Column, Date, DateTime, LargeBinary, String

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class StudentRecordFiling(Base):
    """学籍备案表：layout_config2 字段 + 验证码 + 有效期 + 照片"""

    __tablename__ = "student_record_filing"
    __table_args__ = {"comment": "学籍备案表"}

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="主键ID")
    verification_code = Column(String(16), nullable=False, unique=True, comment="在线验证码")
    update_date = Column(String(32), nullable=True, server_default="''", comment="更新日期")
    name = Column(String(64), nullable=False, comment="姓名")
    gender = Column(String(8), nullable=True, server_default="''", comment="性别")
    birth_date = Column(String(32), nullable=True, server_default="''", comment="出生日期")
    enrollment_date = Column(String(32), nullable=True, server_default="''", comment="入学日期")
    graduation_date = Column(String(32), nullable=True, server_default="''", comment="毕（结）业日期")
    school_name = Column(String(200), nullable=True, server_default="''", comment="学校名称")
    major = Column(String(100), nullable=True, server_default="''", comment="专业")
    duration = Column(String(32), nullable=True, server_default="''", comment="学制")
    level = Column(String(32), nullable=True, server_default="''", comment="层次")
    education_type = Column(String(64), nullable=True, server_default="''", comment="学历类别")
    learning_form = Column(String(64), nullable=True, server_default="''", comment="学习形式")
    graduation_status = Column(String(32), nullable=True, server_default="''", comment="毕（结）业")
    certificate_no = Column(String(64), nullable=True, server_default="''", comment="证书编号")
    president_name = Column(String(64), nullable=True, server_default="''", comment="校（院）长姓名")
    valid_until = Column(Date, nullable=False, comment="验证有效日期")
    photo_blob = Column(LargeBinary, nullable=True, comment="学生照片")
    del_flag = Column(CHAR(1), nullable=True, server_default="'0'", comment="删除标志")
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
