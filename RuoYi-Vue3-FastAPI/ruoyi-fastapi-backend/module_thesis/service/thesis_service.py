"""
论文管理服务层
"""
from typing import Any, Union
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_thesis.dao import (
    ThesisDao,
    ThesisOutlineDao,
    ThesisChapterDao,
    ThesisVersionDao,
)
from module_thesis.entity.vo import (
    ThesisModel,
    ThesisOutlineModel,
    ThesisChapterModel,
    ThesisVersionModel,
    ThesisPageQueryModel,
    DeductQuotaModel,
)
from module_thesis.service.member_service import MemberService
from utils.common_util import CamelCaseUtil


class ThesisService:
    """
    论文管理服务类
    """

    # ==================== 论文管理 ====================

    @classmethod
    async def get_thesis_list(
        cls,
        query_db: AsyncSession,
        query_object: ThesisPageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取论文列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 论文列表
        """
        query_dict = query_object.model_dump(exclude_none=True)
        return await ThesisDao.get_thesis_list(query_db, query_dict, is_page)

    @classmethod
    async def get_thesis_detail(cls, query_db: AsyncSession, thesis_id: int) -> ThesisModel:
        """
        获取论文详情

        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :return: 论文详情
        """
        thesis = await ThesisDao.get_thesis_by_id(query_db, thesis_id)
        if not thesis:
            raise ServiceException(message='论文不存在')
        return ThesisModel(**CamelCaseUtil.transform_result(thesis))

    @classmethod
    async def create_thesis(
        cls,
        query_db: AsyncSession,
        thesis_data: ThesisModel,
        user_id: int
    ) -> CrudResponseModel:
        """
        创建论文（需要扣减配额）

        :param query_db: 数据库会话
        :param thesis_data: 论文数据
        :param user_id: 用户ID
        :return: 操作结果
        """
        try:
            # 先检查配额是否充足（不扣减）
            if not await MemberService.check_quota(query_db, user_id, 'thesis_generation', 1):
                raise ServiceException(message='论文生成配额不足')

            # 创建论文
            thesis_dict = thesis_data.model_dump(exclude_none=True)
            # 移除数据库中不存在的字段（如subject，如果数据库中没有该字段）
            # subject字段在VO中用于验证，但数据库中没有对应字段，所以需要排除
            thesis_dict.pop('subject', None)  # 如果数据库中没有subject字段，则移除
            thesis_dict['user_id'] = user_id
            thesis_dict['status'] = 'draft'
            thesis_dict['total_words'] = 0
            
            new_thesis = await ThesisDao.add_thesis(query_db, thesis_dict)
            
            # 在 flush 后立即提取 thesis_id（此时对象还在 session 中）
            await query_db.flush()
            thesis_id = new_thesis.thesis_id
            
            # 扣减配额（带正确的业务ID，不自动提交）
            deduct_data = DeductQuotaModel(
                user_id=user_id,
                feature_type='thesis_generation',
                amount=1,
                business_type='thesis_create',
                business_id=thesis_id
            )
            await MemberService.deduct_quota(query_db, deduct_data, auto_commit=False)
            
            # 统一提交事务
            await query_db.commit()
            
            return CrudResponseModel(
                is_success=True,
                message='论文创建成功',
                result={'thesis_id': thesis_id}
            )
        except ServiceException as e:
            await query_db.rollback()
            raise e
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'论文创建失败: {str(e)}')

    @classmethod
    async def update_thesis(
        cls,
        query_db: AsyncSession,
        thesis_data: ThesisModel
    ) -> CrudResponseModel:
        """
        更新论文

        :param query_db: 数据库会话
        :param thesis_data: 论文数据
        :return: 操作结果
        """
        # 检查论文是否存在
        await cls.get_thesis_detail(query_db, thesis_data.thesis_id)

        try:
            update_data = thesis_data.model_dump(exclude_unset=True)
            update_data['update_time'] = datetime.now()
            await ThesisDao.update_thesis(query_db, update_data)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='论文更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'论文更新失败: {str(e)}')

    @classmethod
    async def delete_thesis(cls, query_db: AsyncSession, thesis_id: int) -> CrudResponseModel:
        """
        删除论文

        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :return: 操作结果
        """
        # 检查论文是否存在
        await cls.get_thesis_detail(query_db, thesis_id)

        try:
            await ThesisDao.delete_thesis(query_db, thesis_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='论文删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'论文删除失败: {str(e)}')

    @classmethod
    async def get_user_thesis_count(
        cls,
        query_db: AsyncSession,
        user_id: int,
        status: str = None
    ) -> int:
        """
        统计用户论文数量

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param status: 状态（可选）
        :return: 论文数量
        """
        return await ThesisDao.count_user_thesis(query_db, user_id, status)

    # ==================== 大纲管理 ====================

    @classmethod
    async def generate_outline(
        cls,
        query_db: AsyncSession,
        outline_data: ThesisOutlineModel,
        user_id: int
    ) -> CrudResponseModel:
        """
        生成论文大纲（需要扣减配额）

        :param query_db: 数据库会话
        :param outline_data: 大纲数据
        :param user_id: 用户ID
        :return: 操作结果
        """
        # 检查论文是否存在
        thesis = await cls.get_thesis_detail(query_db, outline_data.thesis_id)

        try:
            # 先检查配额是否充足（不扣减）
            if not await MemberService.check_quota(query_db, user_id, 'outline_generation', 1):
                raise ServiceException(message='大纲生成配额不足')

            # 调用AI生成大纲
            from module_thesis.service.ai_generation_service import AiGenerationService
            
            # 从数据库对象获取论文信息
            thesis_dict = await ThesisDao.get_thesis_by_id(query_db, outline_data.thesis_id)
            
            thesis_info = {
                'title': thesis_dict.title if thesis_dict else thesis.title,
                'major': getattr(thesis_dict, 'major', '') if thesis_dict else '',
                'degree_level': getattr(thesis_dict, 'degree_level', '') if thesis_dict else '',
                'research_direction': getattr(thesis_dict, 'research_direction', '') if thesis_dict else '',
                'keywords': getattr(thesis_dict, 'keywords', '') if thesis_dict else ''
            }
            
            ai_outline = await AiGenerationService.generate_outline(query_db, thesis_info)
            
            # 将AI生成的大纲转换为JSON字符串存储
            import json
            outline_content = json.dumps(ai_outline, ensure_ascii=False)

            # 检查是否已有大纲
            existing_outline = await ThesisOutlineDao.get_outline_by_thesis_id(
                query_db, outline_data.thesis_id
            )

            if existing_outline:
                # 更新现有大纲
                update_data = {
                    'outline_id': existing_outline.outline_id,
                    'outline_data': outline_content,
                    'update_time': datetime.now()
                }
                await ThesisOutlineDao.update_outline(query_db, update_data)
                outline_id = existing_outline.outline_id
            else:
                # 创建新大纲
                outline_dict = {
                    'thesis_id': outline_data.thesis_id,
                    'outline_data': outline_content
                }
                new_outline = await ThesisOutlineDao.add_outline(query_db, outline_dict)
                await query_db.flush()
                outline_id = new_outline.outline_id

            # 扣减配额（生成大纲消耗1次大纲生成配额，不自动提交）
            deduct_data = DeductQuotaModel(
                user_id=user_id,
                feature_type='outline_generation',
                amount=1,
                business_type='outline_generate',
                business_id=outline_data.thesis_id
            )
            await MemberService.deduct_quota(query_db, deduct_data, auto_commit=False)

            # 统一提交事务
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='大纲生成成功',
                result={'outline_id': outline_id, 'outline': ai_outline}
            )
        except ServiceException as e:
            await query_db.rollback()
            raise e
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'大纲生成失败: {str(e)}')

    @classmethod
    async def get_thesis_outline(
        cls,
        query_db: AsyncSession,
        thesis_id: int
    ) -> Union[ThesisOutlineModel, None]:
        """
        获取论文大纲

        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :return: 大纲信息
        """
        outline = await ThesisOutlineDao.get_outline_by_thesis_id(query_db, thesis_id)
        if outline:
            return ThesisOutlineModel(**CamelCaseUtil.transform_result(outline))
        return None

    # ==================== 章节管理 ====================

    @classmethod
    async def generate_chapter(
        cls,
        query_db: AsyncSession,
        chapter_data: ThesisChapterModel,
        user_id: int
    ) -> CrudResponseModel:
        """
        生成论文章节（需要扣减配额）

        :param query_db: 数据库会话
        :param chapter_data: 章节数据
        :param user_id: 用户ID
        :return: 操作结果
        """
        # 检查论文是否存在
        thesis = await cls.get_thesis_detail(query_db, chapter_data.thesis_id)

        try:
            # 先检查配额是否充足（不扣减）
            if not await MemberService.check_quota(query_db, user_id, 'chapter_generation', 1):
                raise ServiceException(message='章节生成配额不足')

            # 获取大纲上下文（如果有）
            outline = await ThesisOutlineDao.get_outline_by_thesis_id(query_db, chapter_data.thesis_id)
            outline_context = outline.outline_data if outline else None

            # 调用AI生成章节内容
            from module_thesis.service.ai_generation_service import AiGenerationService
            
            # 从数据库对象获取论文信息
            thesis_dict = await ThesisDao.get_thesis_by_id(query_db, chapter_data.thesis_id)
            
            thesis_info = {
                'title': thesis_dict.title if thesis_dict else thesis.title,
                'major': getattr(thesis_dict, 'major', '') if thesis_dict else '',
                'degree_level': getattr(thesis_dict, 'degree_level', '') if thesis_dict else '',
                'keywords': getattr(thesis_dict, 'keywords', '') if thesis_dict else ''
            }
            
            chapter_info = {
                'chapter_number': chapter_data.chapter_number,
                'chapter_title': chapter_data.chapter_title,
                'sections': []  # 可以从chapter_data中提取小节信息
            }
            
            ai_content = await AiGenerationService.generate_chapter(
                query_db, thesis_info, chapter_info, outline_context
            )
            
            # 计算字数
            word_count = len(ai_content.replace(' ', '').replace('\n', ''))

            # 创建章节
            chapter_dict = {
                'thesis_id': chapter_data.thesis_id,
                'title': chapter_data.chapter_title,
                'level': 1,  # 默认一级章节
                'order_num': chapter_data.chapter_number if isinstance(chapter_data.chapter_number, int) else 1,
                'content': ai_content,
                'word_count': word_count,
                'status': 'completed'
            }
            new_chapter = await ThesisChapterDao.add_chapter(query_db, chapter_dict)
            await query_db.flush()
            chapter_id = new_chapter.chapter_id

            # 更新论文总字数
            total_words = await ThesisChapterDao.count_thesis_words(query_db, chapter_data.thesis_id)
            await ThesisDao.update_word_count(query_db, chapter_data.thesis_id, total_words)

            # 扣减配额（生成章节消耗1次章节生成配额，不自动提交）
            deduct_data = DeductQuotaModel(
                user_id=user_id,
                feature_type='chapter_generation',
                amount=1,
                business_type='chapter_generate',
                business_id=chapter_data.thesis_id
            )
            await MemberService.deduct_quota(query_db, deduct_data, auto_commit=False)

            # 统一提交事务
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='章节生成成功',
                result={'chapter_id': chapter_id, 'content': ai_content, 'word_count': word_count}
            )
        except ServiceException as e:
            await query_db.rollback()
            raise e
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'章节生成失败: {str(e)}')

    @classmethod
    async def batch_generate_chapters(
        cls,
        query_db: AsyncSession,
        thesis_id: int,
        chapters_data: list[ThesisChapterModel],
        user_id: int
    ) -> CrudResponseModel:
        """
        批量生成章节（需要扣减配额）
        
        注意：此方法会实际调用AI生成每个章节的内容

        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :param chapters_data: 章节数据列表
        :param user_id: 用户ID
        :return: 操作结果
        """
        # 检查论文是否存在
        thesis = await cls.get_thesis_detail(query_db, thesis_id)

        chapter_count = len(chapters_data)
        if chapter_count == 0:
            raise ServiceException(message='章节数据不能为空')

        try:
            # 先检查配额是否充足（不扣减）
            if not await MemberService.check_quota(query_db, user_id, 'chapter_generation', chapter_count):
                raise ServiceException(message='章节生成配额不足')

            # 获取大纲上下文（如果有）
            outline = await ThesisOutlineDao.get_outline_by_thesis_id(query_db, thesis_id)
            outline_context = outline.outline_data if outline else None

            # 从数据库对象获取论文信息
            thesis_dict = await ThesisDao.get_thesis_by_id(query_db, thesis_id)
            
            thesis_info = {
                'title': thesis_dict.title if thesis_dict else thesis.title,
                'major': getattr(thesis_dict, 'major', '') if thesis_dict else '',
                'degree_level': getattr(thesis_dict, 'degree_level', '') if thesis_dict else '',
                'keywords': getattr(thesis_dict, 'keywords', '') if thesis_dict else ''
            }

            # 调用AI生成服务
            from module_thesis.service.ai_generation_service import AiGenerationService

            # 批量生成章节内容
            generated_chapters = []
            for chapter_data in chapters_data:
                chapter_info = {
                    'chapter_number': chapter_data.chapter_number,
                    'chapter_title': chapter_data.chapter_title,
                    'sections': []  # 可以从chapter_data中提取小节信息
                }
                
                # 调用AI生成章节内容
                ai_content = await AiGenerationService.generate_chapter(
                    query_db, thesis_info, chapter_info, outline_context
                )
                
                # 计算字数
                word_count = len(ai_content.replace(' ', '').replace('\n', ''))

                # 准备章节数据
                chapter_dict = {
                    'thesis_id': thesis_id,
                    'title': chapter_data.chapter_title,
                    'level': 1,  # 默认一级章节
                    'order_num': chapter_data.chapter_number if isinstance(chapter_data.chapter_number, int) else len(generated_chapters) + 1,
                    'content': ai_content,
                    'word_count': word_count,
                    'status': 'completed'
                }
                generated_chapters.append(chapter_dict)

            # 批量创建章节
            await ThesisChapterDao.batch_add_chapters(query_db, generated_chapters)

            # 更新论文总字数
            total_words = await ThesisChapterDao.count_thesis_words(query_db, thesis_id)
            await ThesisDao.update_word_count(query_db, thesis_id, total_words)

            # 扣减配额（批量生成按章节数量扣减，不自动提交）
            deduct_data = DeductQuotaModel(
                user_id=user_id,
                feature_type='chapter_generation',
                amount=chapter_count,
                business_type='chapter_batch_generate',
                business_id=thesis_id
            )
            await MemberService.deduct_quota(query_db, deduct_data, auto_commit=False)

            # 统一提交事务
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message=f'成功生成{chapter_count}个章节',
                result={'generated_count': chapter_count, 'total_words': total_words}
            )
        except ServiceException as e:
            await query_db.rollback()
            raise e
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'批量生成章节失败: {str(e)}')

    @classmethod
    async def get_thesis_chapters(
        cls,
        query_db: AsyncSession,
        thesis_id: int
    ) -> list[ThesisChapterModel]:
        """
        获取论文的所有章节

        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :return: 章节列表
        """
        chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, thesis_id)
        return [ThesisChapterModel(**CamelCaseUtil.transform_result(chapter)) for chapter in chapters]

    @classmethod
    async def update_chapter(
        cls,
        query_db: AsyncSession,
        chapter_data: ThesisChapterModel
    ) -> CrudResponseModel:
        """
        更新章节

        :param query_db: 数据库会话
        :param chapter_data: 章节数据
        :return: 操作结果
        """
        # 检查章节是否存在
        chapter = await ThesisChapterDao.get_chapter_by_id(query_db, chapter_data.chapter_id)
        if not chapter:
            raise ServiceException(message='章节不存在')

        try:
            update_data = chapter_data.model_dump(exclude_unset=True)
            update_data['update_time'] = datetime.now()
            await ThesisChapterDao.update_chapter(query_db, update_data)

            # 更新论文总字数
            total_words = await ThesisChapterDao.count_thesis_words(query_db, chapter.thesis_id)
            await ThesisDao.update_word_count(query_db, chapter.thesis_id, total_words)

            await query_db.commit()
            return CrudResponseModel(is_success=True, message='章节更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'章节更新失败: {str(e)}')

    @classmethod
    async def delete_chapter(cls, query_db: AsyncSession, chapter_id: int) -> CrudResponseModel:
        """
        删除章节

        :param query_db: 数据库会话
        :param chapter_id: 章节ID
        :return: 操作结果
        """
        # 检查章节是否存在
        chapter = await ThesisChapterDao.get_chapter_by_id(query_db, chapter_id)
        if not chapter:
            raise ServiceException(message='章节不存在')

        try:
            await ThesisChapterDao.delete_chapter(query_db, chapter_id)

            # 更新论文总字数
            total_words = await ThesisChapterDao.count_thesis_words(query_db, chapter.thesis_id)
            await ThesisDao.update_word_count(query_db, chapter.thesis_id, total_words)

            await query_db.commit()
            return CrudResponseModel(is_success=True, message='章节删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'章节删除失败: {str(e)}')

    # ==================== 版本管理 ====================

    @classmethod
    async def create_version(
        cls,
        query_db: AsyncSession,
        version_data: ThesisVersionModel
    ) -> CrudResponseModel:
        """
        创建论文版本

        :param query_db: 数据库会话
        :param version_data: 版本数据
        :return: 操作结果
        """
        # 检查论文是否存在
        await cls.get_thesis_detail(query_db, version_data.thesis_id)

        try:
            version_dict = version_data.model_dump(exclude_none=True)
            new_version = await ThesisVersionDao.add_version(query_db, version_dict)

            # 清理旧版本（保留最新10个）
            await ThesisVersionDao.delete_old_versions(query_db, version_data.thesis_id, keep_count=10)

            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='版本创建成功',
                result={'version_id': new_version.version_id}
            )
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'版本创建失败: {str(e)}')

    @classmethod
    async def get_thesis_versions(
        cls,
        query_db: AsyncSession,
        thesis_id: int,
        limit: int = 10
    ) -> list[ThesisVersionModel]:
        """
        获取论文版本历史

        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :param limit: 返回数量限制
        :return: 版本列表
        """
        versions = await ThesisVersionDao.get_version_list_by_thesis(query_db, thesis_id, limit)
        return [ThesisVersionModel(**CamelCaseUtil.transform_result(version)) for version in versions]

    @classmethod
    async def get_version_detail(
        cls,
        query_db: AsyncSession,
        version_id: int
    ) -> ThesisVersionModel:
        """
        获取版本详情

        :param query_db: 数据库会话
        :param version_id: 版本ID
        :return: 版本详情
        """
        version = await ThesisVersionDao.get_version_by_id(query_db, version_id)
        if not version:
            raise ServiceException(message='版本不存在')
        return ThesisVersionModel(**CamelCaseUtil.transform_result(version))
