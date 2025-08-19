# 智能教学助手2.0 - 图标库使用指南

## 概述

本图标库为智能教学助手2.0提供了完整的SVG图标集，包含导航、功能、状态和教育专用图标，所有图标均采用SVG格式，支持无损缩放和主题色彩定制。

## 图标分类

### 1. 导航图标 (navigation-icons.svg)
- 工作台、备课助手、课堂助手、成绩管理、数据分析、个人中心
- 设置、通知、搜索、菜单、关闭、返回、更多、帮助、退出

### 2. 功能图标 (function-icons.svg)
- 基础操作：添加、编辑、删除、保存、下载、上传
- 文档操作：导出、导入、打印、分享、复制、粘贴
- 界面控制：刷新、筛选、排序、视图、隐藏、全屏
- 媒体控制：播放、暂停、停止、录制、麦克风、摄像头

### 3. 状态图标 (status-icons.svg)
- 反馈状态：成功、错误、警告、信息、加载
- 用户状态：在线、离线、忙碌、空闲
- 交互元素：星级评分、收藏、书签、点赞、评论、标签
- 通用符号：时钟、日历、位置、邮件、电话、链接、锁定

### 4. 教育图标 (education-icons.svg)
- 学科图标：数学、语文、英语、物理、化学、生物、历史、地理、音乐、美术、体育、计算机
- 教学工具：黑板、书本、笔记本、铅笔、橡皮擦、尺子、计算器
- 科学仪器：地球仪、显微镜、试管
- 成就奖励：奖杯、证书、毕业帽

## 使用方法

### 1. HTML中使用

首先在HTML页面中引入图标库：

```html
<!-- 引入所有图标库 -->
<link rel="preload" href="assets/icons/navigation-icons.svg" as="image">
<link rel="preload" href="assets/icons/function-icons.svg" as="image">
<link rel="preload" href="assets/icons/status-icons.svg" as="image">
<link rel="preload" href="assets/icons/education-icons.svg" as="image">

<!-- 或者直接嵌入SVG -->
<div style="display: none;">
  <!-- 这里可以直接粘贴SVG内容 -->
</div>
```

然后使用图标：

```html
<!-- 基础用法 -->
<svg class="icon">
  <use href="#icon-dashboard"></use>
</svg>

<!-- 带样式的图标 -->
<svg class="icon icon-large icon-primary">
  <use href="#icon-lesson-prep"></use>
</svg>

<!-- 按钮中的图标 -->
<button class="btn btn-primary">
  <svg class="icon icon-small">
    <use href="#icon-add"></use>
  </svg>
  添加课件
</button>
```

### 2. CSS样式定义

```css
/* 基础图标样式 */
.icon {
  width: 24px;
  height: 24px;
  fill: currentColor;
  display: inline-block;
  vertical-align: middle;
}

/* 图标尺寸变体 */
.icon-small {
  width: 16px;
  height: 16px;
}

.icon-large {
  width: 32px;
  height: 32px;
}

.icon-xlarge {
  width: 48px;
  height: 48px;
}

/* 图标颜色变体 */
.icon-primary {
  color: #1890ff;
}

.icon-success {
  color: #52c41a;
}

.icon-warning {
  color: #faad14;
}

.icon-error {
  color: #ff4d4f;
}

.icon-muted {
  color: #8c8c8c;
}

/* 图标动画效果 */
.icon-spin {
  animation: icon-spin 1s linear infinite;
}

@keyframes icon-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.icon-pulse {
  animation: icon-pulse 1.5s ease-in-out infinite;
}

@keyframes icon-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

### 3. JavaScript中动态使用

```javascript
// 创建图标元素
function createIcon(iconId, className = '') {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
  
  svg.classList.add('icon');
  if (className) {
    svg.classList.add(...className.split(' '));
  }
  
  use.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#${iconId}`);
  svg.appendChild(use);
  
  return svg;
}

// 使用示例
const dashboardIcon = createIcon('icon-dashboard', 'icon-large icon-primary');
document.getElementById('nav-dashboard').appendChild(dashboardIcon);

