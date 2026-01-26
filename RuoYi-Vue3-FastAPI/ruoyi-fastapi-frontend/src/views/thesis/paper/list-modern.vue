<template>
  <div class="modern-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <FileText :size="32" class="title-icon" />
          我的论文
        </h1>
        <p class="page-subtitle">AI 智能写作，让论文创作更简单</p>
      </div>
      <button class="btn-primary" @click="handleAdd">
        <Plus :size="20" />
        <span>新建论文</span>
      </button>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="search-bar glass-card">
      <div class="search-input-wrapper">
        <Search :size="20" class="search-icon" />
        <input
          v-model="queryParams.title"
          type="text"
          class="search-input"
          placeholder="搜索论文标题..."
          @keyup.enter="handleQuery"
        />
      </div>
      
      <div class="filter-group">
        <select v-model="queryParams.status" class="filter-select" @change="handleQuery">
          <option value="">全部状态</option>
          <option v-for="dict in thesis_status" :key="dict.value" :value="dict.value">
            {{ dict.label }}
          </option>
        </select>
        
        <select v-model="queryParams.type" class="filter-select" @change="handleQuery">
          <option value="">全部类型</option>
          <option v-for="dict in thesis_type" :key="dict.value" :value="dict.value">
            {{ dict.label }}
          </option>
        </select>
        
        <button class="btn-secondary" @click="resetQuery">
          <RotateCcw :size="18" />
          <span>重置</span>
        </button>
      </div>
    </div>

    <!-- 论文卡片网格 -->
    <div v-loading="loading" class="papers-grid">
      <div
        v-for="paper in paperList"
        :key="paper.thesisId"
        class="paper-card glass-card"
        @click="handleRowClick(paper)"
      >
        <!-- 卡片头部 -->
        <div class="card-header">
          <div class="paper-type-badge" :class="`type-${paper.type}`">
            {{ getTypeLabel(paper.type) }}
          </div>
          <div class="card-actions">
            <button class="icon-btn" @click.stop="handleEdit(paper)" title="编辑">
              <Edit2 :size="16" />
            </button>
            <button class="icon-btn" @click.stop="handleDelete(paper)" title="删除">
              <Trash2 :size="16" />
            </button>
          </div>
        </div>

        <!-- 论文标题 -->
        <h3 class="paper-title">{{ paper.title }}</h3>

        <!-- 论文信息 -->
        <div class="paper-meta">
          <div class="meta-item">
            <Calendar :size="14" />
            <span>{{ formatDate(paper.createTime) }}</span>
          </div>
          <div class="meta-item">
            <FileText :size="14" />
            <span>{{ paper.wordCount || 0 }} 字</span>
          </div>
        </div>

        <!-- 进度条 -->
        <div class="progress-section">
          <div class="progress-header">
            <span class="progress-label">完成进度</span>
            <span class="progress-value">{{ calculateProgress(paper) }}%</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: calculateProgress(paper) + '%' }"
              :class="getProgressClass(paper)"
            ></div>
          </div>
        </div>

        <!-- 状态标签 -->
        <div class="card-footer">
          <span class="status-badge" :class="`status-${paper.status}`">
            {{ getStatusLabel(paper.status) }}
          </span>
          
          <button
            v-if="['draft', 'outline_completed'].includes(paper.status)"
            class="btn-action"
            @click.stop="handleGenerate(paper)"
          >
            <Sparkles :size="16" />
            <span>生成</span>
          </button>
          
          <button
            v-if="paper.status === 'completed'"
            class="btn-action"
            @click.stop="handleExportSingle(paper)"
          >
            <Download :size="16" />
            <span>导出</span>
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && paperList.length === 0" class="empty-state">
        <FileText :size="64" class="empty-icon" />
        <h3 class="empty-title">还没有论文</h3>
        <p class="empty-desc">点击"新建论文"开始创作您的第一篇论文</p>
        <button class="btn-primary" @click="handleAdd">
          <Plus :size="20" />
          <span>新建论文</span>
        </button>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination-wrapper">
      <pagination
        :total="total"
        v-model:page="queryParams.pageNum"
        v-model:limit="queryParams.pageSize"
        @pagination="getList"
      />
    </div>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="800px"
      append-to-body
      class="modern-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="论文标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入论文标题" maxlength="200" />
        </el-form-item>
        <el-form-item label="论文类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择论文类型" style="width: 100%">
            <el-option
              v-for="dict in thesis_type"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="研究方向" prop="researchField">
          <el-input v-model="form.researchField" placeholder="请输入研究方向" />
        </el-form-item>
        <el-form-item label="关键词" prop="keywords">
          <el-input
            v-model="form.keywords"
            type="textarea"
            :rows="2"
            placeholder="请输入关键词，多个关键词用逗号分隔"
          />
        </el-form-item>
        <el-form-item label="摘要" prop="abstract">
          <el-input
            v-model="form.abstract"
            type="textarea"
            :rows="4"
            placeholder="请输入论文摘要"
          />
        </el-form-item>
        <el-form-item label="目标字数" prop="targetWordCount">
          <el-input-number
            v-model="form.targetWordCount"
            :min="1000"
            :max="100000"
            :step="1000"
            style="width: 100%"
          />
          <span class="form-tip">建议：本科8000-12000字，硕士20000-30000字</span>
        </el-form-item>
        <el-form-item label="应用模板">
          <el-select
            v-model="form.templateId"
            placeholder="选择模板（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="template in templateList"
              :key="template.templateId"
              :label="`${template.templateName} - ${template.schoolName} (${template.degreeLevel})`"
              :value="template.templateId"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ template.templateName }}</span>
                <el-tag size="small" :type="template.degreeLevel === '博士' ? 'danger' : template.degreeLevel === '硕士' ? 'warning' : 'success'">
                  {{ template.degreeLevel }}
                </el-tag>
              </div>
              <div style="font-size: 12px; color: #8c8c8c; margin-top: 4px;">
                {{ template.schoolName }}{{ template.major ? ' - ' + template.major : '' }}
              </div>
            </el-option>
          </el-select>
          <span class="form-tip" v-if="form.templateId">
            选择模板后，论文将按照该模板的格式要求生成
          </span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="btn-secondary" @click="dialogVisible = false">取消</button>
        <button class="btn-primary" @click="submitForm">确定</button>
      </template>
    </el-dialog>

    <!-- 生成对话框 -->
    <el-dialog
      title="生成论文"
      v-model="generateVisible"
      width="600px"
      append-to-body
      class="modern-dialog generate-dialog"
    >
      <div class="generate-steps">
        <div class="step" :class="{ active: generateStep >= 0, completed: generateStep > 0 }">
          <div class="step-icon">
            <FileText v-if="generateStep === 0" :size="24" />
            <Check v-else :size="24" />
          </div>
          <span class="step-label">生成大纲</span>
        </div>
        <div class="step-line" :class="{ active: generateStep > 0 }"></div>
        <div class="step" :class="{ active: generateStep >= 2, completed: generateStep > 2 }">
          <div class="step-icon">
            <Edit3 v-if="generateStep < 3" :size="24" />
            <Check v-else :size="24" />
          </div>
          <span class="step-label">生成内容</span>
        </div>
        <div class="step-line" :class="{ active: generateStep > 2 }"></div>
        <div class="step" :class="{ active: generateStep >= 4 }">
          <div class="step-icon">
            <CheckCircle :size="24" />
          </div>
          <span class="step-label">完成</span>
        </div>
      </div>

      <div class="generate-content">
        <div v-if="generateStep === 0" class="step-content">
          <Sparkles :size="48" class="content-icon" />
          <p class="content-text">准备生成论文大纲...</p>
          <button class="btn-primary" @click="startGenerateOutline">开始生成大纲</button>
        </div>

        <div v-if="generateStep === 1" class="step-content">
          <Loader :size="48" class="content-icon loading" />
          <p class="content-text">正在生成大纲，请稍候...</p>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: outlineProgress + '%' }"></div>
          </div>
        </div>

        <div v-if="generateStep === 2" class="step-content">
          <CheckCircle :size="48" class="content-icon success" />
          <p class="content-text">大纲生成完成！</p>
          <button class="btn-primary" @click="startGenerateContent">开始生成内容</button>
        </div>

        <div v-if="generateStep === 3" class="step-content">
          <Loader :size="48" class="content-icon loading" />
          <p class="content-text">正在生成论文内容，请稍候...</p>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: contentProgress + '%' }"></div>
          </div>
          <p class="progress-text">已生成 {{ generatedChapters }}/{{ totalChapters }} 章节</p>
        </div>

        <div v-if="generateStep === 4" class="step-content">
          <CheckCircle :size="48" class="content-icon success" />
          <p class="content-text">论文生成完成！</p>
          <button class="btn-primary" @click="viewPaper">查看论文</button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup name="PaperListModern">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  FileText, Plus, Search, RotateCcw, Edit2, Trash2, Calendar,
  Download, Sparkles, Loader, CheckCircle, Check, Edit3
} from 'lucide-vue-next'
import { listPaper, getPaper, addPaper, updatePaper, delPaper, generateOutline, batchGenerateChapters } from '@/api/thesis/paper'
import { listTemplate } from '@/api/thesis/template'

