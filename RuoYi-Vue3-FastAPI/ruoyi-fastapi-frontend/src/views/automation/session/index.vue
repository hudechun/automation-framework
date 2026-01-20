<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="会话ID" prop="sessionId">
        <el-input
          v-model="queryParams.sessionId"
          placeholder="请输入会话ID"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="会话状态" prop="state">
        <el-select v-model="queryParams.state" placeholder="请选择会话状态" clearable>
          <el-option
            v-for="dict in automation_session_state"
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
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['automation:session:remove']"
        >删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="sessionList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="会话ID" align="center" prop="id" width="80" />
      <el-table-column label="会话标识" align="center" prop="sessionId" :show-overflow-tooltip="true" />
      <el-table-column label="会话状态" align="center" prop="state" width="120">
        <template #default="scope">
          <dict-tag :options="automation_session_state" :value="scope.row.state"/>
        </template>
      </el-table-column>
      <el-table-column label="驱动类型" align="center" prop="driverType" width="120">
        <template #default="scope">
          <dict-tag :options="automation_driver_type" :value="scope.row.driverType"/>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createdAt" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createdAt) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" align="center" prop="updatedAt" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.updatedAt) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="150">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleView(scope.row)" v-hasPermi="['automation:session:query']">详情</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['automation:session:remove']">删除</el-button>
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

    <!-- 查看会话详情对话框 -->
    <el-dialog title="会话详情" v-model="open" width="600px" append-to-body>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="会话ID">{{ form.id }}</el-descriptions-item>
        <el-descriptions-item label="会话标识">{{ form.sessionId }}</el-descriptions-item>
        <el-descriptions-item label="会话状态">
          <dict-tag :options="automation_session_state" :value="form.state"/>
        </el-descriptions-item>
        <el-descriptions-item label="驱动类型">
          <dict-tag :options="automation_driver_type" :value="form.driverType"/>
        </el-descriptions-item>
        <el-descriptions-item label="元数据">
          <pre>{{ JSON.stringify(form.metadata, null, 2) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(form.createdAt) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ parseTime(form.updatedAt) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="open = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Session">
import { listSession, getSession, delSession } from "@/api/automation/session";

const { proxy } = getCurrentInstance();
const { automation_session_state, automation_driver_type } = proxy.useDict('automation_session_state', 'automation_driver_type');

const sessionList = ref([]);
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
    sessionId: null,
    state: null,
  }
});

const { queryParams, form } = toRefs(data);

/** 查询会话列表 */
function getList() {
  loading.value = true;
  listSession(proxy.addDateRange(queryParams.value, dateRange.value)).then(response => {
    sessionList.value = response.rows;
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
  getSession(_id).then(response => {
    form.value = response.data;
    open.value = true;
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const _ids = row.id || ids.value;
  proxy.$modal.confirm('是否确认删除会话编号为"' + _ids + '"的数据项？').then(function() {
    return delSession(_ids);
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
}
</style>
