<template>
  <div class="payment-config-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <CreditCard class="header-icon" />
        <div>
          <h1 class="header-title">支付配置</h1>
          <p class="header-subtitle">管理支付渠道和配置信息</p>
        </div>
      </div>
    </div>

    <!-- 支付渠道卡片 -->
    <div class="channels-grid">
      <div 
        v-for="channel in channels" 
        :key="channel.code" 
        class="channel-card"
        :class="{ 
          'channel-enabled': channel.enabled,
          'channel-mock': channel.isMock 
        }"
      >
        <!-- 卡片头部 -->
        <div class="card-header">
          <div class="channel-icon-wrapper" :style="{ background: channel.gradient }">
            <component :is="channel.icon" class="channel-icon" />
          </div>
          <div class="channel-info">
            <h3 class="channel-name">
              {{ channel.name }}
              <span v-if="channel.isMock" class="mock-badge">开发调试</span>
            </h3>
            <span class="channel-code">{{ channel.code }}</span>
          </div>
          <el-switch
            v-model="channel.enabled"
            @change="handleToggle(channel)"
            class="channel-switch"
          />
        </div>

        <!-- 卡片内容 -->
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">状态</span>
              <div class="status-badge" :class="channel.enabled ? 'status-active' : 'status-inactive'">
                <div class="status-dot"></div>
                <span>{{ channel.enabled ? '已启用' : '已禁用' }}</span>
              </div>
            </div>
            <div class="info-item">
              <span class="info-label">手续费率</span>
              <span class="info-value">{{ channel.feeRate }}%</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="card-actions">
            <button @click="handleEdit(channel)" class="btn btn-primary">
              <Settings class="btn-icon" />
              配置
            </button>
            <button @click="handleTest(channel)" class="btn btn-secondary" :disabled="!channel.enabled">
              <Zap class="btn-icon" />
              测试
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 配置对话框 -->
    <el-dialog 
      :title="`配置 ${currentChannel?.name}`" 
      v-model="configVisible" 
      width="700px"
      :close-on-click-modal="false"
      class="config-dialog"
    >
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="120px">
        <!-- 渠道代码（只读） -->
        <el-form-item label="渠道代码">
          <el-input v-model="configForm.provider_type" disabled>
            <template #suffix>
              <Lock class="input-icon" />
            </template>
          </el-input>
          <div class="form-tip">支付方式的唯一标识，不可修改</div>
        </el-form-item>

        <!-- 提供商名称 -->
        <el-form-item label="提供商名称">
          <el-input v-model="configForm.provider_name" placeholder="如：支付宝直连" />
        </el-form-item>

        <!-- 启用状态 -->
        <el-form-item label="启用状态">
          <el-switch 
            v-model="configForm.is_enabled" 
            active-value="1"
            inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>

        <!-- 手续费率 -->
        <el-form-item label="手续费率" prop="fee_rate">
          <el-input-number
            v-model="configForm.fee_rate"
            :min="0"
            :max="1"
            :precision="4"
            :step="0.0001"
            style="width: 100%"
          />
          <div class="form-tip">0.0060 = 0.6%，0.0100 = 1.0%</div>
        </el-form-item>

        <!-- 优先级 -->
        <el-form-item label="优先级">
          <el-input-number
            v-model="configForm.priority"
            :min="0"
            :max="999"
            style="width: 100%"
          />
          <div class="form-tip">数字越大优先级越高，用于多渠道选择</div>
        </el-form-item>

        <!-- 配置数据 -->
        <el-form-item label="配置数据">
          <el-input
            v-model="configDataStr"
            type="textarea"
            :rows="10"
            placeholder='JSON格式配置，例如：
{
  "app_id": "your_app_id",
  "api_key": "your_api_key",
  "notify_url": "https://yourdomain.com/notify"
}'
            class="config-textarea"
          />
          <div class="form-tip">
            <AlertCircle class="tip-icon" />
            请输入有效的JSON格式配置数据
          </div>
        </el-form-item>

        <!-- 备注 -->
        <el-form-item label="备注">
          <el-input
            v-model="configForm.remark"
            type="textarea"
            :rows="2"
            placeholder="可选的备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <button @click="configVisible = false" class="btn btn-cancel">取消</button>
          <button @click="submitConfig" class="btn btn-save">
            <Save class="btn-icon" />
            保存配置
          </button>
        </div>
      </template>
    </el-dialog>

    <!-- 测试对话框 -->
    <el-dialog 
      title="测试支付" 
      v-model="testVisible" 
      width="500px"
      :close-on-click-modal="false"
      class="test-dialog"
    >
      <div class="test-info">
        <div class="test-channel">
          <component :is="currentChannel?.icon" class="test-icon" />
          <span>{{ currentChannel?.name }}</span>
        </div>
      </div>

      <el-form :model="testForm" label-width="100px">
        <el-form-item label="测试金额">
          <el-input-number
            v-model="testForm.amount"
            :min="0.01"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="订单描述">
          <el-input
            v-model="testForm.subject"
            placeholder="测试订单"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <button @click="testVisible = false" class="btn btn-cancel">取消</button>
          <button @click="submitTest" :disabled="testLoading" class="btn btn-test">
            <Zap class="btn-icon" />
            {{ testLoading ? '测试中...' : '发起测试' }}
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="PaymentConfig">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CreditCard, Wallet, Banknote, Settings, Zap, Lock, Save, AlertCircle } from 'lucide-vue-next'
import { listPaymentConfig, getPaymentConfig, updatePaymentConfig, testPayment } from '@/api/thesis/payment'

