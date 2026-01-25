<template>
  <div class="app-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">
          <el-icon class="title-icon"><MagicStick /></el-icon>
          创建自动化任务
        </h2>
        <p class="page-subtitle">使用自然语言描述您的任务，系统将自动解析为可执行的操作序列</p>
      </div>
      <div class="header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSaveDraft" :loading="savingDraft">
          <el-icon><Document /></el-icon>
          保存草稿
        </el-button>
      </div>
    </div>

    <!-- 模式切换 -->
    <el-card class="mode-switch-card" shadow="never">
      <el-radio-group v-model="createMode" size="large" @change="handleModeChange">
        <el-radio-button label="natural">
          <el-icon><ChatLineRound /></el-icon>
          自然语言模式
        </el-radio-button>
        <el-radio-button label="manual">
          <el-icon><Edit /></el-icon>
          手动配置模式
        </el-radio-button>
      </el-radio-group>
    </el-card>

    <!-- 自然语言模式 -->
    <div v-if="createMode === 'natural'" class="natural-language-mode">
      <el-card class="input-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><ChatLineRound /></el-icon>
              任务描述
            </span>
            <el-button 
              type="primary" 
              :loading="parsing" 
              @click="handleParse"
              :disabled="!taskDescription.trim()"
            >
              <el-icon><Search /></el-icon>
              {{ parsing ? '解析中...' : '解析任务' }}
            </el-button>
          </div>
        </template>

        <!-- 自然语言输入区域 -->
        <div class="input-area">
          <el-input
            v-model="taskDescription"
            type="textarea"
            :rows="8"
            placeholder="请输入您的任务描述，例如：&#10;1. 打开京东网站&#10;2. 搜索iPhone 15&#10;3. 获取第一个商品的价格&#10;4. 如果价格低于8000元，发送邮件通知我"
            :disabled="parsing"
            class="task-input"
            show-word-limit
            maxlength="2000"
          />
          
          <!-- 示例提示 -->
          <div class="examples-section">
            <el-collapse v-model="activeExamples">
              <el-collapse-item name="examples" title="查看示例">
                <div class="examples-list">
                  <div 
                    v-for="(example, index) in examples" 
                    :key="index"
                    class="example-item"
                    @click="useExample(example)"
                  >
                    <div class="example-title">{{ example.title }}</div>
                    <div class="example-text">{{ example.text }}</div>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>

        <!-- 解析状态 -->
        <div v-if="parseStatus" class="parse-status">
          <el-alert
            :type="parseStatus.type"
            :title="parseStatus.title"
            :description="parseStatus.message"
            :closable="false"
            show-icon
          />
        </div>
      </el-card>

      <!-- 解析结果预览 -->
      <el-card v-if="parsedActions.length > 0" class="preview-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><View /></el-icon>
              解析结果预览
            </span>
            <div class="header-actions">
              <el-button size="small" @click="handleEditActions">
                <el-icon><Edit /></el-icon>
                编辑操作序列
              </el-button>
              <el-button size="small" type="primary" @click="handleSaveTask" :loading="saving">
                <el-icon><Check /></el-icon>
                保存任务
              </el-button>
            </div>
          </div>
        </template>

        <!-- 操作序列列表 -->
        <div class="actions-preview">
          <div 
            v-for="(action, index) in parsedActions" 
            :key="index"
            class="action-item"
          >
            <div class="action-index">{{ index + 1 }}</div>
            <div class="action-content">
              <div class="action-header">
                <el-tag :type="getActionTypeColor(action.action_type)" size="small">
                  {{ getActionTypeLabel(action.action_type) }}
                </el-tag>
                <span class="action-description">{{ action.description || '无描述' }}</span>
              </div>
              <div class="action-params">
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
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 手动配置模式 -->
    <div v-else class="manual-mode">
      <el-card shadow="never">
        <template #header>
          <span class="card-title">
            <el-icon><Edit /></el-icon>
            手动配置任务
          </span>
        </template>
        <el-form ref="manualFormRef" :model="manualForm" :rules="manualRules" label-width="100px">
          <el-form-item label="任务名称" prop="name">
            <el-input v-model="manualForm.name" placeholder="请输入任务名称" />
          </el-form-item>
          <el-form-item label="任务类型" prop="taskType">
            <el-select v-model="manualForm.taskType" placeholder="请选择任务类型">
              <el-option
                v-for="dict in automation_task_type"
                :key="dict.value"
                :label="dict.label"
                :value="dict.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="任务描述" prop="description">
            <el-input v-model="manualForm.description" type="textarea" :rows="4" placeholder="请输入任务描述" />
          </el-form-item>
          <el-form-item label="任务动作" prop="actions">
            <el-input 
              v-model="manualForm.actionsStr" 
              type="textarea" 
              :rows="8" 
              placeholder='请输入任务动作JSON，例如：[{"type":"click","selector":"#btn"}]'
            />
          </el-form-item>
          <el-form-item label="任务配置" prop="config">
            <el-input 
              v-model="manualForm.configStr" 
              type="textarea" 
              :rows="4" 
              placeholder='请输入任务配置JSON，例如：{"timeout":30}'
            />
          </el-form-item>
        </el-form>
        <div class="form-actions">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="handleSaveManualTask" :loading="saving">
            保存任务
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 操作序列编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑操作序列"
      width="80%"
      :close-on-click-modal="false"
    >
      <div class="edit-actions-container">
        <draggable
          v-model="editableActions"
          item-key="id"
          handle=".drag-handle"
          @end="handleDragEnd"
        >
          <template #item="{ element, index }">
            <div class="editable-action-item">
              <div class="drag-handle">
                <el-icon><Rank /></el-icon>
              </div>
              <div class="action-form">
                <el-form :model="element" label-width="100px" size="small">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item label="操作类型">
                        <el-select v-model="element.action_type" placeholder="选择操作类型">
                          <el-option label="点击" value="click" />
                          <el-option label="输入" value="type" />
                          <el-option label="导航" value="goto_url" />
                          <el-option label="等待" value="wait" />
                          <el-option label="获取文本" value="get_text" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="16">
                      <el-form-item label="描述">
                        <el-input v-model="element.description" placeholder="操作描述" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="参数">
                    <el-input
                      v-model="element.paramsStr"
                      type="textarea"
                      :rows="3"
                      placeholder='JSON格式，例如：{"selector": "#btn", "timeout": 5000}'
                    />
                  </el-form-item>
                </el-form>
              </div>
              <div class="action-actions">
                <el-button type="danger" size="small" @click="removeAction(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
        </draggable>
        <el-button type="primary" plain @click="addNewAction" class="add-action-btn">
          <el-icon><Plus /></el-icon>
          添加操作
        </el-button>
      </div>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEditedActions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="TaskCreateNL">
