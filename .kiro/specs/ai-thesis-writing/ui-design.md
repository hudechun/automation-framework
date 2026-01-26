# AI论文写作系统 - UI/UX设计规范

## 1. 设计理念

### 1.1 核心原则
- **专业学术**: 体现学术严谨性和专业性
- **简洁高效**: 减少认知负担，聚焦核心功能
- **智能引导**: 清晰的流程指引，降低学习成本
- **信任感**: 通过设计传递可靠性和安全性

### 1.2 目标用户画像
- **本科生/研究生/博士生**: 18-30岁，熟悉互联网产品
- **使用场景**: 论文写作、格式调整、内容优化
- **痛点**: 格式复杂、写作困难、时间紧张、查重压力

---

## 2. 视觉设计系统

### 2.1 色彩系统

**主色调 - 学术蓝**
```css
/* 主色 - 传递专业、信任、智慧 */
--primary-50: #EFF6FF;   /* 浅蓝背景 */
--primary-100: #DBEAFE;  /* 悬停背景 */
--primary-200: #BFDBFE;  /* 边框 */
--primary-300: #93C5FD;  /* 禁用状态 */
--primary-400: #60A5FA;  /* 次要按钮 */
--primary-500: #3B82F6;  /* 主按钮 */
--primary-600: #2563EB;  /* 主按钮悬停 */
--primary-700: #1D4ED8;  /* 主按钮按下 */
--primary-800: #1E40AF;  /* 深色强调 */
--primary-900: #1E3A8A;  /* 最深 */
```

**辅助色 - 成功绿**
```css
/* 成功状态 - 完成、通过、正确 */
--success-50: #F0FDF4;
--success-500: #22C55E;
--success-600: #16A34A;
```

**辅助色 - 警告橙**
```css
/* 警告状态 - 配额不足、需要注意 */
--warning-50: #FFFBEB;
--warning-500: #F59E0B;
--warning-600: #D97706;
```

**辅助色 - 错误红**
```css
/* 错误状态 - 失败、拒绝、超限 */
--error-50: #FEF2F2;
--error-500: #EF4444;
--error-600: #DC2626;
```

**中性色 - 灰度**
```css
/* 文本和背景 */
--gray-50: #F9FAFB;    /* 页面背景 */
--gray-100: #F3F4F6;   /* 卡片背景 */
--gray-200: #E5E7EB;   /* 边框 */
--gray-300: #D1D5DB;   /* 禁用边框 */
--gray-400: #9CA3AF;   /* 占位符 */
--gray-500: #6B7280;   /* 次要文本 */
--gray-600: #4B5563;   /* 辅助文本 */
--gray-700: #374151;   /* 正文 */
--gray-800: #1F2937;   /* 标题 */
--gray-900: #111827;   /* 主标题 */
```

**特殊色 - AI功能**
```css
/* AI相关功能的视觉标识 */
--ai-gradient: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
--ai-glow: 0 0 20px rgba(102, 126, 234, 0.3);
```

### 2.2 字体系统

**字体家族**
```css
/* 中文优先，西文衬底 */
--font-sans: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
--font-mono: "SF Mono", "Consolas", "Monaco", monospace;
```

**字体大小**
```css
--text-xs: 0.75rem;    /* 12px - 辅助说明 */
--text-sm: 0.875rem;   /* 14px - 次要文本 */
--text-base: 1rem;     /* 16px - 正文 */
--text-lg: 1.125rem;   /* 18px - 小标题 */
--text-xl: 1.25rem;    /* 20px - 卡片标题 */
--text-2xl: 1.5rem;    /* 24px - 页面标题 */
--text-3xl: 1.875rem;  /* 30px - 主标题 */
--text-4xl: 2.25rem;   /* 36px - 大标题 */
```

**字重**
```css
--font-normal: 400;    /* 正文 */
--font-medium: 500;    /* 强调 */
--font-semibold: 600;  /* 小标题 */
--font-bold: 700;      /* 标题 */
```

**行高**
```css
--leading-tight: 1.25;   /* 标题 */
--leading-normal: 1.5;   /* 正文 */
--leading-relaxed: 1.75; /* 长文本 */
```

### 2.3 间距系统

