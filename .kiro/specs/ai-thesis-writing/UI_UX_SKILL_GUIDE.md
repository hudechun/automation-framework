# UI/UX Pro Max Skill 使用指南

## 安装状态

✅ **已安装**: UI/UX Pro Max Skill
📍 **位置**: `.shared/ui-ux-pro-max/`
🔧 **脚本**: `.shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py`

## 功能概述

UI/UX Pro Max 是一个综合性的设计系统工具，包含：
- 50+ 设计风格
- 97 种配色方案
- 57 种字体组合
- 99 条 UX 指南
- 25 种图表类型
- 9 种技术栈支持

## 基本使用

### 1. 生成设计系统（推荐）

```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "<关键词>" --design-system -p "项目名称"
```

**示例**:
```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "academic thesis education" --design-system -p "AI Thesis Writing System"
```

**输出内容**:
- 产品模式（Pattern）
- 设计风格（Style）
- 配色方案（Colors）
- 字体组合（Typography）
- 关键效果（Effects）
- 反模式（Anti-patterns）
- 交付前检查清单

### 2. 持久化设计系统

```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "<关键词>" --design-system --persist -p "项目名称"
```

这会创建：
- `design-system/MASTER.md` - 全局设计规则
- `design-system/pages/` - 页面特定覆盖

### 3. 特定领域搜索

```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "<关键词>" --domain <domain>
```

**可用领域**:
- `product` - 产品类型推荐
- `style` - UI 风格、颜色、效果
- `typography` - 字体组合
- `color` - 配色方案
- `landing` - 页面结构
- `chart` - 图表类型
- `ux` - 最佳实践
- `react` - React/Next.js 性能
- `web` - Web 界面指南

### 4. 技术栈指南

```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "<关键词>" --stack <stack>
```

**可用技术栈**:
- `html-tailwind` (默认)
- `react`
- `nextjs`
- `vue`
- `svelte`
- `swiftui`
- `react-native`
- `flutter`
- `shadcn`
- `jetpack-compose`

## 论文系统设计建议

### 当前推荐设计系统

基于 "academic thesis education" 关键词：

**设计风格**: Claymorphism（粘土风格）
- 柔和的 3D 效果
- 圆润的边角（16-24px）
- 厚边框（3-4px）
- 双重阴影
- 适合教育类应用

**配色方案**:
```
Primary:    #2563EB (蓝色)
Secondary:  #3B82F6 (浅蓝)
CTA:        #F97316 (橙色)
Background: #F8FAFC (浅灰)
Text:       #1E293B (深灰)
```

**字体组合**: Crimson Pro / Atkinson Hyperlegible
- Crimson Pro: 标题、重要文本
- Atkinson Hyperlegible: 正文、说明文字
- 特点：学术、易读、无障碍友好

**页面模式**: Feature-Rich Showcase
1. Hero 区域
2. 功能展示
3. CTA 行动号召

### 针对不同页面的建议

#### 1. 论文列表页
```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "dashboard list table academic" --domain ux
```

#### 2. 模板管理页
```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "card grid template showcase" --domain style
```

#### 3. 支付页面
```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "payment checkout secure" --domain ux
```

#### 4. 会员中心
```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "profile dashboard user account" --domain product
```

## 关键设计原则

### 图标使用
❌ **不要**: 使用 emoji 作为图标（🎨 🚀 ⚙️）
✅ **要**: 使用 SVG 图标库
- Heroicons
- Lucide
- Simple Icons

### 交互反馈
✅ 所有可点击元素添加 `cursor-pointer`
✅ 悬停状态提供视觉反馈
✅ 平滑过渡（150-300ms）
✅ 键盘导航焦点可见

### 明暗模式对比
✅ 浅色模式文本对比度 ≥ 4.5:1
✅ 玻璃/透明元素在浅色模式下可见
✅ 边框在两种模式下都可见
✅ 交付前测试两种模式

### 布局与间距
✅ 浮动元素与边缘保持适当间距
✅ 内容不被固定导航栏遮挡
✅ 响应式断点：375px, 768px, 1024px, 1440px
✅ 移动端无横向滚动

### 无障碍
✅ 所有图片有 alt 文本
✅ 表单输入有标签
✅ 颜色不是唯一指示器
✅ 尊重 `prefers-reduced-motion`

## 工作流程示例

### 场景：设计新的论文生成页面

1. **分析需求**
   - 产品类型：学术论文生成工具
   - 风格关键词：专业、学术、易用
   - 行业：教育

2. **生成设计系统**
   ```bash
   python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "academic paper generation wizard" --design-system -p "Thesis Generator"
   ```

3. **获取 UX 指南**
   ```bash
   python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "form wizard progress animation" --domain ux
   ```

4. **技术栈最佳实践**
   ```bash
   python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "form validation loading" --stack vue
   ```

5. **实现设计**
   - 应用推荐的配色方案
   - 使用推荐的字体组合
   - 遵循 UX 最佳实践
   - 实现关键效果

6. **交付前检查**
   - 使用输出的检查清单
   - 测试所有交互状态
   - 验证响应式布局
   - 检查无障碍性

## 输出格式

### ASCII 框（默认）
适合终端显示，清晰的视觉分隔

### Markdown
```bash
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "query" --design-system -f markdown
```
适合文档和保存

## 常用命令速查

```bash
# 生成完整设计系统
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "academic education" --design-system -p "Project"

# 搜索配色方案
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "professional blue" --domain color

# 搜索字体组合
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "elegant modern" --domain typography

# 获取 UX 最佳实践
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# Vue 技术栈指南
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "layout responsive" --stack vue

# 持久化设计系统
python .shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py "query" --design-system --persist -p "Project"
```

## 提示与技巧

1. **具体的关键词更好**: "healthcare SaaS dashboard" > "app"
2. **多次搜索**: 不同关键词揭示不同见解
3. **组合领域**: Style + Typography + Color = 完整设计系统
4. **始终检查 UX**: 搜索 "animation", "z-index", "accessibility"
5. **使用技术栈标志**: 获取特定实现的最佳实践
6. **迭代**: 如果首次搜索不匹配，尝试不同关键词

## 资源链接

- **GitHub**: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **本地路径**: `.shared/ui-ux-pro-max/`
- **脚本**: `.shared/ui-ux-pro-max/src/ui-ux-pro-max/scripts/search.py`
- **数据**: `.shared/ui-ux-pro-max/src/ui-ux-pro-max/data/`

---

**安装日期**: 2026-01-25
**版本**: Latest from GitHub
**状态**: ✅ 已安装并测试
