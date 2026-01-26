<template>
  <div class="modern-container">
    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleAdd" class="modern-btn-gradient" v-hasPermi="['thesis:ai-model:add']">
        <Plus class="w-4 h-4 mr-2" />
        新增模型
      </el-button>
      <el-button @click="getList" class="modern-btn-outline">
        <RefreshCw class="w-4 h-4 mr-2" />
        刷新
      </el-button>
    </div>

    <!-- 模型卡片网格 -->
    <div class="model-grid">
      <div
        v-for="model in modelList"
        :key="model.configId"
        class="model-card glass-card"
        :class="{ 'is-default': model.isDefault === '1', 'is-disabled': model.isEnabled === '0' }"
      >
        <!-- 卡片头部 -->
        <div class="card-header">
          <div class="model-title">
            <div class="model-icon">
              <Cpu class="w-6 h-6" />
            </div>
            <span>{{ model.modelName }}</span>
            <div class="model-badges">
              <div v-if="model.isDefault === '1'" class="badge badge-default">
                <Star class="w-3 h-3" />
                <span>默认</span>
              </div>
              <div v-if="model.isPreset === '1'" class="badge badge-preset">
                <Shield class="w-3 h-3" />
                <span>预设</span>
              </div>
            </div>
          </div>
          <el-switch
            v-model="model.isEnabled"
            active-value="1"
            inactive-value="0"
            @change="handleStatusChange(model)"
            v-hasPermi="['thesis:ai-model:edit']"
            class="modern-switch"
          />
        </div>

        <!-- 卡片内容 -->
        <div class="model-info">
          <div class="info-row">
            <span class="label">模型版本</span>
            <span class="value">{{ model.modelVersion }}</span>
          </div>
          <div class="info-row">
            <span class="label">API状态</span>
            <div class="status-badge" :class="model.apiKey ? 'status-success' : 'status-danger'">
              <div class="status-dot"></div>
              <span>{{ model.apiKey ? '已配置' : '未配置' }}</span>
            </div>
          </div>
          <div class="info-row">
            <span class="label">优先级</span>
            <div class="priority-stars">
              <Star 
                v-for="i in 5" 
                :key="i" 
                class="w-4 h-4"
                :class="i <= model.priorityRate ? 'star-filled' : 'star-empty'"
              />
            </div>
          </div>
          <div class="info-row" v-if="model.remark">
            <span class="label">说明</span>
            <span class="value text-muted">{{ model.remark }}</span>
          </div>
        </div>

        <!-- 卡片操作 -->
        <div class="card-footer">
          <el-button
            @click="handleEdit(model)"
            v-hasPermi="['thesis:ai-model:edit']"
            class="action-btn"
          >
            <Edit class="w-4 h-4 mr-2" />
            编辑
          </el-button>
          <el-button
            @click="handleTest(model)"
            v-hasPermi="['thesis:ai-model:test']"
            :disabled="!model.apiKey"
            class="action-btn"
          >
            <Zap class="w-4 h-4 mr-2" />
            测试
          </el-button>
          <el-button
            @click="handleSetDefault(model)"
            v-hasPermi="['thesis:ai-model:edit']"
            v-if="model.isDefault !== '1' && model.isEnabled === '1'"
            class="action-btn"
          >
            <Star class="w-4 h-4 mr-2" />
            设为默认
          </el-button>
          <el-button
            @click="handleDelete(model)"
            v-hasPermi="['thesis:ai-model:remove']"
            v-if="model.isPreset !== '1'"
            class="action-btn action-btn-danger"
          >
            <Trash2 class="w-4 h-4 mr-2" />
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog 
      :title="dialogTitle" 
      v-model="dialogVisible" 
      width="600px" 
      :show-close="false"
      class="modern-dialog"
    >
      <template #header>
        <div class="dialog-header">
          <Cpu class="w-6 h-6" />
          <span>{{ dialogTitle }}</span>
        </div>
      </template>
      
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="modern-form">
        <el-form-item label="模型名称" prop="modelName">
          <el-input v-model="form.modelName" placeholder="请输入模型名称" class="modern-input" />
        </el-form-item>
        <el-form-item label="模型代码" prop="modelCode">
          <el-input v-model="form.modelCode" placeholder="如：openai、claude、qwen" class="modern-input" />
        </el-form-item>
        <el-form-item label="模型版本" prop="modelVersion">
          <el-input v-model="form.modelVersion" placeholder="如：gpt-4、claude-3-opus" class="modern-input" />
        </el-form-item>
        <el-form-item label="API Key" prop="apiKey">
          <el-input
            v-model="form.apiKey"
            :type="showApiKey ? 'text' : 'password'"
            placeholder="请输入API密钥"
            class="modern-input"
          >
            <template #append>
              <el-button @click="showApiKey = !showApiKey" class="password-toggle">
                <component :is="showApiKey ? EyeOff : Eye" class="w-4 h-4" />
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="API地址" prop="apiBaseUrl">
          <el-input v-model="form.apiBaseUrl" placeholder="如：https://api.openai.com/v1" class="modern-input" />
        </el-form-item>
        <el-form-item label="API端点" prop="apiEndpoint">
          <el-input v-model="form.apiEndpoint" placeholder="如：/chat/completions" class="modern-input" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最大Token" prop="maxTokens">
              <el-input-number v-model="form.maxTokens" :min="1" :max="100000" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-input-number v-model="form.priority" :min="0" :max="999" class="w-full" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="温度" prop="temperature">
              <el-input-number v-model="form.temperature" :min="0" :max="2" :step="0.1" :precision="2" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Top P" prop="topP">
              <el-input-number v-model="form.topP" :min="0" :max="1" :step="0.1" :precision="2" class="w-full" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" class="modern-input" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" class="modern-btn-secondary">取消</el-button>
          <el-button type="primary" @click="submitForm" class="modern-btn-gradient">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AiModelConfig">
