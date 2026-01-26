import request from '@/utils/request'

// 查询模板列表
export function listTemplate(query) {
  return request({
    url: '/thesis/template/list',
    method: 'get',
    params: query
  })
}

// 查询模板详细
export function getTemplate(templateId) {
  return request({
    url: '/thesis/template/' + templateId,
    method: 'get'
  })
}

// 新增模板
export function addTemplate(data) {
  return request({
    url: '/thesis/template',
    method: 'post',
    data: data
  })
}

// 修改模板
export function updateTemplate(data) {
  return request({
    url: '/thesis/template',
    method: 'put',
    data: data
  })
}

// 删除模板
export function delTemplate(templateId) {
  return request({
    url: '/thesis/template/' + templateId,
    method: 'delete'
  })
}

// 上传模板文件
export function uploadTemplate(data) {
  return request({
    url: '/thesis/template/upload',
    method: 'post',
    data: data,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 应用模板
export function applyTemplate(data) {
  return request({
    url: `/thesis/template/${data.templateId}/apply/${data.thesisId}`,
    method: 'post'
  })
}

// 查询热门模板
export function listHotTemplates() {
  return request({
    url: '/thesis/template/popular',
    method: 'get'
  })
}