const channels = ref([
  {
    code: 'alipay',
    name: '支付宝',
    icon: Wallet,
    gradient: 'linear-gradient(135deg, #1677ff 0%, #0050b3 100%)',
    enabled: false,
    feeRate: 0.6
  },
  {
    code: 'wechat',
    name: '微信支付',
    icon: Banknote,
    gradient: 'linear-gradient(135deg, #07c160 0%, #059669 100%)',
    enabled: false,
    feeRate: 0.6
  },
  {
    code: 'pingpp',
    name: 'Ping++',
    icon: CreditCard,
    gradient: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)',
    enabled: false,
    feeRate: 1.0
  },
  {
    code: 'mock',
    name: '模拟支付',
    icon: Zap,
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
    enabled: true,
    feeRate: 0.0,
    isMock: true  // 标记为模拟支付
  }
])

const configVisible = ref(false)
const testVisible = ref(false)
const testLoading = ref(false)
const currentChannel = ref(null)
const configDataStr = ref('')

const configForm = reactive({
  config_id: null,
  provider_type: null,
  provider_name: null,
  config_data: {},
  supported_channels: [],
  is_enabled: '0',
  fee_rate: 0.0060,
  priority: 0,
  remark: null
})

const testForm = reactive({
  channel: null,
  amount: 0.01,
  subject: '测试订单'
})

const configRules = {
  fee_rate: [{ required: true, message: '请输入手续费率', trigger: 'blur' }]
}

// 获取配置列表
const getConfigList = async () => {
  try {
    const res = await listPaymentConfig()
    res.data.forEach(config => {
      const channel = channels.value.find(c => c.code === config.provider_type)
      if (channel) {
        channel.enabled = config.is_enabled === '1'
        channel.feeRate = (config.fee_rate * 100).toFixed(2)
      }
    })
  } catch (error) {
    console.error('获取配置失败', error)
    if (error.message && error.message.includes('管理员')) {
      ElMessage.warning('仅管理员可以访问支付配置')
    }
  }
}

