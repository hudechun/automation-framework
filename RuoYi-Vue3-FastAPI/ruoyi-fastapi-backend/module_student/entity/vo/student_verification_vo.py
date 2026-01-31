"""
学籍验证学生 VO
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class StudentVerificationListVO(BaseModel):
    """列表项（不含 photo_blob）"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = None
    verification_code: Optional[str] = None
    update_date: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    nation: Optional[str] = None
    school_name: Optional[str] = None
    level: Optional[str] = None
    major: Optional[str] = None
    duration: Optional[str] = None
    education_type: Optional[str] = None
    learning_form: Optional[str] = None
    branch: Optional[str] = None
    department: Optional[str] = None
    enrollment_date: Optional[str] = None
    graduation_date: Optional[str] = None
    valid_until: Optional[date] = None
    create_time: Optional[datetime] = None
    remark: Optional[str] = None


class StudentVerificationDetailVO(StudentVerificationListVO):
    """详情（可含二维码图片 base64 或 URL，不含 photo_blob 大字段）"""

    qr_image_url: Optional[str] = Field(default=None, description="二维码图片 URL 或 base64")


class StudentVerificationUpdateDTO(BaseModel):
    """编辑学生记录（可更新字段，验证码不可改）"""

    model_config = ConfigDict(alias_generator=to_camel)

    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    nation: Optional[str] = None
    school_name: Optional[str] = None
    level: Optional[str] = None
    major: Optional[str] = None
    duration: Optional[str] = None
    education_type: Optional[str] = None
    learning_form: Optional[str] = None
    branch: Optional[str] = None
    department: Optional[str] = None
    enrollment_date: Optional[str] = None
    graduation_date: Optional[str] = None
    valid_until: Optional[str] = None  # YYYY-MM-DD 或 XXXX年XX月XX日
    update_date: Optional[str] = None
    remark: Optional[str] = None


class VerifyCheckVO(BaseModel):
    """对外 H5 验证检查返回"""

    model_config = ConfigDict(alias_generator=to_camel)

    expired: bool = Field(description="是否已过期")
    name: Optional[str] = None
    report_image_url: Optional[str] = None
    message: Optional[str] = None
