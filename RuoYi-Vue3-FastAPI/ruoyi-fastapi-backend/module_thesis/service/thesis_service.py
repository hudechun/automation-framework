"""
论文管理服务层
"""
from typing import Any, Union, Optional, Dict
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
from utils.log_util import logger


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
            # 确保状态值去除首尾空格
            if 'status' in update_data and isinstance(update_data['status'], str):
                update_data['status'] = update_data['status'].strip()
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
                'research_direction': getattr(thesis_dict, 'research_direction', '') if thesis_dict else '',
                'keywords': getattr(thesis_dict, 'keywords', '') if thesis_dict else '',
                'total_words': getattr(thesis_dict, 'total_words', 0) if thesis_dict else 0,
                'template_id': getattr(thesis_dict, 'template_id', None) if thesis_dict else None
            }
            
            ai_outline = await AiGenerationService.generate_outline(query_db, thesis_info)
            
            # 直接保存字典对象，SQLAlchemy 的 JSON 字段会自动处理
            # 不需要使用 json.dumps()，否则会导致双重编码

            # 检查是否已有大纲
            existing_outline = await ThesisOutlineDao.get_outline_by_thesis_id(
                query_db, outline_data.thesis_id
            )

            if existing_outline:
                # 更新现有大纲
                update_data = {
                    'outline_id': existing_outline.outline_id,
                    'outline_data': ai_outline,  # 直接保存字典，不是 JSON 字符串
                    'update_time': datetime.now()
                }
                await ThesisOutlineDao.update_outline(query_db, update_data)
                outline_id = existing_outline.outline_id
            else:
                # 创建新大纲
                outline_dict = {
                    'thesis_id': outline_data.thesis_id,
                    'outline_data': ai_outline  # 直接保存字典，不是 JSON 字符串
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

            # 更新论文状态为generating（大纲已生成，开始生成章节）
            await ThesisDao.update_thesis(query_db, {
                'thesis_id': outline_data.thesis_id,
                'status': 'generating'
            })

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
            # 转换数据库对象为字典
            outline_dict = CamelCaseUtil.transform_result(outline)
            # outline_data 字段是 JSON 类型，SQLAlchemy 会自动解析为字典
            # 确保 outline_data 和 outline_structure 字段正确映射
            if 'outlineData' in outline_dict and outline_dict['outlineData']:
                # 如果 outline_data 是字符串（旧数据），需要解析
                if isinstance(outline_dict['outlineData'], str):
                    import json
                    try:
                        outline_dict['outlineData'] = json.loads(outline_dict['outlineData'])
                    except json.JSONDecodeError:
                        pass
                # 同时设置 outline_structure（别名）
                outline_dict['outlineStructure'] = outline_dict.get('outlineData')
            return ThesisOutlineModel(**outline_dict)
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
            # 注意：如果是批量生成场景，应该在批量生成接口中统一检查配额
            # 这里只检查单个章节生成的配额
            if not await MemberService.check_quota(query_db, user_id, 'chapter_generation', 1):
                raise ServiceException(message='章节生成配额不足')

            # 获取大纲上下文（如果有）
            outline = await ThesisOutlineDao.get_outline_by_thesis_id(query_db, chapter_data.thesis_id)
            outline_data_dict = None
            outline_context = None
            
            # outline_data 是 JSON 类型，SQLAlchemy 会自动解析为字典
            # 使用统一的大纲解析工具
            from module_thesis.utils.outline_parser import parse_outline_data
            if outline and outline.outline_data:
                outline_data_dict, outline_context = parse_outline_data(outline.outline_data)

            # 调用AI生成章节内容
            from module_thesis.service.ai_generation_service import AiGenerationService
            
            # 从数据库对象获取论文信息
            thesis_dict = await ThesisDao.get_thesis_by_id(query_db, chapter_data.thesis_id)
            
            thesis_info = {
                'title': thesis_dict.title if thesis_dict else thesis.title,
                'major': getattr(thesis_dict, 'major', '') if thesis_dict else '',
                'keywords': getattr(thesis_dict, 'keywords', '') if thesis_dict else '',
                'total_words': getattr(thesis_dict, 'total_words', 0) if thesis_dict else 0,
                'template_id': getattr(thesis_dict, 'template_id', None) if thesis_dict else None
            }
            
            # 从大纲中提取对应章节的小节信息
            sections = []
            if outline_data_dict and 'chapters' in outline_data_dict:
                # 查找对应章节号或章节标题的章节
                target_chapter = None
                for chapter in outline_data_dict['chapters']:
                    chapter_num = chapter.get('chapter_number')
                    chapter_title = chapter.get('chapter_title', '')
                    # 匹配章节号或章节标题
                    if (chapter_num and str(chapter_num) == str(chapter_data.chapter_number)) or \
                       (chapter_title and chapter_title == chapter_data.chapter_title):
                        target_chapter = chapter
                        break
                
                # 如果找到对应章节，提取小节信息
                if target_chapter and 'sections' in target_chapter:
                    sections = target_chapter['sections']
            
            chapter_info = {
                'chapter_number': chapter_data.chapter_number,
                'chapter_title': chapter_data.chapter_title,
                'sections': sections  # 从大纲中提取的小节信息
            }
            
            logger.info(f"开始生成章节 - 论文ID: {chapter_data.thesis_id}, 章节: {chapter_data.chapter_title}, 大纲上下文: {'已提供' if outline_context else '未提供'}")
            ai_content = await AiGenerationService.generate_chapter(
                query_db, thesis_info, chapter_info, outline_context
            )
            logger.info(f"章节生成完成 - 内容长度: {len(ai_content) if ai_content else 0}")
            
            # 计算字数（改进的字数计算）
            word_count = cls._calculate_word_count(ai_content)

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

            # 检查是否所有章节都已完成，如果是则更新论文状态为formatted（表示章节内容已生成，等待格式化）
            all_chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, chapter_data.thesis_id)
            completed_chapters = [c for c in all_chapters if c.status == 'completed']
            if len(all_chapters) > 0 and len(completed_chapters) == len(all_chapters):
                # 所有章节都已完成，更新论文状态为formatted（下一步是格式化）
                await ThesisDao.update_thesis(query_db, {
                    'thesis_id': chapter_data.thesis_id,
                    'status': 'formatted'
                })

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
            outline_data_dict = None
            outline_context = None
            
            # outline_data 是 JSON 类型，SQLAlchemy 会自动解析为字典
            # 使用统一的大纲解析工具
            from module_thesis.utils.outline_parser import parse_outline_data
            if outline and outline.outline_data:
                outline_data_dict, outline_context = parse_outline_data(outline.outline_data)

            # 从数据库对象获取论文信息
            thesis_dict = await ThesisDao.get_thesis_by_id(query_db, thesis_id)
            
            thesis_info = {
                'title': thesis_dict.title if thesis_dict else thesis.title,
                'major': getattr(thesis_dict, 'major', '') if thesis_dict else '',
                'keywords': getattr(thesis_dict, 'keywords', '') if thesis_dict else '',
                'total_words': getattr(thesis_dict, 'total_words', 0) if thesis_dict else 0,
                'template_id': getattr(thesis_dict, 'template_id', None) if thesis_dict else None
            }

            # 调用AI生成服务
            from module_thesis.service.ai_generation_service import AiGenerationService

            # 批量生成章节内容（部分成功策略 + 断点续传）
            generated_chapters = []
            failed_chapters = []
            skipped_chapters = []  # 已完成的章节（跳过）
            
            for chapter_data in chapters_data:
                # 检查章节是否已存在且已完成
                existing_chapter = await ThesisChapterDao.get_chapter_by_title_and_thesis(
                    query_db, thesis_id, chapter_data.chapter_title
                )
                
                if existing_chapter and existing_chapter.status == 'completed':
                    # 章节已存在且已完成，跳过
                    skipped_chapters.append({
                        'chapter_number': chapter_data.chapter_number,
                        'chapter_title': chapter_data.chapter_title,
                        'chapter_id': existing_chapter.chapter_id
                    })
                    logger.info(f"章节已存在且已完成，跳过 - 论文ID: {thesis_id}, 章节: {chapter_data.chapter_title}")
                    continue
                
                # 如果章节存在但未完成，先删除旧记录（重新生成）
                if existing_chapter and existing_chapter.status != 'completed':
                    logger.info(f"章节存在但未完成，删除旧记录重新生成 - 论文ID: {thesis_id}, 章节: {chapter_data.chapter_title}")
                    await ThesisChapterDao.delete_chapter(query_db, existing_chapter.chapter_id)
                
                # 先创建章节记录（状态为generating），用于保存进度
                chapter_dict_pre = {
                    'thesis_id': thesis_id,
                    'title': chapter_data.chapter_title,
                    'level': 1,  # 默认一级章节
                    'order_num': chapter_data.chapter_number if isinstance(chapter_data.chapter_number, int) else len(generated_chapters) + len(skipped_chapters) + 1,
                    'content': '',  # 暂时为空
                    'word_count': 0,
                    'status': 'generating'  # 生成中状态
                }
                new_chapter = await ThesisChapterDao.add_chapter(query_db, chapter_dict_pre)
                await query_db.flush()
                chapter_id = new_chapter.chapter_id
                
                try:
                    # 从大纲中提取对应章节的小节信息
                    from module_thesis.utils.outline_parser import extract_chapters_from_outline
                    sections = []
                    chapters_list = extract_chapters_from_outline(outline_data_dict)
                    if chapters_list:
                        # 查找对应章节号或章节标题的章节
                        target_chapter = None
                        for chapter in chapters_list:
                            chapter_num = chapter.get('chapter_number')
                            chapter_title = chapter.get('chapter_title', '')
                            # 匹配章节号或章节标题
                            if (chapter_num and str(chapter_num) == str(chapter_data.chapter_number)) or \
                               (chapter_title and chapter_title == chapter_data.chapter_title):
                                target_chapter = chapter
                                break
                        
                        # 如果找到对应章节，提取小节信息
                        if target_chapter and 'sections' in target_chapter:
                            sections = target_chapter['sections']
                    
                    chapter_info = {
                        'chapter_number': chapter_data.chapter_number,
                        'chapter_title': chapter_data.chapter_title,
                        'sections': sections  # 从大纲中提取的小节信息
                    }
                    
                    # 调用AI生成章节内容
                    ai_content = await AiGenerationService.generate_chapter(
                        query_db, thesis_info, chapter_info, outline_context
                    )
                    
                    # 计算字数（改进的字数计算）
                    word_count = cls._calculate_word_count(ai_content)

                    # 更新章节记录（从generating更新为completed）
                    update_data = {
                        'chapter_id': chapter_id,
                        'content': ai_content,
                        'word_count': word_count,
                        'status': 'completed'
                    }
                    await ThesisChapterDao.update_chapter(query_db, update_data)
                    
                    generated_chapters.append({
                        'chapter_id': chapter_id,
                        'chapter_number': chapter_data.chapter_number,
                        'chapter_title': chapter_data.chapter_title
                    })
                    logger.info(f"章节生成成功 - 论文ID: {thesis_id}, 章节: {chapter_data.chapter_title}, 章节ID: {chapter_id}")
                    
                except Exception as e:
                    # 单个章节生成失败，更新状态为pending（可以后续继续生成）
                    error_msg = str(e)
                    logger.error(
                        f"章节生成失败 - 论文ID: {thesis_id}, "
                        f"章节: {chapter_data.chapter_title}, "
                        f"错误: {error_msg}",
                        exc_info=True
                    )
                    
                    # 更新章节状态为pending（未完成，可以继续生成）
                    update_data = {
                        'chapter_id': chapter_id,
                        'status': 'pending'  # 标记为待生成，可以继续生成
                    }
                    await ThesisChapterDao.update_chapter(query_db, update_data)
                    
                    failed_chapters.append({
                        'chapter_id': chapter_id,
                        'chapter_number': chapter_data.chapter_number,
                        'chapter_title': chapter_data.chapter_title,
                        'error': error_msg
                    })
                    # 继续生成其他章节，不中断

            # 如果没有成功生成任何新章节（包括跳过的），且没有跳过的章节，抛出异常
            if not generated_chapters and not skipped_chapters:
                raise ServiceException(
                    message=f'所有章节生成失败。失败原因: {failed_chapters[0]["error"] if failed_chapters else "未知错误"}'
                )

            # 更新论文总字数
            total_words = await ThesisChapterDao.count_thesis_words(query_db, thesis_id)
            await ThesisDao.update_word_count(query_db, thesis_id, total_words)

            # 检查是否所有章节都已完成，如果是则更新论文状态为formatted（表示章节内容已生成，等待格式化）
            all_chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, thesis_id)
            completed_chapters = [c for c in all_chapters if c.status == 'completed']
            if len(all_chapters) > 0 and len(completed_chapters) == len(all_chapters):
                # 所有章节都已完成，更新论文状态为formatted（下一步是格式化）
                await ThesisDao.update_thesis(query_db, {
                    'thesis_id': thesis_id,
                    'status': 'formatted'
                })

            # 扣减配额（只扣减成功生成的新章节数量，跳过的章节不扣减）
            if generated_chapters:
                deduct_data = DeductQuotaModel(
                    user_id=user_id,
                    feature_type='chapter_generation',
                    amount=len(generated_chapters),  # 只扣减成功生成的新章节
                    business_type='chapter_batch_generate',
                    business_id=thesis_id
                )
                await MemberService.deduct_quota(query_db, deduct_data, auto_commit=False)

            # 统一提交事务
            await query_db.commit()
            
            # 构建返回消息
            success_count = len(generated_chapters)
            skipped_count = len(skipped_chapters)
            failed_count = len(failed_chapters)
            
            message_parts = []
            if success_count > 0:
                message_parts.append(f'成功生成{success_count}个新章节')
            if skipped_count > 0:
                message_parts.append(f'跳过{skipped_count}个已完成章节')
            if failed_count > 0:
                message_parts.append(f'失败{failed_count}个章节')
            
            message = '，'.join(message_parts) if message_parts else '没有需要生成的章节'
            
            return CrudResponseModel(
                is_success=True,
                message=message,
                result={
                    'generated_count': success_count,
                    'skipped_count': skipped_count,
                    'failed_count': failed_count,
                    'total_words': total_words,
                    'failed_chapters': failed_chapters if failed_chapters else None,
                    'skipped_chapters': skipped_chapters if skipped_chapters else None
                }
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
    async def get_chapter_generation_progress(
        cls,
        query_db: AsyncSession,
        thesis_id: int
    ) -> dict[str, Any]:
        """
        获取章节生成进度

        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :return: 生成进度信息
        """
        # 获取所有章节
        all_chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, thesis_id)
        
        total_count = len(all_chapters)
        completed_count = len([c for c in all_chapters if c.status == 'completed'])
        generating_count = len([c for c in all_chapters if c.status == 'generating'])
        pending_count = len([c for c in all_chapters if c.status == 'pending'])
        
        # 获取未完成的章节列表
        incomplete_chapters = [
            {
                'chapter_id': c.chapter_id,
                'chapter_title': c.title,
                'order_num': c.order_num,
                'status': c.status
            }
            for c in all_chapters if c.status != 'completed'
        ]
        
        return {
            'total_count': total_count,
            'completed_count': completed_count,
            'generating_count': generating_count,
            'pending_count': pending_count,
            'progress_percentage': round((completed_count / total_count * 100) if total_count > 0 else 0, 2),
            'incomplete_chapters': incomplete_chapters
        }

    @classmethod
    async def continue_generate_chapters(
        cls,
        query_db: AsyncSession,
        thesis_id: int,
        user_id: int
    ) -> CrudResponseModel:
        """
        继续生成未完成的章节（断点续传）

        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :param user_id: 用户ID
        :return: 操作结果
        """
        # 检查论文是否存在
        thesis = await cls.get_thesis_detail(query_db, thesis_id)
        
        # 获取未完成的章节
        incomplete_chapters = await ThesisChapterDao.get_incomplete_chapters_by_thesis(query_db, thesis_id)
        
        if not incomplete_chapters:
            return CrudResponseModel(
                is_success=True,
                message='没有需要继续生成的章节',
                result={'generated_count': 0, 'skipped_count': 0, 'failed_count': 0}
            )
        
        try:
            # 检查配额是否充足（不扣减）
            if not await MemberService.check_quota(query_db, user_id, 'chapter_generation', len(incomplete_chapters)):
                raise ServiceException(message='章节生成配额不足')
            
            # 获取大纲上下文（如果有）
            outline = await ThesisOutlineDao.get_outline_by_thesis_id(query_db, thesis_id)
            outline_data_dict = None
            outline_context = None
            
            if outline and outline.outline_data:
                import json
                if isinstance(outline.outline_data, dict):
                    outline_data_dict = outline.outline_data
                    outline_context = json.dumps(outline.outline_data, ensure_ascii=False, indent=2)
                elif isinstance(outline.outline_data, str):
                    try:
                        outline_data_dict = json.loads(outline.outline_data)
                        outline_context = outline.outline_data
                    except json.JSONDecodeError:
                        outline_context = outline.outline_data
                else:
                    outline_context = str(outline.outline_data)
            
            # 从数据库对象获取论文信息
            thesis_dict = await ThesisDao.get_thesis_by_id(query_db, thesis_id)
            
            thesis_info = {
                'title': thesis_dict.title if thesis_dict else thesis.title,
                'major': getattr(thesis_dict, 'major', '') if thesis_dict else '',
                'keywords': getattr(thesis_dict, 'keywords', '') if thesis_dict else '',
                'total_words': getattr(thesis_dict, 'total_words', 0) if thesis_dict else 0,
                'template_id': getattr(thesis_dict, 'template_id', None) if thesis_dict else None
            }
            
            # 调用AI生成服务
            from module_thesis.service.ai_generation_service import AiGenerationService
            
            generated_count = 0
            failed_chapters = []
            
            for chapter in incomplete_chapters:
                try:
                    # 从大纲中提取对应章节的小节信息
                    sections = []
                    if outline_data_dict and 'chapters' in outline_data_dict:
                        for outline_chapter in outline_data_dict['chapters']:
                            chapter_num = outline_chapter.get('chapter_number')
                            chapter_title = outline_chapter.get('chapter_title', '')
                            if (chapter_num and str(chapter_num) == str(chapter.order_num)) or \
                               (chapter_title and chapter_title == chapter.title):
                                if 'sections' in outline_chapter:
                                    sections = outline_chapter['sections']
                                break
                    
                    chapter_info = {
                        'chapter_number': chapter.order_num,
                        'chapter_title': chapter.title,
                        'sections': sections
                    }
                    
                    # 更新状态为generating
                    await ThesisChapterDao.update_chapter(query_db, {
                        'chapter_id': chapter.chapter_id,
                        'status': 'generating'
                    })
                    
                    # 调用AI生成章节内容
                    ai_content = await AiGenerationService.generate_chapter(
                        query_db, thesis_info, chapter_info, outline_context
                    )
                    
                    # 计算字数
                    word_count = cls._calculate_word_count(ai_content)
                    
                    # 更新章节记录为completed
                    update_data = {
                        'chapter_id': chapter.chapter_id,
                        'content': ai_content,
                        'word_count': word_count,
                        'status': 'completed'
                    }
                    await ThesisChapterDao.update_chapter(query_db, update_data)
                    
                    generated_count += 1
                    logger.info(f"继续生成章节成功 - 论文ID: {thesis_id}, 章节: {chapter.title}, 章节ID: {chapter.chapter_id}")
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(
                        f"继续生成章节失败 - 论文ID: {thesis_id}, "
                        f"章节: {chapter.title}, "
                        f"错误: {error_msg}",
                        exc_info=True
                    )
                    
                    # 更新状态为pending
                    await ThesisChapterDao.update_chapter(query_db, {
                        'chapter_id': chapter.chapter_id,
                        'status': 'pending'
                    })
                    
                    failed_chapters.append({
                        'chapter_id': chapter.chapter_id,
                        'chapter_title': chapter.title,
                        'error': error_msg
                    })
            
            # 更新论文总字数
            total_words = await ThesisChapterDao.count_thesis_words(query_db, thesis_id)
            await ThesisDao.update_word_count(query_db, thesis_id, total_words)
            
            # 检查是否所有章节都已完成，如果是则更新论文状态为formatted（表示章节内容已生成，等待格式化）
            all_chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, thesis_id)
            completed_chapters = [c for c in all_chapters if c.status == 'completed']
            if len(all_chapters) > 0 and len(completed_chapters) == len(all_chapters):
                # 所有章节都已完成，更新论文状态为formatted（下一步是格式化）
                await ThesisDao.update_thesis(query_db, {
                    'thesis_id': thesis_id,
                    'status': 'formatted'
                })
            
            # 扣减配额（只扣减成功生成的章节数量）
            if generated_count > 0:
                deduct_data = DeductQuotaModel(
                    user_id=user_id,
                    feature_type='chapter_generation',
                    amount=generated_count,
                    business_type='chapter_continue_generate',
                    business_id=thesis_id
                )
                await MemberService.deduct_quota(query_db, deduct_data, auto_commit=False)
            
            # 统一提交事务
            await query_db.commit()
            
            failed_count = len(failed_chapters)
            message = f'继续生成完成，成功{generated_count}个章节'
            if failed_count > 0:
                message += f'，失败{failed_count}个章节'
            
            return CrudResponseModel(
                is_success=True,
                message=message,
                result={
                    'generated_count': generated_count,
                    'failed_count': failed_count,
                    'total_words': total_words,
                    'failed_chapters': failed_chapters if failed_chapters else None
                }
            )
            
        except ServiceException as e:
            await query_db.rollback()
            raise e
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'继续生成章节失败: {str(e)}')

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

            # 如果章节状态更新为completed，检查是否所有章节都已完成
            if update_data.get('status') == 'completed':
                # 重新查询所有章节（包括刚更新的章节）
                all_chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, chapter.thesis_id)
                completed_chapters = [c for c in all_chapters if c.status == 'completed']
                if len(all_chapters) > 0 and len(completed_chapters) == len(all_chapters):
                    # 所有章节都已完成，更新论文状态为formatted（下一步是格式化）
                    await ThesisDao.update_thesis(query_db, {
                        'thesis_id': chapter.thesis_id,
                        'status': 'formatted'
                    })

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

    @classmethod
    def _calculate_word_count(cls, content: str) -> int:
        """
        计算论文字数（中文字符数 + 英文单词数）
        
        :param content: 内容文本
        :return: 字数
        """
        import re
        if not content:
            return 0
        
        # 统计中文字符数（包括中文标点）
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        
        # 统计英文单词数
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', content))
        
        return chinese_chars + english_words

    @classmethod
    async def get_thesis_progress(
        cls,
        query_db: AsyncSession,
        thesis_id: int
    ) -> dict[str, Any]:
        """
        获取论文生成进度
        
        进度规则：
        - 完成大纲：20%
        - 论文生成（所有章节完成）：40%
        - 格式化：40%
        
        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :return: 进度信息
        """
        # 检查大纲
        outline = await ThesisOutlineDao.get_outline_by_thesis_id(query_db, thesis_id)
        has_outline = outline is not None and outline.outline_data is not None
        
        # 检查章节
        chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, thesis_id)
        completed_chapters = [c for c in chapters if c.status == 'completed']
        total_chapters = len(chapters)
        chapters_completed = total_chapters > 0 and len(completed_chapters) == total_chapters
        
        # 获取论文信息以检查状态
        thesis = await cls.get_thesis_detail(query_db, thesis_id)
        
        # 检查格式化状态
        # 状态流转：generating -> formatted -> completed
        is_formatted = thesis.status == 'formatted' or thesis.status == 'completed'
        
        # 计算进度
        progress = 0
        if has_outline:
            progress += 20  # 大纲完成：20%
        if chapters_completed:
            progress += 40  # 章节生成完成：40%
        if is_formatted:
            progress += 40  # 格式化完成：40%
        
        return {
            'total_progress': progress,
            'outline_completed': has_outline,
            'outline_progress': 20 if has_outline else 0,
            'chapters_completed': chapters_completed,
            'chapters_progress': 40 if chapters_completed else 0,
            'chapters_info': {
                'total': total_chapters,
                'completed': len(completed_chapters),
                'progress_percentage': round((len(completed_chapters) / total_chapters * 100) if total_chapters > 0 else 0, 2)
            },
            'formatted': is_formatted,
            'format_progress': 40 if is_formatted else 0,
            'format_progress_detail': 100 if is_formatted else 0
        }

    @classmethod
    async def format_thesis(
        cls,
        query_db: AsyncSession,
        thesis_id: int,
        user_id: int = None
    ) -> CrudResponseModel:
        """
        格式化论文（从模板表获取Word文档路径）
        
        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :param user_id: 用户ID
        :return: 操作结果
        """
        # 检查论文是否存在
        thesis = await cls.get_thesis_detail(query_db, thesis_id)
        
        # 检查论文状态：只有formatted状态才能进行格式化
        if thesis.status != 'formatted':
            if thesis.status == 'completed':
                raise ServiceException(message='论文已完成格式化，无需重复格式化')
            elif thesis.status == 'generating':
                raise ServiceException(message='论文章节尚未全部生成完成，请先完成所有章节的生成')
            else:
                raise ServiceException(message=f'论文状态不正确（当前状态：{thesis.status}），无法进行格式化。请先完成章节生成。')
        
        # 检查章节是否都已完成（双重检查，确保数据一致性）
        chapters = await ThesisChapterDao.get_chapter_list_by_thesis(query_db, thesis_id)
        if not chapters:
            raise ServiceException(message='论文没有章节，无法进行格式化')
        
        incomplete_chapters = [c for c in chapters if c.status != 'completed']
        if incomplete_chapters:
            incomplete_titles = [c.title for c in incomplete_chapters[:3]]  # 只显示前3个
            incomplete_msg = '、'.join(incomplete_titles)
            if len(incomplete_chapters) > 3:
                incomplete_msg += f'等{len(incomplete_chapters)}个章节'
            raise ServiceException(message=f'请先完成所有章节的生成，再进行格式化。未完成章节：{incomplete_msg}')
        
        # 检查是否有模板
        if not thesis.template_id:
            raise ServiceException(message='论文未关联格式模板，请先选择模板')
        
        try:
            # 从模板表获取Word文档路径
            from module_thesis.dao.template_dao import FormatTemplateDao
            template = await FormatTemplateDao.get_template_by_id(query_db, thesis.template_id)
            
            if not template:
                raise ServiceException(message='模板不存在')
            
            if not template.file_path:
                raise ServiceException(message='模板文件路径为空，无法进行格式化')
            
            # 将相对路径转换为实际文件系统路径
            import os
            from config.env import UploadConfig
            file_path = template.file_path
            
            # 处理URL格式：http://127.0.0.1:9099/dev-api/profile/upload/... -> /profile/upload/...
            if file_path.startswith('http://') or file_path.startswith('https://'):
                # 提取URL中的路径部分
                from urllib.parse import urlparse
                parsed_url = urlparse(file_path)
                file_path = parsed_url.path
                # 移除 /dev-api 前缀（如果存在）
                if file_path.startswith('/dev-api'):
                    file_path = file_path.replace('/dev-api', '', 1)
            
            # 如果 file_path 是 /profile/upload/... 格式，需要转换为实际路径
            if file_path.startswith(UploadConfig.UPLOAD_PREFIX):
                # 将 /profile 替换为实际的上传目录
                word_file_path = file_path.replace(UploadConfig.UPLOAD_PREFIX, UploadConfig.UPLOAD_PATH)
                # 处理路径分隔符（Windows/Linux兼容）
                word_file_path = os.path.normpath(word_file_path)
            else:
                # 如果已经是绝对路径或相对路径，直接使用
                word_file_path = file_path
            
            # 检查文件是否存在
            if not os.path.exists(word_file_path):
                raise ServiceException(message=f'模板文件不存在: {word_file_path}（原始路径: {file_path}）')
            
            from module_thesis.service.format_service import FormatService
            
            # 更新状态：开始格式化
            await ThesisDao.update_thesis(query_db, {
                'thesis_id': thesis_id,
                'status': 'generating'
            })
            await query_db.flush()
            
            # 优先使用模板的 format_data，如果没有则读取Word文档并提取格式指令
            format_instructions = None
            if template.format_data:
                # 如果模板已有格式数据，直接使用
                import json
                format_instructions = json.dumps(template.format_data, ensure_ascii=False)
                logger.info(f"使用模板已解析的格式数据 - 论文ID: {thesis_id}, 模板ID: {thesis.template_id}")
            else:
                # 如果模板没有格式数据，读取Word文档并提取格式指令
                logger.info(f"开始读取Word文档并提取格式指令 - 论文ID: {thesis_id}, 模板ID: {thesis.template_id}, 文件: {word_file_path}")
                read_result = await FormatService.read_word_document_with_ai(query_db, word_file_path)
                format_instructions = read_result['format_instructions']
                
                # 同时更新模板的 format_data，以便下次使用
                try:
                    import json
                    format_data = json.loads(format_instructions) if isinstance(format_instructions, str) else format_instructions
                    from module_thesis.dao.template_dao import FormatTemplateDao
                    await FormatTemplateDao.update_template(query_db, {
                        'template_id': thesis.template_id,
                        'format_data': format_data
                    })
                    logger.info(f"已更新模板的格式数据 - 模板ID: {thesis.template_id}")
                except Exception as e:
                    logger.warning(f"更新模板格式数据失败: {str(e)}")
                    # 不影响格式化流程
            
            # 执行格式化
            logger.info(f"开始格式化论文 - 论文ID: {thesis_id}")
            format_result = await FormatService.format_thesis(
                query_db,
                thesis_id,
                format_instructions=format_instructions
            )
            
            # 格式化完成后，更新状态为 completed（此时才算真正完成，前端会显示导出按钮）
            await ThesisDao.update_thesis(query_db, {
                'thesis_id': thesis_id,
                'status': 'completed'
            })
            
            await query_db.commit()
            
            logger.info(f"论文格式化完成 - 论文ID: {thesis_id}, 输出文件: {format_result['formatted_file_path']}")
            
            return CrudResponseModel(
                is_success=True,
                message='论文格式化成功',
                result={
                    'formatted_file_path': format_result['formatted_file_path'],
                    'format_instructions': format_instructions
                }
            )
            
        except ServiceException:
            await query_db.rollback()
            raise
        except Exception as e:
            await query_db.rollback()
            logger.error(f"格式化论文失败: {str(e)}", exc_info=True)
            raise ServiceException(message=f'格式化论文失败: {str(e)}')
    
    @classmethod
    async def download_thesis(
        cls,
        query_db: AsyncSession,
        thesis_id: int,
        user_id: int = None
    ) -> dict:
        """
        下载格式化后的论文
        
        :param query_db: 数据库会话
        :param thesis_id: 论文ID
        :param user_id: 用户ID
        :return: 文件生成器
        """
        # 检查论文是否存在
        thesis = await cls.get_thesis_detail(query_db, thesis_id)
        
        # 检查论文状态是否为已格式化
        # 前端期望 completed 状态显示导出按钮，所以不需要检查 formatted 状态
        # 只要所有章节完成（status == 'completed'）就可以下载
        if thesis.status != 'completed':
            raise ServiceException(message='论文尚未格式化，无法下载。请先完成格式化。')
        
        # 构建格式化文件路径
        import os
        from pathlib import Path
        
        formatted_file_path = Path('uploads/thesis/formatted') / f'thesis_{thesis_id}_formatted.docx'
        formatted_file_path = formatted_file_path.resolve()  # 转换为绝对路径
        
        # 检查文件是否存在
        if not os.path.exists(formatted_file_path):
            raise ServiceException(message=f'格式化文件不存在: {formatted_file_path}。请重新格式化论文。')
        
        # 生成安全的文件名（移除特殊字符）
        safe_title = thesis.title.replace('/', '_').replace('\\', '_').replace(':', '_') if thesis.title else ''
        file_name = f'{safe_title}_格式化.docx' if safe_title else f'thesis_{thesis_id}_formatted.docx'
        
        # 返回文件路径和文件名
        return {
            'file_path': str(formatted_file_path),
            'file_name': file_name
        }
