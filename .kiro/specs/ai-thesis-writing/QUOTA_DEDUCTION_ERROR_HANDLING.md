# 用户扣费失败处理方案

## 概述

本文档详细说明当用户配额扣减失败时的各种处理策略和用户体验优化方案。

---

## 一、扣费失败的场景分类

### 1. 配额不足（最常见）
**场景**：用户剩余配额不足以完成当前操作

**当前处理**：
```python
if not await MemberService.check_quota(query_db, user_id, 'thesis_generation', 1):
    raise ServiceException(message='论文生成配额不足')
```

**问题**：
- ❌ 错误信息不够友好
- ❌ 没有告诉用户还剩多少配额
- ❌ 没有引导用户购买配额

### 2. 配额记录不存在
**场景**：用户从未开通会员，配额表中没有记录

**当前处理**：
```python
quota = await cls.get_user_quota(query_db, user_id, feature_type)
if not quota:
    return False  # check_quota返回False
```

**问题**：
- ❌ 与配额不足的错误信息相同
- ❌ 没有区分"未开通"和"配额用完"

### 3. 会员已过期
**场景**：用户会员已过期，但配额记录还在

**当前处理**：
- ❌ 没有检查会员状态
- ❌ 过期会员仍可使用剩余配额

### 4. 数据库异常
**场景**：数据库连接失败、死锁、超时等

**当前处理**：
```python
except Exception as e:
    await query_db.rollback()
    raise ServiceException(message=f'操作失败: {str(e)}')
```

**问题**：
- ❌ 错误信息暴露了技术细节
- ❌ 用户不知道如何处理

---

## 二、改进方案

### 1. 增强的配额检查方法

创建一个更详细的配额检查方法，返回详细的检查结果：

```python
from typing import Tuple
from dataclasses import dataclass

@dataclass
class QuotaCheckResult:
    """配额检查结果"""
    is_sufficient: bool  # 配额是否充足
    remaining_quota: int  # 剩余配额
    required_quota: int  # 需要的配额
    error_code: str  # 错误代码
    error_message: str  # 错误信息
    suggestion: str  # 建议操作

@classmethod
async def check_quota_detailed(
    cls,
    query_db: AsyncSession,
    user_id: int,
    feature_type: str,
    amount: int
) -> QuotaCheckResult:
    """
    详细检查用户配额
    
    :param query_db: 数据库会话
    :param user_id: 用户ID
    :param feature_type: 功能类型
    :param amount: 需要的配额数量
    :return: 详细的检查结果
    """
    # 1. 检查会员状态
    membership = await cls.get_user_membership(query_db, user_id)
    
    if not membership:
        return QuotaCheckResult(
            is_sufficient=False,
            remaining_quota=0,
            required_quota=amount,
            error_code='MEMBERSHIP_NOT_FOUND',
            error_message='您还未开通会员',
            suggestion='请先购买会员套餐以使用此功能'
        )
    
    # 2. 检查会员是否过期
    if membership.expire_time and membership.expire_time < datetime.now():
        return QuotaCheckResult(
            is_sufficient=False,
            remaining_quota=0,
            required_quota=amount,
            error_code='MEMBERSHIP_EXPIRED',
            error_message=f'您的会员已于 {membership.expire_time.strftime("%Y-%m-%d")} 过期',
            suggestion='请续费会员以继续使用'
        )
    
    # 3. 检查配额记录
    quota = await cls.get_user_quota(query_db, user_id, feature_type)
    
    if not quota:
        return QuotaCheckResult(
            is_sufficient=False,
            remaining_quota=0,
            required_quota=amount,
            error_code='QUOTA_NOT_INITIALIZED',
            error_message='配额未初始化',
            suggestion='请联系客服处理'
        )
    
    # 4. 检查配额是否充足
    if quota.remaining_quota < amount:
        return QuotaCheckResult(
            is_sufficient=False,
            remaining_quota=quota.remaining_quota,
            required_quota=amount,
            error_code='QUOTA_INSUFFICIENT',
            error_message=f'配额不足，当前剩余 {quota.remaining_quota} 次，需要 {amount} 次',
            suggestion='请购买配额包或升级会员套餐'
        )
    
    # 5. 配额充足
    return QuotaCheckResult(
        is_sufficient=True,
        remaining_quota=quota.remaining_quota,
        required_quota=amount,
        error_code='SUCCESS',
        error_message='配额充足',
        suggestion=''
    )
```

