import request from '@/utils/request'

// 查询支付配置列表
export function listPaymentConfig(query) {
  return request({
    url: '/thesis/payment/configs',
    method: 'get',
    params: query
  })
}

// 查询支付配置详细
export function getPaymentConfig(channel) {
  return request({
    url: '/thesis/payment/config/' + channel,
    method: 'get'
  })
}

// 修改支付配置
export function updatePaymentConfig(data) {
  return request({
    url: '/thesis/payment/config',
    method: 'put',
    data: data
  })
}

// 查询可用支付渠道
export function listPaymentChannels() {
  return request({
    url: '/thesis/payment/channels',
    method: 'get'
  })
}

// 创建支付
export function createPayment(data) {
  return request({
    url: '/thesis/payment/create',
    method: 'post',
    params: {
      order_id: data.orderId,
      channel: data.channel,
      provider: data.provider
    }
  })
}

// 查询支付状态
export function queryPayment(paymentId, provider) {
  return request({
    url: '/thesis/payment/query',
    method: 'get',
    params: {
      payment_id: paymentId,
      provider: provider
    }
  })
}

// 查询交易记录
export function listTransaction(query) {
  return request({
    url: '/thesis/payment/transactions',
    method: 'get',
    params: query
  })
}

// 查询交易详情
export function getTransaction(transactionId) {
  return request({
    url: '/thesis/payment/transaction/' + transactionId,
    method: 'get'
  })
}

// 同步交易状态
export function syncTransaction(transactionId) {
  return request({
    url: '/thesis/payment/transaction/' + transactionId + '/sync',
    method: 'post'
  })
}

// 查询交易统计
export function getTransactionStats(query) {
  return request({
    url: '/thesis/payment/transaction/stats',
    method: 'get',
    params: query
  })
}

// 申请退款
export function refundPayment(data) {
  return request({
    url: '/thesis/payment/refund',
    method: 'post',
    params: {
      payment_id: data.paymentId,
      provider: data.provider,
      amount: data.amount,
      reason: data.reason
    }
  })
}

// 测试支付
export function testPayment(data) {
  return request({
    url: '/thesis/payment/test',
    method: 'post',
    data: data
  })
}

// 模拟支付（开发调试用）
export function mockPayment(orderId) {
  return request({
    url: '/thesis/payment/mock',
    method: 'post',
    params: {
      order_id: orderId
    }
  })
}

// 模拟支付回调（开发调试用）
export function mockPaymentCallback(orderNo) {
  return request({
    url: '/thesis/payment/mock-callback',
    method: 'post',
    params: {
      order_no: orderNo
    }
  })
}
