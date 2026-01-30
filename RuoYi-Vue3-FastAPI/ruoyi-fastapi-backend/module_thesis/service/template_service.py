"""
格式模板管理服务层
"""
from typing import Any, Union
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_thesis.dao import FormatTemplateDao, TemplateFormatRuleDao
from module_thesis.entity.vo import (
    FormatTemplateModel,
    TemplateFormatRuleModel,
    TemplatePageQueryModel,
)
from utils.common_util import CamelCaseUtil
from utils.log_util import logger


class TemplateService:
    """
    格式模板管理服务类
    """

    # ==================== 模板管理 ====================

    @classmethod
    async def get_template_list(
        cls,
        query_db: AsyncSession,
        query_object: TemplatePageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取模板列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 模板列表
        """
        query_dict = query_object.model_dump(exclude_none=True)
        return await FormatTemplateDao.get_template_list(query_db, query_dict, is_page)

    @classmethod
    async def get_template_detail(cls, query_db: AsyncSession, template_id: int) -> FormatTemplateModel:
        """
        获取模板详情

        :param query_db: 数据库会话
        :param template_id: 模板ID
        :return: 模板详情
        """
        template = await FormatTemplateDao.get_template_by_id(query_db, template_id)
        if not template:
            raise ServiceException(message='模板不存在')
        return FormatTemplateModel(**CamelCaseUtil.transform_result(template))

    @classmethod
    async def create_template(
        cls,
        query_db: AsyncSession,
        template_data: FormatTemplateModel,
        user_id: int = None,
        background_tasks = None
    ) -> CrudResponseModel:
        """
        创建格式模板

        :param query_db: 数据库会话
        :param template_data: 模板数据
        :param user_id: 用户ID（可选，管理员上传时为None）
        :return: 操作结果
        """
        # 注释掉重复检查，允许同一学校不同专业有多个模板
        # exists = await FormatTemplateDao.check_template_exists(
        #     query_db,
        #     template_data.school_name,
        #     template_data.degree_level,
        #     template_data.major
        # )
        # if exists:
        #     raise ServiceException(message='该学校、学历层次和专业的模板已存在')

        try:
            # 使用 by_alias=False 确保字段名是蛇形命名（file_path, file_name），而不是驼峰命名（filePath, fileName）
            # 注意：Pydantic 的 alias_generator=to_camel 意味着：
            # - 前端传递 filePath → Pydantic 自动映射到 file_path 字段
            # - model_dump(by_alias=False) 输出 file_path（蛇形命名）
            template_dict = template_data.model_dump(exclude_none=True, by_alias=False)
            
            print(f"[模板创建] Pydantic model_dump 后的数据:")
            print(f"  template_dict keys: {list(template_dict.keys())}")
            print(f"  file_path (from model): {template_dict.get('file_path')}")
            print(f"  file_name (from model): {template_dict.get('file_name')}")
            import sys
            sys.stdout.flush()
            
            # 设置是否为官方模板
            if user_id:
                template_dict['is_official'] = '0'  # 用户上传
                template_dict['create_by'] = str(user_id)
            else:
                template_dict['is_official'] = '1'  # 管理员上传
            
            template_dict['usage_count'] = 0
            template_dict['status'] = '0'  # 启用
            
            # 确保 file_path 和 file_name 字段存在
            # 如果前端传递了 filePath/fileName（驼峰），Pydantic 应该已经映射到 file_path/file_name
            # 但为了保险，我们显式检查并转换
            if 'filePath' in template_dict and 'file_path' not in template_dict:
                template_dict['file_path'] = template_dict.pop('filePath')
                print(f"[模板创建] 已转换 filePath -> file_path: {template_dict.get('file_path')}")
                sys.stdout.flush()
            if 'fileName' in template_dict and 'file_name' not in template_dict:
                template_dict['file_name'] = template_dict.pop('fileName')
                print(f"[模板创建] 已转换 fileName -> file_name: {template_dict.get('file_name')}")
                sys.stdout.flush()
            
            # 如果仍然没有 file_path 或 file_name，检查原始数据
            if not template_dict.get('file_path') or not template_dict.get('file_name'):
                # 尝试从原始 model 数据获取（可能使用了别名）
                raw_dict = template_data.model_dump(exclude_none=True, by_alias=True)
                print(f"[模板创建] 检查原始数据（by_alias=True）:")
                print(f"  raw_dict keys: {list(raw_dict.keys())}")
                print(f"  filePath: {raw_dict.get('filePath')}")
                print(f"  fileName: {raw_dict.get('fileName')}")
                sys.stdout.flush()
                
                if not template_dict.get('file_path') and raw_dict.get('filePath'):
                    template_dict['file_path'] = raw_dict.get('filePath')
                    print(f"[模板创建] 从原始数据获取 file_path: {template_dict.get('file_path')}")
                    sys.stdout.flush()
                if not template_dict.get('file_name') and raw_dict.get('fileName'):
                    template_dict['file_name'] = raw_dict.get('fileName')
                    print(f"[模板创建] 从原始数据获取 file_name: {template_dict.get('file_name')}")
                    sys.stdout.flush()
            
            # 如果提供了 file_path，验证文件是否存在并尝试解析格式数据
            file_path = template_dict.get('file_path')
            
            # 如果 file_path 为空，尝试从原始数据再次获取
            if not file_path:
                raw_dict = template_data.model_dump(exclude_none=True, by_alias=True)
                file_path = raw_dict.get('filePath') or raw_dict.get('file_path')
                if file_path:
                    template_dict['file_path'] = file_path
                    print(f"[模板创建] 从原始数据重新获取 file_path: {file_path}")
                    logger.info(f"[模板创建] 从原始数据重新获取 file_path: {file_path}")
                    import sys
                    sys.stdout.flush()
            
            # 保存原始文件路径（用于数据库存储）
            original_file_path = file_path
            
            print(f"[模板创建] 开始处理模板创建")
            print(f"  原始 file_path: {file_path}")
            print(f"  file_path 类型: {type(file_path)}")
            print(f"  file_path 是否为空: {not file_path}")
            print(f"  file_name: {template_dict.get('file_name')}")
            print(f"  file_size: {template_dict.get('file_size')}")
            print(f"  template_dict keys: {list(template_dict.keys())}")
            import sys
            sys.stdout.flush()
            
            if file_path:
                import os
                from config.env import UploadConfig
                from urllib.parse import urlparse
                
                # 处理URL格式：http://127.0.0.1:9099/dev-api/profile/upload/... -> /profile/upload/...
                if file_path.startswith('http://') or file_path.startswith('https://'):
                    # 提取URL中的路径部分
                    parsed_url = urlparse(file_path)
                    file_path = parsed_url.path
                    # 移除 /dev-api 前缀（如果存在）
                    if file_path.startswith('/dev-api'):
                        file_path = file_path.replace('/dev-api', '', 1)
                    # 更新 template_dict 中的 file_path（保存清理后的URL路径）
                    template_dict['file_path'] = file_path
                    original_file_path = file_path
                
                # 如果 file_name 为空，尝试从 file_path 提取文件名
                if not template_dict.get('file_name'):
                    # 从路径中提取文件名
                    file_name = os.path.basename(file_path)
                    # 移除可能的查询参数或URL片段
                    if '?' in file_name:
                        file_name = file_name.split('?')[0]
                    template_dict['file_name'] = file_name
                    print(f"[模板创建] 从路径提取文件名: {file_name}")
                    sys.stdout.flush()
                
                # 转换为实际文件系统路径（用于文件操作）
                print(f"[模板创建] 处理文件路径")
                print(f"  原始路径（URL）: {file_path}")
                print(f"  UPLOAD_PREFIX: {UploadConfig.UPLOAD_PREFIX}")
                print(f"  UPLOAD_PATH: {UploadConfig.UPLOAD_PATH}")
                sys.stdout.flush()
                
                if file_path.startswith(UploadConfig.UPLOAD_PREFIX):
                    # 将 /profile 替换为实际的上传目录（用于文件操作）
                    actual_file_path = file_path.replace(UploadConfig.UPLOAD_PREFIX, UploadConfig.UPLOAD_PATH)
                    # 处理路径分隔符（Windows/Linux兼容）
                    actual_file_path = os.path.normpath(actual_file_path)
                    print(f"  实际文件系统路径: {actual_file_path}")
                else:
                    # 如果已经是绝对路径或相对路径，直接使用
                    actual_file_path = file_path
                    print(f"  使用原始路径: {actual_file_path}")
                
                sys.stdout.flush()
                
                # 如果 file_size 为空，尝试从文件获取
                if not template_dict.get('file_size') and os.path.exists(actual_file_path):
                    template_dict['file_size'] = os.path.getsize(actual_file_path)
                    print(f"[模板创建] 从文件获取大小: {template_dict['file_size']} 字节")
                    sys.stdout.flush()
                
                # 检查文件是否存在
                print(f"[模板创建] 检查文件是否存在: {actual_file_path}")
                print(f"  文件存在: {os.path.exists(actual_file_path)}")
                sys.stdout.flush()
                
                if not os.path.exists(actual_file_path):
                    logger.error(f"模板文件不存在 - 实际路径: {actual_file_path}, 原始路径: {file_path}")
                    # 尝试检查是否是路径问题
                    if not os.path.isabs(actual_file_path):
                        # 尝试相对于工作目录
                        abs_path = os.path.abspath(actual_file_path)
                        if os.path.exists(abs_path):
                            actual_file_path = abs_path
                            logger.info(f"找到文件（使用绝对路径）: {actual_file_path}")
                        else:
                            raise ServiceException(
                                message=f'模板文件不存在。请确保文件已上传。\n'
                                       f'原始路径: {file_path}\n'
                                       f'实际路径: {actual_file_path}\n'
                                       f'绝对路径: {abs_path}'
                            )
                    else:
                        raise ServiceException(
                            message=f'模板文件不存在。请确保文件已上传。\n'
                                   f'原始路径: {file_path}\n'
                                   f'实际路径: {actual_file_path}'
                        )
                
                # 文件存在，如果提供了 format_data，直接使用；否则在后台异步解析
                # 注意：格式解析可能需要较长时间（AI分析），改为后台任务，不阻塞响应
                print(f"[模板创建] 检查是否需要解析格式数据...")
                print(f"  format_data是否存在: {bool(template_dict.get('format_data'))}")
                print(f"  background_tasks是否为None: {background_tasks is None}")
                import sys
                sys.stdout.flush()
                
                if not template_dict.get('format_data'):
                    # 如果有后台任务支持，将格式解析放到后台执行
                    if background_tasks is not None:
                        # 先创建模板，然后在后台解析格式
                        # 保存文件路径，供后台任务使用
                        template_dict['_pending_format_parse'] = actual_file_path
                        print(f"[模板创建] 设置待解析文件路径: {actual_file_path}")
                        sys.stdout.flush()
                        logger.info(f"模板文件已上传，格式解析将在后台异步执行 - 文件: {actual_file_path}")
                    else:
                        print(f"[模板创建] 警告: background_tasks为None，将尝试同步解析")
                        sys.stdout.flush()
                        # 如果没有后台任务支持，尝试同步解析（兼容旧代码）
                        try:
                            from module_thesis.service.format_service import FormatService
                            
                            logger.info(f"开始解析模板格式数据 - 文件: {actual_file_path}")
                            
                            # 读取Word文档并提取格式指令
                            read_result = await FormatService.read_word_document_with_ai(query_db, actual_file_path)
                            format_instructions = read_result['format_instructions']
                            
                            # 尝试解析为JSON格式
                            try:
                                import json
                                format_data = json.loads(format_instructions) if isinstance(format_instructions, str) else format_instructions
                                template_dict['format_data'] = format_data
                            except (json.JSONDecodeError, TypeError):
                                # 如果解析失败，尝试提取JSON部分
                                format_data = FormatService._extract_json_from_text(format_instructions)
                                template_dict['format_data'] = format_data
                            
                            logger.info(f"模板上传时自动解析格式数据成功 - 模板: {template_dict.get('template_name')}, 文件: {actual_file_path}")
                        except Exception as e:
                            # 解析失败不影响模板创建，只记录警告
                            error_msg = str(e)
                            if 'timeout' in error_msg.lower() or '超时' in error_msg:
                                logger.warning(f"模板格式解析超时，将先创建模板，后续可以手动解析格式: {error_msg}")
                            else:
                                logger.warning(f"模板上传时解析格式数据失败，将使用空格式数据: {error_msg}", exc_info=True)
            
            # 移除临时字段
            pending_format_parse = template_dict.pop('_pending_format_parse', None)
            
            # 确保 file_path 和 file_name 字段存在（用于数据库保存）
            print(f"[模板创建] 准备创建模板记录...")
            print(f"  file_path: {template_dict.get('file_path')}")
            print(f"  file_name: {template_dict.get('file_name')}")
            print(f"  file_size: {template_dict.get('file_size')}")
            print(f"  pending_format_parse: {pending_format_parse}")
            print(f"  background_tasks是否为None: {background_tasks is None}")
            print(f"  template_dict准备保存的字段: {list(template_dict.keys())}")
            print(f"  template_dict完整内容: {template_dict}")
            import sys
            sys.stdout.flush()
            
            # 验证必需字段 - 确保 file_path 和 file_name 都有值
            # 如果 file_path 为空，尝试最后一次从原始数据获取
            if not template_dict.get('file_path'):
                print(f"[模板创建] ⚠ 警告: file_path 为空，尝试最后一次获取")
                logger.warning(f"[模板创建] file_path 为空，尝试最后一次获取")
                
                # 尝试从原始 model 数据获取
                raw_dict = template_data.model_dump(exclude_none=True, by_alias=True)
                if raw_dict.get('filePath'):
                    template_dict['file_path'] = raw_dict.get('filePath')
                    print(f"[模板创建] ✓ 从原始数据最后一次获取 file_path: {template_dict.get('file_path')}")
                    logger.info(f"[模板创建] 从原始数据最后一次获取 file_path: {template_dict.get('file_path')}")
                else:
                    print(f"[模板创建] ✗ 错误: 无法从任何来源获取 file_path")
                    print(f"  原始数据 keys: {list(raw_dict.keys())}")
                    print(f"  filePath 在原始数据中: {'filePath' in raw_dict}")
                    logger.error(f"[模板创建] 无法从任何来源获取 file_path")
                    logger.error(f"  原始数据 keys: {list(raw_dict.keys())}")
                    logger.error(f"  filePath 在原始数据中: {'filePath' in raw_dict}")
                    raise ServiceException(message='模板文件路径不能为空，请先上传模板文件')
            else:
                print(f"[模板创建] ✓ file_path 存在: {template_dict.get('file_path')}")
            
            if not template_dict.get('file_name'):
                print(f"[模板创建] ⚠ 警告: file_name 为空，尝试从 file_path 提取")
                logger.warning(f"[模板创建] file_name 为空，尝试从 file_path 提取")
                if template_dict.get('file_path'):
                    import os
                    # 如果 file_name 仍然为空，从 file_path 提取
                    file_name = os.path.basename(template_dict.get('file_path'))
                    # 移除可能的查询参数或URL片段
                    if '?' in file_name:
                        file_name = file_name.split('?')[0]
                    template_dict['file_name'] = file_name
                    print(f"[模板创建] ✓ 已从file_path提取文件名: {file_name}")
                    logger.info(f"[模板创建] 已从file_path提取文件名: {file_name}")
                else:
                    print(f"[模板创建] ✗ 错误: file_path 也为空，无法提取文件名")
                    logger.error(f"[模板创建] file_path 也为空，无法提取文件名")
                    raise ServiceException(message='模板文件名不能为空，请先上传模板文件')
            else:
                print(f"[模板创建] ✓ file_name 存在: {template_dict.get('file_name')}")
            
            # 最终确认要保存的字段
            print("=" * 100)
            print(f"[模板创建] 最终保存到数据库的字段:")
            print(f"  file_path: {template_dict.get('file_path')}")
            print(f"  file_name: {template_dict.get('file_name')}")
            print(f"  file_size: {template_dict.get('file_size')}")
            print("=" * 100)
            sys.stdout.flush()
            logger.info("=" * 100)
            logger.info(f"[模板创建] 最终保存到数据库的字段:")
            logger.info(f"  file_path: {template_dict.get('file_path')}")
            logger.info(f"  file_name: {template_dict.get('file_name')}")
            logger.info(f"  file_size: {template_dict.get('file_size')}")
            logger.info("=" * 100)
            
            try:
                new_template = await FormatTemplateDao.add_template(query_db, template_dict)
                # 在flush后立即获取ID，避免commit后访问
                template_id = new_template.template_id
                
                print(f"[模板创建] 模板记录已创建，模板ID: {template_id}")
                print(f"[模板创建] 验证保存的数据:")
                print(f"  template_id: {new_template.template_id}")
                print(f"  file_path: {new_template.file_path}")
                print(f"  file_name: {new_template.file_name}")
                print(f"  file_size: {new_template.file_size}")
                sys.stdout.flush()
                logger.info(f"[模板创建] 模板记录已创建，模板ID: {template_id}")
                logger.info(f"[模板创建] 验证保存的数据:")
                logger.info(f"  template_id: {new_template.template_id}")
                logger.info(f"  file_path: {new_template.file_path}")
                logger.info(f"  file_name: {new_template.file_name}")
                logger.info(f"  file_size: {new_template.file_size}")
                
                await query_db.commit()
                
                print(f"[模板创建] ✓ 数据库提交成功，模板ID: {template_id}")
                print(f"[模板创建] ✓ 模板已保存到数据库")
                print(f"[模板创建] 最终验证（提交后）:")
                # 重新查询验证
                saved_template = await FormatTemplateDao.get_template_by_id(query_db, template_id)
                if saved_template:
                    print(f"  file_path: {saved_template.file_path}")
                    print(f"  file_name: {saved_template.file_name}")
                    print(f"  file_size: {saved_template.file_size}")
                else:
                    print(f"  ⚠ 警告: 提交后无法查询到模板记录")
                sys.stdout.flush()
                logger.info(f"[模板创建] ✓ 数据库提交成功，模板ID: {template_id}")
                logger.info(f"[模板创建] ✓ 模板已保存到数据库")
                if saved_template:
                    logger.info(f"[模板创建] 最终验证（提交后）:")
                    logger.info(f"  file_path: {saved_template.file_path}")
                    logger.info(f"  file_name: {saved_template.file_name}")
                    logger.info(f"  file_size: {saved_template.file_size}")
            except Exception as e:
                print(f"[模板创建] ✗ 数据库操作失败: {str(e)}")
                import traceback
                print(traceback.format_exc())
                sys.stdout.flush()
                await query_db.rollback()
                raise
            
            # 如果有待解析的格式，添加到后台任务（异步执行，立即返回）
            if pending_format_parse and background_tasks is not None:
                # 创建后台任务来解析格式
                print("=" * 100)
                print(f"[模板创建] 添加后台任务 - 格式解析将在后台异步执行")
                print(f"  模板ID: {template_id}")
                print(f"  文件路径: {pending_format_parse}")
                print("=" * 100)
                import sys
                sys.stdout.flush()
                logger.info(f"添加后台任务 - 格式解析将在后台异步执行 - 模板ID: {template_id}, 文件: {pending_format_parse}")
                
                # 使用BackgroundTasks添加后台任务
                background_tasks.add_task(
                    cls._parse_template_format_in_background,
                    template_id,
                    pending_format_parse
                )
                print(f"[模板创建] ✓ 后台任务已添加，将立即返回响应")
                sys.stdout.flush()
            elif pending_format_parse:
                # 如果没有background_tasks，记录警告但不阻塞
                logger.warning(f"无法添加后台任务（background_tasks为None），格式解析将跳过 - 模板ID: {template_id}")
                print("=" * 100)
                print(f"[模板创建] 警告: background_tasks为None，格式解析将跳过")
                print(f"  模板ID: {template_id}")
                print(f"  提示: 可以稍后手动触发格式解析")
                print("=" * 100)
                import sys
                sys.stdout.flush()
            
            # 返回成功响应（立即返回，不等待格式解析完成）
            return CrudResponseModel(
                is_success=True,
                message='模板创建成功，格式解析将在后台异步进行' if pending_format_parse else '模板创建成功',
                result={'template_id': template_id}
            )
        except ServiceException as e:
            print(f"[模板创建] ServiceException: {str(e)}")
            import sys
            sys.stdout.flush()
            await query_db.rollback()
            raise e
        except Exception as e:
            print(f"[模板创建] Exception: {str(e)}")
            import traceback
            print(traceback.format_exc())
            import sys
            sys.stdout.flush()
            await query_db.rollback()
            raise ServiceException(message=f'模板创建失败: {str(e)}')

    @classmethod
    async def update_template(
        cls,
        query_db: AsyncSession,
        template_data: FormatTemplateModel
    ) -> CrudResponseModel:
        """
        更新模板

        :param query_db: 数据库会话
        :param template_data: 模板数据
        :return: 操作结果
        """
        # 检查模板是否存在
        await cls.get_template_detail(query_db, template_data.template_id)

        try:
            update_data = template_data.model_dump(exclude_unset=True)
            update_data['update_time'] = datetime.now()
            await FormatTemplateDao.update_template(query_db, update_data)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='模板更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'模板更新失败: {str(e)}')

    @classmethod
    async def delete_template(cls, query_db: AsyncSession, template_id: int) -> CrudResponseModel:
        """
        删除模板

        :param query_db: 数据库会话
        :param template_id: 模板ID
        :return: 操作结果
        """
        # 检查模板是否存在
        await cls.get_template_detail(query_db, template_id)

        try:
            await FormatTemplateDao.delete_template(query_db, template_id)
            # 同时删除关联的格式规则
            await TemplateFormatRuleDao.delete_rules_by_template(query_db, template_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='模板删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'模板删除失败: {str(e)}')

    @classmethod
    async def get_popular_templates(
        cls,
        query_db: AsyncSession,
        limit: int = 10
    ) -> list[FormatTemplateModel]:
        """
        获取热门模板

        :param query_db: 数据库会话
        :param limit: 返回数量
        :return: 模板列表
        """
        templates = await FormatTemplateDao.get_popular_templates(query_db, limit)
        return [FormatTemplateModel(**CamelCaseUtil.transform_result(template)) for template in templates]

    @classmethod
    async def increment_template_usage(
        cls,
        query_db: AsyncSession,
        template_id: int
    ) -> None:
        """
        增加模板使用次数

        :param query_db: 数据库会话
        :param template_id: 模板ID
        :return:
        """
        try:
            await FormatTemplateDao.increment_usage_count(query_db, template_id)
            await query_db.commit()
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新使用次数失败: {str(e)}')

    # ==================== 格式规则管理 ====================

    @classmethod
    async def get_template_rules(
        cls,
        query_db: AsyncSession,
        template_id: int
    ) -> list[TemplateFormatRuleModel]:
        """
        获取模板的所有格式规则

        :param query_db: 数据库会话
        :param template_id: 模板ID
        :return: 规则列表
        """
        rules = await TemplateFormatRuleDao.get_rule_list_by_template(query_db, template_id)
        return [TemplateFormatRuleModel(**CamelCaseUtil.transform_result(rule)) for rule in rules]

    @classmethod
    async def get_rules_by_type(
        cls,
        query_db: AsyncSession,
        template_id: int,
        rule_type: str
    ) -> list[TemplateFormatRuleModel]:
        """
        根据规则类型获取规则列表

        :param query_db: 数据库会话
        :param template_id: 模板ID
        :param rule_type: 规则类型
        :return: 规则列表
        """
        rules = await TemplateFormatRuleDao.get_rules_by_type(query_db, template_id, rule_type)
        return [TemplateFormatRuleModel(**CamelCaseUtil.transform_result(rule)) for rule in rules]

    @classmethod
    async def create_rule(
        cls,
        query_db: AsyncSession,
        rule_data: TemplateFormatRuleModel
    ) -> CrudResponseModel:
        """
        创建格式规则

        :param query_db: 数据库会话
        :param rule_data: 规则数据
        :return: 操作结果
        """
        # 检查模板是否存在
        await cls.get_template_detail(query_db, rule_data.template_id)

        try:
            rule_dict = rule_data.model_dump(exclude_none=True)
            rule_dict['status'] = '0'  # 启用
            new_rule = await TemplateFormatRuleDao.add_rule(query_db, rule_dict)
            
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='规则创建成功',
                result={'rule_id': new_rule.rule_id}
            )
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'规则创建失败: {str(e)}')

    @classmethod
    async def batch_create_rules(
        cls,
        query_db: AsyncSession,
        template_id: int,
        rules_data: list[TemplateFormatRuleModel]
    ) -> CrudResponseModel:
        """
        批量创建格式规则

        :param query_db: 数据库会话
        :param template_id: 模板ID
        :param rules_data: 规则数据列表
        :return: 操作结果
        """
        # 检查模板是否存在
        await cls.get_template_detail(query_db, template_id)

        if not rules_data:
            raise ServiceException(message='规则数据不能为空')

        try:
            rules_dict = []
            for rule in rules_data:
                rule_dict = rule.model_dump(exclude_none=True)
                rule_dict['template_id'] = template_id
                rule_dict['status'] = '0'
                rules_dict.append(rule_dict)
            
            await TemplateFormatRuleDao.batch_add_rules(query_db, rules_dict)
            
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message=f'成功创建{len(rules_data)}条规则'
            )
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'批量创建规则失败: {str(e)}')

    @classmethod
    async def update_rule(
        cls,
        query_db: AsyncSession,
        rule_data: TemplateFormatRuleModel
    ) -> CrudResponseModel:
        """
        更新格式规则

        :param query_db: 数据库会话
        :param rule_data: 规则数据
        :return: 操作结果
        """
        # 检查规则是否存在
        rule = await TemplateFormatRuleDao.get_rule_by_id(query_db, rule_data.rule_id)
        if not rule:
            raise ServiceException(message='规则不存在')

        try:
            update_data = rule_data.model_dump(exclude_unset=True)
            update_data['update_time'] = datetime.now()
            await TemplateFormatRuleDao.update_rule(query_db, update_data)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='规则更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'规则更新失败: {str(e)}')

    @classmethod
    async def delete_rule(cls, query_db: AsyncSession, rule_id: int) -> CrudResponseModel:
        """
        删除格式规则

        :param query_db: 数据库会话
        :param rule_id: 规则ID
        :return: 操作结果
        """
        # 检查规则是否存在
        rule = await TemplateFormatRuleDao.get_rule_by_id(query_db, rule_id)
        if not rule:
            raise ServiceException(message='规则不存在')

        try:
            await TemplateFormatRuleDao.delete_rule(query_db, rule_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='规则删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'规则删除失败: {str(e)}')

    # ==================== 模板应用 ====================

    @classmethod
    async def apply_template_to_thesis(
        cls,
        query_db: AsyncSession,
        template_id: int,
        thesis_id: int
    ) -> CrudResponseModel:
        """
        将模板应用到论文

        :param query_db: 数据库会话
        :param template_id: 模板ID
        :param thesis_id: 论文ID
        :return: 操作结果
        """
        # 检查模板是否存在
        template = await cls.get_template_detail(query_db, template_id)
        
        # 获取模板的所有格式规则
        rules = await cls.get_template_rules(query_db, template_id)

        try:
            # 增加模板使用次数
            await cls.increment_template_usage(query_db, template_id)
            
            # 这里可以添加实际应用模板到论文的逻辑
            # 例如：更新论文的格式设置、应用样式等
            
            return CrudResponseModel(
                is_success=True,
                message='模板应用成功',
                result={
                    'template_name': template.template_name,
                    'rules_count': len(rules)
                }
            )
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'模板应用失败: {str(e)}')

    @classmethod
    async def _parse_template_format_in_background(
        cls,
        template_id: int,
        file_path: str
    ) -> None:
        """
        后台任务：解析模板格式数据
        
        :param template_id: 模板ID
        :param file_path: 模板文件路径
        """
        import sys
        import traceback
        import asyncio
        import os
        from datetime import datetime
        import time
        
        # 记录任务开始时间
        start_time = time.time()
        start_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 立即输出，确保任务已启动
        print("=" * 100)
        print(f"[格式解析任务] ✓ 任务已开始执行")
        print(f"  开始时间: {start_datetime}")
        print(f"  模板ID: {template_id}")
        print(f"  文件路径: {file_path}")
        print(f"  文件是否存在: {os.path.exists(file_path) if file_path else False}")
        if file_path and os.path.exists(file_path):
            print(f"  文件大小: {os.path.getsize(file_path)} 字节")
        print(f"  当前事件循环: {asyncio.get_event_loop()}")
        print("=" * 100)
        sys.stdout.flush()  # 强制刷新输出
        sys.stderr.flush()
        
        from config.database import AsyncSessionLocal
        from utils.log_util import logger
        
        logger.info("=" * 100)
        logger.info(f"[格式解析任务] 任务已开始执行")
        logger.info(f"  开始时间: {start_datetime}")
        logger.info(f"  模板ID: {template_id}")
        logger.info(f"  文件路径: {file_path}")
        logger.info(f"  文件是否存在: {os.path.exists(file_path) if file_path else False}")
        if file_path and os.path.exists(file_path):
            logger.info(f"  文件大小: {os.path.getsize(file_path)} 字节")
        logger.info("=" * 100)
        
        try:
            # 使用全局的数据库会话工厂（后台任务需要独立的会话）
            async with AsyncSessionLocal() as db:
                try:
                    import sys
                    sys.stdout.flush()
                    
                    from module_thesis.service.format_service import FormatService
                    
                    # 同时使用print和logger确保输出可见
                    print("=" * 100)
                    print(f"[后台任务] 开始解析模板格式")
                    print(f"  模板ID: {template_id}")
                    print(f"  文件路径: {file_path}")
                    print("=" * 100)
                    sys.stdout.flush()
                    sys.stderr.flush()
                    
                    logger.info("=" * 100)
                    logger.info(f"[后台任务] 开始解析模板格式")
                    logger.info(f"  模板ID: {template_id}")
                    logger.info(f"  文件路径: {file_path}")
                    logger.info("=" * 100)
                    
                    # 步骤1: 检查文件是否存在
                    step1_start = time.time()
                    import os
                    if not os.path.exists(file_path):
                        error_msg = f"模板文件不存在: {file_path}"
                        print(f"[错误] {error_msg}")
                        logger.error(error_msg)
                        raise FileNotFoundError(error_msg)
                    file_size = os.path.getsize(file_path)
                    step1_elapsed = time.time() - step1_start
                    print(f"[步骤1/4] ✓ 文件存在检查通过")
                    print(f"  文件大小: {file_size} 字节 ({file_size / 1024:.2f} KB)")
                    print(f"  耗时: {step1_elapsed:.2f} 秒")
                    logger.info(f"[步骤1/4] ✓ 文件存在检查通过")
                    logger.info(f"  文件大小: {file_size} 字节 ({file_size / 1024:.2f} KB)")
                    logger.info(f"  耗时: {step1_elapsed:.2f} 秒")
                    
                    # 步骤2: 读取Word文档并提取格式指令
                    step2_start = time.time()
                    print("=" * 100)
                    print(f"[步骤2/4] 开始读取Word文档并提取格式信息...")
                    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  文件路径: {file_path}")
                    print(f"  即将调用AI模型分析文档格式...")
                    print("=" * 100)
                    import sys
                    sys.stdout.flush()
                    logger.info("=" * 100)
                    logger.info(f"[步骤2/4] 开始读取Word文档并提取格式信息...")
                    logger.info(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"  文件路径: {file_path}")
                    logger.info("=" * 100)
                    
                    try:
                        read_result = await FormatService.read_word_document_with_ai(db, file_path)
                        format_instructions = read_result.get('format_instructions', '')
                        natural_language_description = read_result.get('natural_language_description', '')
                        step2_elapsed = time.time() - step2_start
                        print("=" * 100)
                        print(f"[步骤2/4] ✓ Word文档读取和AI分析完成")
                        print(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"  耗时: {step2_elapsed:.2f} 秒 ({step2_elapsed / 60:.2f} 分钟)")
                        print(f"  自然语言描述长度: {len(natural_language_description)} 字符")
                        print(f"  JSON格式指令长度: {len(format_instructions)} 字符")
                        print("=" * 100)
                        sys.stdout.flush()
                        logger.info("=" * 100)
                        logger.info(f"[步骤2/4] ✓ Word文档读取和AI分析完成")
                        logger.info(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        logger.info(f"  耗时: {step2_elapsed:.2f} 秒 ({step2_elapsed / 60:.2f} 分钟)")
                        logger.info(f"  自然语言描述长度: {len(natural_language_description)} 字符")
                        logger.info(f"  JSON格式指令长度: {len(format_instructions)} 字符")
                        logger.info("=" * 100)
                    except Exception as e:
                        print("=" * 100)
                        print(f"[步骤2/4] ✗ Word文档读取或AI分析失败")
                        print(f"  错误: {str(e)}")
                        import traceback
                        print(traceback.format_exc())
                        print("=" * 100)
                        sys.stdout.flush()
                        logger.error("=" * 100)
                        logger.error(f"[步骤2/4] ✗ Word文档读取或AI分析失败")
                        logger.error(f"  错误: {str(e)}")
                        logger.error("=" * 100, exc_info=True)
                        raise
                    
                    print(f"[步骤2/4] Word文档读取完成")
                    if natural_language_description:
                        print(f"  自然语言描述（前200字符）: {natural_language_description[:200]}...")
                    print(f"  JSON格式指令长度: {len(format_instructions)} 字符")
                    print(f"  JSON格式指令内容（前500字符）: {format_instructions[:500]}")
                    logger.info(f"[步骤2/4] Word文档读取完成")
                    if natural_language_description:
                        logger.info(f"  自然语言描述（前200字符）: {natural_language_description[:200]}...")
                    logger.info(f"  JSON格式指令长度: {len(format_instructions)} 字符")
                    logger.debug(f"  JSON格式指令内容（前500字符）: {format_instructions[:500]}")
                    
                    # 步骤3: 尝试解析为JSON格式
                    step3_start = time.time()
                    import json
                    print(f"[步骤3/4] 开始解析格式指令为JSON...")
                    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"[步骤3/4] 开始解析格式指令为JSON...")
                    logger.info(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    try:
                        format_data = json.loads(format_instructions) if isinstance(format_instructions, str) else format_instructions
                        step3_elapsed = time.time() - step3_start
                        print(f"[步骤3/4] ✓ JSON解析成功")
                        print(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"  耗时: {step3_elapsed:.2f} 秒")
                        print(f"  格式指令类型: {type(format_data).__name__}")
                        logger.info(f"[步骤3/4] ✓ JSON解析成功")
                        logger.info(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        logger.info(f"  耗时: {step3_elapsed:.2f} 秒")
                        logger.info(f"  格式指令类型: {type(format_data).__name__}")
                        if isinstance(format_data, dict):
                            keys = list(format_data.keys())
                            print(f"  格式指令包含的键: {keys}")
                            logger.info(f"  格式指令包含的键: {keys}")
                            if 'format_rules' in format_data:
                                format_rules_keys = list(format_data['format_rules'].keys()) if isinstance(format_data['format_rules'], dict) else 'N/A'
                                print(f"  format_rules 包含的键: {format_rules_keys}")
                                logger.info(f"  format_rules 包含的键: {format_rules_keys}")
                            if 'layout_rules' in format_data:
                                layout_rules_keys = list(format_data['layout_rules'].keys()) if isinstance(format_data['layout_rules'], dict) else 'N/A'
                                print(f"  layout_rules 包含的键: {layout_rules_keys}")
                                logger.info(f"  layout_rules 包含的键: {layout_rules_keys}")
                    except (json.JSONDecodeError, TypeError) as e:
                        error_msg = f"[步骤3/4] JSON解析失败，尝试提取JSON部分: {str(e)}"
                        print(error_msg)
                        logger.warning(error_msg)
                        # 如果解析失败，尝试提取JSON部分
                        format_data = FormatService._extract_json_from_text(format_instructions)
                        print(f"[步骤3/4] JSON提取完成")
                        logger.info(f"[步骤3/4] JSON提取完成")
                        if isinstance(format_data, dict):
                            keys = list(format_data.keys())
                            print(f"  提取的格式指令包含的键: {keys}")
                            logger.info(f"  提取的格式指令包含的键: {keys}")
                    
                    # 步骤3.5: 提取固定页面（封面、原创性声明等）
                    step3_5_start = time.time()
                    print(f"[步骤3.5/5] 开始提取固定页面...")
                    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"[步骤3.5/5] 开始提取固定页面...")
                    logger.info(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    special_pages = {}
                    try:
                        # 验证 file_path 是否存在
                        import os
                        if not os.path.exists(file_path):
                            error_msg = f"[步骤3.5/5] ✗ 模板文件不存在，无法提取固定页面: {file_path}"
                            print(error_msg)
                            logger.error(error_msg)
                            raise FileNotFoundError(f"模板文件不存在: {file_path}")
                        
                        file_size = os.path.getsize(file_path)
                        print(f"[步骤3.5/5] 模板文件验证: 路径={file_path}, 大小={file_size} 字节")
                        logger.info(f"[步骤3.5/5] 模板文件验证: 路径={file_path}, 大小={file_size} 字节")
                        
                        special_pages = await FormatService.extract_special_pages(file_path, template_id)
                        step3_5_elapsed = time.time() - step3_5_start
                        
                        if special_pages:
                            print(f"[步骤3.5/5] ✓ 固定页面提取完成")
                            print(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"  耗时: {step3_5_elapsed:.2f} 秒")
                            print(f"  提取的页面: {list(special_pages.keys())}")
                            for page_type, page_info in special_pages.items():
                                print(f"    - {page_type}: {page_info.get('file_path', 'N/A')}")
                            logger.info(f"[步骤3.5/5] ✓ 固定页面提取完成")
                            logger.info(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            logger.info(f"  耗时: {step3_5_elapsed:.2f} 秒")
                            logger.info(f"  提取的页面: {list(special_pages.keys())}")
                            
                            # 将 special_pages 添加到 format_data
                            if isinstance(format_data, dict):
                                # 验证 format_data 结构
                                format_data_keys_before = list(format_data.keys())
                                print(f"  format_data 添加前包含的键: {format_data_keys_before}")
                                logger.info(f"  format_data 添加前包含的键: {format_data_keys_before}")
                                
                                format_data['special_pages'] = special_pages
                                
                                format_data_keys_after = list(format_data.keys())
                                print(f"  format_data 添加后包含的键: {format_data_keys_after}")
                                logger.info(f"  format_data 添加后包含的键: {format_data_keys_after}")
                                
                                # 验证 special_pages 是否正确添加
                                if 'special_pages' in format_data:
                                    special_pages_in_format = format_data['special_pages']
                                    print(f"  ✓ 已将 special_pages 添加到 format_data")
                                    print(f"  special_pages 内容: {list(special_pages_in_format.keys())}")
                                    logger.info(f"  ✓ 已将 special_pages 添加到 format_data")
                                    logger.info(f"  special_pages 内容: {list(special_pages_in_format.keys())}")
                                    
                                    # 验证每个页面的 file_path
                                    for page_type, page_info in special_pages_in_format.items():
                                        file_path_in_info = page_info.get('file_path', 'N/A')
                                        print(f"    - {page_type}: {file_path_in_info}")
                                        logger.info(f"    - {page_type}: {file_path_in_info}")
                                else:
                                    error_msg = "  ✗ special_pages 未成功添加到 format_data"
                                    print(error_msg)
                                    logger.error(error_msg)
                            else:
                                error_msg = f"  ✗ format_data 不是字典类型，无法添加 special_pages (类型: {type(format_data).__name__})"
                                print(error_msg)
                                logger.error(error_msg)
                        else:
                            print(f"[步骤3.5/5] ⚠ 未提取到固定页面（可能模板中没有封面、声明等页面）")
                            logger.info(f"[步骤3.5/5] ⚠ 未提取到固定页面（可能模板中没有封面、声明等页面）")
                    except Exception as e:
                        step3_5_elapsed = time.time() - step3_5_start
                        error_msg = f"[步骤3.5/5] ✗ 固定页面提取失败: {str(e)}"
                        print(error_msg)
                        logger.warning(error_msg, exc_info=True)
                        # 提取失败不影响格式数据保存，继续执行
                    
                    # 步骤4: 保存格式数据到数据库
                    step4_start = time.time()
                    # 将format_data转换为JSON字符串以便存储
                    format_data_json_str = json.dumps(format_data, ensure_ascii=False, indent=2)
                    print(f"[步骤4/5] 准备保存格式数据到数据库...")
                    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  格式数据JSON字符串长度: {len(format_data_json_str)} 字符")
                    print(f"  模板ID: {template_id}")
                    if 'special_pages' in format_data:
                        print(f"  special_pages 已包含在 format_data 中: {list(format_data['special_pages'].keys())}")
                    logger.info(f"[步骤4/5] 准备保存格式数据到数据库...")
                    logger.info(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"  格式数据JSON字符串长度: {len(format_data_json_str)} 字符")
                    logger.info(f"  模板ID: {template_id}")
                    if 'special_pages' in format_data:
                        logger.info(f"  special_pages 已包含在 format_data 中: {list(format_data['special_pages'].keys())}")
                    
                    # 查询更新前的状态
                    template_before = await FormatTemplateDao.get_template_by_id(db, template_id)
                    format_data_before = template_before.format_data if template_before else None
                    print(f"  更新前 format_data 状态: {'存在' if format_data_before else '不存在'}")
                    if format_data_before:
                        print(f"  更新前 format_data 类型: {type(format_data_before).__name__}")
                        if isinstance(format_data_before, dict):
                            print(f"  更新前 format_data 键数量: {len(format_data_before)}")
                    logger.info(f"  更新前 format_data 状态: {'存在' if format_data_before else '不存在'}")
                    if format_data_before:
                        logger.info(f"  更新前 format_data 类型: {type(format_data_before).__name__}")
                        if isinstance(format_data_before, dict):
                            logger.info(f"  更新前 format_data 键数量: {len(format_data_before)}")
                    
                    # 更新模板的 format_data
                    print(f"  正在执行数据库更新操作...")
                    logger.info(f"  正在执行数据库更新操作...")
                    update_start = time.time()
                    await FormatTemplateDao.update_template(
                        db,
                        {
                            'template_id': template_id,
                            'format_data': format_data
                        }
                    )
                    update_elapsed = time.time() - update_start
                    print(f"  数据库更新操作完成，耗时: {update_elapsed:.2f} 秒")
                    logger.info(f"  数据库更新操作完成，耗时: {update_elapsed:.2f} 秒")
                    
                    print(f"  正在提交事务...")
                    logger.info(f"  正在提交事务...")
                    commit_start = time.time()
                    await db.commit()
                    commit_elapsed = time.time() - commit_start
                    print(f"  事务提交完成，耗时: {commit_elapsed:.2f} 秒")
                    logger.info(f"  事务提交完成，耗时: {commit_elapsed:.2f} 秒")
                    
                    # 验证更新后的状态
                    template_after = await FormatTemplateDao.get_template_by_id(db, template_id)
                    format_data_after = template_after.format_data if template_after else None
                    print(f"  更新后 format_data 状态: {'存在' if format_data_after else '不存在'}")
                    if format_data_after:
                        print(f"  更新后 format_data 类型: {type(format_data_after).__name__}")
                        if isinstance(format_data_after, dict):
                            print(f"  更新后 format_data 键数量: {len(format_data_after)}")
                            print(f"  更新后 format_data 键: {list(format_data_after.keys())[:10]}...")
                    logger.info(f"  更新后 format_data 状态: {'存在' if format_data_after else '不存在'}")
                    if format_data_after:
                        logger.info(f"  更新后 format_data 类型: {type(format_data_after).__name__}")
                        if isinstance(format_data_after, dict):
                            logger.info(f"  更新后 format_data 键数量: {len(format_data_after)}")
                            logger.info(f"  更新后 format_data 键: {list(format_data_after.keys())[:10]}...")
                    
                    step4_elapsed = time.time() - step4_start
                    total_elapsed = time.time() - start_time
                    
                    print("=" * 100)
                    print(f"[后台任务] ✓ 成功解析模板格式")
                    print(f"  模板ID: {template_id}")
                    print(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  总耗时: {total_elapsed:.2f} 秒 ({total_elapsed / 60:.2f} 分钟)")
                    print(f"  步骤4耗时: {step4_elapsed:.2f} 秒")
                    print(f"  格式数据已保存到数据库")
                    print(f"  格式数据大小: {len(format_data_json_str)} 字符")
                    print(f"  格式数据更新: {'成功' if format_data_after else '失败（未找到数据）'}")
                    if 'special_pages' in format_data:
                        print(f"  固定页面: {list(format_data['special_pages'].keys())}")
                    print("=" * 100)
                    sys.stdout.flush()
                    logger.info("=" * 100)
                    logger.info(f"[后台任务] ✓ 成功解析模板格式")
                    logger.info(f"  模板ID: {template_id}")
                    logger.info(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"  总耗时: {total_elapsed:.2f} 秒 ({total_elapsed / 60:.2f} 分钟)")
                    logger.info(f"  步骤4耗时: {step4_elapsed:.2f} 秒")
                    logger.info(f"  格式数据已保存到数据库")
                    logger.info(f"  格式数据大小: {len(format_data_json_str)} 字符")
                    logger.info(f"  格式数据更新: {'成功' if format_data_after else '失败（未找到数据）'}")
                    logger.info("=" * 100)
                except ServiceException as e:
                    await db.rollback()
                    total_elapsed = time.time() - start_time
                    # ServiceException 有 message 属性
                    error_msg = e.message if hasattr(e, 'message') and e.message else (str(e) if str(e) else repr(e))
                    error_type = type(e).__name__
                    print("=" * 100)
                    print(f"[后台任务] ✗ 解析模板格式失败 (ServiceException)")
                    print(f"  失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  总耗时: {total_elapsed:.2f} 秒 ({total_elapsed / 60:.2f} 分钟)")
                    print(f"  模板ID: {template_id}")
                    print(f"  错误类型: {error_type}")
                    print(f"  错误信息: {error_msg}")
                    if hasattr(e, 'data') and e.data:
                        print(f"  错误数据: {e.data}")
                    print("=" * 100)
                    import traceback
                    print(traceback.format_exc())
                    sys.stdout.flush()
                    logger.error("=" * 100)
                    logger.error(f"[后台任务] ✗ 解析模板格式失败 (ServiceException)")
                    logger.error(f"  失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.error(f"  总耗时: {total_elapsed:.2f} 秒 ({total_elapsed / 60:.2f} 分钟)")
                    logger.error(f"  模板ID: {template_id}")
                    logger.error(f"  错误类型: {error_type}")
                    logger.error(f"  错误信息: {error_msg}")
                    if hasattr(e, 'data') and e.data:
                        logger.error(f"  错误数据: {e.data}")
                    logger.error("=" * 100, exc_info=True)
                except Exception as e:
                    await db.rollback()
                    total_elapsed = time.time() - start_time
                    # 获取完整的错误信息
                    error_msg = str(e) if str(e) else repr(e)
                    error_type = type(e).__name__
                    print("=" * 100)
                    print(f"[后台任务] ✗ 解析模板格式失败 ({error_type})")
                    print(f"  失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  总耗时: {total_elapsed:.2f} 秒 ({total_elapsed / 60:.2f} 分钟)")
                    print(f"  模板ID: {template_id}")
                    print(f"  错误类型: {error_type}")
                    print(f"  错误信息: {error_msg}")
                    print("=" * 100)
                    import traceback
                    print(traceback.format_exc())
                    sys.stdout.flush()
                    logger.error("=" * 100)
                    logger.error(f"[后台任务] ✗ 解析模板格式失败 ({error_type})")
                    logger.error(f"  失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.error(f"  总耗时: {total_elapsed:.2f} 秒 ({total_elapsed / 60:.2f} 分钟)")
                    logger.error(f"  模板ID: {template_id}")
                    logger.error(f"  错误类型: {error_type}")
                    logger.error(f"  错误信息: {error_msg}")
                    logger.error("=" * 100, exc_info=True)
        except Exception as e:
            total_elapsed = time.time() - start_time
            error_msg = str(e)
            error_type = type(e).__name__
            print("=" * 100)
            print(f"[后台任务] ✗ 执行失败")
            print(f"  失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  总耗时: {total_elapsed:.2f} 秒 ({total_elapsed / 60:.2f} 分钟)")
            print(f"  模板ID: {template_id}")
            print(f"  错误信息: {error_msg}")
            print(f"  错误类型: {error_type}")
            print("=" * 100)
            import traceback
            print(traceback.format_exc())
            sys.stdout.flush()
            logger.error("=" * 100)
            logger.error(f"[后台任务] ✗ 执行失败")
            logger.error(f"  失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.error(f"  总耗时: {total_elapsed:.2f} 秒 ({total_elapsed / 60:.2f} 分钟)")
            logger.error(f"  模板ID: {template_id}")
            logger.error(f"  错误信息: {error_msg}")
            logger.error(f"  错误类型: {error_type}")
            logger.error("=" * 100, exc_info=True)