### 2. 改进的扣费方法

使用详细的配额检查结果：

```python
@classmethod
async def deduct_quota_with_check(
    cls,
    query_db: AsyncSession,
    deduct_data: DeductQuotaModel,
    auto_commit: bool = False
) -> CrudResponseModel:
    """
    扣减用户配额（带详细检查）
    
    :param query_db: 数据库会话
    :param deduct_data: 扣减数据
    :param auto_commit: 是否自动提交
    :return: 操作结果
    """
    # 详细检查配额
    check_result = await cls.check_quota_detailed(
        query_db,
        deduct_data.user_id,
        deduct_data.feature_type,
        deduct_data.amount
    )
    
    # 配额不足，返回详细错误信息
    if not check_result.is_sufficient:
        raise ServiceException(
            message=check_result.error_message,
            code=check_result.error_code,
            data={
                'remaining_quota': check_result.remaining_quota,
                'required_quota': check_result.required_quota,
                'suggestion': check_result.suggestion
            }
        )
    
    try:
        # 扣减配额
        await UserFeatureQuotaDao.deduct_quota(
            query_db,
            deduct_data.user_id,
            deduct_data.feature_type,
            deduct_data.amount
        )
        
        # 记录使用记录
        record_data = {
            'user_id': deduct_data.user_id,
            'feature_type': deduct_data.feature_type,
            'quota_amount': deduct_data.amount,
            'business_id': deduct_data.business_id,
            'business_type': deduct_data.business_type,
            'use_time': datetime.now(),
        }
        await QuotaRecordDao.add_record(query_db, record_data)
        
        # 只有明确要求才自动提交
        if auto_commit:
            await query_db.commit()
        
        return CrudResponseModel(
            is_success=True,
            message='配额扣减成功',
            data={
                'remaining_quota': check_result.remaining_quota - deduct_data.amount
            }
        )
    except Exception as e:
        if auto_commit:
            await query_db.rollback()
        raise ServiceException(
            message='配额扣减失败，请稍后重试',
            code='DEDUCT_FAILED',
            data={'error': str(e)}
        )
```

### 3. 业务层的错误处理

在业务方法中捕获并处理扣费失败：

```python
@classmethod
async def create_thesis(
    cls,
    query_db: AsyncSession,
    thesis_data: ThesisModel,
    user_id: int
) -> CrudResponseModel:
    """
    创建论文（需要扣减配额）
    """
    try:
        # 详细检查配额
        check_result = await MemberService.check_quota_detailed(
            query_db, user_id, 'thesis_generation', 1
        )
        
        if not check_result.is_sufficient:
            # 返回友好的错误信息
            return CrudResponseModel(
                is_success=False,
                message=check_result.error_message,
                code=check_result.error_code,
                data={
                    'remaining_quota': check_result.remaining_quota,
                    'required_quota': check_result.required_quota,
                    'suggestion': check_result.suggestion,
                    'can_purchase': True,  # 是否可以购买配额
                    'purchase_url': '/member/packages'  # 购买页面URL
                }
            )
        
        # 创建论文
        thesis_dict = thesis_data.model_dump(exclude_none=True)
        thesis_dict['user_id'] = user_id
        thesis_dict['status'] = 'draft'
        thesis_dict['total_word_count'] = 0
        
        new_thesis = await ThesisDao.add_thesis(query_db, thesis_dict)
        
        # 扣减配额
        deduct_data = DeductQuotaModel(
            user_id=user_id,
            feature_type='thesis_generation',
            amount=1,
            business_type='thesis_create',
            business_id=new_thesis.thesis_id
        )
        await MemberService.deduct_quota(query_db, deduct_data, auto_commit=False)
        
        # 统一提交事务
        await query_db.commit()
        
        return CrudResponseModel(
            is_success=True,
            message='论文创建成功',
            data={
                'thesis_id': new_thesis.thesis_id,
                'remaining_quota': check_result.remaining_quota - 1
            }
        )
        
    except ServiceException as e:
        await query_db.rollback()
        # 如果是配额相关错误，返回详细信息
        if e.code in ['MEMBERSHIP_NOT_FOUND', 'MEMBERSHIP_EXPIRED', 'QUOTA_INSUFFICIENT']:
            return CrudResponseModel(
                is_success=False,
                message=e.message,
                code=e.code,
                data=e.data
            )
        raise e
    except Exception as e:
        await query_db.rollback()
        raise ServiceException(message=f'论文创建失败: {str(e)}')
```

