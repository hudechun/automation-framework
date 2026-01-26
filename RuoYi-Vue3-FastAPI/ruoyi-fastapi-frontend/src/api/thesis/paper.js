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

// 生成大纲
export function generateOutline(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/outline',
    method: 'post'
  })
}

// 查询大纲
export function getOutline(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/outline',
    method: 'get'
  })
}

// 生成章节
export function generateChapter(data) {
  return request({
    url: '/thesis/paper/' + data.thesisId + '/chapter',
    method: 'post',
    data: data
  })
}

// 批量生成章节 (循环调用单个生成)
export async function batchGenerateChapters(data) {
  const results = []
  for (const chapter of data.chapters) {
    const result = await generateChapter({
      thesisId: data.thesisId,
      ...chapter
    })
    results.push(result)
  }
  return { data: results }
}

// 查询章节列表
export function listChapters(thesisId) {
  return request({
    url: '/thesis/paper/' + thesisId + '/chapters',
    method: 'get'
  })
}

// 导出论文
export function exportPaper(data) {
  return request({
    url: '/thesis/paper/export',
    method: 'post',
    data: data,
    responseType: 'blob'
  })
}
