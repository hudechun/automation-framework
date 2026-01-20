import request from '@/utils/request'

// 查询模型配置列表
export function listConfig(query) {
  return request({
    url: '/automation/config/list',
    method: 'get',
    params: query
  })
}

// 查询模型配置详细
export function getConfig(configId) {
  return request({
    url: '/automation/config/' + configId,
    method: 'get'
  })
}

// 新增模型配置
export function addConfig(data) {
  return request({
    url: '/automation/config',
    method: 'post',
    data: data
  })
}

// 修改模型配置
export function updateConfig(data) {
  return request({
    url: '/automation/config',
    method: 'put',
    data: data
  })
}

// 删除模型配置
export function delConfig(configId) {
  return request({
    url: '/automation/config/' + configId,
    method: 'delete'
  })
}
