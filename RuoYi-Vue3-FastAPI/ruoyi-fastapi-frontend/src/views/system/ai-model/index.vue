<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="模型名称" prop="modelName">
        <el-input
          v-model="queryParams.modelName"
          placeholder="请输入模型名称"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="模型类型" prop="modelType">
        <el-select v-model="queryParams.modelType" placeholder="请选择模型类型" clearable style="width: 240px">
          <el-option label="语言模型" value="language" />
          <el-option label="视觉模型" value="vision" />
        </el-select>
      </el-form-item>
      <el-form-item label="提供商" prop="provider">
        <el-select v-model="queryParams.provider" placeholder="请选择提供商" clearable style="width: 240px">
          <el-option label="OpenAI" value="openai" />
          <el-option label="Anthropic" value="anthropic" />
          <el-option label="Qwen" value="qwen" />
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
          v-hasPermi="['system:ai-model:add']"
        >新增</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="configList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="模型名称" align="center" prop="modelName" :show-overflow-tooltip="true" />
      <el-table-column label="模型代码" align="center" prop="modelCode" width="150" :show-overflow-tooltip="true" />
      <el-table-column label="模型类型" align="center" prop="modelType" width="100">
        <template #default="scope">
          <dict-tag :options="model_type_options" :value="scope.row.modelType"/>
        </template>
      </el-table-column>
      <el-table-column label="提供商" align="center" prop="provider" width="100">
        <template #default="scope">
          <dict-tag :options="provider_options" :value="scope.row.provider"/>
        </template>
      </el-table-column>
      <el-table-column label="优先级" align="center" prop="priority" width="80" />
      <el-table-column label="状态" align="center" width="100">
        <template #default="scope">
          <el-switch
            v-model="scope.row.isEnabled"
            active-value="1"
            inactive-value="0"
            @change="handleStatusChange(scope.row)"
          ></el-switch>
        </template>
      </el-table-column>
      <el-table-column label="默认" align="center" width="80">
        <template #default="scope">
          <el-tag v-if="scope.row.isDefault === '1'" type="success">是</el-tag>
          <el-tag v-else type="info">否</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:ai-model:edit']">修改</el-button>
          <el-button link type="success" icon="Check" @click="handleSetDefault(scope.row)" v-hasPermi="['system:ai-model:edit']" v-if="scope.row.isDefault !== '1'">设为默认</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:ai-model:remove']" v-if="scope.row.isPreset !== '1'">删除</el-button>
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

    <!-- 添加或修改对话框 -->
    <el-dialog :title="title" v-model="open" width="600px" append-to-body>
      <el-form ref="configRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="模型类型" prop="modelType">
          <el-radio-group v-model="form.modelType" @change="handleTypeChange">
            <el-radio label="language">语言模型</el-radio>
            <el-radio label="vision">视觉模型</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="form.provider" placeholder="请选择提供商" @change="handleProviderChange">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Qwen" value="qwen" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择模型" prop="modelCode" v-if="presetModels.length > 0">
          <el-select v-model="form.modelCode" placeholder="请选择预设模型" filterable allow-create @change="handleModelSelect">
            <el-option
              v-for="model in presetModels"
              :key="model.modelCode"
              :label="model.modelName"
              :value="model.modelCode"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模型代码" prop="modelCode" v-else>
          <el-input v-model="form.modelCode" placeholder="请输入模型代码" />
        </el-form-item>
        <el-form-item label="模型名称" prop="modelName">
          <el-input v-model="form.modelName" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="API端点" prop="apiEndpoint">
          <el-input v-model="form.apiEndpoint" placeholder="请输入API端点" />
        </el-form-item>
        <el-form-item label="API密钥" prop="apiKey">
          <el-input v-model="form.apiKey" type="password" placeholder="请输入API密钥" show-password />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="form.priority" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入内容" />
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

<script setup name="AiModelConfig">
import { listAiModel, getAiModel, delAiModel, addAiModel, updateAiModel, enableAiModel, disableAiModel, setDefaultAiModel, getPresetModels } from "@/api/system/aiModel";

const { proxy } = getCurrentInstance();

