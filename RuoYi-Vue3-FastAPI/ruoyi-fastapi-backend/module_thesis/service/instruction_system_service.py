"""
指令系统管理服务层
"""
from typing import Any, Union

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_thesis.dao.template_dao import UniversalInstructionSystemDao
from module_thesis.entity.vo.instruction_system_vo import (
    UniversalInstructionSystemModel,
    InstructionSystemPageQueryModel,
    InstructionSystemAddModel,
    InstructionSystemUpdateModel,
)
from utils.common_util import CamelCaseUtil


class InstructionSystemService:
    """
    指令系统管理服务类
    """

    @classmethod
    async def get_instruction_system_list(
        cls,
        query_db: AsyncSession,
        query_object: InstructionSystemPageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取指令系统列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 指令系统列表
        """
        query_dict = query_object.model_dump(exclude_none=True)
        
        # 使用DAO方法（需要先实现）
        # 暂时使用直接查询方式
        from sqlalchemy import select, func, and_
        from module_thesis.entity.do.template_do import UniversalInstructionSystem
        
        query = select(UniversalInstructionSystem)
        conditions = []
        
        if query_dict.get('version'):
            conditions.append(UniversalInstructionSystem.version == query_dict['version'])
        
        if query_dict.get('is_active') is not None:
            conditions.append(UniversalInstructionSystem.is_active == query_dict['is_active'])
        
        if query_dict.get('description'):
            conditions.append(UniversalInstructionSystem.description.like(f"%{query_dict['description']}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 按ID倒序排列
        query = query.order_by(UniversalInstructionSystem.id.desc())
        
        if is_page:
            # 分页查询
            page_num = query_dict.get('page_num', 1)
            page_size = query_dict.get('page_size', 10)
            
            # 获取总数
            count_query = select(func.count()).select_from(UniversalInstructionSystem)
            if conditions:
                count_query = count_query.where(and_(*conditions))
            total = (await query_db.execute(count_query)).scalar()
            
            # 分页
            offset = (page_num - 1) * page_size
            query = query.offset(offset).limit(page_size)
            
            # 执行查询
            result = (await query_db.execute(query)).scalars().all()
            
            # 转换为字典列表
            data_list = [CamelCaseUtil.transform_result(item) for item in result]
            
            # 构建分页结果
            from common.vo import PageModel
            import math
            has_next = math.ceil(total / page_size) > page_num
            return PageModel(
                rows=data_list,
                pageNum=page_num,
                pageSize=page_size,
                total=total,
                hasNext=has_next
            )
        else:
            # 不分页
            result = (await query_db.execute(query)).scalars().all()
            return [CamelCaseUtil.transform_result(item) for item in result]

    @classmethod
    async def get_instruction_system_detail(
        cls,
        query_db: AsyncSession,
        system_id: int
    ) -> UniversalInstructionSystemModel:
        """
        获取指令系统详情

        :param query_db: 数据库会话
        :param system_id: 指令系统ID
        :return: 指令系统详情
        """
        system = await UniversalInstructionSystemDao.get_instruction_system_by_id(query_db, system_id)
        if not system:
            raise ServiceException(message='指令系统不存在')
        return UniversalInstructionSystemModel(**CamelCaseUtil.transform_result(system))

    @classmethod
    async def get_active_instruction_system(
        cls,
        query_db: AsyncSession
    ) -> Union[UniversalInstructionSystemModel, None]:
        """
        获取激活的指令系统

        :param query_db: 数据库会话
        :return: 激活的指令系统
        """
        system = await UniversalInstructionSystemDao.get_active_instruction_system(query_db)
        if not system:
            return None
        return UniversalInstructionSystemModel(**CamelCaseUtil.transform_result(system))

    @classmethod
    async def create_instruction_system(
        cls,
        query_db: AsyncSession,
        system_data: InstructionSystemAddModel,
        user_name: str = None
    ) -> CrudResponseModel:
        """
        创建指令系统

        :param query_db: 数据库会话
        :param system_data: 指令系统数据
        :param user_name: 用户名
        :return: 操作结果
        """
        # 检查版本号是否已存在
        existing = await UniversalInstructionSystemDao.get_instruction_system_by_version(
            query_db,
            system_data.version
        )
        if existing:
            raise ServiceException(message=f'版本号 {system_data.version} 已存在')
        
        # 如果设置为激活，先停用其他所有指令系统
        if system_data.is_active == '1':
            await UniversalInstructionSystemDao.deactivate_all(query_db)
        
        # 准备插入数据
        insert_data = system_data.model_dump(exclude_none=True)
        if user_name:
            insert_data['create_by'] = user_name
        
        # 插入数据库
        new_system = await UniversalInstructionSystemDao.add_instruction_system(query_db, insert_data)
        await query_db.commit()
        
        return CrudResponseModel(
            is_success=True,
            message='创建指令系统成功',
            result={'id': new_system.id, 'version': new_system.version}
        )

    @classmethod
    async def update_instruction_system(
        cls,
        query_db: AsyncSession,
        system_id: int,
        system_data: InstructionSystemUpdateModel,
        user_name: str = None
    ) -> CrudResponseModel:
        """
        更新指令系统

        :param query_db: 数据库会话
        :param system_id: 指令系统ID
        :param system_data: 更新的数据
        :param user_name: 用户名
        :return: 操作结果
        """
        # 检查指令系统是否存在
        existing = await UniversalInstructionSystemDao.get_instruction_system_by_id(query_db, system_id)
        if not existing:
            raise ServiceException(message='指令系统不存在')
        
        # 准备更新数据
        update_data = system_data.model_dump(exclude_none=True)
        
        # 检查指令数据是否有变化
        instruction_data_changed = False
        if 'instruction_data' in update_data:
            import json
            existing_data_str = json.dumps(existing.instruction_data, sort_keys=True, ensure_ascii=False) if existing.instruction_data else '{}'
            new_data_str = json.dumps(update_data['instruction_data'], sort_keys=True, ensure_ascii=False)
            instruction_data_changed = existing_data_str != new_data_str
        
        # 处理版本号：如果指令数据有变化但没有提供新版本号，自动递增版本号
        if instruction_data_changed and not system_data.version:
            # 自动递增版本号（例如：1.2 -> 1.3）
            current_version = existing.version
            try:
                # 尝试解析版本号（支持 x.y 格式）
                version_parts = current_version.split('.')
                if len(version_parts) == 2:
                    major = int(version_parts[0])
                    minor = int(version_parts[1])
                    new_version = f"{major}.{minor + 1}"
                else:
                    # 如果格式不符合，使用时间戳作为版本号
                    from datetime import datetime
                    new_version = datetime.now().strftime("%Y%m%d.%H%M%S")
            except (ValueError, IndexError):
                # 如果版本号格式无法解析，使用时间戳
                from datetime import datetime
                new_version = datetime.now().strftime("%Y%m%d.%H%M%S")
            
            # 检查新版本号是否已存在
            version_exists = await UniversalInstructionSystemDao.get_instruction_system_by_version(
                query_db,
                new_version
            )
            if version_exists:
                # 如果新版本号已存在，继续递增
                version_parts = new_version.split('.')
                if len(version_parts) == 2:
                    major = int(version_parts[0])
                    minor = int(version_parts[1])
                    new_version = f"{major}.{minor + 1}"
            
            update_data['version'] = new_version
            # 同时更新描述，添加版本更新说明
            if 'description' not in update_data or not update_data.get('description'):
                update_data['description'] = existing.description or ''
            if '自动版本更新' not in update_data['description']:
                update_data['description'] += f"（自动版本更新：{current_version} -> {new_version}）"
        
        # 如果用户提供了新版本号，检查新版本号是否已存在
        elif system_data.version and system_data.version != existing.version:
            version_exists = await UniversalInstructionSystemDao.get_instruction_system_by_version(
                query_db,
                system_data.version
            )
            if version_exists:
                raise ServiceException(message=f'版本号 {system_data.version} 已存在')
        
        # 如果设置为激活，先停用其他所有指令系统
        if system_data.is_active == '1':
            await UniversalInstructionSystemDao.deactivate_all(query_db)
        
        # 如果模型中没有设置update_by，使用传入的user_name
        if user_name and 'update_by' not in update_data:
            update_data['update_by'] = user_name
        # 如果模型中没有设置update_time，使用当前时间
        if 'update_time' not in update_data:
            from datetime import datetime
            update_data['update_time'] = datetime.now()
        
        # 更新数据库
        await UniversalInstructionSystemDao.update_instruction_system(query_db, system_id, update_data)
        await query_db.commit()
        
        return CrudResponseModel(is_success=True, message='更新指令系统成功')

    @classmethod
    async def delete_instruction_system(
        cls,
        query_db: AsyncSession,
        system_id: int
    ) -> CrudResponseModel:
        """
        删除指令系统

        :param query_db: 数据库会话
        :param system_id: 指令系统ID
        :return: 操作结果
        """
        # 检查指令系统是否存在
        existing = await UniversalInstructionSystemDao.get_instruction_system_by_id(query_db, system_id)
        if not existing:
            raise ServiceException(message='指令系统不存在')
        
        # 检查是否是激活的指令系统
        if existing.is_active == '1':
            raise ServiceException(message='不能删除激活的指令系统，请先停用')
        
        # 删除
        await UniversalInstructionSystemDao.delete_instruction_system(query_db, system_id)
        await query_db.commit()
        
        return CrudResponseModel(is_success=True, message='删除指令系统成功')

    @classmethod
    async def activate_instruction_system(
        cls,
        query_db: AsyncSession,
        system_id: int,
        user_name: str = None
    ) -> CrudResponseModel:
        """
        激活指令系统

        :param query_db: 数据库会话
        :param system_id: 指令系统ID
        :param user_name: 用户名
        :return: 操作结果
        """
        # 检查指令系统是否存在
        existing = await UniversalInstructionSystemDao.get_instruction_system_by_id(query_db, system_id)
        if not existing:
            raise ServiceException(message='指令系统不存在')
        
        # 先停用其他所有指令系统
        await UniversalInstructionSystemDao.deactivate_all(query_db)
        
        # 激活当前指令系统
        update_data = {'is_active': '1'}
        if user_name:
            update_data['update_by'] = user_name
        
        await UniversalInstructionSystemDao.update_instruction_system(query_db, system_id, update_data)
        await query_db.commit()
        
        return CrudResponseModel(is_success=True, message='激活指令系统成功')
