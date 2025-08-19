# 智能教学助手 2.0 设计系统

## 概述

智能教学助手 2.0 设计系统是一套完整的设计规范和组件库，旨在为教育科技产品提供一致、专业、易用的用户体验。本设计系统基于现代 UI/UX 设计原则，结合教育行业的特殊需求，确保产品在不同平台和设备上的视觉一致性和交互体验。

## 设计原则

### 1. 教育优先 (Education First)
- 以教学效果为核心，优化师生交互体验
- 符合教育场景的认知习惯和操作流程
- 支持不同年龄段用户的视觉和操作需求

### 2. 智能友好 (AI Friendly)
- 清晰展示 AI 功能和智能推荐
- 提供直观的数据可视化和分析结果
- 保持人机交互的自然和高效

### 3. 简洁专业 (Simple & Professional)
- 减少视觉干扰，突出核心功能
- 使用专业的教育行业色彩和图标
- 保持界面的整洁和层次分明

### 4. 响应适配 (Responsive & Adaptive)
- 支持多设备、多屏幕尺寸
- 优化移动端和桌面端的交互体验
- 考虑无障碍访问和包容性设计

## 色彩系统 (Color System)

### 主色调 (Primary Colors)

```css
/* 主蓝色 - 代表智能和科技 */
--primary-50: #E3F2FD;
--primary-100: #BBDEFB;
--primary-200: #90CAF9;
--primary-300: #64B5F6;
--primary-400: #42A5F5;
--primary-500: #2196F3;  /* 主色 */
--primary-600: #1E88E5;
--primary-700: #1976D2;
--primary-800: #1565C0;
--primary-900: #0D47A1;
```

### 辅助色调 (Secondary Colors)

```css
/* 绿色 - 代表成功和成长 */
--success-50: #E8F5E8;
--success-100: #C8E6C9;
--success-200: #A5D6A7;
--success-300: #81C784;
--success-400: #66BB6A;
--success-500: #4CAF50;  /* 成功色 */
--success-600: #43A047;
--success-700: #388E3C;
--success-800: #2E7D32;
--success-900: #1B5E20;

/* 橙色 - 代表警告和提醒 */
--warning-50: #FFF8E1;
--warning-100: #FFECB3;
--warning-200: #FFE082;
--warning-300: #FFD54F;
--warning-400: #FFCA28;
--warning-500: #FFC107;  /* 警告色 */
--warning-600: #FFB300;
--warning-700: #FFA000;
--warning-800: #FF8F00;
--warning-900: #FF6F00;

/* 红色 - 代表错误和危险 */
--error-50: #FFEBEE;
--error-100: #FFCDD2;
--error-200: #EF9A9A;
--error-300: #E57373;
--error-400: #EF5350;
--error-500: #F44336;  /* 错误色 */
--error-600: #E53935;
--error-700: #D32F2F;
--error-800: #C62828;
--error-900: #B71C1C;
```

### 中性色调 (Neutral Colors)

```css
/* 灰色系 - 用于文本、边框、背景 */
--neutral-50: #FAFAFA;
--neutral-100: #F5F5F5;
--neutral-200: #EEEEEE;
--neutral-300: #E0E0E0;
--neutral-400: #BDBDBD;
--neutral-500: #9E9E9E;
--neutral-600: #757575;
--neutral-700: #616161;
--neutral-800: #424242;
--neutral-900: #212121;

/* 语义化颜色 */
--text-primary: #212121;
--text-secondary: #757575;
--text-disabled: #BDBDBD;
--text-hint: #9E9E9E;

--background-default: #FFFFFF;
--background-paper: #FAFAFA;
--background-level1: #F5F5F5;
--background-level2: #EEEEEE;

--border-light: #E0E0E0;
--border-medium: #BDBDBD;
--border-dark: #757575;
```

### 教育专用色彩 (Education Specific Colors)

```css
/* 学科色彩 */
--subject-math: #2196F3;      /* 数学 - 蓝色 */
--subject-chinese: #F44336;   /* 语文 - 红色 */
--subject-english: #4CAF50;   /* 英语 - 绿色 */
--subject-physics: #9C27B0;   /* 物理 - 紫色 */
--subject-chemistry: #FF9800; /* 化学 - 橙色 */
--subject-biology: #8BC34A;   /* 生物 - 浅绿 */
--subject-history: #795548;   /* 历史 - 棕色 */
--subject-geography: #00BCD4; /* 地理 - 青色 */

/* 成绩等级色彩 */
--grade-excellent: #4CAF50;   /* 优秀 */
--grade-good: #8BC34A;        /* 良好 */
--grade-average: #FFC107;     /* 中等 */
--grade-poor: #FF9800;        /* 较差 */
--grade-fail: #F44336;        /* 不及格 */
```