**基础间距单位: 4px**
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
```

### 2.4 圆角系统

```css
--radius-sm: 0.25rem;   /* 4px - 小元素 */
--radius-md: 0.5rem;    /* 8px - 按钮、输入框 */
--radius-lg: 0.75rem;   /* 12px - 卡片 */
--radius-xl: 1rem;      /* 16px - 大卡片 */
--radius-2xl: 1.5rem;   /* 24px - 模态框 */
--radius-full: 9999px;  /* 圆形 */
```

### 2.5 阴影系统

```css
/* 卡片阴影 */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* 悬浮效果 */
--shadow-hover: 0 12px 24px -4px rgba(0, 0, 0, 0.12);

/* AI功能特殊阴影 */
--shadow-ai: 0 8px 32px rgba(102, 126, 234, 0.2);
```

---

## 3. 组件设计规范

### 3.1 按钮 (Button)

**主按钮 (Primary)**
```html
<button class="btn-primary">
  创建论文
</button>
```
- 背景: `--primary-600`
- 文字: 白色
- 圆角: `--radius-md`
- 内边距: `12px 24px`
- 悬停: `--primary-700` + `--shadow-md`
- 禁用: `--primary-300` + 不可点击

**次要按钮 (Secondary)**
- 背景: 透明
- 边框: `1px solid --primary-600`
- 文字: `--primary-600`
- 悬停: 背景 `--primary-50`

**危险按钮 (Danger)**
- 背景: `--error-600`
- 文字: 白色
- 用于删除、取消等操作

**AI功能按钮**
```html
<button class="btn-ai">
  <span class="ai-icon">✨</span>
  AI生成大纲
</button>
```
- 背景: `--ai-gradient`
- 文字: 白色
- 阴影: `--shadow-ai`
- 图标: 魔法棒或星星

### 3.2 输入框 (Input)

**文本输入**
```html
<div class="input-group">
  <label>论文标题</label>
  <input type="text" placeholder="请输入论文标题">
  <span class="input-hint">建议20-30字</span>
</div>
```
- 边框: `1px solid --gray-300`
- 圆角: `--radius-md`
- 内边距: `12px 16px`
- 聚焦: 边框 `--primary-500` + 阴影
- 错误: 边框 `--error-500`

**富文本编辑器**
- 使用TinyMCE或Quill
- 工具栏: 固定在顶部
- 最小高度: 400px
- 字数统计: 右下角显示

### 3.3 卡片 (Card)

**基础卡片**
```html
<div class="card">
  <div class="card-header">
    <h3>论文标题</h3>
    <span class="badge">草稿</span>
  </div>
  <div class="card-body">
    <p>论文内容预览...</p>
  </div>
  <div class="card-footer">
    <span class="text-muted">更新于 2小时前</span>
    <button>继续编辑</button>
  </div>
</div>
```
- 背景: 白色
- 边框: `1px solid --gray-200`
- 圆角: `--radius-lg`
- 阴影: `--shadow-sm`
- 悬停: `--shadow-md` + 轻微上移

**AI功能卡片**
- 左侧: AI图标 + 渐变背景
- 右侧: 功能说明 + 操作按钮
- 特殊阴影: `--shadow-ai`

### 3.4 徽章 (Badge)

**状态徽章**
```html
<span class="badge badge-success">已完成</span>
<span class="badge badge-warning">生成中</span>
<span class="badge badge-error">失败</span>
<span class="badge badge-info">草稿</span>
```
- 圆角: `--radius-full`
- 内边距: `4px 12px`
- 字体: `--text-xs` + `--font-medium`

**会员徽章**
```html
<span class="badge badge-premium">
  <span class="badge-icon">👑</span>
  旗舰版
</span>
```
- 渐变背景
- 金色图标

### 3.5 进度条 (Progress)

**生成进度**
```html
<div class="progress">
  <div class="progress-bar" style="width: 60%">
    <span class="progress-text">正在生成第3章 (60%)</span>
  </div>
</div>
```
- 高度: 24px
- 圆角: `--radius-md`
- 背景: `--gray-200`
- 进度条: `--primary-600`
- 动画: 平滑过渡

**配额进度**
```html
<div class="quota-progress">
  <div class="quota-bar" style="width: 75%"></div>
  <span class="quota-text">已使用 7,500 / 10,000 字</span>
