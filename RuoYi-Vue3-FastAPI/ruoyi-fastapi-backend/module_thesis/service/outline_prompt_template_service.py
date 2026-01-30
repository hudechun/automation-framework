"""
大纲提示词模板服务层
"""
from datetime import datetime
from typing import Any, Union

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_thesis.dao.outline_prompt_template_dao import OutlinePromptTemplateDao
from module_thesis.dao.template_dao import FormatTemplateDao
from module_thesis.entity.vo.outline_prompt_template_vo import (
    OutlinePromptTemplateModel,
    OutlinePromptTemplatePageQueryModel,
    OutlinePromptTemplateAddModel,
    OutlinePromptTemplateUpdateModel,
)
from utils.common_util import CamelCaseUtil
from utils.log_util import logger


class OutlinePromptTemplateService:
    """大纲提示词模板服务类"""

    @classmethod
    async def get_list(
        cls,
        query_db: AsyncSession,
        query_object: OutlinePromptTemplatePageQueryModel,
        is_page: bool = True,
    ) -> Union[PageModel, list]:
        """分页列表，支持 name、format_template_id、status 筛选；联表带出关联格式模板名称。"""
        query_dict = query_object.model_dump(exclude_none=True)
        result = await OutlinePromptTemplateDao.get_list(query_db, query_dict, is_page=is_page)
        # 联表带出格式模板名称
        rows = result.rows if isinstance(result, PageModel) else result
        if rows:
            ids = [r.get('formatTemplateId') for r in rows if r.get('formatTemplateId') is not None]
            id_to_name = await FormatTemplateDao.get_template_names_by_ids(query_db, ids) if ids else {}
            for r in rows:
                fid = r.get('formatTemplateId')
                r['formatTemplateName'] = id_to_name.get(fid) if fid is not None else None
        return result

    @classmethod
    async def get_by_id(
        cls, query_db: AsyncSession, prompt_template_id: int
    ) -> Union[OutlinePromptTemplateModel, None]:
        """按主键获取详情；联表带出关联格式模板名称。"""
        row = await OutlinePromptTemplateDao.get_by_id(query_db, prompt_template_id)
        if not row:
            return None
        data = CamelCaseUtil.transform_result(row)
        # 联表带出格式模板名称
        if getattr(row, 'format_template_id', None) is not None:
            id_to_name = await FormatTemplateDao.get_template_names_by_ids(
                query_db, [row.format_template_id]
            )
            data['formatTemplateName'] = id_to_name.get(row.format_template_id)
        else:
            data['formatTemplateName'] = None
        return OutlinePromptTemplateModel(**data)

    @classmethod
    async def add(
        cls,
        query_db: AsyncSession,
        data: OutlinePromptTemplateAddModel,
        create_by: str = '',
    ) -> CrudResponseModel:
        """新增。"""
        from module_thesis.entity.do.outline_prompt_template_do import AiWriteOutlinePromptTemplate
        do_fields = {c.key for c in AiWriteOutlinePromptTemplate.__table__.c}
        payload = data.model_dump(exclude_none=True)
        payload['create_by'] = create_by
        payload['create_time'] = datetime.now()
        payload['update_by'] = create_by
        payload['update_time'] = datetime.now()
        payload['del_flag'] = '0'
        filtered = {k: v for k, v in payload.items() if k in do_fields}
        row = await OutlinePromptTemplateDao.add(query_db, filtered)
        return CrudResponseModel(
            is_success=True,
            message='新增成功',
            result={'prompt_template_id': row.prompt_template_id},
        )

    @classmethod
    async def update(
        cls,
        query_db: AsyncSession,
        data: OutlinePromptTemplateUpdateModel,
        update_by: str = '',
    ) -> CrudResponseModel:
        """更新。"""
        existing = await OutlinePromptTemplateDao.get_by_id(query_db, data.prompt_template_id)
        if not existing:
            raise ServiceException(message='大纲提示词模板不存在')
        from module_thesis.entity.do.outline_prompt_template_do import AiWriteOutlinePromptTemplate
        do_fields = {c.key for c in AiWriteOutlinePromptTemplate.__table__.c}
        payload = data.model_dump(exclude_none=True, exclude={'prompt_template_id'})
        payload['update_by'] = update_by
        payload['update_time'] = datetime.now()
        filtered = {k: v for k, v in payload.items() if k in do_fields}
        await OutlinePromptTemplateDao.update_by_id(query_db, data.prompt_template_id, filtered)
        return CrudResponseModel(is_success=True, message='更新成功')

    @classmethod
    async def delete_logic(cls, query_db: AsyncSession, prompt_template_id: int) -> CrudResponseModel:
        """逻辑删除。"""
        existing = await OutlinePromptTemplateDao.get_by_id(query_db, prompt_template_id)
        if not existing:
            raise ServiceException(message='大纲提示词模板不存在')
        await OutlinePromptTemplateDao.delete_logic(query_db, prompt_template_id)
        return CrudResponseModel(is_success=True, message='删除成功')