## 字体系统 (Typography)

### 字体族 (Font Family)

```css
/* 主字体 - 适用于中英文混排 */
--font-family-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
                       'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', 
                       Arial, sans-serif;

/* 等宽字体 - 适用于代码和数据 */
--font-family-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', 
                    Consolas, 'Courier New', monospace;

/* 数字字体 - 适用于数据展示 */
--font-family-numeric: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 
                       'Segoe UI', Roboto, sans-serif;
```

### 字体大小 (Font Size)

```css
/* 标题字体 */
--font-size-h1: 32px;   /* 主标题 */
--font-size-h2: 28px;   /* 二级标题 */
--font-size-h3: 24px;   /* 三级标题 */
--font-size-h4: 20px;   /* 四级标题 */
--font-size-h5: 18px;   /* 五级标题 */
--font-size-h6: 16px;   /* 六级标题 */

/* 正文字体 */
--font-size-body-large: 16px;   /* 大号正文 */
--font-size-body: 14px;         /* 标准正文 */
--font-size-body-small: 12px;   /* 小号正文 */

/* 辅助字体 */
--font-size-caption: 12px;      /* 说明文字 */
--font-size-overline: 10px;     /* 上标文字 */
--font-size-button: 14px;       /* 按钮文字 */
```

### 字体重量 (Font Weight)

```css
--font-weight-light: 300;
--font-weight-regular: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
--font-weight-extrabold: 800;
```

### 行高 (Line Height)

```css
--line-height-tight: 1.2;
--line-height-normal: 1.4;
--line-height-relaxed: 1.6;
--line-height-loose: 1.8;
```

## 间距系统 (Spacing System)

### 基础间距 (Base Spacing)

```css
/* 8px 基础网格系统 */
--spacing-0: 0px;
--spacing-1: 4px;    /* 0.5 * 8px */
--spacing-2: 8px;    /* 1 * 8px */
--spacing-3: 12px;   /* 1.5 * 8px */
--spacing-4: 16px;   /* 2 * 8px */
--spacing-5: 20px;   /* 2.5 * 8px */
--spacing-6: 24px;   /* 3 * 8px */
--spacing-8: 32px;   /* 4 * 8px */
--spacing-10: 40px;  /* 5 * 8px */
--spacing-12: 48px;  /* 6 * 8px */
--spacing-16: 64px;  /* 8 * 8px */
--spacing-20: 80px;  /* 10 * 8px */
--spacing-24: 96px;  /* 12 * 8px */
```

### 语义化间距 (Semantic Spacing)

```css
/* 组件内间距 */
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-2xl: 48px;

/* 布局间距 */
--layout-gutter: 16px;      /* 栅格间距 */
--layout-margin: 24px;      /* 页面边距 */
--layout-section: 48px;     /* 区块间距 */
```

## 圆角系统 (Border Radius)

```css
--radius-none: 0px;
--radius-sm: 4px;     /* 小圆角 */
--radius-md: 8px;     /* 中等圆角 */
--radius-lg: 12px;    /* 大圆角 */
--radius-xl: 16px;    /* 超大圆角 */
--radius-full: 9999px; /* 完全圆角 */

/* 组件专用圆角 */
--radius-button: 8px;
--radius-card: 12px;
--radius-modal: 16px;
--radius-input: 6px;
```

## 阴影系统 (Shadow System)

```css
/* 层级阴影 */
--shadow-none: none;
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* 组件专用阴影 */
--shadow-card: 0 2px 8px rgba(0, 0, 0, 0.1);
--shadow-modal: 0 20px 40px rgba(0, 0, 0, 0.15);
--shadow-dropdown: 0 4px 12px rgba(0, 0, 0, 0.15);
--shadow-button: 0 2px 4px rgba(0, 0, 0, 0.1);
```

## 动画系统 (Animation System)

### 缓动函数 (Easing Functions)

