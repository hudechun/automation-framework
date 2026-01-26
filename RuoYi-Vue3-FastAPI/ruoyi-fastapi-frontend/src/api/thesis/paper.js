import request from '@/utils/request'

// 查询论文列表
export function listPaper(query) {
  return request({
    url: '/thesis/paper/list',
    method: 'get',
    params: query
  })
}

// 查询论文详细
export function getPaper(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId,
    method: 'get'
  })
}

// 新增论文
export function addPaper(data) {
  return request({
    url: '/thesis/paper',
    method: 'post',
    data: data
  })
}

// 修改论文
export function updatePaper(data) {
  return request({
    url: '/thesis/paper',
    method: 'put',
    data: data
  })
}

// 删除论文
export function delPaper(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId,
    method: 'delete'
  })
}

// 生成大纲（长时间任务，超时时间 5 分钟）
export function generateOutline(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/outline',
    method: 'post',
    data: {},
    timeout: 5 * 60 * 1000  // 5 分钟超时
  })
}

// 查询大纲
export function getOutline(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/outline',
    method: 'get'
  })
}

// 生成章节（长时间任务，超时时间 5 分钟）
export function generateChapter(data) {
  return request({
    url: '/thesis/paper/' + data.thesisId + '/chapter',
    method: 'post',
    data: data,
    timeout: 5 * 60 * 1000  // 5 分钟超时
  })
}

// 批量生成章节（使用真正的批量接口，统一检查配额）
export function batchGenerateChapters(thesisId, chapters) {
  return request({
    url: '/thesis/paper/' + thesisId + '/chapters/batch',
    method: 'post',
    data: chapters,  // 直接传递章节数组
    timeout: 30 * 60 * 1000  // 30 分钟超时（批量生成可能需要较长时间）
  })
}

// 查询章节列表
export function listChapters(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/chapters',
    method: 'get'
  })
}

// 查询章节生成进度
export function getChapterProgress(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/chapters/progress',
    method: 'get'
  })
}

// 继续生成未完成的章节
export function continueGenerateChapters(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/chapters/continue',
    method: 'post',
    timeout: 30 * 60 * 1000  // 30 分钟超时
  })
}

// 查询论文生成进度
export function getThesisProgress(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/progress',
    method: 'get'
  })
}

// 格式化论文
export function formatThesis(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/format',
    method: 'post',
    timeout: 10 * 60 * 1000  // 10 分钟超时
  })
}

// 下载论文（格式化后的Word文档）
export function downloadThesis(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/download',
    method: 'get',
    responseType: 'blob'
  })
}
