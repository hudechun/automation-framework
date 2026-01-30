import request from '@/utils/request'

// 查询大纲提示词模板列表
export function listOutlinePromptTemplate(query) {
  return request({
    url: '/thesis/outline-prompt-template/list',
    method: 'get',
    params: query
  })
}

// 查询大纲提示词模板详细
export function getOutlinePromptTemplate(promptTemplateId) {
  return request({
    url: '/thesis/outline-prompt-template/' + promptTemplateId,
    method: 'get'
  })
}

// 新增大纲提示词模板
export function addOutlinePromptTemplate(data) {
  return request({
    url: '/thesis/outline-prompt-template',
    method: 'post',
    data: data
  })
}

// 修改大纲提示词模板
export function updateOutlinePromptTemplate(promptTemplateId, data) {
  return request({
    url: '/thesis/outline-prompt-template/' + promptTemplateId,
    method: 'put',
    data: data
  })
}

// 删除大纲提示词模板
export function delOutlinePromptTemplate(promptTemplateId) {
  return request({
    url: '/thesis/outline-prompt-template/' + promptTemplateId,
    method: 'delete'
  })
}
