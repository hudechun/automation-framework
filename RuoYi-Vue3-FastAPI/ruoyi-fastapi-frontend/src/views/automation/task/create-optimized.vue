<template>
  <div class="task-create-wrapper">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          创建自动化任务
        </h1>
        <p class="page-subtitle">通过简单的步骤配置您的自动化任务</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="saveDraft" :disabled="loading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
          </svg>
          保存草稿
        </button>
        <button class="btn-ghost" @click="handleCancel">取消</button>
      </div>
    </header>

    <!-- 步骤指示器 -->
    <div class="steps-indicator">
      <div 
        v-for="(step, index) in steps" 
        :key="index"
        class="step-item"
        :class="{ 
          'step-active': currentStep === index,
          'step-completed': currentStep > index 
        }"
      >
        <div class="step-circle">
          <svg v-if="currentStep > index" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="step-content">
          <div class="step-title">{{ step.title }}</div>
          <div class="step-desc">{{ step.description }}</div>
        </div>
        <div v-if="index < steps.length - 1" class="step-line"></div>
      </div>
    </div>

    <!-- 表单区域 -->
    <div class="form-wrapper">
      <form @submit.prevent="handleSubmit">
        
        <!-- 步骤1: 基本信息 -->
        <transition name="fade" mode="out-in">
          <div v-if="currentStep === 0" class="step-panel" key="step-0">
            <div class="panel-header">
              <h2 class="panel-title">基本信息</h2>
              <p class="panel-desc">填写任务的基本信息</p>
            </div>

            <div class="form-group">
              <label for="task-name" class="form-label">
                任务名称 <span class="required">*</span>
              </label>
              <input
                id="task-name"
                v-model="formData.name"
                type="text"
                class="form-input"
                placeholder="例如：京东价格监控"
                maxlength="50"
                required
                @blur="validateField('name')"
                :class="{ 'input-error': errors.name }"
              />
              <div v-if="errors.name" class="error-message">{{ errors.name }}</div>
              <div class="input-hint">{{ formData.name.length }}/50</div>
            </div>

            <div class="form-group">
              <label for="task-desc" class="form-label">任务描述</label>
              <textarea
                id="task-desc"
                v-model="formData.description"
                class="form-textarea"
                rows="4"
                placeholder="描述任务的目的和功能，例如：每小时检查京东iPhone价格变化"
                maxlength="200"
              ></textarea>
              <div class="input-hint">{{ formData.description.length }}/200</div>
            </div>

            <div class="form-group">
              <label class="form-label">任务分类</label>
              <div class="radio-group">
                <label class="radio-card" :class="{ 'radio-selected': formData.category === 'scraping' }">
                  <input type="radio" v-model="formData.category" value="scraping" />
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>数据爬取</span>
                </label>
                <label class="radio-card" :class="{ 'radio-selected': formData.category === 'monitoring' }">
                  <input type="radio" v-model="formData.category" value="monitoring" />
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <span>价格监控</span>
                </label>
                <label class="radio-card" :class="{ 'radio-selected': formData.category === 'automation' }">
                  <input type="radio" v-model="formData.category" value="automation" />
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>流程自动化</span>
                </label>
              </div>
            </div>
          </div>
        </transition>

        <!-- 步骤2: 执行模式 -->
        <transition name="fade" mode="out-in">
          <div v-if="currentStep === 1" class="step-panel" key="step-1">
            <div class="panel-header">
              <h2 class="panel-title">选择执行模式</h2>
              <p class="panel-desc">根据您的需求选择合适的执行方式</p>
            </div>

            <div class="mode-cards">
              <!-- 有头模式 -->
              <div 
                class="mode-card" 
                :class="{ 'mode-selected': formData.executionMode === 'headed' }"
                @click="selectMode('headed')"
              >
                <div class="mode-icon mode-icon-headed">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 class="mode-title">有头模式（本地执行）</h3>
                <p class="mode-desc">在您的电脑上运行，可以实时查看浏览器操作过程</p>
                
                <div class="mode-features">
                  <div class="feature-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>实时查看执行过程</span>
                  </div>
                  <div class="feature-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>方便调试和录制</span>
                  </div>
                  <div class="feature-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>需要下载客户端</span>
                  </div>
                </div>

                <div v-if="formData.executionMode === 'headed'" class="client-status">
                  <div v-if="clientConnected" class="status-connected">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>客户端已连接</span>
                  </div>
                  <div v-else class="status-disconnected">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>客户端未连接</span>
                    <button class="btn-link" @click.stop="downloadClient">下载客户端</button>
                  </div>
                </div>
              </div>

              <!-- 无头模式 -->
              <div 
                class="mode-card" 
                :class="{ 'mode-selected': formData.executionMode === 'headless' }"
                @click="selectMode('headless')"
              >
                <div class="mode-icon mode-icon-headless">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                  </svg>
                </div>
                <h3 class="mode-title">无头模式（服务器执行）</h3>
                <p class="mode-desc">在服务器后台运行，无需下载客户端，自动执行</p>
                
                <div class="mode-features">
                  <div class="feature-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>无需下载客户端</span>
                  </div>
                  <div class="feature-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>24/7 自动执行</span>
                  </div>
                  <div class="feature-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>节省本地资源</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition>

        <!-- 步骤3: 任务配置 -->
        <transition name="fade" mode="out-in">
          <div v-if="currentStep === 2" class="step-panel" key="step-2">
            <div class="panel-header">
              <h2 class="panel-title">任务配置</h2>
              <p class="panel-desc">配置任务的详细参数</p>
            </div>

            <div class="form-group">
              <label for="task-url" class="form-label">
                目标网址 <span class="required">*</span>
              </label>
              <input
                id="task-url"
                v-model="formData.url"
                type="url"
                class="form-input"
                placeholder="https://example.com"
                required
                @blur="validateField('url')"
                :class="{ 'input-error': errors.url }"
              />
              <div v-if="errors.url" class="error-message">{{ errors.url }}</div>
            </div>

            <div class="form-group">
              <label class="form-label">执行频率</label>
              <div class="frequency-options">
                <label class="frequency-option" :class="{ 'option-selected': formData.frequency === 'once' }">
                  <input type="radio" v-model="formData.frequency" value="once" />
                  <span>仅执行一次</span>
                </label>
                <label class="frequency-option" :class="{ 'option-selected': formData.frequency === 'hourly' }">
                  <input type="radio" v-model="formData.frequency" value="hourly" />
                  <span>每小时</span>
                </label>
                <label class="frequency-option" :class="{ 'option-selected': formData.frequency === 'daily' }">
                  <input type="radio" v-model="formData.frequency" value="daily" />
                  <span>每天</span>
                </label>
                <label class="frequency-option" :class="{ 'option-selected': formData.frequency === 'weekly' }">
                  <input type="radio" v-model="formData.frequency" value="weekly" />
                  <span>每周</span>
                </label>
              </div>
            </div>
          </div>
        </transition>

        <!-- 步骤4: 确认创建 -->
        <transition name="fade" mode="out-in">
          <div v-if="currentStep === 3" class="step-panel" key="step-3">
            <div class="panel-header">
              <h2 class="panel-title">确认信息</h2>
              <p class="panel-desc">请检查任务配置是否正确</p>
            </div>

            <div class="summary-card">
              <div class="summary-item">
                <div class="summary-label">任务名称</div>
                <div class="summary-value">{{ formData.name }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">任务描述</div>
                <div class="summary-value">{{ formData.description || '无' }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">任务分类</div>
                <div class="summary-value">{{ getCategoryLabel(formData.category) }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">执行模式</div>
                <div class="summary-value">{{ getModeLabel(formData.executionMode) }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">目标网址</div>
                <div class="summary-value">{{ formData.url }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">执行频率</div>
                <div class="summary-value">{{ getFrequencyLabel(formData.frequency) }}</div>
              </div>
            </div>
          </div>
        </transition>

        <!-- 底部按钮 -->
        <div class="form-actions">
          <button 
            v-if="currentStep > 0" 
            type="button" 
            class="btn-secondary"
            @click="prevStep"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            上一步
          </button>
          
          <button 
            v-if="currentStep < steps.length - 1" 
            type="button" 
            class="btn-primary"
            @click="nextStep"
            :disabled="!canProceed"
          >
            下一步
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
          
          <button 
            v-if="currentStep === steps.length - 1" 
            type="submit" 
            class="btn-primary"
            :disabled="loading"
          >
            <svg v-if="!loading" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else class="animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            {{ loading ? '创建中...' : '创建任务' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>


<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { addTask } from '@/api/automation/task'

const router = useRouter()

// 步骤定义
const steps = [
  { title: '基本信息', description: '任务名称和描述' },
  { title: '执行模式', description: '选择执行方式' },
  { title: '任务配置', description: '配置任务详情' },
  { title: '确认创建', description: '检查并创建' }
]

// 当前步骤
const currentStep = ref(0)

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  category: 'scraping',
  executionMode: 'headless',
  url: '',
  frequency: 'once'
})

// 表单错误
const errors = reactive({
  name: '',
  url: ''
})

// 加载状态
const loading = ref(false)

// 客户端连接状态
const clientConnected = ref(false)

// 检查客户端连接状态
const checkClientStatus = () => {
  // TODO: 实际实现时通过 WebSocket 检查客户端状态
  // 这里模拟检查
  clientConnected.value = Math.random() > 0.5
}

// 定时检查客户端状态
let statusCheckInterval = null

onMounted(() => {
  // 每5秒检查一次客户端状态
  checkClientStatus()
  statusCheckInterval = setInterval(checkClientStatus, 5000)
  
  // 尝试从 localStorage 恢复草稿
  const draft = localStorage.getItem('task-draft')
  if (draft) {
    try {
      const draftData = JSON.parse(draft)
      Object.assign(formData, draftData)
    } catch (e) {
      console.error('Failed to load draft:', e)
    }
  }
})

onBeforeUnmount(() => {
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }
})

// 字段验证
const validateField = (field) => {
  errors[field] = ''
  
  if (field === 'name') {
    if (!formData.name.trim()) {
      errors.name = '请输入任务名称'
      return false
    }
    if (formData.name.length < 2) {
      errors.name = '任务名称至少2个字符'
      return false
    }
  }
  
  if (field === 'url') {
    if (!formData.url.trim()) {
      errors.url = '请输入目标网址'
      return false
    }
    try {
      new URL(formData.url)
    } catch {
      errors.url = '请输入有效的网址'
      return false
    }
  }
  
  return true
}

// 检查是否可以进入下一步
const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return formData.name.trim().length >= 2
    case 1:
      return formData.executionMode && 
             (formData.executionMode === 'headless' || clientConnected.value)
    case 2:
      return formData.url.trim() && formData.frequency
    default:
      return true
  }
})