const { proxy } = getCurrentInstance()
const { thesis_status, thesis_type } = proxy.useDict('thesis_status', 'thesis_type')

const paperList = ref([])
const templateList = ref([])
const loading = ref(true)
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const generateVisible = ref(false)
const generateStep = ref(0)
const outlineProgress = ref(0)
const contentProgress = ref(0)
const generatedChapters = ref(0)
const totalChapters = ref(0)
const currentPaper = ref(null)

const queryParams = reactive({
  pageNum: 1,
  pageSize: 12,
  title: null,
  status: null,
  type: null
})

const form = reactive({
  thesisId: null,
  title: '',
  type: '',
  researchField: '',
  keywords: '',
  abstract: '',
  targetWordCount: 10000,
  templateId: null,
  remark: ''
})

const rules = {
  title: [{ required: true, message: '请输入论文标题', trigger: 'blur' }],
  type: [{ required: true, message: '请选择论文类型', trigger: 'change' }],
  targetWordCount: [{ required: true, message: '请输入目标字数', trigger: 'blur' }]
}

// 获取列表
const getList = async () => {
  loading.value = true
  try {
    const res = await listPaper(queryParams)
    paperList.value = res.rows
    total.value = res.total
  } finally {
    loading.value = false
  }
}

// 搜索
const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

