# 智能教学助手2.0 UI组件库文档

## 概述

本文档详细介绍了智能教学助手2.0的UI组件库，包含所有可复用组件的使用方法、参数配置和示例代码。组件库基于现代Web标准设计，支持响应式布局和无障碍访问。

## 设计原则

### 1. 一致性
- 统一的视觉语言和交互模式
- 标准化的组件API和命名规范
- 一致的间距、色彩和字体系统

### 2. 可复用性
- 模块化设计，组件可独立使用
- 灵活的参数配置和扩展机制
- 支持主题定制和样式覆盖

### 3. 可访问性
- 符合WCAG 2.1 AA标准
- 支持键盘导航和屏幕阅读器
- 提供高对比度模式

### 4. 性能优化
- 轻量级实现，最小化CSS和JS体积
- 支持按需加载和树摇优化
- 优化的动画性能

## 基础组件

### 1. 按钮组件 (Button)

#### 基本用法
```html
<button class="btn btn-primary">主要按钮</button>
<button class="btn btn-secondary">次要按钮</button>
<button class="btn btn-outline">边框按钮</button>
<button class="btn btn-text">文本按钮</button>
```

#### 尺寸变体
```html
<button class="btn btn-primary btn-sm">小按钮</button>
<button class="btn btn-primary">默认按钮</button>
<button class="btn btn-primary btn-lg">大按钮</button>
```

#### 状态变体
```html
<button class="btn btn-primary" disabled>禁用状态</button>
<button class="btn btn-primary loading">加载状态</button>
<button class="btn btn-success">成功状态</button>
<button class="btn btn-warning">警告状态</button>
<button class="btn btn-error">错误状态</button>
```

#### 图标按钮
```html
<button class="btn btn-primary">
    <i class="fas fa-plus"></i>
    添加
</button>
<button class="btn btn-icon">
    <i class="fas fa-search"></i>
</button>
```

#### 参数说明
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| type | string | 'button' | 按钮类型 |
| size | string | 'default' | 尺寸：sm, default, lg |
| variant | string | 'primary' | 样式变体 |
| disabled | boolean | false | 是否禁用 |
| loading | boolean | false | 是否显示加载状态 |

### 2. 输入框组件 (Input)

#### 基本用法
```html
<div class="form-group">
    <label for="username">用户名</label>
    <input type="text" id="username" class="form-input" placeholder="请输入用户名">
</div>
```

#### 输入框变体
```html
<!-- 文本输入框 -->
<input type="text" class="form-input" placeholder="文本输入">

<!-- 密码输入框 -->
<input type="password" class="form-input" placeholder="密码输入">

<!-- 数字输入框 -->
<input type="number" class="form-input" placeholder="数字输入">

<!-- 邮箱输入框 -->
<input type="email" class="form-input" placeholder="邮箱输入">

<!-- 搜索输入框 -->
<input type="search" class="form-input form-input-search" placeholder="搜索...">
```

#### 输入框状态
```html
<input type="text" class="form-input" placeholder="默认状态">
<input type="text" class="form-input form-input-success" placeholder="成功状态">
<input type="text" class="form-input form-input-warning" placeholder="警告状态">
<input type="text" class="form-input form-input-error" placeholder="错误状态">
<input type="text" class="form-input" placeholder="禁用状态" disabled>
```

#### 输入框组合
```html
<div class="input-group">
    <span class="input-group-text">@</span>
    <input type="text" class="form-input" placeholder="用户名">
</div>

<div class="input-group">
    <input type="text" class="form-input" placeholder="搜索内容">
    <button class="btn btn-primary">搜索</button>
</div>
```

### 3. 卡片组件 (Card)

#### 基本用法
```html
<div class="card">
    <div class="card-header">
        <h3 class="card-title">卡片标题</h3>
    </div>
    <div class="card-body">
        <p>卡片内容</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">操作</button>
    </div>
</div>
```

#### 卡片变体
```html
<!-- 简单卡片 -->
<div class="card card-simple">
    <div class="card-body">
        <p>简单卡片内容</p>
    </div>
</div>

<!-- 阴影卡片 -->
<div class="card card-shadow">
    <div class="card-body">
        <p>带阴影的卡片</p>
    </div>
</div>

<!-- 边框卡片 -->
<div class="card card-bordered">
    <div class="card-body">
        <p>带边框的卡片</p>
    </div>
</div>
```

#### 卡片网格
```html
<div class="card-grid">
    <div class="card">
        <div class="card-body">
            <h4>卡片1</h4>
            <p>内容1</p>
        </div>
    </div>
    <div class="card">
        <div class="card-body">
            <h4>卡片2</h4>
            <p>内容2</p>
        </div>
    </div>
</div>
```

### 4. 导航组件 (Navigation)

