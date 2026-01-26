<template>
  <div class="modern-container">
    <!-- 顶部搜索区 -->
    <div class="search-section glass-card">
      <el-form :model="queryParams" ref="queryRef" :inline="true">
      <el-form-item>
        <el-input
          v-model="queryParams.userName"
          placeholder="搜索用户名"
          clearable
          @keyup.enter="handleQuery"
          class="modern-input"
        >
          <template #prefix>
            <Search class="w-4 h-4" />
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-select
          v-model="queryParams.packageId"
          placeholder="会员等级"
          clearable
          class="modern-select"
        >
          <el-option
            v-for="pkg in packageList"
            :key="pkg.packageId"
            :label="pkg.packageName"
            :value="pkg.packageId"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-select
          v-model="queryParams.status"
          placeholder="状态"
          clearable
          class="modern-select"
        >
          <el-option label="正常" value="0" />
          <el-option label="过期" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleQuery" class="modern-btn">
          <Search class="w-4 h-4 mr-2" />
          搜索
        </el-button>
        <el-button @click="resetQuery" class="modern-btn-secondary">
          <RefreshCw class="w-4 h-4 mr-2" />
          重置
        </el-button>
      </el-form-item>
    </el-form>
    </div>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleAdd" class="modern-btn-gradient" v-hasPermi="['thesis:member:add']">
        <UserPlus class="w-4 h-4 mr-2" />
        开通会员
      </el-button>
      <el-button @click="handleUpdate" :disabled="single" class="modern-btn-outline" v-hasPermi="['thesis:member:edit']">
        <Edit class="w-4 h-4 mr-2" />
        修改
      </el-button>
      <el-button @click="handleDelete" :disabled="multiple" class="modern-btn-outline" v-hasPermi="['thesis:member:remove']">
        <Trash2 class="w-4 h-4 mr-2" />
        删除
      </el-button>
    </div>

    <!-- 用户会员列表 -->
    <div class="table-section glass-card">
    <el-table
      v-loading="loading"
      :data="memberList"
      @selection-change="handleSelectionChange"
      class="modern-table"
      :header-cell-style="{ background: 'transparent', color: '#1e293b', fontWeight: '600' }"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column label="用户ID" prop="userId" width="80" />
      <el-table-column label="用户名" prop="userName" width="120" />
      <el-table-column label="会员套餐" prop="packageName" width="150">
        <template #default="scope">
          <el-tag v-if="scope.row.packageName" type="success">
            {{ scope.row.packageName }}
          </el-tag>
          <span v-else class="text-muted">未开通</span>
        </template>
      </el-table-column>
      <el-table-column label="配额信息" min-width="200">
        <template #default="scope">
          <div class="quota-info">
            <div class="quota-item">
              <span class="quota-label">论文:</span>
              <el-progress
                :percentage="getQuotaPercent(scope.row.paperQuotaUsed, scope.row.paperQuotaTotal)"
                :color="getQuotaColor(scope.row.paperQuotaUsed, scope.row.paperQuotaTotal)"
              >
                <span class="quota-text">
                  {{ scope.row.paperQuotaUsed || 0 }}/{{ scope.row.paperQuotaTotal || 0 }}
                </span>
              </el-progress>
            </div>
            <div class="quota-item">
              <span class="quota-label">模板:</span>
              <el-progress
                :percentage="getQuotaPercent(scope.row.templateQuotaUsed, scope.row.templateQuotaTotal)"
                :color="getQuotaColor(scope.row.templateQuotaUsed, scope.row.templateQuotaTotal)"
              >
                <span class="quota-text">
                  {{ scope.row.templateQuotaUsed || 0 }}/{{ scope.row.templateQuotaTotal || 0 }}
                </span>
              </el-progress>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="有效期" width="200">
        <template #default="scope">
          <div v-if="scope.row.startTime && scope.row.endTime">
            <div>{{ scope.row.startTime }}</div>
            <div class="text-muted">至 {{ scope.row.endTime }}</div>
          </div>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" prop="status" width="100">
        <template #default="scope">
          <el-tag v-if="isExpired(scope.row.endTime)" type="danger">已过期</el-tag>
          <el-tag v-else-if="scope.row.packageId" type="success">正常</el-tag>
          <el-tag v-else type="info">未开通</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button
            link
            type="primary"
            icon="Edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['thesis:member:edit']"
          >编辑</el-button>
          <el-button
            link
            type="success"
            icon="Plus"
            @click="handleRenew(scope.row)"
            v-hasPermi="['thesis:member:renew']"
          >续费</el-button>
          <el-button
            link
            type="danger"
            icon="Delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['thesis:member:remove']"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <pagination
        v-show="total > 0"
        :total="total"
        v-model:page="queryParams.pageNum"
        v-model:limit="queryParams.pageSize"
        @pagination="getList"
      />
    </div>
    </div>

    <!-- 添加/修改对话框 -->
    <el-dialog :title="title" v-model="open" width="600px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户" prop="userId">
          <el-select
            v-model="form.userId"
            placeholder="请选择用户"
            filterable
            style="width: 100%"
            :disabled="form.memberId != null"
          >
            <el-option
              v-for="user in userList"
              :key="user.userId"
              :label="`${user.userName} (${user.nickName})`"
              :value="user.userId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="会员套餐" prop="packageId">
          <el-select
            v-model="form.packageId"
            placeholder="请选择会员套餐"
            style="width: 100%"
            @change="handlePackageChange"
          >
            <el-option
              v-for="pkg in packageList"
              :key="pkg.packageId"
              :label="`${pkg.packageName} - ¥${pkg.price}`"
              :value="pkg.packageId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="有效期" prop="duration">
          <el-input-number
            v-model="form.duration"
            :min="1"
            :max="365"
            placeholder="天数"
            style="width: 100%"
          />
          <div class="form-tip">开通天数，默认为套餐设置的天数</div>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancel">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 续费对话框 -->
    <el-dialog title="续费会员" v-model="renewVisible" width="500px" append-to-body>
      <el-form :model="renewForm" label-width="100px">
        <el-form-item label="当前套餐">
          <el-tag type="success">{{ renewForm.packageName }}</el-tag>
        </el-form-item>
        <el-form-item label="当前到期">
          <span>{{ renewForm.endTime }}</span>
        </el-form-item>
        <el-form-item label="续费天数">
          <el-input-number
            v-model="renewForm.duration"
            :min="1"
            :max="365"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="续费后到期">
          <span class="text-primary">{{ renewEndTime }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renewVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRenew">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="MemberUser">
import { ref, reactive, computed, onMounted, getCurrentInstance } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshCw, UserPlus, Edit, Trash2, Award, Calendar, TrendingUp } from 'lucide-vue-next'
import { listUserMember, getUserMember, addUserMember, updateUserMember, delUserMember, renewUserMember } from '@/api/thesis/member'
import { listPackage } from '@/api/thesis/member'
import { listUser } from '@/api/system/user'

