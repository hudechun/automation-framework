"""
学籍备案表 DAO
"""
from typing import Any, Union

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_student.entity.do.student_record_filing_do import StudentRecordFiling
from utils.page_util import PageUtil


class StudentRecordFilingDao:
    @classmethod
    async def get_by_id(cls, db: AsyncSession, pk: int) -> Union[StudentRecordFiling, None]:
        r = (
            await db.execute(
                select(StudentRecordFiling).where(
                    StudentRecordFiling.id == pk,
                    StudentRecordFiling.del_flag == "0",
                )
            )
        ).scalars().first()
        return r

    @classmethod
    async def get_by_verification_code(
        cls, db: AsyncSession, code: str
    ) -> Union[StudentRecordFiling, None]:
        r = (
            await db.execute(
                select(StudentRecordFiling).where(
                    StudentRecordFiling.verification_code == code,
                    StudentRecordFiling.del_flag == "0",
                )
            )
        ).scalars().first()
        return r

    @classmethod
    async def exists_verification_code(cls, db: AsyncSession, code: str, exclude_id: int | None = None) -> bool:
        q = select(func.count(StudentRecordFiling.id)).where(
            StudentRecordFiling.verification_code == code,
            StudentRecordFiling.del_flag == "0",
        )
        if exclude_id is not None:
            q = q.where(StudentRecordFiling.id != exclude_id)
        total = (await db.execute(q)).scalar() or 0
        return total > 0

    @classmethod
    async def get_list(
        cls,
        db: AsyncSession,
        query_object: dict | None = None,
        is_page: bool = True,
    ) -> Union[PageModel, list]:
        query_object = query_object or {}
        query = (
            select(StudentRecordFiling)
            .where(StudentRecordFiling.del_flag == "0")
            .order_by(StudentRecordFiling.id.desc())
        )
        name = query_object.get("name")
        if name:
            query = query.where(StudentRecordFiling.name.like(f"%{name}%"))
        verification_code = query_object.get("verification_code")
        if verification_code:
            query = query.where(
                StudentRecordFiling.verification_code.like(f"%{verification_code}%")
            )
        page_num = query_object.get("page_num", 1)
        page_size = query_object.get("page_size", 10)
        return await PageUtil.paginate(db, query, page_num, page_size, is_page)

    @classmethod
    async def add(cls, db: AsyncSession, data: dict) -> StudentRecordFiling:
        obj = StudentRecordFiling(**data)
        db.add(obj)
        await db.flush()
        return obj

    @classmethod
    async def update_by_id(cls, db: AsyncSession, pk: int, data: dict) -> None:
        data.pop("id", None)
        data.pop("verification_code", None)
        from sqlalchemy import update
        await db.execute(
            update(StudentRecordFiling).where(StudentRecordFiling.id == pk).values(**data)
        )

    @classmethod
    async def delete_by_id(cls, db: AsyncSession, pk: int, logical: bool = True) -> None:
        if logical:
            await cls.update_by_id(db, pk, {"del_flag": "2"})
        else:
            from sqlalchemy import delete
            await db.execute(delete(StudentRecordFiling).where(StudentRecordFiling.id == pk))
