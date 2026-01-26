"""
论文管理模块数据库操作层
"""
from typing import Any, Union

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_thesis.entity.do.thesis_do import (
    AiWriteThesis,
    AiWriteThesisChapter,
    AiWriteThesisOutline,
    AiWriteThesisVersion,
)
from utils.page_util import PageUtil


class ThesisDao:
    """
    论文数据访问对象
    """

    @classmethod
    async def get_thesis_by_id(cls, db: AsyncSession, thesis_id: int) -> Union[AiWriteThesis, None]:
        """
        根据论文ID获取论文详情

        :param db: orm对象
        :param thesis_id: 论文ID
        :return: 论文信息对象
        """
        thesis_info = (
            await db.execute(
                select(AiWriteThesis).where(AiWriteThesis.thesis_id == thesis_id, AiWriteThesis.del_flag == '0')
            )
        ).scalars().first()

        return thesis_info

    @classmethod
    async def get_thesis_list(
        cls, db: AsyncSession, query_object: dict = None, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取论文列表

        :param db: orm对象
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 论文列表
        """
        query_object = query_object or {}
        query = (
            select(AiWriteThesis)
            .where(
                AiWriteThesis.user_id == query_object.get('user_id') if query_object.get('user_id') else True,
                AiWriteThesis.title.like(f"%{query_object.get('title')}%") if query_object.get('title') else True,
                AiWriteThesis.thesis_type == query_object.get('thesis_type')
                if query_object.get('thesis_type')
                else True,
                AiWriteThesis.status == query_object.get('status') if query_object.get('status') else True,
                AiWriteThesis.del_flag == '0',
            )
            .order_by(AiWriteThesis.update_time.desc())
        )

        thesis_list: Union[PageModel, list[dict[str, Any]]] = await PageUtil.paginate(
            db, query, query_object.get('page_num', 1), query_object.get('page_size', 10), is_page
        )

        return thesis_list

    @classmethod
    async def add_thesis(cls, db: AsyncSession, thesis_data: dict) -> AiWriteThesis:
        """
        新增论文

        :param db: orm对象
        :param thesis_data: 论文数据
        :return: 论文对象
        """
        db_thesis = AiWriteThesis(**thesis_data)
        db.add(db_thesis)
        await db.flush()

        return db_thesis

    @classmethod
    async def update_thesis(cls, db: AsyncSession, thesis_data: dict) -> None:
        """
        更新论文

        :param db: orm对象
        :param thesis_data: 论文数据
        :return:
        """
        await db.execute(update(AiWriteThesis), [thesis_data])

    @classmethod
    async def delete_thesis(cls, db: AsyncSession, thesis_id: int) -> None:
        """
        删除论文（软删除）

        :param db: orm对象
        :param thesis_id: 论文ID
        :return:
        """
        await db.execute(
            update(AiWriteThesis).where(AiWriteThesis.thesis_id == thesis_id).values(del_flag='2')
        )

    @classmethod
    async def update_word_count(cls, db: AsyncSession, thesis_id: int, word_count: int) -> None:
        """
        更新论文字数

        :param db: orm对象
        :param thesis_id: 论文ID
        :param word_count: 字数
        :return:
        """
        await db.execute(
            update(AiWriteThesis).where(AiWriteThesis.thesis_id == thesis_id).values(total_words=word_count)
        )

    @classmethod
    async def count_user_thesis(cls, db: AsyncSession, user_id: int, status: str = None) -> int:
        """
        统计用户论文数量

        :param db: orm对象
        :param user_id: 用户ID
        :param status: 状态（可选）
        :return: 论文数量
        """
        count = (
            await db.execute(
                select(func.count(AiWriteThesis.thesis_id)).where(
                    AiWriteThesis.user_id == user_id,
                    AiWriteThesis.status == status if status else True,
                    AiWriteThesis.del_flag == '0',
                )
            )
        ).scalar()

        return count or 0


class ThesisOutlineDao:
    """
    论文大纲数据访问对象
    """

    @classmethod
    async def get_outline_by_thesis_id(cls, db: AsyncSession, thesis_id: int) -> Union[AiWriteThesisOutline, None]:
        """
        根据论文ID获取大纲

        :param db: orm对象
        :param thesis_id: 论文ID
        :return: 大纲信息对象
        """
        outline_info = (
            await db.execute(select(AiWriteThesisOutline).where(AiWriteThesisOutline.thesis_id == thesis_id))
        ).scalars().first()

        return outline_info

    @classmethod
    async def add_outline(cls, db: AsyncSession, outline_data: dict) -> AiWriteThesisOutline:
        """
        新增大纲

        :param db: orm对象
        :param outline_data: 大纲数据
        :return: 大纲对象
        """
        db_outline = AiWriteThesisOutline(**outline_data)
        db.add(db_outline)
        await db.flush()

        return db_outline

    @classmethod
    async def update_outline(cls, db: AsyncSession, outline_data: dict) -> None:
        """
        更新大纲

        :param db: orm对象
        :param outline_data: 大纲数据
        :return:
        """
        await db.execute(update(AiWriteThesisOutline), [outline_data])

    @classmethod
    async def delete_outline(cls, db: AsyncSession, outline_id: int) -> None:
        """
        删除大纲

        :param db: orm对象
        :param outline_id: 大纲ID
        :return:
        """
        await db.execute(delete(AiWriteThesisOutline).where(AiWriteThesisOutline.outline_id == outline_id))


class ThesisChapterDao:
    """
    论文章节数据访问对象
    """

    @classmethod
    async def get_chapter_by_id(cls, db: AsyncSession, chapter_id: int) -> Union[AiWriteThesisChapter, None]:
        """
        根据章节ID获取章节详情

        :param db: orm对象
        :param chapter_id: 章节ID
        :return: 章节信息对象
        """
        chapter_info = (
            await db.execute(select(AiWriteThesisChapter).where(AiWriteThesisChapter.chapter_id == chapter_id))
        ).scalars().first()

        return chapter_info

    @classmethod
    async def get_chapter_list_by_thesis(cls, db: AsyncSession, thesis_id: int) -> list[AiWriteThesisChapter]:
        """
        获取论文的所有章节

        :param db: orm对象
        :param thesis_id: 论文ID
        :return: 章节列表
        """
        chapter_list = (
            await db.execute(
                select(AiWriteThesisChapter)
                .where(AiWriteThesisChapter.thesis_id == thesis_id)
                .order_by(AiWriteThesisChapter.order_num)
            )
        ).scalars().all()

        return list(chapter_list)

    @classmethod
    async def get_chapter_list_by_outline(cls, db: AsyncSession, outline_id: int) -> list[AiWriteThesisChapter]:
        """
        获取大纲的所有章节

        :param db: orm对象
        :param outline_id: 大纲ID
        :return: 章节列表
        """
        chapter_list = (
            await db.execute(
                select(AiWriteThesisChapter)
                .where(AiWriteThesisChapter.outline_id == outline_id)
                .order_by(AiWriteThesisChapter.order_num)
            )
        ).scalars().all()

        return list(chapter_list)

    @classmethod
    async def add_chapter(cls, db: AsyncSession, chapter_data: dict) -> AiWriteThesisChapter:
        """
        新增章节

        :param db: orm对象
        :param chapter_data: 章节数据
        :return: 章节对象
        """
        db_chapter = AiWriteThesisChapter(**chapter_data)
        db.add(db_chapter)
        await db.flush()

        return db_chapter

    @classmethod
    async def update_chapter(cls, db: AsyncSession, chapter_data: dict) -> None:
        """
        更新章节

        :param db: orm对象
        :param chapter_data: 章节数据
        :return:
        """
        await db.execute(update(AiWriteThesisChapter), [chapter_data])

    @classmethod
    async def delete_chapter(cls, db: AsyncSession, chapter_id: int) -> None:
        """
        删除章节

        :param db: orm对象
        :param chapter_id: 章节ID
        :return:
        """
        await db.execute(delete(AiWriteThesisChapter).where(AiWriteThesisChapter.chapter_id == chapter_id))

    @classmethod
    async def batch_add_chapters(cls, db: AsyncSession, chapters_data: list[dict]) -> list[AiWriteThesisChapter]:
        """
        批量新增章节

        :param db: orm对象
        :param chapters_data: 章节数据列表
        :return: 章节对象列表
        """
        db_chapters = [AiWriteThesisChapter(**chapter_data) for chapter_data in chapters_data]
        db.add_all(db_chapters)
        await db.flush()

        return db_chapters

    @classmethod
    async def count_thesis_words(cls, db: AsyncSession, thesis_id: int) -> int:
        """
        统计论文总字数

        :param db: orm对象
        :param thesis_id: 论文ID
        :return: 总字数
        """
        total_words = (
            await db.execute(
                select(func.sum(AiWriteThesisChapter.word_count)).where(
                    AiWriteThesisChapter.thesis_id == thesis_id
                )
            )
        ).scalar()

        return total_words or 0


class ThesisVersionDao:
    """
    论文版本数据访问对象
    """

    @classmethod
    async def get_version_by_id(cls, db: AsyncSession, version_id: int) -> Union[AiWriteThesisVersion, None]:
        """
        根据版本ID获取版本详情

        :param db: orm对象
        :param version_id: 版本ID
        :return: 版本信息对象
        """
        version_info = (
            await db.execute(select(AiWriteThesisVersion).where(AiWriteThesisVersion.version_id == version_id))
        ).scalars().first()

        return version_info

    @classmethod
    async def get_version_list_by_thesis(
        cls, db: AsyncSession, thesis_id: int, limit: int = 10
    ) -> list[AiWriteThesisVersion]:
        """
        获取论文的版本历史

        :param db: orm对象
        :param thesis_id: 论文ID
        :param limit: 返回数量限制
        :return: 版本列表
        """
        version_list = (
            await db.execute(
                select(AiWriteThesisVersion)
                .where(AiWriteThesisVersion.thesis_id == thesis_id)
                .order_by(AiWriteThesisVersion.create_time.desc())
                .limit(limit)
            )
        ).scalars().all()

        return list(version_list)

    @classmethod
    async def add_version(cls, db: AsyncSession, version_data: dict) -> AiWriteThesisVersion:
        """
        新增版本

        :param db: orm对象
        :param version_data: 版本数据
        :return: 版本对象
        """
        db_version = AiWriteThesisVersion(**version_data)
        db.add(db_version)
        await db.flush()

        return db_version

    @classmethod
    async def delete_old_versions(cls, db: AsyncSession, thesis_id: int, keep_count: int = 10) -> None:
        """
        删除旧版本（保留最新的N个版本）

        :param db: orm对象
        :param thesis_id: 论文ID
        :param keep_count: 保留数量
        :return:
        """
        # 查询需要删除的版本ID
        subquery = (
            select(AiWriteThesisVersion.version_id)
            .where(AiWriteThesisVersion.thesis_id == thesis_id)
            .order_by(AiWriteThesisVersion.create_time.desc())
            .offset(keep_count)
        )

        await db.execute(
            delete(AiWriteThesisVersion).where(AiWriteThesisVersion.version_id.in_(subquery))
        )
