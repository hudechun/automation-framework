# AI 论文系统 - 现代化设计系统

## 设计目标

✨ **商业化风格** - 专业、现代、高端
🎨 **视觉吸引力** - 漂亮、时尚、有品质感
👆 **易用性** - 直观、流畅、高效
⚡ **保持功能** - 所有现有功能完整保留

## 核心设计系统

### 设计风格：Glassmorphism（玻璃拟态）

**特点**：
- 磨砂玻璃效果
- 透明背景
- 模糊背景
- 多层次深度
- 现代高端感

**适用场景**：
- 现代 SaaS 平台
- 金融仪表板
- 高端企业应用
- 生活方式应用

### 配色方案

```css
/* 主色调 - 靛蓝色系（专业、可信赖） */
--primary: #6366F1;        /* 主色 */
--primary-light: #818CF8;  /* 浅色 */
--primary-dark: #4F46E5;   /* 深色 */

/* 辅助色 - 翡翠绿（成功、行动） */
--success: #10B981;
--success-light: #34D399;

/* 警告色 */
--warning: #F59E0B;
--warning-light: #FBBF24;

/* 危险色 */
--danger: #EF4444;
--danger-light: #F87171;

/* 背景色 */
--bg-primary: #F5F3FF;     /* 浅紫色背景 */
--bg-secondary: #FFFFFF;   /* 白色 */
--bg-glass: rgba(255, 255, 255, 0.7);  /* 玻璃效果 */

/* 文字色 */
--text-primary: #1E1B4B;   /* 深紫色 */
--text-secondary: #64748B; /* 灰色 */
--text-muted: #94A3B8;     /* 浅灰色 */
```

### 字体系统

**标题字体**: Poppins
- 现代、专业、清晰
- 用于：页面标题、卡片标题、按钮

**正文字体**: Open Sans
- 易读、友好、专业
- 用于：正文、表单、描述文字

```css
/* 字体大小 */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* 字重 */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 间距系统

```css
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-5: 1.25rem;  /* 20px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */
--spacing-10: 2.5rem;  /* 40px */
--spacing-12: 3rem;    /* 48px */
--spacing-16: 4rem;    /* 64px */
```

### 圆角系统

```css
--radius-sm: 0.375rem;  /* 6px */
--radius-md: 0.5rem;    /* 8px */
--radius-lg: 0.75rem;   /* 12px */
--radius-xl: 1rem;      /* 16px */
--radius-2xl: 1.5rem;   /* 24px */
--radius-full: 9999px;  /* 圆形 */
```

### 阴影系统

```css
/* 玻璃效果阴影 */
--shadow-glass: 0 8px 32px 0 rgba(31, 38, 135, 0.15);

/* 卡片阴影 */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* 悬停阴影 */
--shadow-hover: 0 20px 40px -5px rgba(99, 102, 241, 0.3);
```

### 玻璃效果

```css
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-glass);
}

.glass-card-strong {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
}
```

## 组件设计规范

### 1. 卡片组件

```vue
<div class="glass-card">
  <!-- 卡片内容 -->
</div>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 1.5rem;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
  transition: all 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -5px rgba(99, 102, 241, 0.3);
}
</style>
```

### 2. 按钮组件

```vue
<!-- 主按钮 -->
<button class="btn-primary">
  <span>按钮文字</span>
</button>

<!-- 次要按钮 -->
<button class="btn-secondary">
  <span>按钮文字</span>
</button>

<style scoped>
.btn-primary {
  background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  color: #6366F1;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(99, 102, 241, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: #6366F1;
}
</style>
```

### 3. 输入框组件

```vue
<div class="input-wrapper">
  <input type="text" class="glass-input" placeholder="请输入...">
</div>

<style scoped>
.glass-input {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  color: #1E1B4B;
  transition: all 0.3s ease;
  width: 100%;
}

.glass-input:focus {
  outline: none;
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: rgba(255, 255, 255, 0.9);
}

.glass-input::placeholder {
  color: #94A3B8;
}
</style>
```

### 4. 状态标签

```vue
<span class="status-badge status-success">已完成</span>
<span class="status-badge status-warning">进行中</span>
<span class="status-badge status-info">草稿</span>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.status-success {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-warning {
  background: rgba(245, 158, 11, 0.1);
  color: #D97706;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-info {
  background: rgba(99, 102, 241, 0.1);
  color: #4F46E5;
  border: 1px solid rgba(99, 102, 241, 0.3);
}
</style>
```

### 5. 进度条

```vue
<div class="progress-bar">
  <div class="progress-fill" :style="{ width: progress + '%' }"></div>
</div>

<style scoped>
.progress-bar {
  width: 100%;
  height: 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366F1 0%, #818CF8 100%);
  border-radius: 9999px;
  transition: width 0.3s ease;
}
</style>
```

## 动画规范

### 过渡时间

```css
--transition-fast: 150ms;
--transition-base: 200ms;
--transition-slow: 300ms;
```

### 缓动函数

```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### 动画原则

1. **微交互**: 150-300ms
2. **页面过渡**: 300-500ms
3. **加载动画**: 持续进行
4. **悬停效果**: 200ms ease-out
5. **尊重用户偏好**: 检查 `prefers-reduced-motion`

## 响应式断点

```css
/* 移动端 */
@media (max-width: 640px) { }

/* 平板 */
@media (min-width: 768px) { }

/* 桌面 */
@media (min-width: 1024px) { }

/* 大屏 */
@media (min-width: 1440px) { }
```

## 图标系统

使用 **Lucide Icons** 或 **Heroicons**

```vue
<script setup>
import { FileText, Plus, Edit, Trash2, Download } from 'lucide-vue-next'
</script>

<template>
  <FileText :size="20" />
</template>
```

## 无障碍规范

1. **对比度**: 文字与背景对比度 ≥ 4.5:1
2. **焦点状态**: 所有交互元素有清晰的焦点指示
3. **键盘导航**: 支持 Tab 键导航
4. **屏幕阅读器**: 使用语义化 HTML 和 ARIA 标签
5. **动画**: 尊重 `prefers-reduced-motion`

## 性能优化

1. **使用 transform 和 opacity** 进行动画
2. **避免动画 width/height/top/left**
3. **限制同时动画的元素数量** (1-2个)
4. **使用 will-change** 提示浏览器优化
5. **懒加载图片和组件**

---

**设计系统版本**: 1.0
**创建日期**: 2026-01-25
**适用项目**: AI 论文写作系统