// 重置
const resetQuery = () => {
  queryParams.title = null
  queryParams.status = null
  queryParams.type = null
  handleQuery()
}

// 新增
const handleAdd = async () => {
  dialogTitle.value = '新建论文'
  dialogVisible.value = true
  resetForm()
  await loadTemplates()
}

// 编辑
const handleEdit = async (row) => {
  dialogTitle.value = '编辑论文'
  dialogVisible.value = true
  Object.assign(form, row)
  await loadTemplates()
}

// 加载模板列表
const loadTemplates = async () => {
  try {
    const res = await listTemplate({ pageNum: 1, pageSize: 100 })
    templateList.value = res.rows || []
  } catch (error) {
    console.error('加载模板列表失败:', error)
    templateList.value = []
  }
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该论文吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    await delPaper(row.thesisId)
    ElMessage.success('删除成功')
    getList()
  })
}

// 提交表单
const submitForm = () => {
  proxy.$refs.formRef.validate(async (valid) => {
    if (valid) {
      if (form.thesisId) {
        await updatePaper(form)
      } else {
        await addPaper(form)
      }
      ElMessage.success('操作成功')
      dialogVisible.value = false
      getList()
    }
  })
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    thesisId: null,
    title: '',
    type: '',
    researchField: '',
    keywords: '',
    abstract: '',
    targetWordCount: 10000,
    templateId: null,
    remark: ''
  })
}

