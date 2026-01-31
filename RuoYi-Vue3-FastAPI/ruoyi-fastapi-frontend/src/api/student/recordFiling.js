import request from '@/utils/request'

export function listStudent(query) {
  return request({
    url: '/student/record-filing/list',
    method: 'get',
    params: query
  })
}

export function getStudent(studentId) {
  return request({
    url: '/student/record-filing/' + studentId,
    method: 'get'
  })
}

export function updateStudent(studentId, data) {
  return request({
    url: '/student/record-filing/' + studentId,
    method: 'put',
    data
  })
}

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

export function importStudents(file) {
  const formData = new FormData()
  formData.append('file', file)
  return multipartRequest({
    url: '/student/record-filing/import',
    method: 'post',
    data: formData,
    timeout: 60000
  })
}

export function uploadPhoto(verificationCode, file) {
  const formData = new FormData()
  formData.append('verification_code', verificationCode)
  formData.append('file', file)
  return multipartRequest({
    url: '/student/record-filing/upload-photo',
    method: 'post',
    data: formData,
    timeout: 30000
  })
}

export function getReportImageBlob(studentId) {
  return request({
    url: '/student/record-filing/report/image/' + studentId,
    method: 'get',
    responseType: 'blob',
    timeout: 60000
  })
}

export function getQrImageBlob(studentId) {
  return request({
    url: '/student/record-filing/qr/image/' + studentId,
    method: 'get',
    responseType: 'blob',
    timeout: 15000
  })
}

export function batchDownloadQr(studentIds) {
  return request({
    url: '/student/record-filing/qr/batch-download',
    method: 'post',
    data: { studentIds },
    responseType: 'blob',
    timeout: 60000
  })
}

export function batchDownloadReport(studentIds) {
  return request({
    url: '/student/record-filing/report/batch-download',
    method: 'post',
    data: { studentIds },
    responseType: 'blob',
    timeout: 300000,
    headers: { repeatSubmit: false }
  })
}

// ========== 对外备案表验证（无需登录） ==========
export function getVerifyFilingCheck(code) {
  return request({
    url: '/verify/filing/check',
    method: 'get',
    params: { code },
    headers: { isToken: false },
    timeout: 10000
  })
}
