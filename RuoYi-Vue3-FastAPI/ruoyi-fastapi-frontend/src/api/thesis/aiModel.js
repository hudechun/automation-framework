import request from '@/utils/request'

// 查询AI模型列表
export function listAiModel(query) {
  return request({
    url: '/thesis/ai-model/list',
    method: 'get',
    params: query
  })
}

// 查询AI模型详细
export function getAiModel(configId) {
  return request({
    url: '/thesis/ai-model/' + configId,
    method: 'get'
  })
}

// 新增AI模型
export function addAiModel(data) {
  return request({
    url: '/thesis/ai-model',
    method: 'post',
    data: data
  })
}

// 修改AI模型
export function updateAiModel(data) {
  return request({
    url: '/thesis/ai-model',
    method: 'put',
    data: data
  })
}

// 删除AI模型
export function delAiModel(configId) {
  return request({
    url: '/thesis/ai-model/' + configId,
    method: 'delete'
  })
}

// 启用AI模型
export function enableAiModel(configId) {
  return request({
    url: '/thesis/ai-model/' + configId + '/enable',
    method: 'put'
  })
}

// 禁用AI模型
export function disableAiModel(configId) {
  return request({
    url: '/thesis/ai-model/' + configId + '/disable',
    method: 'put'
  })
}

// 设置默认模型
export function setDefaultAiModel(configId) {
  return request({
    url: '/thesis/ai-model/' + configId + '/default',
    method: 'put'
  })
}

// 测试模型连接
export function testAiModel(configId) {
  return request({
    url: '/thesis/ai-model/' + configId + '/test',
    method: 'post'
  })
}

// 获取可用模型列表（用于论文生成）
export function getAvailableModels() {
  return request({
    url: '/thesis/ai-model/available',
    method: 'get'
  })
}
