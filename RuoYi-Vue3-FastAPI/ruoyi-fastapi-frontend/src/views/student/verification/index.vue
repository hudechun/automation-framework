<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="88px">
      <el-form-item label="姓名" prop="name">
        <el-input
          v-model="queryParams.name"
          placeholder="请输入姓名"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="验证码" prop="verificationCode">
        <el-input
          v-model="queryParams.verificationCode"
          placeholder="16位验证码"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Upload" @click="handleImport">导入</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="Download" @click="handleBatchDownloadQr">批量下载二维码</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="warning" plain icon="Document" @click="handleBatchDownloadReport">批量下载报告</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" />
    </el-row>

    <el-table ref="tableRef" v-loading="loading" :data="studentList" border @selection-change="handleSelectionChange" row-key="id">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="ID" align="center" prop="id" width="70" />
      <el-table-column label="姓名" align="center" prop="name" min-width="90" show-overflow-tooltip />
      <el-table-column label="验证码" align="center" prop="verificationCode" width="180" show-overflow-tooltip />
      <el-table-column label="学校名称" align="center" prop="schoolName" min-width="120" show-overflow-tooltip />
      <el-table-column label="层次" align="center" prop="level" width="80" />
      <el-table-column label="专业" align="center" prop="major" min-width="100" show-overflow-tooltip />
      <el-table-column label="学习形式" align="center" prop="learningForm" width="90" show-overflow-tooltip />
      <el-table-column label="验证有效日期" align="center" prop="validUntil" width="120" />
      <el-table-column label="操作" align="center" width="240" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="handleViewReport(row)">报告图</el-button>
          <el-button link type="primary" @click="handleDownloadQr(row)">二维码</el-button>
          <el-button link type="primary" @click="handleUploadPhoto(row)">上传照片</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="(e) => getList(e)"
    />

    <!-- 导入对话框 -->
    <el-dialog title="Excel 导入学生" v-model="importVisible" width="460px" append-to-body>
      <el-upload
        ref="uploadRef"
        :limit="1"
        accept=".xlsx,.xls"
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="importFileList"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">仅支持 xls、xlsx，表头需含：姓名、性别、出生日期、…、验证有效日期；照片列可为内嵌图片。</div>
          <div class="el-upload__tip date-format-tip">日期格式约定：XXXX年X月X日、YYYY-MM-DD、YYYY/MM/DD 或 Excel 日期；导入后统一存为 XXXX年XX月XX日</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="submitImport">确定导入</el-button>
      </template>
    </el-dialog>

    <!-- 上传照片 -->
    <el-dialog title="上传学生照片" v-model="uploadPhotoVisible" width="400px" append-to-body>
      <el-form label-width="90px">
        <el-form-item label="姓名">{{ uploadPhotoRow?.name }}</el-form-item>
        <el-form-item label="验证码">{{ uploadPhotoRow?.verificationCode }}</el-form-item>
        <el-form-item label="照片">
          <el-upload
            ref="photoUploadRef"
            :limit="1"
            accept=".png,.jpg,.jpeg"
            :auto-upload="false"
            :on-change="handlePhotoFileChange"
            :file-list="photoFileList"
          >
            <el-button type="primary">选择照片</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 png、jpg、jpeg，将保存到 uploads/pic/photo/{验证码}.png</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadPhotoVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploadPhotoLoading" @click="submitUploadPhoto">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑学生 -->
    <el-dialog title="编辑学生记录" v-model="editVisible" width="700px" append-to-body destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="editForm.name" placeholder="姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-input v-model="editForm.gender" placeholder="性别" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期" prop="birthDate">
              <el-date-picker v-model="editForm.birthDate" type="date" value-format="YYYY-MM-DD" placeholder="出生日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="民族" prop="nation">
              <el-input v-model="editForm.nation" placeholder="民族" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="学校名称" prop="schoolName">
              <el-input v-model="editForm.schoolName" placeholder="学校名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="层次" prop="level">
              <el-input v-model="editForm.level" placeholder="如：专科、本科" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-input v-model="editForm.major" placeholder="专业" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学制" prop="duration">
              <el-input v-model="editForm.duration" placeholder="如：3年" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学历类别" prop="educationType">
              <el-input v-model="editForm.educationType" placeholder="如：普通高等教育" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学习形式" prop="learningForm">
              <el-input v-model="editForm.learningForm" placeholder="如：全日制" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分院" prop="branch">
              <el-input v-model="editForm.branch" placeholder="分院" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="系所" prop="department">
              <el-input v-model="editForm.department" placeholder="系所" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入学日期" prop="enrollmentDate">
              <el-date-picker v-model="editForm.enrollmentDate" type="date" value-format="YYYY-MM-DD" placeholder="入学日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计毕业日期" prop="graduationDate">
              <el-date-picker v-model="editForm.graduationDate" type="date" value-format="YYYY-MM-DD" placeholder="预计毕业日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="验证有效日期" prop="validUntil" required>
              <el-date-picker v-model="editForm.validUntil" type="date" value-format="YYYY-MM-DD" placeholder="验证有效日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="验证码" prop="verificationCode">
              <el-input v-model="editForm.verificationCode" disabled placeholder="不可修改" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="editForm.remark" type="textarea" :rows="2" placeholder="备注" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="submitEdit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 报告图预览 -->
    <el-dialog
      v-model="reportVisible"
      title="学籍报告图"
      width="80%"
      append-to-body
      destroy-on-close
      class="report-dialog"
    >
      <div class="report-preview">
        <img v-if="reportImageUrl" :src="reportImageUrl" alt="报告图" style="max-width: 100%; height: auto;" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup name="StudentVerification">
