<template>
  <div class="modern-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <Crown :size="32" class="title-icon" />
          会员套餐
        </h1>
        <p class="page-subtitle">选择适合您的套餐，开启高效论文创作之旅</p>
      </div>
    </div>

    <!-- 套餐卡片 -->
    <div v-loading="loading" class="packages-grid">
      <div
        v-for="pkg in packageList"
        :key="pkg.packageId"
        class="package-card glass-card"
        :class="{ 'recommended': pkg.isRecommended === '1' }"
      >
        <!-- 推荐标签 -->
        <div v-if="pkg.isRecommended === '1'" class="recommended-badge">
          <Star :size="14" />
          <span>{{ pkg.badge || '推荐' }}</span>
        </div>

        <!-- 套餐头部 -->
        <div class="package-header">
          <div class="package-icon">
            <Zap v-if="pkg.packageName.includes('基础')" :size="32" />
            <Rocket v-else-if="pkg.packageName.includes('专业')" :size="32" />
            <Crown v-else :size="32" />
          </div>
          <h3 class="package-name">{{ pkg.packageName }}</h3>
          <p class="package-desc">{{ pkg.packageDesc }}</p>
        </div>

        <!-- 价格 -->
        <div class="package-price">
          <div class="price-main">
            <span class="currency">¥</span>
            <span class="amount">{{ pkg.price }}</span>
          </div>
          <div class="price-period">/ {{ pkg.durationDays }} 天</div>
        </div>

        <!-- 配额信息 -->
        <div class="package-quotas">
          <div class="quota-item">
            <div class="quota-icon">
              <FileText :size="20" />
            </div>
            <div class="quota-info">
              <span class="quota-label">字数配额</span>
              <span class="quota-value">
                {{ pkg.wordQuota === -1 ? '无限制' : pkg.wordQuota.toLocaleString() + ' 字' }}
              </span>
            </div>
          </div>
          <div class="quota-item">
            <div class="quota-icon">
              <Repeat :size="20" />
            </div>
            <div class="quota-info">
              <span class="quota-label">使用次数</span>
              <span class="quota-value">
                {{ pkg.usageQuota === -1 ? '无限制' : pkg.usageQuota + ' 次' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 功能列表 -->
        <div class="package-features">
          <div
            v-for="(feature, index) in parseFeatures(pkg.features)"
            :key="index"
            class="feature-item"
            :class="{ disabled: !feature.enabled }"
          >
            <Check v-if="feature.enabled" :size="16" class="feature-icon enabled" />
            <X v-else :size="16" class="feature-icon disabled" />
            <span>{{ feature.label }}</span>
          </div>
        </div>

        <!-- 购买按钮 -->
        <button
          class="btn-purchase"
          :class="{ 'btn-recommended': pkg.isRecommended === '1' }"
          @click="handlePurchase(pkg)"
        >
          <ShoppingCart :size="18" />
          <span>立即购买</span>
        </button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && packageList.length === 0" class="empty-state">
      <Crown :size="64" class="empty-icon" />
      <h3 class="empty-title">暂无套餐</h3>
      <p class="empty-desc">敬请期待更多套餐上线</p>
    </div>

    <!-- 支付方式选择对话框 -->
    <el-dialog
      v-model="paymentDialogVisible"
      title="选择支付方式"
      width="500px"
      :close-on-click-modal="false"
      class="payment-dialog"
    >
      <div v-if="selectedPackage" class="dialog-content">
        <!-- 套餐信息 -->
        <div class="selected-package">
          <div class="package-summary">
            <h4>{{ selectedPackage.packageName }}</h4>
            <div class="package-price-summary">
              <span class="price-label">支付金额：</span>
              <span class="price-amount">¥{{ selectedPackage.price }}</span>
            </div>
          </div>
        </div>

        <!-- 支付渠道选择 -->
        <div class="payment-channels">
          <h5 class="channels-title">选择支付方式</h5>
          <div class="channels-list">
            <div
              v-for="channel in paymentChannels"
              :key="channel.code"
              class="channel-option"
              :class="{ active: selectedChannel === channel.code }"
              @click="selectedChannel = channel.code"
            >
              <div class="channel-radio">
                <div class="radio-dot"></div>
              </div>
              <component :is="channel.icon" :size="24" class="channel-icon" />
              <span class="channel-name">{{ channel.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <button @click="paymentDialogVisible = false" class="btn-cancel">取消</button>
          <button
            @click="handleConfirmPurchase"
            :disabled="creatingOrder || !selectedChannel"
            class="btn-confirm"
          >
            <ShoppingCart :size="18" />
            <span>{{ creatingOrder ? '创建中...' : '确认购买' }}</span>
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="PackageModern">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  Crown, Star, Zap, Rocket, FileText, Repeat, Check, X, ShoppingCart, Wallet, CreditCard
} from 'lucide-vue-next'
import { listPackage } from '@/api/thesis/member'
import { createOrder } from '@/api/thesis/order'
import { listPaymentConfig } from '@/api/thesis/payment'

const router = useRouter()
const packageList = ref([])
const loading = ref(true)
const selectedPackage = ref(null)
const paymentDialogVisible = ref(false)
const paymentChannels = ref([])
const selectedChannel = ref('mock')
const creatingOrder = ref(false)

const getList = async () => {
  loading.value = true
  try {
    const res = await listPackage({ pageNum: 1, pageSize: 100 })
    packageList.value = res.rows
  } finally {
    loading.value = false
  }
}

const getPaymentChannels = async () => {
  try {
    const res = await listPaymentConfig()
    paymentChannels.value = res.data
      .filter(config => config.is_enabled === '1')
      .map(config => ({
        code: config.provider_type,
        name: config.provider_name,
        icon: getChannelIcon(config.provider_type)
      }))
  } catch (error) {
    console.error('获取支付渠道失败', error)
  }
}

const getChannelIcon = (type) => {
  const icons = {
    'alipay': Wallet,
    'wechat': Wallet,
    'pingpp': CreditCard,
    'mock': Zap
  }
  return icons[type] || CreditCard
}

const handleConfirmPurchase = async () => {
  if (!selectedChannel.value) {
    ElMessage.warning('请选择支付方式')
    return
  }

  creatingOrder.value = true
  try {
    const res = await createOrder({
      orderType: 'package',
      itemId: selectedPackage.value.packageId,
      amount: selectedPackage.value.price,
      paymentMethod: selectedChannel.value
    })

    ElMessage.success('订单创建成功')
    paymentDialogVisible.value = false

    // 跳转到订单列表
    router.push('/thesis/order')
  } catch (error) {
    ElMessage.error('创建订单失败: ' + (error.message || '未知错误'))
  } finally {
    creatingOrder.value = false
  }
}

const parseFeatures = (featuresStr) => {
  if (!featuresStr) return []
  try {
    const features = JSON.parse(featuresStr)
    return Object.entries(features).map(([key, value]) => ({
      label: getFeatureLabel(key),
      enabled: value === true || value === '1' || value === 1
    }))
  } catch (e) {
    return []
  }
}

const getFeatureLabel = (key) => {
  const labels = {
    'ai_writing': 'AI 智能写作',
    'template': '论文模板',
    'export': '导出功能',
    'priority_support': '优先支持',
    'advanced_ai': '高级 AI 模型',
    'unlimited_revisions': '无限修改',
    'plagiarism_check': '查重检测',
    'format_check': '格式检查'
  }
  return labels[key] || key
}

const handlePurchase = (pkg) => {
  selectedPackage.value = pkg
  paymentDialogVisible.value = true
}

onMounted(() => {
  getList()
  getPaymentChannels()
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
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  font-family: 'Poppins', sans-serif;
  font-size: 2.5rem;
  font-weight: 700;
  color: #1E1B4B;
  margin: 0 0 0.75rem 0;
}

.title-icon {
  color: #6366F1;
}

.page-subtitle {
  font-size: 1.125rem;
  color: #64748B;
  margin: 0;
}

.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
  transition: all 0.3s ease;
}

.package-card {
  position: relative;
  padding: 2rem;
  border-radius: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.package-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px -5px rgba(99, 102, 241, 0.3);
}

.package-card.recommended {
  border: 2px solid #6366F1;
  box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.25);
}

.package-card.recommended:hover {
  box-shadow: 0 20px 40px -5px rgba(99, 102, 241, 0.4);
}

.recommended-badge {
  position: absolute;
  top: -12px;
  right: 2rem;
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
  color: white;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.package-header {
  text-align: center;
}

.package-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  border-radius: 1rem;
  background: linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366F1;
}

.package-name {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1E1B4B;
  margin: 0 0 0.5rem 0;
}

.package-desc {
  font-size: 0.875rem;
  color: #64748B;
  margin: 0;
  line-height: 1.5;
}

.package-price {
  text-align: center;
  padding: 1.5rem 0;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}

.price-main {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 0.25rem;
}

.currency {
  font-size: 1.5rem;
  font-weight: 600;
  color: #6366F1;
}

.amount {
  font-family: 'Poppins', sans-serif;
  font-size: 3rem;
  font-weight: 700;
  color: #6366F1;
  line-height: 1;
}

.price-period {
  font-size: 0.875rem;
  color: #64748B;
  margin-top: 0.5rem;
}

.package-quotas {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.quota-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(99, 102, 241, 0.05);
  border-radius: 0.75rem;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.quota-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366F1;
}

.quota-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.quota-label {
  font-size: 0.75rem;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.quota-value {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #1E1B4B;
}

.package-features {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #1E1B4B;
}

.feature-item.disabled {
  color: #94A3B8;
}

.feature-icon {
  flex-shrink: 0;
}

.feature-icon.enabled {
  color: #10B981;
}

.feature-icon.disabled {
  color: #CBD5E1;
}

.btn-purchase {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 1rem;
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
  border: 2px solid rgba(99, 102, 241, 0.3);
  border-radius: 0.75rem;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-purchase:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: #6366F1;
  transform: translateY(-2px);
}

.btn-recommended {
  background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.btn-recommended:hover {
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
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

@media (max-width: 768px) {
  .modern-container {
    padding: 1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .packages-grid {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 支付对话框样式 */
:deep(.payment-dialog) {
  .el-dialog__header {
    background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
    padding: 1.5rem 2rem;
    margin: 0;
  }

  .el-dialog__title {
    color: white;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
  }

  .el-dialog__headerbtn .el-dialog__close {
    color: white;
  }

  .el-dialog__body {
    padding: 2rem;
  }

  .el-dialog__footer {
    padding: 1.5rem 2rem;
    border-top: 1px solid rgba(99, 102, 241, 0.1);
  }
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.selected-package {
  padding: 1.5rem;
  background: rgba(99, 102, 241, 0.05);
  border-radius: 1rem;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.package-summary h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1E1B4B;
  margin: 0 0 1rem 0;
}

.package-price-summary {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.price-label {
  font-size: 0.875rem;
  color: #64748B;
}

.price-amount {
  font-family: 'Poppins', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: #6366F1;
}

.payment-channels {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.channels-title {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #1E1B4B;
  margin: 0;
}

.channels-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.channel-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 2px solid rgba(99, 102, 241, 0.1);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.channel-option:hover {
  border-color: rgba(99, 102, 241, 0.3);
  background: rgba(99, 102, 241, 0.02);
}

.channel-option.active {
  border-color: #6366F1;
  background: rgba(99, 102, 241, 0.05);
}

.channel-radio {
  width: 20px;
  height: 20px;
  border: 2px solid #CBD5E1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.channel-option.active .channel-radio {
  border-color: #6366F1;
}

.radio-dot {
  width: 10px;
  height: 10px;
  background: #6366F1;
  border-radius: 50%;
  opacity: 0;
  transform: scale(0);
  transition: all 0.3s ease;
}

.channel-option.active .radio-dot {
  opacity: 1;
  transform: scale(1);
}

.channel-icon {
  color: #6366F1;
}

.channel-name {
  flex: 1;
  font-weight: 500;
  color: #1E1B4B;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel,
.btn-confirm {
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-cancel {
  background: white;
  color: #64748B;
  border: 1px solid #E2E8F0;
}

.btn-cancel:hover {
  background: #F8FAFC;
}

.btn-confirm {
  background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.btn-confirm:hover:not(:disabled) {
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
  transform: translateY(-2px);
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
