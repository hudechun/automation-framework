<template>
  <div class="task-create-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon class="title-icon"><Plus /></el-icon>
          创建自动化任务
        </h1>
        <p class="page-subtitle">通过简单的步骤创建您的自动化任务</p>
      </div>
      <div class="header-actions">
        <el-button @click="saveDraft">
          <el-icon><Document /></el-icon>
          保存草稿
        </el-button>
        <el-button @click="handleCancel">取消</el-button>
      </div>
    </div>

    <!-- 步骤导航 -->
    <div class="steps-container">
      <el-steps :active="currentStep" align-center finish-status="success">
        <el-step title="基本信息" description="任务名称和描述">
          <template #icon>
            <el-icon><Edit /></el-icon>
          </template>
        </el-step>
        <el-step title="执行模式" description="选择执行方式">
          <template #icon>
            <el-icon><Setting /></el-icon>
          </template>
        </el-step>
        <el-step title="任务配置" description="配置任务详情">
          <template #icon>
            <el-icon><Tools /></el-icon>
          </template>
        </el-step>
        <el-step title="确认创建" description="检查并创建">
          <template #icon>
            <el-icon><Check /></el-icon>
          </template>
        </el-step>
      </el-steps>
    </div>

    <!-- 表单内容 -->
    <div class="form-container">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        size="large"
      >

        <!-- 步骤1: 基本信息 -->
        <div v-show="currentStep === 0" class="step-content">
          <div class="step-card">
            <div class="card-header">
              <h2 class="card-title">基本信息</h2>
              <p class="card-desc">填写任务的基本信息</p>
            </div>
            
            <el-form-item label="任务名称" prop="name" required>
              <el-input
                v-model="formData.name"
                placeholder="例如：京东价格监控"
                clearable
                maxlength="50"
                show-word-limit
              >
                <template #prefix>
                  <el-icon><Edit /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="任务描述" prop="description">
              <el-input
                v-model="formData.description"
                type="textarea"
                :rows="4"
                placeholder="描述任务的目的和功能，例如：每小时检查京东iPhone价格变化"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="任务分类" prop="category">
              <el-radio-group v-model="formData.category" class="category-group">
                <el-radio-button value="scraping">
                  <el-icon><Document /></el-icon>
                  数据爬取
                </el-radio-button>
                <el-radio-button value="monitoring">
                  <el-icon><View /></el-icon>
                  价格监控
                </el-radio-button>
                <el-radio-button value="automation">
                  <el-icon><Setting /></el-icon>
                  自动化操作
                </el-radio-button>
                <el-radio-button value="other">
                  <el-icon><More /></el-icon>
                  其他
                </el-radio-button>
              </el-radio-group>
            </el-form-item>
          </div>
        </div>

        <!-- 步骤2: 执行模式 -->
        <div v-show="currentStep === 1" class="step-content">
          <div class="step-card">
            <div class="card-header">
              <h2 class="card-title">选择执行模式</h2>
              <p class="card-desc">根据您的需求选择合适的执行方式</p>
            </div>

            <el-form-item prop="execution_mode">
              <div class="execution-modes">
                <!-- 有头模式 -->
                <div
                  class="mode-card"
                  :class="{ active: formData.execution_mode === 'headful' }"
                  @click="selectMode('headful')"
                >
                  <div class="mode-header">
                    <div class="mode-icon-wrapper headful">
                      <el-icon class="mode-icon"><Monitor /></el-icon>
                    </div>
                    <div class="mode-info">
                      <h3 class="mode-title">有头模式（本地客户端）</h3>
                      <el-tag type="success" size="small" effect="plain">推荐</el-tag>
                    </div>
                    <el-radio
                      v-model="formData.execution_mode"
                      value="headful"
                      class="mode-radio"
                    />
                  </div>

                  <p class="mode-description">
                    在您的电脑上执行任务，可以实时查看浏览器窗口
                  </p>

                  <div class="mode-features">
                    <div class="feature-item">
                      <el-icon class="feature-icon success"><CircleCheck /></el-icon>
                      <span>实时查看浏览器窗口</span>
                    </div>
                    <div class="feature-item">
                      <el-icon class="feature-icon success"><CircleCheck /></el-icon>
                      <span>可以手动干预操作</span>
                    </div>
                    <div class="feature-item">
                      <el-icon class="feature-icon success"><CircleCheck /></el-icon>
                      <span>适合调试和开发</span>
                    </div>
                    <div class="feature-item warning">
                      <el-icon class="feature-icon warning"><Warning /></el-icon>
                      <span>需要下载客户端程序</span>
                    </div>
                  </div>

                  <!-- 客户端状态 -->
                  <div v-if="formData.execution_mode === 'headful'" class="client-status">
                    <el-alert
                      v-if="clientStatus.online"
                      type="success"
                      :closable="false"
                      show-icon
                    >
                      <template #title>
                        <span>客户端已连接</span>
                        <span class="status-time">最后在线: {{ clientStatus.lastSeen }}</span>
                      </template>
                    </el-alert>
                    <el-alert
                      v-else
                      type="warning"
                      :closable="false"
                      show-icon
                    >
                      <template #title>
                        客户端未连接
                      </template>
                      <template #default>
                        <p>使用有头模式需要下载并运行客户端程序</p>
                        <el-button type="primary" size="small" @click="downloadClient">
                          <el-icon><Download /></el-icon>
                          下载客户端
                        </el-button>
                      </template>
                    </el-alert>
                  </div>
                </div>

                <!-- 无头模式 -->
                <div
                  class="mode-card"
                  :class="{ active: formData.execution_mode === 'headless' }"
                  @click="selectMode('headless')"
                >
                  <div class="mode-header">
                    <div class="mode-icon-wrapper headless">
                      <el-icon class="mode-icon"><Cpu /></el-icon>
                    </div>
                    <div class="mode-info">
                      <h3 class="mode-title">无头模式（服务器后台）</h3>
                    </div>
                    <el-radio
                      v-model="formData.execution_mode"
                      value="headless"
                      class="mode-radio"
                    />
                  </div>

                  <p class="mode-description">
                    在服务器上自动执行任务，无需人工干预
                  </p>

                  <div class="mode-features">
                    <div class="feature-item">
                      <el-icon class="feature-icon success"><CircleCheck /></el-icon>
                      <span>服务器自动执行</span>
                    </div>
                    <div class="feature-item">
                      <el-icon class="feature-icon success"><CircleCheck /></el-icon>
                      <span>无需下载客户端</span>
                    </div>
                    <div class="feature-item">
                      <el-icon class="feature-icon success"><CircleCheck /></el-icon>
                      <span>适合定时任务</span>
                    </div>
                    <div class="feature-item">
                      <el-icon class="feature-icon success"><CircleCheck /></el-icon>
                      <span>适合批量任务</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-form-item>
          </div>
        </div>

        <!-- 步骤3: 任务配置 -->
        <div v-show="currentStep === 2" class="step-content">
          <div class="step-card">
            <div class="card-header">
              <h2 class="card-title">任务配置</h2>
              <p class="card-desc">配置任务的详细参数</p>
            </div>

            <el-form-item label="任务类型" prop="task_type">
              <el-select v-model="formData.task_type" placeholder="请选择任务类型">
                <el-option label="浏览器自动化" value="browser" />
                <el-option label="桌面应用自动化" value="desktop" />
                <el-option label="混合模式" value="hybrid" />
              </el-select>
            </el-form-item>

            <el-form-item label="调度设置">
              <el-radio-group v-model="scheduleType">
                <el-radio value="manual">手动执行</el-radio>
                <el-radio value="cron">定时执行</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item v-if="scheduleType === 'cron'" label="Cron表达式">
              <el-input
                v-model="formData.cron_expression"
                placeholder="例如: 0 */1 * * * (每小时执行一次)"
              >
                <template #append>
                  <el-button @click="showCronHelper">
                    <el-icon><QuestionFilled /></el-icon>
                    帮助
                  </el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="浏览器配置">
              <el-collapse>
                <el-collapse-item title="高级配置" name="browser">
                  <el-form-item label="浏览器类型">
                    <el-select v-model="formData.config.browser_type">
                      <el-option label="Chromium" value="chromium" />
                      <el-option label="Firefox" value="firefox" />
                      <el-option label="WebKit" value="webkit" />
                    </el-select>
                  </el-form-item>

                  <el-form-item label="窗口大小">
                    <el-row :gutter="10">
                      <el-col :span="12">
                        <el-input v-model.number="formData.config.window_width" placeholder="宽度">
                          <template #append>px</template>
                        </el-input>
                      </el-col>
                      <el-col :span="12">
                        <el-input v-model.number="formData.config.window_height" placeholder="高度">
                          <template #append>px</template>
                        </el-input>
                      </el-col>
                    </el-row>
                  </el-form-item>

                  <el-form-item label="超时设置">
                    <el-input v-model.number="formData.config.timeout" placeholder="30000">
                      <template #append>毫秒</template>
                    </el-input>
                  </el-form-item>
                </el-collapse-item>
              </el-collapse>
            </el-form-item>
          </div>
        </div>

        <!-- 步骤4: 确认创建 -->
        <div v-show="currentStep === 3" class="step-content">
          <div class="step-card">
            <div class="card-header">
              <h2 class="card-title">确认信息</h2>
              <p class="card-desc">请检查任务配置是否正确</p>
            </div>

            <div class="confirm-content">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="任务名称">
                  {{ formData.name }}
                </el-descriptions-item>
                <el-descriptions-item label="任务分类">
                  <el-tag>{{ getCategoryLabel(formData.category) }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="执行模式" :span="2">
                  <el-tag :type="formData.execution_mode === 'headful' ? 'success' : 'info'">
                    {{ formData.execution_mode === 'headful' ? '有头模式' : '无头模式' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="任务描述" :span="2">
                  {{ formData.description || '无' }}
                </el-descriptions-item>
                <el-descriptions-item label="任务类型">
                  {{ getTaskTypeLabel(formData.task_type) }}
                </el-descriptions-item>
                <el-descriptions-item label="调度方式">
                  {{ scheduleType === 'manual' ? '手动执行' : '定时执行' }}
                </el-descriptions-item>
              </el-descriptions>

              <el-alert
                v-if="formData.execution_mode === 'headful' && !clientStatus.online"
                type="warning"
                :closable="false"
                show-icon
                style="margin-top: 20px"
              >
                <template #title>
                  提醒：客户端未连接
                </template>
                <template #default>
                  任务创建后需要启动客户端才能执行
                </template>
              </el-alert>
            </div>
          </div>
        </div>

        <!-- 底部操作按钮 -->
        <div class="form-footer">
          <el-button
            v-if="currentStep > 0"
            size="large"
            @click="prevStep"
          >
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          
          <el-button
            v-if="currentStep < 3"
            type="primary"
            size="large"
            @click="nextStep"
          >
            下一步
            <el-icon><ArrowRight /></el-icon>
          </el-button>

          <el-button
            v-if="currentStep === 3"
            type="primary"
            size="large"
            :loading="submitting"
            @click="handleSubmit"
          >
            <el-icon><Check /></el-icon>
            创建任务
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Edit, Document, Setting, Tools, Check, Monitor, Cpu,
  CircleCheck, Warning, Download, QuestionFilled, ArrowLeft,
  ArrowRight, View, More
} from '@element-plus/icons-vue'
import { createTask, checkClientStatus } from '@/api/automation/task'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 表单引用
const formRef = ref(null)

// 提交状态
const submitting = ref(false)

// 调度类型
const scheduleType = ref('manual')

// 客户端状态
const clientStatus = reactive({
  online: false,
  lastSeen: null
})

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  category: 'scraping',
  execution_mode: 'headful',
  task_type: 'browser',
  cron_expression: '',
  config: {
    browser_type: 'chromium',
    window_width: 1920,
    window_height: 1080,
    timeout: 30000
  }
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  execution_mode: [
    { required: true, message: '请选择执行模式', trigger: 'change' }
  ],
  task_type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ]
}

