"""
统一支付控制器
"""
from typing import Annotated
from decimal import Decimal
from datetime import datetime
from fastapi import Request, Query, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import DataResponseModel
from common.router import APIRouter
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_thesis.service.payment_gateway_service import PaymentGatewayService
from module_thesis.service.order_service import OrderService
from exceptions.exception import ServiceException
from utils.response_util import ResponseUtil
from utils.log_util import logger


payment_controller = APIRouter(prefix='/thesis/payment', tags=['论文系统-支付管理'])


@payment_controller.get(
    '/channels',
    summary='获取可用支付渠道',
    description='获取所有可用的支付渠道列表',
    response_model=DataResponseModel
)
async def get_available_channels(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    """获取可用支付渠道"""
    channels = await PaymentGatewayService.get_available_channels(query_db)
    return ResponseUtil.success(data=channels)


@payment_controller.post(
    '/create',
    summary='创建支付',
    description='创建支付订单（统一入口）',
    response_model=DataResponseModel
)
async def create_payment(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    order_id: Annotated[int, Query(description='订单ID')],
    channel: Annotated[str, Query(description='支付渠道')],
    provider: Annotated[str | None, Query(description='指定支付提供商')] = None,
):
    """创建支付（加锁防并发）"""
    from sqlalchemy import select
    from module_thesis.entity.do.order_do import AiWriteOrder
    
    # 使用行锁查询订单（防止并发创建支付）
    result = await query_db.execute(
        select(AiWriteOrder)
        .where(AiWriteOrder.order_id == order_id)
        .with_for_update()  # 行锁，防止并发
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise ServiceException(message='订单不存在')
    
    # 验证订单所有权
    if order.user_id != current_user.user.user_id:
        raise ServiceException(message='无权操作此订单')
    
    # 验证订单状态
    if order.status != 'pending':
        raise ServiceException(message='订单状态异常，无法支付')
    
    # 获取客户端IP
    client_ip = request.client.host
    
    # 创建支付
    result = await PaymentGatewayService.create_payment(
        query_db,
        order_id=order.order_id,
        order_no=order.order_no,
        amount=order.amount,
        channel=channel,
        subject=f'购买{order.order_type}',
        body=f'订单号：{order.order_no}',
        provider_type=provider,
        client_ip=client_ip
    )
    
    logger.info(f'创建支付成功: {order.order_no}, 渠道: {channel}, 提供商: {result.get("provider")}')
    return ResponseUtil.success(data=result)


@payment_controller.get(
    '/query',
    summary='查询支付',
    description='查询支付状态',
    response_model=DataResponseModel
)
async def query_payment(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    payment_id: Annotated[str, Query(description='支付ID')],
    provider: Annotated[str, Query(description='支付提供商')],
):
    """查询支付"""
    result = await PaymentGatewayService.query_payment(query_db, payment_id, provider)
    return ResponseUtil.success(data=result)


@payment_controller.post(
    '/refund',
    summary='创建退款',
    description='创建退款申请',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:payment:refund')]
)
async def create_refund(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    payment_id: Annotated[str, Query(description='支付ID')],
    provider: Annotated[str, Query(description='支付提供商')],
    amount: Annotated[float | None, Query(description='退款金额')] = None,
    reason: Annotated[str, Query(description='退款原因')] = '',
):
    """创建退款"""
    refund_amount = Decimal(str(amount)) if amount else None
    result = await PaymentGatewayService.create_refund(
        query_db,
        payment_id,
        provider,
        refund_amount,
        reason
    )
    
    logger.info(f'创建退款成功: {payment_id}, 金额: {amount}')
    return ResponseUtil.success(data=result)


# ==================== Webhook回调 ====================

@payment_controller.post(
    '/webhook/pingpp',
    summary='Ping++支付回调',
    description='Ping++支付提供商回调接口',
    include_in_schema=False
)
async def pingpp_webhook(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    """Ping++支付回调"""
    try:
        # 获取原始数据
        raw_data = await request.body()
        signature = request.headers.get('x-pingplusplus-signature')
        
        # 获取提供商实例
        provider, _ = await PaymentGatewayService.get_provider(query_db, 'pingpp')
        
        # 验证签名
        if not provider.verify_webhook(raw_data.decode('utf-8'), signature):
            return {'status': 'fail', 'message': '签名验证失败'}
        
        # 解析数据
        import json
        event = json.loads(raw_data.decode('utf-8'))
        
        if event['type'] == 'charge.succeeded':
            charge = event['data']['object']
            order_no = charge['order_no']
            transaction_no = charge['transaction_no']
            
            # 处理支付
            await OrderService.process_payment(query_db, order_no, transaction_no)
            
            logger.info(f'Ping++支付回调成功: order_no={order_no}')
        
        return {'status': 'success'}
    except Exception as e:
        logger.error(f'Ping++支付回调处理失败: {str(e)}')
        return {'status': 'fail', 'message': str(e)}


@payment_controller.post(
    '/webhook/alipay',
    summary='支付宝支付回调',
    description='支付宝支付提供商回调接口',
    include_in_schema=False
)
async def alipay_webhook(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    """支付宝支付回调"""
    try:
        form_data = await request.form()
        params = dict(form_data)
        
        # 获取提供商实例
        provider, _ = await PaymentGatewayService.get_provider(query_db, 'alipay')
        
        # 验证签名
        if not provider.verify_webhook(params):
            return 'fail'
        
        # 处理支付
        order_no = params.get('out_trade_no')
        trade_status = params.get('trade_status')
        trade_no = params.get('trade_no')
        
        if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
            await OrderService.process_payment(query_db, order_no, trade_no)
            logger.info(f'支付宝支付回调成功: order_no={order_no}')
        
        return 'success'
    except Exception as e:
        logger.error(f'支付宝支付回调处理失败: {str(e)}')
        return 'fail'


@payment_controller.post(
    '/webhook/wechat',
    summary='微信支付回调',
    description='微信支付提供商回调接口',
    include_in_schema=False
)
async def wechat_webhook(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    """微信支付回调"""
    try:
        headers = dict(request.headers)
        body = await request.body()
        
        # 获取提供商实例
        provider, _ = await PaymentGatewayService.get_provider(query_db, 'wechat')
        
        # 验证签名并解密
        webhook_data = {'headers': headers, 'body': body.decode('utf-8')}
        if not provider.verify_webhook(webhook_data):
            return {'code': 'FAIL', 'message': '签名验证失败'}
        
        # 解析数据
        import json
        data = json.loads(body.decode('utf-8'))
        
        # 处理支付
        order_no = data.get('out_trade_no')
        trade_state = data.get('trade_state')
        transaction_id = data.get('transaction_id')
        
        if trade_state == 'SUCCESS':
            await OrderService.process_payment(query_db, order_no, transaction_id)
            logger.info(f'微信支付回调成功: order_no={order_no}')
        
        return {'code': 'SUCCESS', 'message': '成功'}
    except Exception as e:
        logger.error(f'微信支付回调处理失败: {str(e)}')
        return {'code': 'FAIL', 'message': str(e)}


# ==================== 配置管理 ====================

@payment_controller.get(
    '/configs',
    summary='获取支付配置',
    description='获取所有支付配置列表（仅管理员）',
    response_model=DataResponseModel
)
async def get_payment_configs(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
):
    """获取支付配置（仅管理员）"""
    # 检查是否为管理员
    if not current_user.user.admin:
        raise ServiceException(message='仅管理员可以访问支付配置')
    
    configs = await PaymentGatewayService.get_payment_configs(query_db)
    return ResponseUtil.success(data=configs)


@payment_controller.put(
    '/config/status',
    summary='更新配置状态',
    description='启用或禁用支付配置（仅管理员）',
    response_model=DataResponseModel
)
async def update_config_status(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    config_id: Annotated[int, Query(description='配置ID')],
    is_enabled: Annotated[str, Query(description='是否启用（0否 1是）')],
):
    """更新配置状态（仅管理员）"""
    # 检查是否为管理员
    if not current_user.user.admin:
        raise ServiceException(message='仅管理员可以修改支付配置')
    
    await PaymentGatewayService.update_config_status(query_db, config_id, is_enabled)
    return ResponseUtil.success(message='配置状态更新成功')



# ==================== 交易记录管理 ====================

@payment_controller.get(
    '/transactions',
    summary='获取交易记录列表',
    description='获取交易记录分页列表',
    response_model=DataResponseModel
)
async def get_transaction_list(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    transaction_no: Annotated[str | None, Query(description='交易流水号')] = None,
    order_no: Annotated[str | None, Query(description='订单号')] = None,
    channel: Annotated[str | None, Query(description='支付渠道')] = None,
    status: Annotated[str | None, Query(description='交易状态')] = None,
    start_time: Annotated[str | None, Query(description='开始时间')] = None,
    end_time: Annotated[str | None, Query(description='结束时间')] = None,
    page_num: Annotated[int, Query(description='页码', ge=1)] = 1,
    page_size: Annotated[int, Query(description='每页数量', ge=1, le=100)] = 10,
):
    """获取交易记录列表"""
    from sqlalchemy import select, and_
    from module_thesis.entity.do.payment_transaction_do import PaymentTransaction
    
    # 构建查询条件
    conditions = []
    if transaction_no:
        conditions.append(PaymentTransaction.transaction_no.like(f'%{transaction_no}%'))
    if order_no:
        conditions.append(PaymentTransaction.order_no.like(f'%{order_no}%'))
    if channel:
        conditions.append(PaymentTransaction.channel == channel)
    if status:
        conditions.append(PaymentTransaction.status == status)
    if start_time:
        conditions.append(PaymentTransaction.create_time >= start_time)
    if end_time:
        conditions.append(PaymentTransaction.create_time <= end_time)
    
    # 普通用户只能查看自己的交易
    if not current_user.user.admin:
        # 需要关联订单表获取user_id
        from module_thesis.entity.do.order_do import AiWriteOrder
        stmt = (
            select(PaymentTransaction)
            .join(AiWriteOrder, PaymentTransaction.order_no == AiWriteOrder.order_no)
            .where(AiWriteOrder.user_id == current_user.user.user_id)
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))
    else:
        stmt = select(PaymentTransaction)
        if conditions:
            stmt = stmt.where(and_(*conditions))
    
    # 分页
    stmt = stmt.offset((page_num - 1) * page_size).limit(page_size)
    stmt = stmt.order_by(PaymentTransaction.create_time.desc())
    
    result = await query_db.execute(stmt)
    transactions = result.scalars().all()
    
    # 获取总数
    from sqlalchemy import func
    count_stmt = select(func.count(PaymentTransaction.transaction_id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total_result = await query_db.execute(count_stmt)
    total = total_result.scalar()
    
    return ResponseUtil.success(data={
        'rows': [t.__dict__ for t in transactions],
        'total': total
    })


@payment_controller.get(
    '/transaction/{transaction_id}',
    summary='获取交易详情',
    description='获取指定交易的详细信息',
    response_model=DataResponseModel
)
async def get_transaction_detail(
    request: Request,
    transaction_id: Annotated[int, Path(description='交易ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    """获取交易详情"""
    from sqlalchemy import select
    from module_thesis.entity.do.payment_transaction_do import PaymentTransaction
    
    stmt = select(PaymentTransaction).where(PaymentTransaction.transaction_id == transaction_id)
    result = await query_db.execute(stmt)
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        return ResponseUtil.error(msg='交易记录不存在')
    
    return ResponseUtil.success(data=transaction.__dict__)


@payment_controller.post(
    '/transaction/{transaction_id}/sync',
    summary='同步交易状态',
    description='从支付平台同步交易状态',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:transaction:sync')]
)
async def sync_transaction_status(
    request: Request,
    transaction_id: Annotated[int, Path(description='交易ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    """同步交易状态"""
    from sqlalchemy import select
    from module_thesis.entity.do.payment_transaction_do import PaymentTransaction
    
    # 获取交易记录
    stmt = select(PaymentTransaction).where(PaymentTransaction.transaction_id == transaction_id)
    result = await query_db.execute(stmt)
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        return ResponseUtil.error(msg='交易记录不存在')
    
    # 查询支付状态
    try:
        payment_result = await PaymentGatewayService.query_payment(
            query_db,
            transaction.third_party_no,
            transaction.provider
        )
        
        # 更新交易状态
        if payment_result.get('status') == 'success':
            transaction.status = 'success'
            transaction.completed_time = datetime.now()
        elif payment_result.get('status') == 'failed':
            transaction.status = 'failed'
        
        await query_db.commit()
        
        logger.info(f'同步交易状态成功: {transaction.transaction_no}')
        return ResponseUtil.success(msg='同步成功', data=transaction.__dict__)
    except Exception as e:
        logger.error(f'同步交易状态失败: {str(e)}')
        return ResponseUtil.error(msg=f'同步失败: {str(e)}')


@payment_controller.get(
    '/transaction/stats',
    summary='获取交易统计',
    description='获取交易统计信息',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('thesis:transaction:query')]
)
async def get_transaction_stats(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    start_time: Annotated[str | None, Query(description='开始时间')] = None,
    end_time: Annotated[str | None, Query(description='结束时间')] = None,
):
    """获取交易统计"""
    from sqlalchemy import select, func, and_
    from module_thesis.entity.do.payment_transaction_do import PaymentTransaction
    from decimal import Decimal
    
    # 构建查询条件
    conditions = []
    if start_time:
        conditions.append(PaymentTransaction.create_time >= start_time)
    if end_time:
        conditions.append(PaymentTransaction.create_time <= end_time)
    
    # 总交易额
    total_stmt = select(func.sum(PaymentTransaction.amount))
    if conditions:
        total_stmt = total_stmt.where(and_(*conditions))
    total_result = await query_db.execute(total_stmt)
    total_amount = total_result.scalar() or Decimal('0')
    
    # 成功交易额
    success_stmt = select(func.sum(PaymentTransaction.amount)).where(
        PaymentTransaction.status == 'success'
    )
    if conditions:
        success_stmt = success_stmt.where(and_(*conditions))
    success_result = await query_db.execute(success_stmt)
    success_amount = success_result.scalar() or Decimal('0')
    
    # 处理中交易额
    pending_stmt = select(func.sum(PaymentTransaction.amount)).where(
        PaymentTransaction.status == 'pending'
    )
    if conditions:
        pending_stmt = pending_stmt.where(and_(*conditions))
    pending_result = await query_db.execute(pending_stmt)
    pending_amount = pending_result.scalar() or Decimal('0')
    
    # 总手续费
    fee_stmt = select(func.sum(PaymentTransaction.fee))
    if conditions:
        fee_stmt = fee_stmt.where(and_(*conditions))
    fee_result = await query_db.execute(fee_stmt)
    total_fee = fee_result.scalar() or Decimal('0')
    
    return ResponseUtil.success(data={
        'total': float(total_amount),
        'success': float(success_amount),
        'pending': float(pending_amount),
        'fee': float(total_fee)
    })


@payment_controller.post(
    '/test',
    summary='测试支付',
    description='创建测试支付订单（仅管理员）',
    response_model=DataResponseModel
)
async def test_payment(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    channel: Annotated[str, Query(description='支付渠道')],
    amount: Annotated[float, Query(description='测试金额', ge=0.01)],
    subject: Annotated[str, Query(description='订单描述')] = '测试订单',
):
    """测试支付（仅管理员）"""
    # 检查是否为管理员
    if not current_user.user.admin:
        raise ServiceException(message='仅管理员可以测试支付')
    
    from decimal import Decimal
    import uuid
    
    # 生成测试订单号
    test_order_no = f'TEST{datetime.now().strftime("%Y%m%d%H%M%S")}{uuid.uuid4().hex[:6].upper()}'
    
    # 获取客户端IP
    client_ip = request.client.host
    
    try:
        # 创建支付
        result = await PaymentGatewayService.create_payment(
            query_db,
            order_id=0,  # 测试订单ID为0
            order_no=test_order_no,
            amount=Decimal(str(amount)),
            channel=channel,
            subject=subject,
            body='这是一个测试支付订单',
            provider_type=None,
            client_ip=client_ip
        )
        
        logger.info(f'创建测试支付成功: {test_order_no}')
        return ResponseUtil.success(data=result)
    except Exception as e:
        logger.error(f'创建测试支付失败: {str(e)}')
        return ResponseUtil.error(msg=f'创建失败: {str(e)}')


@payment_controller.post(
    '/mock',
    summary='模拟支付',
    description='模拟支付成功（开发调试用，仅管理员）',
    response_model=DataResponseModel
)
async def mock_payment(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    order_id: Annotated[int, Query(description='订单ID')],
):
    """模拟支付成功（开发调试用）"""
    # 检查是否为管理员
    if not current_user.user.admin:
        raise ServiceException(message='仅管理员可以使用模拟支付')
    
    from sqlalchemy import select
    from module_thesis.entity.do.order_do import AiWriteOrder
    import uuid
    
    try:
        # 查询订单
        result = await query_db.execute(
            select(AiWriteOrder).where(AiWriteOrder.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            return ResponseUtil.error(msg='订单不存在')
        
        if order.status != 'pending':
            return ResponseUtil.error(msg=f'订单状态异常：{order.status}，只能支付待支付订单')
        
        # 生成模拟交易号
        mock_transaction_no = f'MOCK{datetime.now().strftime("%Y%m%d%H%M%S")}{uuid.uuid4().hex[:8].upper()}'
        
        # 直接调用订单服务处理支付
        await OrderService.process_payment(query_db, order.order_no, mock_transaction_no)
        
        logger.info(f'模拟支付成功: order_no={order.order_no}, transaction_no={mock_transaction_no}')
        
        return ResponseUtil.success(data={
            'order_no': order.order_no,
            'transaction_no': mock_transaction_no,
            'amount': float(order.amount),
            'status': 'success',
            'message': '模拟支付成功'
        }, msg='模拟支付成功')
        
    except Exception as e:
        logger.error(f'模拟支付失败: {str(e)}')
        await query_db.rollback()
        return ResponseUtil.error(msg=f'模拟支付失败: {str(e)}')


@payment_controller.post(
    '/mock-callback',
    summary='模拟支付回调',
    description='模拟支付平台的异步回调通知（开发调试用，仅管理员）',
    response_model=DataResponseModel
)
async def mock_payment_callback(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    order_no: Annotated[str, Query(description='订单号')],
):
    """模拟支付回调（开发调试用）"""
    # 检查是否为管理员
    if not current_user.user.admin:
        raise ServiceException(message='仅管理员可以使用模拟支付回调')
    
    from sqlalchemy import select
    from module_thesis.entity.do.order_do import AiWriteOrder
    import uuid
    
    try:
        # 查询订单
        result = await query_db.execute(
            select(AiWriteOrder).where(AiWriteOrder.order_no == order_no)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            return ResponseUtil.error(msg='订单不存在')
        
        if order.status != 'pending':
            return ResponseUtil.error(msg=f'订单状态异常：{order.status}，只能回调待支付订单')
        
        # 生成模拟交易号
        mock_transaction_no = f'MOCK_CB_{datetime.now().strftime("%Y%m%d%H%M%S")}_{uuid.uuid4().hex[:8].upper()}'
        
        # 调用支付回调处理（模拟真实支付平台的回调）
        await OrderService.process_payment(query_db, order_no, mock_transaction_no)
        
        logger.info(f'模拟支付回调成功: order_no={order_no}, transaction_no={mock_transaction_no}')
        
        return ResponseUtil.success(data={
            'order_no': order_no,
            'transaction_no': mock_transaction_no,
            'callback_time': datetime.now().isoformat(),
            'status': 'success',
            'message': '模拟支付回调成功'
        }, msg='模拟支付回调成功')
        
    except Exception as e:
        logger.error(f'模拟支付回调失败: {str(e)}')
        await query_db.rollback()
        return ResponseUtil.error(msg=f'模拟支付回调失败: {str(e)}')


@payment_controller.get(
    '/config/{channel}',
    summary='获取支付配置详情',
    description='获取指定渠道的支付配置（仅管理员）',
    response_model=DataResponseModel
)
async def get_payment_config_detail(
    request: Request,
    channel: Annotated[str, Path(description='支付渠道')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
):
    """获取支付配置详情（仅管理员）"""
    # 检查是否为管理员
    if not current_user.user.admin:
        raise ServiceException(message='仅管理员可以访问支付配置')
    
    from sqlalchemy import select
    from module_thesis.entity.do.payment_do import PaymentConfig
    
    stmt = select(PaymentConfig).where(
        PaymentConfig.provider_type == channel,
        PaymentConfig.del_flag == '0'
    )
    result = await query_db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        return ResponseUtil.error(msg='支付配置不存在')
    
    # 隐藏敏感信息
    config_dict = config.__dict__.copy()
    if 'config_data' in config_dict and config_dict['config_data']:
        # 隐藏 config_data 中的敏感信息
        import json
        config_data = config_dict['config_data']
        if isinstance(config_data, str):
            config_data = json.loads(config_data)
        # 隐藏敏感字段
        for key in ['api_key', 'private_key', 'api_v3_key', 'alipay_public_key']:
            if key in config_data:
                config_data[key] = '***' if config_data[key] else ''
        config_dict['config_data'] = config_data
    
    return ResponseUtil.success(data=config_dict)


@payment_controller.put(
    '/config',
    summary='更新支付配置',
    description='更新支付配置信息（仅管理员）',
    response_model=DataResponseModel
)
async def update_payment_config(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    config_data: Annotated[dict, Body(description='配置数据')],
):
    """更新支付配置（仅管理员）"""
    # 检查是否为管理员
    if not current_user.user.admin:
        raise ServiceException(message='仅管理员可以修改支付配置')
    
    from sqlalchemy import select
    from module_thesis.entity.do.payment_do import PaymentConfig
    import json
    
    provider_type = config_data.get('provider_type')
    if not provider_type:
        return ResponseUtil.error(msg='支付提供商类型不能为空')
    
    # 查询配置
    stmt = select(PaymentConfig).where(
        PaymentConfig.provider_type == provider_type,
        PaymentConfig.del_flag == '0'
    )
    result = await query_db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        # 创建新配置
        config = PaymentConfig()
        config.provider_type = provider_type
        config.provider_name = config_data.get('provider_name', provider_type)
        config.config_data = {}
        config.supported_channels = []
        config.create_by = current_user.user.user_name
        config.create_time = datetime.now()
        query_db.add(config)
    
    # 更新配置
    if 'config_data' in config_data:
        config.config_data = config_data['config_data']
    if 'supported_channels' in config_data:
        config.supported_channels = config_data['supported_channels']
    if 'is_enabled' in config_data:
        config.is_enabled = config_data['is_enabled']
    if 'fee_rate' in config_data:
        config.fee_rate = config_data['fee_rate']
    if 'priority' in config_data:
        config.priority = config_data['priority']
    if 'remark' in config_data:
        config.remark = config_data['remark']
    
    config.update_by = current_user.user.user_name
    config.update_time = datetime.now()
    
    try:
        await query_db.commit()
        logger.info(f'更新支付配置成功: {provider_type}')
        return ResponseUtil.success(msg='更新成功')
    except Exception as e:
        await query_db.rollback()
        logger.error(f'更新支付配置失败: {str(e)}')
        return ResponseUtil.error(msg=f'更新失败: {str(e)}')
