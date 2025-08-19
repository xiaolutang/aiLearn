/**
 * 课堂AI助手模块 JavaScript
 * 实现课堂AI助手的各种交互功能
 */

class ClassroomAIModule {
    constructor() {
        this.currentTab = 'realtime-analysis';
        this.realtimeData = {
            students: [],
            metrics: {
                onlineStudents: 32,
                attentionRate: 78,
                participationRate: 85,
                comprehensionRate: 72
            },
            chartData: []
        };
        this.runningApps = new Map();
        this.experimentData = {
            steps: [],
            materials: []
        };
        this.whiteboardContext = null;
        this.isDrawing = false;
        this.currentTool = 'pen';
        
        this.init();
    }

    init() {
        this.initTabs();
        this.initRealtimeAnalysis();
        this.initExperimentDesigner();
        this.initAIApplications();
        this.initInteractionTools();
        this.loadMockData();
        this.startRealtimeUpdates();
    }

    // 初始化标签页
    initTabs() {
        const tabItems = document.querySelectorAll('.tab-item');
        const tabPanes = document.querySelectorAll('.tab-pane');

        tabItems.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.dataset.tab;
                this.switchTab(targetTab);
            });
        });
    }

    // 切换标签页
    switchTab(tabId) {
        // 更新标签状态
        document.querySelectorAll('.tab-item').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

        // 更新内容面板
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');

        this.currentTab = tabId;
        this.onTabChanged(tabId);
    }

    // 标签页切换回调
    onTabChanged(tabId) {
        switch(tabId) {
            case 'realtime-analysis':
                this.refreshRealtimeData();
                break;
            case 'experiment-assistant':
                this.refreshExperimentData();
                break;
            case 'ai-applications':
                this.refreshAIApps();
                break;
            case 'interaction-tools':
                this.refreshInteractionTools();
                break;
        }
    }

    // 初始化实时学情分析
    initRealtimeAnalysis() {
        // 初始化筛选标签
        const filterTabs = document.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                filterTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.filterStudents(tab.dataset.filter);
            });
        });

        // 初始化快速操作
        const quickActions = document.querySelectorAll('.quick-actions-vertical .btn');
        quickActions.forEach(btn => {
            btn.addEventListener('click', () => {
                this.handleQuickAction(btn);
            });
        });
    }

    // 筛选学生
    filterStudents(filter) {
        const students = this.realtimeData.students;
        let filteredStudents = students;

        switch(filter) {
            case 'attention':
                filteredStudents = students.filter(s => s.needsAttention);
                break;
            case 'active':
                filteredStudents = students.filter(s => s.isActive);
                break;
            case 'confused':
                filteredStudents = students.filter(s => s.isConfused);
                break;
            default:
                filteredStudents = students;
        }

        this.renderStudentList(filteredStudents);
    }

    // 渲染学生列表
    renderStudentList(students) {
        const container = document.querySelector('.student-list');
        if (!container) return;

        container.innerHTML = students.map(student => `
            <div class="student-item">
                <div class="student-avatar">${student.name.charAt(0)}</div>
                <div class="student-info">
                    <div class="student-name">${student.name}</div>
                    <div class="student-status">${student.status}</div>
                </div>
                <div class="student-metrics">
                    ${student.needsAttention ? '<span class="metric-badge attention">需关注</span>' : ''}
                    ${student.isActive ? '<span class="metric-badge active">活跃</span>' : ''}
                    ${student.isConfused ? '<span class="metric-badge confused">困惑</span>' : ''}
                </div>
            </div>
        `).join('');
    }

    // 处理快速操作
    handleQuickAction(btn) {
        const icon = btn.querySelector('i').className;
        
        if (icon.includes('question-circle')) {
            this.startQuestionSession();
        } else if (icon.includes('poll')) {
            this.createPoll();
        } else if (icon.includes('gamepad')) {
            this.startInteractiveGame();
        } else if (icon.includes('pause')) {
            this.startBreakTime();
        }
    }

    // 开始提问环节
    startQuestionSession() {
        this.showNotification('已开启提问环节，学生可以举手发言', 'success');
    }

    // 创建投票
    createPoll() {
        this.switchTab('interaction-tools');
        setTimeout(() => {
            document.querySelector('.btn-create-poll').click();
        }, 300);
    }

    // 开始互动游戏
    startInteractiveGame() {
        this.switchTab('interaction-tools');
        setTimeout(() => {
            document.querySelector('.btn-start-game').click();
        }, 300);
    }

    // 开始课间休息
    startBreakTime() {
        this.showNotification('课间休息开始，预计10分钟后继续上课', 'info');
    }

    // 初始化实验设计助手
    initExperimentDesigner() {
        // 添加步骤按钮
        const addStepBtn = document.querySelector('.btn-add-step');
        if (addStepBtn) {
            addStepBtn.addEventListener('click', () => {
                this.addExperimentStep();
            });
        }

        // 添加材料按钮
        const addMaterialBtn = document.querySelector('.btn-add-material');
        if (addMaterialBtn) {
            addMaterialBtn.addEventListener('click', () => {
                this.addExperimentMaterial();
            });
        }

        // 实验模板点击
        this.initTemplateSelection();
    }

    // 添加实验步骤
    addExperimentStep() {
        const stepNumber = this.experimentData.steps.length + 1;
        const step = {
            id: `step-${stepNumber}`,
            number: stepNumber,
            title: `步骤 ${stepNumber}`,
            description: '请输入步骤描述...'
        };
        
        this.experimentData.steps.push(step);
        this.renderExperimentSteps();
    }

    // 渲染实验步骤
    renderExperimentSteps() {
        const container = document.querySelector('.experiment-steps');
        if (!container) return;

        container.innerHTML = this.experimentData.steps.map(step => `
            <div class="step-item" data-step-id="${step.id}">
                <div class="step-number">${step.number}</div>
                <div class="step-content">
                    <input type="text" class="step-title form-input" value="${step.title}" placeholder="步骤标题">
                    <textarea class="step-description form-input" placeholder="步骤描述">${step.description}</textarea>
                </div>
                <div class="step-actions">
                    <button class="btn-icon btn-edit-step" title="编辑">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-delete-step" title="删除">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');

        // 绑定步骤操作事件
        this.bindStepEvents();
    }

    // 绑定步骤操作事件
    bindStepEvents() {
        document.querySelectorAll('.btn-delete-step').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const stepItem = e.target.closest('.step-item');
                const stepId = stepItem.dataset.stepId;
                this.deleteExperimentStep(stepId);
            });
        });
    }

    // 删除实验步骤
    deleteExperimentStep(stepId) {
        this.experimentData.steps = this.experimentData.steps.filter(step => step.id !== stepId);
        // 重新编号
        this.experimentData.steps.forEach((step, index) => {
            step.number = index + 1;
        });
        this.renderExperimentSteps();
    }

    // 添加实验材料
    addExperimentMaterial() {
        const material = {
            id: `material-${Date.now()}`,
            name: '新材料',
            quantity: '1个',
            icon: 'fas fa-flask'
        };
        
        this.experimentData.materials.push(material);
        this.renderExperimentMaterials();
    }

    // 渲染实验材料
    renderExperimentMaterials() {
        const container = document.querySelector('.materials-list');
        if (!container) return;

        container.innerHTML = this.experimentData.materials.map(material => `
            <div class="material-item" data-material-id="${material.id}">
                <div class="material-icon">
                    <i class="${material.icon}"></i>
                </div>
                <div class="material-info">
                    <div class="material-name">${material.name}</div>
                    <div class="material-quantity">${material.quantity}</div>
                </div>
                <div class="material-actions">
                    <button class="btn-icon btn-delete-material" title="删除">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');

        // 绑定材料操作事件
        this.bindMaterialEvents();
    }

    // 绑定材料操作事件
    bindMaterialEvents() {
        document.querySelectorAll('.btn-delete-material').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const materialItem = e.target.closest('.material-item');
                const materialId = materialItem.dataset.materialId;
                this.deleteExperimentMaterial(materialId);
            });
        });
    }

    // 删除实验材料
    deleteExperimentMaterial(materialId) {
        this.experimentData.materials = this.experimentData.materials.filter(material => material.id !== materialId);
        this.renderExperimentMaterials();
    }

    // 初始化模板选择
    initTemplateSelection() {
        // 模拟模板数据
        const templates = [
            { id: 1, title: '观察植物细胞', description: '使用显微镜观察洋葱表皮细胞结构' },
            { id: 2, title: '酸碱指示剂实验', description: '使用紫甘蓝汁液检测不同溶液的酸碱性' },
            { id: 3, title: '种子萌发实验', description: '观察不同条件下种子的萌发情况' }
        ];

        this.renderTemplateList(templates);
    }

    // 渲染模板列表
    renderTemplateList(templates) {
        const container = document.querySelector('.template-list');
        if (!container) return;

        container.innerHTML = templates.map(template => `
            <div class="template-item" data-template-id="${template.id}">
                <div class="template-title">${template.title}</div>
                <div class="template-description">${template.description}</div>
            </div>
        `).join('');

        // 绑定模板点击事件
        document.querySelectorAll('.template-item').forEach(item => {
            item.addEventListener('click', () => {
                const templateId = item.dataset.templateId;
                this.loadExperimentTemplate(templateId);
            });
        });
    }

    // 加载实验模板
    loadExperimentTemplate(templateId) {
        // 模拟加载模板数据
        const templateData = {
            1: {
                name: '观察植物细胞',
                type: '观察实验',
                duration: 45,
                difficulty: '简单',
                steps: [
                    { title: '准备材料', description: '准备洋葱、显微镜、载玻片等' },
                    { title: '制作标本', description: '撕取洋葱内表皮，制作临时装片' },
                    { title: '显微观察', description: '使用显微镜观察细胞结构' }
                ],
                materials: [
                    { name: '洋葱', quantity: '1个', icon: 'fas fa-seedling' },
                    { name: '显微镜', quantity: '1台', icon: 'fas fa-microscope' },
                    { name: '载玻片', quantity: '2片', icon: 'fas fa-square' }
                ]
            }
        };

        const template = templateData[templateId];
        if (template) {
            // 填充表单
            document.querySelector('input[placeholder="请输入实验名称"]').value = template.name;
            
            // 加载步骤和材料
            this.experimentData.steps = template.steps.map((step, index) => ({
                id: `step-${index + 1}`,
                number: index + 1,
                title: step.title,
                description: step.description
            }));
            
            this.experimentData.materials = template.materials.map((material, index) => ({
                id: `material-${index + 1}`,
                name: material.name,
                quantity: material.quantity,
                icon: material.icon
            }));
            
            this.renderExperimentSteps();
            this.renderExperimentMaterials();
            
            this.showNotification(`已加载模板：${template.name}`, 'success');
        }
    }

    // 初始化AI应用
    initAIApplications() {
        // 绑定应用启动按钮
        document.querySelectorAll('.btn-launch-app').forEach(btn => {
            btn.addEventListener('click', () => {
                const appType = btn.dataset.app;
                this.launchAIApp(appType);
            });
        });
    }

    // 启动AI应用
    launchAIApp(appType) {
        const appConfig = {
            'qa-assistant': {
                name: '智能问答助手',
                icon: 'fas fa-comments',
                interface: this.createQAInterface()
            },
            'smart-board': {
                name: '智能板书系统',
                icon: 'fas fa-chalkboard',
                interface: this.createSmartBoardInterface()
            },
            'voice-assistant': {
                name: '语音教学助手',
                icon: 'fas fa-microphone',
                interface: this.createVoiceInterface()
            },
            'image-recognition': {
                name: '图像识别分析',
                icon: 'fas fa-camera',
                interface: this.createImageRecognitionInterface()
            },
            'personalization': {
                name: '个性化推荐',
                icon: 'fas fa-user-cog',
                interface: this.createPersonalizationInterface()
            },
            'emotion-analysis': {
                name: '情感状态分析',
                icon: 'fas fa-heart',
                interface: this.createEmotionAnalysisInterface()
            }
        };

        const app = appConfig[appType];
        if (app) {
            this.showAIAppModal(app);
            this.addRunningApp(appType, app);
        }
    }

    // 显示AI应用模态框
    showAIAppModal(app) {
        const modal = document.getElementById('ai-app-modal');
        const title = modal.querySelector('.modal-title');
        const body = modal.querySelector('.ai-app-interface');
        
        title.textContent = app.name;
        body.innerHTML = app.interface;
        
        modal.style.display = 'flex';
        
        // 绑定关闭事件
        modal.querySelector('.modal-close').onclick = () => {
            modal.style.display = 'none';
        };
        
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        };
    }

    // 添加运行中的应用
    addRunningApp(appType, app) {
        this.runningApps.set(appType, {
            ...app,
            startTime: new Date(),
            status: '运行中'
        });
        
        this.renderRunningApps();
    }

    // 渲染运行中的应用
    renderRunningApps() {
        const container = document.querySelector('.running-apps');
        if (!container) return;

        const apps = Array.from(this.runningApps.entries());
        
        container.innerHTML = apps.map(([appType, app]) => `
            <div class="running-app-item">
                <div class="running-app-icon">
                    <i class="${app.icon}"></i>
                </div>
                <div class="running-app-info">
                    <div class="running-app-name">${app.name}</div>
                    <div class="running-app-status">${app.status}</div>
                </div>
                <button class="btn-icon btn-stop-app" data-app="${appType}" title="停止">
                    <i class="fas fa-stop"></i>
                </button>
            </div>
        `).join('');

        // 绑定停止按钮事件
        document.querySelectorAll('.btn-stop-app').forEach(btn => {
            btn.addEventListener('click', () => {
                const appType = btn.dataset.app;
                this.stopAIApp(appType);
            });
        });
    }

    // 停止AI应用
    stopAIApp(appType) {
        this.runningApps.delete(appType);
        this.renderRunningApps();
        this.showNotification('AI应用已停止', 'info');
    }

    // 创建各种AI应用界面
    createQAInterface() {
        return `
            <div class="qa-interface">
                <div class="qa-chat-area">
                    <div class="chat-messages">
                        <div class="message ai-message">
                            <div class="message-content">您好！我是智能问答助手，有什么问题可以问我。</div>
                        </div>
                    </div>
                    <div class="chat-input-area">
                        <input type="text" class="chat-input" placeholder="输入您的问题...">
                        <button class="btn btn-primary">发送</button>
                    </div>
                </div>
            </div>
        `;
    }

    createSmartBoardInterface() {
        return `
            <div class="smart-board-interface">
                <div class="board-tools">
                    <button class="tool-btn active">画笔</button>
                    <button class="tool-btn">文字</button>
                    <button class="tool-btn">图形</button>
                    <button class="tool-btn">清除</button>
                </div>
                <div class="board-canvas">
                    <canvas width="600" height="400" style="border: 1px solid #ddd;"></canvas>
                </div>
            </div>
        `;
    }

    createVoiceInterface() {
        return `
            <div class="voice-interface">
                <div class="voice-controls">
                    <button class="btn btn-primary btn-voice-record">
                        <i class="fas fa-microphone"></i>
                        开始录音
                    </button>
                    <button class="btn btn-outline btn-voice-play">
                        <i class="fas fa-play"></i>
                        播放
                    </button>
                </div>
                <div class="voice-status">
                    <div class="status-text">点击开始录音按钮开始语音交互</div>
                </div>
            </div>
        `;
    }

    createImageRecognitionInterface() {
        return `
            <div class="image-recognition-interface">
                <div class="upload-area">
                    <div class="upload-placeholder">
                        <i class="fas fa-camera fa-3x"></i>
                        <p>点击上传图片或拖拽图片到此处</p>
                        <input type="file" accept="image/*" style="display: none;">
                    </div>
                </div>
                <div class="recognition-results">
                    <h4>识别结果</h4>
                    <div class="results-content">暂无识别结果</div>
                </div>
            </div>
        `;
    }

    createPersonalizationInterface() {
        return `
            <div class="personalization-interface">
                <div class="student-selector">
                    <select class="form-select">
                        <option>选择学生</option>
                        <option>张三</option>
                        <option>李四</option>
                        <option>王五</option>
                    </select>
                </div>
                <div class="recommendations">
                    <h4>个性化推荐</h4>
                    <div class="recommendation-list">
                        <div class="recommendation-item">
                            <h5>学习内容推荐</h5>
                            <p>基于学习进度，建议加强细胞结构相关知识点</p>
                        </div>
                        <div class="recommendation-item">
                            <h5>学习方法推荐</h5>
                            <p>建议使用图像记忆法学习生物分类</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createEmotionAnalysisInterface() {
        return `
            <div class="emotion-analysis-interface">
                <div class="emotion-overview">
                    <h4>课堂情感状态</h4>
                    <div class="emotion-metrics">
                        <div class="emotion-item">
                            <span class="emotion-label">积极</span>
                            <span class="emotion-value">65%</span>
                        </div>
                        <div class="emotion-item">
                            <span class="emotion-label">专注</span>
                            <span class="emotion-value">78%</span>
                        </div>
                        <div class="emotion-item">
                            <span class="emotion-label">困惑</span>
                            <span class="emotion-value">12%</span>
                        </div>
                    </div>
                </div>
                <div class="emotion-suggestions">
                    <h4>调节建议</h4>
                    <ul>
                        <li>可以适当增加互动环节提高参与度</li>
                        <li>注意观察困惑学生的学习状态</li>
                        <li>保持当前教学节奏</li>
                    </ul>
                </div>
            </div>
        `;
    }

    // 初始化互动工具
    initInteractionTools() {
        // 创建投票按钮
        const createPollBtn = document.querySelector('.btn-create-poll');
        if (createPollBtn) {
            createPollBtn.addEventListener('click', () => {
                this.createNewPoll();
            });
        }

        // 开始游戏按钮
        const startGameBtn = document.querySelector('.btn-start-game');
        if (startGameBtn) {
            startGameBtn.addEventListener('click', () => {
                this.startNewGame();
            });
        }

        // 初始化白板
        this.initWhiteboard();
    }

    // 创建新投票
    createNewPoll() {
        const pollContainer = document.querySelector('.poll-container');
        if (!pollContainer) return;

        pollContainer.innerHTML = `
            <div class="poll-creator">
                <h4>创建投票</h4>
                <div class="form-group">
                    <label>投票问题</label>
                    <input type="text" class="form-input" placeholder="请输入投票问题">
                </div>
                <div class="form-group">
                    <label>选项</label>
                    <div class="poll-options">
                        <input type="text" class="form-input" placeholder="选项1">
                        <input type="text" class="form-input" placeholder="选项2">
                    </div>
                    <button class="btn btn-outline btn-add-option">添加选项</button>
                </div>
                <div class="form-actions">
                    <button class="btn btn-primary btn-start-poll">开始投票</button>
                    <button class="btn btn-outline btn-cancel-poll">取消</button>
                </div>
            </div>
        `;

        // 绑定事件
        this.bindPollEvents();
    }

    // 绑定投票事件
    bindPollEvents() {
        const addOptionBtn = document.querySelector('.btn-add-option');
        const startPollBtn = document.querySelector('.btn-start-poll');
        const cancelPollBtn = document.querySelector('.btn-cancel-poll');

        if (addOptionBtn) {
            addOptionBtn.addEventListener('click', () => {
                const optionsContainer = document.querySelector('.poll-options');
                const optionCount = optionsContainer.children.length + 1;
                const newOption = document.createElement('input');
                newOption.type = 'text';
                newOption.className = 'form-input';
                newOption.placeholder = `选项${optionCount}`;
                optionsContainer.appendChild(newOption);
            });
        }

        if (startPollBtn) {
            startPollBtn.addEventListener('click', () => {
                this.startPoll();
            });
        }

        if (cancelPollBtn) {
            cancelPollBtn.addEventListener('click', () => {
                this.cancelPoll();
            });
        }
    }

    // 开始投票
    startPoll() {
        const question = document.querySelector('.poll-creator input[placeholder="请输入投票问题"]').value;
        const options = Array.from(document.querySelectorAll('.poll-options input')).map(input => input.value).filter(value => value.trim());

        if (!question.trim() || options.length < 2) {
            this.showNotification('请输入投票问题和至少两个选项', 'error');
            return;
        }

        // 显示投票界面
        this.showActivePoll(question, options);
        this.showNotification('投票已开始，学生可以参与投票', 'success');
    }

    // 显示活跃投票
    showActivePoll(question, options) {
        const pollContainer = document.querySelector('.poll-container');
        
        pollContainer.innerHTML = `
            <div class="active-poll">
                <h4>${question}</h4>
                <div class="poll-results">
                    ${options.map((option, index) => `
                        <div class="poll-option">
                            <div class="option-text">${option}</div>
                            <div class="option-bar">
                                <div class="option-fill" style="width: ${Math.random() * 100}%"></div>
                            </div>
                            <div class="option-count">${Math.floor(Math.random() * 20)} 票</div>
                        </div>
                    `).join('')}
                </div>
                <div class="poll-actions">
                    <button class="btn btn-outline btn-end-poll">结束投票</button>
                </div>
            </div>
        `;

        // 绑定结束投票事件
        document.querySelector('.btn-end-poll').addEventListener('click', () => {
            this.endPoll();
        });
    }

    // 结束投票
    endPoll() {
        const pollContainer = document.querySelector('.poll-container');
        pollContainer.innerHTML = '<div class="empty-state">暂无进行中的投票</div>';
        this.showNotification('投票已结束', 'info');
    }

    // 取消投票
    cancelPoll() {
        const pollContainer = document.querySelector('.poll-container');
        pollContainer.innerHTML = '<div class="empty-state">暂无进行中的投票</div>';
    }

    // 开始新游戏
    startNewGame() {
        const gameContainer = document.querySelector('.game-container');
        if (!gameContainer) return;

        const games = [
            { name: '生物分类大挑战', description: '快速分类不同的生物' },
            { name: '细胞结构拼图', description: '拼出完整的细胞结构图' },
            { name: '生态系统连连看', description: '连接相关的生态要素' }
        ];

        const randomGame = games[Math.floor(Math.random() * games.length)];

        gameContainer.innerHTML = `
            <div class="game-interface">
                <h4>${randomGame.name}</h4>
                <p>${randomGame.description}</p>
                <div class="game-area">
                    <div class="game-placeholder">
                        <i class="fas fa-gamepad fa-3x"></i>
                        <p>游戏正在加载中...</p>
                    </div>
                </div>
                <div class="game-controls">
                    <button class="btn btn-primary">开始游戏</button>
                    <button class="btn btn-outline">结束游戏</button>
                </div>
            </div>
        `;

        this.showNotification(`已启动游戏：${randomGame.name}`, 'success');
    }

    // 初始化白板
    initWhiteboard() {
        const canvas = document.getElementById('whiteboard');
        if (!canvas) return;

        this.whiteboardContext = canvas.getContext('2d');
        
        // 绑定绘图事件
        canvas.addEventListener('mousedown', (e) => {
            this.isDrawing = true;
            this.startDrawing(e);
        });

        canvas.addEventListener('mousemove', (e) => {
            if (this.isDrawing) {
                this.draw(e);
            }
        });

        canvas.addEventListener('mouseup', () => {
            this.isDrawing = false;
        });

        // 绑定工具按钮
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentTool = btn.dataset.tool;
            });
        });

        // 清空按钮
        const clearBtn = document.querySelector('.whiteboard-tools .btn-outline');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearWhiteboard();
            });
        }
    }

    // 开始绘图
    startDrawing(e) {
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        this.whiteboardContext.beginPath();
        this.whiteboardContext.moveTo(x, y);
    }

    // 绘图
    draw(e) {
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        this.whiteboardContext.lineTo(x, y);
        this.whiteboardContext.stroke();
    }

    // 清空白板
    clearWhiteboard() {
        const canvas = document.getElementById('whiteboard');
        this.whiteboardContext.clearRect(0, 0, canvas.width, canvas.height);
    }

    // 刷新数据方法
    refreshRealtimeData() {
        this.updateMetrics();
        this.renderStudentList(this.realtimeData.students);
        this.renderAISuggestions();
        this.renderClassroomStats();
    }

    refreshExperimentData() {
        this.renderExperimentSteps();
        this.renderExperimentMaterials();
        this.renderAIExperimentSuggestions();
        this.renderSafetyReminders();
    }

    refreshAIApps() {
        this.renderRunningApps();
        this.renderPerformanceMetrics();
        this.renderUsageStats();
    }

    refreshInteractionTools() {
        this.renderParticipationStats();
        this.renderInteractionHistory();
        this.renderTemplateShortcuts();
    }

    // 更新指标
    updateMetrics() {
        // 模拟实时数据更新
        this.realtimeData.metrics.attentionRate = Math.max(60, Math.min(95, this.realtimeData.metrics.attentionRate + (Math.random() - 0.5) * 5));
        this.realtimeData.metrics.participationRate = Math.max(70, Math.min(100, this.realtimeData.metrics.participationRate + (Math.random() - 0.5) * 3));
        this.realtimeData.metrics.comprehensionRate = Math.max(60, Math.min(90, this.realtimeData.metrics.comprehensionRate + (Math.random() - 0.5) * 4));

        // 更新显示
        const metrics = document.querySelectorAll('.metric-value');
        if (metrics.length >= 4) {
            metrics[0].textContent = this.realtimeData.metrics.onlineStudents;
            metrics[1].textContent = Math.round(this.realtimeData.metrics.attentionRate) + '%';
            metrics[2].textContent = Math.round(this.realtimeData.metrics.participationRate) + '%';
            metrics[3].textContent = Math.round(this.realtimeData.metrics.comprehensionRate) + '%';
        }
    }

    // 渲染AI建议
    renderAISuggestions() {
        const container = document.querySelector('.ai-suggestions');
        if (!container) return;

        const suggestions = [
            { title: '注意力提醒', content: '检测到部分学生注意力下降，建议增加互动环节' },
            { title: '教学节奏', content: '当前教学节奏适中，学生理解度良好' },
            { title: '重点强调', content: '建议重点强调细胞膜的功能和结构特点' }
        ];

        container.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item">
                <div class="suggestion-title">${suggestion.title}</div>
                <div class="suggestion-content">${suggestion.content}</div>
            </div>
        `).join('');
    }

    // 渲染课堂统计
    renderClassroomStats() {
        const container = document.querySelector('.classroom-stats');
        if (!container) return;

        const stats = [
            { label: '课程进度', value: '65%' },
            { label: '提问次数', value: '12次' },
            { label: '互动参与', value: '28人' },
            { label: '作业完成', value: '85%' }
        ];

        container.innerHTML = stats.map(stat => `
            <div class="stat-item">
                <span class="stat-label">${stat.label}</span>
                <span class="stat-value">${stat.value}</span>
            </div>
        `).join('');
    }

    // 渲染AI实验建议
    renderAIExperimentSuggestions() {
        const container = document.querySelector('.ai-experiment-suggestions');
        if (!container) return;

        const suggestions = [
            { title: '实验优化', content: '建议在步骤2中增加安全提醒' },
            { title: '材料建议', content: '可以准备备用的载玻片以防破损' },
            { title: '时间安排', content: '观察环节可适当延长5分钟' }
        ];

        container.innerHTML = suggestions.map(suggestion => `
            <div class="experiment-suggestion">
                <div class="experiment-suggestion-title">${suggestion.title}</div>
                <div class="experiment-suggestion-content">${suggestion.content}</div>
            </div>
        `).join('');
    }

    // 渲染安全提醒
    renderSafetyReminders() {
        const container = document.querySelector('.safety-reminders');
        if (!container) return;

        const reminders = [
            '使用显微镜时注意保护镜头',
            '载玻片易碎，小心操作',
            '实验结束后及时清理器材',
            '注意用电安全'
        ];

        container.innerHTML = reminders.map(reminder => `
            <div class="safety-reminder">${reminder}</div>
        `).join('');
    }

    // 渲染性能指标
    renderPerformanceMetrics() {
        const container = document.querySelector('.performance-metrics');
        if (!container) return;

        const metrics = [
            { label: 'CPU使用率', value: '45%', percentage: 45 },
            { label: '内存使用', value: '2.1GB', percentage: 60 },
            { label: '网络延迟', value: '12ms', percentage: 20 },
            { label: 'AI响应时间', value: '0.8s', percentage: 30 }
        ];

        container.innerHTML = metrics.map(metric => `
            <div class="performance-item">
                <div class="performance-label">${metric.label}</div>
                <div class="performance-value">${metric.value}</div>
                <div class="performance-bar">
                    <div class="performance-fill" style="width: ${metric.percentage}%"></div>
                </div>
            </div>
        `).join('');
    }

    // 渲染使用统计
    renderUsageStats() {
        const container = document.querySelector('.usage-stats');
        if (!container) return;

        const stats = [
            { label: '今日使用时长', value: '2.5小时' },
            { label: '启动应用数', value: '6个' },
            { label: '处理请求数', value: '156次' },
            { label: '成功率', value: '98.5%' }
        ];

        container.innerHTML = stats.map(stat => `
            <div class="usage-item">
                <span class="usage-label">${stat.label}</span>
                <span class="usage-value">${stat.value}</span>
            </div>
        `).join('');
    }

    // 渲染参与统计
    renderParticipationStats() {
        const container = document.querySelector('.participation-stats');
        if (!container) return;

        const stats = [
            { label: '投票参与率', value: '92%' },
            { label: '游戏参与人数', value: '28人' },
            { label: '白板协作次数', value: '15次' },
            { label: '提问回答率', value: '85%' }
        ];

        container.innerHTML = stats.map(stat => `
            <div class="participation-item">
                <span class="participation-label">${stat.label}</span>
                <span class="participation-value">${stat.value}</span>
            </div>
        `).join('');
    }

    // 渲染互动历史
    renderInteractionHistory() {
        const container = document.querySelector('.interaction-history');
        if (!container) return;

        const history = [
            { time: '14:25', content: '开始课堂投票：细胞的基本结构' },
            { time: '14:20', content: '启动互动游戏：生物分类挑战' },
            { time: '14:15', content: '学生张三举手提问' },
            { time: '14:10', content: '开启白板协作模式' }
        ];

        container.innerHTML = history.map(item => `
            <div class="history-item">
                <div class="history-time">${item.time}</div>
                <div class="history-content">${item.content}</div>
            </div>
        `).join('');
    }

    // 渲染快速模板
    renderTemplateShortcuts() {
        const container = document.querySelector('.template-shortcuts');
        if (!container) return;

        const shortcuts = [
            '是非判断题',
            '选择题投票',
            '分组讨论',
            '知识竞赛',
            '课堂小测'
        ];

        container.innerHTML = shortcuts.map(shortcut => `
            <div class="template-shortcut">${shortcut}</div>
        `).join('');
    }

    // 加载模拟数据
    loadMockData() {
        // 模拟学生数据
        this.realtimeData.students = [
            { name: '张三', status: '专注听讲', needsAttention: false, isActive: true, isConfused: false },
            { name: '李四', status: '积极参与', needsAttention: false, isActive: true, isConfused: false },
            { name: '王五', status: '需要关注', needsAttention: true, isActive: false, isConfused: true },
            { name: '赵六', status: '正常学习', needsAttention: false, isActive: false, isConfused: false },
            { name: '钱七', status: '举手提问', needsAttention: false, isActive: true, isConfused: false }
        ];

        // 初始渲染
        this.renderStudentList(this.realtimeData.students);
        this.renderAISuggestions();
        this.renderClassroomStats();
    }

    // 开始实时更新
    startRealtimeUpdates() {
        // 每5秒更新一次数据
        setInterval(() => {
            if (this.currentTab === 'realtime-analysis') {
                this.updateMetrics();
            }
        }, 5000);
    }

    // 显示通知
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // 添加到页面
        document.body.appendChild(notification);

        // 绑定关闭事件
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });

        // 自动关闭
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // 获取通知图标
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.classroomAI = new ClassroomAIModule();
});