// 检查客户端状态
const checkClient = async () => {
  try {
    const res = await checkClientStatus()
    clientStatus.online = res.data.online
    clientStatus.lastSeen = res.data.last_seen
  } catch (error) {
    console.error('检查客户端状态失败:', error)
  }
}

// 选择执行模式
const selectMode = (mode) => {
  formData.execution_mode = mode
  if (mode === 'headful') {
    checkClient()
  }
}

// 下载客户端
const downloadClient = () => {
  const platform = detectOS()
  window.open(`/api/download/client/${platform}`)
  
  ElMessage.info({
    message: '下载完成后，请运行客户端并登录',
    duration: 5000
  })
}

// 检测操作系统
const detectOS = () => {
  const platform = navigator.platform.toLowerCase()
  if (platform.includes('win')) return 'windows'
  if (platform.includes('mac')) return 'macos'
  return 'linux'
}

// 获取分类标签
const getCategoryLabel = (category) => {
  const labels = {
    scraping: '数据爬取',
    monitoring: '价格监控',
    automation: '自动化操作',
    other: '其他'
  }
  return labels[category] || category
}

// 获取任务类型标签
const getTaskTypeLabel = (type) => {
  const labels = {
    browser: '浏览器自动化',
    desktop: '桌面应用自动化',
    hybrid: '混合模式'
  }
  return labels[type] || type
}

