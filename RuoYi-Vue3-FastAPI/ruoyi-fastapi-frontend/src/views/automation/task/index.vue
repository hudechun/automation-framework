<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="任务名称" prop="name">
        <el-input
          v-model="queryParams.name"
          placeholder="请输入任务名称"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="任务状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择任务状态" clearable>
          <el-option
            v-for="dict in automation_task_status"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="创建时间" style="width: 308px">
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
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['automation:task:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['automation:task:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['automation:task:remove']"
        >删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="taskList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="任务ID" align="center" prop="id" width="80" />
      <el-table-column label="任务名称" align="center" prop="name" :show-overflow-tooltip="true" min-width="150">
        <template #default="scope">
          <el-link type="primary" @click="handleViewMonitor(scope.row)" :underline="false">
            {{ scope.row.name }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="任务类型" align="center" prop="taskType" width="120">
        <template #default="scope">
          <dict-tag :options="automation_task_type" :value="scope.row.taskType"/>
        </template>
      </el-table-column>
      <el-table-column label="任务描述" align="center" prop="description" :show-overflow-tooltip="true" min-width="200" />
      <el-table-column label="执行状态" align="center" width="120">
        <template #default="scope">
          <el-tag :type="getExecutionStatusType(scope.row.executionState)" size="small">
            {{ getExecutionStatusLabel(scope.row.executionState) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行进度" align="center" width="200">
        <template #default="scope">
          <div v-if="scope.row.executionState === 'running' || scope.row.executionState === 'paused'" class="progress-cell">
            <el-progress
              :percentage="scope.row.progressPercentage || 0"
              :status="scope.row.executionState === 'paused' ? 'warning' : null"
              :stroke-width="8"
              :show-text="true"
            />
            <div class="progress-info">
              {{ scope.row.completedActions || 0 }}/{{ scope.row.totalActions || 0 }}
            </div>
          </div>
          <span v-else class="no-progress">--</span>
        </template>
      </el-table-column>
      <el-table-column label="任务状态" align="center" prop="status" width="100">
        <template #default="scope">
          <dict-tag :options="automation_task_status" :value="scope.row.status"/>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createdAt" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createdAt) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="280" fixed="right">
        <template #default="scope">
          <el-button 
            link 
            type="primary" 
            icon="View" 
            @click="handleViewMonitor(scope.row)"
            v-hasPermi="['automation:task:view']"
          >
            监控
          </el-button>
          <el-button 
            link 
            type="primary" 
            icon="Edit" 
            @click="handleUpdate(scope.row)" 
            v-hasPermi="['automation:task:edit']"
          >
            修改
          </el-button>
          <el-dropdown 
            v-if="['running', 'paused'].includes(scope.row.executionState)"
            @command="(cmd) => handleExecutionControl(cmd, scope.row)"
          >
            <el-button link type="primary">
              控制<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item 
                  v-if="scope.row.executionState === 'running'"
                  command="pause"
                  icon="VideoPause"
                >
                  暂停
                </el-dropdown-item>
                <el-dropdown-item 
                  v-if="scope.row.executionState === 'paused'"
                  command="resume"
                  icon="VideoPlay"
                >
                  恢复
                </el-dropdown-item>
                <el-dropdown-item 
                  command="stop"
                  icon="Close"
                  divided
                >
                  停止
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button 
            v-else
            link 
            type="success" 
            icon="VideoPlay" 
            @click="handleExecute(scope.row)" 
            v-hasPermi="['automation:task:execute']"
          >
            执行
          </el-button>
          <el-button 
            link 
            type="danger" 
            icon="Delete" 
            @click="handleDelete(scope.row)" 
            v-hasPermi="['automation:task:remove']"
          >
            删除
          </el-button>
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

    <!-- 添加或修改任务对话框 -->
    <el-dialog :title="title" v-model="open" width="600px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型" prop="taskType">
          <el-select v-model="form.taskType" placeholder="请选择任务类型">
            <el-option
              v-for="dict in automation_task_type"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入任务描述" />
        </el-form-item>
        <el-form-item label="任务动作" prop="actions">
          <el-input v-model="form.actionsStr" type="textarea" :rows="5" placeholder='请输入任务动作JSON，例如：[{"type":"click","selector":"#btn"}]' />
        </el-form-item>
        <el-form-item label="任务配置" prop="config">
          <el-input v-model="form.configStr" type="textarea" :rows="3" placeholder='请输入任务配置JSON，例如：{"timeout":30}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Task">
import { listTask, getTask, delTask, addTask, updateTask, executeTask, pauseTask, resumeTask, stopTask, getExecutionStatus, getExecutionProgress } from "@/api/automation/task";
import { useRouter } from 'vue-router';
import { ArrowDown, VideoPause, VideoPlay, Close, View } from '@element-plus/icons-vue';
import { getCurrentInstance } from 'vue';

const { proxy } = getCurrentInstance();
const router = useRouter();
const { automation_task_status, automation_task_type } = proxy.useDict('automation_task_status', 'automation_task_type');

const taskList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const dateRange = ref([]);

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    name: null,
    status: null,
  },
  rules: {
    name: [
      { required: true, message: "任务名称不能为空", trigger: "blur" }
    ],
    taskType: [
      { required: true, message: "任务类型不能为空", trigger: "change" }
    ],
  }
});

const { queryParams, form, rules } = toRefs(data);

/** 查询任务列表 */
function getList() {
  loading.value = true;
  listTask(proxy.addDateRange(queryParams.value, dateRange.value)).then(response => {
    taskList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

// 取消按钮
function cancel() {
  open.value = false;
  reset();
}

// 表单重置
function reset() {
  form.value = {
    id: null,
    name: null,
    description: null,
    taskType: null,
    actionsStr: null,
    configStr: null,
    status: "pending"
  };
  proxy.resetForm("formRef");
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
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "新增任务";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const _id = row.id || ids.value
  getTask(_id).then(response => {
    form.value = response.data;
    // 将JSON对象转换为字符串以便编辑
    form.value.actionsStr = JSON.stringify(form.value.actions, null, 2);
    form.value.configStr = form.value.config ? JSON.stringify(form.value.config, null, 2) : '';
    open.value = true;
    title.value = "修改任务";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["formRef"].validate(valid => {
    if (valid) {
      // 将字符串转换回JSON对象
      try {
        form.value.actions = JSON.parse(form.value.actionsStr || '[]');
        form.value.config = form.value.configStr ? JSON.parse(form.value.configStr) : null;
      } catch (e) {
        proxy.$modal.msgError("JSON格式错误，请检查");
        return;
      }
      
      if (form.value.id != null) {
        updateTask(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addTask(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const _ids = row.id || ids.value;
  proxy.$modal.confirm('是否确认删除任务编号为"' + _ids + '"的数据项？').then(function() {
    return delTask(_ids);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 执行任务 */
function handleExecute(row) {
  proxy.$modal.confirm('是否确认执行任务"' + row.name + '"？').then(function() {
    return executeTask(row.id);
  }).then(() => {
    proxy.$modal.msgSuccess("任务已开始执行");
    getList();
    // 开始轮询执行状态
    startPollingExecutionStatus(row.id);
  }).catch(() => {});
}

/** 查看执行监控 */
function handleViewMonitor(row) {
  router.push({
    path: '/automation/task/monitor',
    query: {
      taskId: row.id,
      executionId: row.executionId
    }
  });
}

/** 执行控制 */
function handleExecutionControl(command, row) {
  switch (command) {
    case 'pause':
      handlePause(row);
      break;
    case 'resume':
      handleResume(row);
      break;
    case 'stop':
      handleStop(row);
      break;
  }
}

/** 暂停任务 */
function handlePause(row) {
  proxy.$modal.confirm('确定要暂停任务"' + row.name + '"吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    return pauseTask(row.id);
  }).then(() => {
    proxy.$modal.msgSuccess("任务已暂停");
    getList();
  }).catch(() => {});
}

/** 恢复任务 */
function handleResume(row) {
  resumeTask(row.id).then(() => {
    proxy.$modal.msgSuccess("任务已恢复");
    getList();
  }).catch(() => {});
}

/** 停止任务 */
function handleStop(row) {
  proxy.$modal.confirm('确定要停止任务"' + row.name + '"吗？停止后无法恢复', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    return stopTask(row.id);
  }).then(() => {
    proxy.$modal.msgSuccess("任务已停止");
    getList();
  }).catch(() => {});
}

/** 获取执行状态类型 */
function getExecutionStatusType(state) {
  const typeMap = {
    'pending': 'info',
    'running': 'success',
    'paused': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'stopped': 'info'
  };
  return typeMap[state] || 'info';
}

/** 获取执行状态标签 */
function getExecutionStatusLabel(state) {
  const labelMap = {
    'pending': '待执行',
    'running': '执行中',
    'paused': '已暂停',
    'completed': '已完成',
    'failed': '执行失败',
    'stopped': '已停止'
  };
  return labelMap[state] || state || '未知';
}

/** 轮询执行状态 */
const pollingTasks = new Set();
let pollingTimer = null;

function startPollingExecutionStatus(taskId) {
  if (pollingTasks.has(taskId)) return;
  pollingTasks.add(taskId);
  
  if (!pollingTimer) {
    pollingTimer = setInterval(() => {
      pollingTasks.forEach(async (id) => {
        try {
          const statusRes = await getExecutionStatus(id);
          const progressRes = await getExecutionProgress(id);
          
          if (statusRes.code === 200 && progressRes.code === 200) {
            // 更新任务列表中的执行状态
            const task = taskList.value.find(t => t.id === id);
            if (task) {
              task.executionState = statusRes.data?.state || 'pending';
              if (progressRes.data) {
                task.progressPercentage = progressRes.data.progress_percentage || 0;
                task.completedActions = progressRes.data.completed_actions || 0;
                task.totalActions = progressRes.data.total_actions || 0;
              }
              
              // 如果任务已完成或失败，停止轮询
              if (['completed', 'failed', 'stopped'].includes(task.executionState)) {
                pollingTasks.delete(id);
              }
            }
          }
        } catch (error) {
          console.error('轮询执行状态失败:', error);
        }
      });
      
      // 如果没有正在轮询的任务，清除定时器
      if (pollingTasks.size === 0) {
        clearInterval(pollingTimer);
        pollingTimer = null;
      }
    }, 2000); // 每2秒轮询一次
  }
}

getList();
</script>

<style scoped lang="scss">
.progress-cell {
  .progress-info {
    margin-top: 5px;
    font-size: 12px;
    color: #909399;
    text-align: center;
  }
}

.no-progress {
  color: #c0c4cc;
}
</style>
