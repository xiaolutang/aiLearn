/**
 * 备课助手模块 JavaScript 交互逻辑
 * 智能教学助手2.0 - 备课助手模块
 */

// 备课助手模块对象
const LessonPrep = {
    // 当前活跃的标签页
    activeTab: 'material-analysis',
    
    // 上传状态
    uploadState: {
        isUploading: false,
        progress: 0,
        currentFile: null
    },
    
    // 分析结果数据
    analysisData: {
        knowledgePoints: [],
        difficulties: [],
        objectives: []
    },
    
    // 教学环节数据
    lessonSteps: [],
    
    // 资源推荐数据
    resources: [],
    
    // 初始化
    init() {
        this.bindEvents();
        this.loadInitialData();
        this.setupTabSwitching();
        this.initializeUploadArea();
    },
    
    // 绑定事件
    bindEvents() {
        // 标签页切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // 文件上传
        const uploadArea = document.querySelector('.upload-area');
        const fileInput = document.querySelector('#file-upload');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => fileInput.click());
            uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
            uploadArea.addEventListener('drop', this.handleFileDrop.bind(this));
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }
        
        // 分析按钮
        const analyzeBtn = document.querySelector('.analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', this.startAnalysis.bind(this));
        }
        
        // 导出按钮
        const exportBtn = document.querySelector('.export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', this.exportResults.bind(this));
        }
        
        // 教学环节编辑
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('edit-step-btn')) {
                this.editLessonStep(e.target.dataset.stepId);
            }
            if (e.target.classList.contains('delete-step-btn')) {
                this.deleteLessonStep(e.target.dataset.stepId);
            }
        });
        
        // 资源预览
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('preview-resource-btn')) {
                this.previewResource(e.target.dataset.resourceId);
            }
            if (e.target.classList.contains('download-resource-btn')) {
                this.downloadResource(e.target.dataset.resourceId);
            }
        });
    },
    
    // 加载初始数据
    loadInitialData() {
        // 模拟加载知识点数据
        this.analysisData.knowledgePoints = [
            { id: 1, type: 'primary', content: '函数的定义与性质', level: '重点' },
            { id: 2, type: 'secondary', content: '函数的图像与变换', level: '难点' },
            { id: 3, type: 'tertiary', content: '函数的应用实例', level: '一般' }
        ];
        
        // 模拟加载教学目标
        this.analysisData.objectives = [
            { id: 1, type: 'knowledge', content: '理解函数的概念，掌握函数的表示方法' },
            { id: 2, type: 'ability', content: '能够分析函数的性质，绘制函数图像' },
            { id: 3, type: 'emotion', content: '培养数学思维，提高解决问题的能力' }
        ];
        
        // 模拟加载教学环节
        this.lessonSteps = [
            {
                id: 1,
                title: '课程导入',
                time: '5分钟',
                description: '通过生活实例引入函数概念，激发学生学习兴趣',
                activities: ['问题导入', '情境创设', '思维启发']
            },
            {
                id: 2,
                title: '新知讲授',
                time: '25分钟',
                description: '系统讲解函数的定义、性质和表示方法',
                activities: ['概念讲解', '例题分析', '互动讨论']
            },
            {
                id: 3,
                title: '练习巩固',
                time: '10分钟',
                description: '通过练习题巩固所学知识，检验学习效果',
                activities: ['课堂练习', '小组讨论', '答疑解惑']
            }
        ];
        
        // 模拟加载资源推荐
        this.resources = [
            {
                id: 1,
                title: '函数概念教学课件',
                description: '包含丰富的图表和动画演示',
                type: 'PPT',
                size: '2.5MB',
                icon: 'fas fa-file-powerpoint'
            },
            {
                id: 2,
                title: '函数性质练习题',
                description: '分层次的练习题集，适合不同水平学生',
                type: 'PDF',
                size: '1.8MB',
                icon: 'fas fa-file-pdf'
            },
            {
                id: 3,
                title: '函数图像绘制工具',
                description: '交互式图像绘制软件，帮助学生理解函数',
                type: '软件',
                size: '15.2MB',
                icon: 'fas fa-desktop'
            }
        ];
        
        this.renderInitialContent();
    },
    
    // 渲染初始内容
    renderInitialContent() {
        this.renderKnowledgePoints();
        this.renderObjectives();
        this.renderLessonSteps();
        this.renderResources();
    },
    
    // 设置标签页切换
    setupTabSwitching() {
        const tabs = document.querySelectorAll('.tab-btn');
        const contents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.dataset.tab;
                
                // 移除所有活跃状态
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                
                // 添加活跃状态
                tab.classList.add('active');
                const targetContent = document.querySelector(`[data-tab-content="${targetTab}"]`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
                
                this.activeTab = targetTab;
            });
        });
    },
    
    // 初始化上传区域
    initializeUploadArea() {
        const uploadArea = document.querySelector('.upload-area');
        if (!uploadArea) return;
        
        uploadArea.addEventListener('dragenter', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            if (!uploadArea.contains(e.relatedTarget)) {
                uploadArea.classList.remove('drag-over');
            }
        });
    },
    
    // 切换标签页
    switchTab(tabName) {
        const tabs = document.querySelectorAll('.tab-btn');
        const contents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        contents.forEach(content => {
            content.classList.toggle('active', content.dataset.tabContent === tabName);
        });
        
        this.activeTab = tabName;
    },
    
    // 处理拖拽悬停
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    },
    
    // 处理文件拖拽
    handleFileDrop(e) {
        e.preventDefault();
        const uploadArea = e.currentTarget;
        uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    },
    
    // 处理文件选择
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    },
    
    // 处理文件
    processFile(file) {
        // 验证文件类型
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        
        if (!allowedTypes.includes(file.type)) {
            this.showNotification('请上传PDF、Word或文本文件', 'error');
            return;
        }
        
        // 验证文件大小 (10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showNotification('文件大小不能超过10MB', 'error');
            return;
        }
        
        this.uploadState.currentFile = file;
        this.showUploadProgress();
        this.simulateUpload();
    },
    
    // 显示上传进度
    showUploadProgress() {
        const uploadSection = document.querySelector('.upload-section');
        if (!uploadSection) return;
        
        uploadSection.innerHTML = `
            <div class="upload-progress">
                <div class="progress-icon">
                    <i class="fas fa-cloud-upload-alt"></i>
                </div>
                <h3>正在上传文件...</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
                <p class="progress-text">0%</p>
            </div>
        `;
    },
    
    // 模拟上传过程
    simulateUpload() {
        this.uploadState.isUploading = true;
        this.uploadState.progress = 0;
        
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');
        
        const interval = setInterval(() => {
            this.uploadState.progress += Math.random() * 15;
            
            if (this.uploadState.progress >= 100) {
                this.uploadState.progress = 100;
                clearInterval(interval);
                
                setTimeout(() => {
                    this.uploadState.isUploading = false;
                    this.showAnalysisInterface();
                }, 500);
            }
            
            if (progressFill) {
                progressFill.style.width = `${this.uploadState.progress}%`;
            }
            if (progressText) {
                progressText.textContent = `${Math.round(this.uploadState.progress)}%`;
            }
        }, 200);
    },
    
    // 显示分析界面
    showAnalysisInterface() {
        const uploadSection = document.querySelector('.upload-section');
        if (!uploadSection) return;
        
        uploadSection.innerHTML = `
            <div class="upload-card">
                <div class="file-info">
                    <div class="file-icon">
                        <i class="fas fa-file-alt"></i>
                    </div>
                    <div class="file-details">
                        <h4>${this.uploadState.currentFile.name}</h4>
                        <p>文件大小: ${(this.uploadState.currentFile.size / 1024 / 1024).toFixed(2)} MB</p>
                        <p>上传时间: ${new Date().toLocaleString()}</p>
                    </div>
                </div>
                <div class="analysis-actions">
                    <button class="btn btn-primary analyze-btn">
                        <i class="fas fa-brain"></i>
                        开始智能分析
                    </button>
                    <button class="btn btn-secondary reupload-btn">
                        <i class="fas fa-upload"></i>
                        重新上传
                    </button>
                </div>
            </div>
        `;
        
        // 重新绑定事件
        const analyzeBtn = document.querySelector('.analyze-btn');
        const reuploadBtn = document.querySelector('.reupload-btn');
        
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', this.startAnalysis.bind(this));
        }
        
        if (reuploadBtn) {
            reuploadBtn.addEventListener('click', this.resetUpload.bind(this));
        }
    },
    
    // 开始分析
    startAnalysis() {
        this.showLoadingOverlay('正在进行智能分析...');
        
        // 模拟分析过程
        setTimeout(() => {
            this.hideLoadingOverlay();
            this.showAnalysisResults();
            this.showNotification('分析完成！', 'success');
        }, 3000);
    },
    
    // 显示分析结果
    showAnalysisResults() {
        const resultsContainer = document.querySelector('.analysis-results');
        if (!resultsContainer) return;
        
        resultsContainer.style.display = 'grid';
        resultsContainer.innerHTML = `
            <div class="result-card">
                <div class="card-header">
                    <h3><i class="fas fa-lightbulb"></i>知识点分析</h3>
                    <div class="card-actions">
                        <button class="btn btn-sm btn-outline export-knowledge-btn">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <div class="knowledge-points" id="knowledge-points-container">
                        <!-- 知识点内容将在这里渲染 -->
                    </div>
                </div>
            </div>
            
            <div class="result-card">
                <div class="card-header">
                    <h3><i class="fas fa-exclamation-triangle"></i>教学重难点</h3>
                    <div class="card-actions">
                        <button class="btn btn-sm btn-outline export-difficulties-btn">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <div class="difficulty-analysis" id="difficulties-container">
                        <!-- 重难点内容将在这里渲染 -->
                    </div>
                </div>
            </div>
            
            <div class="result-card">
                <div class="card-header">
                    <h3><i class="fas fa-target"></i>教学目标</h3>
                    <div class="card-actions">
                        <button class="btn btn-sm btn-outline export-objectives-btn">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <div class="objectives-list" id="objectives-container">
                        <!-- 教学目标内容将在这里渲染 -->
                    </div>
                </div>
            </div>
        `;
        
        this.renderKnowledgePoints();
        this.renderDifficulties();
        this.renderObjectives();
    },
    
    // 渲染知识点
    renderKnowledgePoints() {
        const container = document.querySelector('#knowledge-points-container');
        if (!container) return;
        
        container.innerHTML = this.analysisData.knowledgePoints.map(point => `
            <div class="knowledge-point ${point.type}">
                <div class="point-label">${point.level}</div>
                <div class="point-content">${point.content}</div>
            </div>
        `).join('');
    },
    
    // 渲染重难点
    renderDifficulties() {
        const container = document.querySelector('#difficulties-container');
        if (!container) return;
        
        const difficulties = [
            {
                type: 'important',
                title: '教学重点',
                content: '函数概念的理解和函数表示方法的掌握',
                suggestions: ['概念讲解', '实例分析', '对比学习']
            },
            {
                type: 'difficult',
                title: '教学难点',
                content: '函数性质的分析和函数图像的绘制',
                suggestions: ['图像演示', '分步讲解', '练习巩固']
            }
        ];
        
        container.innerHTML = difficulties.map(item => `
            <div class="difficulty-item">
                <div class="difficulty-type ${item.type}">${item.title}</div>
                <div class="difficulty-desc">${item.content}</div>
                <div class="difficulty-suggestions">
                    ${item.suggestions.map(suggestion => `
                        <span class="suggestion-tag">${suggestion}</span>
                    `).join('')}
                </div>
            </div>
        `).join('');
    },
    
    // 渲染教学目标
    renderObjectives() {
        const container = document.querySelector('#objectives-container');
        if (!container) return;
        
        container.innerHTML = this.analysisData.objectives.map((objective, index) => `
            <div class="objective-item">
                <div class="objective-number ${objective.type}">${index + 1}</div>
                <div class="objective-content">${objective.content}</div>
            </div>
        `).join('');
    },
    
    // 渲染教学环节
    renderLessonSteps() {
        const container = document.querySelector('#lesson-timeline');
        if (!container) return;
        
        container.innerHTML = this.lessonSteps.map((step, index) => `
            <div class="timeline-item">
                <div class="timeline-marker">${index + 1}</div>
                <div class="timeline-content">
                    <div class="step-header">
                        <h4><i class="fas fa-play-circle"></i>${step.title}</h4>
                        <div class="time-badge">${step.time}</div>
                    </div>
                    <div class="step-description">
                        <p>${step.description}</p>
                    </div>
                    <div class="step-activities">
                        ${step.activities.map(activity => `
                            <span class="activity-tag">${activity}</span>
                        `).join('')}
                    </div>
                    <div class="step-actions">
                        <button class="btn btn-sm btn-outline edit-step-btn" data-step-id="${step.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline delete-step-btn" data-step-id="${step.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    },
    
    // 渲染资源推荐
    renderResources() {
        const container = document.querySelector('#resources-grid');
        if (!container) return;
        
        container.innerHTML = this.resources.map(resource => `
            <div class="resource-item">
                <div class="resource-icon">
                    <i class="${resource.icon}"></i>
                </div>
                <div class="resource-info">
                    <h4>${resource.title}</h4>
                    <p>${resource.description}</p>
                    <div class="resource-meta">
                        <span class="resource-type">${resource.type}</span>
                        <span class="resource-size">${resource.size}</span>
                    </div>
                </div>
                <div class="resource-actions">
                    <button class="btn btn-sm btn-outline preview-resource-btn" data-resource-id="${resource.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-primary download-resource-btn" data-resource-id="${resource.id}">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
        `).join('');
    },
    
    // 重置上传
    resetUpload() {
        const uploadSection = document.querySelector('.upload-section');
        if (!uploadSection) return;
        
        uploadSection.innerHTML = `
            <div class="upload-card">
                <div class="upload-area">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <h3>上传教材文件</h3>
                    <p>支持PDF、Word、文本格式，文件大小不超过10MB</p>
                    <input type="file" id="file-upload" accept=".pdf,.doc,.docx,.txt" style="display: none;">
                </div>
                <div class="upload-options">
                    <div class="option-item">
                        <input type="checkbox" id="extract-images" checked>
                        <label for="extract-images">提取图片内容</label>
                    </div>
                    <div class="option-item">
                        <input type="checkbox" id="analyze-structure" checked>
                        <label for="analyze-structure">分析文档结构</label>
                    </div>
                    <div class="option-item">
                        <input type="checkbox" id="generate-outline" checked>
                        <label for="generate-outline">生成内容大纲</label>
                    </div>
                </div>
            </div>
        `;
        
        this.uploadState = {
            isUploading: false,
            progress: 0,
            currentFile: null
        };
        
        this.initializeUploadArea();
        
        // 重新绑定文件上传事件
        const uploadArea = document.querySelector('.upload-area');
        const fileInput = document.querySelector('#file-upload');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => fileInput.click());
            uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
            uploadArea.addEventListener('drop', this.handleFileDrop.bind(this));
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }
    },
    
    // 编辑教学环节
    editLessonStep(stepId) {
        const step = this.lessonSteps.find(s => s.id == stepId);
        if (!step) return;
        
        this.showModal('编辑教学环节', `
            <form id="edit-step-form">
                <div class="form-group">
                    <label for="step-title">环节标题</label>
                    <input type="text" id="step-title" class="form-input" value="${step.title}" required>
                </div>
                <div class="form-group">
                    <label for="step-time">时间安排</label>
                    <input type="text" id="step-time" class="form-input" value="${step.time}" required>
                </div>
                <div class="form-group">
                    <label for="step-description">环节描述</label>
                    <textarea id="step-description" class="form-textarea" required>${step.description}</textarea>
                </div>
                <div class="form-group">
                    <label for="step-activities">教学活动（用逗号分隔）</label>
                    <input type="text" id="step-activities" class="form-input" value="${step.activities.join(', ')}" required>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="LessonPrep.closeModal()">取消</button>
                    <button type="submit" class="btn btn-primary">保存</button>
                </div>
            </form>
        `);
        
        // 绑定表单提交事件
        document.getElementById('edit-step-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveStepEdit(stepId);
        });
    },
    
    // 保存环节编辑
    saveStepEdit(stepId) {
        const step = this.lessonSteps.find(s => s.id == stepId);
        if (!step) return;
        
        step.title = document.getElementById('step-title').value;
        step.time = document.getElementById('step-time').value;
        step.description = document.getElementById('step-description').value;
        step.activities = document.getElementById('step-activities').value.split(',').map(a => a.trim());
        
        this.renderLessonSteps();
        this.closeModal();
        this.showNotification('教学环节已更新', 'success');
    },
    
    // 删除教学环节
    deleteLessonStep(stepId) {
        if (confirm('确定要删除这个教学环节吗？')) {
            this.lessonSteps = this.lessonSteps.filter(s => s.id != stepId);
            this.renderLessonSteps();
            this.showNotification('教学环节已删除', 'success');
        }
    },
    
    // 预览资源
    previewResource(resourceId) {
        const resource = this.resources.find(r => r.id == resourceId);
        if (!resource) return;
        
        this.showModal('资源预览', `
            <div class="resource-preview">
                <div class="preview-header">
                    <div class="resource-icon large">
                        <i class="${resource.icon}"></i>
                    </div>
                    <div class="resource-details">
                        <h3>${resource.title}</h3>
                        <p>${resource.description}</p>
                        <div class="resource-meta">
                            <span class="resource-type">${resource.type}</span>
                            <span class="resource-size">${resource.size}</span>
                        </div>
                    </div>
                </div>
                <div class="preview-content">
                    <p>这里是资源预览内容...</p>
                    <div class="preview-placeholder">
                        <i class="fas fa-file-alt" style="font-size: 4rem; color: #ddd;"></i>
                        <p>预览功能开发中</p>
                    </div>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="LessonPrep.closeModal()">关闭</button>
                    <button type="button" class="btn btn-primary download-resource-btn" data-resource-id="${resource.id}">下载资源</button>
                </div>
            </div>
        `);
    },
    
    // 下载资源
    downloadResource(resourceId) {
        const resource = this.resources.find(r => r.id == resourceId);
        if (!resource) return;
        
        // 模拟下载过程
        this.showNotification(`正在下载 ${resource.title}...`, 'info');
        
        setTimeout(() => {
            this.showNotification(`${resource.title} 下载完成`, 'success');
        }, 2000);
    },
    
    // 导出结果
    exportResults() {
        this.showLoadingOverlay('正在生成导出文件...');
        
        setTimeout(() => {
            this.hideLoadingOverlay();
            this.showNotification('分析结果已导出', 'success');
        }, 2000);
    },
    
    // 显示模态框
    showModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="LessonPrep.closeModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 添加点击外部关闭功能
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });
    },
    
    // 关闭模态框
    closeModal() {
        const modal = document.querySelector('.modal-overlay');
        if (modal) {
            modal.remove();
        }
    },
    
    // 显示加载覆盖层
    showLoadingOverlay(message = '加载中...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i>
                </div>
                <p>${message}</p>
            </div>
        `;
        
        document.body.appendChild(overlay);
    },
    
    // 隐藏加载覆盖层
    hideLoadingOverlay() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    },
    
    // 显示通知
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="${icons[type]}"></i>
            <span>${message}</span>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // 自动关闭
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
        
        // 点击关闭
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        });
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    LessonPrep.init();
});