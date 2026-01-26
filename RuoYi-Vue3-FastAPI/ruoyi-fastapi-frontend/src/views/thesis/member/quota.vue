<template>
  <div class="modern-container">
    <!-- 顶部搜索区 -->
    <div class="search-section glass-card">
      <el-form :model="queryParams" ref="queryRef" :inline="true">
        <el-form-item>
          <el-input
            v-model="queryParams.userName"
            placeholder="搜索用户名"
            clearable
            @keyup.enter="handleQuery"
            class="modern-input"
          >
            <template #prefix>
              <Search class="w-4 h-4" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-select
            v-model="queryParams.operationType"
            placeholder="操作类型"
            clearable
            class="modern-select"
          >
            <el-option label="扣减" value="deduct" />
            <el-option label="充值" value="recharge" />
            <el-option label="退款" value="refund" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery" class="modern-btn">
            <Search class="w-4 h-4 mr-2" />
            搜索
          </el-button>
          <el-button @click="resetQuery" class="modern-btn-secondary">
            <RefreshCw class="w-4 h-4 mr-2" />
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleRecharge" class="modern-btn-gradient">
        <Plus class="w-4 h-4 mr-2" />
        充值配额
      </el-button>
      <el-button @click="handleExport" class="modern-btn-outline">
        <Download class="w-4 h-4 mr-2" />
        导出记录
      </el-button>
    </div>

    <!-- 配额记录列表 -->
    <div class="table-section glass-card">
      <el-table 
        v-loading="loading" 
        :data="quotaList"
        class="modern-table"
        :header-cell-style="{ background: 'transparent', color: '#1e293b', fontWeight: '600' }"
      >
        <el-table-column label="用户" width="180">
          <template #default="scope">
            <div class="user-cell">
              <div class="user-avatar">
                {{ scope.row.userName?.charAt(0).toUpperCase() }}
              </div>
              <div class="user-info">
                <div class="user-name">{{ scope.row.userName }}</div>
                <div class="user-id">ID: {{ scope.row.userId }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作类型" width="120">
          <template #default="scope">
            <div class="operation-badge" :class="`operation-${scope.row.operationType}`">
              <component :is="getOperationIcon(scope.row.operationType)" class="w-4 h-4" />
              <span>{{ getOperationLabel(scope.row.operationType) }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="配额类型" width="120">
          <template #default="scope">
            <div class="quota-type-badge">
              <FileText class="w-4 h-4" />
              <span>{{ getQuotaTypeLabel(scope.row.quotaType) }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="变动数量" width="120">
          <template #default="scope">
            <div class="amount-cell" :class="getAmountClass(scope.row.operationType)">
              <component :is="getAmountIcon(scope.row.operationType)" class="w-4 h-4" />
              <span>{{ getAmountText(scope.row.operationType, scope.row.amount) }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="变动前" prop="beforeAmount" width="100" />
        <el-table-column label="变动后" prop="afterAmount" width="100" />
        
        <el-table-column label="关联业务" min-width="200">
          <template #default="scope">
            <div v-if="scope.row.relatedType" class="related-info">
              <div class="related-tag">
                <Tag class="w-3 h-3" />
                {{ getRelatedTypeLabel(scope.row.relatedType) }}
              </div>
              <div class="related-id">#{{ scope.row.relatedId }}</div>
              <div class="related-desc">{{ scope.row.description }}</div>
            </div>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作人" prop="operatorName" width="120" />
        <el-table-column label="操作时间" prop="createTime" width="160" />
        <el-table-column label="备注" prop="remark" min-width="150" show-overflow-tooltip />
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <pagination
          v-show="total > 0"
          :total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          @pagination="getList"
        />
      </div>
    </div>

    <!-- 充值配额对话框 -->
    <el-dialog 
      v-model="rechargeVisible" 
      width="500px" 
      :show-close="false"
      class="modern-dialog"
    >
      <template #header>
        <div class="dialog-header">
          <Wallet class="w-6 h-6 text-indigo-600" />
          <span>充值配额</span>
        </div>
      </template>
      
      <el-form ref="rechargeFormRef" :model="rechargeForm" :rules="rechargeRules" label-width="100px">
        <el-form-item label="选择用户" prop="userId">
          <el-select
            v-model="rechargeForm.userId"
            placeholder="请选择用户"
            filterable
            class="w-full"
            @change="handleUserChange"
          >
            <el-option
              v-for="user in userList"
              :key="user.userId"
              :label="`${user.userName} (${user.nickName})`"
              :value="user.userId"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="当前配额" v-if="currentQuota">
          <div class="current-quota-display">
            <div class="quota-item">
              <FileText class="w-4 h-4" />
              <span>论文: {{ currentQuota.paperQuota || 0 }}</span>
            </div>
            <div class="quota-item">
              <FileText class="w-4 h-4" />
              <span>模板: {{ currentQuota.templateQuota || 0 }}</span>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="配额类型" prop="quotaType">
          <el-radio-group v-model="rechargeForm.quotaType" class="modern-radio-group">
            <el-radio label="paper">论文配额</el-radio>
            <el-radio label="template">模板配额</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="充值数量" prop="amount">
          <el-input-number
            v-model="rechargeForm.amount"
            :min="1"
            :max="10000"
            class="w-full"
          />
        </el-form-item>
        
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="rechargeForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入充值原因"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="rechargeVisible = false" class="modern-btn-secondary">取消</el-button>
          <el-button type="primary" @click="submitRecharge" class="modern-btn-gradient">确定充值</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="QuotaManagement">
import { ref, reactive, onMounted, getCurrentInstance } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, RefreshCw, Plus, Download, Wallet, FileText, Tag, TrendingUp, TrendingDown, RotateCcw } from 'lucide-vue-next'
import { listQuotaLog, rechargeQuota, exportQuotaLog, getUserMember } from '@/api/thesis/member'
import { listUser } from '@/api/system/user'
import { download } from '@/utils/request'

const { proxy } = getCurrentInstance()

const quotaList = ref([])
const userList = ref([])
const loading = ref(true)
const total = ref(0)
const rechargeVisible = ref(false)
const currentQuota = ref(null)

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  userName: null,
  operationType: null
})

const rechargeForm = reactive({
  userId: null,
  quotaType: 'paper',
  amount: 1,
  remark: null
})

const rechargeRules = {
  userId: [{ required: true, message: '请选择用户', trigger: 'change' }],
  quotaType: [{ required: true, message: '请选择配额类型', trigger: 'change' }],
  amount: [{ required: true, message: '请输入充值数量', trigger: 'blur' }]
}

const getList = async () => {
  loading.value = true
  try {
    const res = await listQuotaLog(queryParams)
    quotaList.value = res.rows
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const getUserList = async () => {
  const res = await listUser({ pageNum: 1, pageSize: 1000 })
  userList.value = res.rows
}

const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  proxy.resetForm('queryRef')
  handleQuery()
}

const handleRecharge = () => {
  resetRechargeForm()
  rechargeVisible.value = true
}

const handleUserChange = async (userId) => {
  try {
    const res = await getUserMember(userId)
    currentQuota.value = {
      paperQuota: res.data.paperQuotaTotal - res.data.paperQuotaUsed,
      templateQuota: res.data.templateQuotaTotal - res.data.templateQuotaUsed
    }
  } catch (error) {
    currentQuota.value = null
  }
}

const submitRecharge = () => {
  proxy.$refs.rechargeFormRef.validate(async (valid) => {
    if (valid) {
      await rechargeQuota(rechargeForm)
      ElMessage.success('充值成功')
      rechargeVisible.value = false
      getList()
    }
  })
}

const handleExport = () => {
  download('/thesis/quota/export', queryParams, '配额记录.xlsx')
}

const resetRechargeForm = () => {
  rechargeForm.userId = null
  rechargeForm.quotaType = 'paper'
  rechargeForm.amount = 1
  rechargeForm.remark = null
  currentQuota.value = null
  proxy.resetForm('rechargeFormRef')
}

const getOperationIcon = (type) => {
  const iconMap = {
    'deduct': TrendingDown,
    'recharge': TrendingUp,
    'refund': RotateCcw
  }
  return iconMap[type] || FileText
}

const getOperationLabel = (type) => {
  const labelMap = {
    'deduct': '扣减',
    'recharge': '充值',
    'refund': '退款'
  }
  return labelMap[type] || type
}

const getQuotaTypeLabel = (type) => {
  const labelMap = {
    'paper': '论文配额',
    'template': '模板配额'
  }
  return labelMap[type] || type
}

const getRelatedTypeLabel = (type) => {
  const labelMap = {
    'order': '订单',
    'paper': '论文',
    'template': '模板'
  }
  return labelMap[type] || type
}

const getAmountClass = (type) => {
  return type === 'deduct' ? 'amount-minus' : 'amount-plus'
}

const getAmountIcon = (type) => {
  return type === 'deduct' ? TrendingDown : TrendingUp
}

const getAmountText = (type, amount) => {
  return type === 'deduct' ? `-${amount}` : `+${amount}`
}

onMounted(() => {
  getList()
  getUserList()
})
</script>

<style scoped lang="scss">
.modern-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  margin-bottom: 1.5rem;
}

.search-section {
  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

.modern-input {
  width: 240px;
  :deep(.el-input__wrapper) {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
}

.modern-select {
  width: 200px;
  :deep(.el-input__wrapper) {
    border-radius: 12px;
  }
}

.modern-btn {
  border-radius: 12px;
  padding: 0.625rem 1.5rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  }
}

.modern-btn-secondary {
  @extend .modern-btn;
  background: white;
  border: 1px solid #e2e8f0;
  color: #64748b;
  
  &:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
}

.modern-btn-gradient {
  @extend .modern-btn;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  
  &:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  }
}

.modern-btn-outline {
  @extend .modern-btn;
  background: transparent;
  border: 2px solid white;
  color: white;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.action-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.table-section {
  .modern-table {
    :deep(.el-table__body-wrapper) {
      .el-table__row {
        transition: all 0.3s;
        
        &:hover {
          background: rgba(99, 102, 241, 0.05);
          transform: scale(1.01);
        }
      }
    }
  }
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  
  .user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1rem;
  }
  
  .user-info {
    .user-name {
      font-weight: 600;
      color: #1e293b;
      margin-bottom: 0.25rem;
    }
    
    .user-id {
      font-size: 0.75rem;
      color: #94a3b8;
    }
  }
}

.operation-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  
  &.operation-deduct {
    background: rgba(239, 68, 68, 0.1);
    color: #dc2626;
  }
  
  &.operation-recharge {
    background: rgba(34, 197, 94, 0.1);
    color: #16a34a;
  }
  
  &.operation-refund {
    background: rgba(251, 191, 36, 0.1);
    color: #d97706;
  }
}

