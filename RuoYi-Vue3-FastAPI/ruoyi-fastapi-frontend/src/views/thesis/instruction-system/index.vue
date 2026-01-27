<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="版本号" prop="version">
        <el-input
          v-model="queryParams.version"
          placeholder="请输入版本号"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="状态" prop="isActive">
        <el-select v-model="queryParams.isActive" placeholder="请选择状态" clearable>
          <el-option label="激活" value="1" />
          <el-option label="停用" value="0" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="queryParams.description"
          placeholder="请输入描述"
          clearable
          @keyup.enter.native="handleQuery"
        />
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
          v-hasPermi="['thesis:instruction-system:add']"
        >新增</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="instructionSystemList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="ID" align="center" prop="id" width="80" />
      <el-table-column label="版本号" align="center" prop="version" width="120" />
      <el-table-column label="描述" align="center" prop="description" :show-overflow-tooltip="true" />
      <el-table-column label="状态" align="center" prop="isActive" width="100">
        <template #default="scope">
          <dict-tag v-if="sysNormalDisableOptions && sysNormalDisableOptions.length > 0" :options="sysNormalDisableOptions" :value="scope.row.isActive === '1' ? '0' : '1'" />
          <el-tag v-else :type="scope.row.isActive === '1' ? 'success' : 'info'">{{ scope.row.isActive === '1' ? '激活' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d} {h}:{i}:{s}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="280">
        <template #default="scope">
          <el-button
            size="mini"
            type="text"
            icon="View"
            @click="handleView(scope.row)"
          >查看</el-button>
          <el-button
            size="mini"
            type="text"
            icon="Edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['thesis:instruction-system:edit']"
          >修改</el-button>
          <el-button
            v-if="scope.row.isActive !== '1'"
            size="mini"
            type="text"
            icon="Check"
            @click="handleActivate(scope.row)"
            v-hasPermi="['thesis:instruction-system:edit']"
          >激活</el-button>
          <el-button
            size="mini"
            type="text"
            icon="Delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['thesis:instruction-system:remove']"
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

    <!-- 添加或修改指令系统对话框 -->
    <el-dialog :title="title" v-model="open" width="1200px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="版本号" prop="version">
          <el-input v-model="form.version" placeholder="请输入版本号，如：1.0" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="是否激活" prop="isActive">
          <el-radio-group v-model="form.isActive">
            <el-radio label="1">激活</el-radio>
            <el-radio label="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="指令数据" prop="instructionData">
          <!-- 查找工具栏 -->
          <div class="search-toolbar" v-show="showSearchBar">
            <el-input
              v-model="searchText"
              placeholder="查找..."
              size="small"
              style="width: 200px; margin-right: 10px;"
              @keyup.enter="findNext"
              @input="onSearchInput"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button-group size="small">
              <el-button @click="findPrevious" :disabled="!searchText || matchCount === 0" icon="ArrowUp">上一个</el-button>
              <el-button @click="findNext" :disabled="!searchText || matchCount === 0" icon="ArrowDown">下一个</el-button>
            </el-button-group>
            <span v-if="searchText" class="match-count">
              {{ currentMatchIndex > 0 ? `${currentMatchIndex} / ${matchCount}` : (matchCount > 0 ? `${matchCount} 个匹配` : '未找到') }}
            </span>
            <el-button
              size="small"
              text
              @click="showSearchBar = false"
              style="margin-left: auto;"
            >
              关闭
            </el-button>
          </div>
          <div style="width: 100%; height: 500px; position: relative;">
            <el-input
              ref="instructionDataInput"
              v-model="instructionDataJson"
              type="textarea"
              :rows="20"
              placeholder="请输入JSON格式的指令数据"
              style="font-family: 'Courier New', monospace;"
              @keydown.ctrl.f.prevent="openSearchBar"
            />
            <!-- 查找按钮（浮动） -->
            <el-button
              v-if="!showSearchBar"
              class="search-toggle-btn"
              size="small"
              circle
              @click="openSearchBar"
              title="查找 (Ctrl+F)"
            >
              <el-icon><Search /></el-icon>
            </el-button>
          </div>
          <div style="margin-top: 10px; color: #909399; font-size: 12px;">
            <el-icon><InfoFilled /></el-icon>
            提示：请确保JSON格式正确，可以使用JSON格式化工具验证。按 Ctrl+F 打开查找功能
          </div>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancel">取 消</el-button>
          <el-button type="primary" @click="submitForm">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看指令系统对话框 -->
    <el-dialog title="查看指令系统" v-model="viewOpen" width="1200px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ID">{{ viewForm.id }}</el-descriptions-item>
        <el-descriptions-item label="版本号">{{ viewForm.version }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ viewForm.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <dict-tag v-if="sysNormalDisableOptions && sysNormalDisableOptions.length > 0" :options="sysNormalDisableOptions" :value="viewForm.isActive === '1' ? '0' : '1'" />
          <el-tag v-else :type="viewForm.isActive === '1' ? 'success' : 'info'">{{ viewForm.isActive === '1' ? '激活' : '停用' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(viewForm.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="创建者">{{ viewForm.createBy || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ parseTime(viewForm.updateTime) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新者">{{ viewForm.updateBy || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewForm.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-divider>指令数据</el-divider>
      <div style="max-height: 500px; overflow: auto;">
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; font-size: 12px; line-height: 1.6;">{{ JSON.stringify(viewForm.instructionData, null, 2) }}</pre>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="viewOpen = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="InstructionSystem">
import { ref, reactive, onMounted, getCurrentInstance, computed, watch, nextTick } from 'vue'
import { listInstructionSystem, getInstructionSystem, delInstructionSystem, addInstructionSystem, updateInstructionSystem, activateInstructionSystem } from '@/api/thesis/instructionSystem'
import { InfoFilled, Search, ArrowUp, ArrowDown } from '@element-plus/icons-vue'

const { proxy } = getCurrentInstance()
const { sys_normal_disable } = proxy.useDict('sys_normal_disable')

// 安全获取字典数据
const sysNormalDisableOptions = computed(() => {
  return sys_normal_disable.value || []
})

const instructionSystemList = ref([])
const open = ref(false)
const viewOpen = ref(false)
const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref('')
const instructionDataJson = ref('')
const instructionDataInput = ref(null)
const showSearchBar = ref(false)
const searchText = ref('')
const matchCount = ref(0)
const currentMatchIndex = ref(0)
const matchPositions = ref([])

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  version: null,
  isActive: null,
  description: null
})

const form = ref({})
const viewForm = ref({})
const rules = {
  version: [
    { required: true, message: '版本号不能为空', trigger: 'blur' }
  ],
  instructionData: [
    { required: true, message: '指令数据不能为空', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        try {
          JSON.parse(instructionDataJson.value)
          callback()
        } catch (e) {
          callback(new Error('指令数据必须是有效的JSON格式'))
        }
      },
      trigger: 'blur'
    }
  ]
}

/** 查询指令系统列表 */
function getList() {
  loading.value = true
  listInstructionSystem(queryParams).then(response => {
    console.log('指令系统列表响应:', response)
    // 处理响应数据
    if (response && response.rows) {
      instructionSystemList.value = response.rows || []
      total.value = response.total || 0
    } else {
      console.warn('响应格式异常:', response)
      instructionSystemList.value = []
      total.value = 0
    }
    loading.value = false
  }).catch(error => {
    console.error('获取指令系统列表失败:', error)
    loading.value = false
    proxy.$modal.msgError('获取指令系统列表失败: ' + (error.message || error))
  })
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm('queryForm')
  handleQuery()
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id)
  single.value = selection.length !== 1
  multiple.value = !selection.length
}

/** 新增按钮操作 */
function handleAdd() {
  reset()
  open.value = true
  title.value = '添加指令系统'
  instructionDataJson.value = JSON.stringify({
    version: '1.0',
    description: '通用格式指令系统',
    instruction_type: 'universal_format',
    format_rules: {},
    application_rules: {}
  }, null, 2)
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset()
  const systemId = row.id
  getInstructionSystem(systemId).then(response => {
    console.log('获取指令系统详情响应:', response)
    const data = response.data || response
    form.value = data
    instructionDataJson.value = JSON.stringify(data.instructionData || {}, null, 2)
    open.value = true
    title.value = '修改指令系统'
  }).catch(error => {
    console.error('获取指令系统详情失败:', error)
    proxy.$modal.msgError('获取指令系统详情失败')
  })
}

/** 查看按钮操作 */
function handleView(row) {
  const systemId = row.id
  getInstructionSystem(systemId).then(response => {
    console.log('查看指令系统详情响应:', response)
    viewForm.value = response.data || response
    viewOpen.value = true
  }).catch(error => {
    console.error('获取指令系统详情失败:', error)
    proxy.$modal.msgError('获取指令系统详情失败')
  })
}

/** 激活按钮操作 */
function handleActivate(row) {
  const systemId = row.id
  proxy.$modal.confirm('是否确认激活版本号为"' + row.version + '"的指令系统？').then(function() {
    return activateInstructionSystem(systemId)
  }).then(() => {
    getList()
    proxy.$modal.msgSuccess('激活成功')
  }).catch(() => {})
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs['formRef'].validate(valid => {
    if (valid) {
      // 解析JSON
      try {
        form.value.instructionData = JSON.parse(instructionDataJson.value)
      } catch (e) {
        proxy.$modal.msgError('指令数据JSON格式错误：' + e.message)
        return
      }

      if (form.value.id !== undefined) {
        updateInstructionSystem(form.value.id, form.value).then(response => {
          proxy.$modal.msgSuccess('修改成功')
          open.value = false
          getList()
          // 重置查找状态
          showSearchBar.value = false
          searchText.value = ''
          matchCount.value = 0
          currentMatchIndex.value = 0
          matchPositions.value = []
        })
      } else {
        addInstructionSystem(form.value).then(response => {
          proxy.$modal.msgSuccess('新增成功')
          open.value = false
          getList()
          // 重置查找状态
          showSearchBar.value = false
          searchText.value = ''
          matchCount.value = 0
          currentMatchIndex.value = 0
          matchPositions.value = []
        })
      }
    }
  })
}

/** 删除按钮操作 */
function handleDelete(row) {
  const systemIds = row.id || ids.value
  proxy.$modal.confirm('是否确认删除指令系统编号为"' + systemIds + '"的数据项？').then(function() {
    return delInstructionSystem(systemIds)
  }).then(() => {
    getList()
    proxy.$modal.msgSuccess('删除成功')
  }).catch(() => {})
}

/** 取消按钮 */
function cancel() {
  open.value = false
  reset()
  // 重置查找状态
  showSearchBar.value = false
  searchText.value = ''
  matchCount.value = 0
  currentMatchIndex.value = 0
  matchPositions.value = []
}

/** 表单重置 */
function reset() {
  form.value = {
    id: undefined,
    version: '',
    description: '',
    instructionData: {},
    isActive: '1',
    remark: ''
  }
  instructionDataJson.value = ''
  proxy.resetForm('formRef')
  // 重置查找状态
  showSearchBar.value = false
  searchText.value = ''
  matchCount.value = 0
  currentMatchIndex.value = 0
  matchPositions.value = []
}

/** 打开查找栏 */
function openSearchBar() {
  showSearchBar.value = true
  nextTick(() => {
    // 聚焦到查找输入框
    const searchInput = document.querySelector('.search-toolbar .el-input__inner')
    if (searchInput) {
      searchInput.focus()
      searchInput.select()
    }
  })
}

/** 查找输入变化 */
function onSearchInput() {
  if (!searchText.value) {
    matchCount.value = 0
    currentMatchIndex.value = 0
    matchPositions.value = []
    return
  }
  performSearch()
}

/** 执行查找 */
function performSearch() {
  if (!instructionDataJson.value || !searchText.value) {
    matchCount.value = 0
    currentMatchIndex.value = 0
    matchPositions.value = []
    return
  }
  
  const text = instructionDataJson.value
  const search = searchText.value
  const positions = []
  let index = 0
  
  // 不区分大小写查找所有匹配位置
  const lowerText = text.toLowerCase()
  const lowerSearch = search.toLowerCase()
  
  while ((index = lowerText.indexOf(lowerSearch, index)) !== -1) {
    positions.push(index)
    index += search.length
  }
  
  matchPositions.value = positions
  matchCount.value = positions.length
  
  if (positions.length > 0 && currentMatchIndex.value === 0) {
    currentMatchIndex.value = 1
    scrollToMatch(positions[0])
  } else if (positions.length === 0) {
    currentMatchIndex.value = 0
  }
}

/** 查找下一个 */
function findNext() {
  if (matchPositions.value.length === 0) {
    performSearch()
    return
  }
  
  if (currentMatchIndex.value >= matchPositions.value.length) {
    currentMatchIndex.value = 1
  } else {
    currentMatchIndex.value++
  }
  
  const index = currentMatchIndex.value - 1
  scrollToMatch(matchPositions.value[index])
}

/** 查找上一个 */
function findPrevious() {
  if (matchPositions.value.length === 0) {
    performSearch()
    return
  }
  
  if (currentMatchIndex.value <= 1) {
    currentMatchIndex.value = matchPositions.value.length
  } else {
    currentMatchIndex.value--
  }
  
  const index = currentMatchIndex.value - 1
  scrollToMatch(matchPositions.value[index])
}

/** 滚动到匹配位置 */
function scrollToMatch(position) {
  if (!instructionDataInput.value) return
  
  nextTick(() => {
    // Element Plus Input 组件的 textarea 访问方式
    let textarea = null
    if (instructionDataInput.value.$el) {
      textarea = instructionDataInput.value.$el.querySelector('textarea')
    } else if (instructionDataInput.value.textarea) {
      textarea = instructionDataInput.value.textarea
    } else if (instructionDataInput.value.input) {
      textarea = instructionDataInput.value.input
    }
    
    if (!textarea) {
      // 尝试通过 DOM 查询
      const container = document.querySelector('.el-textarea__inner')
      if (container) {
        textarea = container
      }
    }
    
    if (!textarea) return
    
    // 计算行号和列号
    const textBeforeMatch = instructionDataJson.value.substring(0, position)
    const lines = textBeforeMatch.split('\n')
    const lineNumber = lines.length - 1
    
    // 计算滚动位置（每行大约21px高度）
    const lineHeight = 21
    const scrollTop = lineNumber * lineHeight - 100 // 留出一些顶部空间
    
    textarea.scrollTop = Math.max(0, scrollTop)
    
    // 设置选中文本
    setTimeout(() => {
      const start = position
      const end = position + searchText.value.length
      if (textarea.setSelectionRange) {
        textarea.setSelectionRange(start, end)
      } else if (textarea.createTextRange) {
        // IE 兼容
        const range = textarea.createTextRange()
        range.collapse(true)
        range.moveStart('character', start)
        range.moveEnd('character', end - start)
        range.select()
      }
      textarea.focus()
    }, 50)
  })
}

// 监听查找文本变化
watch(searchText, () => {
  onSearchInput()
})

// 监听指令数据变化，重新查找
watch(instructionDataJson, () => {
  if (searchText.value) {
    performSearch()
  }
})

onMounted(() => {
  getList()
})
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.search-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px 4px 0 0;
  margin-bottom: -1px;
}

.match-count {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.search-toggle-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
