/**
 * 智能教学助手2.0 - 通用JavaScript组件库
 * 提供共享的工具函数、UI组件和交互功能
 */

// 通用工具函数库
const Utils = {
    // 格式化日期
    formatDate(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hour = String(d.getHours()).padStart(2, '0');
        const minute = String(d.getMinutes()).padStart(2, '0');
        const second = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hour)
            .replace('mm', minute)
            .replace('ss', second);
    },
    
    // 防抖函数
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
    
    // 节流函数
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
    },
    
    // 生成唯一ID
    generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    },
    
    // 深拷贝对象
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = this.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    },
    
    // 格式化文件大小
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // 验证邮箱格式
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // 验证手机号格式
    validatePhone(phone) {
        const re = /^1[3-9]\d{9}$/;
        return re.test(phone);
    },
    
    // 获取URL参数
    getUrlParams() {
        const params = {};
        const urlSearchParams = new URLSearchParams(window.location.search);
        for (const [key, value] of urlSearchParams) {
            params[key] = value;
        }
        return params;
    },
    
    // 设置本地存储
    setStorage(key, value, type = 'localStorage') {
        try {
            const storage = type === 'sessionStorage' ? sessionStorage : localStorage;
            storage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Storage error:', error);
            return false;
        }
    },
    
    // 获取本地存储
    getStorage(key, type = 'localStorage') {
        try {
            const storage = type === 'sessionStorage' ? sessionStorage : localStorage;
            const value = storage.getItem(key);
            return value ? JSON.parse(value) : null;
        } catch (error) {
            console.error('Storage error:', error);
            return null;
        }
    },
    
    // 删除本地存储
    removeStorage(key, type = 'localStorage') {
        try {
            const storage = type === 'sessionStorage' ? sessionStorage : localStorage;
            storage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Storage error:', error);
            return false;
        }
    }
};