import { listStudent, updateStudent, importStudents, uploadPhoto, getReportImageBlob, getQrImageBlob, batchDownloadQr, batchDownloadReport } from '@/api/student/verification'
import { saveAs } from 'file-saver'

const { proxy } = getCurrentInstance()
const studentList = ref([])
const loading = ref(true)
const showSearch = ref(true)
const total = ref(0)
const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  name: undefined,
  verificationCode: undefined
})
const importVisible = ref(false)
const importFileList = ref([])
const importSelectedFile = ref(null)
const importing = ref(false)
const uploadRef = ref(null)
const reportVisible = ref(false)
const reportImageUrl = ref('')
const uploadPhotoVisible = ref(false)
const uploadPhotoRow = ref(null)
const photoFileList = ref([])
const photoSelectedFile = ref(null)
const uploadPhotoLoading = ref(false)
const photoUploadRef = ref(null)
const tableRef = ref(null)
const selectedIds = ref([])
const editVisible = ref(false)
const editFormRef = ref(null)
const editLoading = ref(false)
const editForm = ref({
  id: null,
  verificationCode: '',
  name: '',
  gender: '',
  birthDate: '',
  nation: '',
  schoolName: '',
  level: '',
  major: '',
  duration: '',
  educationType: '',
  learningForm: '',
  branch: '',
  department: '',
  enrollmentDate: '',
  graduationDate: '',
  validUntil: '',
  remark: ''
})
const editRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  validUntil: [{ required: true, message: '请选择验证有效日期', trigger: 'change' }]
}