// 下一步
const nextStep = () => {
  if (currentStep.value < steps.length - 1 && canProceed.value) {
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 选择执行模式
const selectMode = (mode) => {
  formData.executionMode = mode
}

// 保存草稿
const saveDraft = () => {
  localStorage.setItem('task-draft', JSON.stringify(formData))
  ElMessage.success('草稿已保存')
}

// 下载客户端
const downloadClient = () => {
  // TODO: 实际下载链接
  window.open('/downloads/automation-client.exe', '_blank')
}

// 取消
const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消创建任务吗？未保存的数据将丢失', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    router.back()
  } catch {
    // 用户取消
  }
}

// 提交表单
const handleSubmit = async () => {
  // 验证所有字段
  if (!validateField('name') || !validateField('url')) {
    ElMessage.error('请检查表单填写是否正确')
    return
  }
  
  loading.value = true
  
  try {
    await addTask(formData)
    ElMessage.success('任务创建成功')
    localStorage.removeItem('task-draft')
    router.push('/automation/task')
  } catch (error) {
    ElMessage.error(error.message || '创建任务失败')
  } finally {
    loading.value = false
  }
}

// 获取分类标签
const getCategoryLabel = (category) => {
  const labels = {
    scraping: '数据爬取',
    monitoring: '价格监控',
    automation: '流程自动化'
  }
  return labels[category] || category
}