// 显示Cron帮助
const showCronHelper = () => {
  ElMessageBox.alert(
    `常用Cron表达式示例：
    
• 每分钟执行: * * * * *
• 每小时执行: 0 * * * *
• 每天8点执行: 0 8 * * *
• 每周一8点执行: 0 8 * * 1
• 每月1号8点执行: 0 8 1 * *`,
    'Cron表达式帮助',
    {
      confirmButtonText: '知道了'
    }
  )
}

// 下一步
const nextStep = async () => {
  // 验证当前步骤
  if (currentStep.value === 0) {
    try {
      await formRef.value.validateField(['name', 'category'])
    } catch {
      return
    }
  }
  
  if (currentStep.value === 1) {
    if (!formData.execution_mode) {
      ElMessage.warning('请选择执行模式')
      return
    }
    
    // 如果选择有头模式但客户端未连接，提示用户
    if (formData.execution_mode === 'headful' && !clientStatus.online) {
      const result = await ElMessageBox.confirm(
        '客户端未连接，任务创建后需要启动客户端才能执行。是否继续？',
        '提示',
        {
          confirmButtonText: '继续',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).catch(() => false)
      
      if (!result) return
    }
  }
  
  if (currentStep.value === 2) {
    try {
      await formRef.value.validateField(['task_type'])
    } catch {
      return
    }
  }
  
  currentStep.value++
}

// 上一步
const prevStep = () => {
  currentStep.value--
}

// 保存草稿
const saveDraft = () => {
  localStorage.setItem('task_draft', JSON.stringify(formData))
  ElMessage.success('草稿已保存')
}

// 取消
const handleCancel = async () => {
  const result = await ElMessageBox.confirm(
    '确定要取消创建任务吗？未保存的数据将丢失',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)
  
  if (result) {
    router.back()
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    const data = {
      ...formData,
      schedule_type: scheduleType.value
    }
    
    await createTask(data)
    
    ElMessage.success('任务创建成功')
    
    // 跳转到任务列表
    router.push('/automation/task')
  } catch (error) {
    console.error('创建任务失败:', error)
    ElMessage.error(error.message || '创建任务失败')
  } finally {
    submitting.value = false
  }
}

// 监听执行模式变化
watch(() => formData.execution_mode, (newMode) => {
  if (newMode === 'headful') {
    checkClient()
  }
})

// 组件挂载时
onMounted(() => {
  // 尝试加载草稿
  const draft = localStorage.getItem('task_draft')
  if (draft) {
    try {
      const draftData = JSON.parse(draft)
      Object.assign(formData, draftData)
    } catch (error) {
      console.error('加载草稿失败:', error)
    }
  }
  
  // 检查客户端状态
  checkClient()
  
  // 每30秒检查一次客户端状态
  setInterval(checkClient, 30000)
})
</script>

<style scoped lang="scss">
.task-create-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
}