---

## 三、前端处理建议

### 1. 配额不足提示

```javascript
// 处理配额不足的响应
if (response.code === 'QUOTA_INSUFFICIENT') {
  ElMessageBox.confirm(
    `${response.message}\n\n${response.data.suggestion}`,
    '配额不足',
    {
      confirmButtonText: '立即购买',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 跳转到购买页面
    router.push(response.data.purchase_url)
  })
}
```

### 2. 会员过期提示

```javascript
if (response.code === 'MEMBERSHIP_EXPIRED') {
  ElMessageBox.confirm(
    `${response.message}\n\n${response.data.suggestion}`,
    '会员已过期',
    {
      confirmButtonText: '立即续费',
      cancelButtonText: '取消',
      type: 'error'
    }
  ).then(() => {
    router.push('/member/renew')
  })
}
```

### 3. 未开通会员提示

```javascript
if (response.code === 'MEMBERSHIP_NOT_FOUND') {
  ElMessageBox.confirm(
    `${response.message}\n\n${response.data.suggestion}`,
    '未开通会员',
    {
      confirmButtonText: '查看套餐',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    router.push('/member/packages')
  })
}
```

### 4. 操作前预检查

在用户点击操作按钮前，先检查配额：

```javascript
async function beforeCreateThesis() {
  try {
    // 调用配额检查接口
    const checkResult = await checkQuota({
      feature_type: 'thesis_generation',
      amount: 1
    })
    
    if (!checkResult.is_sufficient) {
      // 显示配额不足提示
      showQuotaInsufficientDialog(checkResult)
      return false
    }
    
    // 配额充足，继续操作
    return true
  } catch (error) {
    ElMessage.error('配额检查失败，请稍后重试')
    return false
  }
}

// 创建论文
async function createThesis() {
  // 先检查配额
  const canProceed = await beforeCreateThesis()
  if (!canProceed) return
  
  // 执行创建操作
  // ...
}
```

---

## 四、配额预警机制

### 1. 配额低于阈值时提醒

```python
@classmethod
async def check_quota_warning(
    cls,
    query_db: AsyncSession,
    user_id: int,
    feature_type: str
) -> dict:
    """
    检查配额预警
    
    :param query_db: 数据库会话
    :param user_id: 用户ID
    :param feature_type: 功能类型
    :return: 预警信息
    """
    quota = await cls.get_user_quota(query_db, user_id, feature_type)
    
    if not quota:
        return {
            'has_warning': True,
            'warning_level': 'critical',
            'message': '您还未开通此功能',
            'suggestion': '请购买会员套餐'
        }
    
    # 计算使用率
    usage_rate = quota.used_quota / quota.total_quota if quota.total_quota > 0 else 0
    
    # 配额用完
    if quota.remaining_quota == 0:
        return {
            'has_warning': True,
            'warning_level': 'critical',
            'message': '配额已用完',
            'suggestion': '请购买配额包或升级套餐'
        }
    
    # 配额不足10%
    elif usage_rate >= 0.9:
        return {
            'has_warning': True,
            'warning_level': 'high',
            'message': f'配额即将用完，仅剩 {quota.remaining_quota} 次',
            'suggestion': '建议尽快购买配额包'
        }
    
    # 配额不足30%
    elif usage_rate >= 0.7:
        return {
            'has_warning': True,
            'warning_level': 'medium',
            'message': f'配额剩余 {quota.remaining_quota} 次',
            'suggestion': '建议提前购买配额包'
        }
    
    # 配额充足
    else:
        return {
            'has_warning': False,
            'warning_level': 'normal',
            'message': f'配额充足，剩余 {quota.remaining_quota} 次',
            'suggestion': ''
        }
```

### 2. 前端配额显示组件

