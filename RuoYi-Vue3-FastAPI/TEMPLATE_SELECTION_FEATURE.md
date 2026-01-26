# 论文模板选择功能实现

## 需求

在"论文管理"页面的新增论文对话框中,添加模板选择功能,用户可以选择已上传的格式模板。

## 实现方案

### 1. 前端修改

#### 修改文件: `ruoyi-fastapi-frontend/src/views/thesis/paper/list.vue`

**需要添加的功能**:

1. **在新增论文表单中添加模板选择字段**
   ```vue
   <el-form-item label="格式模板" prop="templateId">
     <el-select
       v-model="form.templateId"
       placeholder="请选择格式模板"
       clearable
       filterable
       style="width: 100%"
     >
       <el-option
         v-for="template in templateList"
         :key="template.templateId"
         :label="`${template.templateName} (${template.schoolName} - ${template.degreeLevel})`"
         :value="template.templateId"
       >
         <div style="display: flex; justify-content: space-between">
           <span>{{ template.templateName }}</span>
           <span style="color: #8492a6; font-size: 13px">
             {{ template.schoolName }} - {{ template.degreeLevel }}
           </span>
         </div>
       </el-option>
     </el-select>
   </el-form-item>
   ```

2. **添加模板列表数据**
   ```javascript
   const templateList = ref([])
   
   // 获取模板列表
   const getTemplateList = async () => {
     try {
       const res = await listTemplate({ status: '0', pageNum: 1, pageSize: 100 })
       templateList.value = res.rows || []
     } catch (error) {
       console.error('获取模板列表失败:', error)
     }
   }
   
   // 在组件挂载时获取模板列表
   onMounted(() => {
     getList()
     getTemplateList()
   })
   ```

3. **导入模板API**
   ```javascript
   import { listTemplate } from '@/api/thesis/template'
   ```

### 2. API接口

#### 创建文件: `ruoyi-fastapi-frontend/src/api/thesis/template.js`

```javascript
import request from '@/utils/request'

// 查询模板列表
export function listTemplate(query) {
  return request({
    url: '/thesis/template/list',
    method: 'get',
    params: query
  })
}

// 查询模板详情
export function getTemplate(templateId) {
  return request({
    url: `/thesis/template/${templateId}`,
    method: 'get'
  })
}

// 新增模板
export function addTemplate(data) {
  return request({
    url: '/thesis/template',
    method: 'post',
    data: data
  })
}

// 修改模板
export function updateTemplate(data) {
  return request({
    url: '/thesis/template',
    method: 'put',
    data: data
  })
}

// 删除模板
export function delTemplate(templateId) {
  return request({
    url: `/thesis/template/${templateId}`,
    method: 'delete'
  })
}
```

### 3. 数据库字段

确认 `ai_write_thesis` 表中有 `template_id` 字段:

```sql
ALTER TABLE ai_write_thesis 
ADD COLUMN template_id INT NULL COMMENT '格式模板ID' AFTER type;

ALTER TABLE ai_write_thesis 
ADD CONSTRAINT fk_thesis_template 
FOREIGN KEY (template_id) REFERENCES ai_write_format_template(template_id);
```

### 4. 后端修改

#### 修改文件: `module_thesis/entity/vo/thesis_vo.py`

添加 `template_id` 字段:

```python
class ThesisModel(BaseModel):
    # ... 其他字段
    template_id: Optional[int] = Field(default=None, description='格式模板ID')
    # ... 其他字段
```

### 5. 用户体验优化

1. **模板预览**
   - 点击模板选项时显示模板详情
   - 显示模板的格式要求

2. **智能推荐**
   - 根据用户的学校、专业自动推荐合适的模板
   - 显示热门模板

3. **模板应用**
   - 选择模板后,自动应用格式规则
   - 提示用户模板已应用

## 实现步骤

### 步骤1: 创建模板API文件

创建 `ruoyi-fastapi-frontend/src/api/thesis/template.js`

### 步骤2: 修改论文管理页面

修改 `ruoyi-fastapi-frontend/src/views/thesis/paper/list.vue`:
1. 导入模板API
2. 添加模板列表数据
3. 在表单中添加模板选择字段
4. 添加获取模板列表的方法

### 步骤3: 数据库添加字段

执行SQL添加 `template_id` 字段

### 步骤4: 后端添加字段

修改 `thesis_vo.py` 添加 `template_id` 字段

### 步骤5: 测试

1. 上传几个测试模板
2. 新建论文时选择模板
3. 验证模板ID正确保存

## 完整代码示例

由于代码较长,我会分别创建修改后的文件。

## 注意事项

1. **模板状态过滤**: 只显示启用状态的模板 (`status='0'`)
2. **权限控制**: 确保用户只能看到自己有权限使用的模板
3. **错误处理**: 模板加载失败时的友好提示
4. **性能优化**: 模板列表缓存,避免重复请求

## 后续优化

1. **模板分类**: 按学校、专业、学历层次分类
2. **模板搜索**: 支持模板名称、学校名称搜索
3. **模板收藏**: 用户可以收藏常用模板
4. **模板预览**: 点击查看模板详细格式要求