function safeFileName(name, code) {
  const n = (name || '').replace(/[/\\:*?"<>|]/g, '_').trim() || '未命名'
  return `${n}_${(code || '').trim()}.png`
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map((r) => r.id)
}

function getList(paginationEvent) {
  loading.value = true
  const params = { ...queryParams.value }
  if (paginationEvent && typeof paginationEvent.page === 'number') {
    params.pageNum = paginationEvent.page
    params.pageSize = paginationEvent.limit ?? params.pageSize
  }
  listStudent(params)
    .then((res) => {
      studentList.value = res.rows || []
      total.value = res.total ?? 0
    })
    .finally(() => { loading.value = false })
}

function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

function resetQuery() {
  proxy.resetForm('queryRef')
  handleQuery()
}

function handleImport() {
  importFileList.value = []
  importSelectedFile.value = null
  importVisible.value = true
}

function handleFileChange(file, fileList) {
  importSelectedFile.value = file.raw
  importFileList.value = fileList.slice(-1)
}

function submitImport() {
  const file = importSelectedFile.value
  if (!file || (!file.name.toLowerCase().endsWith('.xls') && !file.name.toLowerCase().endsWith('.xlsx'))) {
    proxy.$modal.msgError('请选择 xls 或 xlsx 文件')
    return
  }
  importing.value = true
  importStudents(file)
    .then((res) => {
      const msg = res.msg || `导入成功 ${res.data?.success ?? 0} 条，失败 ${res.data?.fail ?? 0} 条`
      if (res.data?.fail > 0 && res.data?.fail_details?.length) {
        proxy.$modal.msgWarning(msg + '\n' + res.data.fail_details.join('\n'))
      } else {
        proxy.$modal.msgSuccess(msg)
      }
      importVisible.value = false
      getList()
    })
    .catch(() => {})
    .finally(() => { importing.value = false })
}

function revokeReportUrl() {
  if (reportImageUrl.value) {
    URL.revokeObjectURL(reportImageUrl.value)
    reportImageUrl.value = ''
  }
}

function handleViewReport(row) {
  revokeReportUrl()
  getReportImageBlob(row.id)
    .then((blob) => {
      reportImageUrl.value = URL.createObjectURL(blob)
      reportVisible.value = true
    })
    .catch(() => {
      proxy.$modal.msgError('获取报告图失败')
    })
}

function handleDownloadQr(row) {
  getQrImageBlob(row.id)
    .then((blob) => {
      saveAs(blob, safeFileName(row.name, row.verificationCode))
      proxy.$modal.msgSuccess('二维码已下载')
    })
    .catch(() => {
      proxy.$modal.msgError('下载二维码失败')
    })
}

function handleBatchDownloadQr() {
  const ids = selectedIds.value
  if (!ids || ids.length === 0) {
    proxy.$modal.msgWarning('请先勾选要下载的学生')
    return
  }
  batchDownloadQr(ids)
    .then((blob) => {
      saveAs(blob, '学籍验证二维码.zip')
      proxy.$modal.msgSuccess(`已下载 ${ids.length} 个二维码`)
    })
    .catch(() => {
      proxy.$modal.msgError('批量下载失败')
    })
}

function handleBatchDownloadReport() {
  const ids = selectedIds.value
  if (!ids || ids.length === 0) {
    proxy.$modal.msgWarning('请先勾选要下载的学生')
    return
  }
  if (ids.length > 50) {
    proxy.$modal.msgWarning('单次最多选择 50 个学生')
    return
  }
  proxy.$modal.loading('正在生成报告，请稍候…')
  batchDownloadReport(ids)
    .then(async (blob) => {
      if (blob.type === 'application/json') {
        const text = await blob.text()
        let msg = '批量下载报告失败'
        try {
          const json = JSON.parse(text)
          if (json.msg) msg = json.msg
        } catch (_) {}
        proxy.$modal.msgError(msg)
        return
      }
      saveAs(blob, '学籍验证报告.zip')
      proxy.$modal.msgSuccess(`已下载 ${ids.length} 个验证报告`)
    })
    .catch((err) => {
      const msg = err?.response?.data?.msg || err?.msg || err?.message || '批量下载报告失败'
      proxy.$modal.msgError(typeof msg === 'string' ? msg : '批量下载报告失败')
    })
    .finally(() => {
      proxy.$modal.closeLoading()
    })
}

function handleEdit(row) {
  editForm.value = {
    id: row.id,
    verificationCode: row.verificationCode || '',
    name: row.name || '',
    gender: row.gender || '',
    birthDate: row.birthDate ? parseDateForEdit(row.birthDate) : '',
    nation: row.nation || '',
    schoolName: row.schoolName || '',
    level: row.level || '',
    major: row.major || '',
    duration: row.duration || '',
    educationType: row.educationType || '',
    learningForm: row.learningForm || '',
    branch: row.branch || '',
    department: row.department || '',
    enrollmentDate: row.enrollmentDate ? parseDateForEdit(row.enrollmentDate) : '',
    graduationDate: row.graduationDate ? parseDateForEdit(row.graduationDate) : '',
    validUntil: row.validUntil ? parseDateForEdit(row.validUntil) : '',
    remark: row.remark || ''
  }
  editVisible.value = true
}

function parseDateForEdit(val) {
  if (!val) return ''
  if (typeof val === 'string' && /^\d{4}-\d{2}-\d{2}/.test(val)) return val.substring(0, 10)
  const m = String(val).match(/(\d{4})年(\d{1,2})月(\d{1,2})日/)
  if (m) return `${m[1]}-${m[2].padStart(2, '0')}-${m[3].padStart(2, '0')}`
  return val
}

function submitEdit() {
  editFormRef.value?.validate((valid) => {
    if (!valid) return
    editLoading.value = true
    const payload = {
      name: editForm.value.name,
      gender: editForm.value.gender || undefined,
      birthDate: editForm.value.birthDate || undefined,
      nation: editForm.value.nation || undefined,
      schoolName: editForm.value.schoolName || undefined,
      level: editForm.value.level || undefined,
      major: editForm.value.major || undefined,
      duration: editForm.value.duration || undefined,
      educationType: editForm.value.educationType || undefined,
      learningForm: editForm.value.learningForm || undefined,
      branch: editForm.value.branch || undefined,
      department: editForm.value.department || undefined,
      enrollmentDate: editForm.value.enrollmentDate || undefined,
      graduationDate: editForm.value.graduationDate || undefined,
      validUntil: editForm.value.validUntil || undefined,
      remark: editForm.value.remark || undefined
    }
    Object.keys(payload).forEach((k) => payload[k] === undefined && delete payload[k])
    updateStudent(editForm.value.id, payload)
      .then(() => {
        proxy.$modal.msgSuccess('修改成功')
        editVisible.value = false
        getList()
      })
      .catch(() => {
        proxy.$modal.msgError('修改失败')
      })
      .finally(() => { editLoading.value = false })
  })
}

function handleUploadPhoto(row) {
  uploadPhotoRow.value = row
  photoFileList.value = []
  photoSelectedFile.value = null
  uploadPhotoVisible.value = true
}

function handlePhotoFileChange(file, fileList) {
  photoSelectedFile.value = file.raw
  photoFileList.value = fileList.slice(-1)
}

function submitUploadPhoto() {
  const row = uploadPhotoRow.value
  const file = photoSelectedFile.value
  if (!row?.verificationCode) {
    proxy.$modal.msgError('验证码不存在')
    return
  }
  if (!file || !file.name.toLowerCase().match(/\.(png|jpg|jpeg)$/)) {
    proxy.$modal.msgError('请选择 png、jpg 或 jpeg 格式的照片')
    return
  }
  uploadPhotoLoading.value = true
  uploadPhoto(row.verificationCode, file)
    .then((res) => {
      proxy.$modal.msgSuccess(res.msg || '上传成功')
      uploadPhotoVisible.value = false
    })
    .catch((err) => {
      const msg = err?.response?.data?.msg || err?.msg || err?.message || '上传失败'
      proxy.$modal.msgError(msg)
    })
    .finally(() => { uploadPhotoLoading.value = false })
}

onUnmounted(() => {
  revokeReportUrl()
})

onMounted(() => {
  getList()
})
</script>

<style scoped>
.report-dialog :deep(.el-dialog__body) {
  max-height: 75vh;
  overflow: auto;
}
.report-preview {
  text-align: center;
}
</style>
