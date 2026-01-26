import request from '@/utils/request'

// 查询订单列表
export function listOrder(query) {
  return request({
    url: '/thesis/order/list',
    method: 'get',
    params: query
  })
}

// 查询订单详细
export function getOrder(orderId) {
  return request({
    url: '/thesis/order/' + orderId,
    method: 'get'
  })
}

// 创建订单
export function createOrder(data) {
  return request({
    url: '/thesis/order/create',
    method: 'post',
    params: {
      order_type: data.orderType,
      item_id: data.itemId,
      amount: data.amount,
      payment_method: data.paymentMethod || 'wechat'
    }
  })
}

// 取消订单
export function cancelOrder(orderId) {
  return request({
    url: '/thesis/order/cancel/' + orderId,
    method: 'post'
  })
}

// 申请退款
export function refundOrder(data) {
  return request({
    url: '/thesis/order/refund/' + data.orderId,
    method: 'post',
    params: {
      refund_reason: data.refundReason
    }
  })
}

// 查询订单统计
export function getOrderStats(query) {
  return request({
    url: '/thesis/order/statistics',
    method: 'get',
    params: query
  })
}