const { proxy } = getCurrentInstance()

const memberList = ref([])
const packageList = ref([])
const userList = ref([])
const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref('')
const open = ref(false)
const renewVisible = ref(false)

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  userName: null,
  packageId: null,
  status: null
})

const form = reactive({
  memberId: null,
  userId: null,
  packageId: null,
  duration: 30,
  remark: null
})

const renewForm = reactive({
  memberId: null,
  packageName: '',
  endTime: '',
  duration: 30
})

const rules = {
  userId: [{ required: true, message: '请选择用户', trigger: 'change' }],
  packageId: [{ required: true, message: '请选择会员套餐', trigger: 'change' }],
  duration: [{ required: true, message: '请输入有效期', trigger: 'blur' }]
}

// 计算续费后到期时间
const renewEndTime = computed(() => {
  if (!renewForm.endTime || !renewForm.duration) return ''
  const date = new Date(renewForm.endTime)
  date.setDate(date.getDate() + renewForm.duration)
  return date.toISOString().split('T')[0]
})

// 获取列表
const getList = async () => {
  loading.value = true
  try {
    const res = await listUserMember(queryParams)
    memberList.value = res.rows
    total.value = res.total
  } finally {
    loading.value = false
  }
}

// 获取套餐列表
const getPackageList = async () => {
  const res = await listPackage({ pageNum: 1, pageSize: 100 })
  packageList.value = res.rows
}

// 获取用户列表
const getUserList = async () => {
  const res = await listUser({ pageNum: 1, pageSize: 1000 })
  userList.value = res.rows
}

// 搜索
const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

