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

// 创建任务（addTask 别名）
export const createTask = addTask

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

// 暂停任务
export function pauseTask(taskId) {
  return request({
    url: '/automation/task/' + taskId + '/pause',
    method: 'post'
  })
}

// 恢复任务
export function resumeTask(taskId) {
  return request({
    url: '/automation/task/' + taskId + '/resume',
    method: 'post'
  })
}

// 停止任务
export function stopTask(taskId) {
  return request({
    url: '/automation/task/' + taskId + '/stop',
    method: 'post'
  })
}

// 解析自然语言任务
export function parseTask(data) {
  return request({
    url: '/automation/task/parse',
    method: 'post',
    data: data
  })
}

// 获取执行状态
export function getExecutionStatus(taskId) {
  return request({
    url: '/automation/task/' + taskId + '/execution/status',
    method: 'get'
  })
}

// 获取执行进度
export function getExecutionProgress(taskId) {
  return request({
    url: '/automation/task/' + taskId + '/execution/progress',
    method: 'get'
  })
}

// 获取执行日志
export function getExecutionLogs(taskId, params) {
  return request({
    url: '/automation/task/' + taskId + '/execution/logs',
    method: 'get',
    params: params
  })
}

// 检查客户端连接状态（headful 模式用，未部署 automation 时返回离线）
export function checkClientStatus() {
  return Promise.resolve({ data: { online: false, last_seen: null } })
}
