"""
论文管理控制器
"""
from datetime import datetime
from typing import Annotated, Optional

from fastapi import Path, Query, Request, Response
from fastapi.responses import StreamingResponse
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_thesis.entity.vo import (
    ThesisModel,
    ThesisOutlineModel,
    ThesisChapterModel,
    ThesisPageQueryModel,
)
from exceptions.exception import ServiceException
from module_thesis.service import ThesisService
from utils.log_util import logger
from utils.response_util import ResponseUtil
from utils.upload_util import UploadUtil

thesis_controller = APIRouterPro(
    prefix='/thesis/paper',
    order_num=2,
    tags=['论文系统-论文管理'],
    dependencies=[PreAuthDependency()]
)


# ==================== 论文管理 ====================

@thesis_controller.get(
    '/list',
    summary='获取论文列表',
    description='获取论文分页列表',
    response_model=PageResponseModel[ThesisModel],
)
async def get_thesis_list(
    request: Request,
    query: Annotated[ThesisPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取论文列表"""
    # 普通用户只能查看自己的论文
    if not current_user.user.admin:
        query.user_id = current_user.user.user_id
    
    result = await ThesisService.get_thesis_list(query_db, query, is_page=True)
    logger.info('获取论文列表成功')
    return ResponseUtil.success(model_content=result)


@thesis_controller.get(
    '/{thesis_id}',
    summary='获取论文详情',
    description='获取指定论文的详细信息',
    response_model=DataResponseModel[ThesisModel],
)
async def get_thesis_detail(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取论文详情"""
    result = await ThesisService.get_thesis_detail(query_db, thesis_id)
    
    # 权限检查：只能查看自己的论文（管理员除外）
    if not current_user.user.admin and result.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权访问此论文')
    
    logger.info(f'获取论文ID为{thesis_id}的信息成功')
    return ResponseUtil.success(data=result)


@thesis_controller.post(
    '',
    summary='创建论文',
    description='创建新论文（需要扣减配额）',
    response_model=ResponseBaseModel,
)
@ValidateFields(validate_model='add_thesis')
@Log(title='论文管理', business_type=BusinessType.INSERT)
async def create_thesis(
    request: Request,
    thesis_data: ThesisModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """创建论文"""
    thesis_data.create_by = current_user.user.user_name
    thesis_data.create_time = datetime.now()
    thesis_data.update_by = current_user.user.user_name
    thesis_data.update_time = datetime.now()
    
    result = await ThesisService.create_thesis(
        query_db,
        thesis_data,
        current_user.user.user_id
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@thesis_controller.put(
    '',
    summary='更新论文',
    description='更新论文信息',
    response_model=ResponseBaseModel,
)
@ValidateFields(validate_model='edit_thesis')
@Log(title='论文管理', business_type=BusinessType.UPDATE)
async def update_thesis(
    request: Request,
    thesis_data: ThesisModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新论文"""
    # 权限检查
    existing = await ThesisService.get_thesis_detail(query_db, thesis_data.thesis_id)
    if not current_user.user.admin and existing.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权修改此论文')
    
    thesis_data.update_by = current_user.user.user_name
    thesis_data.update_time = datetime.now()
    
    result = await ThesisService.update_thesis(query_db, thesis_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@thesis_controller.delete(
    '/{thesis_id}',
    summary='删除论文',
    description='删除指定论文',
    response_model=ResponseBaseModel,
)
@Log(title='论文管理', business_type=BusinessType.DELETE)
async def delete_thesis(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """删除论文"""
    # 权限检查
    existing = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and existing.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权删除此论文')
    
    result = await ThesisService.delete_thesis(query_db, thesis_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ==================== 大纲管理 ====================

@thesis_controller.get(
    '/{thesis_id}/outline',
    summary='获取论文大纲',
    description='获取指定论文的大纲',
    response_model=DataResponseModel[ThesisOutlineModel],
)
async def get_thesis_outline(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取论文大纲"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权访问此论文')
    
    result = await ThesisService.get_thesis_outline(query_db, thesis_id)
    logger.info('获取论文大纲成功')
    return ResponseUtil.success(data=result)


@thesis_controller.post(
    '/{thesis_id}/outline',
    summary='生成论文大纲',
    description='生成论文大纲（需要扣减配额）',
    response_model=ResponseBaseModel,
)
@Log(title='论文大纲', business_type=BusinessType.INSERT)
async def generate_outline(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    outline_data: Optional[ThesisOutlineModel] = None,
) -> Response:
    """生成论文大纲"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权操作此论文')
    
    # 如果前端没有传递 outline_data，创建一个默认的
    if outline_data is None:
        outline_data = ThesisOutlineModel(thesis_id=thesis_id)
    else:
        outline_data.thesis_id = thesis_id
    
    outline_data.create_by = current_user.user.user_name
    outline_data.create_time = datetime.now()
    
    result = await ThesisService.generate_outline(
        query_db,
        outline_data,
        current_user.user.user_id
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


# ==================== 章节管理 ====================

@thesis_controller.get(
    '/{thesis_id}/chapters',
    summary='获取论文章节',
    description='获取指定论文的所有章节',
    response_model=DataResponseModel,
)
async def get_thesis_chapters(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取论文章节"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权访问此论文')
    
    result = await ThesisService.get_thesis_chapters(query_db, thesis_id)
    logger.info('获取论文章节成功')
    return ResponseUtil.success(data=result)


@thesis_controller.get(
    '/{thesis_id}/chapters/progress',
    summary='获取章节生成进度',
    description='获取指定论文的章节生成进度',
    response_model=DataResponseModel,
)
async def get_chapter_generation_progress(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取章节生成进度"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权访问此论文')
    
    result = await ThesisService.get_chapter_generation_progress(query_db, thesis_id)
    logger.info('获取章节生成进度成功')
    return ResponseUtil.success(data=result)


@thesis_controller.post(
    '/{thesis_id}/chapters/continue',
    summary='继续生成未完成的章节',
    description='继续生成未完成的章节（断点续传）',
    response_model=ResponseBaseModel,
)
@Log(title='继续生成章节', business_type=BusinessType.UPDATE)
async def continue_generate_chapters(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """继续生成未完成的章节"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权操作此论文')
    
    result = await ThesisService.continue_generate_chapters(
        query_db,
        thesis_id,
        current_user.user.user_id
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@thesis_controller.post(
    '/{thesis_id}/chapter',
    summary='生成论文章节',
    description='生成单个论文章节（需要扣减配额）',
    response_model=ResponseBaseModel,
)
@ValidateFields(validate_model='add_chapter')
@Log(title='论文章节', business_type=BusinessType.INSERT)
async def generate_chapter(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    chapter_data: ThesisChapterModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """生成论文章节"""
    try:
        # 记录接收到的数据（用于调试）
        logger.info(f'接收章节生成请求 - 论文ID: {thesis_id}, 数据: chapter_number={chapter_data.chapter_number}, chapter_title={chapter_data.chapter_title}')
        
        # 权限检查
        thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
        if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
            return ResponseUtil.error(msg='无权操作此论文')
        
        # 验证必要字段
        if not chapter_data.chapter_number:
            logger.warning(f'章节号为空 - 论文ID: {thesis_id}')
            return ResponseUtil.error(msg='章节号不能为空')
        if not chapter_data.chapter_title:
            logger.warning(f'章节标题为空 - 论文ID: {thesis_id}')
            return ResponseUtil.error(msg='章节标题不能为空')
        
        chapter_data.thesis_id = thesis_id
        chapter_data.create_by = current_user.user.user_name
        chapter_data.create_time = datetime.now()
        
        logger.info(f'开始生成章节 - 论文ID: {thesis_id}, 章节: {chapter_data.chapter_title}')
        result = await ThesisService.generate_chapter(
            query_db,
            chapter_data,
            current_user.user.user_id
        )
        logger.info(result.message)
        return ResponseUtil.success(msg=result.message, data=result.result)
    except ServiceException as e:
        # ServiceException 有 message 属性
        error_msg = e.message if e.message else '服务异常'
        logger.error(f'生成章节失败 - 论文ID: {thesis_id}, ServiceException: {error_msg}', exc_info=True)
        return ResponseUtil.error(msg=error_msg)
    except Exception as e:
        # 获取更详细的错误信息
        error_type = type(e).__name__
        
        # 尝试多种方式获取错误消息
        error_msg = None
        if hasattr(e, 'message') and e.message:
            error_msg = e.message
        elif hasattr(e, 'msg') and e.msg:
            error_msg = e.msg
        elif str(e) and str(e).strip():
            error_msg = str(e)
        elif repr(e):
            error_msg = repr(e)
        
        # 如果仍然没有错误消息，使用默认值
        if not error_msg or error_msg.strip() == '':
            error_msg = f'{error_type}: 未知错误，请查看服务器日志'
        
        # 记录完整的错误信息
        logger.error(
            f'生成章节失败 - 论文ID: {thesis_id}, '
            f'错误类型: {error_type}, '
            f'错误信息: {error_msg}',
            exc_info=True
        )
        
        return ResponseUtil.error(msg=f'生成章节失败: {error_msg}')


@thesis_controller.post(
    '/{thesis_id}/chapters/batch',
    summary='批量生成论文章节',
    description='批量生成多个论文章节（需要扣减配额，在开始前统一检查配额）',
    response_model=ResponseBaseModel,
)
@Log(title='批量生成论文章节', business_type=BusinessType.INSERT)
async def batch_generate_chapters(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    chapters_data: list[ThesisChapterModel],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """批量生成论文章节"""
    try:
        # 权限检查
        thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
        if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
            return ResponseUtil.error(msg='无权操作此论文')
        
        if not chapters_data or len(chapters_data) == 0:
            return ResponseUtil.error(msg='章节数据不能为空')
        
        logger.info(f'开始批量生成章节 - 论文ID: {thesis_id}, 章节数: {len(chapters_data)}')
        result = await ThesisService.batch_generate_chapters(
            query_db,
            thesis_id,
            chapters_data,
            current_user.user.user_id
        )
        logger.info(result.message)
        return ResponseUtil.success(msg=result.message, data=result.result)
    except ServiceException as e:
        error_msg = e.message if e.message else '服务异常'
        logger.error(f'批量生成章节失败 - 论文ID: {thesis_id}, ServiceException: {error_msg}', exc_info=True)
        return ResponseUtil.error(msg=error_msg)
    except Exception as e:
        error_type = type(e).__name__
        error_msg = None
        if hasattr(e, 'message') and e.message:
            error_msg = e.message
        elif hasattr(e, 'msg') and e.msg:
            error_msg = e.msg
        elif str(e) and str(e).strip():
            error_msg = str(e)
        elif repr(e):
            error_msg = repr(e)
        
        if not error_msg or error_msg.strip() == '':
            error_msg = f'{error_type}: 未知错误，请查看服务器日志'
        
        logger.error(
            f'批量生成章节失败 - 论文ID: {thesis_id}, '
            f'错误类型: {error_type}, '
            f'错误信息: {error_msg}',
            exc_info=True
        )
        
        return ResponseUtil.error(msg=f'批量生成章节失败: {error_msg}')


@thesis_controller.put(
    '/chapter',
    summary='更新章节',
    description='更新章节内容',
    response_model=ResponseBaseModel,
)
@ValidateFields(validate_model='edit_chapter')
@Log(title='论文章节', business_type=BusinessType.UPDATE)
async def update_chapter(
    request: Request,
    chapter_data: ThesisChapterModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新章节"""
    chapter_data.update_by = current_user.user.user_name
    chapter_data.update_time = datetime.now()
    
    result = await ThesisService.update_chapter(query_db, chapter_data)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@thesis_controller.delete(
    '/chapter/{chapter_id}',
    summary='删除章节',
    description='删除指定章节',
    response_model=ResponseBaseModel,
)
@Log(title='论文章节', business_type=BusinessType.DELETE)
async def delete_chapter(
    request: Request,
    chapter_id: Annotated[int, Path(description='章节ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除章节"""
    result = await ThesisService.delete_chapter(query_db, chapter_id)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ==================== 版本管理 ====================

@thesis_controller.get(
    '/{thesis_id}/versions',
    summary='获取论文版本历史',
    description='获取指定论文的版本历史',
    response_model=DataResponseModel,
)
async def get_thesis_versions(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    limit: Annotated[int, Query(description='返回数量', ge=1, le=50)] = 10,
) -> Response:
    """获取论文版本历史"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权访问此论文')
    
    result = await ThesisService.get_thesis_versions(query_db, thesis_id, limit)
    logger.info('获取版本历史成功')
    return ResponseUtil.success(data=result)


# ==================== 统计信息 ====================

@thesis_controller.get(
    '/statistics/count',
    summary='获取论文统计',
    description='获取用户论文数量统计',
    response_model=DataResponseModel[int],
)
async def get_thesis_count(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    status: Annotated[str | None, Query(description='论文状态')] = None,
) -> Response:
    """获取论文统计"""
    result = await ThesisService.get_user_thesis_count(
        query_db,
        current_user.user.user_id,
        status
    )
    return ResponseUtil.success(data=result)


# ==================== 论文格式化 ====================

@thesis_controller.get(
    '/{thesis_id}/progress',
    summary='获取论文生成进度',
    description='获取论文的生成进度（大纲20%，生成40%，格式化40%）',
    response_model=DataResponseModel,
)
async def get_thesis_progress(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取论文生成进度"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权访问此论文')
    
    result = await ThesisService.get_thesis_progress(query_db, thesis_id)
    logger.info('获取论文生成进度成功')
    return ResponseUtil.success(data=result)


@thesis_controller.post(
    '/{thesis_id}/format',
    summary='格式化论文',
    description='从模板表读取Word文档，使用AI提取格式指令，然后格式化论文',
    response_model=ResponseBaseModel,
)
@Log(title='论文格式化', business_type=BusinessType.UPDATE)
async def format_thesis(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """格式化论文"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权操作此论文')
    
    result = await ThesisService.format_thesis(
        query_db,
        thesis_id,
        current_user.user.user_id
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@thesis_controller.get(
    '/{thesis_id}/download',
    summary='下载格式化后的论文',
    description='下载已格式化的Word文档',
    response_class=StreamingResponse,
    responses={
        200: {
            'description': '流式返回文件',
            'content': {
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {},
            },
        }
    },
)
@Log(title='论文下载', business_type=BusinessType.EXPORT)
async def download_thesis(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> StreamingResponse:
    """下载格式化后的论文"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权下载此论文')
    
    # 获取文件信息
    file_info = await ThesisService.download_thesis(
        query_db,
        thesis_id,
        current_user.user.user_id
    )
    
    # 生成文件流
    file_generator = UploadUtil.generate_file(file_info['file_path'])
    
    # 处理文件名编码（支持中文）
    from urllib.parse import quote
    encoded_filename = quote(file_info['file_name'], safe='')
    
    # 设置响应头（使用RFC 5987格式支持中文文件名）
    headers = {
        'Content-Disposition': f'attachment; filename="{file_info["file_name"]}"; filename*=UTF-8\'\'{encoded_filename}',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    # 安全地记录日志，避免中文字符编码问题
    try:
        logger.info(f'用户 {current_user.user.user_name} 下载论文 ID: {thesis_id}, 文件名: {file_info["file_name"]}')
    except UnicodeEncodeError:
        # 如果文件名包含无法编码的字符，使用安全的编码方式
        safe_filename = file_info["file_name"].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        logger.info(f'用户 {current_user.user.user_name} 下载论文 ID: {thesis_id}, 文件名: {safe_filename}')
    return ResponseUtil.streaming(data=file_generator, headers=headers)