// 行点击
const handleRowClick = (row) => {
  // TODO: 跳转到论文详情页
}

// 生成论文
const handleGenerate = (row) => {
  currentPaper.value = row
  generateVisible.value = true
  generateStep.value = 0
}

// 开始生成大纲
const startGenerateOutline = async () => {
  generateStep.value = 1
  outlineProgress.value = 0

  const timer = setInterval(() => {
    outlineProgress.value += 10
    if (outlineProgress.value >= 100) {
      clearInterval(timer)
      generateStep.value = 2
    }
  }, 500)

  try {
    await generateOutline(currentPaper.value.thesisId)
  } catch (error) {
    clearInterval(timer)
    ElMessage.error('大纲生成失败')
  }
}

// 开始生成内容
const startGenerateContent = async () => {
  generateStep.value = 3
  contentProgress.value = 0
  generatedChapters.value = 0
  totalChapters.value = 6

  const timer = setInterval(() => {
    if (generatedChapters.value < totalChapters.value) {
      generatedChapters.value++
      contentProgress.value = Math.floor((generatedChapters.value / totalChapters.value) * 100)
    } else {
      clearInterval(timer)
      generateStep.value = 4
    }
  }, 2000)

  try {
    await batchGenerateChapters({
      thesisId: currentPaper.value.thesisId,
      chapterIds: []
    })
  } catch (error) {
    clearInterval(timer)
    ElMessage.error('内容生成失败')
  }
}

// 查看论文
const viewPaper = () => {
  generateVisible.value = false
  getList()
}

// 导出单个
const handleExportSingle = (row) => {
  ElMessage.info('导出功能开发中')
}

// 导出
const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

// 计算进度
const calculateProgress = (row) => {
  const statusMap = {
    'draft': 0,
    'outline_generating': 20,
    'outline_completed': 40,
    'content_generating': 70,
    'completed': 100,
    'failed': 0
  }
  return statusMap[row.status] || 0
}

// 获取进度类
const getProgressClass = (row) => {
  const progress = calculateProgress(row)
  if (progress === 100) return 'progress-success'
  if (progress >= 50) return 'progress-primary'
  return 'progress-warning'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labelMap = {
    'draft': '草稿',
    'outline_generating': '大纲生成中',
    'outline_completed': '大纲已完成',
    'content_generating': '内容生成中',
    'completed': '已完成',
    'failed': '生成失败'
  }
  return labelMap[status] || status
}

// 获取类型标签
const getTypeLabel = (type) => {
  const dict = thesis_type.value.find(d => d.value === type)
  return dict ? dict.label : type
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
/* 导入 Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Open+Sans:wght@300;400;500;600;700&display=swap');

/* 容器 */
.modern-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
  padding: 2rem;
  font-family: 'Open Sans', sans-serif;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-content {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-family: 'Poppins', sans-serif;
  font-size: 2.25rem;
  font-weight: 700;
  color: #1E1B4B;
  margin: 0 0 0.5rem 0;
}

.title-icon {
  color: #6366F1;
}

.page-subtitle {
  font-size: 1rem;
  color: #64748B;
  margin: 0;
}

/* 按钮 */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
  color: white;
  padding: 0.875rem 1.75rem;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 1rem;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
  font-family: 'Poppins', sans-serif;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  color: #6366F1;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(99, 102, 241, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: #6366F1;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  border: 1px solid rgba(99, 102, 241, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-action:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: #6366F1;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #64748B;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.9);
  color: #6366F1;
  border-color: #6366F1;
}