#### 顶部导航
```html
<nav class="navbar">
    <div class="navbar-brand">
        <img src="logo.png" alt="Logo">
        <span>智能教学助手</span>
    </div>
    <ul class="navbar-nav">
        <li class="nav-item">
            <a href="#" class="nav-link active">首页</a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link">备课助手</a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link">课堂AI</a>
        </li>
    </ul>
</nav>
```

#### 侧边导航
```html
<nav class="sidebar">
    <div class="sidebar-header">
        <h3>菜单</h3>
    </div>
    <ul class="sidebar-nav">
        <li class="nav-item">
            <a href="#" class="nav-link active">
                <i class="fas fa-home"></i>
                <span>首页</span>
            </a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link">
                <i class="fas fa-book"></i>
                <span>备课助手</span>
            </a>
        </li>
    </ul>
</nav>
```

#### 面包屑导航
```html
<nav class="breadcrumb">
    <a href="#" class="breadcrumb-item">首页</a>
    <span class="breadcrumb-separator">/</span>
    <a href="#" class="breadcrumb-item">备课助手</a>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-item active">教材分析</span>
</nav>
```

### 5. 表格组件 (Table)

#### 基本表格
```html
<div class="table-container">
    <table class="table">
        <thead>
            <tr>
                <th>姓名</th>
                <th>学号</th>
                <th>成绩</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>张三</td>
                <td>S001</td>
                <td>85</td>
                <td>
                    <button class="btn btn-sm btn-outline">编辑</button>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

#### 表格变体
```html
<!-- 条纹表格 -->
<table class="table table-striped">
    <!-- 表格内容 -->
</table>

<!-- 边框表格 -->
<table class="table table-bordered">
    <!-- 表格内容 -->
</table>

<!-- 悬停效果表格 -->
<table class="table table-hover">
    <!-- 表格内容 -->
</table>

<!-- 紧凑表格 -->
<table class="table table-sm">
    <!-- 表格内容 -->
</table>
```

#### 响应式表格
```html
<div class="table-responsive">
    <table class="table">
        <!-- 表格内容 -->
    </table>
</div>
```

## 复合组件

### 1. 模态框组件 (Modal)

#### 基本用法
```html
<div class="modal" id="exampleModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 class="modal-title">模态框标题</h3>
            <button class="modal-close">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="modal-body">
            <p>模态框内容</p>
        </div>
        <div class="modal-footer">
            <button class="btn btn-outline">取消</button>
            <button class="btn btn-primary">确认</button>
        </div>
    </div>
</div>
```

#### JavaScript API
```javascript
// 显示模态框
const modal = new Modal('#exampleModal');
modal.show();

// 隐藏模态框
modal.hide();

// 事件监听
modal.on('show', () => {
    console.log('模态框显示');
});

modal.on('hide', () => {
    console.log('模态框隐藏');
});
```

### 2. 通知组件 (Notification)

#### 基本用法
```html
<div class="notification notification-success">
    <i class="fas fa-check-circle"></i>
    <span>操作成功</span>
    <button class="notification-close">
        <i class="fas fa-times"></i>
    </button>
</div>
```

#### 通知类型
```html
<div class="notification notification-info">
    <i class="fas fa-info-circle"></i>
    <span>信息提示</span>
</div>

<div class="notification notification-success">
    <i class="fas fa-check-circle"></i>
    <span>成功提示</span>
</div>

<div class="notification notification-warning">
    <i class="fas fa-exclamation-triangle"></i>
    <span>警告提示</span>
</div>

<div class="notification notification-error">
    <i class="fas fa-exclamation-circle"></i>
    <span>错误提示</span>
</div>
```

#### JavaScript API
```javascript
// 显示通知
Notification.show('操作成功', 'success');
Notification.show('操作失败', 'error');
Notification.show('警告信息', 'warning');
Notification.show('提示信息', 'info');

// 配置选项
Notification.show('自定义通知', 'info', {
    duration: 5000, // 显示时长
    closable: true, // 是否可关闭
    position: 'top-right' // 显示位置
});
```

### 3. 下拉菜单组件 (Dropdown)

#### 基本用法
```html
<div class="dropdown">
    <button class="btn btn-outline dropdown-toggle">
        下拉菜单
        <i class="fas fa-chevron-down"></i>
    </button>
    <div class="dropdown-menu">
        <a href="#" class="dropdown-item">选项1</a>
        <a href="#" class="dropdown-item">选项2</a>
        <div class="dropdown-divider"></div>
        <a href="#" class="dropdown-item">选项3</a>
    </div>
</div>
```

#### 下拉菜单位置
```html
<!-- 向下展开 -->
<div class="dropdown dropdown-down">
    <!-- 菜单内容 -->
</div>

<!-- 向上展开 -->
<div class="dropdown dropdown-up">
    <!-- 菜单内容 -->
</div>