// 通用UI组件库
const UIComponents = {
    // 显示模态框
    showModal(title, content, options = {}) {
        const defaultOptions = {
            width: 'auto',
            height: 'auto',
            closable: true,
            maskClosable: true,
            className: ''
        };
        
        const config = { ...defaultOptions, ...options };
        
        // 移除已存在的模态框
        this.closeModal();
        
        const modal = document.createElement('div');
        modal.className = `modal-overlay ${config.className}`;
        modal.innerHTML = `
            <div class="modal-container" style="width: ${config.width}; height: ${config.height}">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    ${config.closable ? '<button class="modal-close" onclick="UIComponents.closeModal()"><i class="fas fa-times"></i></button>' : ''}
                </div>
                <div class="modal-content">
                    ${content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 点击遮罩关闭
        if (config.maskClosable) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }
        
        // ESC键关闭
        if (config.closable) {
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    this.closeModal();
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);
        }
        
        return modal;
    },
    
    // 关闭模态框
    closeModal() {
        const modal = document.querySelector('.modal-overlay');
        if (modal) {
            modal.remove();
        }
    },
    
    // 显示确认对话框
    showConfirm(title, message, onConfirm, onCancel) {
        const content = `
            <div class="confirm-dialog">
                <div class="confirm-message">${message}</div>
                <div class="confirm-actions">
                    <button class="btn btn-secondary" onclick="UIComponents.handleConfirmCancel()">取消</button>
                    <button class="btn btn-primary" onclick="UIComponents.handleConfirmOk()">确定</button>
                </div>
            </div>
        `;
        
        this.showModal(title, content, { width: '400px', maskClosable: false });
        
        // 临时存储回调函数
        this._confirmCallbacks = { onConfirm, onCancel };
    },
    
    // 处理确认对话框的确定按钮
    handleConfirmOk() {
        if (this._confirmCallbacks && this._confirmCallbacks.onConfirm) {
            this._confirmCallbacks.onConfirm();
        }
        this.closeModal();
        delete this._confirmCallbacks;
    },
    
    // 处理确认对话框的取消按钮
    handleConfirmCancel() {
        if (this._confirmCallbacks && this._confirmCallbacks.onCancel) {
            this._confirmCallbacks.onCancel();
        }
        this.closeModal();
        delete this._confirmCallbacks;
    },
    
    // 显示通知
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span class="notification-message">${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // 添加到通知容器
        let container = document.querySelector('.notification-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // 自动关闭
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
        
        return notification;
    },
    
    // 获取通知图标
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    },
    
    // 显示加载覆盖层
    showLoading(message = '加载中...') {
        // 移除已存在的加载层
        this.hideLoading();
        
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p class="loading-message">${message}</p>
            </div>
        `;
        
        document.body.appendChild(overlay);
        return overlay;
    },
    
    // 隐藏加载覆盖层
    hideLoading() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    },
    
    // 创建工具提示
    createTooltip(element, content, position = 'top') {
        const tooltip = document.createElement('div');
        tooltip.className = `tooltip tooltip-${position}`;
        tooltip.innerHTML = content;
        
        element.addEventListener('mouseenter', () => {
            document.body.appendChild(tooltip);
            this.positionTooltip(tooltip, element, position);
        });
        
        element.addEventListener('mouseleave', () => {
            if (tooltip.parentElement) {
                tooltip.remove();
            }
        });
    },
    
    // 定位工具提示
    positionTooltip(tooltip, element, position) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let top, left;
        
        switch (position) {
            case 'top':
                top = rect.top - tooltipRect.height - 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = rect.bottom + 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.left - tooltipRect.width - 8;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.right + 8;
                break;
        }
        
        tooltip.style.top = `${top + window.scrollY}px`;
        tooltip.style.left = `${left + window.scrollX}px`;
    },
    
    // 创建进度条
    createProgressBar(container, options = {}) {
        const defaultOptions = {
            value: 0,
            max: 100,
            showText: true,
            animated: true,
            color: '#007bff'
        };
        
        const config = { ...defaultOptions, ...options };
        
        const progressBar = document.createElement('div');
        progressBar.className = `progress-bar ${config.animated ? 'animated' : ''}`;
        progressBar.innerHTML = `
            <div class="progress-track">
                <div class="progress-fill" style="background-color: ${config.color}"></div>
            </div>
            ${config.showText ? '<div class="progress-text">0%</div>' : ''}
        `;
        
        container.appendChild(progressBar);
        
        // 更新进度的方法
        progressBar.updateProgress = (value) => {
            const percentage = Math.min(Math.max((value / config.max) * 100, 0), 100);
            const fill = progressBar.querySelector('.progress-fill');
            const text = progressBar.querySelector('.progress-text');
            
            fill.style.width = `${percentage}%`;
            if (text) {
                text.textContent = `${Math.round(percentage)}%`;
            }
        };
        
        // 初始化进度
        progressBar.updateProgress(config.value);
        
        return progressBar;
    },
    
    // 创建标签页组件
    createTabs(container, tabs, options = {}) {
        const defaultOptions = {
            activeIndex: 0,
            onChange: null
        };
        
        const config = { ...defaultOptions, ...options };
        
        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'tabs-container';
        
        // 创建标签头部
        const tabsHeader = document.createElement('div');
        tabsHeader.className = 'tabs-header';
        
        tabs.forEach((tab, index) => {
            const tabButton = document.createElement('button');
            tabButton.className = `tab-button ${index === config.activeIndex ? 'active' : ''}`;
            tabButton.innerHTML = `
                ${tab.icon ? `<i class="${tab.icon}"></i>` : ''}
                <span>${tab.title}</span>
            `;
            
            tabButton.addEventListener('click', () => {
                this.switchTab(tabsContainer, index, config.onChange);
            });
            
            tabsHeader.appendChild(tabButton);
        });
        
        // 创建标签内容
        const tabsContent = document.createElement('div');
        tabsContent.className = 'tabs-content';
        
        tabs.forEach((tab, index) => {
            const tabPane = document.createElement('div');
            tabPane.className = `tab-pane ${index === config.activeIndex ? 'active' : ''}`;
            tabPane.innerHTML = tab.content;
            tabsContent.appendChild(tabPane);
        });
        
        tabsContainer.appendChild(tabsHeader);
        tabsContainer.appendChild(tabsContent);
        container.appendChild(tabsContainer);
        
        return tabsContainer;
    },
    
    // 切换标签页
    switchTab(tabsContainer, index, onChange) {
        const buttons = tabsContainer.querySelectorAll('.tab-button');
        const panes = tabsContainer.querySelectorAll('.tab-pane');
        
        // 移除所有活动状态
        buttons.forEach(btn => btn.classList.remove('active'));
        panes.forEach(pane => pane.classList.remove('active'));
        
        // 设置新的活动状态
        if (buttons[index]) buttons[index].classList.add('active');
        if (panes[index]) panes[index].classList.add('active');
        
        // 触发回调
        if (onChange && typeof onChange === 'function') {
            onChange(index);
        }
    }
};

