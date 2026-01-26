"""
订单和支付管理服务层
"""
from typing import Any, Union
from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_thesis.dao import OrderDao, FeatureServiceDao, ExportRecordDao
from module_thesis.entity.vo import (
    OrderModel,
    FeatureServiceModel,
    ExportRecordModel,
    OrderPageQueryModel,
    FeatureServicePageQueryModel,
    ExportRecordPageQueryModel,
    DeductQuotaModel,
)
from module_thesis.service.member_service import MemberService
from utils.common_util import CamelCaseUtil


class OrderService:
    """
    订单管理服务类
    """

    # ==================== 订单管理 ====================

    @classmethod
    def _generate_order_no(cls) -> str:
        """
        生成订单号

        :return: 订单号
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = str(uuid.uuid4().hex)[:6].upper()
        return f'ORD{timestamp}{random_str}'

    @classmethod
    async def create_order(
        cls,
        query_db: AsyncSession,
        user_id: int,
        order_type: str,
        item_id: int,
        amount: Decimal,
        payment_method: str = 'wechat'
    ) -> CrudResponseModel:
        """
        创建订单

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param order_type: 订单类型（package-套餐, service-服务）
        :param item_id: 商品ID（套餐ID或服务ID）
        :param amount: 订单金额
        :param payment_method: 支付方式
        :return: 操作结果
        """
        try:
            # 生成订单号
            order_no = cls._generate_order_no()
            
            # 计算过期时间（30分钟后）
            from datetime import datetime, timedelta
            expired_at = datetime.now() + timedelta(minutes=30)
            
            # 创建订单对象
            order_data = {
                'order_no': order_no,
                'user_id': user_id,
                'order_type': order_type,
                'item_id': item_id,
                'package_id': item_id if order_type == 'package' else None,  # 兼容字段
                'amount': amount,
                'payment_method': payment_method,
                'status': 'pending',
                'expired_at': expired_at,
            }
            
            new_order = await OrderDao.add_order(query_db, order_data)
            
            # 在 commit 之前提取数据（避免异步上下文错误）
            order_id = new_order.order_id
            order_no_result = new_order.order_no
            order_amount = float(new_order.amount)
            
            await query_db.commit()
            
            return CrudResponseModel(
                is_success=True,
                message='订单创建成功',
                result={
                    'order_id': order_id,
                    'order_no': order_no_result,
                    'amount': order_amount
                }
            )
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'订单创建失败: {str(e)}')

    @classmethod
    async def get_order_detail(cls, query_db: AsyncSession, order_id: int) -> OrderModel:
        """
        获取订单详情

        :param query_db: 数据库会话
        :param order_id: 订单ID
        :return: 订单详情
        """
        order = await OrderDao.get_order_by_id(query_db, order_id)
        if not order:
            raise ServiceException(message='订单不存在')
        return OrderModel(**CamelCaseUtil.transform_result(order))

    @classmethod
    async def get_order_by_order_no(cls, query_db: AsyncSession, order_no: str) -> OrderModel:
        """
        根据订单号获取订单

        :param query_db: 数据库会话
        :param order_no: 订单号
        :return: 订单详情
        """
        order = await OrderDao.get_order_by_order_no(query_db, order_no)
        if not order:
            raise ServiceException(message='订单不存在')
        return OrderModel(**CamelCaseUtil.transform_result(order))

    @classmethod
    async def get_order_list(
        cls,
        query_db: AsyncSession,
        query_object: OrderPageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取订单列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 订单列表
        """
        return await OrderDao.get_order_list(
            query_db,
            user_id=query_object.user_id,
            status=query_object.status,
            page_num=query_object.page_num or 1,
            page_size=query_object.page_size or 10,
            is_page=is_page
        )

    @classmethod
    async def cancel_order(cls, query_db: AsyncSession, order_id: int, user_id: int) -> CrudResponseModel:
        """
        取消订单

        :param query_db: 数据库会话
        :param order_id: 订单ID
        :param user_id: 用户ID
        :return: 操作结果
        """
        # 获取订单详情
        order = await cls.get_order_detail(query_db, order_id)
        
        # 验证订单所有权
        if order.user_id != user_id:
            raise ServiceException(message='无权操作此订单')
        
        # 只有待支付的订单可以取消
        if order.status != 'pending':
            raise ServiceException(message='只有待支付的订单可以取消')

        try:
            await OrderDao.update_order_status(query_db, order_id, 'cancelled')
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='订单已取消')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'取消订单失败: {str(e)}')

    # ==================== 支付处理 ====================

    @classmethod
    async def process_payment(
        cls,
        query_db: AsyncSession,
        order_no: str,
        transaction_id: str,
        payment_time: datetime = None
    ) -> CrudResponseModel:
        """
        处理支付（支付回调）

        :param query_db: 数据库会话
        :param order_no: 订单号
        :param transaction_id: 第三方交易号
        :param payment_time: 支付时间
        :return: 操作结果
        """
        # 直接从 DAO 获取订单对象（不是 Pydantic 模型）
        order = await OrderDao.get_order_by_order_no(query_db, order_no)
        
        if not order:
            raise ServiceException(message='订单不存在')
        
        # 检查订单状态
        if order.status == 'paid':
            return CrudResponseModel(is_success=True, message='订单已支付')
        
        if order.status != 'pending':
            raise ServiceException(message='订单状态异常，无法支付')

        try:
            # 更新订单状态
            await OrderDao.update_order_status(
                query_db,
                order.order_id,
                'paid',
                payment_time or datetime.now(),
                transaction_id
            )
            
            # 根据订单类型处理业务逻辑
            if order.order_type == 'package':
                # 激活会员套餐
                await MemberService.activate_membership(
                    query_db,
                    order.user_id,
                    order.item_id,
                    auto_commit=False
                )
            elif order.order_type == 'service':
                # 处理单次服务购买
                service = await FeatureServiceDao.get_service_by_id(query_db, order.item_id)
                if service:
                    # 根据服务类型增加对应配额
                    # 这里需要根据实际业务逻辑处理
                    # 例如：增加字数配额、使用次数等
                    pass
            
            # 统一提交事务
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='支付成功')
        except ServiceException as e:
            await query_db.rollback()
            raise e
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'支付处理失败: {str(e)}')

    @classmethod
    async def process_refund(
        cls,
        query_db: AsyncSession,
        order_id: int,
        refund_reason: str = None
    ) -> CrudResponseModel:
        """
        处理退款

        :param query_db: 数据库会话
        :param order_id: 订单ID
        :param refund_reason: 退款原因
        :return: 操作结果
        """
        # 获取订单详情
        order = await cls.get_order_detail(query_db, order_id)
        
        # 只有已支付的订单可以退款
        if order.status != 'paid':
            raise ServiceException(message='只有已支付的订单可以退款')

        try:
            # 更新订单状态
            update_data = {
                'order_id': order_id,
                'status': 'refunded',
                'refund_time': datetime.now(),
                'refund_reason': refund_reason,
                'update_time': datetime.now()
            }
            await OrderDao.update_order(query_db, update_data)
            
            # 这里可以添加实际的退款逻辑（调用支付平台API）
            
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='退款成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'退款处理失败: {str(e)}')

    @classmethod
    async def get_order_statistics(
        cls,
        query_db: AsyncSession,
        user_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> dict:
        """
        获取订单统计

        :param query_db: 数据库会话
        :param user_id: 用户ID（可选）
        :param start_date: 开始日期（可选）
        :param end_date: 结束日期（可选）
        :return: 统计信息
        """
        return await OrderDao.get_order_statistics(query_db, user_id, start_date, end_date)

    # ==================== 功能服务管理 ====================

    @classmethod
    async def get_service_list(
        cls,
        query_db: AsyncSession,
        query_object: FeatureServicePageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取功能服务列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 服务列表
        """
        return await FeatureServiceDao.get_service_list(
            query_db,
            status=query_object.status,
            page_num=query_object.page_num or 1,
            page_size=query_object.page_size or 10,
            is_page=is_page
        )

    @classmethod
    async def get_service_detail(cls, query_db: AsyncSession, service_id: int) -> FeatureServiceModel:
        """
        获取服务详情

        :param query_db: 数据库会话
        :param service_id: 服务ID
        :return: 服务详情
        """
        service = await FeatureServiceDao.get_service_by_id(query_db, service_id)
        if not service:
            raise ServiceException(message='服务不存在')
        return FeatureServiceModel(**CamelCaseUtil.transform_result(service))

    @classmethod
    async def create_service(
        cls,
        query_db: AsyncSession,
        service_data: FeatureServiceModel
    ) -> CrudResponseModel:
        """
        创建功能服务

        :param query_db: 数据库会话
        :param service_data: 服务数据
        :return: 操作结果
        """
        try:
            service_dict = service_data.model_dump(exclude_none=True)
            service_dict['status'] = '0'  # 启用
            new_service = await FeatureServiceDao.add_service(query_db, service_dict)
            
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='服务创建成功',
                result={'service_id': new_service.service_id}
            )
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'服务创建失败: {str(e)}')

    @classmethod
    async def update_service(
        cls,
        query_db: AsyncSession,
        service_data: FeatureServiceModel
    ) -> CrudResponseModel:
        """
        更新功能服务

        :param query_db: 数据库会话
        :param service_data: 服务数据
        :return: 操作结果
        """
        # 检查服务是否存在
        await cls.get_service_detail(query_db, service_data.service_id)

        try:
            update_data = service_data.model_dump(exclude_unset=True)
            update_data['update_time'] = datetime.now()
            await FeatureServiceDao.update_service(query_db, update_data)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='服务更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'服务更新失败: {str(e)}')

    @classmethod
    async def delete_service(cls, query_db: AsyncSession, service_id: int) -> CrudResponseModel:
        """
        删除功能服务

        :param query_db: 数据库会话
        :param service_id: 服务ID
        :return: 操作结果
        """
        # 检查服务是否存在
        await cls.get_service_detail(query_db, service_id)

        try:
            await FeatureServiceDao.delete_service(query_db, service_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='服务删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'服务删除失败: {str(e)}')

    # ==================== 导出记录管理 ====================

    @classmethod
    async def create_export_record(
        cls,
        query_db: AsyncSession,
        user_id: int,
        thesis_id: int,
        export_format: str,
        file_path: str,
        file_size: int
    ) -> CrudResponseModel:
        """
        创建导出记录（需要扣减配额）

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param thesis_id: 论文ID
        :param export_format: 导出格式
        :param file_path: 文件路径
        :param file_size: 文件大小
        :return: 操作结果
        """
        try:
            # 先检查配额是否充足（不扣减）
            if not await MemberService.check_quota(query_db, user_id, 'export', 1):
                raise ServiceException(message='导出配额不足')

            # 创建导出记录
            record_data = {
                'user_id': user_id,
                'thesis_id': thesis_id,
                'export_format': export_format,
                'file_path': file_path,
                'file_size': file_size,
            }
            new_record = await ExportRecordDao.add_record(query_db, record_data)
            
            # 扣减配额（导出消耗1次导出配额，不自动提交）
            deduct_data = DeductQuotaModel(
                user_id=user_id,
                feature_type='export',
                amount=1,
                business_type='thesis_export',
                business_id=thesis_id
            )
            await MemberService.deduct_quota(query_db, deduct_data, auto_commit=False)

            # 统一提交事务
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='导出成功',
                result={'record_id': new_record.record_id}
            )
        except ServiceException as e:
            await query_db.rollback()
            raise e
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'导出失败: {str(e)}')

    @classmethod
    async def get_export_record_list(
        cls,
        query_db: AsyncSession,
        query_object: ExportRecordPageQueryModel,
        is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取导出记录列表

        :param query_db: 数据库会话
        :param query_object: 查询参数
        :param is_page: 是否分页
        :return: 记录列表
        """
        return await ExportRecordDao.get_record_list(
            query_db,
            user_id=query_object.user_id,
            thesis_id=query_object.thesis_id,
            page_num=query_object.page_num or 1,
            page_size=query_object.page_size or 10,
            is_page=is_page
        )

    @classmethod
    async def get_export_record_detail(cls, query_db: AsyncSession, record_id: int) -> ExportRecordModel:
        """
        获取导出记录详情

        :param query_db: 数据库会话
        :param record_id: 记录ID
        :return: 记录详情
        """
        record = await ExportRecordDao.get_record_by_id(query_db, record_id)
        if not record:
            raise ServiceException(message='导出记录不存在')
        return ExportRecordModel(**CamelCaseUtil.transform_result(record))

    @classmethod
    async def delete_export_record(cls, query_db: AsyncSession, record_id: int) -> CrudResponseModel:
        """
        删除导出记录

        :param query_db: 数据库会话
        :param record_id: 记录ID
        :return: 操作结果
        """
        # 检查记录是否存在
        await cls.get_export_record_detail(query_db, record_id)

        try:
            await ExportRecordDao.delete_record(query_db, record_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='记录删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'记录删除失败: {str(e)}')

    @classmethod
    async def get_user_export_count(
        cls,
        query_db: AsyncSession,
        user_id: int,
        thesis_id: int = None
    ) -> int:
        """
        获取用户导出次数

        :param query_db: 数据库会话
        :param user_id: 用户ID
        :param thesis_id: 论文ID（可选）
        :return: 导出次数
        """
        return await ExportRecordDao.get_user_export_count(query_db, user_id, thesis_id)