// 切换启用状态
const handleToggle = async (channel) => {
  try {
    const res = await getPaymentConfig(channel.code)
    if (res.data) {
      await updatePaymentConfig({
        ...res.data,
        is_enabled: channel.enabled ? '1' : '0'
      })
      ElMessage.success(channel.enabled ? '已启用' : '已禁用')
    } else {
      ElMessage.warning('请先配置该支付渠道')
      channel.enabled = false
    }
  } catch (error) {
    channel.enabled = !channel.enabled
    if (error.message && error.message.includes('管理员')) {
      ElMessage.warning('仅管理员可以修改支付配置')
    } else {
      ElMessage.error('操作失败')
    }
  }
}

// 编辑配置
const handleEdit = async (channel) => {
  currentChannel.value = channel
  try {
    const res = await getPaymentConfig(channel.code)
    if (res.data) {
      Object.assign(configForm, {
        config_id: res.data.config_id,
        provider_type: res.data.provider_type,
        provider_name: res.data.provider_name,
        config_data: res.data.config_data || {},
        supported_channels: res.data.supported_channels || [],
        is_enabled: res.data.is_enabled || '0',
        fee_rate: res.data.fee_rate || 0.0060,
        priority: res.data.priority || 0,
        remark: res.data.remark
      })
      configDataStr.value = JSON.stringify(configForm.config_data, null, 2)
    } else {
      resetConfigForm()
      configForm.provider_type = channel.code
      configForm.provider_name = channel.name
      configForm.fee_rate = channel.feeRate / 100
      configDataStr.value = '{}'
    }
    configVisible.value = true
  } catch (error) {
    if (error.message && error.message.includes('管理员')) {
      ElMessage.warning('仅管理员可以访问支付配置')
    } else {
      ElMessage.error('获取配置失败')
    }
  }
}

// 提交配置
const submitConfig = async () => {
  try {
    try {
      configForm.config_data = JSON.parse(configDataStr.value)
    } catch (e) {
      ElMessage.error('配置数据格式错误，请输入有效的JSON')
      return
    }
    
    await updatePaymentConfig(configForm)
    ElMessage.success('保存成功')
    configVisible.value = false
    getConfigList()
  } catch (error) {
    if (error.message && error.message.includes('管理员')) {
      ElMessage.warning('仅管理员可以修改支付配置')
    } else {
      ElMessage.error('保存失败')
    }
  }
}

// 测试支付
const handleTest = (channel) => {
  if (!channel.enabled) {
    ElMessage.warning('请先启用该支付渠道')
    return
  }
  currentChannel.value = channel
  testForm.channel = channel.code
  testForm.amount = 0.01
  testForm.subject = `测试${channel.name}支付`
  testVisible.value = true
}

// 提交测试
const submitTest = async () => {
  testLoading.value = true
  try {
    const res = await testPayment(testForm)
    ElMessageBox.alert(
      `<div style="padding: 20px;">
        <p style="margin-bottom: 10px;">✓ 测试订单创建成功</p>
        <p style="margin-bottom: 10px;">订单号: <strong>${res.data.orderNo}</strong></p>
        <p><a href="${res.data.payUrl}" target="_blank" style="color: #667eea;">点击支付 →</a></p>
      </div>`,
      '测试结果',
      {
        dangerouslyUseHTMLString: true,
        type: 'success'
      }
    )
    testVisible.value = false
  } catch (error) {
    if (error.message && error.message.includes('管理员')) {
      ElMessage.warning('仅管理员可以测试支付')
    } else {
      ElMessage.error('测试失败: ' + (error.message || '未知错误'))
    }
  } finally {
    testLoading.value = false
  }
}

// 重置配置表单
const resetConfigForm = () => {
  configForm.config_id = null
  configForm.provider_type = null
  configForm.provider_name = null
  configForm.config_data = {}
  configForm.supported_channels = []
  configForm.is_enabled = '0'
  configForm.fee_rate = 0.0060
  configForm.priority = 0
  configForm.remark = null
  configDataStr.value = '{}'
}

onMounted(() => {
  getConfigList()
})
</script>

