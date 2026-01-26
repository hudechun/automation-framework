# 扣费失败处理实现总结

## 实施时间
2026-01-25

## 实现内容

### 一、新增数据结构

#### QuotaCheckResult（配额检查结果）
```python
@dataclass
class QuotaCheckResult:
    """配额检查结果"""
    is_sufficient: bool      # 配额是否充足
    remaining_quota: int     # 剩余配额
    required_quota: int      # 需要的配额
    error_code: str          # 错误代码
    error_message: str       # 错误信息
    suggestion: str          # 建议操作
```

### 二、新增Service方法

#### 1. check_quota_detailed（详细配额检查）
**功能**：返回详细的配额检查结果，包含错误代码和建议

**检查项**：
1. ✅ 会员是否存在
2. ✅ 会员是否过期
3. ✅ 配额记录是否初始化
4. ✅ 配额是否充足

**错误代码**：
- `MEMBERSHIP_NOT_FOUND` - 未开通会员
- `MEMBERSHIP_EXPIRED` - 会员已过期
- `QUOTA_NOT_INITIALIZED` - 配额未初始化
- `QUOTA_INSUFFICIENT` - 配额不足
- `SUCCESS` - 配额充足

**示例**：
```python
result = await MemberService.check_quota_detailed(
    query_db, user_id, 'thesis_generation', 1
)

if not result.is_sufficient:
    # 配额不足
    print(result.error_message)  # "论文生成配额不足，当前剩余 0 次，需要 1 次"
    print(result.suggestion)      # "请购买配额包或升级会员套餐"
```

#### 2. check_quota_warning（配额预警检查）
**功能**：检查配额使用情况，返回预警信息

**预警级别**：
- `critical` - 配额用完或未开通（使用率100%）
- `high` - 配额不足10%（使用率≥90%）
- `medium` - 配额不足30%（使用率≥70%）
- `normal` - 配额充足（使用率<70%）

**返回数据**：
```python
{
    'has_warning': True,
    'warning_level': 'high',
    'message': '配额即将用完，仅剩 5 次',
    'suggestion': '建议尽快购买配额包',
    'remaining_quota': 5,
    'total_quota': 50
}
```

#### 3. compensate_quota（配额补偿）
**功能**：用于异常情况的配额补偿

**使用场景**：
- 系统异常导致扣费但业务未执行
- 用户投诉需要补偿
- 活动赠送配额

**特点**：
- 记录补偿原因
- 使用负数记录（表示补偿）
- 需要管理员权限

**示例**：
```python
await MemberService.compensate_quota(
    query_db,
    user_id=123,
    feature_type='thesis_generation',
    amount=5,
    reason='系统异常补偿',
    business_id=456
)
```

### 三、改进的deduct_quota方法

**改进点**：
1. ✅ 使用 `check_quota_detailed` 进行详细检查
2. ✅ 抛出带错误代码的异常
3. ✅ 返回剩余配额信息
4. ✅ 区分不同类型的异常

**错误处理**：
```python
try:
    await MemberService.deduct_quota(query_db, deduct_data)
except ServiceException as e:
    if e.code == 'MEMBERSHIP_NOT_FOUND':
        # 未开通会员
    elif e.code == 'MEMBERSHIP_EXPIRED':
        # 会员已过期
    elif e.code == 'QUOTA_INSUFFICIENT':
        # 配额不足
    elif e.code == 'DEDUCT_FAILED':
        # 扣减失败
```

### 四、新增Controller接口

#### 1. GET /thesis/member/quota/check/detailed
**功能**：详细检查配额

**参数**：
- `feature_type` - 功能类型
- `amount` - 需要的配额数量

**返回**：
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "is_sufficient": false,
        "remaining_quota": 0,
        "required_quota": 1,
        "error_code": "QUOTA_INSUFFICIENT",
        "error_message": "论文生成配额不足，当前剩余 0 次，需要 1 次",
        "suggestion": "请购买配额包或升级会员套餐"
    }
}
```

#### 2. GET /thesis/member/quota/warning
**功能**：配额预警检查

**参数**：
- `feature_type` - 功能类型

**返回**：
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "has_warning": true,
        "warning_level": "high",
        "message": "配额即将用完，仅剩 5 次",
        "suggestion": "建议尽快购买配额包",
        "remaining_quota": 5,
        "total_quota": 50
    }
}
```

#### 3. POST /thesis/member/quota/compensate
**功能**：配额补偿（管理员）

**权限**：`thesis:quota:compensate`

**参数**：
- `user_id` - 用户ID
- `feature_type` - 功能类型
- `amount` - 补偿数量
- `reason` - 补偿原因
- `business_id` - 业务ID（可选）

**返回**：
```json
{
    "code": 200,
    "msg": "配额补偿成功，已返还 5 次配额"
}
```

---

## 使用示例

### 场景1：创建论文前检查配额