// 重置
const resetQuery = () => {
  proxy.resetForm('queryRef')
  handleQuery()
}

// 多选
const handleSelectionChange = (selection) => {
  ids.value = selection.map(item => item.memberId)
  single.value = selection.length !== 1
  multiple.value = !selection.length
}

// 新增
const handleAdd = () => {
  reset()
  open.value = true
  title.value = '开通会员'
}

// 修改
const handleUpdate = async (row) => {
  reset()
  const memberId = row.memberId || ids.value[0]
  const res = await getUserMember(memberId)
  Object.assign(form, res.data)
  open.value = true
  title.value = '修改会员'
}

// 删除
const handleDelete = (row) => {
  const memberIds = row.memberId ? [row.memberId] : ids.value
  ElMessageBox.confirm('确定要删除选中的会员记录吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    await delUserMember(memberIds)
    ElMessage.success('删除成功')
    getList()
  })
}

// 续费
const handleRenew = (row) => {
  renewForm.memberId = row.memberId
  renewForm.packageName = row.packageName
  renewForm.endTime = row.endTime
  renewForm.duration = 30
  renewVisible.value = true
}

// 提交续费
const submitRenew = async () => {
  await renewUserMember({
    memberId: renewForm.memberId,
    duration: renewForm.duration
  })
  ElMessage.success('续费成功')
  renewVisible.value = false
  getList()
}

// 套餐变更
const handlePackageChange = (packageId) => {
  const pkg = packageList.value.find(p => p.packageId === packageId)
  if (pkg) {
    form.duration = pkg.duration || 30
  }
}

// 提交表单
const submitForm = () => {
  proxy.$refs.formRef.validate(async (valid) => {
    if (valid) {
      if (form.memberId) {
        await updateUserMember(form)
        ElMessage.success('修改成功')
      } else {
        await addUserMember(form)
        ElMessage.success('开通成功')
      }
      open.value = false
      getList()
    }
  })
}

// 取消
const cancel = () => {
  open.value = false
  reset()
}

// 重置表单
const reset = () => {
  form.memberId = null
  form.userId = null
  form.packageId = null
  form.duration = 30
  form.remark = null
  proxy.resetForm('formRef')
}

// 计算配额百分比
const getQuotaPercent = (used, total) => {
  if (!total) return 0
  return Math.round((used / total) * 100)
}

// 获取配额颜色
const getQuotaColor = (used, total) => {
  const percent = getQuotaPercent(used, total)
  if (percent >= 90) return '#f5222d'
  if (percent >= 70) return '#faad14'
  return '#52c41a'
}

// 判断是否过期
const isExpired = (endTime) => {
  if (!endTime) return false
  return new Date(endTime) < new Date()
}

onMounted(() => {
  getList()
  getPackageList()
  getUserList()
})
</script>

<style scoped lang="scss">
.modern-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  margin-bottom: 1.5rem;
}

.search-section {
  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

.modern-input {
  width: 240px;
  :deep(.el-input__wrapper) {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
}

.modern-select {
  width: 200px;
  :deep(.el-input__wrapper) {
    border-radius: 12px;
  }
}

.modern-btn {
  border-radius: 12px;
  padding: 0.625rem 1.5rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  }
}

.modern-btn-secondary {
  @extend .modern-btn;
  background: white;
  border: 1px solid #e2e8f0;
  color: #64748b;
  
  &:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
}

.modern-btn-gradient {
  @extend .modern-btn;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  
  &:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  }
}

.modern-btn-outline {
  @extend .modern-btn;
  background: transparent;
  border: 2px solid white;
  color: white;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.action-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.table-section {
  .modern-table {
    :deep(.el-table__body-wrapper) {
      .el-table__row {
        transition: all 0.3s;
        
        &:hover {
          background: rgba(99, 102, 241, 0.05);
          transform: scale(1.01);
        }
      }
    }
  }
}

.quota-info {
  .quota-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .quota-label {
      width: 50px;
      font-size: 12px;
      color: #8c8c8c;
    }
    
    .el-progress {
      flex: 1;
    }
    
    .quota-text {
      font-size: 12px;
      color: #595959;
    }
  }
}

.pagination-wrapper {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}

.text-muted {
  color: #94a3b8;
}

.text-primary {
  color: #6366f1;
  font-weight: 500;
}

.form-tip {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}
</style>