/* 玻璃卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
  transition: all 0.3s ease;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-input-wrapper {
  flex: 1;
  min-width: 300px;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: #94A3B8;
}

.search-input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 0.75rem;
  font-size: 1rem;
  color: #1E1B4B;
  transition: all 0.3s ease;
  font-family: 'Open Sans', sans-serif;
}

.search-input:focus {
  outline: none;
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: rgba(255, 255, 255, 0.9);
}

.search-input::placeholder {
  color: #94A3B8;
}

.filter-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.filter-select {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 0.75rem;
  font-size: 0.875rem;
  color: #1E1B4B;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Open Sans', sans-serif;
}

.filter-select:focus {
  outline: none;
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* 论文网格 */
.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* 论文卡片 */
.paper-card {
  padding: 1.5rem;
  border-radius: 1rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.paper-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -5px rgba(99, 102, 241, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.paper-type-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.type-bachelor {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.type-master {
  background: rgba(245, 158, 11, 0.1);
  color: #D97706;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.type-doctor {
  background: rgba(239, 68, 68, 0.1);
  color: #DC2626;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.paper-title {
  font-family: 'Poppins', sans-serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1E1B4B;
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.paper-meta {
  display: flex;
  gap: 1.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748B;
}

/* 进度部分 */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-label {
  font-size: 0.875rem;
  color: #64748B;
  font-weight: 500;
}

.progress-value {
  font-size: 0.875rem;
  color: #6366F1;
  font-weight: 600;
}

.progress-bar {
  width: 100%;
  height: 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.progress-success {
  background: linear-gradient(90deg, #10B981 0%, #34D399 100%);
}

.progress-primary {
  background: linear-gradient(90deg, #6366F1 0%, #818CF8 100%);
}

.progress-warning {
  background: linear-gradient(90deg, #F59E0B 0%, #FBBF24 100%);
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.status-draft {
  background: rgba(148, 163, 184, 0.1);
  color: #475569;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.status-outline_generating,
.status-content_generating {
  background: rgba(245, 158, 11, 0.1);
  color: #D97706;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-outline_completed {
  background: rgba(99, 102, 241, 0.1);
  color: #4F46E5;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.status-completed {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-failed {
  background: rgba(239, 68, 68, 0.1);
  color: #DC2626;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
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
  margin: 0 0 2rem 0;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}

/* 生成对话框 */
.generate-dialog {
  .generate-steps {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 3rem;
    padding: 0 2rem;
  }

  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .step-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(148, 163, 184, 0.1);
    color: #94A3B8;
    transition: all 0.3s ease;
  }

  .step.active .step-icon {
    background: rgba(99, 102, 241, 0.1);
    color: #6366F1;
  }

  .step.completed .step-icon {
    background: rgba(16, 185, 129, 0.1);
    color: #10B981;
  }

  .step-label {
    font-size: 0.875rem;
    color: #64748B;
    font-weight: 500;
  }

  .step-line {
    width: 4rem;
    height: 2px;
    background: rgba(148, 163, 184, 0.2);
    margin: 0 1rem;
    transition: all 0.3s ease;
  }

  .step-line.active {
    background: rgba(99, 102, 241, 0.3);
  }

  .generate-content {
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .step-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    text-align: center;
    width: 100%;
  }

  .content-icon {
    color: #6366F1;
  }

  .content-icon.loading {
    animation: spin 1s linear infinite;
  }

  .content-icon.success {
    color: #10B981;
  }

  .content-text {
    font-size: 1.125rem;
    color: #1E1B4B;
    font-weight: 500;
    margin: 0;
  }

  .progress-text {
    font-size: 0.875rem;
    color: #64748B;
    margin: 0;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .modern-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .page-title {
    font-size: 1.75rem;
  }

  .search-bar {
    flex-direction: column;
  }

  .search-input-wrapper {
    min-width: 100%;
  }

  .filter-group {
    width: 100%;
    flex-wrap: wrap;
  }

  .filter-select {
    flex: 1;
  }

  .papers-grid {
    grid-template-columns: 1fr;
  }
}

/* 表单提示 */
.form-tip {
  font-size: 0.875rem;
  color: #64748B;
  margin-left: 0.5rem;
}

/* 动画 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
