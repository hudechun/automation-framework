"""
大纲提示词模板数据库操作层
"""
from typing import Any, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_thesis.entity.do.outline_prompt_template_do import AiWriteOutlinePromptTemplate
from utils.page_util import PageUtil


class OutlinePromptTemplateDao:
    """
    大纲提示词模板数据访问对象
    """

    @classmethod
    async def get_by_format_template_id(
        cls, db: AsyncSession, format_template_id: Union[int, None]
    ) -> Union[AiWriteOutlinePromptTemplate, None]:
        """
        按格式模板ID获取一条提示词模板（先匹配该格式模板，若无则取全局默认）

        :param db: 数据库会话
        :param format_template_id: 格式模板ID，None 表示只查全局默认
        :return: 一条模板对象或 None
        """
        base_conditions = (
            AiWriteOutlinePromptTemplate.status == '0',
            AiWriteOutlinePromptTemplate.del_flag == '0',
        )
        # 1) 若传入了格式模板ID，先查该格式模板下的记录（多条时取 is_default='1'）
        if format_template_id is not None:
            q = (
                select(AiWriteOutlinePromptTemplate)
                .where(
                    AiWriteOutlinePromptTemplate.format_template_id == format_template_id,
                    *base_conditions,
                )
                .order_by(AiWriteOutlinePromptTemplate.is_default.desc())
            )
            result = (await db.execute(q)).scalars().first()
            if result is not None:
                return result
        # 2) 查全局默认（format_template_id IS NULL）
        q_global = (
            select(AiWriteOutlinePromptTemplate)
            .where(
                AiWriteOutlinePromptTemplate.format_template_id.is_(None),
                *base_conditions,
            )
            .order_by(AiWriteOutlinePromptTemplate.is_default.desc())
        )
        return (await db.execute(q_global)).scalars().first()

    @classmethod
    async def get_by_id(
        cls, db: AsyncSession, prompt_template_id: int
    ) -> Union[AiWriteOutlinePromptTemplate, None]:
        """
        按主键获取大纲提示词模板

        :param db: 数据库会话
        :param prompt_template_id: 主键ID
        :return: 模板对象或 None
        """
        result = (
            await db.execute(
                select(AiWriteOutlinePromptTemplate).where(
                    AiWriteOutlinePromptTemplate.prompt_template_id == prompt_template_id,
                    AiWriteOutlinePromptTemplate.del_flag == '0',
                )
            )
        ).scalars().first()
        return result

    @classmethod
    async def get_list(
        cls, db: AsyncSession, query_object: dict = None, is_page: bool = False
    ) -> Union[PageModel, list]:
        """分页或全量列表，支持 name、format_template_id、status 筛选。"""
        query_object = query_object or {}
        q = (
            select(AiWriteOutlinePromptTemplate)
            .where(
                AiWriteOutlinePromptTemplate.del_flag == '0',
                AiWriteOutlinePromptTemplate.name.like(f"%{query_object.get('name') or ''}%")
                if query_object.get('name') else True,
                AiWriteOutlinePromptTemplate.format_template_id == query_object.get('format_template_id')
                if query_object.get('format_template_id') is not None else True,
                AiWriteOutlinePromptTemplate.status == query_object.get('status')
                if query_object.get('status') is not None else True,
            )
            .order_by(AiWriteOutlinePromptTemplate.sort_order.asc(), AiWriteOutlinePromptTemplate.prompt_template_id.desc())
        )
        return await PageUtil.paginate(
            db, q,
            query_object.get('page_num', 1),
            query_object.get('page_size', 10),
            is_page
        )

    @classmethod
    async def add(cls, db: AsyncSession, data: dict) -> AiWriteOutlinePromptTemplate:
        """新增一条记录。"""
        row = AiWriteOutlinePromptTemplate(**data)
        db.add(row)
        await db.flush()
        return row

    @classmethod
    async def update_by_id(cls, db: AsyncSession, prompt_template_id: int, data: dict) -> None:
        """按主键更新。"""
        await db.execute(
            update(AiWriteOutlinePromptTemplate)
            .where(AiWriteOutlinePromptTemplate.prompt_template_id == prompt_template_id)
            .values(**data)
        )

    @classmethod
    async def delete_logic(cls, db: AsyncSession, prompt_template_id: int) -> None:
        """逻辑删除（del_flag='2'）。"""
        await db.execute(
            update(AiWriteOutlinePromptTemplate)
            .where(AiWriteOutlinePromptTemplate.prompt_template_id == prompt_template_id)
            .values(del_flag='2')
        )
