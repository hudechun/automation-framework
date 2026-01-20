import request from '@/utils/request'

// 查询任务列表
export function listTask(query) {
  return request({
    url: '/automation/task/list',
    method: 'get',
    params: query
  })
}

// 查询任务详细
export function getTask(taskId) {
  return request({
    url: '/automation/task/' + taskId,
    method: 'get'
  })
}

// 新增任务
export function addTask(data) {
  return request({
    url: '/automation/task',
    method: 'post',
    data: data
  })
}

// 修改任务
export function updateTask(data) {
  return request({
    url: '/automation/task',
    method: 'put',
    data: data
  })
}

// 删除任务
export function delTask(taskId) {
  return request({
    url: '/automation/task/' + taskId,
    method: 'delete'
  })
}

// 执行任务
export function executeTask(taskId) {
  return request({
    url: '/automation/task/' + taskId + '/execute',
    method: 'post'
  })
}