const configList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const presetModels = ref([]);

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    modelName: undefined,
    modelType: undefined,
    provider: undefined,
    isEnabled: undefined
  },
  rules: {
    modelName: [
      { required: true, message: "模型名称不能为空", trigger: "blur" }
    ],
    modelCode: [
      { required: true, message: "模型代码不能为空", trigger: "blur" }
    ],
    modelType: [
      { required: true, message: "模型类型不能为空", trigger: "change" }
    ],
    provider: [
      { required: true, message: "提供商不能为空", trigger: "change" }
    ],
    apiKey: [
      { required: true, message: "API密钥不能为空", trigger: "blur" }
    ],
    apiEndpoint: [
      { required: true, message: "API端点不能为空", trigger: "blur" }
    ]
  }
});

const { queryParams, form, rules } = toRefs(data);

// 模型类型选项
const model_type_options = ref([
  { label: "语言模型", value: "language", listClass: "success" },
  { label: "视觉模型", value: "vision", listClass: "warning" }
]);

// 提供商选项
const provider_options = ref([
  { label: "OpenAI", value: "openai", listClass: "primary" },
  { label: "Anthropic", value: "anthropic", listClass: "success" },
  { label: "Qwen", value: "qwen", listClass: "warning" },
  { label: "自定义", value: "custom", listClass: "info" }
]);

/** 查询列表 */
function getList() {
  loading.value = true;
  listAiModel(queryParams.value).then(response => {
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
    configId: null,
    modelName: null,
    modelCode: null,
    modelType: "language",
    provider: "openai",
    apiKey: null,
    apiEndpoint: null,
    modelVersion: null,
    params: null,
    priority: 0,
    isEnabled: "1",
    isDefault: "0",
    isPreset: "0",
    remark: null
  };
  proxy.resetForm("configRef");
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
  ids.value = selection.map(item => item.configId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加AI模型配置";
  loadPresetModels();
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const _configId = row.configId || ids.value
  getAiModel(_configId).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改AI模型配置";
    loadPresetModels();
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["configRef"].validate(valid => {
    if (valid) {
      if (form.value.configId != null) {
        updateAiModel(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addAiModel(form.value).then(response => {
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
  const _configIds = row.configId || ids.value;
  proxy.$modal.confirm('是否确认删除AI模型配置编号为"' + _configIds + '"的数据项？').then(function() {
    return delAiModel(_configIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 状态修改 */
function handleStatusChange(row) {
  let text = row.isEnabled === "1" ? "启用" : "禁用";
  proxy.$modal.confirm('确认要"' + text + '""' + row.modelName + '"吗？').then(function() {
    if (row.isEnabled === "1") {
      return enableAiModel(row.configId);
    } else {
      return disableAiModel(row.configId);
    }
  }).then(() => {
    proxy.$modal.msgSuccess(text + "成功");
  }).catch(function() {
    row.isEnabled = row.isEnabled === "0" ? "1" : "0";
  });
}

/** 设置默认 */
function handleSetDefault(row) {
  proxy.$modal.confirm('确认要将"' + row.modelName + '"设为默认模型吗？').then(function() {
    return setDefaultAiModel(row.configId);
  }).then(() => {
    proxy.$modal.msgSuccess("设置成功");
    getList();
  }).catch(() => {});
}

/** 加载预设模型 */
function loadPresetModels() {
  getPresetModels({
    modelType: form.value.modelType,
    provider: form.value.provider
  }).then(response => {
    presetModels.value = response.data || [];
  }).catch(() => {
    presetModels.value = [];
  });
}

/** 模型类型改变 */
function handleTypeChange() {
  form.value.modelCode = null;
  form.value.modelName = null;
  form.value.apiEndpoint = null;
  loadPresetModels();
}

/** 提供商改变 */
function handleProviderChange() {
  form.value.modelCode = null;
  form.value.modelName = null;
  form.value.apiEndpoint = null;
  loadPresetModels();
}

/** 选择模型后自动填充 */
function handleModelSelect(modelCode) {
  const selected = presetModels.value.find(m => m.modelCode === modelCode);
  if (selected) {
    form.value.modelName = selected.modelName;
    form.value.apiEndpoint = selected.apiEndpoint;
    form.value.modelVersion = selected.modelVersion;
    form.value.params = selected.params;
  }
}

getList();
</script>