import { ref, reactive, onMounted, computed, getCurrentInstance } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Cpu, Edit, Trash2, Zap, Star, Plus, RefreshCw, Shield, Eye, EyeOff } from 'lucide-vue-next'
import {
  listAiModel,
  getAiModel,
  addAiModel,
  updateAiModel,
  delAiModel,
  enableAiModel,
  disableAiModel,
  setDefaultAiModel,
  testAiModel
} from '@/api/thesis/aiModel'

const { proxy } = getCurrentInstance()

const modelList = ref([])
const loading = ref(true)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const showApiKey = ref(false)

const form = reactive({
  configId: null,
  modelName: '',
  modelCode: '',
  modelVersion: '',
  apiKey: '',
  apiBaseUrl: '',
  apiEndpoint: '',
  maxTokens: 4096,
  temperature: 0.7,
  topP: 0.9,
  priority: 50,
  remark: ''
})

const rules = {
  modelName: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  modelCode: [{ required: true, message: '请输入模型代码', trigger: 'blur' }],
  modelVersion: [{ required: true, message: '请输入模型版本', trigger: 'blur' }],
  apiBaseUrl: [{ required: true, message: '请输入API地址', trigger: 'blur' }]
}

// 获取列表
const getList = async () => {
  loading.value = true
  try {
    const res = await listAiModel({})
    // 计算优先级星级（0-100映射到0-5星）
    modelList.value = res.rows.map(item => ({
      ...item,
      priorityRate: Math.min(5, Math.floor(item.priority / 20))
    }))
  } finally {
    loading.value = false
  }
}

// 新增
const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增AI模型'
  dialogVisible.value = true
}

// 编辑
const handleEdit = async (row) => {
  resetForm()
  dialogTitle.value = '编辑AI模型'
  const res = await getAiModel(row.configId)
  Object.assign(form, res.data)
  dialogVisible.value = true
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该模型吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    await delAiModel(row.configId)
    ElMessage.success('删除成功')
    getList()
  })
}

// 状态切换
const handleStatusChange = async (row) => {
  try {
    if (row.isEnabled === '1') {
      await enableAiModel(row.configId)
      ElMessage.success('已启用')
    } else {
      await disableAiModel(row.configId)
      ElMessage.success('已禁用')
    }
    getList()
  } catch (error) {
    // 恢复原状态
    row.isEnabled = row.isEnabled === '1' ? '0' : '1'
  }
}

// 设为默认
const handleSetDefault = async (row) => {
  try {
    await setDefaultAiModel(row.configId)
    ElMessage.success('已设为默认模型')
    getList()
  } catch (error) {
    ElMessage.error('设置失败')
  }
}

// 测试连接
const handleTest = async (row) => {
  const loading = ElMessage({
    message: '正在测试连接...',
    type: 'info',
    duration: 0
  })
  try {
    const res = await testAiModel(row.configId)
    loading.close()
    ElMessage.success(res.msg || '连接测试成功')
  } catch (error) {
    loading.close()
    ElMessage.error('连接测试失败')
  }
}

