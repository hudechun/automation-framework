<template>
  <div class="modern-container">
    <!-- 搜索栏 -->
    <div class="search-section glass-card">
    <el-form :model="queryParams" ref="queryRef" :inline="true">
      <el-form-item label="交易流水号" prop="transactionNo">
        <el-input
          v-model="queryParams.transactionNo"
          placeholder="请输入交易流水号"
          clearable
          @keyup.enter="handleQuery"
          style="width: 240px"
        />
      </el-form-item>
      <el-form-item label="订单号" prop="orderNo">
        <el-input
          v-model="queryParams.orderNo"
          placeholder="请输入订单号"
          clearable
          @keyup.enter="handleQuery"
          style="width: 240px"
        />
      </el-form-item>
      <el-form-item label="支付渠道" prop="channel">
        <el-select
          v-model="queryParams.channel"
          placeholder="请选择渠道"
          clearable
          style="width: 200px"
        >
          <el-option
            v-for="dict in thesis_payment_channel"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="交易状态" prop="status">
        <el-select
          v-model="queryParams.status"
          placeholder="请选择状态"
          clearable
          style="width: 200px"
        >
          <el-option
            v-for="dict in thesis_transaction_status"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="交易时间">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 240px"
        />
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

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div v-for="stat in stats" :key="stat.key" class="stat-card glass-card">
        <div class="stat-content">
          <div class="stat-icon" :style="{ background: stat.gradient }">
            <component :is="stat.icon" class="w-8 h-8" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="action-bar">
      <el-button @click="handleExport" class="modern-btn-outline" v-hasPermi="['thesis:transaction:export']">
        <Download class="w-4 h-4 mr-2" />
        导出记录
      </el-button>
    </div>

    <!-- 交易记录列表 -->
    <div class="table-section glass-card">
    <el-table 
      v-loading="loading" 
      :data="transactionList" 
      @row-click="handleDetail"
      class="modern-table"
      :header-cell-style="{ background: 'transparent', color: '#1e293b', fontWeight: '600' }"
    >
      <el-table-column label="交易流水号" prop="transactionNo" width="200" />
      <el-table-column label="订单号" prop="orderNo" width="180" />
      <el-table-column label="支付渠道" prop="channel" width="120">
        <template #default="scope">
          <div class="channel-info">
            <el-icon :color="getChannelColor(scope.row.channel)">
              <component :is="getChannelIcon(scope.row.channel)" />
            </el-icon>
            <span>{{ getChannelLabel(scope.row.channel) }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="交易金额" prop="amount" width="120">
        <template #default="scope">
          <span class="amount">¥{{ scope.row.amount }}</span>
        </template>
      </el-table-column>
      <el-table-column label="手续费" prop="fee" width="100">
        <template #default="scope">
          <span class="fee">¥{{ scope.row.fee || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column label="实收金额" prop="actualAmount" width="120">
        <template #default="scope">
          <span class="actual-amount">¥{{ scope.row.actualAmount }}</span>
        </template>
      </el-table-column>
      <el-table-column label="交易状态" prop="status" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusLabel(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="第三方流水号" prop="thirdPartyNo" min-width="200" show-overflow-tooltip />
      <el-table-column label="交易时间" prop="transactionTime" width="160" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button
            link
            type="primary"
            icon="View"
            @click.stop="handleDetail(scope.row)"
            v-hasPermi="['thesis:transaction:query']"
          >详情</el-button>
          <el-button
            link
            type="success"
            icon="Refresh"
            @click.stop="handleSync(scope.row)"
            v-hasPermi="['thesis:transaction:sync']"
            v-if="scope.row.status === 'pending'"
          >同步</el-button>
        </template>
      </el-table-column>
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

    <!-- 交易详情对话框 -->
    <el-dialog title="交易详情" v-model="detailVisible" width="800px" append-to-body>
      <el-descriptions :column="2" border v-if="currentTransaction">
        <el-descriptions-item label="交易流水号" :span="2">
          {{ currentTransaction.transactionNo }}
        </el-descriptions-item>
        <el-descriptions-item label="订单号">
          {{ currentTransaction.orderNo }}
        </el-descriptions-item>
        <el-descriptions-item label="支付渠道">
          <div class="channel-info">
            <el-icon :color="getChannelColor(currentTransaction.channel)">
              <component :is="getChannelIcon(currentTransaction.channel)" />
            </el-icon>
            <span>{{ getChannelLabel(currentTransaction.channel) }}</span>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="交易金额">
          <span class="amount-large">¥{{ currentTransaction.amount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="手续费">
          ¥{{ currentTransaction.fee || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="实收金额">
          <span class="actual-amount-large">¥{{ currentTransaction.actualAmount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="交易状态">
          <el-tag :type="getStatusType(currentTransaction.status)">
            {{ getStatusLabel(currentTransaction.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="第三方流水号" :span="2">
          {{ currentTransaction.thirdPartyNo || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="交易时间">
          {{ currentTransaction.transactionTime }}
        </el-descriptions-item>
        <el-descriptions-item label="完成时间">
          {{ currentTransaction.completedTime || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="回调数据" :span="2">
          <el-input
            v-model="currentTransaction.callbackData"
            type="textarea"
            :rows="5"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentTransaction.remark || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup name="TransactionList">
import { ref, reactive, onMounted, getCurrentInstance } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, RefreshCw, Download, Wallet, Banknote, CreditCard, TrendingUp } from 'lucide-vue-next'
import { listTransaction, getTransaction, syncTransaction, getTransactionStats } from '@/api/thesis/payment'
import { download } from '@/utils/request'

const { proxy } = getCurrentInstance()
const { thesis_payment_channel, thesis_transaction_status } = proxy.useDict(
  'thesis_payment_channel',
  'thesis_transaction_status'
)

const transactionList = ref([])
const loading = ref(true)
const showSearch = ref(true)
const total = ref(0)
const detailVisible = ref(false)
const currentTransaction = ref(null)
const dateRange = ref([])

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  transactionNo: null,
  orderNo: null,
  channel: null,
  status: null,
  startTime: null,
  endTime: null
})

const stats = ref([
  { key: 'total', label: '总交易额', value: '¥0', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', icon: TrendingUp },
  { key: 'success', label: '成功交易', value: '¥0', gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', icon: Banknote },
  { key: 'pending', label: '处理中', value: '¥0', gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', icon: Wallet },
  { key: 'fee', label: '总手续费', value: '¥0', gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', icon: CreditCard }
])

// 获取列表
const getList = async () => {
  loading.value = true
  try {
    // 处理日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      queryParams.startTime = dateRange.value[0]
      queryParams.endTime = dateRange.value[1]
    } else {
      queryParams.startTime = null
      queryParams.endTime = null
    }
    
    const res = await listTransaction(queryParams)
    transactionList.value = res.rows
    total.value = res.total
  } finally {
    loading.value = false
  }
}

// 获取统计
const getStats = async () => {
  try {
    const res = await getTransactionStats()
    stats.value[0].value = `¥${res.data.total || 0}`
    stats.value[1].value = `¥${res.data.success || 0}`
    stats.value[2].value = `¥${res.data.pending || 0}`
    stats.value[3].value = `¥${res.data.fee || 0}`
  } catch (error) {
    console.error('获取统计失败', error)
  }
}

// 搜索
const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

// 重置
const resetQuery = () => {
  dateRange.value = []
  proxy.resetForm('queryRef')
  handleQuery()
}

// 查看详情
const handleDetail = async (row) => {
  try {
    const res = await getTransaction(row.transactionId)
    currentTransaction.value = res.data
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('获取交易详情失败')
  }
}

// 同步交易状态
const handleSync = async (row) => {
  try {
    await syncTransaction(row.transactionId)
    ElMessage.success('同步成功')
    getList()
    getStats()
  } catch (error) {
    ElMessage.error('同步失败')
  }
}

// 导出
const handleExport = () => {
  const params = { ...queryParams }
  if (dateRange.value && dateRange.value.length === 2) {
    params.startTime = dateRange.value[0]
    params.endTime = dateRange.value[1]
  }
  download('/thesis/transaction/export', params, '交易记录.xlsx')
}

// 获取渠道图标
const getChannelIcon = (channel) => {
  const iconMap = {
    'alipay': Wallet,
    'wechat': Money,
    'pingpp': CreditCard
  }
  return iconMap[channel] || CreditCard
}

// 获取渠道颜色
const getChannelColor = (channel) => {
  const colorMap = {
    'alipay': '#1677ff',
    'wechat': '#07c160',
    'pingpp': '#ff6b6b'
  }
  return colorMap[channel] || '#8c8c8c'
}

// 获取渠道标签
const getChannelLabel = (channel) => {
  if (!channel) return ''
  const item = thesis_payment_channel.value.find(d => d.value === channel)
  return item ? item.label : channel
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'success': 'success',
    'failed': 'danger',
    'cancelled': 'info'
  }
  return typeMap[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labelMap = {
    'pending': '处理中',
    'success': '成功',
    'failed': '失败',
    'cancelled': '已取消'
  }
  return labelMap[status] || status
}

onMounted(() => {
  getList()
  getStats()
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

.modern-btn-outline {
  @extend .modern-btn;
  background: transparent;
  border: 2px solid white;
  color: white;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  }
  
  .stat-content {
    display: flex;
    align-items: center;
    gap: 1rem;
    
    .stat-icon {
      width: 64px;
      height: 64px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stat-info {
      flex: 1;
      
      .stat-value {
        font-size: 1.75rem;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 0.25rem;
      }
      
      .stat-label {
        font-size: 0.875rem;
        color: #64748b;
      }
    }
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
        cursor: pointer;
        
        &:hover {
          background: rgba(99, 102, 241, 0.05);
          transform: scale(1.01);
        }
      }
    }
  }
}

.pagination-wrapper {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.amount {
  font-size: 16px;
  font-weight: bold;
  color: #f5222d;
}

.amount-large {
  font-size: 20px;
  font-weight: bold;
  color: #f5222d;
}

.fee {
  color: #faad14;
}

.actual-amount {
  font-size: 16px;
  font-weight: bold;
  color: #52c41a;
}

.actual-amount-large {
  font-size: 20px;
  font-weight: bold;
  color: #52c41a;
}
</style>
