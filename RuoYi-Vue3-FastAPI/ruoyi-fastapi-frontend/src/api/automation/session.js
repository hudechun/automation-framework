import request from '@/utils/request'

// 查询会话列表
export function listSession(query) {
  return request({
    url: '/automation/session/list',
    method: 'get',
    params: query
  })
}

// 查询会话详细
export function getSession(sessionId) {
  return request({
    url: '/automation/session/' + sessionId,
    method: 'get'
  })
}

// 删除会话
export function delSession(sessionId) {
  return request({
    url: '/automation/session/' + sessionId,
    method: 'delete'
  })
}