```vue
<template>
  <div class="quota-display">
    <el-progress
      :percentage="usagePercentage"
      :status="progressStatus"
      :stroke-width="8"
    />
    <div class="quota-info">
      <span>剩余配额：{{ remainingQuota }} / {{ totalQuota }}</span>
      <el-button
        v-if="showPurchaseButton"
        type="primary"
        size="small"
        @click="goPurchase"
      >
        购买配额
      </el-button>
    </div>
    <el-alert
      v-if="warningMessage"
      :title="warningMessage"
      :type="warningType"
      :closable="false"
      show-icon
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  remainingQuota: Number,
  totalQuota: Number,
  warningLevel: String
})

const usagePercentage = computed(() => {
  return ((props.totalQuota - props.remainingQuota) / props.totalQuota) * 100
})

const progressStatus = computed(() => {
  if (props.warningLevel === 'critical') return 'exception'
  if (props.warningLevel === 'high') return 'warning'
  return 'success'
})

const showPurchaseButton = computed(() => {
  return props.warningLevel === 'critical' || props.warningLevel === 'high'
})
</script>
```

---

## 五、异常情况的降级处理

### 1. 数据库异常时的处理

```python
@classmethod
async def deduct_quota_with_fallback(
    cls,
    query_db: AsyncSession,
    deduct_data: DeductQuotaModel,
    auto_commit: bool = False
) -> CrudResponseModel:
    """
    扣减配额（带降级处理）
    """
    try:
        return await cls.deduct_quota(query_db, deduct_data, auto_commit)
    except DatabaseError as e:
        # 数据库异常，记录日志
        logger.error(f'配额扣减数据库异常: {str(e)}')
        
        # 可以选择：
        # 1. 允许操作继续（后续补扣）
        # 2. 拒绝操作
        # 3. 使用缓存的配额信息
        
        raise ServiceException(
            message='系统繁忙，请稍后重试',
            code='SYSTEM_BUSY'
        )
```

### 2. 配额补偿机制

如果因为系统异常导致扣费失败但业务已执行，需要补偿机制：

```python
@classmethod
async def compensate_quota(
    cls,
    query_db: AsyncSession,
    user_id: int,
    feature_type: str,
    amount: int,
    reason: str
) -> CrudResponseModel:
    """
    配额补偿（用于异常情况的补偿）
    
    :param query_db: 数据库会话
    :param user_id: 用户ID
    :param feature_type: 功能类型
    :param amount: 补偿数量
    :param reason: 补偿原因
    :return: 操作结果
    """
    try:
        # 增加配额
        await UserFeatureQuotaDao.add_quota_amount(
            query_db, user_id, feature_type, amount
        )
        
        # 记录补偿记录
        record_data = {
            'user_id': user_id,
            'feature_type': feature_type,
            'quota_amount': -amount,  # 负数表示补偿
            'business_type': 'quota_compensation',
            'business_id': 0,
            'use_time': datetime.now(),
            'remark': reason
        }
        await QuotaRecordDao.add_record(query_db, record_data)
        
        await query_db.commit()
        
        return CrudResponseModel(
            is_success=True,
            message=f'配额补偿成功，已返还 {amount} 次配额'
        )
    except Exception as e:
        await query_db.rollback()
        raise ServiceException(message=f'配额补偿失败: {str(e)}')
```

---

## 六、实施步骤

### 第一阶段：基础改进（立即实施）
1. ✅ 改进配额检查方法，返回详细信息
2. ✅ 优化错误信息，区分不同的失败场景
3. ✅ 添加会员状态检查

### 第二阶段：用户体验优化（1周内）
1. 前端添加配额预检查
2. 实现配额预警机制
3. 优化错误提示和引导

### 第三阶段：高级功能（2周内）
1. 实现配额补偿机制
2. 添加配额使用统计和分析
3. 实现配额包推荐算法

---

## 七、总结

### 扣费失败处理的核心原则

1. **友好提示**：清晰告知用户失败原因和解决方案
2. **提前预警**：在配额不足前提醒用户
3. **引导购买**：失败时引导用户购买配额或升级套餐
4. **数据一致**：确保扣费和业务操作的原子性
5. **异常补偿**：系统异常时有补偿机制

### 用户体验优化要点

1. ✅ 操作前检查配额，避免操作失败
2. ✅ 配额不足时显示剩余数量
3. ✅ 提供一键购买入口
4. ✅ 配额预警提醒
5. ✅ 友好的错误提示

### 技术实现要点

1. ✅ 详细的配额检查结果
2. ✅ 区分不同的失败场景
3. ✅ 事务一致性保证
4. ✅ 异常降级处理
5. ✅ 配额补偿机制