// 页面头部
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);

  .header-content {
    .page-title {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 28px;
      font-weight: 600;
      color: #1f2937;
      margin: 0 0 8px 0;

      .title-icon {
        font-size: 32px;
        color: #6366f1;
      }
    }

    .page-subtitle {
      font-size: 14px;
      color: #6b7280;
      margin: 0;
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

// 步骤导航
.steps-container {
  margin-bottom: 32px;
  padding: 32px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);

  :deep(.el-steps) {
    .el-step__title {
      font-size: 16px;
      font-weight: 500;
    }

    .el-step__description {
      font-size: 13px;
    }
  }
}

// 表单容器
.form-container {
  max-width: 900px;
  margin: 0 auto;
}

// 步骤内容
.step-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 步骤卡片
.step-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;

  .card-header {
    margin-bottom: 32px;
    padding-bottom: 20px;
    border-bottom: 2px solid #f3f4f6;

    .card-title {
      font-size: 22px;
      font-weight: 600;
      color: #1f2937;
      margin: 0 0 8px 0;
    }

    .card-desc {
      font-size: 14px;
      color: #6b7280;
      margin: 0;
    }
  }
}

// 分类选择
.category-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;

  :deep(.el-radio-button) {
    .el-radio-button__inner {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 12px 20px;
      border-radius: 8px;
      border: 2px solid #e5e7eb;
      background: white;
      transition: all 0.3s;

      &:hover {
        border-color: #6366f1;
        background: #f5f3ff;
      }
    }

    &.is-active .el-radio-button__inner {
      border-color: #6366f1;
      background: #6366f1;
      color: white;
    }
  }
}