<style scoped lang="scss">
.payment-config-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
  
  .header-content {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    padding: 2rem;
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    
    .header-icon {
      width: 48px;
      height: 48px;
      color: #667eea;
    }
    
    .header-title {
      font-size: 1.75rem;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 0.25rem 0;
    }
    
    .header-subtitle {
      font-size: 0.875rem;
      color: #64748b;
      margin: 0;
    }
  }
}

.channels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.channel-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  }
  
  &.channel-enabled {
    border-color: rgba(102, 126, 234, 0.3);
    background: rgba(255, 255, 255, 0.98);
  }
  
  &.channel-mock {
    border-color: rgba(245, 158, 11, 0.3);
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 251, 235, 0.95) 100%);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  
  .channel-icon-wrapper {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    
    .channel-icon {
      width: 32px;
      height: 32px;
      color: white;
    }
  }
  
  .channel-info {
    flex: 1;
    
    .channel-name {
      font-size: 1.25rem;
      font-weight: 600;
      color: #1e293b;
      margin: 0 0 0.25rem 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    
    .mock-badge {
      display: inline-flex;
      align-items: center;
      padding: 0.25rem 0.75rem;
      background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
      color: white;
      font-size: 0.75rem;
      font-weight: 500;
      border-radius: 8px;
      letter-spacing: 0.025em;
      box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
    }
    
    .channel-code {
      font-size: 0.875rem;
      color: #94a3b8;
      font-family: 'Courier New', monospace;
    }
  }
  
  .channel-switch {
    :deep(.el-switch__core) {
      height: 28px;
      border-radius: 14px;
    }
  }
}

.card-body {
  .info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
    
    .info-item {
      .info-label {
        display: block;
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      
      .info-value {
        font-size: 1.125rem;
        color: #1e293b;
        font-weight: 600;
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
        
        &.status-active {
          background: rgba(34, 197, 94, 0.1);
          color: #16a34a;
          
          .status-dot {
            background: #16a34a;
            box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
            animation: pulse 2s infinite;
          }
        }
        
        &.status-inactive {
          background: rgba(148, 163, 184, 0.1);
          color: #64748b;
          
          .status-dot {
            background: #94a3b8;
          }
        }
      }
    }
  }
  
  .card-actions {
    display: flex;
    gap: 0.75rem;
  }
}

.btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 500;
  font-size: 0.875rem;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  
  .btn-icon {
    width: 16px;
    height: 16px;
  }
  
  &.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
  }
  
  &.btn-secondary {
    background: white;
    color: #64748b;
    border: 1px solid #e2e8f0;
    
    &:hover:not(:disabled) {
      background: #f8fafc;
      border-color: #cbd5e1;
      transform: translateY(-2px);
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
  
  &.btn-cancel {
    background: white;
    color: #64748b;
    border: 1px solid #e2e8f0;
    
    &:hover {
      background: #f8fafc;
    }
  }
  
  &.btn-save, &.btn-test {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    
    &:hover {
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
  }
}

.form-tip {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  
  .tip-icon {
    width: 14px;
    height: 14px;
  }
}

.input-icon {
  width: 16px;
  height: 16px;
  color: #94a3b8;
}

.config-textarea {
  :deep(textarea) {
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.test-info {
  margin-bottom: 1.5rem;
  
  .test-channel {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 12px;
    
    .test-icon {
      width: 24px;
      height: 24px;
      color: #667eea;
    }
    
    span {
      font-weight: 600;
      color: #1e293b;
    }
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

:deep(.el-dialog) {
  border-radius: 24px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1.5rem 2rem;
  margin: 0;
  
  .el-dialog__title {
    color: white;
    font-weight: 600;
  }
  
  .el-dialog__headerbtn .el-dialog__close {
    color: white;
  }
}

:deep(.el-dialog__body) {
  padding: 2rem;
}

:deep(.el-dialog__footer) {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e2e8f0;
}
</style>
