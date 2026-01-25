<template>
  <div class="app-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleBack" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div class="header-info">
          <h2 class="page-title">{{ taskInfo.name || '任务执行监控' }}</h2>
          <p class="page-subtitle">任务ID: {{ taskId }} | 执行ID: {{ executionId }}</p>
        </div>
      </div>
      <div class="header-right">
        <el-button 
          v-if="executionState === 'running'"
          type="warning" 
          @click="handlePause"
          :loading="controlling"
        >
          <el-icon><VideoPause /></el-icon>
          暂停
        </el-button>
        <el-button 
          v-if="executionState === 'paused'"
          type="success" 
          @click="handleResume"
          :loading="controlling"
        >
          <el-icon><VideoPlay /></el-icon>
          恢复
        </el-button>
        <el-button 
          v-if="['running', 'paused'].includes(executionState)"
          type="danger" 
          @click="handleStop"
          :loading="controlling"
        >
          <el-icon><Close /></el-icon>
          停止
        </el-button>
      </div>
    </div>

    <!-- 执行状态卡片 -->
    <el-row :gutter="20" class="status-cards">
      <el-col :span="6">
        <el-card class="status-card" shadow="hover">
          <div class="status-item">
            <div class="status-label">执行状态</div>
            <div class="status-value">
              <el-tag :type="getStatusType(executionState)" size="large">
                {{ getStatusLabel(executionState) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card" shadow="hover">
          <div class="status-item">
            <div class="status-label">执行进度</div>
            <div class="status-value">
              <span class="progress-text">{{ progressPercentage }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card" shadow="hover">
          <div class="status-item">
            <div class="status-label">已执行操作</div>
            <div class="status-value">
              <span class="count-text">{{ completedActions }}/{{ totalActions }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card" shadow="hover">
          <div class="status-item">
            <div class="status-label">执行时长</div>
            <div class="status-value">
              <span class="time-text">{{ executionDuration }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 进度条 -->
    <el-card class="progress-card" shadow="never">
      <template #header>
        <span class="card-title">执行进度</span>
      </template>
      <div class="progress-container">
        <el-progress
          :percentage="progressPercentage"
          :status="getProgressStatus()"
          :stroke-width="20"
          striped
          striped-flow
        />
        <div class="progress-info">
          <span>已完成 {{ completedActions }} 个操作，剩余 {{ remainingActions }} 个操作</span>
          <span v-if="estimatedTime" class="estimated-time">
            预计剩余时间: {{ estimatedTime }}
          </span>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 操作执行列表 -->
      <el-col :span="16">
        <el-card class="actions-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">操作执行列表</span>
              <el-button size="small" @click="refreshActions">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <div class="actions-list" v-loading="loadingActions">
            <div
              v-for="(action, index) in actionList"
              :key="index"
              class="action-item"
              :class="{
                'action-completed': action.status === 'completed',
                'action-running': action.status === 'running',
                'action-failed': action.status === 'failed',
                'action-pending': action.status === 'pending'
              }"
            >
              <div class="action-index">{{ index + 1 }}</div>
              <div class="action-content">
                <div class="action-header">
                  <el-tag :type="getActionStatusType(action.status)" size="small">
                    {{ getActionStatusLabel(action.status) }}
                  </el-tag>
                  <span class="action-type">{{ getActionTypeLabel(action.action_type) }}</span>
                  <span class="action-description">{{ action.description || '无描述' }}</span>
                </div>
                <div v-if="action.params && Object.keys(action.params).length > 0" class="action-params">
                  <el-descriptions :column="2" size="small" border>
                    <el-descriptions-item
                      v-for="(value, key) in action.params"
                      :key="key"
                      :label="key"
                    >
                      {{ value }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
                <div v-if="action.result" class="action-result">
                  <el-collapse>
                    <el-collapse-item title="查看结果" name="result">
                      <pre>{{ JSON.stringify(action.result, null, 2) }}</pre>
                    </el-collapse-item>
                  </el-collapse>
                </div>
                <div v-if="action.error" class="action-error">
                  <el-alert
                    type="error"
                    :title="action.error"
                    :closable="false"
                    show-icon
                  />
                </div>
                <div v-if="action.execution_time" class="action-time">
                  <el-icon><Clock /></el-icon>
                  执行时间: {{ action.execution_time }}ms
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 实时日志 -->
      <el-col :span="8">
        <el-card class="logs-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">执行日志</span>
              <div class="header-actions">
                <el-button size="small" @click="clearLogs">
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
                <el-switch
                  v-model="autoScroll"
                  active-text="自动滚动"
                  size="small"
                />
              </div>
            </div>
          </template>

          <div class="logs-container" ref="logsContainerRef">
            <div
              v-for="(log, index) in logs"
              :key="index"
              class="log-item"
              :class="`log-${log.level}`"
            >
              <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              <span class="log-level">{{ log.level.toUpperCase() }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <div v-if="logs.length === 0" class="logs-empty">
              暂无日志
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 错误详情对话框 -->
    <el-dialog
      v-model="errorDialogVisible"
      title="错误详情"
      width="60%"
    >
      <div class="error-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="错误类型">
            {{ errorDetail.type }}
          </el-descriptions-item>
          <el-descriptions-item label="错误信息">
            {{ errorDetail.message }}
          </el-descriptions-item>
          <el-descriptions-item label="错误堆栈" v-if="errorDetail.stack">
            <pre class="error-stack">{{ errorDetail.stack }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="发生时间">
            {{ formatTime(errorDetail.timestamp) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup name="ExecutionMonitor">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  VideoPause,
  VideoPlay,
  Close,
  Refresh,
  Delete,
  Clock
} from '@element-plus/icons-vue'
import { getCurrentInstance } from 'vue'
import {
  getExecutionStatus,
  getExecutionProgress,
  getExecutionLogs,
  pauseTask,
  resumeTask,
  stopTask
} from '@/api/automation/task'

const { proxy } = getCurrentInstance()
const route = useRoute()
const router = useRouter()

const taskId = ref(route.params.taskId || route.query.taskId)
const executionId = ref(route.query.executionId)

// 任务信息
const taskInfo = ref({})

// 执行状态
const executionState = ref('pending')
const progressPercentage = ref(0)
const completedActions = ref(0)
const totalActions = ref(0)
const remainingActions = computed(() => totalActions.value - completedActions.value)
const executionDuration = ref('00:00:00')
const estimatedTime = ref('')

// 操作列表
const actionList = ref([])
const loadingActions = ref(false)

// 日志
const logs = ref([])
const autoScroll = ref(true)
const logsContainerRef = ref(null)

// 控制状态
const controlling = ref(false)

// 错误详情
const errorDialogVisible = ref(false)
const errorDetail = reactive({
  type: '',
  message: '',
  stack: '',
  timestamp: null
})

// 轮询定时器
let statusPollTimer = null
let logsPollTimer = null

// 获取执行状态
async function fetchExecutionStatus() {
  try {
    const response = await getExecutionStatus(taskId.value)
    if (response.code === 200 && response.data) {
      executionState.value = response.data.state || 'pending'
      taskInfo.value = response.data.task_info || {}
    }
  } catch (error) {
    console.error('获取执行状态失败:', error)
  }
}

// 获取执行进度
async function fetchExecutionProgress() {
  try {
    const response = await getExecutionProgress(taskId.value)
    if (response.code === 200 && response.data) {
      const progress = response.data
      progressPercentage.value = progress.progress_percentage || 0
      completedActions.value = progress.completed_actions || 0
      totalActions.value = progress.total_actions || 0
      executionDuration.value = formatDuration(progress.elapsed_time || 0)
      estimatedTime.value = progress.estimated_remaining_time
        ? formatDuration(progress.estimated_remaining_time)
        : ''
    }
  } catch (error) {
    console.error('获取执行进度失败:', error)
  }
}

// 获取操作列表
async function fetchActions() {
  loadingActions.value = true
  try {
    // 这里应该调用获取操作列表的API
    // 暂时使用模拟数据
    const response = await getExecutionStatus(taskId.value)
    if (response.code === 200 && response.data) {
      // 从执行状态中获取操作列表
      actionList.value = response.data.actions || []
    }
  } catch (error) {
    console.error('获取操作列表失败:', error)
  } finally {
    loadingActions.value = false
  }
}

// 获取日志
async function fetchLogs() {
  try {
    const response = await getExecutionLogs(taskId.value, {
      skip: 0,
      limit: 100
    })
    if (response.code === 200 && response.data) {
      logs.value = response.data.logs || []
      if (autoScroll.value) {
        nextTick(() => {
          scrollToBottom()
        })
      }
    }
  } catch (error) {
    console.error('获取日志失败:', error)
  }
}

// 刷新操作列表
function refreshActions() {
  fetchActions()
}

// 清空日志
function clearLogs() {
  logs.value = []
}

// 滚动到底部
function scrollToBottom() {
  if (logsContainerRef.value) {
    logsContainerRef.value.scrollTop = logsContainerRef.value.scrollHeight
  }
}

// 暂停任务
async function handlePause() {
  try {
    await ElMessageBox.confirm('确定要暂停任务执行吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    controlling.value = true
    const response = await pauseTask(taskId.value)
    if (response.code === 200) {
      ElMessage.success('任务已暂停')
      fetchExecutionStatus()
    } else {
      throw new Error(response.msg || '暂停失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('暂停任务失败：' + error.message)
    }
  } finally {
    controlling.value = false
  }
}

// 恢复任务
async function handleResume() {
  controlling.value = true
  try {
    const response = await resumeTask(taskId.value)
    if (response.code === 200) {
      ElMessage.success('任务已恢复')
      fetchExecutionStatus()
    } else {
      throw new Error(response.msg || '恢复失败')
    }
  } catch (error) {
    ElMessage.error('恢复任务失败：' + error.message)
  } finally {
    controlling.value = false
  }
}

// 停止任务
async function handleStop() {
  try {
    await ElMessageBox.confirm('确定要停止任务执行吗？停止后无法恢复', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    controlling.value = true
    const response = await stopTask(taskId.value)
    if (response.code === 200) {
      ElMessage.success('任务已停止')
      fetchExecutionStatus()
    } else {
      throw new Error(response.msg || '停止失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停止任务失败：' + error.message)
    }
  } finally {
    controlling.value = false
  }
}

// 返回
function handleBack() {
  router.back()
}

// 获取状态类型
function getStatusType(state) {
  const typeMap = {
    'pending': 'info',
    'running': 'success',
    'paused': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'stopped': 'info'
  }
  return typeMap[state] || 'info'
}

// 获取状态标签
function getStatusLabel(state) {
  const labelMap = {
    'pending': '待执行',
    'running': '执行中',
    'paused': '已暂停',
    'completed': '已完成',
    'failed': '执行失败',
    'stopped': '已停止'
  }
  return labelMap[state] || state
}

// 获取进度状态
function getProgressStatus() {
  if (executionState.value === 'failed') return 'exception'
  if (executionState.value === 'completed') return 'success'
  return null
}

// 获取操作状态类型
function getActionStatusType(status) {
  const typeMap = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取操作状态标签
function getActionStatusLabel(status) {
  const labelMap = {
    'pending': '待执行',
    'running': '执行中',
    'completed': '已完成',
    'failed': '失败'
  }
  return labelMap[status] || status
}

// 获取操作类型标签
function getActionTypeLabel(type) {
  const labelMap = {
    'click': '点击',
    'type': '输入',
    'goto_url': '导航',
    'wait': '等待',
    'get_text': '获取文本'
  }
  return labelMap[type] || type
}

// 格式化时间
function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN')
}

// 格式化时长
function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

// 监听自动滚动
watch(autoScroll, (newVal) => {
  if (newVal) {
    scrollToBottom()
  }
})

// 初始化
onMounted(() => {
  fetchExecutionStatus()
  fetchExecutionProgress()
  fetchActions()
  fetchLogs()

  // 开始轮询
  statusPollTimer = setInterval(() => {
    fetchExecutionStatus()
    fetchExecutionProgress()
  }, 2000) // 每2秒更新一次状态

  logsPollTimer = setInterval(() => {
    fetchLogs()
  }, 3000) // 每3秒更新一次日志
})

// 清理
onUnmounted(() => {
  if (statusPollTimer) {
    clearInterval(statusPollTimer)
  }
  if (logsPollTimer) {
    clearInterval(logsPollTimer)
  }
})
</script>

<style scoped lang="scss">
.app-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

  .header-left {
    display: flex;
    align-items: center;
    gap: 15px;

    .header-info {
      .page-title {
        margin: 0 0 5px 0;
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }

      .page-subtitle {
        margin: 0;
        font-size: 13px;
        color: #909399;
      }
    }
  }

  .header-right {
    display: flex;
    gap: 10px;
  }
}

.status-cards {
  margin-bottom: 20px;

  .status-card {
    .status-item {
      .status-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 10px;
      }

      .status-value {
        .progress-text,
        .count-text,
        .time-text {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
        }
      }
    }
  }
}

.progress-card {
  margin-bottom: 20px;

  .progress-container {
    .progress-info {
      display: flex;
      justify-content: space-between;
      margin-top: 15px;
      font-size: 13px;
      color: #606266;

      .estimated-time {
        color: #909399;
      }
    }
  }
}

.actions-card,
.logs-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }
  }
}

.actions-list {
  max-height: 600px;
  overflow-y: auto;

  .action-item {
    display: flex;
    gap: 15px;
    padding: 15px;
    margin-bottom: 15px;
    background: #f5f7fa;
    border-radius: 4px;
    border-left: 4px solid #e4e7ed;
    transition: all 0.3s;

    &.action-completed {
      border-left-color: #67c23a;
      background: #f0f9ff;
    }

    &.action-running {
      border-left-color: #e6a23c;
      background: #fdf6ec;
      animation: pulse 2s infinite;
    }

    &.action-failed {
      border-left-color: #f56c6c;
      background: #fef0f0;
    }

    &.action-pending {
      border-left-color: #909399;
      opacity: 0.7;
    }

    .action-index {
      flex-shrink: 0;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #e4e7ed;
      color: #606266;
      border-radius: 50%;
      font-weight: 600;
    }

    .action-content {
      flex: 1;

      .action-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;

        .action-type {
          font-weight: 600;
          color: #303133;
        }

        .action-description {
          color: #606266;
          font-size: 14px;
        }
      }

      .action-params {
        margin: 10px 0;
      }

      .action-result {
        margin: 10px 0;

        pre {
          background: #f5f7fa;
          padding: 10px;
          border-radius: 4px;
          font-size: 12px;
          overflow-x: auto;
        }
      }

      .action-error {
        margin: 10px 0;
      }

      .action-time {
        display: flex;
        align-items: center;
        gap: 5px;
        margin-top: 10px;
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

.logs-container {
  height: 600px;
  overflow-y: auto;
  background: #1e1e1e;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;

  .log-item {
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
    line-height: 1.6;

    .log-time {
      color: #909399;
      flex-shrink: 0;
    }

    .log-level {
      flex-shrink: 0;
      font-weight: 600;
      width: 60px;
    }

    .log-message {
      flex: 1;
      color: #e4e7ed;
    }

    &.log-info {
      .log-level {
        color: #409eff;
      }
    }

    &.log-warning {
      .log-level {
        color: #e6a23c;
      }
    }

    &.log-error {
      .log-level {
        color: #f56c6c;
      }
    }

    &.log-success {
      .log-level {
        color: #67c23a;
      }
    }
  }

  .logs-empty {
    text-align: center;
    color: #909399;
    padding: 50px 0;
  }
}

.error-detail {
  .error-stack {
    background: #f5f7fa;
    padding: 15px;
    border-radius: 4px;
    font-size: 12px;
    overflow-x: auto;
    max-height: 400px;
    overflow-y: auto;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
</style>
