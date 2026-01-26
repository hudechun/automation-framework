"""
论文管理控制器
"""
from datetime import datetime
from typing import Annotated

from fastapi import Path, Query, Request, Response
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
from module_thesis.service import ThesisService
from utils.log_util import logger
from utils.response_util import ResponseUtil

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
    return ResponseUtil.success(msg=result.message, data=result.data)


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
@ValidateFields(validate_model='add_outline')
@Log(title='论文大纲', business_type=BusinessType.INSERT)
async def generate_outline(
    request: Request,
    thesis_id: Annotated[int, Path(description='论文ID')],
    outline_data: ThesisOutlineModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """生成论文大纲"""
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权操作此论文')
    
    outline_data.thesis_id = thesis_id
    outline_data.create_by = current_user.user.user_name
    outline_data.create_time = datetime.now()
    
    result = await ThesisService.generate_outline(
        query_db,
        outline_data,
        current_user.user.user_id
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.data)


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
    # 权限检查
    thesis = await ThesisService.get_thesis_detail(query_db, thesis_id)
    if not current_user.user.admin and thesis.user_id != current_user.user.user_id:
        return ResponseUtil.error(msg='无权操作此论文')
    
    chapter_data.thesis_id = thesis_id
    chapter_data.create_by = current_user.user.user_name
    chapter_data.create_time = datetime.now()
    
    result = await ThesisService.generate_chapter(
        query_db,
        chapter_data,
        current_user.user.user_id
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.data)


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