```css
--ease-linear: cubic-bezier(0, 0, 1, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-back: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 动画时长 (Duration)

```css
--duration-fast: 150ms;
--duration-normal: 250ms;
--duration-slow: 350ms;
--duration-slower: 500ms;
```

### 常用动画 (Common Animations)

```css
/* 淡入淡出 */
.fade-in {
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

.fade-out {
  animation: fadeOut var(--duration-normal) var(--ease-in);
}

/* 滑动 */
.slide-up {
  animation: slideUp var(--duration-normal) var(--ease-out);
}

.slide-down {
  animation: slideDown var(--duration-normal) var(--ease-out);
}

/* 缩放 */
.scale-in {
  animation: scaleIn var(--duration-normal) var(--ease-back);
}

.scale-out {
  animation: scaleOut var(--duration-fast) var(--ease-in);
}
```

## 响应式断点 (Breakpoints)

```css
/* 移动设备优先的响应式设计 */
--breakpoint-xs: 0px;      /* 超小屏幕 */
--breakpoint-sm: 576px;    /* 小屏幕 */
--breakpoint-md: 768px;    /* 中等屏幕 */
--breakpoint-lg: 992px;    /* 大屏幕 */
--breakpoint-xl: 1200px;   /* 超大屏幕 */
--breakpoint-2xl: 1400px;  /* 超超大屏幕 */

/* 媒体查询 */
@media (min-width: 576px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 992px) { /* lg */ }
@media (min-width: 1200px) { /* xl */ }
@media (min-width: 1400px) { /* 2xl */ }
```

## 组件规范

### 按钮 (Button)

```css
/* 按钮尺寸 */
.btn-sm { height: 32px; padding: 0 12px; font-size: 12px; }
.btn-md { height: 40px; padding: 0 16px; font-size: 14px; }
.btn-lg { height: 48px; padding: 0 24px; font-size: 16px; }

/* 按钮类型 */
.btn-primary { background: var(--primary-500); color: white; }
.btn-secondary { background: var(--neutral-100); color: var(--text-primary); }
.btn-success { background: var(--success-500); color: white; }
.btn-warning { background: var(--warning-500); color: white; }
.btn-error { background: var(--error-500); color: white; }
```

### 输入框 (Input)

```css
.input {
  height: 40px;
  padding: 0 12px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-input);
  font-size: 14px;
  transition: border-color var(--duration-fast) var(--ease-out);
}

.input:focus {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}
```

### 卡片 (Card)

```css
.card {
  background: var(--background-default);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  padding: var(--spacing-6);
  transition: box-shadow var(--duration-normal) var(--ease-out);
}

.card:hover {
  box-shadow: var(--shadow-lg);
}
```

## 图标规范

### 图标尺寸

```css
--icon-xs: 12px;
--icon-sm: 16px;
--icon-md: 20px;
--icon-lg: 24px;
--icon-xl: 32px;
--icon-2xl: 48px;
```

### 图标使用原则

1. **一致性**: 同一功能使用相同图标
2. **识别性**: 图标含义清晰，符合用户认知
3. **适配性**: 支持不同尺寸和主题
4. **无障碍**: 提供替代文本和语义化标签

## 无障碍设计 (Accessibility)

### 颜色对比度

- 正文文字对比度不低于 4.5:1
- 大号文字对比度不低于 3:1
- 非文字元素对比度不低于 3:1

### 焦点管理

```css
/* 焦点样式 */
.focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* 跳过链接 */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary-500);
  color: white;
  padding: 8px;
  text-decoration: none;
  transition: top var(--duration-fast);
}

.skip-link:focus {
  top: 6px;
}
```

### 语义化标记

- 使用正确的 HTML 语义标签
- 提供 ARIA 标签和属性
- 确保键盘导航的可用性
- 支持屏幕阅读器

## 暗色模式 (Dark Mode)

```css
/* 暗色模式色彩变量 */
@media (prefers-color-scheme: dark) {
  :root {
    --text-primary: #FFFFFF;
    --text-secondary: #AAAAAA;
    --text-disabled: #666666;
    
    --background-default: #121212;
    --background-paper: #1E1E1E;
    --background-level1: #2D2D2D;
    --background-level2: #3D3D3D;
    
    --border-light: #3D3D3D;
    --border-medium: #555555;
    --border-dark: #777777;
  }
}
```

## 使用指南

### 开发者使用

1. **引入设计系统**: 在项目中引入 CSS 变量和基础样式
2. **使用组件**: 按照规范使用预定义的组件类
3. **自定义扩展**: 基于设计系统进行功能扩展
4. **保持一致**: 遵循设计原则和规范

### 设计师使用

1. **设计文件**: 使用 Figma 设计系统文件
2. **组件库**: 复用预定义的设计组件
3. **规范检查**: 确保设计符合系统规范
4. **协作交付**: 与开发团队协作交付

## 更新日志

### v2.0.0 (2024-01)
- 建立完整的设计系统框架
- 定义教育行业专用色彩和组件
- 支持暗色模式和响应式设计
- 完善无障碍设计规范

---

**智能教学助手 2.0 设计系统** - 让教育科技产品更专业、更易用、更智能。