.quota-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  font-size: 0.875rem;
  font-weight: 500;
}

.amount-cell {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 1rem;
  
  &.amount-minus {
    color: #dc2626;
  }
  
  &.amount-plus {
    color: #16a34a;
  }
}

.related-info {
  .related-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.75rem;
    border-radius: 8px;
    background: rgba(99, 102, 241, 0.1);
    color: #6366f1;
    font-size: 0.75rem;
    margin-bottom: 0.5rem;
  }
  
  .related-id {
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 0.25rem;
  }
  
  .related-desc {
    font-size: 0.75rem;
    color: #94a3b8;
  }
}

.pagination-wrapper {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}

.modern-dialog {
  :deep(.el-dialog) {
    border-radius: 24px;
    overflow: hidden;
  }
  
  :deep(.el-dialog__header) {
    padding: 0;
    margin: 0;
  }
  
  :deep(.el-dialog__body) {
    padding: 2rem;
  }
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1.25rem;
  font-weight: 600;
}

.current-quota-display {
  display: flex;
  gap: 1rem;
  
  .quota-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    background: rgba(99, 102, 241, 0.1);
    color: #6366f1;
    font-weight: 500;
  }
}

.modern-radio-group {
  :deep(.el-radio) {
    margin-right: 2rem;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.text-muted {
  color: #94a3b8;
}
</style>
