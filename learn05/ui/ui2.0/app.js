/**
 * 智能教学助手 2.0 - 主应用脚本
 * 实现导航、交互和页面管理功能
 */

class TeachingAssistantApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.sidebarCollapsed = false;
        this.mobileMenuOpen = false;
        
        this.init();
    }

    /**
     * 初始化应用
     */
    init() {
        this.bindEvents();
        this.initializeComponents();
        this.loadPage(this.currentPage);
        
        // 检查移动端
        this.checkMobile();
        window.addEventListener('resize', () => this.checkMobile());
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 侧边栏切换
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // 移动端菜单切换
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => this.toggleMobileMenu());
        }

        // 移动端遮罩层
        const mobileOverlay = document.getElementById('mobileOverlay');
        if (mobileOverlay) {
            mobileOverlay.addEventListener('click', () => this.closeMobileMenu());
        }

        // 导航链接
        document.addEventListener('click', (e) => {
            const navLink = e.target.closest('[data-page]');
            if (navLink) {
                e.preventDefault();
                const page = navLink.getAttribute('data-page');
                this.navigateToPage(page);
                
                // 移动端自动关闭菜单
                if (this.isMobile()) {
                    this.closeMobileMenu();
                }
            }
        });

        // 全局搜索
        const globalSearch = document.getElementById('globalSearch');
        if (globalSearch) {
            globalSearch.addEventListener('input', (e) => this.handleGlobalSearch(e.target.value));
            globalSearch.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.executeSearch(e.target.value);
                }
            });
        }

        // 用户下拉菜单
        this.initDropdowns();

        // 快速操作按钮
        this.initQuickActions();

        // ESC键关闭移动端菜单
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.mobileMenuOpen) {
                this.closeMobileMenu();
            }
        });
    }

    /**
     * 初始化组件
     */
    initializeComponents() {
        // 初始化工具提示
        this.initTooltips();
        
        // 初始化动画
        this.initAnimations();
        
        // 初始化主题
        this.initTheme();
    }

    /**
     * 切换侧边栏
     */
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            this.sidebarCollapsed = !this.sidebarCollapsed;
            sidebar.classList.toggle('collapsed', this.sidebarCollapsed);
            
            // 保存状态到本地存储
            localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
            
            // 触发自定义事件
            this.dispatchEvent('sidebarToggle', { collapsed: this.sidebarCollapsed });
        }
    }

    /**
     * 切换移动端菜单
     */
    toggleMobileMenu() {
        this.mobileMenuOpen = !this.mobileMenuOpen;
        this.updateMobileMenu();
    }

    /**
     * 关闭移动端菜单
     */
    closeMobileMenu() {
        this.mobileMenuOpen = false;
        this.updateMobileMenu();
    }

    /**
     * 更新移动端菜单状态
     */
    updateMobileMenu() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileOverlay');
        
        if (sidebar) {
            sidebar.classList.toggle('mobile-open', this.mobileMenuOpen);
        }
        
        if (overlay) {
            overlay.classList.toggle('active', this.mobileMenuOpen);
        }
        
        // 防止背景滚动
        document.body.style.overflow = this.mobileMenuOpen ? 'hidden' : '';
    }

    /**
     * 检查是否为移动端
     */
    isMobile() {
        return window.innerWidth <= 768;
    }

    /**
     * 检查移动端状态
     */
    checkMobile() {
        if (!this.isMobile() && this.mobileMenuOpen) {
            this.closeMobileMenu();
        }
    }

    /**
     * 导航到指定页面
     */
    navigateToPage(page) {
        if (page === this.currentPage) return;
        
        // 更新导航状态
        this.updateNavigation(page);
        
        // 加载页面内容
        this.loadPage(page);
        
        // 更新面包屑
        this.updateBreadcrumb(page);
        
        // 更新URL（如果需要）
        this.updateURL(page);
        
        this.currentPage = page;
        
        // 触发页面切换事件
        this.dispatchEvent('pageChange', { page, previousPage: this.currentPage });
    }

    /**
     * 更新导航状态
     */
    updateNavigation(page) {
        // 移除所有活动状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // 添加当前页面的活动状态
        const currentNavLink = document.querySelector(`[data-page="${page}"]`);
        if (currentNavLink) {
            currentNavLink.classList.add('active');
        }
    }

    /**
     * 加载页面内容
     */
    loadPage(page) {
        // 隐藏所有页面
        document.querySelectorAll('.page').forEach(pageEl => {
            pageEl.classList.add('hidden');
        });
        
        // 显示目标页面
        const targetPage = document.getElementById(`${page}-page`);
        if (targetPage) {
            targetPage.classList.remove('hidden');
            
            // 如果页面需要动态加载内容
            this.loadPageContent(page, targetPage);
        }
    }

    /**
     * 动态加载页面内容
     */
    async loadPageContent(page, pageElement) {
        // 检查是否已经加载过内容
        if (pageElement.dataset.loaded === 'true') {
            return;
        }
        
        try {
            // 显示加载状态
            this.showPageLoading(pageElement);
            
            // 模拟加载延迟（实际项目中这里会是API调用）
            await this.delay(800);
            
            // 根据页面类型加载不同内容
            switch (page) {
                case 'lesson-prep':
                    await this.loadLessonPrepContent(pageElement);
                    break;
                case 'classroom':
                    await this.loadClassroomContent(pageElement);
                    break;
                case 'grade-management':
                    await this.loadGradeManagementContent(pageElement);
                    break;
                default:
                    // 其他页面的默认处理
                    this.hidePageLoading(pageElement);
                    break;
            }
            
            // 标记为已加载
            pageElement.dataset.loaded = 'true';
            
        } catch (error) {
            console.error(`加载页面 ${page} 时出错:`, error);
            this.showPageError(pageElement, error);
        }
    }

    /**
     * 显示页面加载状态
     */
    showPageLoading(pageElement) {
        const loadingEl = pageElement.querySelector('.page-loading');
        if (loadingEl) {
            loadingEl.style.display = 'flex';
        }
    }

    /**
     * 隐藏页面加载状态
     */
    hidePageLoading(pageElement) {
        const loadingEl = pageElement.querySelector('.page-loading');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }

    /**
     * 显示页面错误
     */
    showPageError(pageElement, error) {
        this.hidePageLoading(pageElement);
        
        const errorHTML = `
            <div class="page-error">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="error-message">
                    <h3>页面加载失败</h3>
                    <p>${error.message || '未知错误'}</p>
                    <button class="btn btn-primary" onclick="location.reload()">重新加载</button>
                </div>
            </div>
        `;
        
        pageElement.innerHTML = errorHTML;
    }

    /**
     * 加载备课助手内容
     */
    async loadLessonPrepContent(pageElement) {
        const content = `
            <div class="page-header">
                <h1 class="page-title">备课助手</h1>
                <p class="page-subtitle">AI驱动的智能备课系统</p>
            </div>
            
            <div class="lesson-prep-content">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2">
                        <div class="card">
                            <div class="card-header">
                                <h3 class="card-title">教材智能分析</h3>
                            </div>
                            <div class="card-body">
                                <div class="upload-area">
                                    <i class="fas fa-cloud-upload-alt"></i>
                                    <p>拖拽或点击上传教材文件</p>
                                    <button class="btn btn-primary">选择文件</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <div class="card">
                            <div class="card-header">
                                <h3 class="card-title">快速操作</h3>
                            </div>
                            <div class="card-body">
                                <div class="quick-actions-list">
                                    <button class="btn btn-secondary btn-block">新建课程</button>
                                    <button class="btn btn-secondary btn-block">导入模板</button>
                                    <button class="btn btn-secondary btn-block">AI生成大纲</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.hidePageLoading(pageElement);
        pageElement.innerHTML = content;
    }

    /**
     * 加载课堂助手内容
     */
    async loadClassroomContent(pageElement) {
        const content = `
            <div class="page-header">
                <h1 class="page-title">课堂助手</h1>
                <p class="page-subtitle">AI实时学情分析与课堂互动</p>
            </div>
            
            <div class="classroom-content">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">实时学情监控</h3>
                        </div>
                        <div class="card-body">
                            <div class="monitoring-dashboard">
                                <div class="metric">
                                    <span class="metric-label">参与度</span>
                                    <span class="metric-value">89%</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">理解度</span>
                                    <span class="metric-value">76%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">AI建议</h3>
                        </div>
                        <div class="card-body">
                            <div class="ai-suggestions">
                                <div class="suggestion">
                                    <i class="fas fa-lightbulb"></i>
                                    <span>建议增加互动环节</span>
                                </div>
                                <div class="suggestion">
                                    <i class="fas fa-chart-line"></i>
                                    <span>调整讲解速度</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.hidePageLoading(pageElement);
        pageElement.innerHTML = content;
    }

    /**
     * 加载成绩管理内容
     */
    async loadGradeManagementContent(pageElement) {
        const content = `
            <div class="page-header">
                <h1 class="page-title">成绩管理</h1>
                <p class="page-subtitle">智能成绩分析与个性化报告</p>
            </div>
            
            <div class="grade-management-content">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">成绩概览</h3>
                    </div>
                    <div class="card-body">
                        <div class="grade-overview">
                            <div class="grade-stats">
                                <div class="stat">
                                    <span class="stat-label">班级平均分</span>
                                    <span class="stat-value">85.6</span>
                                </div>
                                <div class="stat">
                                    <span class="stat-label">及格率</span>
                                    <span class="stat-value">92%</span>
                                </div>
                                <div class="stat">
                                    <span class="stat-label">优秀率</span>
                                    <span class="stat-value">68%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.hidePageLoading(pageElement);
        pageElement.innerHTML = content;
    }

    /**
     * 更新面包屑导航
     */
    updateBreadcrumb(page) {
        const breadcrumb = document.querySelector('.breadcrumb');
        if (!breadcrumb) return;
        
        const pageNames = {
            'dashboard': '工作台',
            'lesson-prep': '备课助手',
            'classroom': '课堂助手',
            'grade-management': '成绩管理',
            'data-analysis': '数据分析',
            'resource-library': '资源库',
            'settings': '系统设置',
            'help': '帮助中心'
        };
        
        const pageName = pageNames[page] || page;
        breadcrumb.innerHTML = `
            <div class="breadcrumb-item">
                <span class="breadcrumb-link">${pageName}</span>
            </div>
        `;
    }

    /**
     * 更新URL
     */
    updateURL(page) {
        if (history.pushState) {
            const url = page === 'dashboard' ? '/' : `/#${page}`;
            history.pushState({ page }, '', url);
        }
    }

    /**
     * 处理全局搜索
     */
    handleGlobalSearch(query) {
        // 实时搜索建议（防抖处理）
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            if (query.length >= 2) {
                this.showSearchSuggestions(query);
            } else {
                this.hideSearchSuggestions();
            }
        }, 300);
    }

    /**
     * 执行搜索
     */
    executeSearch(query) {
        if (!query.trim()) return;
        
        console.log('执行搜索:', query);
        // 这里实现具体的搜索逻辑
        this.hideSearchSuggestions();
    }

    /**
     * 显示搜索建议
     */
    showSearchSuggestions(query) {
        // 模拟搜索建议
        const suggestions = [
            '函数的性质',
            '一元二次方程',
            '导数的应用',
            '高二(3)班',
            '张同学'
        ].filter(item => item.includes(query));
        
        // 这里可以显示搜索建议下拉框
        console.log('搜索建议:', suggestions);
    }

    /**
     * 隐藏搜索建议
     */
    hideSearchSuggestions() {
        // 隐藏搜索建议下拉框
    }

    /**
     * 初始化下拉菜单
     */
    initDropdowns() {
        document.addEventListener('click', (e) => {
            const dropdown = e.target.closest('.dropdown');
            
            if (dropdown) {
                const menu = dropdown.querySelector('.dropdown-menu');
                if (menu) {
                    menu.classList.toggle('show');
                }
            } else {
                // 点击外部关闭所有下拉菜单
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
    }

    /**
     * 初始化快速操作
     */
    initQuickActions() {
        // 消息通知
        const notificationBtn = document.querySelector('[title="消息通知"]');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', () => {
                this.showNotifications();
            });
        }
        
        // AI助手
        const aiBtn = document.querySelector('[title="AI助手"]');
        if (aiBtn) {
            aiBtn.addEventListener('click', () => {
                this.openAIAssistant();
            });
        }
    }

    /**
     * 显示通知
     */
    showNotifications() {
        console.log('显示通知');
        // 实现通知面板
    }

    /**
     * 打开AI助手
     */
    openAIAssistant() {
        console.log('打开AI助手');
        // 实现AI助手对话框
    }

    /**
     * 初始化工具提示
     */
    initTooltips() {
        // 简单的工具提示实现
        document.querySelectorAll('[title]').forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.getAttribute('title'));
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    /**
     * 显示工具提示
     */
    showTooltip(element, text) {
        // 实现工具提示显示逻辑
    }

    /**
     * 隐藏工具提示
     */
    hideTooltip() {
        // 实现工具提示隐藏逻辑
    }

    /**
     * 初始化动画
     */
    initAnimations() {
        // 页面进入动画
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        });
        
        document.querySelectorAll('.card, .quick-entry').forEach(el => {
            observer.observe(el);
        });
    }

    /**
     * 初始化主题
     */
    initTheme() {
        // 从本地存储恢复主题设置
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
        }
        
        // 从本地存储恢复侧边栏状态
        const savedSidebarState = localStorage.getItem('sidebarCollapsed');
        if (savedSidebarState === 'true') {
            this.sidebarCollapsed = true;
            const sidebar = document.getElementById('sidebar');
            if (sidebar) {
                sidebar.classList.add('collapsed');
            }
        }
    }

    /**
     * 切换主题
     */
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        this.dispatchEvent('themeChange', { theme: newTheme });
    }

    /**
     * 工具方法：延迟
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 工具方法：触发自定义事件
     */
    dispatchEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { detail });
        document.dispatchEvent(event);
    }

    /**
     * 工具方法：格式化日期
     */
    formatDate(date) {
        return new Intl.DateTimeFormat('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long'
        }).format(date);
    }

    /**
     * 工具方法：防抖
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
     * 工具方法：节流
     */
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
        };
    }
}

// 应用初始化
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TeachingAssistantApp();
    
    // 全局错误处理
    window.addEventListener('error', (e) => {
        console.error('应用错误:', e.error);
    });
    
    // 全局未处理的Promise拒绝
    window.addEventListener('unhandledrejection', (e) => {
        console.error('未处理的Promise拒绝:', e.reason);
    });
});

// 导出应用类（如果使用模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TeachingAssistantApp;
}