// 获取模式标签
const getModeLabel = (mode) => {
  const labels = {
    headed: '有头模式（本地执行）',
    headless: '无头模式（服务器执行）'
  }
  return labels[mode] || mode
}

// 获取频率标签
const getFrequencyLabel = (frequency) => {
  const labels = {
    once: '仅执行一次',
    hourly: '每小时',
    daily: '每天',
    weekly: '每周'
  }
  return labels[frequency] || frequency
}
</script>


<style scoped>
/* 导入 Fira Code 和 Fira Sans 字体 */
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

/* 深色主题配色 - 基于 ui-ux-pro-max 建议 */
:root {
  --color-primary: #7C3AED;
  --color-primary-hover: #6D28D9;
  --color-secondary: #A78BFA;
  --color-cta: #F97316;
  --color-cta-hover: #EA580C;
  
  --color-bg-dark: #0F172A;
  --color-bg-card: #1E293B;
  --color-bg-hover: #334155;
  
  --color-text-primary: #F1F5F9;
  --color-text-secondary: #CBD5E1;
  --color-text-muted: #94A3B8;
  
  --color-border: #334155;
  --color-border-light: #475569;
  
  --color-success: #10B981;
  --color-error: #EF4444;
  --color-warning: #F59E0B;
  
  --font-sans: 'Fira Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'Fira Code', 'Courier New', monospace;
  
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* 全局容器 */
.task-create-wrapper {
  min-height: 100vh;
  background: var(--color-bg-dark);
  color: var(--color-text-primary);
  font-family: var(--font-sans);
  padding: 2rem;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--color-border);
}