// 文件处理工具
const FileUtils = {
    // 读取文件内容
    readFile(file, type = 'text') {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            
            switch (type) {
                case 'text':
                    reader.readAsText(file);
                    break;
                case 'dataURL':
                    reader.readAsDataURL(file);
                    break;
                case 'arrayBuffer':
                    reader.readAsArrayBuffer(file);
                    break;
                default:
                    reader.readAsText(file);
            }
        });
    },
    
    // 下载文件
    downloadFile(content, filename, type = 'text/plain') {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
    },
    
    // 验证文件类型
    validateFileType(file, allowedTypes) {
        const fileType = file.type;
        const fileName = file.name;
        const fileExtension = fileName.split('.').pop().toLowerCase();
        
        return allowedTypes.some(type => {
            if (type.startsWith('.')) {
                return type.slice(1) === fileExtension;
            }
            return fileType.includes(type);
        });
    },
    
    // 验证文件大小
    validateFileSize(file, maxSize) {
        return file.size <= maxSize;
    },
    
    // 压缩图片
    compressImage(file, quality = 0.8, maxWidth = 1920, maxHeight = 1080) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                // 计算新尺寸
                let { width, height } = img;
                
                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }
                
                if (height > maxHeight) {
                    width = (width * maxHeight) / height;
                    height = maxHeight;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // 绘制并压缩
                ctx.drawImage(img, 0, 0, width, height);
                canvas.toBlob(resolve, 'image/jpeg', quality);
            };
            
            img.src = URL.createObjectURL(file);
        });
    }
};

