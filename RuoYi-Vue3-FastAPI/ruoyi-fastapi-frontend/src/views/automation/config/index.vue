<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="配置名称" prop="name">
        <el-input
          v-model="queryParams.name"
          placeholder="请输入配置名称"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="提供商" prop="provider">
        <el-select v-model="queryParams.provider" placeholder="请选择提供商" clearable>
          <el-option
            v-for="dict in automation_model_provider"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="启用状态" prop="enabled">
        <el-select v-model="queryParams.enabled" placeholder="请选择启用状态" clearable>
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>
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
          v-hasPermi="['automation:config:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['automation:config:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['automation:config:remove']"
        >删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="configList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="配置ID" align="center" prop="id" width="80" />
      <el-table-column label="配置名称" align="center" prop="name" :show-overflow-tooltip="true" />
      <el-table-column label="提供商" align="center" prop="provider" width="120">
        <template #default="scope">
          <dict-tag :options="automation_model_provider" :value="scope.row.provider"/>
        </template>
      </el-table-column>
      <el-table-column label="模型名称" align="center" prop="model" :show-overflow-tooltip="true" />
      <el-table-column label="启用状态" align="center" prop="enabled" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.enabled ? 'success' : 'danger'">
            {{ scope.row.enabled ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createdAt" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createdAt) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="150">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['automation:config:edit']">修改</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['automation:config:remove']">删除</el-button>
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

    <!-- 添加或修改模型配置对话框 -->
    <el-dialog :title="title" v-model="open" width="600px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="form.provider" placeholder="请选择提供商">
            <el-option
              v-for="dict in automation_model_provider"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" prop="model">
          <el-input v-model="form.model" placeholder="请输入模型名称，例如：qwen-max" />
        </el-form-item>
        <el-form-item label="API密钥" prop="apiKey">
          <el-input v-model="form.apiKey" type="password" placeholder="请输入API密钥" show-password />
        </el-form-item>
        <el-form-item label="模型参数" prop="params">
          <el-input v-model="form.paramsStr" type="textarea" :rows="5" placeholder='请输入模型参数JSON，例如：{"temperature":0.7,"max_tokens":2000}' />
        </el-form-item>
        <el-form-item label="启用状态" prop="enabled">
          <el-radio-group v-model="form.enabled">
            <el-radio :label="true">启用</el-radio>
            <el-radio :label="false">禁用</el-radio>
          </el-radio-group>
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

<script setup name="Config">
import { listConfig, getConfig, delConfig, addConfig, updateConfig } from "@/api/automation/config";

const { proxy } = getCurrentInstance();
const { automation_model_provider } = proxy.useDict('automation_model_provider');

const configList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    name: null,
    provider: null,
    enabled: null,
  },
  rules: {
    name: [
      { required: true, message: "配置名称不能为空", trigger: "blur" }
    ],
    provider: [
      { required: true, message: "提供商不能为空", trigger: "change" }
    ],
    model: [
      { required: true, message: "模型名称不能为空", trigger: "blur" }
    ],
  }
});

const { queryParams, form, rules } = toRefs(data);

/** 查询模型配置列表 */
function getList() {
  loading.value = true;
  listConfig(queryParams.value).then(response => {
    configList.value = response.rows;
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
    provider: null,
    model: null,
    apiKey: null,
    paramsStr: null,
    enabled: true
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
  title.value = "添加模型配置";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const _id = row.id || ids.value
  getConfig(_id).then(response => {
    form.value = response.data;
    // 将JSON对象转换为字符串以便编辑
    form.value.paramsStr = form.value.params ? JSON.stringify(form.value.params, null, 2) : '';
    open.value = true;
    title.value = "修改模型配置";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["formRef"].validate(valid => {
    if (valid) {
      // 将字符串转换回JSON对象
      try {
        form.value.params = form.value.paramsStr ? JSON.parse(form.value.paramsStr) : null;
      } catch (e) {
        proxy.$modal.msgError("参数JSON格式错误，请检查");
        return;
      }
      
      if (form.value.id != null) {
        updateConfig(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addConfig(form.value).then(response => {
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
  proxy.$modal.confirm('是否确认删除模型配置编号为"' + _ids + '"的数据项？').then(function() {
    return delConfig(_ids);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

getList();
</script>