// 批量设置导航图标
const navItems = [
  { id: 'nav-dashboard', icon: 'icon-dashboard' },
  { id: 'nav-lesson-prep', icon: 'icon-lesson-prep' },
  { id: 'nav-classroom', icon: 'icon-classroom' },
  { id: 'nav-grades', icon: 'icon-grades' },
  { id: 'nav-analytics', icon: 'icon-analytics' },
  { id: 'nav-profile', icon: 'icon-profile' }
];

navItems.forEach(item => {
  const element = document.getElementById(item.id);
  if (element) {
    const icon = createIcon(item.icon);
    element.insertBefore(icon, element.firstChild);
  }
});
```

## 图标命名规范

所有图标均采用统一的命名规范：

- 前缀：`icon-`
- 命名：使用小写字母和连字符
- 分类：按功能和用途分组

### 命名示例

```
导航类：icon-dashboard, icon-lesson-prep, icon-classroom
操作类：icon-add, icon-edit, icon-delete, icon-save
状态类：icon-success, icon-error, icon-warning, icon-loading
学科类：icon-math, icon-chinese, icon-english, icon-physics
```

## 自定义和扩展

### 1. 添加新图标

在相应的SVG文件中添加新的`<symbol>`元素：

```svg
<symbol id="icon-new-feature" viewBox="0 0 24 24">
  <path fill="currentColor" d="...SVG路径数据..."/>
</symbol>
```

### 2. 修改现有图标

直接编辑对应的`<path>`元素的`d`属性，或添加新的图形元素。

### 3. 主题定制

通过CSS变量实现主题切换：

```css
:root {
  --icon-color-primary: #1890ff;
  --icon-color-success: #52c41a;
  --icon-color-warning: #faad14;
  --icon-color-error: #ff4d4f;
}

[data-theme="dark"] {
  --icon-color-primary: #177ddc;
  --icon-color-success: #49aa19;
  --icon-color-warning: #d89614;
  --icon-color-error: #d32029;
}

.icon-primary {
  color: var(--icon-color-primary);
}
```

## 性能优化建议

### 1. 预加载关键图标

```html
<link rel="preload" href="assets/icons/navigation-icons.svg" as="image">
```

### 2. 按需加载

```javascript
// 动态加载图标库
async function loadIconLibrary(library) {
  const response = await fetch(`assets/icons/${library}.svg`);
  const svgText = await response.text();
  
  // 将SVG内容插入到页面中
  const div = document.createElement('div');
  div.style.display = 'none';
  div.innerHTML = svgText;
  document.body.appendChild(div);
}

// 使用
loadIconLibrary('navigation-icons');
```

### 3. 图标缓存

利用浏览器缓存和Service Worker缓存图标资源。

## 无障碍访问

### 1. 添加语义化标签

```html
<svg class="icon" aria-label="工作台" role="img">
  <use href="#icon-dashboard"></use>
</svg>

<!-- 装饰性图标 -->
<svg class="icon" aria-hidden="true">
  <use href="#icon-decoration"></use>
</svg>
```

### 2. 提供文字替代

```html
<button>
  <svg class="icon" aria-hidden="true">
    <use href="#icon-add"></use>
  </svg>
  <span>添加课件</span>
</button>
```

## 浏览器兼容性

- 现代浏览器：完全支持
- IE 11：需要SVG polyfill
- 移动端：完全支持

### IE 11 兼容性处理

```javascript
// 检测是否需要polyfill
if (!document.createElementNS('http://www.w3.org/2000/svg', 'svg').createSVGRect) {
  // 加载SVG polyfill
  loadScript('https://cdn.jsdelivr.net/npm/svg4everybody@2.1.9/dist/svg4everybody.min.js');
}
```

## 更新日志

### v2.0.0 (2024-01-20)
- 初始版本发布
- 包含4个图标库，共100+图标
- 支持主题定制和响应式设计
- 完整的使用文档和示例

---

如有问题或建议，请联系开发团队。