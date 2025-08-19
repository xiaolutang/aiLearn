// 智能教学助手2.0 - 主JavaScript文件

// 全局应用对象
const TeachingAssistant = {
  // 应用状态
  state: {
    currentModule: 'dashboard',
    sidebarCollapsed: false,
    user: {
      name: '张老师',
      avatar: 'https://via.placeholder.com/32x32/2563EB/FFFFFF?text=张',
      role: '语文教师'
    },
    notifications: [
      { id: 1, type: 'info', message: '新的备课建议已生成', time: '5分钟前' },
      { id: 2, type: 'success', message: '成绩录入完成', time: '1小时前' },
      { id: 3, type: 'warning', message: '课堂录制存储空间不足', time: '2小时前' }
    ]
  },

  // 初始化应用
  init() {
    this.bindEvents();
    this.loadModule(this.state.currentModule);
    this.updateUserInfo();
    this.updateNotifications();
    console.log('智能教学助手2.0 已初始化');
  },

  // 绑定事件
  bindEvents() {
    // 侧边栏切换
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', () => this.toggleSidebar());
    }

    // 导航链接点击
    document.addEventListener('click', (e) => {
      if (e.target.matches('.nav-link') || e.target.closest('.nav-link')) {
        e.preventDefault();
        const link = e.target.closest('.nav-link');
        const module = link.dataset.module;
        if (module) {
          this.loadModule(module);
        }
      }
    });

    // 快速功能卡片点击
    document.addEventListener('click', (e) => {
      if (e.target.matches('.action-card') || e.target.closest('.action-card')) {
        const card = e.target.closest('.action-card');
        const action = card.dataset.action;
        if (action) {
          this.handleQuickAction(action);
        }
      }
    });

    // 通知图标点击
    const notificationIcon = document.querySelector('.notification-icon');
    if (notificationIcon) {
      notificationIcon.addEventListener('click', () => this.showNotifications());
    }

    // 用户资料点击
    const userProfile = document.querySelector('.user-profile');
    if (userProfile) {
      userProfile.addEventListener('click', () => this.showUserMenu());
    }

    // 窗口大小变化
    window.addEventListener('resize', () => this.handleResize());

    // ESC键关闭模态框
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeModal();
      }
    });
  },

  // 切换侧边栏
  toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    this.state.sidebarCollapsed = !this.state.sidebarCollapsed;
    
    if (this.state.sidebarCollapsed) {
      sidebar.classList.add('collapsed');
    } else {
      sidebar.classList.remove('collapsed');
    }

    // 保存状态到本地存储
    localStorage.setItem('sidebarCollapsed', this.state.sidebarCollapsed);
  },

  // 加载模块
  loadModule(moduleName) {
    this.state.currentModule = moduleName;
    
    // 更新导航状态
    this.updateNavigation(moduleName);
    
    // 更新面包屑
    this.updateBreadcrumb(moduleName);
    
    // 加载模块内容
    this.loadModuleContent(moduleName);
    
    // 更新URL
    history.pushState({ module: moduleName }, '', `#${moduleName}`);
  },

  // 更新导航状态
  updateNavigation(activeModule) {
    // 清除所有活动状态
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.remove('active');
    });
    
    // 设置当前活动状态
    const activeLink = document.querySelector(`[data-module="${activeModule}"]`);
    if (activeLink) {
      activeLink.classList.add('active');
    }
  },

  // 更新面包屑
  updateBreadcrumb(moduleName) {
    const breadcrumb = document.querySelector('.breadcrumb');
    if (!breadcrumb) return;

    const moduleNames = {
      'dashboard': '工作台',
      'lesson-prep': '备课助手',
      'classroom-ai': '课堂AI助手',
      'grade-management': '成绩管理',
      'settings': '系统设置'
    };

    breadcrumb.innerHTML = `
      <span class="breadcrumb-item">首页</span>
      <i class="fas fa-chevron-right"></i>
      <span class="breadcrumb-item current">${moduleNames[moduleName] || '未知模块'}</span>
    `;
  },

  // 加载模块内容
  loadModuleContent(moduleName) {
    const contentArea = document.querySelector('.page-content');
    if (!contentArea) return;

    // 显示加载状态
    this.showLoading();

    // 模拟异步加载
    setTimeout(() => {
      let content = '';
      
      switch (moduleName) {
        case 'dashboard':
          content = this.getDashboardContent();
          break;
        case 'lesson-prep':
          content = this.getLessonPrepContent();
          break;
        case 'classroom-ai':
          content = this.getClassroomAIContent();
          break;
        case 'grade-management':
          content = this.getGradeManagementContent();
          break;
        case 'settings':
          content = this.getSettingsContent();
          break;
        default:
          content = '<h2>模块开发中...</h2><p>该功能正在开发中，敬请期待。</p>';
      }
      
      contentArea.innerHTML = content;
      this.hideLoading();
      
      // 添加淡入动画
      contentArea.classList.add('fade-in');
      setTimeout(() => contentArea.classList.remove('fade-in'), 300);
      
    }, 500);
  },

  // 获取工作台内容
  getDashboardContent() {
    return `
      <div class="page-header">
        <h1 class="page-title">工作台</h1>
        <p class="page-subtitle">欢迎使用智能教学助手2.0，让AI为您的教学赋能</p>
      </div>
      
      <div class="quick-actions">
        <h2 class="section-title">快速功能</h2>
        <div class="action-grid">
          <div class="action-card" data-action="new-lesson">
            <div class="action-icon">
              <i class="fas fa-plus-circle"></i>
            </div>
            <h3>新建课程</h3>
            <p>快速创建新的教学课程，AI将协助您完成备课工作</p>
          </div>
          <div class="action-card" data-action="grade-input">
            <div class="action-icon">
              <i class="fas fa-edit"></i>
            </div>
            <h3>录入成绩</h3>
            <p>智能成绩录入，支持多种方式，自动生成分析报告</p>
          </div>
          <div class="action-card" data-action="classroom-record">
            <div class="action-icon">
              <i class="fas fa-video"></i>
            </div>
            <h3>课堂录制</h3>
            <p>开始课堂录制，AI将实时分析教学效果</p>
          </div>
          <div class="action-card" data-action="student-report">
            <div class="action-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <h3>学情分析</h3>
            <p>查看学生学习情况，获取个性化教学建议</p>
          </div>
        </div>
      </div>
      
      <div class="stats-overview">
        <h2 class="section-title">数据概览</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-users"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">156</div>
              <div class="stat-label">学生总数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-book"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">24</div>
              <div class="stat-label">本周课程</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-clipboard-check"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">89%</div>
              <div class="stat-label">作业完成率</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-star"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">4.8</div>
              <div class="stat-label">教学评分</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="recent-activities">
        <h2 class="section-title">最近活动</h2>
        <div class="activity-list">
          <div class="activity-item">
            <div class="activity-icon">
              <i class="fas fa-book-open"></i>
            </div>
            <div class="activity-content">
              <h4>完成《春》课程备课</h4>
              <p>AI生成了详细的教学方案和互动环节设计</p>
            </div>
            <div class="activity-status">
              <span class="status-badge success">已完成</span>
            </div>
          </div>
          <div class="activity-item">
            <div class="activity-icon">
              <i class="fas fa-chart-bar"></i>
            </div>
            <div class="activity-content">
              <h4>生成期中考试分析报告</h4>
              <p>为156名学生生成了个性化学习建议</p>
            </div>
            <div class="activity-status">
              <span class="status-badge info">进行中</span>
            </div>
          </div>
          <div class="activity-item">
            <div class="activity-icon">
              <i class="fas fa-video"></i>
            </div>
            <div class="activity-content">
              <h4>课堂录制分析</h4>
              <p>昨日语文课堂教学效果分析已完成</p>
            </div>
            <div class="activity-status">
              <span class="status-badge warning">待查看</span>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  // 获取备课助手内容
  getLessonPrepContent() {
    return `
      <div class="page-header">
        <h1 class="page-title">备课助手</h1>
        <p class="page-subtitle">AI智能备课，让教学准备更高效</p>
      </div>
      
      <div class="module-content">
        <h2>功能开发中...</h2>
        <p>备课助手模块正在开发中，将包含以下功能：</p>
        <ul>
          <li>教材智能分析</li>
          <li>教学环节策划</li>
          <li>学情预设分析</li>
          <li>优秀案例推荐</li>
        </ul>
      </div>
    `;
  },

  // 获取课堂AI助手内容
  getClassroomAIContent() {
    return `
      <div class="page-header">
        <h1 class="page-title">课堂AI助手</h1>
        <p class="page-subtitle">实时智能分析，提升课堂教学效果</p>
      </div>
      
      <div class="module-content">
        <h2>功能开发中...</h2>
        <p>课堂AI助手模块正在开发中，将包含以下功能：</p>
        <ul>
          <li>实时学情生成</li>
          <li>智能练习推荐</li>
          <li>实验设计助手</li>
          <li>课堂录制分析</li>
        </ul>
      </div>
    `;
  },

  // 获取成绩管理内容
  getGradeManagementContent() {
    return `
      <div class="page-header">
        <h1 class="page-title">成绩管理</h1>
        <p class="page-subtitle">智能成绩分析，个性化学习指导</p>
      </div>
      
      <div class="module-content">
        <h2>功能开发中...</h2>
        <p>成绩管理模块正在开发中，将包含以下功能：</p>
        <ul>
          <li>智能成绩录入</li>
          <li>多维度成绩分析</li>
          <li>个性化学习报告</li>
          <li>辅导方案生成</li>
        </ul>
      </div>
    `;
  },

  // 获取设置内容
  getSettingsContent() {
    return `
      <div class="page-header">
        <h1 class="page-title">系统设置</h1>
        <p class="page-subtitle">个性化配置，优化使用体验</p>
      </div>
      
      <div class="module-content">
        <h2>功能开发中...</h2>
        <p>系统设置模块正在开发中，将包含以下功能：</p>
        <ul>
          <li>个人信息管理</li>
          <li>系统偏好设置</li>
          <li>数据导入导出</li>
          <li>权限管理</li>
        </ul>
      </div>
    `;
  },

  // 处理快速功能
  handleQuickAction(action) {
    switch (action) {
      case 'new-lesson':
        this.loadModule('lesson-prep');
        break;
      case 'grade-input':
        this.loadModule('grade-management');
        break;
      case 'classroom-record':
        this.loadModule('classroom-ai');
        break;
      case 'student-report':
        this.showModal('学情分析', '学情分析功能开发中...');
        break;
      default:
        console.log('未知操作:', action);
    }
  },

  // 更新用户信息
  updateUserInfo() {
    const userNameEl = document.querySelector('.user-name');
    const userAvatarEl = document.querySelector('.user-avatar');
    
    if (userNameEl) userNameEl.textContent = this.state.user.name;
    if (userAvatarEl) userAvatarEl.src = this.state.user.avatar;
  },

  // 更新通知
  updateNotifications() {
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
      const unreadCount = this.state.notifications.length;
      notificationBadge.textContent = unreadCount;
      notificationBadge.style.display = unreadCount > 0 ? 'flex' : 'none';
    }
  },

  // 显示通知
  showNotifications() {
    const notifications = this.state.notifications.map(notif => `
      <div class="notification-item">
        <div class="notification-icon ${notif.type}">
          <i class="fas fa-${this.getNotificationIcon(notif.type)}"></i>
        </div>
        <div class="notification-content">
          <p>${notif.message}</p>
          <span class="notification-time">${notif.time}</span>
        </div>
      </div>
    `).join('');

    this.showModal('通知中心', `
      <div class="notifications-list">
        ${notifications}
      </div>
    `);
  },

  // 获取通知图标
  getNotificationIcon(type) {
    const icons = {
      'info': 'info-circle',
      'success': 'check-circle',
      'warning': 'exclamation-triangle',
      'error': 'times-circle'
    };
    return icons[type] || 'bell';
  },

  // 显示用户菜单
  showUserMenu() {
    this.showModal('用户菜单', `
      <div class="user-menu">
        <div class="user-info">
          <img src="${this.state.user.avatar}" alt="用户头像" class="user-avatar-large">
          <h3>${this.state.user.name}</h3>
          <p>${this.state.user.role}</p>
        </div>
        <div class="menu-items">
          <a href="#" class="menu-item">
            <i class="fas fa-user"></i>
            <span>个人资料</span>
          </a>
          <a href="#" class="menu-item">
            <i class="fas fa-cog"></i>
            <span>账户设置</span>
          </a>
          <a href="#" class="menu-item">
            <i class="fas fa-question-circle"></i>
            <span>帮助中心</span>
          </a>
          <a href="#" class="menu-item logout">
            <i class="fas fa-sign-out-alt"></i>
            <span>退出登录</span>
          </a>
        </div>
      </div>
    `);
  },

  // 显示模态框
  showModal(title, content) {
    const modalHTML = `
      <div class="modal-overlay" id="modal">
        <div class="modal-container">
          <div class="modal-header">
            <h3 class="modal-title">${title}</h3>
            <button class="modal-close" onclick="TeachingAssistant.closeModal()">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            ${content}
          </div>
        </div>
      </div>
    `;
    
    // 移除现有模态框
    const existingModal = document.getElementById('modal');
    if (existingModal) {
      existingModal.remove();
    }
    
    // 添加新模态框
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 显示模态框
    setTimeout(() => {
      const modal = document.getElementById('modal');
      if (modal) {
        modal.classList.add('show');
      }
    }, 10);
  },

  // 关闭模态框
  closeModal() {
    const modal = document.getElementById('modal');
    if (modal) {
      modal.classList.remove('show');
      setTimeout(() => modal.remove(), 300);
    }
  },

  // 显示加载状态
  showLoading() {
    const loadingHTML = `
      <div class="loading-overlay" id="loading">
        <div class="loading-spinner">
          <i class="fas fa-spinner fa-spin"></i>
          <p>加载中...</p>
        </div>
      </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', loadingHTML);
  },

  // 隐藏加载状态
  hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
      loading.remove();
    }
  },

  // 处理窗口大小变化
  handleResize() {
    const width = window.innerWidth;
    
    // 在小屏幕上自动折叠侧边栏
    if (width <= 1024 && !this.state.sidebarCollapsed) {
      this.toggleSidebar();
    }
  },

  // 工具函数：格式化日期
  formatDate(date) {
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  },

  // 工具函数：防抖
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
  },

  // 工具函数：节流
  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    }
  }
};

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
  TeachingAssistant.init();
});

// 处理浏览器前进后退
window.addEventListener('popstate', (e) => {
  if (e.state && e.state.module) {
    TeachingAssistant.loadModule(e.state.module);
  }
});

// 导出到全局作用域
window.TeachingAssistant = TeachingAssistant;