.header-content {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.title-icon {
  width: 2rem;
  height: 2rem;
  color: var(--color-primary);
}

.page-subtitle {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* 按钮样式 */
button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: all var(--transition-base);
  outline: none;
}

button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

button svg {
  width: 1.25rem;
  height: 1.25rem;
  stroke-width: 2;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-bg-hover);
  border-color: var(--color-border-light);
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}

.btn-ghost:hover {
  background: var(--color-bg-card);
  color: var(--color-text-primary);
}

.btn-link {
  background: none;
  color: var(--color-primary);
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.btn-link:hover {
  color: var(--color-secondary);
  text-decoration: underline;
}

/* 步骤指示器 */
.steps-indicator {
  display: flex;
  justify-content: space-between;
  margin-bottom: 3rem;
  position: relative;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  flex: 1;
  position: relative;
}

.step-circle {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: var(--color-bg-card);
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--color-text-muted);
  transition: all var(--transition-base);
  flex-shrink: 0;
}

.step-circle svg {
  width: 1.5rem;
  height: 1.5rem;
}

.step-active .step-circle {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  box-shadow: 0 0 20px rgba(124, 58, 237, 0.4);
}

.step-completed .step-circle {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
}

.step-content {
  flex: 1;
  padding-top: 0.25rem;
}

.step-title {
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.step-active .step-title {
  color: var(--color-primary);
}

.step-desc {
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.step-line {
  position: absolute;
  top: 1.5rem;
  left: calc(100% - 1rem);
  width: calc(100% - 4rem);
  height: 2px;
  background: var(--color-border);
  transition: background var(--transition-base);
}

.step-completed .step-line {
  background: var(--color-success);
}

/* 表单区域 */
.form-wrapper {
  max-width: 56rem;
  margin: 0 auto;
}

.step-panel {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
}

.panel-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.panel-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.panel-desc {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 表单组 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.required {
  color: var(--color-error);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--color-bg-dark);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  color: var(--color-text-primary);
  font-family: var(--font-sans);
  font-size: 0.875rem;
  transition: all var(--transition-base);
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: var(--color-text-muted);
}

.input-error {
  border-color: var(--color-error);
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.error-message {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-error);
}

.input-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-align: right;
}

.form-textarea {
  resize: vertical;
  min-height: 6rem;
}

/* 单选卡片组 */
.radio-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.radio-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 1rem;
  background: var(--color-bg-dark);
  border: 2px solid var(--color-border);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all var(--transition-base);
}

