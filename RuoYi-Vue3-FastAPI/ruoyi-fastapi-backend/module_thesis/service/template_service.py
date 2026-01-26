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
        user_id: int = None
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
            template_dict = template_data.model_dump(exclude_none=True)
            
            # 设置是否为官方模板
            if user_id:
                template_dict['is_official'] = '0'  # 用户上传
                template_dict['create_by'] = str(user_id)
            else:
                template_dict['is_official'] = '1'  # 管理员上传
            
            template_dict['usage_count'] = 0
            template_dict['status'] = '0'  # 启用
            
            new_template = await FormatTemplateDao.add_template(query_db, template_dict)
            # 在flush后立即获取ID，避免commit后访问
            template_id = new_template.template_id
            
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='模板创建成功',
                result={'template_id': template_id}
            )
        except ServiceException as e:
            await query_db.rollback()
            raise e
        except Exception as e:
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