import { ref, reactive, computed, getCurrentInstance } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  MagicStick,
  Document,
  ChatLineRound,
  Edit,
  Search,
  View,
  Check,
  Rank,
  Delete,
  Plus
} from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import { parseTask, addTask } from '@/api/automation/task'

const { proxy } = getCurrentInstance()
const router = useRouter()
const { automation_task_type } = proxy.useDict('automation_task_type')

// 创建模式
const createMode = ref('natural')

// 自然语言模式数据
const taskDescription = ref('')
const parsing = ref(false)
const parseStatus = ref(null)
const parsedActions = ref([])
const activeExamples = ref([])
const saving = ref(false)
const savingDraft = ref(false)

// 手动配置模式数据
const manualFormRef = ref(null)
const manualForm = reactive({
  name: '',
  taskType: '',
  description: '',
  actionsStr: '',
  configStr: ''
})
const manualRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  taskType: [{ required: true, message: '请选择任务类型', trigger: 'change' }]
}

// 编辑对话框
const editDialogVisible = ref(false)
const editableActions = ref([])

// 示例任务
const examples = [
  {
    title: '价格监控',
    text: '打开京东网站，搜索iPhone 15，获取第一个商品的价格，如果价格低于8000元，发送邮件通知我'
  },
  {
    title: '数据采集',
    text: '访问百度新闻首页，获取前10条新闻的标题和链接，保存到Excel文件'
  },
  {
    title: '表单填写',
    text: '打开登录页面，输入用户名和密码，点击登录按钮，等待页面加载完成'
  },
  {
    title: '信息查询',
    text: '打开天气网站，查询北京的天气预报，获取今天的最高温度和最低温度'
  }
]

