<template>
  <div class="verify-page">
    <div v-if="redirectMode" class="verify-card redirect-mode">
      <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
      <p class="loading-text">正在跳转备案表报告...</p>
    </div>
    <div v-else class="verify-card">
      <h1 class="title">学历备案表验证</h1>
      <p class="hint">请输入 16 位验证码进行查询</p>
      <div class="input-row">
        <el-input
          v-model="code"
          placeholder="验证码"
          maxlength="16"
          show-word-limit
          clearable
          size="large"
          class="code-input"
          @keyup.enter="handleCheck"
        />
        <el-button type="primary" size="large" :loading="loading" @click="handleCheck">查询</el-button>
      </div>

      <div v-if="result" class="result-area">
        <el-alert v-if="result.expired" type="warning" :title="result.message || '验证已过期'" show-icon />
        <template v-else>
          <p class="name">姓名：{{ result.name || '—' }}</p>
          <div v-if="result.reportImageUrl" class="report-wrap">
            <p class="report-label">学历备案表报告图</p>
            <img :src="result.reportImageUrl" alt="备案表报告" class="report-img" @error="onImgError" />
            <el-button type="primary" plain class="open-btn" @click="openReportPage">在新窗口打开报告图</el-button>
          </div>
        </template>
      </div>
      <div v-else-if="checked && !loading" class="empty-hint">请输入验证码并点击查询</div>
    </div>
  </div>
</template>

<script setup name="VerifyFilingPage">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { getVerifyFilingCheck } from '@/api/student/recordFiling'

const route = useRoute()
const hasCodeInUrl = !!(route.query?.code)
const code = ref(hasCodeInUrl ? String(route.query.code).trim().slice(0, 16) : '')
const loading = ref(false)
const result = ref(null)
const checked = ref(false)
const redirectMode = ref(hasCodeInUrl)

function handleCheck(isFromUrl = false) {
  const c = (code.value || '').trim()
  if (!c) {
    result.value = null
    checked.value = true
    if (isFromUrl) redirectMode.value = false
    return
  }
  loading.value = true
  result.value = null
  getVerifyFilingCheck(c)
    .then((res) => {
      checked.value = true
      const data = res.data || res
      const reportUrl = data?.reportImageUrl ?? data?.report_image_url
      const canRedirect = !data?.expired && (reportUrl || (data?.name && c))
      if (canRedirect) {
        const url = reportUrl || `${import.meta.env.VITE_APP_BASE_API || '/dev-api'}/verify/filing/report/image?code=${encodeURIComponent(c)}`
        window.location.replace(url)
        return
      }
      result.value = data
      if (isFromUrl) redirectMode.value = false
    })
    .catch((err) => {
      checked.value = true
      const msg = err?.response?.data?.msg || err?.message || '查询失败，请检查验证码或稍后重试'
      result.value = { expired: true, message: msg }
      if (isFromUrl) redirectMode.value = false
    })
    .finally(() => { loading.value = false })
}

function openReportPage() {
  if (result.value?.reportImageUrl) {
    window.open(result.value.reportImageUrl, '_blank', 'noopener,noreferrer')
  }
}

function onImgError() {
  if (result.value?.reportImageUrl) {
    window.open(result.value.reportImageUrl, '_blank', 'noopener,noreferrer')
  }
}

onMounted(() => {
  if (hasCodeInUrl) {
    handleCheck(true)
  }
})
</script>

<style scoped>
.verify-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.verify-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 32px;
  max-width: 560px;
  width: 100%;
}
.title {
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
}
.hint {
  margin: 0 0 20px;
  color: #909399;
  font-size: 14px;
}
.input-row {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.code-input {
  flex: 1;
}
.result-area {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
.result-area .name {
  margin: 0 0 16px;
  font-size: 16px;
  color: #303133;
}
.report-label {
  margin: 0 0 8px;
  font-size: 14px;
  color: #606266;
}
.report-wrap {
  margin-top: 12px;
}
.open-btn {
  margin-top: 12px;
}
.report-img {
  max-width: 100%;
  height: auto;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
}
.empty-hint {
  color: #909399;
  font-size: 14px;
  text-align: center;
  padding: 20px 0;
}
.redirect-mode {
  text-align: center;
}
.loading-icon {
  color: #409eff;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.loading-text {
  margin: 16px 0 0;
  color: #606266;
  font-size: 14px;
}
</style>
