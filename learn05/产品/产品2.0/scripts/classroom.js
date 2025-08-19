/**
 * 课堂助手模块 JavaScript 交互逻辑
 * 智能教学助手2.0 - 课堂助手模块
 */

// 课堂助手模块对象
const Classroom = {
    // 当前活跃的标签页
    activeTab: 'real-time-analysis',
    
    // 课堂状态
    classroomState: {
        isActive: false,
        startTime: null,
        currentStep: null,
        studentCount: 0
    },
    
    // 学情数据
    studentData: {
        responses: [],
        participation: [],
        understanding: []
    },
    
    // 练习推荐数据
    exerciseData: [],
    
    // 实验设计数据
    experimentData: [],
    
    // 录制分析数据
    recordingData: {
        isRecording: false,
        duration: 0,
        analysisResults: null
    },
    
    // 初始化
    init() {
        this.bindEvents();
        this.loadInitialData();
        this.setupTabSwitching();
        this.initializeRealTimeMonitoring();
    },
    
    // 绑定事件
    bindEvents() {
        // 标签页切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // 开始/结束课堂
        const startClassBtn = document.querySelector('.start-class-btn');
        const endClassBtn = document.querySelector('.end-class-btn');
        
        if (startClassBtn) {
            startClassBtn.addEventListener('click', this.startClass.bind(this));
        }
        if (endClassBtn) {
            endClassBtn.addEventListener('click', this.endClass.bind(this));
        }
        
        // 开始/停止录制
        const recordBtn = document.querySelector('.record-btn');
        const stopRecordBtn = document.querySelector('.stop-record-btn');
        
        if (recordBtn) {
            recordBtn.addEventListener('click', this.startRecording.bind(this));
        }
        if (stopRecordBtn) {
            stopRecordBtn.addEventListener('click', this.stopRecording.bind(this));
        }
        
        // 生成练习
        const generateExerciseBtn = document.querySelector('.generate-exercise-btn');
        if (generateExerciseBtn) {
            generateExerciseBtn.addEventListener('click', this.generateExercise.bind(this));
        }
        
        // 实验设计
        const designExperimentBtn = document.querySelector('.design-experiment-btn');
        if (designExperimentBtn) {
            designExperimentBtn.addEventListener('click', this.designExperiment.bind(this));
        }
        
        // 导出报告
        const exportReportBtn = document.querySelector('.export-report-btn');
        if (exportReportBtn) {
            exportReportBtn.addEventListener('click', this.exportReport.bind(this));
        }
        
        // 学生互动事件
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('student-detail-btn')) {
                this.showStudentDetail(e.target.dataset.studentId);
            }
            if (e.target.classList.contains('send-exercise-btn')) {
                this.sendExercise(e.target.dataset.exerciseId);
            }
            if (e.target.classList.contains('preview-experiment-btn')) {
                this.previewExperiment(e.target.dataset.experimentId);
            }
        });
    },
    
    // 加载初始数据
    loadInitialData() {
        // 模拟学生数据
        this.studentData.responses = [
            { id: 1, name: '张三', correct: 8, total: 10, accuracy: 80, participation: 85 },
            { id: 2, name: '李四', correct: 9, total: 10, accuracy: 90, participation: 92 },
            { id: 3, name: '王五', correct: 6, total: 10, accuracy: 60, participation: 70 },
            { id: 4, name: '赵六', correct: 7, total: 10, accuracy: 70, participation: 78 }
        ];
        
        // 模拟练习数据
        this.exerciseData = [
            {
                id: 1,
                title: '函数基础练习',
                difficulty: '简单',
                type: '选择题',
                targetStudents: ['张三', '王五'],
                questions: 5,
                estimatedTime: '10分钟'
            },
            {
                id: 2,
                title: '函数图像分析',
                difficulty: '中等',
                type: '解答题',
                targetStudents: ['李四', '赵六'],
                questions: 3,
                estimatedTime: '15分钟'
            }
        ];
        
        // 模拟实验数据
        this.experimentData = [
            {
                id: 1,
                title: '函数图像绘制实验',
                description: '通过动手绘制函数图像，理解函数的性质',
                materials: ['坐标纸', '彩色笔', '计算器'],
                steps: ['准备材料', '绘制坐标系', '计算函数值', '绘制图像', '分析性质'],
                duration: '20分钟',
                difficulty: '中等'
            },
            {
                id: 2,
                title: '函数变换观察实验',
                description: '观察函数图像的平移、伸缩等变换规律',
                materials: ['图形软件', '投影设备'],
                steps: ['打开软件', '输入函数', '观察变换', '记录规律', '总结结论'],
                duration: '15分钟',
                difficulty: '简单'
            }
        ];
        
        this.renderInitialContent();
    },
    
    // 渲染初始内容
    renderInitialContent() {
        this.renderStudentAnalysis();
        this.renderExerciseRecommendations();
        this.renderExperimentDesigns();
        this.updateClassroomStatus();
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
    
    // 初始化实时监控
    initializeRealTimeMonitoring() {
        // 模拟实时数据更新
        setInterval(() => {
            if (this.classroomState.isActive) {
                this.updateRealTimeData();
            }
        }, 5000); // 每5秒更新一次
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
    
    // 开始课堂
    startClass() {
        this.classroomState.isActive = true;
        this.classroomState.startTime = new Date();
        this.classroomState.studentCount = this.studentData.responses.length;
        
        this.updateClassroomStatus();
        this.showNotification('课堂已开始，开始实时监控学生学习状态', 'success');
        
        // 开始实时数据收集
        this.startRealTimeCollection();
    },
    
    // 结束课堂
    endClass() {
        if (confirm('确定要结束当前课堂吗？')) {
            this.classroomState.isActive = false;
            this.updateClassroomStatus();
            this.generateClassSummary();
            this.showNotification('课堂已结束，正在生成课堂总结报告', 'info');
        }
    },
    
    // 更新课堂状态
    updateClassroomStatus() {
        const statusContainer = document.querySelector('.classroom-status');
        if (!statusContainer) return;
        
        const duration = this.classroomState.startTime ? 
            Math.floor((new Date() - this.classroomState.startTime) / 1000 / 60) : 0;
        
        statusContainer.innerHTML = `
            <div class="status-card ${this.classroomState.isActive ? 'active' : 'inactive'}">
                <div class="status-indicator">
                    <div class="indicator-dot ${this.classroomState.isActive ? 'active' : ''}"></div>
                    <span class="status-text">${this.classroomState.isActive ? '课堂进行中' : '课堂未开始'}</span>
                </div>
                <div class="status-info">
                    <div class="info-item">
                        <span class="info-label">学生人数</span>
                        <span class="info-value">${this.classroomState.studentCount}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">课堂时长</span>
                        <span class="info-value">${duration}分钟</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">当前环节</span>
                        <span class="info-value">${this.classroomState.currentStep || '未设置'}</span>
                    </div>
                </div>
                <div class="status-actions">
                    ${this.classroomState.isActive ? 
                        '<button class="btn btn-danger end-class-btn"><i class="fas fa-stop"></i>结束课堂</button>' :
                        '<button class="btn btn-primary start-class-btn"><i class="fas fa-play"></i>开始课堂</button>'
                    }
                </div>
            </div>
        `;
        
        // 重新绑定事件
        const startBtn = statusContainer.querySelector('.start-class-btn');
        const endBtn = statusContainer.querySelector('.end-class-btn');
        
        if (startBtn) {
            startBtn.addEventListener('click', this.startClass.bind(this));
        }
        if (endBtn) {
            endBtn.addEventListener('click', this.endClass.bind(this));
        }
    },
    
    // 开始实时数据收集
    startRealTimeCollection() {
        // 模拟实时数据收集
        this.showNotification('开始收集学生实时学习数据', 'info');
    },
    
    // 更新实时数据
    updateRealTimeData() {
        // 模拟数据变化
        this.studentData.responses.forEach(student => {
            // 随机更新学生数据
            const change = Math.random() * 10 - 5; // -5 到 5 的随机变化
            student.participation = Math.max(0, Math.min(100, student.participation + change));
        });
        
        this.renderStudentAnalysis();
    },
    
    // 渲染学生分析
    renderStudentAnalysis() {
        const container = document.querySelector('#student-analysis-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="analysis-overview">
                <div class="overview-stats">
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${this.studentData.responses.length}</h3>
                            <p>在线学生</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${Math.round(this.studentData.responses.reduce((sum, s) => sum + s.accuracy, 0) / this.studentData.responses.length)}%</h3>
                            <p>平均正确率</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-hand-paper"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${Math.round(this.studentData.responses.reduce((sum, s) => sum + s.participation, 0) / this.studentData.responses.length)}%</h3>
                            <p>平均参与度</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${new Date().toLocaleTimeString()}</h3>
                            <p>当前时间</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="student-list">
                <div class="list-header">
                    <h3>学生实时状态</h3>
                    <div class="list-actions">
                        <button class="btn btn-sm btn-outline refresh-btn">
                            <i class="fas fa-sync-alt"></i>刷新
                        </button>
                    </div>
                </div>
                <div class="student-grid">
                    ${this.studentData.responses.map(student => `
                        <div class="student-card">
                            <div class="student-avatar">
                                <i class="fas fa-user"></i>
                            </div>
                            <div class="student-info">
                                <h4>${student.name}</h4>
                                <div class="student-stats">
                                    <div class="stat-item">
                                        <span class="stat-label">正确率</span>
                                        <span class="stat-value ${student.accuracy >= 80 ? 'good' : student.accuracy >= 60 ? 'average' : 'poor'}">
                                            ${student.accuracy}%
                                        </span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">参与度</span>
                                        <span class="stat-value ${student.participation >= 80 ? 'good' : student.participation >= 60 ? 'average' : 'poor'}">
                                            ${Math.round(student.participation)}%
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="student-actions">
                                <button class="btn btn-sm btn-outline student-detail-btn" data-student-id="${student.id}">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // 绑定刷新按钮事件
        const refreshBtn = container.querySelector('.refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.updateRealTimeData();
                this.showNotification('数据已刷新', 'success');
            });
        }
    },
    
    // 渲染练习推荐
    renderExerciseRecommendations() {
        const container = document.querySelector('#exercise-recommendations-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="exercise-header">
                <h3>智能练习推荐</h3>
                <div class="header-actions">
                    <button class="btn btn-primary generate-exercise-btn">
                        <i class="fas fa-magic"></i>生成新练习
                    </button>
                </div>
            </div>
            
            <div class="exercise-grid">
                ${this.exerciseData.map(exercise => `
                    <div class="exercise-card">
                        <div class="exercise-header">
                            <h4>${exercise.title}</h4>
                            <div class="difficulty-badge ${exercise.difficulty}">${exercise.difficulty}</div>
                        </div>
                        <div class="exercise-info">
                            <div class="info-row">
                                <span class="info-label">类型:</span>
                                <span class="info-value">${exercise.type}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">题目数:</span>
                                <span class="info-value">${exercise.questions}题</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">预计时间:</span>
                                <span class="info-value">${exercise.estimatedTime}</span>
                            </div>
                        </div>
                        <div class="target-students">
                            <span class="target-label">推荐学生:</span>
                            <div class="student-tags">
                                ${exercise.targetStudents.map(student => `
                                    <span class="student-tag">${student}</span>
                                `).join('')}
                            </div>
                        </div>
                        <div class="exercise-actions">
                            <button class="btn btn-sm btn-outline preview-btn">
                                <i class="fas fa-eye"></i>预览
                            </button>
                            <button class="btn btn-sm btn-primary send-exercise-btn" data-exercise-id="${exercise.id}">
                                <i class="fas fa-paper-plane"></i>发送
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        // 重新绑定生成练习按钮事件
        const generateBtn = container.querySelector('.generate-exercise-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', this.generateExercise.bind(this));
        }
    },
    
    // 渲染实验设计
    renderExperimentDesigns() {
        const container = document.querySelector('#experiment-designs-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="experiment-header">
                <h3>实验设计助手</h3>
                <div class="header-actions">
                    <button class="btn btn-primary design-experiment-btn">
                        <i class="fas fa-flask"></i>设计新实验
                    </button>
                </div>
            </div>
            
            <div class="experiment-grid">
                ${this.experimentData.map(experiment => `
                    <div class="experiment-card">
                        <div class="experiment-header">
                            <h4>${experiment.title}</h4>
                            <div class="difficulty-badge ${experiment.difficulty}">${experiment.difficulty}</div>
                        </div>
                        <div class="experiment-description">
                            <p>${experiment.description}</p>
                        </div>
                        <div class="experiment-details">
                            <div class="detail-section">
                                <h5><i class="fas fa-tools"></i>实验材料</h5>
                                <div class="material-list">
                                    ${experiment.materials.map(material => `
                                        <span class="material-tag">${material}</span>
                                    `).join('')}
                                </div>
                            </div>
                            <div class="detail-section">
                                <h5><i class="fas fa-list-ol"></i>实验步骤</h5>
                                <div class="step-list">
                                    ${experiment.steps.map((step, index) => `
                                        <div class="step-item">
                                            <span class="step-number">${index + 1}</span>
                                            <span class="step-text">${step}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            <div class="detail-section">
                                <div class="experiment-meta">
                                    <div class="meta-item">
                                        <i class="fas fa-clock"></i>
                                        <span>预计时长: ${experiment.duration}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="experiment-actions">
                            <button class="btn btn-sm btn-outline preview-experiment-btn" data-experiment-id="${experiment.id}">
                                <i class="fas fa-eye"></i>预览
                            </button>
                            <button class="btn btn-sm btn-primary start-experiment-btn">
                                <i class="fas fa-play"></i>开始实验
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        // 重新绑定设计实验按钮事件
        const designBtn = container.querySelector('.design-experiment-btn');
        if (designBtn) {
            designBtn.addEventListener('click', this.designExperiment.bind(this));
        }
    },
    
    // 生成练习
    generateExercise() {
        this.showModal('生成智能练习', `
            <form id="generate-exercise-form">
                <div class="form-group">
                    <label for="exercise-topic">练习主题</label>
                    <input type="text" id="exercise-topic" class="form-input" placeholder="请输入练习主题" required>
                </div>
                <div class="form-group">
                    <label for="exercise-difficulty">难度等级</label>
                    <select id="exercise-difficulty" class="form-select" required>
                        <option value="简单">简单</option>
                        <option value="中等">中等</option>
                        <option value="困难">困难</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="exercise-type">题目类型</label>
                    <select id="exercise-type" class="form-select" required>
                        <option value="选择题">选择题</option>
                        <option value="填空题">填空题</option>
                        <option value="解答题">解答题</option>
                        <option value="综合题">综合题</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="exercise-count">题目数量</label>
                    <input type="number" id="exercise-count" class="form-input" min="1" max="20" value="5" required>
                </div>
                <div class="form-group">
                    <label for="target-students">目标学生</label>
                    <div class="student-checkboxes">
                        ${this.studentData.responses.map(student => `
                            <div class="checkbox-item">
                                <input type="checkbox" id="student-${student.id}" value="${student.name}">
                                <label for="student-${student.id}">${student.name}</label>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="Classroom.closeModal()">取消</button>
                    <button type="submit" class="btn btn-primary">生成练习</button>
                </div>
            </form>
        `);
        
        // 绑定表单提交事件
        document.getElementById('generate-exercise-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveGeneratedExercise();
        });
    },
    
    // 保存生成的练习
    saveGeneratedExercise() {
        const topic = document.getElementById('exercise-topic').value;
        const difficulty = document.getElementById('exercise-difficulty').value;
        const type = document.getElementById('exercise-type').value;
        const count = document.getElementById('exercise-count').value;
        
        const selectedStudents = [];
        document.querySelectorAll('.student-checkboxes input:checked').forEach(checkbox => {
            selectedStudents.push(checkbox.value);
        });
        
        const newExercise = {
            id: this.exerciseData.length + 1,
            title: topic,
            difficulty: difficulty,
            type: type,
            targetStudents: selectedStudents,
            questions: parseInt(count),
            estimatedTime: `${Math.ceil(parseInt(count) * 2)}分钟`
        };
        
        this.exerciseData.push(newExercise);
        this.renderExerciseRecommendations();
        this.closeModal();
        this.showNotification('练习生成成功！', 'success');
    },
    
    // 发送练习
    sendExercise(exerciseId) {
        const exercise = this.exerciseData.find(e => e.id == exerciseId);
        if (!exercise) return;
        
        this.showLoadingOverlay('正在发送练习给学生...');
        
        setTimeout(() => {
            this.hideLoadingOverlay();
            this.showNotification(`练习"${exercise.title}"已发送给${exercise.targetStudents.join('、')}`, 'success');
        }, 2000);
    },
    
    // 设计实验
    designExperiment() {
        this.showModal('设计教学实验', `
            <form id="design-experiment-form">
                <div class="form-group">
                    <label for="experiment-title">实验标题</label>
                    <input type="text" id="experiment-title" class="form-input" placeholder="请输入实验标题" required>
                </div>
                <div class="form-group">
                    <label for="experiment-description">实验描述</label>
                    <textarea id="experiment-description" class="form-textarea" placeholder="请描述实验目的和内容" required></textarea>
                </div>
                <div class="form-group">
                    <label for="experiment-materials">实验材料（用逗号分隔）</label>
                    <input type="text" id="experiment-materials" class="form-input" placeholder="例如：坐标纸,彩色笔,计算器" required>
                </div>
                <div class="form-group">
                    <label for="experiment-steps">实验步骤（每行一个步骤）</label>
                    <textarea id="experiment-steps" class="form-textarea" placeholder="请输入实验步骤，每行一个" required></textarea>
                </div>
                <div class="form-group">
                    <label for="experiment-duration">预计时长</label>
                    <input type="text" id="experiment-duration" class="form-input" placeholder="例如：20分钟" required>
                </div>
                <div class="form-group">
                    <label for="experiment-difficulty">难度等级</label>
                    <select id="experiment-difficulty" class="form-select" required>
                        <option value="简单">简单</option>
                        <option value="中等">中等</option>
                        <option value="困难">困难</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="Classroom.closeModal()">取消</button>
                    <button type="submit" class="btn btn-primary">创建实验</button>
                </div>
            </form>
        `);
        
        // 绑定表单提交事件
        document.getElementById('design-experiment-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveDesignedExperiment();
        });
    },
    
    // 保存设计的实验
    saveDesignedExperiment() {
        const title = document.getElementById('experiment-title').value;
        const description = document.getElementById('experiment-description').value;
        const materials = document.getElementById('experiment-materials').value.split(',').map(m => m.trim());
        const steps = document.getElementById('experiment-steps').value.split('\n').filter(s => s.trim());
        const duration = document.getElementById('experiment-duration').value;
        const difficulty = document.getElementById('experiment-difficulty').value;
        
        const newExperiment = {
            id: this.experimentData.length + 1,
            title: title,
            description: description,
            materials: materials,
            steps: steps,
            duration: duration,
            difficulty: difficulty
        };
        
        this.experimentData.push(newExperiment);
        this.renderExperimentDesigns();
        this.closeModal();
        this.showNotification('实验设计创建成功！', 'success');
    },
    
    // 预览实验
    previewExperiment(experimentId) {
        const experiment = this.experimentData.find(e => e.id == experimentId);
        if (!experiment) return;
        
        this.showModal('实验预览', `
            <div class="experiment-preview">
                <div class="preview-header">
                    <h3>${experiment.title}</h3>
                    <div class="difficulty-badge ${experiment.difficulty}">${experiment.difficulty}</div>
                </div>
                <div class="preview-content">
                    <div class="section">
                        <h4><i class="fas fa-info-circle"></i>实验描述</h4>
                        <p>${experiment.description}</p>
                    </div>
                    <div class="section">
                        <h4><i class="fas fa-tools"></i>实验材料</h4>
                        <div class="material-list">
                            ${experiment.materials.map(material => `
                                <span class="material-tag">${material}</span>
                            `).join('')}
                        </div>
                    </div>
                    <div class="section">
                        <h4><i class="fas fa-list-ol"></i>实验步骤</h4>
                        <div class="step-list">
                            ${experiment.steps.map((step, index) => `
                                <div class="step-item">
                                    <span class="step-number">${index + 1}</span>
                                    <span class="step-text">${step}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="section">
                        <h4><i class="fas fa-clock"></i>时间安排</h4>
                        <p>预计时长: ${experiment.duration}</p>
                    </div>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="Classroom.closeModal()">关闭</button>
                    <button type="button" class="btn btn-primary">开始实验</button>
                </div>
            </div>
        `);
    },
    
    // 显示学生详情
    showStudentDetail(studentId) {
        const student = this.studentData.responses.find(s => s.id == studentId);
        if (!student) return;
        
        this.showModal('学生详细信息', `
            <div class="student-detail">
                <div class="student-header">
                    <div class="student-avatar large">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="student-info">
                        <h3>${student.name}</h3>
                        <p>学号: ${student.id.toString().padStart(4, '0')}</p>
                    </div>
                </div>
                <div class="student-stats-detail">
                    <div class="stat-card">
                        <h4>答题情况</h4>
                        <div class="stat-value large">${student.correct}/${student.total}</div>
                        <div class="stat-label">正确/总数</div>
                    </div>
                    <div class="stat-card">
                        <h4>正确率</h4>
                        <div class="stat-value large ${student.accuracy >= 80 ? 'good' : student.accuracy >= 60 ? 'average' : 'poor'}">
                            ${student.accuracy}%
                        </div>
                        <div class="stat-label">答题正确率</div>
                    </div>
                    <div class="stat-card">
                        <h4>参与度</h4>
                        <div class="stat-value large ${student.participation >= 80 ? 'good' : student.participation >= 60 ? 'average' : 'poor'}">
                            ${Math.round(student.participation)}%
                        </div>
                        <div class="stat-label">课堂参与度</div>
                    </div>
                </div>
                <div class="student-recommendations">
                    <h4>个性化建议</h4>
                    <div class="recommendation-list">
                        ${student.accuracy < 70 ? 
                            '<div class="recommendation-item"><i class="fas fa-lightbulb"></i>建议加强基础知识练习</div>' : ''
                        }
                        ${student.participation < 70 ? 
                            '<div class="recommendation-item"><i class="fas fa-hand-paper"></i>建议增加课堂互动参与</div>' : ''
                        }
                        ${student.accuracy >= 90 && student.participation >= 90 ? 
                            '<div class="recommendation-item"><i class="fas fa-star"></i>表现优秀，可以尝试更有挑战性的题目</div>' : ''
                        }
                    </div>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="Classroom.closeModal()">关闭</button>
                    <button type="button" class="btn btn-primary">发送个性化练习</button>
                </div>
            </div>
        `);
    },
    
    // 开始录制
    startRecording() {
        this.recordingData.isRecording = true;
        this.recordingData.duration = 0;
        
        this.updateRecordingStatus();
        this.showNotification('开始录制课堂视频', 'success');
        
        // 模拟录制计时
        this.recordingInterval = setInterval(() => {
            this.recordingData.duration++;
            this.updateRecordingStatus();
        }, 1000);
    },
    
    // 停止录制
    stopRecording() {
        if (confirm('确定要停止录制吗？')) {
            this.recordingData.isRecording = false;
            clearInterval(this.recordingInterval);
            
            this.updateRecordingStatus();
            this.showNotification('录制已停止，正在进行AI分析...', 'info');
            
            // 模拟分析过程
            setTimeout(() => {
                this.generateRecordingAnalysis();
            }, 3000);
        }
    },
    
    // 更新录制状态
    updateRecordingStatus() {
        const statusContainer = document.querySelector('.recording-status');
        if (!statusContainer) return;
        
        const minutes = Math.floor(this.recordingData.duration / 60);
        const seconds = this.recordingData.duration % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        statusContainer.innerHTML = `
            <div class="recording-indicator ${this.recordingData.isRecording ? 'active' : ''}">
                <div class="recording-dot"></div>
                <span class="recording-text">
                    ${this.recordingData.isRecording ? '正在录制' : '录制已停止'}
                </span>
                <span class="recording-time">${timeString}</span>
            </div>
            <div class="recording-actions">
                ${this.recordingData.isRecording ? 
                    '<button class="btn btn-danger stop-record-btn"><i class="fas fa-stop"></i>停止录制</button>' :
                    '<button class="btn btn-primary record-btn"><i class="fas fa-video"></i>开始录制</button>'
                }
            </div>
        `;
        
        // 重新绑定事件
        const recordBtn = statusContainer.querySelector('.record-btn');
        const stopBtn = statusContainer.querySelector('.stop-record-btn');
        
        if (recordBtn) {
            recordBtn.addEventListener('click', this.startRecording.bind(this));
        }
        if (stopBtn) {
            stopBtn.addEventListener('click', this.stopRecording.bind(this));
        }
    },
    
    // 生成录制分析
    generateRecordingAnalysis() {
        this.recordingData.analysisResults = {
            teachingBehavior: {
                speechRate: 85,
                gestureFrequency: 72,
                movementPattern: '良好',
                eyeContact: 88
            },
            studentEngagement: {
                attentionLevel: 78,
                participationRate: 65,
                questionFrequency: 12,
                responseQuality: 82
            },
            classroomInteraction: {
                teacherStudentRatio: '1:3.2',
                discussionTime: '15分钟',
                silentTime: '8分钟',
                activeTime: '22分钟'
            },
            suggestions: [
                '建议增加学生互动环节',
                '可以适当放慢语速',
                '增加提问频次',
                '注意课堂节奏控制'
            ]
        };
        
        this.renderRecordingAnalysis();
        this.showNotification('课堂录制分析完成！', 'success');
    },
    
    // 渲染录制分析
    renderRecordingAnalysis() {
        const container = document.querySelector('#recording-analysis-container');
        if (!container || !this.recordingData.analysisResults) return;
        
        const results = this.recordingData.analysisResults;
        
        container.innerHTML = `
            <div class="analysis-results">
                <div class="result-section">
                    <h3><i class="fas fa-user-tie"></i>教学行为分析</h3>
                    <div class="behavior-stats">
                        <div class="stat-item">
                            <span class="stat-label">语速适中度</span>
                            <div class="stat-bar">
                                <div class="stat-fill" style="width: ${results.teachingBehavior.speechRate}%"></div>
                            </div>
                            <span class="stat-value">${results.teachingBehavior.speechRate}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">手势频率</span>
                            <div class="stat-bar">
                                <div class="stat-fill" style="width: ${results.teachingBehavior.gestureFrequency}%"></div>
                            </div>
                            <span class="stat-value">${results.teachingBehavior.gestureFrequency}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">眼神交流</span>
                            <div class="stat-bar">
                                <div class="stat-fill" style="width: ${results.teachingBehavior.eyeContact}%"></div>
                            </div>
                            <span class="stat-value">${results.teachingBehavior.eyeContact}%</span>
                        </div>
                    </div>
                </div>
                
                <div class="result-section">
                    <h3><i class="fas fa-users"></i>学生参与度分析</h3>
                    <div class="engagement-stats">
                        <div class="stat-card">
                            <h4>注意力水平</h4>
                            <div class="stat-value large">${results.studentEngagement.attentionLevel}%</div>
                        </div>
                        <div class="stat-card">
                            <h4>参与率</h4>
                            <div class="stat-value large">${results.studentEngagement.participationRate}%</div>
                        </div>
                        <div class="stat-card">
                            <h4>提问次数</h4>
                            <div class="stat-value large">${results.studentEngagement.questionFrequency}</div>
                        </div>
                        <div class="stat-card">
                            <h4>回答质量</h4>
                            <div class="stat-value large">${results.studentEngagement.responseQuality}%</div>
                        </div>
                    </div>
                </div>
                
                <div class="result-section">
                    <h3><i class="fas fa-comments"></i>课堂互动分析</h3>
                    <div class="interaction-info">
                        <div class="info-item">
                            <span class="info-label">师生互动比例</span>
                            <span class="info-value">${results.classroomInteraction.teacherStudentRatio}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">讨论时间</span>
                            <span class="info-value">${results.classroomInteraction.discussionTime}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">静默时间</span>
                            <span class="info-value">${results.classroomInteraction.silentTime}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">活跃时间</span>
                            <span class="info-value">${results.classroomInteraction.activeTime}</span>
                        </div>
                    </div>
                </div>
                
                <div class="result-section">
                    <h3><i class="fas fa-lightbulb"></i>改进建议</h3>
                    <div class="suggestions-list">
                        ${results.suggestions.map(suggestion => `
                            <div class="suggestion-item">
                                <i class="fas fa-arrow-right"></i>
                                <span>${suggestion}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    },
    
    // 生成课堂总结
    generateClassSummary() {
        this.showLoadingOverlay('正在生成课堂总结报告...');
        
        setTimeout(() => {
            this.hideLoadingOverlay();
            this.showClassSummaryModal();
        }, 2000);
    },
    
    // 显示课堂总结模态框
    showClassSummaryModal() {
        const duration = this.classroomState.startTime ? 
            Math.floor((new Date() - this.classroomState.startTime) / 1000 / 60) : 0;
        
        const avgAccuracy = Math.round(this.studentData.responses.reduce((sum, s) => sum + s.accuracy, 0) / this.studentData.responses.length);
        const avgParticipation = Math.round(this.studentData.responses.reduce((sum, s) => sum + s.participation, 0) / this.studentData.responses.length);
        
        this.showModal('课堂总结报告', `
            <div class="class-summary">
                <div class="summary-header">
                    <h3>课堂基本信息</h3>
                    <div class="basic-info">
                        <div class="info-item">
                            <span class="info-label">课堂时长</span>
                            <span class="info-value">${duration}分钟</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">参与学生</span>
                            <span class="info-value">${this.studentData.responses.length}人</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">平均正确率</span>
                            <span class="info-value">${avgAccuracy}%</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">平均参与度</span>
                            <span class="info-value">${avgParticipation}%</span>
                        </div>
                    </div>
                </div>
                
                <div class="summary-section">
                    <h4>学生表现概况</h4>
                    <div class="performance-overview">
                        <div class="performance-chart">
                            <div class="chart-item good">
                                <span class="chart-label">优秀</span>
                                <span class="chart-value">${this.studentData.responses.filter(s => s.accuracy >= 80).length}人</span>
                            </div>
                            <div class="chart-item average">
                                <span class="chart-label">良好</span>
                                <span class="chart-value">${this.studentData.responses.filter(s => s.accuracy >= 60 && s.accuracy < 80).length}人</span>
                            </div>
                            <div class="chart-item poor">
                                <span class="chart-label">待提高</span>
                                <span class="chart-value">${this.studentData.responses.filter(s => s.accuracy < 60).length}人</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="summary-section">
                    <h4>课堂亮点</h4>
                    <div class="highlights">
                        <div class="highlight-item">
                            <i class="fas fa-star"></i>
                            <span>学生整体参与度较高，课堂氛围活跃</span>
                        </div>
                        <div class="highlight-item">
                            <i class="fas fa-thumbs-up"></i>
                            <span>重点知识点掌握情况良好</span>
                        </div>
                        <div class="highlight-item">
                            <i class="fas fa-chart-line"></i>
                            <span>课堂互动效果显著</span>
                        </div>
                    </div>
                </div>
                
                <div class="summary-section">
                    <h4>改进建议</h4>
                    <div class="improvements">
                        <div class="improvement-item">
                            <i class="fas fa-arrow-right"></i>
                            <span>对理解困难的学生提供个性化辅导</span>
                        </div>
                        <div class="improvement-item">
                            <i class="fas fa-arrow-right"></i>
                            <span>增加实践练习环节</span>
                        </div>
                        <div class="improvement-item">
                            <i class="fas fa-arrow-right"></i>
                            <span>关注参与度较低的学生</span>
                        </div>
                    </div>
                </div>
                
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="Classroom.closeModal()">关闭</button>
                    <button type="button" class="btn btn-primary export-report-btn">导出报告</button>
                </div>
            </div>
        `);
        
        // 绑定导出按钮事件
        document.querySelector('.export-report-btn').addEventListener('click', this.exportReport.bind(this));
    },
    
    // 导出报告
    exportReport() {
        this.showLoadingOverlay('正在生成报告文件...');
        
        setTimeout(() => {
            this.hideLoadingOverlay();
            this.showNotification('课堂报告已导出', 'success');
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
                    <button class="modal-close" onclick="Classroom.closeModal()">
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
    Classroom.init();
});