</div>
```
- 显示剩余配额
- 接近上限时变为警告色

### 3.6 模态框 (Modal)

**标准模态框**
```html
<div class="modal">
  <div class="modal-overlay"></div>
  <div class="modal-content">
    <div class="modal-header">
      <h3>确认删除</h3>
      <button class="modal-close">×</button>
    </div>
    <div class="modal-body">
      <p>确定要删除这篇论文吗？此操作不可恢复。</p>
    </div>
    <div class="modal-footer">
      <button class="btn-secondary">取消</button>
      <button class="btn-danger">删除</button>
    </div>
  </div>
</div>
```
- 遮罩: 黑色 50% 透明度
- 内容: 白色背景 + `--shadow-xl`
- 圆角: `--radius-2xl`
- 最大宽度: 600px
- 动画: 淡入 + 缩放

### 3.7 表格 (Table)

**数据表格**
- 表头: 背景 `--gray-50` + 粗体
- 行: 悬停背景 `--gray-50`
- 边框: `--gray-200`
- 分页: 底部居中

---

## 4. 页面布局规范

### 4.1 整体布局

**顶部导航栏**
- 高度: 64px
- 背景: 白色
- 阴影: `--shadow-sm`
- 内容: Logo + 导航菜单 + 用户信息

**侧边栏 (可选)**
- 宽度: 240px
- 背景: `--gray-50`
- 用于论文编辑页面的章节导航

**主内容区**
- 最大宽度: 1280px
- 居中对齐
- 内边距: `--space-8`

**底部**
- 背景: `--gray-50`
- 内容: 版权信息 + 链接

### 4.2 响应式断点

```css
/* 移动端 */
@media (max-width: 640px) {
  /* 单列布局 */
}

/* 平板 */
@media (min-width: 641px) and (max-width: 1024px) {
  /* 两列布局 */
}

/* 桌面 */
@media (min-width: 1025px) {
  /* 三列布局 */
}
```

---

## 5. 页面设计

### 5.1 首页 / 论文列表

**布局**
```
┌─────────────────────────────────────────┐
│  顶部导航栏                              │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │  欢迎回来，张三                    │  │
│  │  您还有 5,000 字配额               │  │
│  │  [创建新论文]                      │  │
│  └───────────────────────────────────┘  │
│                                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ 论文1   │ │ 论文2   │ │ 论文3   │   │
│  │ 草稿    │ │ 生成中  │ │ 已完成  │   │
│  │ 更新于  │ │ 60%     │ │ 导出    │   │
│  └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────┘
```

**关键元素**
- 欢迎卡片: 显示用户名 + 配额 + 快速操作
- 论文卡片网格: 3列布局（桌面）
- 筛选器: 状态、时间、关键词
- 排序: 最近更新、创建时间、标题

### 5.2 创建论文页面

**步骤指示器**
```
1. 基本信息 → 2. 选择模板 → 3. 生成大纲 → 4. 开始写作
   (当前)
```

**表单布局**
- 左侧: 表单字段
- 右侧: 实时预览 / 提示信息
- 底部: 上一步 / 下一步按钮

### 5.3 论文编辑页面

**三栏布局**
```
┌──────┬────────────────────┬──────┐
│ 章节 │   富文本编辑器      │ 工具 │
│ 导航 │                    │ 面板 │
│      │                    │      │
│ 摘要 │   正在编辑第1章...  │ AI  │
│ 第1章│                    │ 优化 │
│ 第2章│                    │      │
│ ...  │                    │ 版本 │
│      │                    │ 历史 │
└──────┴────────────────────┴──────┘
```

**左侧章节导航**
- 可折叠的树形结构
- 当前章节高亮
- 拖拽排序

**中间编辑器**
- 全屏模式切换
- 字数统计（实时）
- 自动保存提示

**右侧工具面板**
- AI优化按钮
- 版本历史
- 导出选项

### 5.4 会员套餐页面

**对比表格**
```
┌─────────┬─────────┬─────────┬─────────┐
│ 免费版  │ 基础版  │ 专业版  │ 旗舰版  │
│ ¥0     │ ¥99/月  │ ¥299/月 │ ¥599/月 │
├─────────┼─────────┼─────────┼─────────┤
│ 5K字   │ 50K字   │ 200K字  │ 无限    │
│ 1次    │ 10次    │ 50次    │ 无限    │
│ ✓基础  │ ✓去AI化 │ ✓润色   │ ✓全部   │
│        │         │ ✓查重   │ ✓审核   │
└─────────┴─────────┴─────────┴─────────┘
```

**推荐标签**
- 最受欢迎
- 性价比之选
- 限时优惠

### 5.5 支付页面

**订单确认**
- 套餐信息
- 价格明细
- 支付方式选择（微信/支付宝）
- 二维码展示

**支付状态**
- 等待支付: 倒计时
- 支付成功: 跳转到论文列表
- 支付失败: 重试按钮

---

## 6. 交互设计

### 6.1 加载状态

**骨架屏 (Skeleton)**
- 用于列表加载
- 灰色占位块 + 脉冲动画

**加载指示器 (Spinner)**
- 用于按钮点击后
- 圆形旋转动画

**进度条**
- 用于AI生成过程
- 显示百分比和当前步骤

### 6.2 反馈提示

**Toast通知**
```html
<div class="toast toast-success">
  <span class="toast-icon">✓</span>
  <span class="toast-message">保存成功</span>
