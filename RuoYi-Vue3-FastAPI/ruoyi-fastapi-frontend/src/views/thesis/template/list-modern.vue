<template>
  <div class="modern-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <Layout :size="32" class="title-icon" />
          论文模板
        </h1>
        <p class="page-subtitle">选择合适的模板，让论文格式更规范</p>
      </div>
      <button class="btn-primary" @click="handleAdd">
        <Plus :size="20" />
        <span>上传模板</span>
      </button>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="search-bar glass-card">
      <div class="search-input-wrapper">
        <Search :size="20" class="search-icon" />
        <input
          v-model="queryParams.templateName"
          type="text"
          class="search-input"
          placeholder="搜索模板名称或学校..."
          @keyup.enter="handleQuery"
        />
      </div>
      
      <div class="filter-group">
        <button class="btn-secondary" @click="resetQuery">
          <RotateCcw :size="18" />
          <span>重置</span>
        </button>
      </div>
    </div>

    <!-- 模板网格 -->
    <div v-loading="loading" class="templates-grid">
      <div
        v-for="template in templateList"
        :key="template.templateId"
        class="template-card glass-card"
        @click="handlePreview(template)"
      >
        <!-- 模板缩略图 -->
        <div class="template-thumbnail">
          <img
            v-if="template.thumbnail"
            :src="template.thumbnail"
            :alt="template.templateName"
            class="thumbnail-image"
          />
          <div v-else class="thumbnail-placeholder">
            <FileText :size="48" />
          </div>
          
          <!-- 学位级别标签 -->
          <div class="degree-badge" :class="`degree-${getDegreeClass(template.degreeLevel)}`">
            <GraduationCap :size="14" />
            <span>{{ template.degreeLevel }}</span>
          </div>
        </div>

        <!-- 模板信息 -->
        <div class="template-info">
          <h3 class="template-name">{{ template.templateName }}</h3>
          <p class="template-school">
            <Building2 :size="14" />
            <span>{{ template.schoolName }}</span>
          </p>
          <p v-if="template.major" class="template-major">
            <BookOpen :size="14" />
            <span>{{ template.major }}</span>
          </p>
        </div>

        <!-- 统计信息 -->
        <div class="template-stats">
          <div class="stat-item">
            <Eye :size="14" />
            <span>{{ template.viewCount || 0 }}</span>
          </div>
          <div class="stat-item">
            <Star :size="14" />
            <span>{{ template.useCount || 0 }}</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="template-actions">
          <button class="btn-action btn-apply" @click.stop="handleApply(template)">
            <Check :size="16" />
            <span>应用</span>
          </button>
          <button class="icon-btn" @click.stop="handleEdit(template)" title="编辑">
            <Edit2 :size="16" />
          </button>
          <button class="icon-btn" @click.stop="handleDelete(template)" title="删除">
            <Trash2 :size="16" />
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && templateList.length === 0" class="empty-state">
        <Layout :size="64" class="empty-icon" />
        <h3 class="empty-title">还没有模板</h3>
        <p class="empty-desc">上传您的第一个论文模板</p>
        <button class="btn-primary" @click="handleAdd">
          <Plus :size="20" />
          <span>上传模板</span>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="700px"
      append-to-body
      class="modern-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="模板名称" prop="templateName">
          <el-input v-model="form.templateName" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="学校名称" prop="schoolName">
          <el-input v-model="form.schoolName" placeholder="请输入学校名称" />
        </el-form-item>
        <el-form-item label="专业" prop="major">
          <el-input v-model="form.major" placeholder="请输入专业（可选）" />
        </el-form-item>
        <el-form-item label="学位级别" prop="degreeLevel">
          <el-select v-model="form.degreeLevel" placeholder="请选择学位级别" style="width: 100%">
            <el-option label="本科" value="本科" />
            <el-option label="硕士" value="硕士" />
            <el-option label="博士" value="博士" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板文件" prop="filePath">
          <el-upload
            class="template-file-uploader"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="true"
            :limit="1"
            :on-success="handleTemplateFileSuccess"
            :before-upload="beforeTemplateUpload"
            accept=".docx,.doc"
          >
            <button type="button" class="btn-secondary">
              <Upload :size="18" />
              <span>上传Word模板</span>
            </button>
            <template #tip>
              <div class="upload-tip">
                只能上传 Word 文档（.doc/.docx），且不超过 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="缩略图">
          <el-upload
            class="thumbnail-uploader"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleThumbnailSuccess"
            accept="image/*"
          >
            <img v-if="form.thumbnail" :src="form.thumbnail" class="thumbnail-preview" />
            <div v-else class="thumbnail-upload-placeholder">
              <ImagePlus :size="32" />
              <span>上传缩略图</span>
            </div>
          </el-upload>
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

    <!-- 应用模板对话框 -->
    <el-dialog
      title="应用模板"
      v-model="applyVisible"
      width="500px"
      append-to-body
      class="modern-dialog"
    >
      <el-form :model="applyForm" label-width="100px">
        <el-form-item label="选择论文">
          <el-select v-model="applyForm.thesisId" placeholder="请选择论文" style="width: 100%">
            <el-option
              v-for="paper in paperList"
              :key="paper.thesisId"
              :label="paper.title"
              :value="paper.thesisId"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="btn-secondary" @click="applyVisible = false">取消</button>
        <button class="btn-primary" @click="submitApply">确定</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="TemplateListModern">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Layout, Plus, Search, RotateCcw, FileText, GraduationCap, Building2,
  BookOpen, Eye, Star, Check, Edit2, Trash2, Upload, ImagePlus
} from 'lucide-vue-next'
import { listTemplate, addTemplate, updateTemplate, delTemplate, applyTemplate } from '@/api/thesis/template'
import { listPaper } from '@/api/thesis/paper'
import { getToken } from '@/utils/auth'