// 使用示例
function useExample(example) {
  taskDescription.value = example.text
  ElMessage.success('已应用示例')
}

// 模式切换
function handleModeChange() {
  if (createMode.value === 'manual') {
    // 切换到手动模式时，可以保留自然语言解析的结果
    if (parsedActions.value.length > 0) {
      manualForm.actionsStr = JSON.stringify(parsedActions.value, null, 2)
    }
  }
}

// 解析任务
async function handleParse() {
  if (!taskDescription.value.trim()) {
    ElMessage.warning('请输入任务描述')
    return
  }

  parsing.value = true
  parseStatus.value = {
    type: 'info',
    title: '正在解析...',
    message: '系统正在分析您的任务描述，请稍候'
  }

  try {
    const response = await parseTask({
      description: taskDescription.value
    })

    if (response.code === 200 && response.data) {
      parsedActions.value = response.data.actions || []
      parseStatus.value = {
        type: 'success',
        title: '解析成功',
        message: `成功解析出 ${parsedActions.value.length} 个操作步骤`
      }
      ElMessage.success('任务解析成功')
    } else {
      throw new Error(response.msg || '解析失败')
    }
  } catch (error) {
    parseStatus.value = {
      type: 'error',
      title: '解析失败',
      message: error.message || '请检查任务描述是否清晰，或稍后重试'
    }
    ElMessage.error('任务解析失败：' + error.message)
  } finally {
    parsing.value = false
  }
}

// 编辑操作序列
function handleEditActions() {
  editableActions.value = parsedActions.value.map((action, index) => ({
    id: index,
    ...action,
    paramsStr: JSON.stringify(action.params || {}, null, 2)
  }))
  editDialogVisible.value = true
}

// 保存编辑后的操作序列
function handleSaveEditedActions() {
  try {
    parsedActions.value = editableActions.value.map(action => {
      const { id, paramsStr, ...rest } = action
      return {
        ...rest,
        params: paramsStr ? JSON.parse(paramsStr) : {}
      }
    })
    editDialogVisible.value = false
    ElMessage.success('操作序列已更新')
  } catch (error) {
    ElMessage.error('JSON格式错误：' + error.message)
  }
}

// 添加新操作
function addNewAction() {
  editableActions.value.push({
    id: Date.now(),
    action_type: 'click',
    description: '',
    params: {},
    paramsStr: '{}'
  })
}

// 删除操作
function removeAction(index) {
  editableActions.value.splice(index, 1)
}

// 拖拽结束
function handleDragEnd() {
  // 拖拽后可以做一些处理
}

// 获取操作类型颜色
function getActionTypeColor(type) {
  const colorMap = {
    'click': 'primary',
    'type': 'success',
    'goto_url': 'info',
    'wait': 'warning',
    'get_text': ''
  }
  return colorMap[type] || ''
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

// 保存任务
async function handleSaveTask() {
  if (parsedActions.value.length === 0) {
    ElMessage.warning('请先解析任务或添加操作')
    return
  }

  saving.value = true
  try {
    const taskData = {
      name: taskDescription.value.substring(0, 50) || '未命名任务',
      description: taskDescription.value,
      taskType: 'browser',
      actions: parsedActions.value,
      config: {
        timeout: 3600
      },
      isNaturalLanguage: true
    }

    const response = await addTask(taskData)
    if (response.code === 200) {
      ElMessage.success('任务创建成功')
      router.push('/automation/task')
    } else {
      throw new Error(response.msg || '创建失败')
    }
  } catch (error) {
    ElMessage.error('任务创建失败：' + error.message)
  } finally {
    saving.value = false
  }
}

// 保存手动配置任务
async function handleSaveManualTask() {
  if (!manualFormRef.value) return

  await manualFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const taskData = {
          ...manualForm,
          actions: JSON.parse(manualForm.actionsStr || '[]'),
          config: manualForm.configStr ? JSON.parse(manualForm.configStr) : null
        }
        delete taskData.actionsStr
        delete taskData.configStr

        const response = await addTask(taskData)
        if (response.code === 200) {
          ElMessage.success('任务创建成功')
          router.push('/automation/task')
        } else {
          throw new Error(response.msg || '创建失败')
        }
      } catch (error) {
        if (error.message.includes('JSON')) {
          ElMessage.error('JSON格式错误，请检查')
        } else {
          ElMessage.error('任务创建失败：' + error.message)
        }
      }
    }
  })
}