// 数据处理工具
const DataUtils = {
    // 导出为Excel
    exportToExcel(data, filename = 'export.xlsx') {
        // 这里需要引入第三方库如 SheetJS
        console.log('Export to Excel:', data, filename);
        UIComponents.showNotification('Excel导出功能需要引入SheetJS库', 'warning');
    },
    
    // 导出为CSV
    exportToCSV(data, filename = 'export.csv') {
        if (!Array.isArray(data) || data.length === 0) {
            UIComponents.showNotification('没有数据可导出', 'warning');
            return;
        }
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
        ].join('\n');
        
        FileUtils.downloadFile(csvContent, filename, 'text/csv');
    },
    
    // 导出为PDF
    exportToPDF(element, filename = 'export.pdf') {
        // 这里需要引入第三方库如 jsPDF
        console.log('Export to PDF:', element, filename);
        UIComponents.showNotification('PDF导出功能需要引入jsPDF库', 'warning');
    },
    
    // 数据分页
    paginate(data, page = 1, pageSize = 10) {
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        
        return {
            data: data.slice(startIndex, endIndex),
            currentPage: page,
            pageSize: pageSize,
            totalItems: data.length,
            totalPages: Math.ceil(data.length / pageSize),
            hasNext: endIndex < data.length,
            hasPrev: page > 1
        };
    },
    
    // 数据排序
    sortData(data, key, order = 'asc') {
        return [...data].sort((a, b) => {
            const aVal = a[key];
            const bVal = b[key];
            
            if (typeof aVal === 'string' && typeof bVal === 'string') {
                return order === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            }
            
            if (order === 'asc') {
                return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
            } else {
                return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
            }
        });
    },
    
    // 数据筛选
    filterData(data, filters) {
        return data.filter(item => {
            return Object.keys(filters).every(key => {
                const filterValue = filters[key];
                const itemValue = item[key];
                
                if (filterValue === '' || filterValue === null || filterValue === undefined) {
                    return true;
                }
                
                if (typeof filterValue === 'string') {
                    return String(itemValue).toLowerCase().includes(filterValue.toLowerCase());
                }
                
                return itemValue === filterValue;
            });
        });
    },
    
    // 数据统计
    calculateStats(data, key) {
        if (!Array.isArray(data) || data.length === 0) {
            return { count: 0, sum: 0, avg: 0, min: 0, max: 0 };
        }
        
        const values = data.map(item => Number(item[key]) || 0);
        const sum = values.reduce((acc, val) => acc + val, 0);
        
        return {
            count: values.length,
            sum: sum,
            avg: sum / values.length,
            min: Math.min(...values),
            max: Math.max(...values)
        };
    }
};

// 动画工具
const AnimationUtils = {
    // 淡入动画
    fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        const start = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = progress;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    },
    
    // 淡出动画
    fadeOut(element, duration = 300) {
        const start = performance.now();
        const startOpacity = parseFloat(getComputedStyle(element).opacity);
        
        const animate = (currentTime) => {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = startOpacity * (1 - progress);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.style.display = 'none';
            }
        };
        
        requestAnimationFrame(animate);
    },
    
    // 滑动显示
    slideDown(element, duration = 300) {
        element.style.height = '0';
        element.style.overflow = 'hidden';
        element.style.display = 'block';
        
        const targetHeight = element.scrollHeight;
        const start = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.height = `${targetHeight * progress}px`;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.style.height = 'auto';
                element.style.overflow = 'visible';
            }
        };
        
        requestAnimationFrame(animate);
    },
    
    // 滑动隐藏
    slideUp(element, duration = 300) {
        const startHeight = element.offsetHeight;
        const start = performance.now();
        
        element.style.overflow = 'hidden';
        
        const animate = (currentTime) => {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.height = `${startHeight * (1 - progress)}px`;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.style.display = 'none';
                element.style.height = 'auto';
                element.style.overflow = 'visible';
            }
        };
        
        requestAnimationFrame(animate);
    }
};

// 全局事件管理
const EventManager = {
    events: {},
    
    // 注册事件监听
    on(eventName, callback) {
        if (!this.events[eventName]) {
            this.events[eventName] = [];
        }
        this.events[eventName].push(callback);
    },
    
    // 移除事件监听
    off(eventName, callback) {
        if (!this.events[eventName]) return;
        
        if (callback) {
            this.events[eventName] = this.events[eventName].filter(cb => cb !== callback);
        } else {
            delete this.events[eventName];
        }
    },
    
    // 触发事件
    emit(eventName, data) {
        if (!this.events[eventName]) return;
        
        this.events[eventName].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Event callback error for ${eventName}:`, error);
            }
        });
    },
    
    // 只执行一次的事件监听
    once(eventName, callback) {
        const onceCallback = (data) => {
            callback(data);
            this.off(eventName, onceCallback);
        };
        this.on(eventName, onceCallback);
    }
};

// 导出到全局
window.Utils = Utils;
window.UIComponents = UIComponents;
window.FileUtils = FileUtils;
window.DataUtils = DataUtils;
window.AnimationUtils = AnimationUtils;
window.EventManager = EventManager;

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('智能教学助手2.0 - 通用组件库已加载');
    
    // 初始化全局事件监听
    EventManager.emit('app:ready');
});