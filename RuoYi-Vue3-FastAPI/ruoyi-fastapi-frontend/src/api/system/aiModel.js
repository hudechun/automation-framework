import request from '@/utils/request'

// 获取AI模型配置列表
export function listAiModel(query) {
  return request({
    url: '/system/ai-model/list',
    method: 'get',
    params: query
  })
}

// 兼容旧的API路径（论文模块）
export function listThesisAiModel(query) {
  return request({
    url: '/thesis/ai-model/list',
    method: 'get',
    params: query
  })
}

// 获取预设模型列表
export function getPresetModels(query) {
  return request({
    url: '/system/ai-model/preset-models',
    method: 'get',
    params: query
  })
}

// 根据类型获取模型列表
export function getModelsByType(modelType) {
  return request({
    url: `/system/ai-model/models-by-type/${modelType}`,
    method: 'get'
  })
}

// 获取AI模型配置详情
export function getAiModel(configId) {
  return request({
    url: `/system/ai-model/${configId}`,
    method: 'get'
  })
}

// 获取默认AI模型配置
export function getDefaultAiModel(modelType = 'language') {
  return request({
    url: '/system/ai-model/default/config',
    method: 'get',
    params: { modelType }
  })
}

// 获取启用的AI模型配置列表
export function getEnabledAiModels(modelType) {
  return request({
    url: '/system/ai-model/enabled/list',
    method: 'get',
    params: { modelType }
  })
}

// 新增AI模型配置
export function addAiModel(data) {
  return request({
    url: '/system/ai-model',
    method: 'post',
    data: data
  })
}

// 修改AI模型配置
export function updateAiModel(data) {
  return request({
    url: '/system/ai-model',
    method: 'put',
    data: data
  })
}

// 删除AI模型配置
export function delAiModel(configId) {
  return request({
    url: `/system/ai-model/${configId}`,
    method: 'delete'
  })
}

// 启用AI模型配置
export function enableAiModel(configId) {
  return request({
    url: `/system/ai-model/${configId}/enable`,
    method: 'put'
  })
}

// 禁用AI模型配置
export function disableAiModel(configId) {
  return request({
    url: `/system/ai-model/${configId}/disable`,
    method: 'put'
  })
}

// 设置默认AI模型配置
export function setDefaultAiModel(configId) {
  return request({
    url: `/system/ai-model/${configId}/default`,
    method: 'put'
  })
}

// 测试AI模型配置
export function testAiModel(configId, testPrompt = '你好') {
  return request({
    url: `/system/ai-model/${configId}/test`,
    method: 'post',
    params: { testPrompt }
  })
}
