<template>
  <div class="modern-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <ShoppingCart :size="32" class="title-icon" />
          我的订单
        </h1>
        <p class="page-subtitle">查看您的购买记录和订单状态</p>
      </div>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="search-bar glass-card">
      <div class="search-input-wrapper">
        <Search :size="20" class="search-icon" />
        <input
          v-model="queryParams.orderNo"
          type="text"
          class="search-input"
          placeholder="搜索订单号..."
          @keyup.enter="handleQuery"
        />
      </div>
      
      <div class="filter-group">
        <select v-model="queryParams.status" class="filter-select" @change="handleQuery">
          <option value="">全部状态</option>
          <option value="pending">待支付</option>
          <option value="paid">已支付</option>
          <option value="cancelled">已取消</option>
        </select>
        
        <button class="btn-secondary" @click="resetQuery">
          <RotateCcw :size="18" />
          <span>重置</span>
        </button>
      </div>
    </div>

    <!-- 订单列表 -->
    <div v-loading="loading" class="orders-list">
      <div
        v-for="order in orderList"
        :key="order.orderId"
        class="order-card glass-card"
      >
        <!-- 订单头部 -->
        <div class="order-header">
          <div class="order-info">
            <span class="order-no">订单号: {{ order.orderNo }}</span>
            <span class="order-time">
              <Clock :size="14" />
              {{ formatDate(order.createTime) }}
            </span>
          </div>
          <span class="order-status" :class="`status-${order.status}`">
            {{ getStatusLabel(order.status) }}
          </span>
        </div>

        <!-- 订单内容 -->
        <div class="order-content">
          <div class="package-info">
            <div class="package-icon">
              <Package :size="32" />
            </div>
            <div class="package-details">
              <h3 class="package-name">{{ order.packageName }}</h3>
              <p class="package-desc">{{ order.packageDesc }}</p>
            </div>
          </div>

          <div class="order-amount">
            <span class="amount-label">订单金额</span>
            <span class="amount-value">¥{{ order.amount }}</span>
          </div>
        </div>

        <!-- 订单操作 -->
        <div class="order-actions">
          <button
            v-if="order.status === 'pending'"
            class="btn-action btn-pay"
            @click="handlePay(order)"
          >
            <CreditCard :size="16" />
            <span>立即支付</span>
          </button>
          <button
            v-if="order.status === 'pending'"
            class="btn-action btn-cancel"
            @click="handleCancel(order)"
          >
            <X :size="16" />
            <span>取消订单</span>
          </button>
          <button
            class="btn-action btn-detail"
            @click="handleDetail(order)"
          >
            <FileText :size="16" />
            <span>订单详情</span>
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && orderList.length === 0" class="empty-state">
        <ShoppingCart :size="64" class="empty-icon" />
        <h3 class="empty-title">还没有订单</h3>
        <p class="empty-desc">购买套餐后，订单将显示在这里</p>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination-wrapper">
      <pagination
        :total="total"
        v-model:page="queryParams.pageNum"
        v-model:limit="queryParams.pageSize"
        @pagination="getList"
      />
    </div>
  </div>
</template>

<script setup name="OrderListModern">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ShoppingCart, Search, RotateCcw, Clock, Package, CreditCard,
  X, FileText
} from 'lucide-vue-next'
import { listOrder, cancelOrder } from '@/api/thesis/order'

const { proxy } = getCurrentInstance()

const orderList = ref([])
const loading = ref(true)
const total = ref(0)

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  orderNo: null,
  status: null
})

const getList = async () => {
  loading.value = true
  try {
    const res = await listOrder(queryParams)
    orderList.value = res.rows
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  queryParams.orderNo = null
  queryParams.status = null
  handleQuery()
}

const handlePay = (order) => {
  ElMessage.info('支付功能开发中')
}

const handleCancel = (order) => {
  ElMessageBox.confirm('确定要取消该订单吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    await cancelOrder(order.orderId)
    ElMessage.success('订单已取消')
    getList()
  })
}

const handleDetail = (order) => {
  ElMessage.info('订单详情功能开发中')
}

const getStatusLabel = (status) => {
  const map = {
    'pending': '待支付',
    'paid': '已支付',
    'cancelled': '已取消',
    'refunded': '已退款'
  }
  return map[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Open+Sans:wght@300;400;500;600;700&display=swap');

.modern-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
  padding: 2rem;
  font-family: 'Open Sans', sans-serif;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-content {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-family: 'Poppins', sans-serif;
  font-size: 2.25rem;
  font-weight: 700;
  color: #1E1B4B;
  margin: 0 0 0.5rem 0;
}

.title-icon {
  color: #6366F1;
}

.page-subtitle {
  font-size: 1rem;
  color: #64748B;
  margin: 0;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  color: #6366F1;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(99, 102, 241, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: #6366F1;
}

.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
  transition: all 0.3s ease;
}

.search-bar {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-input-wrapper {
  flex: 1;
  min-width: 300px;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: #94A3B8;
}

.search-input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 0.75rem;
  font-size: 1rem;
  color: #1E1B4B;
  transition: all 0.3s ease;
  font-family: 'Open Sans', sans-serif;
}

.search-input:focus {
  outline: none;
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: rgba(255, 255, 255, 0.9);
}

.filter-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.filter-select {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 0.75rem;
  font-size: 0.875rem;
  color: #1E1B4B;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Open Sans', sans-serif;
}

.filter-select:focus {
  outline: none;
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.order-card {
  padding: 1.5rem;
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.order-no {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #1E1B4B;
}

.order-time {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: #64748B;
}

.order-status {
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.status-pending {
  background: rgba(245, 158, 11, 0.1);
  color: #D97706;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-paid {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-cancelled {
  background: rgba(148, 163, 184, 0.1);
  color: #475569;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.order-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.package-info {
  display: flex;
  gap: 1rem;
  flex: 1;
}

.package-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 0.75rem;
  background: linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366F1;
}

.package-details {
  flex: 1;
}

.package-name {
  font-family: 'Poppins', sans-serif;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1E1B4B;
  margin: 0 0 0.5rem 0;
}

.package-desc {
  font-size: 0.875rem;
  color: #64748B;
  margin: 0;
}

.order-amount {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.amount-label {
  font-size: 0.875rem;
  color: #64748B;
}

.amount-value {
  font-family: 'Poppins', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: #6366F1;
}

.order-actions {
  display: flex;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-pay {
  background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
}

.btn-pay:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.btn-cancel {
  background: rgba(239, 68, 68, 0.1);
  color: #DC2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.btn-cancel:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: #DC2626;
}

.btn-detail {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.btn-detail:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: #6366F1;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  color: #CBD5E1;
  margin-bottom: 1.5rem;
}

.empty-title {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1E1B4B;
  margin: 0 0 0.5rem 0;
}

.empty-desc {
  font-size: 1rem;
  color: #64748B;
  margin: 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}

@media (max-width: 768px) {
  .modern-container {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.75rem;
  }

  .search-bar {
    flex-direction: column;
  }

  .search-input-wrapper {
    min-width: 100%;
  }

  .order-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .order-amount {
    align-items: flex-start;
  }

  .order-actions {
    flex-wrap: wrap;
  }

  .btn-action {
    flex: 1;
    min-width: calc(50% - 0.375rem);
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
