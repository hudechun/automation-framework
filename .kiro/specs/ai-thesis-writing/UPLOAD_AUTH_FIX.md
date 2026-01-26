# 上传认证问题修复

## 问题描述

用户上传文件时提示"用户未登录"，但实际上已经登录了。

### 错误信息
```
Uncaught (in promise) Error: A listener indicated an asynchronous response by returning true, 
but the message channel closed before a response was received
```

## 问题原因

**根本原因**：上传组件没有携带认证token

在RuoYi-Vue3-FastAPI系统中，所有API请求都需要携带JWT token进行身份验证。但是 `el-upload` 组件默认不会自动携带token，需要手动配置 `headers` 属性。

### 缺失的配置

```vue
<!-- ❌ 错误：没有携带token -->
<el-upload
  :action="uploadUrl"
  :on-success="handleSuccess"
>
  <el-button>上传</el-button>
</el-upload>
```

## 修复方案

### 1. 导入认证工具

```javascript
import { getToken } from '@/utils/auth'
```

### 2. 定义上传请求头

```javascript
// 上传请求头 - 携带认证token
const uploadHeaders = ref({ Authorization: 'Bearer ' + getToken() })
```

### 3. 配置上传组件

```vue
<!-- ✅ 正确：携带token -->
<el-upload
  :action="uploadUrl"
  :headers="uploadHeaders"
  :on-success="handleSuccess"
>
  <el-button>上传</el-button>
</el-upload>
```

## 完整修复代码

### 模板列表页面修复

```vue
<script setup name="TemplateList">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture, View, Star, Plus, Upload } from '@element-plus/icons-vue'
import { listTemplate, addTemplate, updateTemplate, delTemplate, applyTemplate } from '@/api/thesis/template'
import { listPaper } from '@/api/thesis/paper'
import { getToken } from '@/utils/auth'  // ⭐ 导入getToken

const { proxy } = getCurrentInstance()
const { thesis_template_type } = proxy.useDict('thesis_template_type')

// 上传地址
const uploadUrl = ref(import.meta.env.VITE_APP_BASE_API + '/common/upload')
// 上传请求头 - 携带认证token ⭐ 新增
const uploadHeaders = ref({ Authorization: 'Bearer ' + getToken() })

// ... 其他代码
</script>

<template>
  <!-- 模板文件上传 -->
  <el-form-item label="模板文件">
    <el-upload
      :action="uploadUrl"
      :headers="uploadHeaders"  <!-- ⭐ 添加headers -->
      :on-success="handleTemplateFileSuccess"
      :before-upload="beforeTemplateUpload"
      accept=".docx,.doc"
    >
      <el-button type="primary" icon="Upload">上传Word模板</el-button>
    </el-upload>
  </el-form-item>

  <!-- 缩略图上传 -->
  <el-form-item label="缩略图">
    <el-upload
      :action="uploadUrl"
      :headers="uploadHeaders"  <!-- ⭐ 添加headers -->
      :on-success="handleThumbnailSuccess"
      accept="image/*"
    >
      <img v-if="form.thumbnail" :src="form.thumbnail" class="thumbnail" />
      <el-icon v-else class="thumbnail-uploader-icon"><Plus /></el-icon>
    </el-upload>
  </el-form-item>
</template>
```

## 修复的文件

- ✅ `RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/thesis/template/list.vue`

## 验证步骤

### 1. 清除浏览器缓存
```
1. 打开浏览器开发者工具（F12）
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"
```

### 2. 重新登录
```
1. 退出登录
2. 重新登录系统
3. 确保token已刷新
```

### 3. 测试上传
```
1. 进入模板管理页面
2. 点击"新增模板"
3. 上传Word文档
4. ✅ 应该成功上传，不再提示"用户未登录"
```

### 4. 检查请求头
```
1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 上传文件
4. 查看上传请求
5. ✅ Request Headers 中应该包含 Authorization 字段
```

## 其他需要修复的页面

如果系统中还有其他页面使用了 `el-upload` 组件，也需要添加 `headers` 配置：

### 检查方法

```bash
# 搜索所有使用el-upload但没有headers的组件
grep -r "el-upload" --include="*.vue" | grep -v ":headers"
```

### 常见位置
- 用户头像上传
- 文件导入功能
- 图片上传功能
- 附件上传功能

## 技术说明

### JWT Token认证流程

1. **登录**：用户登录后，后端返回JWT token
2. **存储**：前端将token存储在localStorage中
3. **携带**：每次请求时，在请求头中携带token
4. **验证**：后端验证token的有效性
5. **响应**：验证通过后返回数据

### Token格式

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### getToken() 函数

位置：`src/utils/auth.js`

```javascript
export function getToken() {
  return Cookies.get(TokenKey)
}
```

## 常见问题

### Q1: 为什么其他API请求不需要手动添加token？

**A**: 因为系统使用了axios拦截器，在 `src/utils/request.js` 中自动为所有axios请求添加token。但是 `el-upload` 组件使用的是原生XMLHttpRequest，不会经过axios拦截器，所以需要手动配置。

### Q2: Token过期怎么办？

**A**: 系统会自动处理token过期：
1. 后端返回401状态码
2. 前端拦截器捕获401
3. 自动跳转到登录页
4. 用户重新登录获取新token

### Q3: 上传大文件时token会过期吗？

**A**: 可能会。建议：
1. 设置合理的token过期时间
2. 实现token自动刷新机制
3. 上传前检查token有效期

### Q4: 如何调试token问题？

**A**: 
1. 打开浏览器开发者工具
2. 查看Network标签
3. 检查请求头中的Authorization字段
4. 使用jwt.io解码token查看内容

## 安全建议

### 1. Token存储
- ✅ 使用httpOnly cookie（更安全）
- ⚠️ 使用localStorage（当前方案）
- ❌ 不要存储在sessionStorage（刷新会丢失）

### 2. Token传输
- ✅ 使用HTTPS加密传输
- ✅ 在请求头中传输（不在URL中）
- ❌ 不要在URL参数中传输token

### 3. Token过期
- ✅ 设置合理的过期时间（如2小时）
- ✅ 实现自动刷新机制
- ✅ 过期后自动跳转登录

## 相关文档

- [模板上传修复总结](.kiro/specs/ai-thesis-writing/TEMPLATE_UPLOAD_FIX.md)
- [模板上传测试指南](.kiro/specs/ai-thesis-writing/TEMPLATE_UPLOAD_TEST_GUIDE.md)
- [Session 12 总结](.kiro/specs/ai-thesis-writing/SESSION_12_TEMPLATE_UPLOAD_FIX.md)
- [JWT认证机制说明](../../RuoYi-Vue3-FastAPI/FastAPI认证机制说明.md)

## 总结

上传认证问题的核心是 `el-upload` 组件需要手动配置 `headers` 属性来携带JWT token。修复后，用户可以正常上传文件，不再出现"用户未登录"的错误提示。

**关键点**：
- ✅ 导入 `getToken` 函数
- ✅ 定义 `uploadHeaders` 变量
- ✅ 在 `el-upload` 组件中添加 `:headers="uploadHeaders"`
- ✅ 清除浏览器缓存后测试
