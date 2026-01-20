# RuoYi集成Automation业务功能方案

## 目标

将Automation Framework的业务功能完整集成到RuoYi系统中，包括：
1. 后端API（符合RuoYi规范）
2. 前端页面（Vue3 + Element Plus）
3. 菜单权限配置
4. 数据字典配置

## 集成步骤

### 第一阶段：使用RuoYi代码生成器（推荐）

RuoYi提供了强大的代码生成器，可以一键生成CRUD代码。

#### 1. 导入业务表到代码生成器

登录RuoYi管理后台 → 系统工具 → 代码生成 → 导入

导入以下表：
- `tasks` - 自动化任务表
- `sessions` - 会话管理表  
- `execution_records` - 执行记录表
- `model_configs` - 模型配置表

#### 2. 配置生成信息

为每个表配置：
- **基本信息**
  - 表名称：任务管理
  - 表注释：自动化任务信息表
  - 类名称：Task
  - 作者：你的名字
  - 生成包路径：module_automation
  - 生成模块名：automation
  - 业务名：task
  - 功能名：任务

- **字段信息**
  - 设置每个字段的显示类型（输入框、下拉框、日期等）
  - 设置是否必填
  - 设置查询方式（等于、模糊、范围等）

- **生成信息**
  - 生成模板：CRUD（增删改查）
  - 生成代码方式：zip压缩包

#### 3. 生成并导入代码

点击"生成代码"下载zip包，解压后：

**后端代码**：
- 复制到 `ruoyi-fastapi-backend/module_automation/`
- 包含：controller、service、dao、entity

**前端代码**：
- 复制到 `ruoyi-fastapi-frontend/src/views/automation/`
- 包含：index.vue、form.vue

### 第二阶段：手动集成（如果需要自定义）

如果代码生成器不能满足需求，可以手动开发。

#### 后端开发规范

##### 1. 目录结构
```
ruoyi-fastapi-backend/
└── module_automation/          # 自动化模块
    ├── __init__.py
    ├── entity/                 # 实体类
    │   ├── vo/                # 视图对象
    │   ├── query/             # 查询对象
    │   └── dto/               # 数据传输对象
    ├── dao/                   # 数据访问层
    ├── service/               # 业务逻辑层
    └── controller/            # 控制器层
```

