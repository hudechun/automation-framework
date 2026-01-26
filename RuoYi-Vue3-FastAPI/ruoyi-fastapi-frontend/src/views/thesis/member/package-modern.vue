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
  </div>
</template>

<script setup name="PackageModern">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Crown, Star, Zap, Rocket, FileText, Repeat, Check, X, ShoppingCart
} from 'lucide-vue-next'
import { listPackage } from '@/api/thesis/member'

const packageList = ref([])
const loading = ref(true)

const getList = async () => {
  loading.value = true
  try {
    const res = await listPackage({ pageNum: 1, pageSize: 100 })
    packageList.value = res.rows
  } finally {
    loading.value = false
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
  ElMessage.info('购买功能开发中')
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
</style>