.radio-card input[type="radio"] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.radio-card svg {
  width: 2rem;
  height: 2rem;
  color: var(--color-text-secondary);
  transition: color var(--transition-base);
}

.radio-card span {
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: color var(--transition-base);
}

.radio-card:hover {
  border-color: var(--color-primary);
  background: rgba(124, 58, 237, 0.05);
}

.radio-selected {
  border-color: var(--color-primary);
  background: rgba(124, 58, 237, 0.1);
}

.radio-selected svg,
.radio-selected span {
  color: var(--color-primary);
}

/* 执行模式卡片 */
.mode-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.mode-card {
  background: var(--color-bg-dark);
  border: 2px solid var(--color-border);
  border-radius: 1rem;
  padding: 2rem;
  cursor: pointer;
  transition: all var(--transition-base);
}

.mode-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.mode-selected {
  border-color: var(--color-primary);
  background: rgba(124, 58, 237, 0.05);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.mode-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.mode-icon svg {
  width: 2rem;
  height: 2rem;
}

.mode-icon-headed {
  background: rgba(124, 58, 237, 0.1);
  color: var(--color-primary);
}

.mode-icon-headless {
  background: rgba(249, 115, 22, 0.1);
  color: var(--color-cta);
}

.mode-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.mode-desc {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0 0 1.5rem 0;
  line-height: 1.6;
}

.mode-features {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.feature-item svg {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-success);
  flex-shrink: 0;
}

/* 客户端状态 */
.client-status {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.status-connected,
.status-disconnected {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
}

.status-connected {
  color: var(--color-success);
}

.status-connected svg {
  width: 1.5rem;
  height: 1.5rem;
}

.status-disconnected {
  color: var(--color-warning);
  flex-wrap: wrap;
}

.status-disconnected svg {
  width: 1.5rem;
  height: 1.5rem;
}

/* 频率选项 */
.frequency-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
}

.frequency-option {
  position: relative;
  padding: 0.75rem 1rem;
  background: var(--color-bg-dark);
  border: 2px solid var(--color-border);
  border-radius: 0.5rem;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.frequency-option input[type="radio"] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.frequency-option:hover {
  border-color: var(--color-primary);
  background: rgba(124, 58, 237, 0.05);
}

.option-selected {
  border-color: var(--color-primary);
  background: rgba(124, 58, 237, 0.1);
  color: var(--color-primary);
  font-weight: 500;
}

/* 摘要卡片 */
.summary-card {
  background: var(--color-bg-dark);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.summary-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.summary-label {
  font-weight: 500;
  color: var(--color-text-muted);
  font-size: 0.875rem;
  min-width: 6rem;
}

.summary-value {
  flex: 1;
  color: var(--color-text-primary);
  font-weight: 500;
  text-align: right;
  word-break: break-word;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base), transform var(--transition-base);
}

.fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-create-wrapper {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .steps-indicator {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .step-line {
    display: none;
  }
  
  .mode-cards {
    grid-template-columns: 1fr;
  }
  
  .radio-group {
    grid-template-columns: 1fr;
  }
  
  .frequency-options {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .form-actions button {
    width: 100%;
    justify-content: center;
  }
}

/* 无障碍访问 - 减少动画 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  .animate-spin {
    animation: none;
  }
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
  .step-circle,
  .form-input,
  .form-textarea,
  .radio-card,
  .mode-card {
    border-width: 2px;
  }
}
</style>
