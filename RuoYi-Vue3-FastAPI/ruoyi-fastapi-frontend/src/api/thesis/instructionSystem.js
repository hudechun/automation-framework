import request from '@/utils/request'

// 查询指令系统列表
export function listInstructionSystem(query) {
  return request({
    url: '/thesis/instruction-system/list',
    method: 'get',
    params: query
  })
}

// 查询激活的指令系统
export function getActiveInstructionSystem() {
  return request({
    url: '/thesis/instruction-system/active',
    method: 'get'
  })
}

// 查询指令系统详细
export function getInstructionSystem(systemId) {
  return request({
    url: '/thesis/instruction-system/' + systemId,
    method: 'get'
  })
}

// 新增指令系统
export function addInstructionSystem(data) {
  return request({
    url: '/thesis/instruction-system',
    method: 'post',
    data: data
  })
}

// 修改指令系统
export function updateInstructionSystem(systemId, data) {
  return request({
    url: '/thesis/instruction-system/' + systemId,
    method: 'put',
    data: data
  })
}

// 删除指令系统
export function delInstructionSystem(systemId) {
  return request({
    url: '/thesis/instruction-system/' + systemId,
    method: 'delete'
  })
}

// 激活指令系统
export function activateInstructionSystem(systemId) {
  return request({
    url: '/thesis/instruction-system/' + systemId + '/activate',
    method: 'put'
  })
}
