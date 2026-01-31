"""
学籍备案表 VO
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class StudentRecordFilingListVO(BaseModel):
    """列表项（不含 photo_blob）"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = None
    verification_code: Optional[str] = None
    update_date: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    enrollment_date: Optional[str] = None
    graduation_date: Optional[str] = None
    school_name: Optional[str] = None
    major: Optional[str] = None
    duration: Optional[str] = None
    level: Optional[str] = None
    education_type: Optional[str] = None
    learning_form: Optional[str] = None
    graduation_status: Optional[str] = None
    certificate_no: Optional[str] = None
    president_name: Optional[str] = None
    valid_until: Optional[date] = None
    create_time: Optional[datetime] = None
    remark: Optional[str] = None


class StudentRecordFilingUpdateDTO(BaseModel):
    """编辑备案表记录"""

    model_config = ConfigDict(alias_generator=to_camel)

    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    enrollment_date: Optional[str] = None
    graduation_date: Optional[str] = None
    school_name: Optional[str] = None
    major: Optional[str] = None
    duration: Optional[str] = None
    level: Optional[str] = None
    education_type: Optional[str] = None
    learning_form: Optional[str] = None
    graduation_status: Optional[str] = None
    certificate_no: Optional[str] = None
    president_name: Optional[str] = None
    valid_until: Optional[str] = None
    update_date: Optional[str] = None
    remark: Optional[str] = None
