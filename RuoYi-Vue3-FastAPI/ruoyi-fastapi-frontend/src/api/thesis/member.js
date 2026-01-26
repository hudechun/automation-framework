import request from '@/utils/request'

// 查询会员套餐列表
export function listPackage(query) {
  return request({
    url: '/thesis/member/package/list',
    method: 'get',
    params: query
  })
}

// 查询会员套餐详细
export function getPackage(packageId) {
  return request({
    url: '/thesis/member/package/' + packageId,
    method: 'get'
  })
}

// 新增会员套餐
export function addPackage(data) {
  return request({
    url: '/thesis/member/package',
    method: 'post',
    data: data
  })
}

// 修改会员套餐
export function updatePackage(data) {
  return request({
    url: '/thesis/member/package',
    method: 'put',
    data: data
  })
}

// 删除会员套餐
export function delPackage(packageId) {
  return request({
    url: '/thesis/member/package/' + packageId,
    method: 'delete'
  })
}

// 查询用户会员列表
export function listUserMember(query) {
  return request({
    url: '/thesis/member/membership/list',
    method: 'get',
    params: query
  })
}

// 查询用户会员详情
export function getUserMember(userId) {
  return request({
    url: '/thesis/member/membership/my',
    method: 'get'
  })
}

// 新增用户会员
export function addUserMember(data) {
  return request({
    url: '/thesis/member/membership/activate',
    method: 'post',
    params: {
      user_id: data.userId,
      package_id: data.packageId
    }
  })
}

// 修改用户会员
export function updateUserMember(data) {
  return request({
    url: '/thesis/member/membership/activate',
    method: 'post',
    params: {
      user_id: data.userId,
      package_id: data.packageId
    }
  })
}

// 删除用户会员
export function delUserMember(memberIds) {
  return request({
    url: '/thesis/member/membership/' + memberIds,
    method: 'delete'
  })
}

// 续费会员
export function renewUserMember(data) {
  return request({
    url: '/thesis/member/membership/activate',
    method: 'post',
    params: {
      user_id: data.userId,
      package_id: data.packageId
    }
  })
}

// 查询配额
export function getQuota(userId) {
  return request({
    url: '/thesis/member/quota/my',
    method: 'get'
  })
}

// 查询配额记录
export function listQuotaLog(query) {
  return request({
    url: '/thesis/member/quota/record/list',
    method: 'get',
    params: query
  })
}

// 充值配额
export function rechargeQuota(data) {
  return request({
    url: '/thesis/member/quota/compensate',
    method: 'post',
    params: {
      user_id: data.userId,
      feature_type: data.quotaType,
      amount: data.amount,
      reason: data.remark || '管理员充值',
      business_id: 0
    }
  })
}

// 导出配额记录
export function exportQuotaLog(query) {
  return request({
    url: '/thesis/member/quota/record/export',
    method: 'get',
    params: query,
    responseType: 'blob'
  })
}