<!-- 向左展开 -->
<div class="dropdown dropdown-left">
    <!-- 菜单内容 -->
</div>

<!-- 向右展开 -->
<div class="dropdown dropdown-right">
    <!-- 菜单内容 -->
</div>
```

### 4. 标签页组件 (Tabs)

#### 基本用法
```html
<div class="tabs">
    <div class="tab-list">
        <button class="tab-item active" data-tab="tab1">标签1</button>
        <button class="tab-item" data-tab="tab2">标签2</button>
        <button class="tab-item" data-tab="tab3">标签3</button>
    </div>
    <div class="tab-content">
        <div class="tab-pane active" id="tab1">
            <p>标签1内容</p>
        </div>
        <div class="tab-pane" id="tab2">
            <p>标签2内容</p>
        </div>
        <div class="tab-pane" id="tab3">
            <p>标签3内容</p>
        </div>
    </div>
</div>
```

#### JavaScript API
```javascript
// 初始化标签页
const tabs = new Tabs('.tabs');

// 切换到指定标签
tabs.show('tab2');

// 事件监听
tabs.on('change', (activeTab) => {
    console.log('切换到标签:', activeTab);
});
```

## 业务组件

### 1. 学生卡片组件

```html
<div class="student-card">
    <div class="student-card-header">
        <div class="student-avatar">张</div>
        <div class="student-info">
            <div class="student-name">张三</div>
            <div class="student-id">S001</div>
        </div>
        <span class="student-status excellent">优秀</span>
    </div>
    <div class="student-metrics">
        <div class="metric-item">
            <div class="metric-value">85.5</div>
            <div class="metric-label">平均分</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">5</div>
            <div class="metric-label">班级排名</div>
        </div>
    </div>
</div>
```

### 2. 成绩统计卡片

```html
<div class="stat-card">
    <div class="stat-icon">
        <i class="fas fa-users"></i>
    </div>
    <div class="stat-content">
        <div class="stat-value">45</div>
        <div class="stat-label">学生总数</div>
    </div>
</div>
```

### 3. 课程进度组件

```html
<div class="progress-card">
    <div class="progress-header">
        <h4>数学课程</h4>
        <span class="progress-percentage">75%</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill" style="width: 75%"></div>
    </div>
    <div class="progress-info">
        <span>已完成 15/20 章节</span>
    </div>
</div>
```

### 4. AI分析结果组件

```html
<div class="ai-insight">
    <div class="insight-header">
        <i class="fas fa-robot"></i>
        <h4>AI分析结果</h4>
    </div>
    <div class="insight-content">
        <p>根据学生表现分析，建议加强基础知识训练。</p>
    </div>
    <div class="insight-actions">
        <button class="btn btn-sm btn-outline">查看详情</button>
        <button class="btn btn-sm btn-primary">采纳建议</button>
    </div>
</div>
```

## 工具组件

### 1. 加载组件 (Loading)

#### 基本用法
```html
<div class="loading">
    <div class="loading-spinner"></div>
    <span>加载中...</span>
</div>
```

#### 加载变体
```html
<!-- 圆形加载器 -->
<div class="loading loading-circle">
    <div class="loading-spinner"></div>
</div>

<!-- 点状加载器 -->
<div class="loading loading-dots">
    <div class="loading-dot"></div>
    <div class="loading-dot"></div>
    <div class="loading-dot"></div>
</div>

<!-- 条形加载器 -->
<div class="loading loading-bar">
    <div class="loading-progress"></div>
</div>
```

### 2. 进度条组件 (Progress)

#### 基本用法
```html
<div class="progress">
    <div class="progress-bar" style="width: 60%"></div>
</div>
```

#### 进度条变体
```html
<!-- 带标签的进度条 -->
<div class="progress progress-labeled">
    <div class="progress-bar" style="width: 60%">
        <span class="progress-label">60%</span>
    </div>
</div>

<!-- 彩色进度条 -->
<div class="progress">
    <div class="progress-bar progress-bar-success" style="width: 40%"></div>
    <div class="progress-bar progress-bar-warning" style="width: 20%"></div>
    <div class="progress-bar progress-bar-error" style="width: 10%"></div>
</div>

<!-- 条纹进度条 -->
<div class="progress">
    <div class="progress-bar progress-bar-striped" style="width: 60%"></div>
</div>
```

### 3. 徽章组件 (Badge)

#### 基本用法
```html
<span class="badge">默认</span>
<span class="badge badge-primary">主要</span>
<span class="badge badge-success">成功</span>
<span class="badge badge-warning">警告</span>
<span class="badge badge-error">错误</span>
```

#### 徽章变体
```html
<!-- 圆形徽章 -->
<span class="badge badge-circle">5</span>

<!-- 点状徽章 -->
<span class="badge badge-dot"></span>

<!-- 大徽章 -->
<span class="badge badge-lg">大徽章</span>