// 执行模式卡片
.execution-modes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.mode-card {
  border: 3px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;

  &:hover {
    border-color: #6366f1;
    box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.1);
    transform: translateY(-2px);
  }

  &.active {
    border-color: #6366f1;
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.2);
  }

  .mode-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;

    .mode-icon-wrapper {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;

      &.headful {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.headless {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }

      .mode-icon {
        font-size: 24px;
        color: white;
      }
    }

    .mode-info {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 8px;

      .mode-title {
        font-size: 18px;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
      }
    }

    .mode-radio {
      margin-left: auto;
    }
  }

  .mode-description {
    font-size: 14px;
    color: #6b7280;
    margin: 0 0 20px 0;
    line-height: 1.6;
  }

  .mode-features {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .feature-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      color: #374151;

      .feature-icon {
        font-size: 18px;

        &.success {
          color: #10b981;
        }

        &.warning {
          color: #f59e0b;
        }
      }

      &.warning {
        color: #92400e;
      }
    }
  }

  .client-status {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #e5e7eb;

    .status-time {
      margin-left: 12px;
      font-size: 12px;
      color: #6b7280;
    }
  }
}

// 确认内容
.confirm-content {
  :deep(.el-descriptions) {
    .el-descriptions__label {
      font-weight: 500;
    }
  }
}

// 底部操作按钮
.form-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);

  .el-button {
    min-width: 120px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .task-create-container {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .execution-modes {
    grid-template-columns: 1fr;
  }

  .form-footer {
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }
}
</style>
