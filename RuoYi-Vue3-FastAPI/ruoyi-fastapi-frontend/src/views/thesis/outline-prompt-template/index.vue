<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="100px">
      <el-form-item label="模板名称" prop="name">
        <el-input
          v-model="queryParams.name"
          placeholder="请输入模板名称"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="关联格式模板" prop="formatTemplateId">
        <el-select v-model="queryParams.formatTemplateId" placeholder="全部" clearable style="width: 200px">
          <el-option label="全局默认" :value="null" />
          <el-option
            v-for="t in formatTemplateOptions"
            :key="t.templateId"
            :label="t.templateName || t.name || ('ID:' + t.templateId)"
            :value="t.templateId"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="全部" clearable>
          <el-option label="正常" value="0" />
          <el-option label="停用" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          size="mini"
          @click="handleAdd"
          v-hasPermi="['thesis:outline-prompt-template:add']"
        >新增</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="dataList">
      <el-table-column label="ID" align="center" prop="promptTemplateId" width="80" />
      <el-table-column label="模板名称" align="center" prop="name" min-width="140" :show-overflow-tooltip="true" />
      <el-table-column label="关联格式模板" align="center" prop="formatTemplateId" width="160">
        <template #default="scope">
          <span v-if="scope.row.formatTemplateId == null">全局默认</span>
          <span v-else>{{ scope.row.formatTemplateName || getFormatTemplateName(scope.row.formatTemplateId) || 'ID:' + scope.row.formatTemplateId }}</span>
        </template>
      </el-table-column>
      <el-table-column label="是否默认" align="center" prop="isDefault" width="90">
        <template #default="scope">
          <el-tag :type="scope.row.isDefault === '1' ? 'success' : 'info'">{{ scope.row.isDefault === '1' ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" prop="status" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'info'">{{ scope.row.status === '0' ? '正常' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="备注" align="center" prop="remark" min-width="120" :show-overflow-tooltip="true" />
      <el-table-column label="创建时间" align="center" prop="createTime" width="165">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d} {h}:{i}:{s}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="220" fixed="right">
        <template #default="scope">
          <el-button size="mini" type="text" icon="View" @click="handleView(scope.row)">查看</el-button>
          <el-button
            size="mini"
            type="text"
            icon="Edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['thesis:outline-prompt-template:edit']"
          >修改</el-button>
          <el-button
            size="mini"
            type="text"
            icon="Delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['thesis:outline-prompt-template:remove']"
          >删除</el-button>
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

    <!-- 新增/修改对话框 -->
    <el-dialog :title="title" v-model="open" width="900px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入模板名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="关联格式模板" prop="formatTemplateId">
          <el-select v-model="form.formatTemplateId" placeholder="空表示全局默认" clearable style="width: 100%">
            <el-option
              v-for="t in formatTemplateOptions"
              :key="t.templateId"
              :label="t.templateName || t.name || ('ID:' + t.templateId)"
              :value="t.templateId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="提示词正文" prop="templateContent">
          <el-input v-model="form.templateContent" type="textarea" :rows="12" placeholder="支持占位符：{{title}}、{{degree_level}}、{{major}}、{{research_direction}}、{{keywords}}、{{word_count}}、{{format_requirements}}" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="变量说明等" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="是否默认" prop="isDefault">
          <el-radio-group v-model="form.isDefault">
            <el-radio label="1">是</el-radio>
            <el-radio label="0">否</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="排序" prop="sortOrder">
          <el-input-number v-model="form.sortOrder" :min="0" controls-position="right" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="0">正常</el-radio>
            <el-radio label="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancel">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </template>
    </el-dialog>

    <!-- 查看对话框 -->
    <el-dialog title="查看大纲提示词模板" v-model="viewOpen" width="900px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ID">{{ viewForm.promptTemplateId }}</el-descriptions-item>
        <el-descriptions-item label="模板名称">{{ viewForm.name }}</el-descriptions-item>
        <el-descriptions-item label="关联格式模板">
          <span v-if="viewForm.formatTemplateId == null">全局默认</span>
          <span v-else>{{ viewForm.formatTemplateName || getFormatTemplateName(viewForm.formatTemplateId) || 'ID:' + viewForm.formatTemplateId }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="是否默认">{{ viewForm.isDefault === '1' ? '是' : '否' }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ viewForm.status === '0' ? '正常' : '停用' }}</el-descriptions-item>
        <el-descriptions-item label="排序">{{ viewForm.sortOrder }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(viewForm.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewForm.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item label="提示词正文" :span="2">
          <pre class="prompt-content">{{ viewForm.templateContent || '-' }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewOpen = false">关 闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="OutlinePromptTemplate">
import { ref, reactive, onMounted } from 'vue'
import { getCurrentInstance } from 'vue'
import {
  listOutlinePromptTemplate,
  getOutlinePromptTemplate,
  addOutlinePromptTemplate,
  updateOutlinePromptTemplate,
  delOutlinePromptTemplate
} from '@/api/thesis/outlinePromptTemplate'
import { listTemplate } from '@/api/thesis/template'

const { proxy } = getCurrentInstance()

const dataList = ref([])
const total = ref(0)
const loading = ref(true)
const showSearch = ref(true)
const open = ref(false)
const viewOpen = ref(false)
const title = ref('')
const formatTemplateOptions = ref([])

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  name: undefined,
  formatTemplateId: undefined,
  status: undefined
})

const form = ref({})
const viewForm = ref({})
const rules = {
  name: [{ required: true, message: '模板名称不能为空', trigger: 'blur' }],
  templateContent: [{ required: true, message: '提示词正文不能为空', trigger: 'blur' }]
}

function getFormatTemplateName(templateId) {
  const t = formatTemplateOptions.value.find((x) => x.templateId === templateId)
  return t ? (t.templateName || t.name) : ''
}

function getList() {
  loading.value = true
  listOutlinePromptTemplate(queryParams)
    .then((response) => {
      dataList.value = response.rows || []
      total.value = response.total || 0
      loading.value = false
    })
    .catch(() => {
      loading.value = false
      proxy.$modal.msgError('获取列表失败')
    })
}

function loadFormatTemplates() {
  listTemplate({ pageNum: 1, pageSize: 500 })
    .then((res) => {
      formatTemplateOptions.value = res.rows || []
    })
    .catch(() => {})
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  proxy.resetForm('queryForm')
  handleQuery()
}

function handleAdd() {
  reset()
  open.value = true
  title.value = '新增大纲提示词模板'
}

function handleUpdate(row) {
  reset()
  getOutlinePromptTemplate(row.promptTemplateId).then((response) => {
    const data = response.data ?? response
    form.value = {
      promptTemplateId: data.promptTemplateId,
      name: data.name,
      formatTemplateId: data.formatTemplateId ?? undefined,
      templateContent: data.templateContent,
      remark: data.remark,
      isDefault: data.isDefault ?? '0',
      sortOrder: data.sortOrder ?? 0,
      status: data.status ?? '0'
    }
    open.value = true
    title.value = '修改大纲提示词模板'
  }).catch(() => {
    proxy.$modal.msgError('获取详情失败')
  })
}

function handleView(row) {
  getOutlinePromptTemplate(row.promptTemplateId).then((response) => {
    viewForm.value = response.data ?? response
    viewOpen.value = true
  }).catch(() => {
    proxy.$modal.msgError('获取详情失败')
  })
}

function submitForm() {
  proxy.$refs['formRef'].validate((valid) => {
    if (!valid) return
    const payload = {
      name: form.value.name,
      formatTemplateId: form.value.formatTemplateId ?? null,
      templateContent: form.value.templateContent,
      remark: form.value.remark,
      isDefault: form.value.isDefault ?? '0',
      sortOrder: form.value.sortOrder ?? 0,
      status: form.value.status ?? '0'
    }
    if (form.value.promptTemplateId != null) {
      updateOutlinePromptTemplate(form.value.promptTemplateId, payload).then(() => {
        proxy.$modal.msgSuccess('修改成功')
        open.value = false
        getList()
      }).catch(() => {})
    } else {
      addOutlinePromptTemplate(payload).then(() => {
        proxy.$modal.msgSuccess('新增成功')
        open.value = false
        getList()
      }).catch(() => {})
    }
  })
}

function handleDelete(row) {
  const id = row.promptTemplateId
  proxy.$modal.confirm('是否确认删除该大纲提示词模板？').then(() => {
    return delOutlinePromptTemplate(id)
  }).then(() => {
    getList()
    proxy.$modal.msgSuccess('删除成功')
  }).catch(() => {})
}

function cancel() {
  open.value = false
  reset()
}

function reset() {
  form.value = {
    promptTemplateId: undefined,
    name: '',
    formatTemplateId: undefined,
    templateContent: '',
    remark: '',
    isDefault: '0',
    sortOrder: 0,
    status: '0'
  }
  proxy.resetForm('formRef')
}

onMounted(() => {
  getList()
  loadFormatTemplates()
})
</script>

<style scoped>
.prompt-content {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow: auto;
  margin: 0;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
}
</style>