// 保存草稿
function handleSaveDraft() {
  const draft = {
    mode: createMode.value,
    taskDescription: taskDescription.value,
    parsedActions: parsedActions.value,
    manualForm: manualForm
  }
  localStorage.setItem('task-draft', JSON.stringify(draft))
  savingDraft.value = true
  setTimeout(() => {
    savingDraft.value = false
    ElMessage.success('草稿已保存')
  }, 500)
}

// 取消
function handleCancel() {
  ElMessageBox.confirm('确定要取消创建任务吗？未保存的数据将丢失', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    router.back()
  }).catch(() => {})
}

// 加载草稿
function loadDraft() {
  const draft = localStorage.getItem('task-draft')
  if (draft) {
    try {
      const data = JSON.parse(draft)
      createMode.value = data.mode || 'natural'
      taskDescription.value = data.taskDescription || ''
      parsedActions.value = data.parsedActions || []
      Object.assign(manualForm, data.manualForm || {})
    } catch (e) {
      console.error('加载草稿失败:', e)
    }
  }
}

// 初始化
loadDraft()
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
  align-items: flex-start;
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

  .header-left {
    flex: 1;

    .page-title {
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 0 0 8px 0;
      font-size: 20px;
      font-weight: 600;
      color: #303133;

      .title-icon {
        font-size: 24px;
        color: #409eff;
      }
    }

    .page-subtitle {
      margin: 0;
      font-size: 14px;
      color: #909399;
    }
  }

  .header-right {
    display: flex;
    gap: 10px;
  }
}

.mode-switch-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.natural-language-mode,
.manual-mode {
  .input-card,
  .preview-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }

      .header-actions {
        display: flex;
        gap: 10px;
      }
    }
  }
}

.input-area {
  .task-input {
    margin-bottom: 20px;
  }

  .examples-section {
    margin-top: 20px;

    .examples-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 15px;
      margin-top: 15px;

      .example-item {
        padding: 15px;
        background: #f5f7fa;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          background: #e4e7ed;
          transform: translateY(-2px);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .example-title {
          font-weight: 600;
          color: #303133;
          margin-bottom: 8px;
        }

        .example-text {
          font-size: 13px;
          color: #606266;
          line-height: 1.6;
        }
      }
    }
  }
}

.parse-status {
  margin-top: 20px;
}

.actions-preview {
  .action-item {
    display: flex;
    gap: 15px;
    padding: 15px;
    margin-bottom: 15px;
    background: #f5f7fa;
    border-radius: 4px;
    border-left: 4px solid #409eff;

    .action-index {
      flex-shrink: 0;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #409eff;
      color: #fff;
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

        .action-description {
          color: #606266;
          font-size: 14px;
        }
      }

      .action-params {
        :deep(.el-descriptions) {
          background: #fff;
        }
      }
    }
  }
}

.edit-actions-container {
  max-height: 600px;
  overflow-y: auto;

  .editable-action-item {
    display: flex;
    gap: 15px;
    padding: 15px;
    margin-bottom: 15px;
    background: #f5f7fa;
    border-radius: 4px;
    border: 1px solid #e4e7ed;

    .drag-handle {
      flex-shrink: 0;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #e4e7ed;
      border-radius: 4px;
      cursor: move;
      color: #909399;

      &:hover {
        background: #d3d4d6;
        color: #606266;
      }
    }

    .action-form {
      flex: 1;
    }

    .action-actions {
      flex-shrink: 0;
    }
  }

  .add-action-btn {
    width: 100%;
    margin-top: 15px;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
