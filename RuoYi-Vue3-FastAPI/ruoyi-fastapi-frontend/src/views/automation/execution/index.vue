<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="任务ID" prop="taskId">
        <el-input
          v-model="queryParams.taskId"
          placeholder="请输入任务ID"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="执行状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择执行状态" clearable>
          <el-option
            v-for="dict in automation_execution_status"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="开始时间" style="width: 308px">
        <el-date-picker
          v-model="dateRange"
          value-format="YYYY-MM-DD"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['automation:execution:remove']"
        >删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="executionList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="记录ID" align="center" prop="id" width="80" />
      <el-table-column label="任务名称" align="center" prop="taskName" :show-overflow-tooltip="true" />
      <el-table-column label="执行状态" align="center" prop="status" width="120">
        <template #default="scope">
          <dict-tag :options="automation_execution_status" :value="scope.row.status"/>
        </template>
      </el-table-column>
      <el-table-column label="开始时间" align="center" prop="startTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.startTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="结束时间" align="center" prop="endTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.endTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="执行时长" align="center" prop="duration" width="100">
        <template #default="scope">
          <span v-if="scope.row.duration">{{ scope.row.duration }}秒</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="150">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleView(scope.row)" v-hasPermi="['automation:execution:query']">详情</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['automation:execution:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <pagination
      v-show="total>0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 查看执行记录详情对话框 -->
    <el-dialog title="执行记录详情" v-model="open" width="800px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="记录ID">{{ form.id }}</el-descriptions-item>
        <el-descriptions-item label="任务名称">{{ form.taskName }}</el-descriptions-item>
        <el-descriptions-item label="执行状态">
          <dict-tag :options="automation_execution_status" :value="form.status"/>
        </el-descriptions-item>
        <el-descriptions-item label="执行时长">
          <span v-if="form.duration">{{ form.duration }}秒</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ parseTime(form.startTime) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ parseTime(form.endTime) }}</el-descriptions-item>
      </el-descriptions>
      
      <el-divider content-position="left">执行日志</el-divider>
      <pre class="log-content">{{ form.logs || '无日志' }}</pre>
      
      <el-divider content-position="left" v-if="form.errorMessage">错误信息</el-divider>
      <pre class="error-content" v-if="form.errorMessage">{{ form.errorMessage }}</pre>
      
      <el-divider content-position="left" v-if="form.result">执行结果</el-divider>
      <pre class="result-content" v-if="form.result">{{ JSON.stringify(form.result, null, 2) }}</pre>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="open = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Execution">
import { listExecution, getExecution, delExecution } from "@/api/automation/execution";

const { proxy } = getCurrentInstance();
const { automation_execution_status } = proxy.useDict('automation_execution_status');

const executionList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const multiple = ref(true);
const total = ref(0);
const dateRange = ref([]);

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    taskId: null,
    status: null,
  }
});

const { queryParams, form } = toRefs(data);

/** 查询执行记录列表 */
function getList() {
  loading.value = true;
  listExecution(proxy.addDateRange(queryParams.value, dateRange.value, 'beginTime', 'endTime')).then(response => {
    executionList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  dateRange.value = [];
  proxy.resetForm("queryRef");
  handleQuery();
}

// 多选框选中数据
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id);
  multiple.value = !selection.length;
}

/** 查看详情 */
function handleView(row) {
  const _id = row.id;
  getExecution(_id).then(response => {
    form.value = response.data;
    open.value = true;
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const _ids = row.id || ids.value;
  proxy.$modal.confirm('是否确认删除执行记录编号为"' + _ids + '"的数据项？').then(function() {
    return delExecution(_ids);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

getList();
</script>

<style scoped>
pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.log-content {
  background-color: #f0f9ff;
  border-left: 3px solid #409eff;
}

.error-content {
  background-color: #fef0f0;
  border-left: 3px solid #f56c6c;
  color: #f56c6c;
}

.result-content {
  background-color: #f0f9ff;
  border-left: 3px solid #67c23a;
}
</style>
