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
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" />
    </el-row>

    <el-table v-loading="loading" :data="studentList" border>
      <el-table-column label="ID" align="center" prop="id" width="70" />
      <el-table-column label="姓名" align="center" prop="name" min-width="90" show-overflow-tooltip />
      <el-table-column label="验证码" align="center" prop="verificationCode" width="180" show-overflow-tooltip />
      <el-table-column label="学校名称" align="center" prop="schoolName" min-width="120" show-overflow-tooltip />
      <el-table-column label="层次" align="center" prop="level" width="80" />
      <el-table-column label="专业" align="center" prop="major" min-width="100" show-overflow-tooltip />
      <el-table-column label="学习形式" align="center" prop="learningForm" width="90" show-overflow-tooltip />
      <el-table-column label="验证有效日期" align="center" prop="validUntil" width="120" />
      <el-table-column label="操作" align="center" width="180" fixed="right">
        <template #default="{ row }">
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
      @pagination="getList"
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
import { listStudent, importStudents, uploadPhoto, getReportImageBlob, getQrImageBlob } from '@/api/student/verification'
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

function getList() {
  loading.value = true
  listStudent(queryParams.value)
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
      saveAs(blob, `学籍验证码_${row.verificationCode || row.id}.png`)
      proxy.$modal.msgSuccess('二维码已下载')
    })
    .catch(() => {
      proxy.$modal.msgError('下载二维码失败')
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
