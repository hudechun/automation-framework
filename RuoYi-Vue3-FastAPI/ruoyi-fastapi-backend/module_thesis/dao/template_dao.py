"""
格式模板管理模块数据库操作层
"""
from typing import Any, Union

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_thesis.entity.do.template_do import AiWriteFormatTemplate, AiWriteTemplateFormatRule
from utils.page_util import PageUtil


class FormatTemplateDao:
    """
    格式模板数据访问对象
    """

    @classmethod
    async def get_template_by_id(cls, db: AsyncSession, template_id: int) -> Union[AiWriteFormatTemplate, None]:
        """
        根据模板ID获取模板详情

        :param db: orm对象
        :param template_id: 模板ID
        :return: 模板信息对象
        """
        template_info = (
            await db.execute(
                select(AiWriteFormatTemplate).where(
                    AiWriteFormatTemplate.template_id == template_id, AiWriteFormatTemplate.del_flag == '0'
                )
            )
        ).scalars().first()

        return template_info

    @classmethod
    async def get_template_list(
        cls, db: AsyncSession, query_object: dict = None, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取模板列表

        :param db: orm对象
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 模板列表
        """
        query_object = query_object or {}
        # 处理字段名映射：VO中使用school，数据库中使用school_name
        school_name = query_object.get('school_name') or query_object.get('school')
        template_name = query_object.get('template_name')
        
        query = (
            select(AiWriteFormatTemplate)
            .where(
                AiWriteFormatTemplate.template_name.like(f"%{template_name}%")
                if template_name
                else True,
                AiWriteFormatTemplate.school_name.like(f"%{school_name}%")
                if school_name
                else True,
                AiWriteFormatTemplate.major.like(f"%{query_object.get('major')}%")
                if query_object.get('major')
                else True,
                AiWriteFormatTemplate.degree_level == query_object.get('degree_level')
                if query_object.get('degree_level')
                else True,
                AiWriteFormatTemplate.is_official == query_object.get('is_official')
                if query_object.get('is_official') is not None
                else True,
                AiWriteFormatTemplate.status == query_object.get('status') if query_object.get('status') is not None else True,
                AiWriteFormatTemplate.del_flag == '0',
            )
            .order_by(AiWriteFormatTemplate.is_official.desc(), AiWriteFormatTemplate.usage_count.desc())
        )

        template_list: Union[PageModel, list[dict[str, Any]]] = await PageUtil.paginate(
            db, query, query_object.get('page_num', 1), query_object.get('page_size', 10), is_page
        )

        return template_list

    @classmethod
    async def add_template(cls, db: AsyncSession, template_data: dict) -> AiWriteFormatTemplate:
        """
        新增模板

        :param db: orm对象
        :param template_data: 模板数据
        :return: 模板对象
        """
        db_template = AiWriteFormatTemplate(**template_data)
        db.add(db_template)
        await db.flush()

        return db_template

    @classmethod
    async def update_template(cls, db: AsyncSession, template_data: dict) -> None:
        """
        更新模板

        :param db: orm对象
        :param template_data: 模板数据
        :return:
        """
        await db.execute(update(AiWriteFormatTemplate), [template_data])

    @classmethod
    async def delete_template(cls, db: AsyncSession, template_id: int) -> None:
        """
        删除模板（软删除）

        :param db: orm对象
        :param template_id: 模板ID
        :return:
        """
        await db.execute(
            update(AiWriteFormatTemplate).where(AiWriteFormatTemplate.template_id == template_id).values(del_flag='2')
        )

    @classmethod
    async def increment_usage_count(cls, db: AsyncSession, template_id: int) -> None:
        """
        增加模板使用次数

        :param db: orm对象
        :param template_id: 模板ID
        :return:
        """
        await db.execute(
            update(AiWriteFormatTemplate)
            .where(AiWriteFormatTemplate.template_id == template_id)
            .values(usage_count=AiWriteFormatTemplate.usage_count + 1)
        )

    @classmethod
    async def get_popular_templates(cls, db: AsyncSession, limit: int = 10) -> list[AiWriteFormatTemplate]:
        """
        获取热门模板

        :param db: orm对象
        :param limit: 返回数量
        :return: 模板列表
        """
        template_list = (
            await db.execute(
                select(AiWriteFormatTemplate)
                .where(AiWriteFormatTemplate.status == '0', AiWriteFormatTemplate.del_flag == '0')
                .order_by(AiWriteFormatTemplate.usage_count.desc())
                .limit(limit)
            )
        ).scalars().all()

        return list(template_list)

    @classmethod
    async def check_template_exists(
        cls, db: AsyncSession, school_name: str, degree_level: str, major: str = None
    ) -> bool:
        """
        检查模板是否已存在

        :param db: orm对象
        :param school_name: 学校名称
        :param degree_level: 学历层次
        :param major: 专业（可选）
        :return: 是否存在
        """
        count = (
            await db.execute(
                select(func.count(AiWriteFormatTemplate.template_id)).where(
                    AiWriteFormatTemplate.school_name == school_name,
                    AiWriteFormatTemplate.degree_level == degree_level,
                    AiWriteFormatTemplate.major == major if major else True,
                    AiWriteFormatTemplate.del_flag == '0',
                )
            )
        ).scalar()

        return count > 0


class TemplateFormatRuleDao:
    """
    模板格式规则数据访问对象
    """

    @classmethod
    async def get_rule_by_id(cls, db: AsyncSession, rule_id: int) -> Union[AiWriteTemplateFormatRule, None]:
        """
        根据规则ID获取规则详情

        :param db: orm对象
        :param rule_id: 规则ID
        :return: 规则信息对象
        """
        rule_info = (
            await db.execute(select(AiWriteTemplateFormatRule).where(AiWriteTemplateFormatRule.rule_id == rule_id))
        ).scalars().first()

        return rule_info

    @classmethod
    async def get_rule_list_by_template(cls, db: AsyncSession, template_id: int) -> list[AiWriteTemplateFormatRule]:
        """
        获取模板的所有格式规则

        :param db: orm对象
        :param template_id: 模板ID
        :return: 规则列表
        """
        rule_list = (
            await db.execute(
                select(AiWriteTemplateFormatRule)
                .where(
                    AiWriteTemplateFormatRule.template_id == template_id, AiWriteTemplateFormatRule.status == '0'
                )
                .order_by(AiWriteTemplateFormatRule.sort_order)
            )
        ).scalars().all()

        return list(rule_list)

    @classmethod
    async def get_rules_by_type(
        cls, db: AsyncSession, template_id: int, rule_type: str
    ) -> list[AiWriteTemplateFormatRule]:
        """
        根据规则类型获取规则列表

        :param db: orm对象
        :param template_id: 模板ID
        :param rule_type: 规则类型
        :return: 规则列表
        """
        rule_list = (
            await db.execute(
                select(AiWriteTemplateFormatRule).where(
                    AiWriteTemplateFormatRule.template_id == template_id,
                    AiWriteTemplateFormatRule.rule_type == rule_type,
                    AiWriteTemplateFormatRule.status == '0',
                )
            )
        ).scalars().all()

        return list(rule_list)

    @classmethod
    async def add_rule(cls, db: AsyncSession, rule_data: dict) -> AiWriteTemplateFormatRule:
        """
        新增格式规则

        :param db: orm对象
        :param rule_data: 规则数据
        :return: 规则对象
        """
        db_rule = AiWriteTemplateFormatRule(**rule_data)
        db.add(db_rule)
        await db.flush()

        return db_rule

    @classmethod
    async def batch_add_rules(cls, db: AsyncSession, rules_data: list[dict]) -> list[AiWriteTemplateFormatRule]:
        """
        批量新增格式规则

        :param db: orm对象
        :param rules_data: 规则数据列表
        :return: 规则对象列表
        """
        db_rules = [AiWriteTemplateFormatRule(**rule_data) for rule_data in rules_data]
        db.add_all(db_rules)
        await db.flush()

        return db_rules

    @classmethod
    async def update_rule(cls, db: AsyncSession, rule_data: dict) -> None:
        """
        更新格式规则

        :param db: orm对象
        :param rule_data: 规则数据
        :return:
        """
        await db.execute(update(AiWriteTemplateFormatRule), [rule_data])

    @classmethod
    async def delete_rule(cls, db: AsyncSession, rule_id: int) -> None:
        """
        删除格式规则

        :param db: orm对象
        :param rule_id: 规则ID
        :return:
        """
        await db.execute(delete(AiWriteTemplateFormatRule).where(AiWriteTemplateFormatRule.rule_id == rule_id))

    @classmethod
    async def delete_rules_by_template(cls, db: AsyncSession, template_id: int) -> None:
        """
        删除模板的所有格式规则

        :param db: orm对象
        :param template_id: 模板ID
        :return:
        """
        await db.execute(
            delete(AiWriteTemplateFormatRule).where(AiWriteTemplateFormatRule.template_id == template_id)
        )