**前端代码**：
```javascript
// 操作前检查配额
async function beforeCreateThesis() {
  try {
    const res = await checkQuotaDetailed({
      feature_type: 'thesis_generation',
      amount: 1
    })
    
    if (!res.data.is_sufficient) {
      // 显示配额不足提示
      ElMessageBox.confirm(
        `${res.data.error_message}\n\n${res.data.suggestion}`,
        '配额不足',
        {
          confirmButtonText: '立即购买',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        router.push('/member/packages')
      })
      return false
    }
    
    return true
  } catch (error) {
    ElMessage.error('配额检查失败')
    return false
  }
}

// 创建论文
async function createThesis() {
  // 先检查配额
  if (!await beforeCreateThesis()) return
  
  // 执行创建
  // ...
}
```

### 场景2：显示配额预警

**前端代码**：
```javascript
// 页面加载时检查配额预警
async function checkQuotaWarnings() {
  const features = ['thesis_generation', 'outline_generation', 'chapter_generation', 'export']
  
  for (const feature of features) {
    const res = await checkQuotaWarning({ feature_type: feature })
    
    if (res.data.has_warning && res.data.warning_level !== 'normal') {
      // 显示预警提示
      ElNotification({
        title: '配额预警',
        message: res.data.message,
        type: res.data.warning_level === 'critical' ? 'error' : 'warning',
        duration: 0,
        onClick: () => {
          router.push('/member/packages')
        }
      })
    }
  }
}

// 在mounted或onMounted中调用
onMounted(() => {
  checkQuotaWarnings()
})
```

### 场景3：配额显示组件

**Vue组件**：
```vue
<template>
  <div class="quota-card">
    <div class="quota-header">
      <span>{{ featureName }}</span>
      <el-tag :type="tagType">{{ warningLevel }}</el-tag>
    </div>
    
    <el-progress
      :percentage="usagePercentage"
      :status="progressStatus"
      :stroke-width="10"
    />
    
    <div class="quota-info">
      <span>剩余：{{ remainingQuota }} / {{ totalQuota }}</span>
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
      :type="alertType"
      :closable="false"
      show-icon
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { checkQuotaWarning } from '@/api/member'

const props = defineProps({
  featureType: String,
  featureName: String
})

const warningData = ref({})

const usagePercentage = computed(() => {
  const total = warningData.value.total_quota || 0
  const remaining = warningData.value.remaining_quota || 0
  return ((total - remaining) / total) * 100
})

const progressStatus = computed(() => {
  const level = warningData.value.warning_level
  if (level === 'critical') return 'exception'
  if (level === 'high') return 'warning'
  return 'success'
})

const showPurchaseButton = computed(() => {
  return ['critical', 'high'].includes(warningData.value.warning_level)
})

onMounted(async () => {
  const res = await checkQuotaWarning({ feature_type: props.featureType })
  warningData.value = res.data
})
</script>
```

---

## 错误处理流程

### 1. 配额不足
```
用户操作 → 检查配额 → 配额不足 → 返回详细错误 → 前端提示 → 引导购买
```

### 2. 会员过期
```
用户操作 → 检查会员 → 会员过期 → 返回过期信息 → 前端提示 → 引导续费
```

### 3. 未开通会员
```
用户操作 → 检查会员 → 未开通 → 返回提示信息 → 前端提示 → 引导购买套餐
```

### 4. 系统异常
```
用户操作 → 扣减配额 → 系统异常 → 回滚事务 → 返回友好提示 → 管理员补偿
```

---

## 数据库记录

### 配额使用记录（正常扣减）
```sql
INSERT INTO ai_write_quota_record (
    user_id, feature_type, quota_amount, 
    business_type, business_id, use_time
) VALUES (
    123, 'thesis_generation', 1,
    'thesis_create', 456, NOW()
);
```

### 配额补偿记录（异常补偿）
```sql
INSERT INTO ai_write_quota_record (
    user_id, feature_type, quota_amount, 
    business_type, business_id, use_time, remark
) VALUES (
    123, 'thesis_generation', -1,  -- 负数表示补偿
    'quota_compensation', 456, NOW(), '系统异常补偿'
);
```

---

## 优势总结

### 1. 用户体验优化
- ✅ 操作前预检查，避免操作失败
- ✅ 详细的错误提示，告知原因和解决方案
- ✅ 配额预警提醒，提前购买
- ✅ 一键购买入口，方便快捷

### 2. 技术实现优化
- ✅ 详细的错误代码，便于前端处理
- ✅ 区分不同失败场景，精准提示
- ✅ 配额补偿机制，处理异常情况
- ✅ 完整的记录追踪，便于审计

### 3. 业务价值
- ✅ 提升用户满意度
- ✅ 减少客服工作量
- ✅ 提高转化率（引导购买）
- ✅ 降低投诉率

---

## 后续优化建议

### 1. 配额包推荐
根据用户使用情况，智能推荐合适的配额包

### 2. 配额使用分析
提供配额使用趋势图表，帮助用户了解使用情况

### 3. 配额到期提醒
会员到期前提醒用户续费

### 4. 配额转赠
允许用户之间转赠配额（需要审核）

### 5. 配额冻结
对于异常账号，可以冻结配额使用
