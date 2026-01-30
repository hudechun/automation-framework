import request from '@/utils/request'

// 学生列表（分页）
export function listStudent(query) {
  return request({
    url: '/student/verification/list',
    method: 'get',
    params: query
  })
}

// 学生详情
export function getStudent(studentId) {
  return request({
    url: '/student/verification/' + studentId,
    method: 'get'
  })
}

// 封装 multipart 请求：删除 Content-Type 让浏览器自动设置 boundary
function multipartRequest(options) {
  return request({
    ...options,
    transformRequest: [(data, headers) => {
      if (data instanceof FormData) {
        delete headers['Content-Type']
      }
      return data
    }]
  })
}

// Excel 导入（上传文件）
export function importStudents(file) {
  const formData = new FormData()
  formData.append('file', file)
  return multipartRequest({
    url: '/student/verification/import',
    method: 'post',
    data: formData,
    timeout: 60000
  })
}

// 上传学生照片（按验证码存储到 uploads/pic/photo/{验证码}.png）
export function uploadPhoto(verificationCode, file) {
  const formData = new FormData()
  formData.append('verification_code', verificationCode)
  formData.append('file', file)
  return multipartRequest({
    url: '/student/verification/upload-photo',
    method: 'post',
    data: formData,
    timeout: 30000
  })
}

// 报告图（Blob，需鉴权）
export function getReportImageBlob(studentId) {
  return request({
    url: '/student/verification/report/image/' + studentId,
    method: 'get',
    responseType: 'blob',
    timeout: 60000
  })
}

// 二维码图片（Blob，需鉴权，用于下载）
export function getQrImageBlob(studentId) {
  return request({
    url: '/student/verification/qr/image/' + studentId,
    method: 'get',
    responseType: 'blob',
    timeout: 15000
  })
}

// ========== 对外验证（无需登录） ==========
// 根据验证码查询学籍（H5 用，不携带 token）
export function getVerifyCheck(code) {
  return request({
    url: '/verify/check',
    method: 'get',
    params: { code },
    headers: { isToken: false },
    timeout: 10000
  })
}
