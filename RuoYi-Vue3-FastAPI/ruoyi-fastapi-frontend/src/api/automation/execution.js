import request from '@/utils/request'

// 查询执行记录列表
export function listExecution(query) {
  return request({
    url: '/automation/execution/list',
    method: 'get',
    params: query
  })
}

// 查询执行记录详细
export function getExecution(executionId) {
  return request({
    url: '/automation/execution/' + executionId,
    method: 'get'
  })
}

// 删除执行记录
export function delExecution(executionId) {
  return request({
    url: '/automation/execution/' + executionId,
    method: 'delete'
  })
}