const { proxy } = getCurrentInstance()

const uploadUrl = ref(import.meta.env.VITE_APP_BASE_API + '/common/upload')
const uploadHeaders = ref({ Authorization: 'Bearer ' + getToken() })

const templateList = ref([])
const paperList = ref([])
const loading = ref(true)
const total = ref(0)
const dialogVisible = ref(false)
const applyVisible = ref(false)
const dialogTitle = ref('')

const queryParams = reactive({
  pageNum: 1,
  pageSize: 12,
  templateName: null,
  schoolName: null
})

const form = reactive({
  templateId: null,
  templateName: '',
  schoolName: '',
  major: '',
  degreeLevel: '',
  filePath: '',
  fileName: '',
  thumbnail: '',
  remark: ''
})

const applyForm = reactive({
  templateId: null,
  thesisId: null
})

const rules = {
  templateName: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  schoolName: [{ required: true, message: '请输入学校名称', trigger: 'blur' }],
  degreeLevel: [{ required: true, message: '请选择学位级别', trigger: 'change' }]
}

const getList = async () => {
  loading.value = true
  try {
    const res = await listTemplate(queryParams)
    templateList.value = res.rows
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  queryParams.templateName = null
  queryParams.schoolName = null
  handleQuery()
}

const handleAdd = () => {
  dialogTitle.value = '上传模板'
  dialogVisible.value = true
  resetForm()
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑模板'
  dialogVisible.value = true
  Object.assign(form, row)
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该模板吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    await delTemplate(row.templateId)
    ElMessage.success('删除成功')
    getList()
  })
}

const handleApply = async (row) => {
  applyForm.templateId = row.templateId
  applyVisible.value = true
  const res = await listPaper({ pageNum: 1, pageSize: 100 })
  paperList.value = res.rows
}

const submitApply = async () => {
  if (!applyForm.thesisId) {
    ElMessage.warning('请选择论文')
    return
  }
  await applyTemplate(applyForm)
  ElMessage.success('应用成功')
  applyVisible.value = false
}

const handlePreview = (row) => {
  ElMessage.info('预览功能开发中')
}

const submitForm = () => {
  proxy.$refs.formRef.validate(async (valid) => {
    if (valid) {
      if (form.templateId) {
        await updateTemplate(form)
      } else {
        await addTemplate(form)
      }
      ElMessage.success('操作成功')
      dialogVisible.value = false
      getList()
    }
  })
}

const handleTemplateFileSuccess = (response, file) => {
  if (response.code === 200) {
    form.filePath = response.url
    form.fileName = file.name || response.fileName || response.url.split('/').pop()
    ElMessage.success('模板文件上传成功')
  } else {
    ElMessage.error(response.msg || '上传失败')
  }
}

const handleThumbnailSuccess = (response) => {
  if (response.code === 200) {
    form.thumbnail = response.url
    ElMessage.success('缩略图上传成功')
  } else {
    ElMessage.error(response.msg || '上传失败')
  }
}

const beforeTemplateUpload = (file) => {
  const isDoc = file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
                file.type === 'application/msword'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isDoc) {
    ElMessage.error('只能上传 Word 文档!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

const resetForm = () => {
  Object.assign(form, {
    templateId: null,
    templateName: '',
    schoolName: '',
    major: '',
    degreeLevel: '',
    filePath: '',
    fileName: '',
    thumbnail: '',
    remark: ''
  })
}

const getDegreeClass = (degree) => {
  const map = {
    '本科': 'bachelor',
    '硕士': 'master',
    '博士': 'doctor'
  }
  return map[degree] || 'bachelor'
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

.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
  transition: all 0.3s ease;
}

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

.filter-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.template-card {
  padding: 0;
  border-radius: 1rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -5px rgba(99, 102, 241, 0.3);
}

.template-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #A78BFA;
}

.degree-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.degree-bachelor {
  background: rgba(16, 185, 129, 0.9);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.degree-master {
  background: rgba(245, 158, 11, 0.9);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.degree-doctor {
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.template-info {
  padding: 1.5rem;
  flex: 1;
}

.template-name {
  font-family: 'Poppins', sans-serif;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1E1B4B;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.template-school,
.template-major {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748B;
  margin: 0.5rem 0;
}

.template-stats {
  display: flex;
  gap: 1.5rem;
  padding: 0 1.5rem 1rem;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
  padding-top: 1rem;
  margin: 0 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: #64748B;
}

.template-actions {
  display: flex;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
}

.btn-action {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-apply {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.btn-apply:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: #6366F1;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
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

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}

.thumbnail-uploader {
  .thumbnail-preview {
    width: 178px;
    height: 178px;
    display: block;
    object-fit: cover;
    border-radius: 0.75rem;
    border: 2px solid rgba(99, 102, 241, 0.2);
  }

  .thumbnail-upload-placeholder {
    width: 178px;
    height: 178px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background: rgba(99, 102, 241, 0.05);
    border: 2px dashed rgba(99, 102, 241, 0.3);
    border-radius: 0.75rem;
    cursor: pointer;
    transition: all 0.3s ease;
    color: #6366F1;
  }

  .thumbnail-upload-placeholder:hover {
    background: rgba(99, 102, 241, 0.1);
    border-color: #6366F1;
  }
}

.upload-tip {
  font-size: 0.875rem;
  color: #64748B;
  margin-top: 0.5rem;
}

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

  .templates-grid {
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
