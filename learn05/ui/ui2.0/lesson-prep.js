// 备课助手模块交互逻辑

class LessonPrepModule {
    constructor() {
        this.currentTab = 'material-analysis';
        this.uploadedFiles = [];
        this.analysisResults = null;
        this.init();
    }

    init() {
        this.initTabSwitching();
        this.initFileUpload();
        this.initAnalysisTabs();
        this.initTimelineInteractions();
        this.initFormHandlers();
        this.initFilterHandlers();
        this.loadMockData();
    }

    // 标签页切换
    initTabSwitching() {
        const tabItems = document.querySelectorAll('.tab-item');
        const tabPanes = document.querySelectorAll('.tab-pane');

        tabItems.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.dataset.tab;
                
                // 更新标签状态
                tabItems.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // 更新内容显示
                tabPanes.forEach(pane => {
                    pane.classList.remove('active');
                    if (pane.id === targetTab) {
                        pane.classList.add('active');
                    }
                });
                
                this.currentTab = targetTab;
                this.onTabChange(targetTab);
            });
        });
    }

    // 文件上传功能
    initFileUpload() {
        const uploadArea = document.querySelector('.upload-area');
        const fileInput = document.querySelector('.file-input');
        const fileList = document.querySelector('.file-list');

        if (!uploadArea || !fileInput) return;

        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files);
            this.handleFileUpload(files);
        });

        // 点击上传
        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFileUpload(files);
        });
    }

    // 处理文件上传
    handleFileUpload(files) {
        files.forEach(file => {
            if (this.validateFile(file)) {
                const fileData = {
                    id: Date.now() + Math.random(),
                    name: file.name,
                    size: this.formatFileSize(file.size),
                    type: file.type,
                    file: file,
                    uploadTime: new Date()
                };
                
                this.uploadedFiles.push(fileData);
                this.renderFileItem(fileData);
                this.startAnalysis(fileData);
            }
        });
        
        this.updateUploadedFilesDisplay();
    }

    // 验证文件
    validateFile(file) {
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'image/jpeg',
            'image/png'
        ];
        
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        if (!allowedTypes.includes(file.type)) {
            this.showNotification('不支持的文件类型', 'error');
            return false;
        }
        
        if (file.size > maxSize) {
            this.showNotification('文件大小不能超过10MB', 'error');
            return false;
        }
        
        return true;
    }

    // 格式化文件大小
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // 渲染文件项
    renderFileItem(fileData) {
        const fileList = document.querySelector('.file-list');
        if (!fileList) return;

        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-icon">
                <i class="fas ${this.getFileIcon(fileData.type)}"></i>
            </div>
            <div class="file-info">
                <p class="file-name">${fileData.name}</p>
                <p class="file-size">${fileData.size}</p>
            </div>
            <div class="file-actions">
                <button class="btn btn-sm btn-outline" onclick="lessonPrep.previewFile('${fileData.id}')">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline btn-danger" onclick="lessonPrep.removeFile('${fileData.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        fileList.appendChild(fileItem);
    }

    // 获取文件图标
    getFileIcon(fileType) {
        const iconMap = {
            'application/pdf': 'fa-file-pdf',
            'application/msword': 'fa-file-word',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'fa-file-word',
            'text/plain': 'fa-file-alt',
            'image/jpeg': 'fa-file-image',
            'image/png': 'fa-file-image'
        };
        
        return iconMap[fileType] || 'fa-file';
    }

    // 开始AI分析
    startAnalysis(fileData) {
        this.showAnalysisProgress();
        
        // 模拟AI分析过程
        setTimeout(() => {
            this.completeAnalysis(fileData);
        }, 2000 + Math.random() * 3000);
    }

    // 显示分析进度
    showAnalysisProgress() {
        const analysisResults = document.querySelector('.analysis-results');
        if (!analysisResults) return;

        analysisResults.innerHTML = `
            <div class="analysis-status">
                <div class="status-badge">
                    <i class="fas fa-spinner fa-spin"></i>
                    AI正在分析中...
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
        `;
        
        // 模拟进度条
        const progressFill = analysisResults.querySelector('.progress-fill');
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            progressFill.style.width = progress + '%';
        }, 200);
    }

    // 完成分析
    completeAnalysis(fileData) {
        this.analysisResults = this.generateMockAnalysis(fileData);
        this.renderAnalysisResults();
        this.showNotification('AI分析完成', 'success');
    }

    // 生成模拟分析结果
    generateMockAnalysis(fileData) {
        return {
            summary: {
                title: '细胞的结构与功能',
                description: '本章节主要介绍细胞的基本结构，包括细胞膜、细胞质、细胞核等组成部分，以及各部分的功能特点。通过学习，学生将理解细胞作为生命活动基本单位的重要性。',
                concepts: ['细胞膜', '细胞质', '细胞核', '细胞壁', '叶绿体', '线粒体']
            },
            structure: {
                root: '细胞的结构与功能',
                children: [
                    {
                        title: '细胞膜',
                        children: ['膜的结构', '膜的功能', '物质运输']
                    },
                    {
                        title: '细胞质',
                        children: ['细胞质基质', '细胞器', '细胞骨架']
                    },
                    {
                        title: '细胞核',
                        children: ['核膜', '核质', '染色体']
                    }
                ]
            },
            difficulties: [
                {
                    level: 'high',
                    title: '细胞膜的选择透过性',
                    description: '学生难以理解细胞膜如何选择性地允许某些物质通过而阻止其他物质',
                    suggestions: ['实验演示', '动画展示', '类比教学']
                },
                {
                    level: 'medium',
                    title: '细胞器的功能区分',
                    description: '各种细胞器的功能容易混淆，需要重点区分',
                    suggestions: ['对比表格', '功能归类', '记忆口诀']
                }
            ],
            objectives: {
                knowledge: [
                    '掌握细胞的基本结构组成',
                    '理解各细胞器的主要功能',
                    '认识细胞膜的结构特点'
                ],
                ability: [
                    '能够识别细胞结构图中的各个组成部分',
                    '能够分析细胞结构与功能的关系',
                    '培养观察和分析能力'
                ],
                emotion: [
                    '感受生命的奇妙和复杂',
                    '培养科学探究的兴趣',
                    '树立正确的生命观'
                ]
            }
        };
    }

    // 渲染分析结果
    renderAnalysisResults() {
        const analysisResults = document.querySelector('.analysis-results');
        if (!analysisResults || !this.analysisResults) return;

        analysisResults.innerHTML = `
            <div class="analysis-status">
                <div class="status-badge status-success">
                    <i class="fas fa-check"></i>
                    分析完成
                </div>
            </div>
            <div class="analysis-tabs">
                <div class="mini-tabs">
                    <button class="mini-tab active" data-panel="summary">内容概要</button>
                    <button class="mini-tab" data-panel="structure">知识结构</button>
                    <button class="mini-tab" data-panel="difficulties">难点分析</button>
                    <button class="mini-tab" data-panel="objectives">教学目标</button>
                </div>
                <div class="analysis-content">
                    ${this.renderAnalysisPanels()}
                </div>
            </div>
        `;
        
        this.initAnalysisTabs();
    }

    // 渲染分析面板
    renderAnalysisPanels() {
        const { summary, structure, difficulties, objectives } = this.analysisResults;
        
        return `
            <div class="analysis-panel active" id="summary">
                <div class="content-summary">
                    <h4>${summary.title}</h4>
                    <p>${summary.description}</p>
                    <div class="concept-tags">
                        ${summary.concepts.map(concept => `<span class="concept-tag">${concept}</span>`).join('')}
                    </div>
                </div>
            </div>
            
            <div class="analysis-panel" id="structure">
                <div class="knowledge-tree">
                    <div class="tree-node root">
                        <div class="node-title">${structure.root}</div>
                        <div class="tree-children">
                            ${structure.children.map(child => `
                                <div class="tree-node">
                                    <div class="node-title">${child.title}</div>
                                    <div class="tree-children">
                                        ${child.children.map(subChild => `
                                            <div class="tree-node leaf">
                                                <div class="node-title">${subChild}</div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="analysis-panel" id="difficulties">
                <div class="difficulty-items">
                    ${difficulties.map(item => `
                        <div class="difficulty-item ${item.level}">
                            <div class="difficulty-header">
                                <span class="difficulty-level">${item.level}</span>
                                <span class="difficulty-title">${item.title}</span>
                            </div>
                            <p class="difficulty-desc">${item.description}</p>
                            <div class="difficulty-suggestions">
                                ${item.suggestions.map(suggestion => `<span class="suggestion-tag">${suggestion}</span>`).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="analysis-panel" id="objectives">
                <div class="objectives-list">
                    <div class="objective-item">
                        <div class="objective-type">知识目标</div>
                        <ul>
                            ${objectives.knowledge.map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="objective-item">
                        <div class="objective-type">能力目标</div>
                        <ul>
                            ${objectives.ability.map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="objective-item">
                        <div class="objective-type">情感目标</div>
                        <ul>
                            ${objectives.emotion.map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    // 初始化分析标签页
    initAnalysisTabs() {
        const miniTabs = document.querySelectorAll('.mini-tab');
        const analysisPanels = document.querySelectorAll('.analysis-panel');

        miniTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetPanel = tab.dataset.panel;
                
                // 更新标签状态
                miniTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // 更新面板显示
                analysisPanels.forEach(panel => {
                    panel.classList.remove('active');
                    if (panel.id === targetPanel) {
                        panel.classList.add('active');
                    }
                });
            });
        });
    }

    // 初始化时间轴交互
    initTimelineInteractions() {
        // 添加时间轴项目的交互功能
        document.addEventListener('click', (e) => {
            if (e.target.closest('.timeline-actions .btn-edit')) {
                const timelineItem = e.target.closest('.timeline-item');
                this.editTimelineItem(timelineItem);
            }
            
            if (e.target.closest('.timeline-actions .btn-delete')) {
                const timelineItem = e.target.closest('.timeline-item');
                this.deleteTimelineItem(timelineItem);
            }
        });
    }

    // 初始化表单处理
    initFormHandlers() {
        // 教学方法标签选择
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('method-tag')) {
                e.target.classList.toggle('active');
            }
            
            if (e.target.classList.contains('popular-tag')) {
                e.target.classList.toggle('active');
            }
        });
        
        // 复选框和单选框处理
        document.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox' || e.target.type === 'radio') {
                this.updateFormData();
            }
        });
    }

    // 初始化筛选处理
    initFilterHandlers() {
        const filterInputs = document.querySelectorAll('.recommendation-filters input');
        filterInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.applyFilters();
            });
        });
    }

    // 应用筛选
    applyFilters() {
        const filters = this.getActiveFilters();
        this.filterCases(filters);
    }

    // 获取激活的筛选条件
    getActiveFilters() {
        const filters = {};
        
        // 获取学科筛选
        const subjectFilter = document.querySelector('input[name="subject"]:checked');
        if (subjectFilter) {
            filters.subject = subjectFilter.value;
        }
        
        // 获取年级筛选
        const gradeFilter = document.querySelector('input[name="grade"]:checked');
        if (gradeFilter) {
            filters.grade = gradeFilter.value;
        }
        
        // 获取类型筛选
        const typeFilter = document.querySelector('input[name="type"]:checked');
        if (typeFilter) {
            filters.type = typeFilter.value;
        }
        
        return filters;
    }

    // 筛选案例
    filterCases(filters) {
        const caseItems = document.querySelectorAll('.case-item');
        
        caseItems.forEach(item => {
            let shouldShow = true;
            
            // 这里可以根据实际的筛选逻辑来判断
            // 目前只是示例实现
            
            if (shouldShow) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    // 标签页切换回调
    onTabChange(tabId) {
        switch (tabId) {
            case 'material-analysis':
                this.loadMaterialAnalysis();
                break;
            case 'lesson-planning':
                this.loadLessonPlanning();
                break;
            case 'student-analysis':
                this.loadStudentAnalysis();
                break;
            case 'case-recommendation':
                this.loadCaseRecommendation();
                break;
        }
    }

    // 加载教材分析
    loadMaterialAnalysis() {
        // 如果已有分析结果，直接显示
        if (this.analysisResults) {
            this.renderAnalysisResults();
        }
    }

    // 加载教学策划
    loadLessonPlanning() {
        this.loadTimelineData();
    }

    // 加载学情分析
    loadStudentAnalysis() {
        this.loadStudentData();
    }

    // 加载案例推荐
    loadCaseRecommendation() {
        this.loadRecommendationData();
    }

    // 加载时间轴数据
    loadTimelineData() {
        // 模拟加载教学流程数据
        const timelineData = [
            {
                title: '课程导入',
                duration: '5分钟',
                description: '通过生活实例引入细胞概念，激发学生学习兴趣',
                method: '情境导入',
                materials: '多媒体课件',
                objectives: '激发兴趣，引入主题'
            },
            {
                title: '新课讲授',
                duration: '25分钟',
                description: '系统讲解细胞的基本结构，重点突出各部分功能',
                method: '讲授法+演示法',
                materials: '显微镜，细胞模型',
                objectives: '掌握细胞结构知识'
            },
            {
                title: '实践探究',
                duration: '10分钟',
                description: '学生分组观察细胞切片，记录观察结果',
                method: '实验法+合作学习',
                materials: '显微镜，细胞切片',
                objectives: '培养观察能力'
            },
            {
                title: '总结反思',
                duration: '5分钟',
                description: '总结本节课重点内容，布置课后作业',
                method: '总结法',
                materials: '板书',
                objectives: '巩固知识，拓展思维'
            }
        ];
        
        this.renderTimeline(timelineData);
    }

    // 渲染时间轴
    renderTimeline(data) {
        const timeline = document.querySelector('.lesson-timeline');
        if (!timeline) return;
        
        timeline.innerHTML = data.map((item, index) => `
            <div class="timeline-item">
                <div class="timeline-marker">
                    <span class="timeline-number">${index + 1}</span>
                </div>
                <div class="timeline-content">
                    <div class="timeline-header">
                        <h4 class="timeline-title">${item.title}</h4>
                        <span class="timeline-duration">${item.duration}</span>
                    </div>
                    <p class="timeline-description">${item.description}</p>
                    <div class="timeline-details">
                        <div class="detail-item">
                            <span class="detail-label">教学方法:</span>
                            <span class="detail-value">${item.method}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">教学材料:</span>
                            <span class="detail-value">${item.materials}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">教学目标:</span>
                            <span class="detail-value">${item.objectives}</span>
                        </div>
                    </div>
                    <div class="timeline-actions">
                        <button class="btn btn-sm btn-outline btn-edit">
                            <i class="fas fa-edit"></i> 编辑
                        </button>
                        <button class="btn btn-sm btn-outline btn-danger btn-delete">
                            <i class="fas fa-trash"></i> 删除
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // 加载学生数据
    loadStudentData() {
        const abilityData = [
            { name: '理解能力', score: 85, level: 'good' },
            { name: '记忆能力', score: 72, level: 'average' },
            { name: '分析能力', score: 68, level: 'average' },
            { name: '实验能力', score: 55, level: 'poor' },
            { name: '表达能力', score: 78, level: 'good' }
        ];
        
        this.renderAbilityAnalysis(abilityData);
        this.loadDifficultyPredictions();
        this.loadPersonalizedSuggestions();
    }

    // 渲染能力分析
    renderAbilityAnalysis(data) {
        const container = document.querySelector('.ability-analysis');
        if (!container) return;
        
        container.innerHTML = data.map(item => `
            <div class="ability-item">
                <div class="ability-header">
                    <span class="ability-name">${item.name}</span>
                    <span class="ability-score ${item.level}">${item.score}分</span>
                </div>
                <div class="ability-bar">
                    <div class="ability-fill ${item.level}" style="width: ${item.score}%"></div>
                </div>
                <p class="ability-desc">${this.getAbilityDescription(item.level)}</p>
            </div>
        `).join('');
    }

    // 获取能力描述
    getAbilityDescription(level) {
        const descriptions = {
            good: '表现良好，可以适当增加挑战性内容',
            average: '表现一般，需要针对性指导和练习',
            poor: '需要重点关注，建议增加基础训练'
        };
        return descriptions[level] || '';
    }

    // 加载困难预测
    loadDifficultyPredictions() {
        const predictions = [
            {
                level: 'high-risk',
                title: '细胞膜透过性理解困难',
                description: '基于历史数据分析，约65%的学生在理解细胞膜选择透过性方面存在困难',
                suggestions: ['增加实验演示', '使用类比教学', '提供更多练习']
            },
            {
                level: 'medium-risk',
                title: '细胞器功能记忆混淆',
                description: '约40%的学生容易混淆不同细胞器的功能',
                suggestions: ['制作对比表格', '使用记忆口诀', '增加复习频次']
            }
        ];
        
        this.renderDifficultyPredictions(predictions);
    }

    // 渲染困难预测
    renderDifficultyPredictions(data) {
        const container = document.querySelector('.difficulty-predictions');
        if (!container) return;
        
        container.innerHTML = data.map(item => `
            <div class="prediction-item ${item.level}">
                <div class="prediction-header">
                    <span class="risk-level">${item.level.replace('-', ' ')}</span>
                    <span class="prediction-title">${item.title}</span>
                </div>
                <div class="prediction-details">
                    <p>${item.description}</p>
                    <div class="prediction-suggestions">
                        ${item.suggestions.map(suggestion => `<span class="suggestion-tag">${suggestion}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');
    }

    // 加载个性化建议
    loadPersonalizedSuggestions() {
        const suggestions = [
            {
                category: '教学策略建议',
                content: '建议采用多元化教学方法，结合实验、讨论、演示等多种形式，照顾不同学习风格的学生',
                actions: ['实验教学', '小组讨论', '多媒体演示', '个别辅导']
            },
            {
                category: '重点关注学生',
                content: '张三、李四在生物学科基础较弱，建议课后单独辅导，提供额外的练习材料',
                actions: ['课后辅导', '基础练习', '家长沟通', '学习计划']
            },
            {
                category: '课堂互动建议',
                content: '增加课堂提问和互动环节，鼓励学生主动参与，提高课堂活跃度',
                actions: ['随机提问', '小组竞赛', '角色扮演', '实时反馈']
            }
        ];
        
        this.renderPersonalizedSuggestions(suggestions);
    }

    // 渲染个性化建议
    renderPersonalizedSuggestions(data) {
        const container = document.querySelector('.personalized-suggestions');
        if (!container) return;
        
        container.innerHTML = data.map(item => `
            <div class="suggestion-category">
                <h4 class="category-title">${item.category}</h4>
                <div class="category-content">
                    <p>${item.content}</p>
                    <div class="suggestion-actions">
                        ${item.actions.map(action => `<span class="action-tag">${action}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');
    }

    // 加载推荐数据
    loadRecommendationData() {
        const cases = [
            {
                id: 1,
                title: '细胞结构观察实验设计',
                author: '王老师',
                rating: 4.8,
                description: '通过显微镜观察不同类型细胞，让学生直观了解细胞结构差异，配合详细的实验指导和观察记录表',
                tags: ['实验教学', '观察法', '高中生物', '细胞结构'],
                featured: true
            },
            {
                id: 2,
                title: '细胞膜透过性探究活动',
                author: '李老师',
                rating: 4.6,
                description: '设计多个小实验验证细胞膜的选择透过性，包括渗透实验、扩散实验等，帮助学生理解抽象概念',
                tags: ['探究学习', '实验设计', '概念理解', '细胞膜'],
                featured: false
            },
            {
                id: 3,
                title: '细胞器功能类比教学法',
                author: '张老师',
                rating: 4.7,
                description: '将细胞比作工厂，各个细胞器比作不同的车间和设备，通过生动的类比帮助学生记忆和理解',
                tags: ['类比教学', '记忆方法', '概念建构', '细胞器'],
                featured: false
            }
        ];
        
        this.renderCaseList(cases);
    }

    // 渲染案例列表
    renderCaseList(cases) {
        const container = document.querySelector('.case-list');
        if (!container) return;
        
        container.innerHTML = cases.map(caseItem => `
            <div class="case-item ${caseItem.featured ? 'featured' : ''}">
                <div class="case-header">
                    <h4 class="case-title">${caseItem.title}</h4>
                    <div class="case-meta">
                        <div class="case-rating">
                            <i class="fas fa-star"></i>
                            <span>${caseItem.rating}</span>
                        </div>
                        <div class="case-author">by ${caseItem.author}</div>
                    </div>
                </div>
                <p class="case-description">${caseItem.description}</p>
                <div class="case-tags">
                    ${caseItem.tags.map(tag => `<span class="case-tag">${tag}</span>`).join('')}
                </div>
                <div class="case-actions">
                    <button class="btn btn-sm btn-outline" onclick="lessonPrep.previewCase(${caseItem.id})">
                        <i class="fas fa-eye"></i> 预览
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="lessonPrep.useCase(${caseItem.id})">
                        <i class="fas fa-download"></i> 使用
                    </button>
                </div>
            </div>
        `).join('');
    }

    // 加载模拟数据
    loadMockData() {
        // 加载侧边栏数据
        this.loadSidebarData();
    }

    // 加载侧边栏数据
    loadSidebarData() {
        // AI建议
        const suggestions = [
            {
                icon: 'fa-lightbulb',
                title: '教学建议',
                content: '建议增加互动环节提高学生参与度'
            },
            {
                icon: 'fa-clock',
                title: '时间分配',
                content: '当前设计可能时间偏紧，建议调整'
            },
            {
                icon: 'fa-users',
                title: '学生特点',
                content: '注意照顾不同层次学生的需求'
            }
        ];
        
        this.renderAISuggestions(suggestions);
        
        // 相关资源
        const resources = [
            {
                icon: 'fa-file-pdf',
                name: '细胞结构图解.pdf',
                meta: '2.3MB · 昨天'
            },
            {
                icon: 'fa-video',
                name: '细胞分裂动画.mp4',
                meta: '15.6MB · 3天前'
            },
            {
                icon: 'fa-image',
                name: '显微镜使用图片',
                meta: '1.2MB · 1周前'
            }
        ];
        
        this.renderRelatedResources(resources);
    }

    // 渲染AI建议
    renderAISuggestions(suggestions) {
        const container = document.querySelector('.ai-suggestions');
        if (!container) return;
        
        container.innerHTML = suggestions.map(item => `
            <div class="suggestion-item">
                <div class="suggestion-icon">
                    <i class="fas ${item.icon}"></i>
                </div>
                <div class="suggestion-content">
                    <h4>${item.title}</h4>
                    <p>${item.content}</p>
                </div>
            </div>
        `).join('');
    }

    // 渲染相关资源
    renderRelatedResources(resources) {
        const container = document.querySelector('.resource-list');
        if (!container) return;
        
        container.innerHTML = resources.map(item => `
            <div class="resource-item">
                <div class="resource-icon">
                    <i class="fas ${item.icon}"></i>
                </div>
                <div class="resource-info">
                    <p class="resource-name">${item.name}</p>
                    <p class="resource-meta">${item.meta}</p>
                </div>
            </div>
        `).join('');
    }

    // 工具方法
    previewFile(fileId) {
        const file = this.uploadedFiles.find(f => f.id == fileId);
        if (file) {
            this.showNotification(`预览文件: ${file.name}`, 'info');
            // 这里可以实现文件预览功能
        }
    }

    removeFile(fileId) {
        this.uploadedFiles = this.uploadedFiles.filter(f => f.id != fileId);
        this.updateUploadedFilesDisplay();
        this.showNotification('文件已删除', 'success');
    }

    previewCase(caseId) {
        this.showNotification(`预览案例: ${caseId}`, 'info');
        // 这里可以实现案例预览功能
    }

    useCase(caseId) {
        this.showNotification(`使用案例: ${caseId}`, 'success');
        // 这里可以实现案例使用功能
    }

    editTimelineItem(item) {
        this.showNotification('编辑时间轴项目', 'info');
        // 这里可以实现编辑功能
    }

    deleteTimelineItem(item) {
        if (confirm('确定要删除这个教学环节吗？')) {
            item.remove();
            this.showNotification('教学环节已删除', 'success');
        }
    }

    updateUploadedFilesDisplay() {
        const uploadedFiles = document.querySelector('.uploaded-files');
        if (!uploadedFiles) return;
        
        if (this.uploadedFiles.length === 0) {
            uploadedFiles.style.display = 'none';
        } else {
            uploadedFiles.style.display = 'block';
        }
    }

    updateFormData() {
        // 更新表单数据
        console.log('Form data updated');
    }

    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 自动关闭
        setTimeout(() => {
            notification.remove();
        }, 3000);
        
        // 点击关闭
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }
}

// 初始化备课助手模块
let lessonPrep;
document.addEventListener('DOMContentLoaded', () => {
    lessonPrep = new LessonPrepModule();
});

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LessonPrepModule;
}