// 提交表单
const submitForm = () => {
  proxy.$refs.formRef.validate(async (valid) => {
    if (valid) {
      if (form.configId) {
        await updateAiModel(form)
        ElMessage.success('修改成功')
      } else {
        await addAiModel(form)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      getList()
    }
  })
}

// 重置表单
const resetForm = () => {
  form.configId = null
  form.modelName = ''
  form.modelCode = ''
  form.modelVersion = ''
  form.apiKey = ''
  form.apiBaseUrl = ''
  form.apiEndpoint = ''
  form.maxTokens = 4096
  form.temperature = 0.7
  form.topP = 0.9
  form.priority = 50
  form.remark = ''
  showApiKey.value = false
  proxy.$refs.formRef?.resetFields()
}

onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped>
.modern-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.action-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.modern-btn-gradient {
  border-radius: 12px;
  padding: 0.625rem 1.5rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: all 0.3s;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  
  &:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  }
}

.modern-btn-outline {
  border-radius: 12px;
  padding: 0.625rem 1.5rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: all 0.3s;
  background: transparent;
  border: 2px solid white;
  color: white;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
  }
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  }
}

.model-card {
  &.is-default {
    border: 2px solid #fbbf24;
    box-shadow: 0 8px 32px rgba(251, 191, 36, 0.3);
  }
  
  &.is-disabled {
    opacity: 0.6;
    filter: grayscale(30%);
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    
    .model-title {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-weight: 600;
      font-size: 1.125rem;
      color: #1e293b;
      flex: 1;
      
      .model-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .model-badges {
        display: flex;
        gap: 0.5rem;
        margin-left: auto;
        
        .badge {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.25rem 0.75rem;
          border-radius: 8px;
          font-size: 0.75rem;
          font-weight: 500;
          
          &.badge-default {
            background: rgba(251, 191, 36, 0.1);
            color: #d97706;
          }
          
          &.badge-preset {
            background: rgba(99, 102, 241, 0.1);
            color: #6366f1;
          }
        }
      }
    }
  }
  
  .model-info {
    .info-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 0;
      
      .label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
      }
      
      .value {
        font-size: 0.875rem;
        color: #1e293b;
        font-weight: 600;
        
        &.text-muted {
          color: #94a3b8;
          font-weight: 400;
        }
      }
      
      .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 500;
        
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        
        &.status-success {
          background: rgba(34, 197, 94, 0.1);
          color: #16a34a;
          
          .status-dot {
            background: #16a34a;
            box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
          }
        }
        
        &.status-danger {
          background: rgba(239, 68, 68, 0.1);
          color: #dc2626;
          
          .status-dot {
            background: #dc2626;
          }
        }
      }
      
      .priority-stars {
        display: flex;
        gap: 0.25rem;
        
        .star-filled {
          color: #fbbf24;
          fill: #fbbf24;
        }
        
        .star-empty {
          color: #e2e8f0;
        }
      }
    }
  }
  
  .card-footer {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(0, 0, 0, 0.05);
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    
    .action-btn {
      flex: 1;
      min-width: 100px;
      border-radius: 12px;
      padding: 0.625rem 1rem;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s;
      background: white;
      border: 1px solid #e2e8f0;
      color: #64748b;
      font-size: 0.875rem;
      
      &:hover:not(:disabled) {
        background: #f8fafc;
        border-color: #cbd5e1;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      &.action-btn-danger {
        color: #dc2626;
        
        &:hover {
          background: rgba(239, 68, 68, 0.05);
          border-color: #fca5a5;
        }
      }
    }
  }
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

.modern-form {
  .modern-input {
    :deep(.el-input__wrapper) {
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      transition: all 0.3s;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      &.is-focus {
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
      }
    }
    
    :deep(.el-textarea__inner) {
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      transition: all 0.3s;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      &:focus {
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
      }
    }
  }
  
  .password-toggle {
    border: none;
    background: transparent;
    padding: 0 0.5rem;
    
    &:hover {
      background: rgba(99, 102, 241, 0.1);
    }
  }
  
  :deep(.el-input-number) {
    width: 100%;
    
    .el-input__wrapper {
      border-radius: 12px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.modern-btn-secondary {
  border-radius: 12px;
  padding: 0.625rem 1.5rem;
  font-weight: 500;
  background: white;
  border: 1px solid #e2e8f0;
  color: #64748b;
  transition: all 0.3s;
  
  &:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
}

.modern-btn-gradient {
  border-radius: 12px;
  padding: 0.625rem 1.5rem;
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  transition: all 0.3s;
  
  &:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  }
}
</style>
