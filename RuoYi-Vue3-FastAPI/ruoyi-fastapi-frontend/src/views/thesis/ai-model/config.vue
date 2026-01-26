<template>
  <div class="app-container">
    <!-- 操作按钮 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['thesis:ai-model:add']"
        >新增模型</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Refresh"
          @click="getList"
        >刷新</el-button>
      </el-col>
    </el-row>

    <!-- 模型卡片网格 -->
    <div class="model-grid" v-loading="loading">
      <el-card
        v-for="model in modelList"
        :key="model.configId"
        class="model-card"
        :class="{ 'is-default': model.isDefault === '1', 'is-disabled': model.isEnabled === '0' }"
        shadow="hover"
      >
        <!-- 卡片头部 -->
        <template #header>
          <div class="card-header">
            <div class="model-title">
              <el-icon class="model-icon"><Cpu /></el-icon>
              <span>{{ model.modelName }}</span>
              <el-tag v-if="model.isDefault === '1'" type="success" size="small" class="ml-2">默认</el-tag>
              <el-tag v-if="model.isPreset === '1'" type="info" size="small" class="ml-2">预设</el-tag>
            </div>
            <el-switch
              v-model="model.isEnabled"
              active-value="1"
              inactive-value="0"
              @change="handleStatusChange(model)"
              v-hasPermi="['thesis:ai-model:edit']"
            />
          </div>
        </template>

        <!-- 卡片内容 -->
        <div class="model-info">
          <div class="info-row">
            <span class="label">模型类型：</span>
            <el-tag :type="model.modelType === 'language' ? 'primary' : 'warning'" size="small">
              {{ model.modelType === 'language' ? '语言模型' : '视觉模型' }}
            </el-tag>
          </div>
          <div class="info-row">
            <span class="label">模型版本：</span>
            <span class="value">{{ model.modelVersion }}</span>
          </div>
          <div class="info-row">
            <span class="label">提供商：</span>
            <el-tag size="small">{{ model.provider || model.modelCode }}</el-tag>
          </div>
          <div class="info-row">
            <span class="label">API状态：</span>
            <el-tag :type="model.apiKey ? 'success' : 'danger'" size="small">
              {{ model.apiKey ? '已配置' : '未配置' }}
            </el-tag>
          </div>
          <div class="info-row">
            <span class="label">优先级：</span>
            <el-rate v-model="model.priorityRate" disabled :max="5" />
          </div>
          <div class="info-row" v-if="model.remark">
            <span class="label">说明：</span>
            <span class="value text-muted">{{ model.remark }}</span>
          </div>
        </div>

        <!-- 卡片操作 -->
        <template #footer>
          <div class="card-footer">
            <el-button
              size="small"
              type="primary"
              link
              icon="Edit"
              @click="handleEdit(model)"
              v-hasPermi="['thesis:ai-model:edit']"
            >编辑</el-button>
            <el-button
              size="small"
              type="success"
              link
              icon="Connection"
              @click="handleTest(model)"
              v-hasPermi="['thesis:ai-model:test']"
              :disabled="!model.apiKey"
            >测试</el-button>
            <el-button
              size="small"
              type="warning"
              link
              icon="Star"
              @click="handleSetDefault(model)"
              v-hasPermi="['thesis:ai-model:edit']"
              v-if="model.isDefault !== '1' && model.isEnabled === '1'"
            >设为默认</el-button>
            <el-button
              size="small"
              type="danger"
              link
              icon="Delete"
              @click="handleDelete(model)"
              v-hasPermi="['thesis:ai-model:remove']"
              v-if="model.isPreset !== '1'"
            >删除</el-button>
          </div>
        </template>
      </el-card>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="600px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="模型类型" prop="modelType">
          <el-radio-group v-model="form.modelType">
            <el-radio label="language">语言模型</el-radio>
            <el-radio label="vision">视觉模型</el-radio>
          </el-radio-group>
          <div style="color: #909399; font-size: 12px; margin-top: 4px;">
            语言模型用于文本生成、论文写作；视觉模型用于图像识别、验证码识别
          </div>
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="form.provider" placeholder="请选择提供商" style="width: 100%">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic (Claude)" value="anthropic" />
            <el-option label="Qwen (通义千问)" value="qwen" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" prop="modelName">
          <el-input v-model="form.modelName" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="模型代码" prop="modelCode">
          <el-input v-model="form.modelCode" placeholder="如：openai、claude、qwen" />
        </el-form-item>
        <el-form-item label="模型版本" prop="modelVersion">
          <el-input v-model="form.modelVersion" placeholder="如：gpt-4o、claude-3-5-sonnet-20241022" />
        </el-form-item>
        <el-form-item label="API Key" prop="apiKey">
          <el-input
            v-model="form.apiKey"
            :type="showApiKey ? 'text' : 'password'"
            placeholder="请输入API密钥"
          >
            <template #append>
              <el-button :icon="showApiKey ? 'Hide' : 'View'" @click="showApiKey = !showApiKey" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="API地址" prop="apiBaseUrl">
          <el-input v-model="form.apiBaseUrl" placeholder="如：https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="API端点" prop="apiEndpoint">
          <el-input v-model="form.apiEndpoint" placeholder="如：/chat/completions" />
        </el-form-item>
        <el-row>
          <el-col :span="12">
            <el-form-item label="最大Token" prop="maxTokens">
              <el-input-number v-model="form.maxTokens" :min="1" :max="100000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-input-number v-model="form.priority" :min="0" :max="999" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="温度" prop="temperature">
              <el-input-number v-model="form.temperature" :min="0" :max="2" :step="0.1" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Top P" prop="topP">
              <el-input-number v-model="form.topP" :min="0" :max="1" :step="0.1" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AiModelConfig">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Cpu, Edit, Delete, Connection, Star, Plus, Refresh, View, Hide } from '@element-plus/icons-vue'
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
  modelType: 'language',
  provider: 'openai',
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
  modelType: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }],
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
  form.modelType = 'language'
  form.provider = 'openai'
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
.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.model-card {
  transition: all 0.3s;
  
  &.is-default {
    border-color: #67c23a;
  }
  
  &.is-disabled {
    opacity: 0.6;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .model-title {
      display: flex;
      align-items: center;
      font-weight: 600;
      font-size: 16px;
      
      .model-icon {
        margin-right: 8px;
        font-size: 20px;
        color: #409eff;
      }
    }
  }
  
  .model-info {
    .info-row {
      display: flex;
      align-items: center;
      margin-bottom: 12px;
      
      .label {
        color: #909399;
        min-width: 80px;
      }
      
      .value {
        flex: 1;
        color: #606266;
        
        &.text-muted {
          color: #909399;
          font-size: 13px;
        }
      }
    }
  }
  
  .card-footer {
    display: flex;
    justify-content: space-around;
    padding-top: 10px;
    border-top: 1px solid #ebeef5;
  }
}
</style>
