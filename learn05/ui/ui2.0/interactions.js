/* 智能教学助手2.0 - 交互原型控制器 */

/**
 * 交互原型管理器
 * 负责管理所有动画效果、交互反馈和用户体验优化
 */
class InteractionManager {
  constructor() {
    this.animations = new Map();
    this.observers = new Map();
    this.preferences = this.loadUserPreferences();
    this.init();
  }

  /**
   * 初始化交互管理器
   */
  init() {
    this.setupAnimationObserver();
    this.setupReducedMotionSupport();
    this.setupTouchSupport();
    this.setupKeyboardSupport();
    this.setupPerformanceMonitoring();
    this.bindGlobalEvents();
  }

  /**
   * 设置动画观察器
   */
  setupAnimationObserver() {
    // 交叉观察器用于懒加载动画
    this.intersectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.triggerEnterAnimation(entry.target);
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: '50px'
      }
    );

    // 观察所有需要动画的元素
    document.querySelectorAll('[data-animate-on-scroll]').forEach(el => {
      this.intersectionObserver.observe(el);
    });
  }

  /**
   * 设置减少动画偏好支持
   */
  setupReducedMotionSupport() {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    const handleMotionPreference = (e) => {
      document.documentElement.setAttribute(
        'data-reduced-motion', 
        e.matches ? 'true' : 'false'
      );
      
      if (e.matches) {
        this.disableAnimations();
      } else {
        this.enableAnimations();
      }
    };

    mediaQuery.addListener(handleMotionPreference);
    handleMotionPreference(mediaQuery);
  }

  /**
   * 设置触摸支持
   */
  setupTouchSupport() {
    // 检测触摸设备
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    document.documentElement.setAttribute('data-touch-device', isTouchDevice);

    if (isTouchDevice) {
      this.setupTouchGestures();
    }
  }

  /**
   * 设置触摸手势
   */
  setupTouchGestures() {
    let startX, startY, startTime;

    document.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      startTime = Date.now();
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
      if (!startX || !startY) return;

      const endX = e.changedTouches[0].clientX;
      const endY = e.changedTouches[0].clientY;
      const endTime = Date.now();

      const deltaX = endX - startX;
      const deltaY = endY - startY;
      const deltaTime = endTime - startTime;

      // 检测滑动手势
      if (Math.abs(deltaX) > 50 && deltaTime < 300) {
        const direction = deltaX > 0 ? 'right' : 'left';
        this.handleSwipeGesture(e.target, direction, deltaX);
      }

      // 检测长按手势
      if (deltaTime > 500 && Math.abs(deltaX) < 10 && Math.abs(deltaY) < 10) {
        this.handleLongPress(e.target);
      }

      startX = startY = null;
    }, { passive: true });
  }

  /**
   * 设置键盘支持
   */
  setupKeyboardSupport() {
    document.addEventListener('keydown', (e) => {
      // 焦点管理
      if (e.key === 'Tab') {
        this.handleTabNavigation(e);
      }

      // 快捷键支持
      if (e.ctrlKey || e.metaKey) {
        this.handleKeyboardShortcuts(e);
      }

      // 方向键导航
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        this.handleArrowNavigation(e);
      }
    });
  }

  /**
   * 设置性能监控
   */
  setupPerformanceMonitoring() {
    // 监控动画性能
    this.performanceObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach(entry => {
        if (entry.duration > 16) { // 超过一帧的时间
          console.warn('Animation performance issue:', entry);
        }
      });
    });

    if ('observe' in this.performanceObserver) {
      this.performanceObserver.observe({ entryTypes: ['measure'] });
    }
  }

  /**
   * 绑定全局事件
   */
  bindGlobalEvents() {
    // 窗口大小变化
    window.addEventListener('resize', this.debounce(() => {
      this.handleResize();
    }, 250));

    // 页面可见性变化
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pauseAnimations();
      } else {
        this.resumeAnimations();
      }
    });

    // 动画事件监听
    document.addEventListener('animationstart', this.handleAnimationStart.bind(this));
    document.addEventListener('animationend', this.handleAnimationEnd.bind(this));
    document.addEventListener('transitionend', this.handleTransitionEnd.bind(this));
  }

  /**
   * 触发进入动画
   */
  triggerEnterAnimation(element) {
    const animationType = element.dataset.animateOnScroll || 'fade-in-up';
    const delay = element.dataset.animateDelay || 0;
    const duration = element.dataset.animateDuration || null;

    setTimeout(() => {
      this.addAnimation(element, animationType, duration);
    }, parseInt(delay));
  }

  /**
   * 添加动画
   */
  addAnimation(element, animationType, duration = null) {
    if (this.preferences.reducedMotion) {
      element.style.opacity = '1';
      element.style.transform = 'none';
      return;
    }

    // 记录动画开始时间用于性能监控
    performance.mark(`animation-start-${animationType}`);

    element.classList.add(`animate-${animationType}`);
    
    if (duration) {
      element.style.animationDuration = duration;
    }

    // 存储动画信息
    this.animations.set(element, {
      type: animationType,
      startTime: Date.now(),
      duration: duration
    });
  }

  /**
   * 移除动画
   */
  removeAnimation(element, animationType) {
    element.classList.remove(`animate-${animationType}`);
    this.animations.delete(element);
    
    // 性能监控
    performance.mark(`animation-end-${animationType}`);
    performance.measure(
      `animation-duration-${animationType}`,
      `animation-start-${animationType}`,
      `animation-end-${animationType}`
    );
  }

  /**
   * 创建波纹效果
   */
  createRippleEffect(element, event) {
    if (this.preferences.reducedMotion) return;

    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    const ripple = document.createElement('div');
    ripple.className = 'ripple';
    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s linear;
      pointer-events: none;
    `;

    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);

    setTimeout(() => {
      ripple.remove();
    }, 600);
  }

  /**
   * 创建加载动画
   */
  createLoadingAnimation(container, type = 'spinner') {
    const loadingEl = document.createElement('div');
    loadingEl.className = `loading-${type}`;
    
    switch (type) {
      case 'spinner':
        loadingEl.innerHTML = '<div class="loading-spinner"></div>';
        break;
      case 'dots':
        loadingEl.innerHTML = `
          <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
          </div>
        `;
        break;
      case 'progress':
        loadingEl.innerHTML = `
          <div class="loading-progress">
            <div class="progress-bar-indeterminate"></div>
          </div>
        `;
        break;
    }

    container.appendChild(loadingEl);
    return loadingEl;
  }

  /**
   * 移除加载动画
   */
  removeLoadingAnimation(loadingEl) {
    if (loadingEl && loadingEl.parentNode) {
      this.addAnimation(loadingEl, 'fade-out');
      setTimeout(() => {
        loadingEl.remove();
      }, 300);
    }
  }

  /**
   * 创建通知动画
   */
  showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <i class="notification-icon fas fa-${this.getNotificationIcon(type)}"></i>
        <span class="notification-message">${message}</span>
        <button class="notification-close" aria-label="关闭">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;

    // 添加到通知容器
    let container = document.querySelector('.notification-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'notification-container';
      document.body.appendChild(container);
    }

    container.appendChild(notification);

    // 进入动画
    this.addAnimation(notification, 'slide-in-right');

    // 关闭按钮事件
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
      this.hideNotification(notification);
    });

    // 自动关闭
    if (duration > 0) {
      setTimeout(() => {
        this.hideNotification(notification);
      }, duration);
    }

    return notification;
  }

  /**
   * 隐藏通知
   */
  hideNotification(notification) {
    this.addAnimation(notification, 'slide-out-right');
    setTimeout(() => {
      notification.remove();
    }, 300);
  }

  /**
   * 获取通知图标
   */
  getNotificationIcon(type) {
    const icons = {
      success: 'check-circle',
      error: 'exclamation-circle',
      warning: 'exclamation-triangle',
      info: 'info-circle'
    };
    return icons[type] || 'info-circle';
  }

  /**
   * 创建模态框动画
   */
  showModal(modalElement) {
    modalElement.style.display = 'flex';
    modalElement.classList.add('show');
    
    const backdrop = modalElement.querySelector('.modal-backdrop');
    const content = modalElement.querySelector('.modal-content');
    
    if (backdrop) {
      this.addAnimation(backdrop, 'fade-in');
    }
    
    if (content) {
      this.addAnimation(content, 'zoom-in-up');
    }

    // 焦点管理
    const firstFocusable = modalElement.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (firstFocusable) {
      firstFocusable.focus();
    }

    // 阻止背景滚动
    document.body.style.overflow = 'hidden';
  }

  /**
   * 隐藏模态框
   */
  hideModal(modalElement) {
    const backdrop = modalElement.querySelector('.modal-backdrop');
    const content = modalElement.querySelector('.modal-content');
    
    if (backdrop) {
      this.addAnimation(backdrop, 'fade-out');
    }
    
    if (content) {
      this.addAnimation(content, 'zoom-out');
    }

    setTimeout(() => {
      modalElement.classList.remove('show');
      modalElement.style.display = 'none';
      document.body.style.overflow = '';
    }, 300);
  }

  /**
   * 创建页面过渡动画
   */
  transitionToPage(fromPage, toPage, direction = 'forward') {
    const animations = {
      forward: {
        from: 'slide-out-left',
        to: 'slide-in-right'
      },
      backward: {
        from: 'slide-out-right',
        to: 'slide-in-left'
      },
      up: {
        from: 'slide-out-up',
        to: 'slide-in-down'
      },
      down: {
        from: 'slide-out-down',
        to: 'slide-in-up'
      }
    };

    const anim = animations[direction] || animations.forward;

    // 隐藏当前页面
    if (fromPage) {
      this.addAnimation(fromPage, anim.from);
      setTimeout(() => {
        fromPage.style.display = 'none';
      }, 300);
    }

    // 显示新页面
    if (toPage) {
      toPage.style.display = 'block';
      this.addAnimation(toPage, anim.to);
    }
  }

  /**
   * 创建数据更新动画
   */
  animateDataUpdate(element, newValue, oldValue = null) {
    if (this.preferences.reducedMotion) {
      element.textContent = newValue;
      return;
    }

    // 数值变化动画
    if (!isNaN(newValue) && !isNaN(oldValue)) {
      this.animateNumber(element, oldValue, newValue);
    } else {
      // 文本变化动画
      this.addAnimation(element, 'pulse');
      setTimeout(() => {
        element.textContent = newValue;
      }, 150);
    }
  }

  /**
   * 数字动画
   */
  animateNumber(element, from, to, duration = 1000) {
    const startTime = Date.now();
    const difference = to - from;

    const updateNumber = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // 使用缓动函数
      const easeProgress = this.easeOutCubic(progress);
      const currentValue = from + (difference * easeProgress);
      
      element.textContent = Math.round(currentValue);

      if (progress < 1) {
        requestAnimationFrame(updateNumber);
      }
    };

    requestAnimationFrame(updateNumber);
  }

  /**
   * 缓动函数
   */
  easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  /**
   * 处理滑动手势
   */
  handleSwipeGesture(target, direction, distance) {
    const swipeEvent = new CustomEvent('swipe', {
      detail: { direction, distance, target }
    });
    target.dispatchEvent(swipeEvent);

    // 添加视觉反馈
    if (target.classList.contains('swipeable')) {
      this.addAnimation(target, direction === 'left' ? 'slide-out-left' : 'slide-out-right');
    }
  }

  /**
   * 处理长按手势
   */
  handleLongPress(target) {
    const longPressEvent = new CustomEvent('longpress', {
      detail: { target }
    });
    target.dispatchEvent(longPressEvent);

    // 添加触觉反馈（如果支持）
    if ('vibrate' in navigator) {
      navigator.vibrate(50);
    }

    // 添加视觉反馈
    this.addAnimation(target, 'pulse');
  }

  /**
   * 处理Tab导航
   */
  handleTabNavigation(event) {
    const focusableElements = document.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    
    const currentIndex = Array.from(focusableElements).indexOf(document.activeElement);
    
    if (event.shiftKey) {
      // Shift+Tab - 向前导航
      if (currentIndex === 0) {
        event.preventDefault();
        focusableElements[focusableElements.length - 1].focus();
      }
    } else {
      // Tab - 向后导航
      if (currentIndex === focusableElements.length - 1) {
        event.preventDefault();
        focusableElements[0].focus();
      }
    }
  }

  /**
   * 处理键盘快捷键
   */
  handleKeyboardShortcuts(event) {
    const shortcuts = {
      'KeyS': () => this.saveData(),
      'KeyZ': () => this.undo(),
      'KeyY': () => this.redo(),
      'KeyF': () => this.openSearch(),
      'Escape': () => this.closeModal()
    };

    const action = shortcuts[event.code];
    if (action) {
      event.preventDefault();
      action();
    }
  }

  /**
   * 处理方向键导航
   */
  handleArrowNavigation(event) {
    const target = event.target;
    
    // 在网格布局中导航
    if (target.closest('.grid-navigation')) {
      this.handleGridNavigation(event, target);
    }
    
    // 在列表中导航
    if (target.closest('.list-navigation')) {
      this.handleListNavigation(event, target);
    }
  }

  /**
   * 处理网格导航
   */
  handleGridNavigation(event, target) {
    const grid = target.closest('.grid-navigation');
    const items = Array.from(grid.querySelectorAll('.grid-item'));
    const currentIndex = items.indexOf(target);
    const columns = parseInt(grid.dataset.columns) || 3;
    
    let newIndex;
    
    switch (event.key) {
      case 'ArrowLeft':
        newIndex = currentIndex - 1;
        break;
      case 'ArrowRight':
        newIndex = currentIndex + 1;
        break;
      case 'ArrowUp':
        newIndex = currentIndex - columns;
        break;
      case 'ArrowDown':
        newIndex = currentIndex + columns;
        break;
    }
    
    if (newIndex >= 0 && newIndex < items.length) {
      event.preventDefault();
      items[newIndex].focus();
    }
  }

  /**
   * 处理列表导航
   */
  handleListNavigation(event, target) {
    const list = target.closest('.list-navigation');
    const items = Array.from(list.querySelectorAll('.list-item'));
    const currentIndex = items.indexOf(target);
    
    let newIndex;
    
    switch (event.key) {
      case 'ArrowUp':
        newIndex = currentIndex - 1;
        break;
      case 'ArrowDown':
        newIndex = currentIndex + 1;
        break;
    }
    
    if (newIndex >= 0 && newIndex < items.length) {
      event.preventDefault();
      items[newIndex].focus();
    }
  }

  /**
   * 处理窗口大小变化
   */
  handleResize() {
    // 重新计算动画参数
    this.updateAnimationParameters();
    
    // 触发自定义事件
    const resizeEvent = new CustomEvent('responsiveResize', {
      detail: {
        width: window.innerWidth,
        height: window.innerHeight,
        isMobile: window.innerWidth < 768,
        isTablet: window.innerWidth >= 768 && window.innerWidth < 1024,
        isDesktop: window.innerWidth >= 1024
      }
    });
    window.dispatchEvent(resizeEvent);
  }

  /**
   * 更新动画参数
   */
  updateAnimationParameters() {
    const isMobile = window.innerWidth < 768;
    const root = document.documentElement;
    
    if (isMobile) {
      root.style.setProperty('--animation-fast', '0.1s');
      root.style.setProperty('--animation-base', '0.2s');
      root.style.setProperty('--animation-slow', '0.3s');
    } else {
      root.style.setProperty('--animation-fast', '0.15s');
      root.style.setProperty('--animation-base', '0.3s');
      root.style.setProperty('--animation-slow', '0.5s');
    }
  }

  /**
   * 处理动画开始事件
   */
  handleAnimationStart(event) {
    const element = event.target;
    element.classList.add('animating');
    
    // 触发自定义事件
    const customEvent = new CustomEvent('animationStart', {
      detail: { element, animationName: event.animationName }
    });
    element.dispatchEvent(customEvent);
  }

  /**
   * 处理动画结束事件
   */
  handleAnimationEnd(event) {
    const element = event.target;
    element.classList.remove('animating');
    
    // 清理动画类
    const animationClasses = Array.from(element.classList).filter(cls => 
      cls.startsWith('animate-')
    );
    animationClasses.forEach(cls => element.classList.remove(cls));
    
    // 清理will-change属性
    element.style.willChange = 'auto';
    
    // 触发自定义事件
    const customEvent = new CustomEvent('animationEnd', {
      detail: { element, animationName: event.animationName }
    });
    element.dispatchEvent(customEvent);
  }

  /**
   * 处理过渡结束事件
   */
  handleTransitionEnd(event) {
    const element = event.target;
    
    // 触发自定义事件
    const customEvent = new CustomEvent('transitionEnd', {
      detail: { element, propertyName: event.propertyName }
    });
    element.dispatchEvent(customEvent);
  }

  /**
   * 禁用动画
   */
  disableAnimations() {
    document.documentElement.classList.add('animations-disabled');
    this.preferences.reducedMotion = true;
  }

  /**
   * 启用动画
   */
  enableAnimations() {
    document.documentElement.classList.remove('animations-disabled');
    this.preferences.reducedMotion = false;
  }

  /**
   * 暂停动画
   */
  pauseAnimations() {
    document.querySelectorAll('.animating').forEach(el => {
      el.style.animationPlayState = 'paused';
    });
  }

  /**
   * 恢复动画
   */
  resumeAnimations() {
    document.querySelectorAll('.animating').forEach(el => {
      el.style.animationPlayState = 'running';
    });
  }

  /**
   * 加载用户偏好
   */
  loadUserPreferences() {
    const defaults = {
      reducedMotion: false,
      animationSpeed: 'normal',
      enableSounds: false,
      enableVibration: true
    };

    try {
      const saved = localStorage.getItem('interaction-preferences');
      return saved ? { ...defaults, ...JSON.parse(saved) } : defaults;
    } catch {
      return defaults;
    }
  }

  /**
   * 保存用户偏好
   */
  saveUserPreferences() {
    try {
      localStorage.setItem('interaction-preferences', JSON.stringify(this.preferences));
    } catch (error) {
      console.warn('无法保存用户偏好设置:', error);
    }
  }

  /**
   * 工具函数：防抖
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /**
   * 工具函数：节流
   */
  throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  /**
   * 销毁管理器
   */
  destroy() {
    // 清理观察器
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
    }
    
    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
    }

    // 清理动画
    this.animations.clear();
    this.observers.clear();

    // 保存用户偏好
    this.saveUserPreferences();
  }
}

/**
 * 教育场景专用交互效果
 */
class EducationInteractions {
  constructor(interactionManager) {
    this.manager = interactionManager;
    this.init();
  }

  init() {
    this.setupScoreAnimations();
    this.setupProgressAnimations();
    this.setupAIFeedbackAnimations();
    this.setupGamificationEffects();
  }

  /**
   * 设置成绩动画
   */
  setupScoreAnimations() {
    document.addEventListener('scoreUpdate', (event) => {
      const { element, newScore, oldScore } = event.detail;
      
      if (newScore > oldScore) {
        this.manager.addAnimation(element, 'score-increase');
        this.showScoreImprovement(element, newScore - oldScore);
      } else if (newScore < oldScore) {
        this.manager.addAnimation(element, 'score-decrease');
      }
    });
  }

  /**
   * 显示成绩提升效果
   */
  showScoreImprovement(element, improvement) {
    const improvementEl = document.createElement('div');
    improvementEl.className = 'score-improvement';
    improvementEl.textContent = `+${improvement}`;
    improvementEl.style.cssText = `
      position: absolute;
      top: -20px;
      right: 0;
      color: var(--success-500);
      font-weight: bold;
      font-size: 0.875rem;
      animation: scoreImprovement 2s ease-out forwards;
    `;

    element.style.position = 'relative';
    element.appendChild(improvementEl);

    setTimeout(() => {
      improvementEl.remove();
    }, 2000);
  }

  /**
   * 设置进度动画
   */
  setupProgressAnimations() {
    document.addEventListener('progressUpdate', (event) => {
      const { element, progress } = event.detail;
      this.animateProgress(element, progress);
    });
  }

  /**
   * 动画进度条
   */
  animateProgress(element, targetProgress) {
    const progressBar = element.querySelector('.progress-bar');
    if (!progressBar) return;

    const currentWidth = parseFloat(progressBar.style.width) || 0;
    const targetWidth = targetProgress;

    this.manager.animateNumber(
      { style: progressBar.style },
      currentWidth,
      targetWidth,
      1000
    );

    // 如果达到100%，显示庆祝动画
    if (targetProgress >= 100) {
      setTimeout(() => {
        this.manager.addAnimation(element, 'progress-celebration');
        this.showCompletionEffect(element);
      }, 1000);
    }
  }

  /**
   * 显示完成效果
   */
  showCompletionEffect(element) {
    // 创建庆祝粒子效果
    for (let i = 0; i < 10; i++) {
      setTimeout(() => {
        this.createCelebrationParticle(element);
      }, i * 100);
    }
  }

  /**
   * 创建庆祝粒子
   */
  createCelebrationParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'celebration-particle';
    particle.style.cssText = `
      position: absolute;
      width: 6px;
      height: 6px;
      background: var(--primary-500);
      border-radius: 50%;
      pointer-events: none;
      animation: celebrationParticle 1s ease-out forwards;
    `;

    const rect = container.getBoundingClientRect();
    particle.style.left = `${Math.random() * rect.width}px`;
    particle.style.top = `${Math.random() * rect.height}px`;

    container.style.position = 'relative';
    container.appendChild(particle);

    setTimeout(() => {
      particle.remove();
    }, 1000);
  }

  /**
   * 设置AI反馈动画
   */
  setupAIFeedbackAnimations() {
    document.addEventListener('aiFeedback', (event) => {
      const { element, type, message } = event.detail;
      this.showAIFeedback(element, type, message);
    });
  }

  /**
   * 显示AI反馈
   */
  showAIFeedback(element, type, message) {
    const feedback = document.createElement('div');
    feedback.className = `ai-feedback ai-feedback-${type}`;
    feedback.innerHTML = `
      <div class="ai-avatar">
        <i class="fas fa-robot"></i>
      </div>
      <div class="ai-message">${message}</div>
    `;

    element.appendChild(feedback);
    this.manager.addAnimation(feedback, 'fade-in-up');

    // 打字机效果
    this.typewriterEffect(feedback.querySelector('.ai-message'), message);
  }

  /**
   * 打字机效果
   */
  typewriterEffect(element, text) {
    element.textContent = '';
    let i = 0;
    
    const typeInterval = setInterval(() => {
      element.textContent += text.charAt(i);
      i++;
      
      if (i >= text.length) {
        clearInterval(typeInterval);
      }
    }, 50);
  }

  /**
   * 设置游戏化效果
   */
  setupGamificationEffects() {
    document.addEventListener('achievement', (event) => {
      const { type, title, description } = event.detail;
      this.showAchievement(type, title, description);
    });

    document.addEventListener('levelUp', (event) => {
      const { level } = event.detail;
      this.showLevelUp(level);
    });
  }

  /**
   * 显示成就
   */
  showAchievement(type, title, description) {
    const achievement = document.createElement('div');
    achievement.className = 'achievement-notification';
    achievement.innerHTML = `
      <div class="achievement-icon">
        <i class="fas fa-trophy"></i>
      </div>
      <div class="achievement-content">
        <h4 class="achievement-title">${title}</h4>
        <p class="achievement-description">${description}</p>
      </div>
    `;

    document.body.appendChild(achievement);
    this.manager.addAnimation(achievement, 'bounce-in');

    // 自动关闭
    setTimeout(() => {
      this.manager.addAnimation(achievement, 'fade-out');
      setTimeout(() => achievement.remove(), 300);
    }, 5000);
  }

  /**
   * 显示升级效果
   */
  showLevelUp(level) {
    const levelUp = document.createElement('div');
    levelUp.className = 'level-up-notification';
    levelUp.innerHTML = `
      <div class="level-up-content">
        <h2>恭喜升级！</h2>
        <div class="level-number">Lv.${level}</div>
      </div>
    `;

    document.body.appendChild(levelUp);
    this.manager.addAnimation(levelUp, 'zoom-in');

    // 添加闪光效果
    setTimeout(() => {
      this.manager.addAnimation(levelUp, 'flash');
    }, 500);

    // 自动关闭
    setTimeout(() => {
      this.manager.addAnimation(levelUp, 'zoom-out');
      setTimeout(() => levelUp.remove(), 300);
    }, 3000);
  }
}

// 初始化交互管理器
const interactionManager = new InteractionManager();
const educationInteractions = new EducationInteractions(interactionManager);

// 导出到全局
window.InteractionManager = InteractionManager;
window.EducationInteractions = EducationInteractions;
window.interactionManager = interactionManager;
window.educationInteractions = educationInteractions;

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
  interactionManager.destroy();
});