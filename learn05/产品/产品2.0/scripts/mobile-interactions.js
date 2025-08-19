/**
 * 智能教学助手2.0 - 移动端交互脚本
 * 提供移动设备专用的交互功能和手势支持
 */

class MobileInteractions {
    constructor() {
        this.init();
        this.bindEvents();
        this.setupGestures();
    }

    init() {
        // 检测设备类型
        this.isMobile = window.innerWidth <= 768;
        this.isTouch = 'ontouchstart' in window;
        
        // 初始化移动端特性
        if (this.isMobile) {
            this.setupMobileFeatures();
        }
        
        // 监听屏幕方向变化
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });
        
        // 监听窗口大小变化
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }

    setupMobileFeatures() {
        // 禁用双击缩放
        document.addEventListener('touchstart', (e) => {
            if (e.touches.length > 1) {
                e.preventDefault();
            }
        });
        
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        // 设置视口元标签
        this.setViewportMeta();
        
        // 添加移动端CSS类
        document.body.classList.add('mobile-device');
        if (this.isTouch) {
            document.body.classList.add('touch-device');
        }
    }

    setViewportMeta() {
        let viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            viewport = document.createElement('meta');
            viewport.name = 'viewport';
            document.head.appendChild(viewport);
        }
        viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
    }

    bindEvents() {
        // 汉堡菜单切换
        this.setupMobileMenu();
        
        // 表格视图切换
        this.setupTableViewToggle();
        
        // 模态框移动端优化
        this.setupMobileModals();
        
        // 表单优化
        this.setupMobileForms();
        
        // 通知优化
        this.setupMobileNotifications();
    }

    setupMobileMenu() {
        // 创建汉堡菜单按钮
        const header = document.querySelector('.app-header');
        if (header && !header.querySelector('.mobile-menu-toggle')) {
            const menuToggle = document.createElement('button');
            menuToggle.className = 'mobile-menu-toggle';
            menuToggle.innerHTML = '<span></span>';
            menuToggle.setAttribute('aria-label', '切换菜单');
            header.insertBefore(menuToggle, header.firstChild);
            
            // 创建侧边栏遮罩
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
            
            // 绑定事件
            menuToggle.addEventListener('click', () => {
                this.toggleMobileMenu();
            });
            
            overlay.addEventListener('click', () => {
                this.closeMobileMenu();
            });
            
            // ESC键关闭菜单
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeMobileMenu();
                }
            });
        }
    }

    toggleMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const toggle = document.querySelector('.mobile-menu-toggle');
        
        if (sidebar && overlay && toggle) {
            const isOpen = sidebar.classList.contains('open');
            
            if (isOpen) {
                this.closeMobileMenu();
            } else {
                this.openMobileMenu();
            }
        }
    }

    openMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const toggle = document.querySelector('.mobile-menu-toggle');
        
        sidebar?.classList.add('open');
        overlay?.classList.add('active');
        toggle?.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const toggle = document.querySelector('.mobile-menu-toggle');
        
        sidebar?.classList.remove('open');
        overlay?.classList.remove('active');
        toggle?.classList.remove('active');
        document.body.style.overflow = '';
    }

    setupTableViewToggle() {
        const tables = document.querySelectorAll('.table-responsive');
        
        tables.forEach(tableContainer => {
            if (window.innerWidth <= 768) {
                this.createTableCardView(tableContainer);
            }
        });
    }

    createTableCardView(tableContainer) {
        const table = tableContainer.querySelector('.table');
        if (!table) return;
        
        // 创建视图切换按钮
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'table-view-toggle';
        toggleContainer.innerHTML = `
            <button class="btn btn-sm table-view-btn active" data-view="table">
                <i class="icon-table"></i> 表格
            </button>
            <button class="btn btn-sm table-view-btn" data-view="card">
                <i class="icon-card"></i> 卡片
            </button>
        `;
        
        tableContainer.insertBefore(toggleContainer, table);
        
        // 创建卡片视图
        const cardView = this.generateTableCardView(table);
        tableContainer.appendChild(cardView);
        
        // 绑定切换事件
        const toggleBtns = toggleContainer.querySelectorAll('.table-view-btn');
        toggleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.dataset.view;
                this.switchTableView(tableContainer, view);
                
                toggleBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    generateTableCardView(table) {
        const cardView = document.createElement('div');
        cardView.className = 'table-card-view';
        
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            const card = document.createElement('div');
            card.className = 'table-card';
            
            const cardHeader = document.createElement('div');
            cardHeader.className = 'table-card-header';
            cardHeader.innerHTML = `
                <div class="table-card-title">${cells[0]?.textContent || `项目 ${index + 1}`}</div>
                <div class="table-card-actions">
                    ${row.querySelector('.btn') ? row.querySelector('.btn').outerHTML : ''}
                </div>
            `;
            
            const cardBody = document.createElement('div');
            cardBody.className = 'table-card-body';
            
            cells.forEach((cell, cellIndex) => {
                if (cellIndex === 0) return; // 跳过第一列，已在标题中显示
                
                const cardRow = document.createElement('div');
                cardRow.className = 'table-card-row';
                cardRow.innerHTML = `
                    <div class="table-card-label">${headers[cellIndex] || ''}:</div>
                    <div class="table-card-value">${cell.textContent}</div>
                `;
                cardBody.appendChild(cardRow);
            });
            
            card.appendChild(cardHeader);
            card.appendChild(cardBody);
            cardView.appendChild(card);
        });
        
        return cardView;
    }

    switchTableView(container, view) {
        const table = container.querySelector('.table');
        const cardView = container.querySelector('.table-card-view');
        
        if (view === 'card') {
            table.style.display = 'none';
            cardView.classList.add('active');
        } else {
            table.style.display = '';
            cardView.classList.remove('active');
        }
    }

    setupMobileModals() {
        const modals = document.querySelectorAll('.modal-overlay');
        
        modals.forEach(modal => {
            // 添加移动端手势支持
            this.addModalGestures(modal);
            
            // 优化模态框显示
            const container = modal.querySelector('.modal-container');
            if (container && window.innerWidth <= 768) {
                container.style.maxHeight = '90vh';
                container.style.borderRadius = '16px 16px 0 0';
            }
        });
    }

    addModalGestures(modal) {
        const container = modal.querySelector('.modal-container');
        if (!container) return;
        
        let startY = 0;
        let currentY = 0;
        let isDragging = false;
        
        container.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
            isDragging = true;
        });
        
        container.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            
            currentY = e.touches[0].clientY;
            const deltaY = currentY - startY;
            
            if (deltaY > 0) {
                container.style.transform = `translateY(${deltaY}px)`;
            }
        });
        
        container.addEventListener('touchend', () => {
            if (!isDragging) return;
            
            const deltaY = currentY - startY;
            
            if (deltaY > 100) {
                // 向下滑动超过100px，关闭模态框
                this.closeModal(modal);
            } else {
                // 回弹
                container.style.transform = 'translateY(0)';
            }
            
            isDragging = false;
        });
    }

    closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    setupMobileForms() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // 优化输入框焦点行为
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // 防止iOS缩放
                if (input.type !== 'file') {
                    input.style.fontSize = '16px';
                }
                
                // 输入框获得焦点时滚动到视图
                input.addEventListener('focus', () => {
                    setTimeout(() => {
                        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 300);
                });
            });
            
            // 文件上传优化
            const fileInputs = form.querySelectorAll('input[type="file"]');
            fileInputs.forEach(input => {
                this.enhanceFileInput(input);
            });
        });
    }

    enhanceFileInput(input) {
        const wrapper = document.createElement('div');
        wrapper.className = 'file-upload';
        wrapper.innerHTML = `
            <div class="file-upload-icon">📁</div>
            <div class="file-upload-text">点击选择文件或拖拽到此处</div>
        `;
        
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        input.style.opacity = '0';
        input.style.position = 'absolute';
        input.style.width = '100%';
        input.style.height = '100%';
        input.style.cursor = 'pointer';
        
        // 拖拽支持
        wrapper.addEventListener('dragover', (e) => {
            e.preventDefault();
            wrapper.classList.add('dragover');
        });
        
        wrapper.addEventListener('dragleave', () => {
            wrapper.classList.remove('dragover');
        });
        
        wrapper.addEventListener('drop', (e) => {
            e.preventDefault();
            wrapper.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                this.updateFileUploadText(wrapper, files[0].name);
            }
        });
        
        input.addEventListener('change', () => {
            if (input.files.length > 0) {
                this.updateFileUploadText(wrapper, input.files[0].name);
            }
        });
    }

    updateFileUploadText(wrapper, fileName) {
        const textElement = wrapper.querySelector('.file-upload-text');
        if (textElement) {
            textElement.textContent = `已选择: ${fileName}`;
        }
    }

    setupMobileNotifications() {
        // 创建移动端通知容器
        let container = document.querySelector('.notification-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        // 优化通知显示位置
        if (window.innerWidth <= 768) {
            container.style.top = '16px';
            container.style.left = '16px';
            container.style.right = '16px';
            container.style.bottom = 'auto';
        }
    }

    setupGestures() {
        // 下拉刷新
        this.setupPullToRefresh();
        
        // 滑动删除
        this.setupSwipeToDelete();
        
        // 无限滚动
        this.setupInfiniteScroll();
    }

    setupPullToRefresh() {
        const refreshableElements = document.querySelectorAll('.pull-refresh');
        
        refreshableElements.forEach(element => {
            let startY = 0;
            let currentY = 0;
            let isPulling = false;
            
            element.addEventListener('touchstart', (e) => {
                if (element.scrollTop === 0) {
                    startY = e.touches[0].clientY;
                    isPulling = true;
                }
            });
            
            element.addEventListener('touchmove', (e) => {
                if (!isPulling) return;
                
                currentY = e.touches[0].clientY;
                const deltaY = currentY - startY;
                
                if (deltaY > 0 && deltaY < 100) {
                    element.classList.add('pulling');
                    e.preventDefault();
                }
            });
            
            element.addEventListener('touchend', () => {
                if (!isPulling) return;
                
                const deltaY = currentY - startY;
                
                if (deltaY > 60) {
                    this.triggerRefresh(element);
                }
                
                element.classList.remove('pulling');
                isPulling = false;
            });
        });
    }

    triggerRefresh(element) {
        const event = new CustomEvent('pullrefresh', {
            detail: { element }
        });
        element.dispatchEvent(event);
        
        // 显示刷新指示器
        this.showToast('正在刷新...');
    }

    setupSwipeToDelete() {
        const swipeItems = document.querySelectorAll('.swipe-item');
        
        swipeItems.forEach(item => {
            let startX = 0;
            let currentX = 0;
            let isSwiping = false;
            
            item.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                isSwiping = true;
            });
            
            item.addEventListener('touchmove', (e) => {
                if (!isSwiping) return;
                
                currentX = e.touches[0].clientX;
                const deltaX = currentX - startX;
                
                if (deltaX < -50) {
                    item.classList.add('swiped');
                } else if (deltaX > 50) {
                    item.classList.remove('swiped');
                }
            });
            
            item.addEventListener('touchend', () => {
                isSwiping = false;
            });
            
            // 点击删除按钮
            const deleteBtn = item.querySelector('.swipe-actions');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', () => {
                    this.handleSwipeDelete(item);
                });
            }
        });
    }

    handleSwipeDelete(item) {
        const event = new CustomEvent('swipedelete', {
            detail: { item }
        });
        item.dispatchEvent(event);
    }

    setupInfiniteScroll() {
        const scrollContainers = document.querySelectorAll('.infinite-scroll');
        
        scrollContainers.forEach(container => {
            const trigger = container.querySelector('.infinite-scroll-trigger');
            if (!trigger) return;
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.triggerInfiniteLoad(container);
                    }
                });
            }, {
                rootMargin: '100px'
            });
            
            observer.observe(trigger);
        });
    }

    triggerInfiniteLoad(container) {
        const event = new CustomEvent('infiniteload', {
            detail: { container }
        });
        container.dispatchEvent(event);
    }

    handleOrientationChange() {
        // 重新计算布局
        this.isMobile = window.innerWidth <= 768;
        
        // 关闭移动菜单
        if (!this.isMobile) {
            this.closeMobileMenu();
        }
        
        // 重新设置表格视图
        setTimeout(() => {
            this.setupTableViewToggle();
        }, 100);
    }

    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        if (wasMobile !== this.isMobile) {
            // 设备类型发生变化
            if (this.isMobile) {
                document.body.classList.add('mobile-device');
                this.setupMobileFeatures();
            } else {
                document.body.classList.remove('mobile-device');
                this.closeMobileMenu();
            }
        }
    }

    // 工具方法
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

    showToast(message, duration = 3000) {
        // 移除现有的toast
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        // 创建新的toast
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // 显示动画
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // 自动隐藏
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, duration);
    }

    // 公共API
    static getInstance() {
        if (!MobileInteractions.instance) {
            MobileInteractions.instance = new MobileInteractions();
        }
        return MobileInteractions.instance;
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    MobileInteractions.getInstance();
});

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileInteractions;
} else if (typeof window !== 'undefined') {
    window.MobileInteractions = MobileInteractions;
}