##### 2. 实体类示例（entity/task.py）
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    """任务基础模型"""
    name: str = Field(..., description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    status: str = Field(default="pending", description="任务状态")

class TaskCreate(TaskBase):
    """创建任务"""
    pass

class TaskUpdate(TaskBase):
    """更新任务"""
    id: int

class TaskQuery(BaseModel):
    """查询任务"""
    name: Optional[str] = None
    status: Optional[str] = None
    page_num: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

class TaskVO(TaskBase):
    """任务视图对象"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

##### 3. DAO层示例（dao/task_dao.py）
```python
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

class TaskDao:
    """任务数据访问对象"""
    
    @staticmethod
    async def get_task_list(
        db: AsyncSession,
        query: TaskQuery
    ) -> tuple[List[Task], int]:
        """获取任务列表"""
        # 构建查询
        stmt = select(Task)
        
        # 添加查询条件
        if query.name:
            stmt = stmt.where(Task.name.like(f"%{query.name}%"))
        if query.status:
            stmt = stmt.where(Task.status == query.status)
        
        # 分页
        total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
        stmt = stmt.offset((query.page_num - 1) * query.page_size).limit(query.page_size)
        
        result = await db.execute(stmt)
        return result.scalars().all(), total
```

##### 4. Service层示例（service/task_service.py）
```python
from module_automation.dao.task_dao import TaskDao
from module_automation.entity.task import TaskCreate, TaskUpdate, TaskQuery, TaskVO
from utils.response_util import ResponseUtil

class TaskService:
    """任务服务"""
    
    @staticmethod
    async def get_task_list(query: TaskQuery, db: AsyncSession):
        """获取任务列表"""
        tasks, total = await TaskDao.get_task_list(db, query)
        
        return ResponseUtil.success(
            data={
                'rows': [TaskVO.from_orm(task) for task in tasks],
                'total': total
            }
        )
    
    @staticmethod
    async def create_task(task: TaskCreate, db: AsyncSession):
        """创建任务"""
        # 业务逻辑
        new_task = await TaskDao.create_task(db, task)
        return ResponseUtil.success(msg="创建成功")
```

##### 5. Controller层示例（controller/task_controller.py）
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_automation.service.task_service import TaskService
from module_automation.entity.task import TaskCreate, TaskUpdate, TaskQuery

router = APIRouter(prefix='/automation/task', tags=['自动化任务'])

@router.get('/list')
async def get_task_list(
    query: TaskQuery = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表"""
    return await TaskService.get_task_list(query, db)

@router.post('')
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建任务"""
    return await TaskService.create_task(task, db)

@router.put('')
async def update_task(
    task: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新任务"""
    return await TaskService.update_task(task, db)

@router.delete('/{task_id}')
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除任务"""
    return await TaskService.delete_task(task_id, db)
```

#### 前端开发规范

##### 1. 目录结构
```
ruoyi-fastapi-frontend/
└── src/
    └── views/
        └── automation/         # 自动化模块
            ├── task/          # 任务管理
            │   └── index.vue
            ├── session/       # 会话管理
            │   └── index.vue
            └── execution/     # 执行记录
                └── index.vue
```

##### 2. 页面示例（views/automation/task/index.vue）
```vue
<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true">
      <el-form-item label="任务名称" prop="name">
        <el-input
          v-model="queryParams.name"
          placeholder="请输入任务名称"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="任务状态" clearable>
          <el-option label="待执行" value="pending" />
          <el-option label="执行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
        >删除</el-button>
      </el-col>
    </el-row>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="taskList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="任务ID" align="center" prop="id" />
      <el-table-column label="任务名称" align="center" prop="name" :show-overflow-tooltip="true" />
      <el-table-column label="描述" align="center" prop="description" :show-overflow-tooltip="true" />
      <el-table-column label="状态" align="center" prop="status">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusLabel(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createdAt" width="180" />
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)">修改</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)">删除</el-button>
          <el-button link type="primary" icon="VideoPlay" @click="handleExecute(scope.row)">执行</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入内容" />
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
import { listTask, getTask, delTask, addTask, updateTask } from "@/api/automation/task";

const { proxy } = getCurrentInstance();

const taskList = ref([]);
const open = ref(false);
const loading = ref(true);
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
    status: null,
  },
  rules: {
    name: [
      { required: true, message: "任务名称不能为空", trigger: "blur" }
    ],
  }
});

const { queryParams, form, rules } = toRefs(data);

/** 查询任务列表 */
function getList() {
  loading.value = true;
  listTask(queryParams.value).then(response => {
    taskList.value = response.rows;
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
  proxy.resetForm("queryRef");
  handleQuery();
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加任务";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const id = row.id || ids.value;
  getTask(id).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改任务";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["formRef"].validate(valid => {
    if (valid) {
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
  const taskIds = row.id || ids.value;
  proxy.$modal.confirm('是否确认删除任务编号为"' + taskIds + '"的数据项？').then(function() {
    return delTask(taskIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 执行任务 */
function handleExecute(row) {
  proxy.$modal.confirm('是否确认执行任务"' + row.name + '"？').then(function() {
    // 调用执行API
    return executeTask(row.id);
  }).then(() => {
    proxy.$modal.msgSuccess("任务已开始执行");
    getList();
  }).catch(() => {});
}

function getStatusType(status) {
  const statusMap = {
    'pending': '',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  };
  return statusMap[status];
}

function getStatusLabel(status) {
  const labelMap = {
    'pending': '待执行',
    'running': '执行中',
    'completed': '已完成',
    'failed': '失败'
  };
  return labelMap[status];
}

function reset() {
  form.value = {
    id: null,
    name: null,
    description: null,
  };
  proxy.resetForm("formRef");
}

function cancel() {
  open.value = false;
  reset();
}

getList();
</script>
```

##### 3. API接口（api/automation/task.js）
```javascript
import request from '@/utils/request'

// 查询任务列表
export function listTask(query) {
  return request({
    url: '/automation/task/list',
    method: 'get',
    params: query
  })
}

// 查询任务详细
export function getTask(id) {
  return request({
    url: '/automation/task/' + id,
    method: 'get'
  })
}

// 新增任务
export function addTask(data) {
  return request({
    url: '/automation/task',
    method: 'post',
    data: data
  })
}

// 修改任务
export function updateTask(data) {
  return request({
    url: '/automation/task',
    method: 'put',
    data: data
  })
}

// 删除任务
export function delTask(id) {
  return request({
    url: '/automation/task/' + id,
    method: 'delete'
  })
}

// 执行任务
export function executeTask(id) {
  return request({
    url: '/automation/task/' + id + '/execute',
    method: 'post'
  })
}
```

### 第三阶段：配置菜单和权限

#### 1. 添加菜单

登录RuoYi → 系统管理 → 菜单管理 → 新增

**一级菜单：自动化管理**
- 菜单名称：自动化管理
- 显示排序：5
- 菜单图标：robot
- 路由地址：automation
- 组件路径：Layout

**二级菜单：任务管理**
- 上级菜单：自动化管理
- 菜单名称：任务管理
- 显示排序：1
- 菜单图标：list
- 路由地址：task
- 组件路径：automation/task/index
- 权限标识：automation:task:list

**按钮权限**
- 查询：automation:task:query
- 新增：automation:task:add
- 修改：automation:task:edit
- 删除：automation:task:remove
- 执行：automation:task:execute

#### 2. 分配权限

系统管理 → 角色管理 → 选择角色 → 分配权限

勾选"自动化管理"及其子菜单和按钮权限。

### 第四阶段：配置数据字典

系统管理 → 字典管理 → 新增

**任务状态字典**
- 字典名称：任务状态
- 字典类型：automation_task_status
- 状态：正常

**字典数据**
- pending - 待执行
- running - 执行中
- completed - 已完成
- failed - 失败
- cancelled - 已取消

## 推荐方案

**强烈推荐使用第一阶段的代码生成器方式**，因为：
1. ✅ 快速生成标准化代码
2. ✅ 自动符合RuoYi规范
3. ✅ 包含完整的CRUD功能
4. ✅ 前后端代码一起生成
5. ✅ 自动生成API文档

只需要在生成的代码基础上添加业务逻辑即可！

## 下一步

1. 登录RuoYi管理后台
2. 进入"系统工具" → "代码生成"
3. 导入业务表
4. 配置生成信息
5. 生成并下载代码
6. 解压并复制到对应目录
7. 配置菜单和权限
8. 测试功能

需要我帮你生成具体某个模块的代码吗？