<!-- 小徽章 -->
<span class="badge badge-sm">小徽章</span>
```

### 4. 工具提示组件 (Tooltip)

#### 基本用法
```html
<button class="btn btn-primary tooltip" data-tooltip="这是一个提示信息">
    悬停查看提示
</button>
```

#### 提示位置
```html
<button class="tooltip tooltip-top" data-tooltip="顶部提示">顶部</button>
<button class="tooltip tooltip-right" data-tooltip="右侧提示">右侧</button>
<button class="tooltip tooltip-bottom" data-tooltip="底部提示">底部</button>
<button class="tooltip tooltip-left" data-tooltip="左侧提示">左侧</button>
```

## 布局组件

### 1. 网格系统

#### 基本网格
```html
<div class="container">
    <div class="row">
        <div class="col-12 col-md-6 col-lg-4">
            <div class="card">
                <div class="card-body">列1</div>
            </div>
        </div>
        <div class="col-12 col-md-6 col-lg-4">
            <div class="card">
                <div class="card-body">列2</div>
            </div>
        </div>
        <div class="col-12 col-md-12 col-lg-4">
            <div class="card">
                <div class="card-body">列3</div>
            </div>
        </div>
    </div>
</div>
```

#### 响应式网格
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="card">
        <div class="card-body">网格项1</div>
    </div>
    <div class="card">
        <div class="card-body">网格项2</div>
    </div>
    <div class="card">
        <div class="card-body">网格项3</div>
    </div>
</div>
```

### 2. 弹性布局

#### 基本弹性布局
```html
<div class="flex flex-wrap gap-4">
    <div class="flex-1">
        <div class="card">
            <div class="card-body">弹性项1</div>
        </div>
    </div>
    <div class="flex-1">
        <div class="card">
            <div class="card-body">弹性项2</div>
        </div>
    </div>
</div>
```

#### 对齐方式
```html
<!-- 水平居中 -->
<div class="flex justify-center">
    <div class="card">居中内容</div>
</div>

<!-- 垂直居中 -->
<div class="flex items-center h-64">
    <div class="card">垂直居中</div>
</div>

<!-- 两端对齐 -->
<div class="flex justify-between">
    <div class="card">左侧</div>
    <div class="card">右侧</div>
</div>
```

## 主题定制

### 1. CSS变量覆盖

```css
:root {
    /* 主色调定制 */
    --primary-50: #eff6ff;
    --primary-500: #3b82f6;
    --primary-600: #2563eb;
    
    /* 字体定制 */
    --font-family-base: 'Custom Font', sans-serif;
    --font-size-base: 16px;
    
    /* 间距定制 */
    --spacing-unit: 8px;
    
    /* 圆角定制 */
    --radius-base: 6px;
}
```

### 2. 深色模式

```css
[data-theme="dark"] {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --text-primary: #ffffff;
    --text-secondary: #a0a0a0;
    --border-light: #404040;
}
```

### 3. 高对比度模式

```css
[data-theme="high-contrast"] {
    --primary-500: #0000ff;
    --text-primary: #000000;
    --bg-primary: #ffffff;
    --border-light: #000000;
}
```

## 最佳实践

### 1. 组件使用规范

- **语义化HTML**: 使用正确的HTML标签和ARIA属性
- **类名规范**: 遵循BEM命名规范，保持一致性
- **响应式设计**: 优先考虑移动端体验
- **性能优化**: 避免不必要的DOM操作和样式重绘

### 2. 可访问性指南

- **键盘导航**: 确保所有交互元素可通过键盘访问
- **屏幕阅读器**: 提供适当的ARIA标签和描述
- **颜色对比**: 确保文本和背景有足够的对比度
- **焦点指示**: 为焦点状态提供清晰的视觉指示

### 3. 性能优化建议

- **按需加载**: 只加载当前页面需要的组件
- **CSS优化**: 使用CSS变量减少重复代码
- **JavaScript优化**: 避免全局污染，使用模块化开发
- **图片优化**: 使用SVG图标，支持高分辨率显示

### 4. 浏览器兼容性

- **现代浏览器**: 支持Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **移动端**: 支持iOS Safari 13+, Android Chrome 80+
- **降级方案**: 为不支持的特性提供合理的降级方案

## 更新日志

### v2.0.0 (2024-01-20)
- 🎉 初始版本发布
- ✨ 完整的组件库实现
- 🎨 统一的设计系统
- 📱 响应式布局支持
- ♿ 无障碍访问优化

### 未来规划

- 🔄 组件动画效果增强
- 🎨 更多主题选项
- 📊 数据可视化组件
- 🚀 性能进一步优化
- 📖 更详细的文档和示例

---

## 技术支持

如有问题或建议，请联系开发团队或提交Issue。我们致力于为智能教学助手提供最优质的UI组件库。