</div>
```
- 位置: 右上角
- 自动消失: 3秒
- 类型: 成功、警告、错误、信息

**确认对话框**
- 用于删除、取消等操作
- 清晰的操作说明
- 主次按钮区分

### 6.3 动画效果

**页面切换**
- 淡入淡出: 200ms
- 避免过度动画

**卡片悬停**
- 上移: 4px
- 阴影增强
- 过渡: 150ms

**按钮点击**
- 缩放: 0.98
- 过渡: 100ms

**AI生成动画**
- 打字机效果
- 渐进式显示内容

---

## 7. 可访问性 (A11y)

### 7.1 键盘导航
- 所有交互元素可通过Tab键访问
- 焦点状态清晰可见
- 支持快捷键（Ctrl+S保存等）

### 7.2 屏幕阅读器
- 所有图片有alt属性
- 表单有label标签
- ARIA标签正确使用

### 7.3 颜色对比
- 文本对比度 ≥ 4.5:1
- 大文本对比度 ≥ 3:1
- 不仅依赖颜色传递信息

---

## 8. 性能优化

### 8.1 图片优化
- 使用WebP格式
- 懒加载
- 响应式图片

### 8.2 代码分割
- 路由级别代码分割
- 组件按需加载

### 8.3 缓存策略
- 静态资源长期缓存
- API响应适当缓存

---

## 9. 设计资源

### 9.1 图标库
- **Heroicons**: 主要图标库
- **Lucide Icons**: 补充图标
- **Simple Icons**: 品牌Logo

### 9.2 插图
- **unDraw**: 免费插图
- **Storyset**: 可定制插图

### 9.3 设计工具
- **Figma**: 设计稿
- **Tailwind CSS**: CSS框架
- **Element Plus**: Vue组件库

---

## 10. 实现检查清单

### 视觉质量
- [ ] 无emoji作为图标（使用SVG）
- [ ] 图标来自统一图标集
- [ ] 品牌Logo正确
- [ ] 悬停状态不引起布局偏移
- [ ] 直接使用主题色（不用var()包装）

### 交互
- [ ] 可点击元素有cursor-pointer
- [ ] 悬停状态有视觉反馈
- [ ] 过渡动画流畅（150-300ms）
- [ ] 键盘导航焦点可见

### 明暗模式
- [ ] 浅色模式文本对比度充足
- [ ] 玻璃/透明元素在浅色模式可见
- [ ] 边框在两种模式都可见
- [ ] 交付前测试两种模式

### 布局
- [ ] 浮动元素与边缘有适当间距
- [ ] 内容不被固定导航栏遮挡
- [ ] 响应式适配（375px, 768px, 1024px, 1440px）
- [ ] 无水平滚动条（移动端）

### 可访问性
- [ ] 所有图片有alt文本
- [ ] 表单输入有label
- [ ] 颜色不是唯一指示器
- [ ] 尊重prefers-reduced-motion

---

## 11. 参考案例

### 11.1 类似产品
- **Notion**: 编辑器体验
- **Grammarly**: AI辅助写作
- **Overleaf**: 学术写作平台
- **语雀**: 文档协作

### 11.2 设计灵感
- **Dribbble**: 搜索 "academic writing"
- **Behance**: 搜索 "education platform"
- **Awwwards**: 优秀SaaS产品设计
