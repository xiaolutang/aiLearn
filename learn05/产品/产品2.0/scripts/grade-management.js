/**
 * 成绩管理模块 JavaScript 交互逻辑
 * 智能教学助手2.0 - 成绩管理模块
 */

// 成绩管理模块对象
const GradeManagement = {
    // 当前活跃的标签页
    activeTab: 'grade-input',
    
    // 成绩数据
    gradeData: {
        students: [],
        subjects: [],
        examTypes: [],
        currentGrades: []
    },
    
    // 分析数据
    analysisData: {
        statistics: {},
        trends: [],
        comparisons: []
    },
    
    // 报告数据
    reportData: {
        individualReports: [],
        classReports: [],
        templates: []
    },
    
    // 辅导方案数据
    tutoringData: {
        plans: [],
        recommendations: [],
        resources: []
    },
    
    // 初始化
    init() {
        this.bindEvents();
        this.loadInitialData();
        this.setupTabSwitching();
        this.initializeGradeInput();
    },
    
    // 绑定事件
    bindEvents() {
        // 标签页切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // 成绩录入相关事件
        const importBtn = document.querySelector('.import-grades-btn');
        const exportBtn = document.querySelector('.export-grades-btn');
        const saveBtn = document.querySelector('.save-grades-btn');
        const analyzeBtn = document.querySelector('.analyze-grades-btn');
        
        if (importBtn) {
            importBtn.addEventListener('click', this.importGrades.bind(this));
        }
        if (exportBtn) {
            exportBtn.addEventListener('click', this.exportGrades.bind(this));
        }
        if (saveBtn) {
            saveBtn.addEventListener('click', this.saveGrades.bind(this));
        }
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', this.analyzeGrades.bind(this));
        }
        
        // 报告生成相关事件
        const generateReportBtn = document.querySelector('.generate-report-btn');
        const batchReportBtn = document.querySelector('.batch-report-btn');
        
        if (generateReportBtn) {
            generateReportBtn.addEventListener('click', this.generateReport.bind(this));
        }
        if (batchReportBtn) {
            batchReportBtn.addEventListener('click', this.generateBatchReports.bind(this));
        }
        
        // 辅导方案相关事件
        const createPlanBtn = document.querySelector('.create-plan-btn');
        if (createPlanBtn) {
            createPlanBtn.addEventListener('click', this.createTutoringPlan.bind(this));
        }
        
        // 动态事件绑定
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('edit-grade-btn')) {
                this.editGrade(e.target.dataset.studentId, e.target.dataset.subject);
            }
            if (e.target.classList.contains('view-report-btn')) {
                this.viewReport(e.target.dataset.studentId);
            }
            if (e.target.classList.contains('view-plan-btn')) {
                this.viewTutoringPlan(e.target.dataset.planId);
            }
            if (e.target.classList.contains('photo-recognition-btn')) {
                this.startPhotoRecognition();
            }
        });
        
        // 文件上传事件
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('grade-file-input')) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
    },
    
    // 加载初始数据
    loadInitialData() {
        // 模拟学生数据
        this.gradeData.students = [
            { id: 1, name: '张三', studentId: '2024001', class: '高一(1)班' },
            { id: 2, name: '李四', studentId: '2024002', class: '高一(1)班' },
            { id: 3, name: '王五', studentId: '2024003', class: '高一(1)班' },
            { id: 4, name: '赵六', studentId: '2024004', class: '高一(1)班' },
            { id: 5, name: '钱七', studentId: '2024005', class: '高一(1)班' },
            { id: 6, name: '孙八', studentId: '2024006', class: '高一(1)班' }
        ];
        
        // 模拟科目数据
        this.gradeData.subjects = ['语文', '数学', '英语', '物理', '化学', '生物'];
        
        // 模拟考试类型
        this.gradeData.examTypes = ['平时测验', '月考', '期中考试', '期末考试'];
        
        // 模拟成绩数据
        this.gradeData.currentGrades = [
            { studentId: 1, subject: '数学', examType: '期中考试', score: 85, fullScore: 100, date: '2024-03-15' },
            { studentId: 1, subject: '语文', examType: '期中考试', score: 78, fullScore: 100, date: '2024-03-15' },
            { studentId: 1, subject: '英语', examType: '期中考试', score: 92, fullScore: 100, date: '2024-03-15' },
            { studentId: 2, subject: '数学', examType: '期中考试', score: 76, fullScore: 100, date: '2024-03-15' },
            { studentId: 2, subject: '语文', examType: '期中考试', score: 88, fullScore: 100, date: '2024-03-15' },
            { studentId: 2, subject: '英语', examType: '期中考试', score: 82, fullScore: 100, date: '2024-03-15' },
            { studentId: 3, subject: '数学', examType: '期中考试', score: 92, fullScore: 100, date: '2024-03-15' },
            { studentId: 3, subject: '语文', examType: '期中考试', score: 85, fullScore: 100, date: '2024-03-15' },
            { studentId: 3, subject: '英语', examType: '期中考试', score: 89, fullScore: 100, date: '2024-03-15' }
        ];
        
        // 模拟辅导方案数据
        this.tutoringData.plans = [
            {
                id: 1,
                studentId: 2,
                studentName: '李四',
                subject: '数学',
                weakPoints: ['函数概念', '图像分析', '应用题'],
                targetScore: 85,
                currentScore: 76,
                duration: '4周',
                status: '进行中',
                createdDate: '2024-03-20'
            },
            {
                id: 2,
                studentId: 4,
                studentName: '赵六',
                subject: '英语',
                weakPoints: ['语法', '阅读理解', '写作'],
                targetScore: 80,
                currentScore: 65,
                duration: '6周',
                status: '待开始',
                createdDate: '2024-03-22'
            }
        ];
        
        this.renderInitialContent();
    },
    
    // 渲染初始内容
    renderInitialContent() {
        this.renderGradeInput();
        this.renderGradeAnalysis();
        this.renderReportGeneration();
        this.renderTutoringPlans();
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
    
    // 初始化成绩录入
    initializeGradeInput() {
        this.renderGradeTable();
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
    
    // 渲染成绩录入
    renderGradeInput() {
        const container = document.querySelector('#grade-input-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="grade-input-header">
                <div class="input-controls">
                    <div class="control-group">
                        <label for="exam-type-select">考试类型</label>
                        <select id="exam-type-select" class="form-select">
                            ${this.gradeData.examTypes.map(type => `
                                <option value="${type}">${type}</option>
                            `).join('')}
                        </select>
                    </div>
                    <div class="control-group">
                        <label for="subject-select">科目</label>
                        <select id="subject-select" class="form-select">
                            ${this.gradeData.subjects.map(subject => `
                                <option value="${subject}">${subject}</option>
                            `).join('')}
                        </select>
                    </div>
                    <div class="control-group">
                        <label for="full-score-input">满分</label>
                        <input type="number" id="full-score-input" class="form-input" value="100" min="1">
                    </div>
                </div>
                
                <div class="input-actions">
                    <button class="btn btn-outline import-grades-btn">
                        <i class="fas fa-file-import"></i>导入Excel
                    </button>
                    <button class="btn btn-outline photo-recognition-btn">
                        <i class="fas fa-camera"></i>拍照识别
                    </button>
                    <button class="btn btn-primary save-grades-btn">
                        <i class="fas fa-save"></i>保存成绩
                    </button>
                </div>
            </div>
            
            <div class="grade-table-container">
                <div id="grade-table">
                    <!-- 成绩表格将由renderGradeTable方法生成 -->
                </div>
            </div>
        `;
        
        this.renderGradeTable();
        
        // 重新绑定事件
        const importBtn = container.querySelector('.import-grades-btn');
        const photoBtn = container.querySelector('.photo-recognition-btn');
        const saveBtn = container.querySelector('.save-grades-btn');
        
        if (importBtn) {
            importBtn.addEventListener('click', this.importGrades.bind(this));
        }
        if (photoBtn) {
            photoBtn.addEventListener('click', this.startPhotoRecognition.bind(this));
        }
        if (saveBtn) {
            saveBtn.addEventListener('click', this.saveGrades.bind(this));
        }
    },
    
    // 渲染成绩表格
    renderGradeTable() {
        const tableContainer = document.querySelector('#grade-table');
        if (!tableContainer) return;
        
        const selectedSubject = document.querySelector('#subject-select')?.value || this.gradeData.subjects[0];
        const selectedExamType = document.querySelector('#exam-type-select')?.value || this.gradeData.examTypes[0];
        
        tableContainer.innerHTML = `
            <table class="grade-table">
                <thead>
                    <tr>
                        <th>序号</th>
                        <th>学号</th>
                        <th>姓名</th>
                        <th>班级</th>
                        <th>成绩</th>
                        <th>等级</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.gradeData.students.map((student, index) => {
                        const grade = this.gradeData.currentGrades.find(g => 
                            g.studentId === student.id && 
                            g.subject === selectedSubject && 
                            g.examType === selectedExamType
                        );
                        const score = grade ? grade.score : '';
                        const level = this.getGradeLevel(score);
                        
                        return `
                            <tr>
                                <td>${index + 1}</td>
                                <td>${student.studentId}</td>
                                <td>${student.name}</td>
                                <td>${student.class}</td>
                                <td>
                                    <input type="number" 
                                           class="grade-input" 
                                           data-student-id="${student.id}"
                                           data-subject="${selectedSubject}"
                                           data-exam-type="${selectedExamType}"
                                           value="${score}" 
                                           min="0" 
                                           max="100"
                                           placeholder="请输入成绩">
                                </td>
                                <td>
                                    <span class="grade-level ${level.class}">${level.text}</span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline edit-grade-btn" 
                                            data-student-id="${student.id}" 
                                            data-subject="${selectedSubject}">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
        
        // 绑定成绩输入事件
        tableContainer.querySelectorAll('.grade-input').forEach(input => {
            input.addEventListener('input', this.handleGradeInput.bind(this));
            input.addEventListener('blur', this.validateGradeInput.bind(this));
        });
    },
    
    // 获取成绩等级
    getGradeLevel(score) {
        if (!score || score === '') {
            return { text: '-', class: 'none' };
        }
        
        const numScore = parseFloat(score);
        if (numScore >= 90) {
            return { text: '优秀', class: 'excellent' };
        } else if (numScore >= 80) {
            return { text: '良好', class: 'good' };
        } else if (numScore >= 70) {
            return { text: '中等', class: 'average' };
        } else if (numScore >= 60) {
            return { text: '及格', class: 'pass' };
        } else {
            return { text: '不及格', class: 'fail' };
        }
    },
    
    // 处理成绩输入
    handleGradeInput(event) {
        const input = event.target;
        const studentId = parseInt(input.dataset.studentId);
        const subject = input.dataset.subject;
        const examType = input.dataset.examType;
        const score = parseFloat(input.value);
        
        // 更新等级显示
        const row = input.closest('tr');
        const levelCell = row.querySelector('.grade-level');
        const level = this.getGradeLevel(score);
        
        levelCell.textContent = level.text;
        levelCell.className = `grade-level ${level.class}`;
        
        // 更新数据
        const existingGrade = this.gradeData.currentGrades.find(g => 
            g.studentId === studentId && 
            g.subject === subject && 
            g.examType === examType
        );
        
        if (existingGrade) {
            existingGrade.score = score;
        } else {
            this.gradeData.currentGrades.push({
                studentId: studentId,
                subject: subject,
                examType: examType,
                score: score,
                fullScore: 100,
                date: new Date().toISOString().split('T')[0]
            });
        }
    },
    
    // 验证成绩输入
    validateGradeInput(event) {
        const input = event.target;
        const value = parseFloat(input.value);
        const fullScore = parseFloat(document.querySelector('#full-score-input')?.value || 100);
        
        if (value < 0 || value > fullScore) {
            input.classList.add('error');
            this.showNotification(`成绩应在0-${fullScore}之间`, 'error');
        } else {
            input.classList.remove('error');
        }
    },
    
    // 导入成绩
    importGrades() {
        this.showModal('导入成绩', `
            <div class="import-grades-modal">
                <div class="import-options">
                    <div class="option-card">
                        <div class="option-icon">
                            <i class="fas fa-file-excel"></i>
                        </div>
                        <h4>Excel文件导入</h4>
                        <p>支持.xlsx和.xls格式文件</p>
                        <input type="file" class="grade-file-input" accept=".xlsx,.xls" style="display: none;">
                        <button class="btn btn-primary" onclick="this.previousElementSibling.click()">
                            选择文件
                        </button>
                    </div>
                    
                    <div class="option-card">
                        <div class="option-icon">
                            <i class="fas fa-camera"></i>
                        </div>
                        <h4>拍照识别</h4>
                        <p>拍摄成绩单照片自动识别</p>
                        <button class="btn btn-primary photo-recognition-btn">
                            开始拍照
                        </button>
                    </div>
                </div>
                
                <div class="import-template">
                    <h4>Excel模板格式</h4>
                    <div class="template-preview">
                        <table class="template-table">
                            <thead>
                                <tr>
                                    <th>学号</th>
                                    <th>姓名</th>
                                    <th>班级</th>
                                    <th>科目</th>
                                    <th>考试类型</th>
                                    <th>成绩</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>2024001</td>
                                    <td>张三</td>
                                    <td>高一(1)班</td>
                                    <td>数学</td>
                                    <td>期中考试</td>
                                    <td>85</td>
                                </tr>
                                <tr>
                                    <td>2024002</td>
                                    <td>李四</td>
                                    <td>高一(1)班</td>
                                    <td>数学</td>
                                    <td>期中考试</td>
                                    <td>76</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <button class="btn btn-outline download-template-btn">
                        <i class="fas fa-download"></i>下载模板
                    </button>
                </div>
                
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="GradeManagement.closeModal()">取消</button>
                </div>
            </div>
        `);
    },
    
    // 处理文件上传
    handleFileUpload(file) {
        if (!file) return;
        
        this.showLoadingOverlay('正在解析Excel文件...');
        
        // 模拟文件解析过程
        setTimeout(() => {
            this.hideLoadingOverlay();
            this.closeModal();
            
            // 模拟导入的成绩数据
            const importedGrades = [
                { studentId: 4, subject: '数学', examType: '期中考试', score: 88, fullScore: 100, date: '2024-03-15' },
                { studentId: 5, subject: '数学', examType: '期中考试', score: 72, fullScore: 100, date: '2024-03-15' },
                { studentId: 6, subject: '数学', examType: '期中考试', score: 95, fullScore: 100, date: '2024-03-15' }
            ];
            
            // 合并到现有数据
            importedGrades.forEach(grade => {
                const existingIndex = this.gradeData.currentGrades.findIndex(g => 
                    g.studentId === grade.studentId && 
                    g.subject === grade.subject && 
                    g.examType === grade.examType
                );
                
                if (existingIndex >= 0) {
                    this.gradeData.currentGrades[existingIndex] = grade;
                } else {
                    this.gradeData.currentGrades.push(grade);
                }
            });
            
            this.renderGradeTable();
            this.showNotification('成绩导入成功！', 'success');
        }, 2000);
    },
    
    // 开始拍照识别
    startPhotoRecognition() {
        this.showModal('拍照识别成绩', `
            <div class="photo-recognition-modal">
                <div class="camera-container">
                    <div class="camera-placeholder">
                        <i class="fas fa-camera"></i>
                        <p>点击下方按钮开启摄像头</p>
                    </div>
                </div>
                
                <div class="recognition-controls">
                    <button class="btn btn-primary start-camera-btn">
                        <i class="fas fa-video"></i>开启摄像头
                    </button>
                    <button class="btn btn-success capture-btn" style="display: none;">
                        <i class="fas fa-camera"></i>拍照
                    </button>
                    <button class="btn btn-outline upload-image-btn">
                        <i class="fas fa-upload"></i>上传图片
                    </button>
                </div>
                
                <div class="recognition-tips">
                    <h4>拍照提示</h4>
                    <ul>
                        <li>确保成绩单清晰可见，光线充足</li>
                        <li>保持手机稳定，避免模糊</li>
                        <li>成绩单应完整显示在画面中</li>
                        <li>支持手写和打印的成绩单</li>
                    </ul>
                </div>
                
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="GradeManagement.closeModal()">取消</button>
                </div>
            </div>
        `);
    },
    
    // 保存成绩
    saveGrades() {
        this.showLoadingOverlay('正在保存成绩...');
        
        setTimeout(() => {
            this.hideLoadingOverlay();
            this.showNotification('成绩保存成功！', 'success');
        }, 1000);
    },
    
    // 渲染成绩分析
    renderGradeAnalysis() {
        const container = document.querySelector('#grade-analysis-container');
        if (!container) return;
        
        // 计算统计数据
        const stats = this.calculateStatistics();
        
        container.innerHTML = `
            <div class="analysis-overview">
                <div class="overview-cards">
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${stats.totalStudents}</h3>
                            <p>总学生数</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${stats.averageScore.toFixed(1)}</h3>
                            <p>平均分</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-trophy"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${stats.highestScore}</h3>
                            <p>最高分</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${stats.passRate.toFixed(1)}%</h3>
                            <p>及格率</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="analysis-charts">
                <div class="chart-container">
                    <h3>成绩分布</h3>
                    <div class="score-distribution">
                        ${this.renderScoreDistribution(stats.distribution)}
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>科目对比</h3>
                    <div class="subject-comparison">
                        ${this.renderSubjectComparison()}
                    </div>
                </div>
            </div>
            
            <div class="analysis-details">
                <div class="detail-section">
                    <h3>学生排名</h3>
                    <div class="student-ranking">
                        ${this.renderStudentRanking()}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>进步分析</h3>
                    <div class="progress-analysis">
                        ${this.renderProgressAnalysis()}
                    </div>
                </div>
            </div>
        `;
    },
    
    // 计算统计数据
    calculateStatistics() {
        const grades = this.gradeData.currentGrades;
        const totalStudents = this.gradeData.students.length;
        
        if (grades.length === 0) {
            return {
                totalStudents: totalStudents,
                averageScore: 0,
                highestScore: 0,
                lowestScore: 0,
                passRate: 0,
                distribution: { excellent: 0, good: 0, average: 0, pass: 0, fail: 0 }
            };
        }
        
        const scores = grades.map(g => g.score);
        const averageScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        const highestScore = Math.max(...scores);
        const lowestScore = Math.min(...scores);
        const passCount = scores.filter(score => score >= 60).length;
        const passRate = (passCount / scores.length) * 100;
        
        const distribution = {
            excellent: scores.filter(s => s >= 90).length,
            good: scores.filter(s => s >= 80 && s < 90).length,
            average: scores.filter(s => s >= 70 && s < 80).length,
            pass: scores.filter(s => s >= 60 && s < 70).length,
            fail: scores.filter(s => s < 60).length
        };
        
        return {
            totalStudents,
            averageScore,
            highestScore,
            lowestScore,
            passRate,
            distribution
        };
    },
    
    // 渲染成绩分布
    renderScoreDistribution(distribution) {
        const total = Object.values(distribution).reduce((sum, count) => sum + count, 0);
        
        return `
            <div class="distribution-chart">
                <div class="distribution-item excellent">
                    <div class="distribution-bar" style="width: ${total > 0 ? (distribution.excellent / total) * 100 : 0}%"></div>
                    <div class="distribution-label">
                        <span class="label-text">优秀(90+)</span>
                        <span class="label-count">${distribution.excellent}人</span>
                    </div>
                </div>
                <div class="distribution-item good">
                    <div class="distribution-bar" style="width: ${total > 0 ? (distribution.good / total) * 100 : 0}%"></div>
                    <div class="distribution-label">
                        <span class="label-text">良好(80-89)</span>
                        <span class="label-count">${distribution.good}人</span>
                    </div>
                </div>
                <div class="distribution-item average">
                    <div class="distribution-bar" style="width: ${total > 0 ? (distribution.average / total) * 100 : 0}%"></div>
                    <div class="distribution-label">
                        <span class="label-text">中等(70-79)</span>
                        <span class="label-count">${distribution.average}人</span>
                    </div>
                </div>
                <div class="distribution-item pass">
                    <div class="distribution-bar" style="width: ${total > 0 ? (distribution.pass / total) * 100 : 0}%"></div>
                    <div class="distribution-label">
                        <span class="label-text">及格(60-69)</span>
                        <span class="label-count">${distribution.pass}人</span>
                    </div>
                </div>
                <div class="distribution-item fail">
                    <div class="distribution-bar" style="width: ${total > 0 ? (distribution.fail / total) * 100 : 0}%"></div>
                    <div class="distribution-label">
                        <span class="label-text">不及格(<60)</span>
                        <span class="label-count">${distribution.fail}人</span>
                    </div>
                </div>
            </div>
        `;
    },
    
    // 渲染科目对比
    renderSubjectComparison() {
        const subjectStats = {};
        
        this.gradeData.subjects.forEach(subject => {
            const subjectGrades = this.gradeData.currentGrades.filter(g => g.subject === subject);
            if (subjectGrades.length > 0) {
                const scores = subjectGrades.map(g => g.score);
                const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
                subjectStats[subject] = average;
            }
        });
        
        return `
            <div class="subject-chart">
                ${Object.entries(subjectStats).map(([subject, average]) => `
                    <div class="subject-item">
                        <div class="subject-name">${subject}</div>
                        <div class="subject-bar">
                            <div class="subject-fill" style="width: ${average}%"></div>
                        </div>
                        <div class="subject-score">${average.toFixed(1)}</div>
                    </div>
                `).join('')}
            </div>
        `;
    },
    
    // 渲染学生排名
    renderStudentRanking() {
        const studentAverages = this.gradeData.students.map(student => {
            const studentGrades = this.gradeData.currentGrades.filter(g => g.studentId === student.id);
            const average = studentGrades.length > 0 ? 
                studentGrades.reduce((sum, g) => sum + g.score, 0) / studentGrades.length : 0;
            
            return {
                ...student,
                average: average,
                gradeCount: studentGrades.length
            };
        }).sort((a, b) => b.average - a.average);
        
        return `
            <div class="ranking-list">
                ${studentAverages.map((student, index) => `
                    <div class="ranking-item">
                        <div class="ranking-position">
                            <span class="position-number">${index + 1}</span>
                            ${index < 3 ? `<i class="fas fa-medal ranking-medal rank-${index + 1}"></i>` : ''}
                        </div>
                        <div class="ranking-student">
                            <div class="student-name">${student.name}</div>
                            <div class="student-id">${student.studentId}</div>
                        </div>
                        <div class="ranking-score">
                            <span class="score-value">${student.average.toFixed(1)}</span>
                            <span class="score-label">平均分</span>
                        </div>
                        <div class="ranking-actions">
                            <button class="btn btn-sm btn-outline view-report-btn" data-student-id="${student.id}">
                                <i class="fas fa-chart-bar"></i>查看报告
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },
    
    // 渲染进步分析
    renderProgressAnalysis() {
        // 模拟进步数据
        const progressData = [
            { name: '张三', current: 85, previous: 78, change: 7 },
            { name: '李四', current: 82, previous: 76, change: 6 },
            { name: '王五', current: 89, previous: 92, change: -3 },
            { name: '赵六', current: 75, previous: 70, change: 5 }
        ];
        
        return `
            <div class="progress-list">
                ${progressData.map(student => `
                    <div class="progress-item">
                        <div class="progress-student">
                            <span class="student-name">${student.name}</span>
                        </div>
                        <div class="progress-scores">
                            <span class="previous-score">${student.previous}</span>
                            <i class="fas fa-arrow-right"></i>
                            <span class="current-score">${student.current}</span>
                        </div>
                        <div class="progress-change ${student.change >= 0 ? 'positive' : 'negative'}">
                            <i class="fas fa-arrow-${student.change >= 0 ? 'up' : 'down'}"></i>
                            <span>${Math.abs(student.change)}分</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },
    
    // 渲染报告生成
    renderReportGeneration() {
        const container = document.querySelector('#report-generation-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="report-header">
                <h3>学习报告生成</h3>
                <div class="header-actions">
                    <button class="btn btn-primary generate-report-btn">
                        <i class="fas fa-file-alt"></i>生成个人报告
                    </button>
                    <button class="btn btn-outline batch-report-btn">
                        <i class="fas fa-files"></i>批量生成报告
                    </button>
                </div>
            </div>
            
            <div class="report-templates">
                <h4>报告模板</h4>
                <div class="template-grid">
                    <div class="template-card">
                        <div class="template-preview">
                            <i class="fas fa-chart-pie"></i>
                        </div>
                        <div class="template-info">
                            <h5>综合分析报告</h5>
                            <p>包含成绩分析、能力评估、学习建议</p>
                        </div>
                        <div class="template-actions">
                            <button class="btn btn-sm btn-primary use-template-btn" data-template="comprehensive">
                                使用模板
                            </button>
                        </div>
                    </div>
                    
                    <div class="template-card">
                        <div class="template-preview">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="template-info">
                            <h5>进步跟踪报告</h5>
                            <p>重点关注学习进步和趋势分析</p>
                        </div>
                        <div class="template-actions">
                            <button class="btn btn-sm btn-primary use-template-btn" data-template="progress">
                                使用模板
                            </button>
                        </div>
                    </div>
                    
                    <div class="template-card">
                        <div class="template-preview">
                            <i class="fas fa-bullseye"></i>
                        </div>
                        <div class="template-info">
                            <h5>薄弱点分析报告</h5>
                            <p>深入分析学习薄弱环节和改进方案</p>
                        </div>
                        <div class="template-actions">
                            <button class="btn btn-sm btn-primary use-template-btn" data-template="weakness">
                                使用模板
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="recent-reports">
                <h4>最近生成的报告</h4>
                <div class="report-list">
                    <div class="report-item">
                        <div class="report-icon">
                            <i class="fas fa-file-pdf"></i>
                        </div>
                        <div class="report-info">
                            <h5>张三 - 期中考试综合报告</h5>
                            <p>生成时间: 2024-03-20 14:30</p>
                        </div>
                        <div class="report-actions">
                            <button class="btn btn-sm btn-outline">
                                <i class="fas fa-eye"></i>预览
                            </button>
                            <button class="btn btn-sm btn-outline">
                                <i class="fas fa-download"></i>下载
                            </button>
                        </div>
                    </div>
                    
                    <div class="report-item">
                        <div class="report-icon">
                            <i class="fas fa-file-pdf"></i>
                        </div>
                        <div class="report-info">
                            <h5>李四 - 学习进步分析报告</h5>
                            <p>生成时间: 2024-03-19 16:45</p>
                        </div>
                        <div class="report-actions">
                            <button class="btn btn-sm btn-outline">
                                <i class="fas fa-eye"></i>预览
                            </button>
                            <button class="btn btn-sm btn-outline">
                                <i class="fas fa-download"></i>下载
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 重新绑定事件
        const generateBtn = container.querySelector('.generate-report-btn');
        const batchBtn = container.querySelector('.batch-report-btn');
        
        if (generateBtn) {
            generateBtn.addEventListener('click', this.generateReport.bind(this));
        }
        if (batchBtn) {
            batchBtn.addEventListener('click', this.generateBatchReports.bind(this));
        }
    },
    
    // 生成报告
    generateReport() {
        this.showModal('生成学习报告', `
            <form id="generate-report-form">
                <div class="form-group">
                    <label for="report-student">选择学生</label>
                    <select id="report-student" class="form-select" required>
                        <option value="">请选择学生</option>
                        ${this.gradeData.students.map(student => `
                            <option value="${student.id}">${student.name} (${student.studentId})</option>
                        `).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="report-template">报告模板</label>
                    <select id="report-template" class="form-select" required>
                        <option value="comprehensive">综合分析报告</option>
                        <option value="progress">进步跟踪报告</option>
                        <option value="weakness">薄弱点分析报告</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="report-period">报告周期</label>
                    <select id="report-period" class="form-select" required>
                        <option value="current">当前考试</option>
                        <option value="semester">本学期</option>
                        <option value="year">本学年</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="report-subjects">包含科目</label>
                    <div class="subject-checkboxes">
                        ${this.gradeData.subjects.map(subject => `
                            <div class="checkbox-item">
                                <input type="checkbox" id="subject-${subject}" value="${subject}" checked>
                                <label for="subject-${subject}">${subject}</label>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="report-format">输出格式</label>
                    <div class="format-options">
                        <div class="radio-item">
                            <input type="radio" id="format-pdf" name="format" value="pdf" checked>
                            <label for="format-pdf">PDF文档</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="format-word" name="format" value="word">
                            <label for="format-word">Word文档</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="format-html" name="format" value="html">
                            <label for="format-html">网页格式</label>
                        </div>
                    </div>
                </div>
                
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="GradeManagement.closeModal()">取消</button>
                    <button type="submit" class="btn btn-primary">生成报告</button>
                </div>
            </form>
        `);
        
        // 绑定表单提交事件
        document.getElementById('generate-report-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveGeneratedReport();
        });
    },
    
    // 保存生成的报告
    saveGeneratedReport() {
        const studentId = document.getElementById('report-student').value;
        const template = document.getElementById('report-template').value;
        const period = document.getElementById('report-period').value;
        const format = document.querySelector('input[name="format"]:checked').value;
        
        const student = this.gradeData.students.find(s => s.id == studentId);
        if (!student) {
            this.showNotification('请选择学生', 'error');
            return;
        }
        
        this.closeModal();
        this.showLoadingOverlay('正在生成报告...');
        
        setTimeout(() => {
            this.hideLoadingOverlay();
            this.showNotification(`${student.name}的学习报告已生成完成`, 'success');
        }, 3000);
    },
    
    // 批量生成报告
    generateBatchReports() {
        this.showModal('批量生成报告', `
            <form id="batch-report-form">
                <div class="form-group">
                    <label for="batch-students">选择学生</label>
                    <div class="student-selection">
                        <div class="selection-header">
                            <button type="button" class="btn btn-sm btn-outline select-all-btn">全选</button>
                            <button type="button" class="btn btn-sm btn-outline deselect-all-btn">取消全选</button>
                        </div>
                        <div class="student-checkboxes">
                            ${this.gradeData.students.map(student => `
                                <div class="checkbox-item">
                                    <input type="checkbox" id="batch-student-${student.id}" value="${student.id}" checked>
                                    <label for="batch-student-${student.id}">${student.name} (${student.studentId})</label>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="batch-template">报告模板</label>
                    <select id="batch-template" class="form-select" required>
                        <option value="comprehensive">综合分析报告</option>
                        <option value="progress">进步跟踪报告</option>
                        <option value="weakness">薄弱点分析报告</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="batch-format">输出格式</label>
                    <select id="batch-format" class="form-select" required>
                        <option value="pdf">PDF文档</option>
                        <option value="word">Word文档</option>
                        <option value="zip">打包下载</option>
                    </select>
                </div>
                
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="GradeManagement.closeModal()">取消</button>
                    <button type="submit" class="btn btn-primary">开始生成</button>
                </div>
            </form>
        `);
        
        // 绑定选择按钮事件
        document.querySelector('.select-all-btn').addEventListener('click', () => {
            document.querySelectorAll('.student-checkboxes input[type="checkbox"]').forEach(cb => {
                cb.checked = true;
            });
        });
        
        document.querySelector('.deselect-all-btn').addEventListener('click', () => {
            document.querySelectorAll('.student-checkboxes input[type="checkbox"]').forEach(cb => {
                cb.checked = false;
            });
        });
        
        // 绑定表单提交事件
        document.getElementById('batch-report-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveBatchReports();
        });
    },
    
    // 保存批量报告
    saveBatchReports() {
        const selectedStudents = [];
        document.querySelectorAll('.student-checkboxes input:checked').forEach(checkbox => {
            selectedStudents.push(parseInt(checkbox.value));
        });
        
        if (selectedStudents.length === 0) {
            this.showNotification('请至少选择一个学生', 'error');
            return;
        }
        
        this.closeModal();
        this.showLoadingOverlay(`正在为${selectedStudents.length}名学生生成报告...`);
        
        setTimeout(() => {
            this.hideLoadingOverlay();
            this.showNotification(`已成功为${selectedStudents.length}名学生生成报告`, 'success');
        }, 5000);
    },
    
    // 渲染辅导方案
    renderTutoringPlans() {
        const container = document.querySelector('#tutoring-plans-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="tutoring-header">
                <h3>个性化辅导方案</h3>
                <div class="header-actions">
                    <button class="btn btn-primary create-plan-btn">
                        <i class="fas fa-plus"></i>创建辅导方案
                    </button>
                </div>
            </div>
            
            <div class="tutoring-overview">
                <div class="overview-stats">
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-clipboard-list"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${this.tutoringData.plans.length}</h3>
                            <p>辅导方案</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-play-circle"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${this.tutoringData.plans.filter(p => p.status === '进行中').length}</h3>
                            <p>进行中</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${this.tutoringData.plans.filter(p => p.status === '已完成').length}</h3>
                            <p>已完成</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="stat-info">
                            <h3>${this.tutoringData.plans.filter(p => p.status === '待开始').length}</h3>
                            <p>待开始</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="plans-list">
                <h4>辅导方案列表</h4>
                <div class="plan-grid">
                    ${this.tutoringData.plans.map(plan => `
                        <div class="plan-card">
                            <div class="plan-header">
                                <div class="plan-student">
                                    <h5>${plan.studentName}</h5>
                                    <span class="plan-subject">${plan.subject}</span>
                                </div>
                                <div class="plan-status ${plan.status}">${plan.status}</div>
                            </div>
                            
                            <div class="plan-content">
                                <div class="plan-scores">
                                    <div class="score-item">
                                        <span class="score-label">当前成绩</span>
                                        <span class="score-value current">${plan.currentScore}</span>
                                    </div>
                                    <div class="score-arrow">
                                        <i class="fas fa-arrow-right"></i>
                                    </div>
                                    <div class="score-item">
                                        <span class="score-label">目标成绩</span>
                                        <span class="score-value target">${plan.targetScore}</span>
                                    </div>
                                </div>
                                
                                <div class="plan-details">
                                    <div class="detail-item">
                                        <span class="detail-label">薄弱点:</span>
                                        <div class="weak-points">
                                            ${plan.weakPoints.map(point => `
                                                <span class="weak-point-tag">${point}</span>
                                            `).join('')}
                                        </div>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">预计时长:</span>
                                        <span class="detail-value">${plan.duration}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">创建时间:</span>
                                        <span class="detail-value">${plan.createdDate}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="plan-actions">
                                <button class="btn btn-sm btn-outline view-plan-btn" data-plan-id="${plan.id}">
                                    <i class="fas fa-eye"></i>查看详情
                                </button>
                                <button class="btn btn-sm btn-primary edit-plan-btn" data-plan-id="${plan.id}">
                                    <i class="fas fa-edit"></i>编辑
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="recommendations-section">
                <h4>智能推荐</h4>
                <div class="recommendation-list">
                    <div class="recommendation-item">
                        <div class="recommendation-icon">
                            <i class="fas fa-lightbulb"></i>
                        </div>
                        <div class="recommendation-content">
                            <h5>建议为王五创建数学辅导方案</h5>
                            <p>该学生数学成绩有下降趋势，建议重点关注函数和几何部分</p>
                        </div>
                        <div class="recommendation-actions">
                            <button class="btn btn-sm btn-primary create-recommended-plan-btn" data-student-id="3">
                                创建方案
                            </button>
                        </div>
                    </div>
                    
                    <div class="recommendation-item">
                        <div class="recommendation-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="recommendation-content">
                            <h5>钱七英语成绩需要关注</h5>
                            <p>英语成绩低于班级平均水平，建议加强词汇和语法练习</p>
                        </div>
                        <div class="recommendation-actions">
                            <button class="btn btn-sm btn-primary create-recommended-plan-btn" data-student-id="5">
                                创建方案
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 重新绑定事件
        const createBtn = container.querySelector('.create-plan-btn');
        if (createBtn) {
            createBtn.addEventListener('click', this.createTutoringPlan.bind(this));
        }
    },
    
    // 创建辅导方案
    createTutoringPlan() {
        this.showModal('创建个性化辅导方案', `
            <form id="create-plan-form">
                <div class="form-group">
                    <label for="plan-student">选择学生</label>
                    <select id="plan-student" class="form-select" required>
                        <option value="">请选择学生</option>
                        ${this.gradeData.students.map(student => `
                            <option value="${student.id}">${student.name} (${student.studentId})</option>
                        `).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="plan-subject">辅导科目</label>
                    <select id="plan-subject" class="form-select" required>
                        <option value="">请选择科目</option>
                        ${this.gradeData.subjects.map(subject => `
                            <option value="${subject}">${subject}</option>
                        `).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="current-score">当前成绩</label>
                    <input type="number" id="current-score" class="form-input" min="0" max="100" required>
                </div>
                
                <div class="form-group">
                    <label for="target-score">目标成绩</label>
                    <input type="number" id="target-score" class="form-input" min="0" max="100" required>
                </div>
                
                <div class="form-group">
                    <label for="plan-duration">预计时长</label>
                    <select id="plan-duration" class="form-select" required>
                        <option value="2周">2周</option>
                        <option value="4周">4周</option>
                        <option value="6周">6周</option>
                        <option value="8周">8周</option>
                    </select>
                </div>
                
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="GradeManagement.closeModal()">取消</button>
                    <button type="submit" class="btn btn-primary">创建方案</button>
                </div>
            </form>
        `);
        
        // 绑定表单提交事件
        document.getElementById('create-plan-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveTutoringPlan();
        });
    },
    
    // 保存辅导方案
    saveTutoringPlan() {
        const studentId = parseInt(document.getElementById('plan-student').value);
        const subject = document.getElementById('plan-subject').value;
        const currentScore = parseInt(document.getElementById('current-score').value);
        const targetScore = parseInt(document.getElementById('target-score').value);
        const duration = document.getElementById('plan-duration').value;
        
        const student = this.gradeData.students.find(s => s.id === studentId);
        if (!student) {
            this.showNotification('请选择学生', 'error');
            return;
        }
        
        if (targetScore <= currentScore) {
            this.showNotification('目标成绩应高于当前成绩', 'error');
            return;
        }
        
        const newPlan = {
            id: this.tutoringData.plans.length + 1,
            studentId: studentId,
            studentName: student.name,
            subject: subject,
            currentScore: currentScore,
            targetScore: targetScore,
            duration: duration,
            status: '待开始',
            weakPoints: ['待分析'],
            createdDate: new Date().toISOString().split('T')[0]
        };
        
        this.tutoringData.plans.push(newPlan);
        this.closeModal();
        this.renderTutoringPlans();
        this.showNotification('辅导方案创建成功', 'success');
    },
    
    // 查看辅导方案详情
    viewTutoringPlan(planId) {
        const plan = this.tutoringData.plans.find(p => p.id == planId);
        if (!plan) return;
        
        this.showModal(`${plan.studentName} - ${plan.subject}辅导方案`, `
            <div class="plan-detail-modal">
                <div class="plan-overview">
                    <div class="overview-item">
                        <span class="label">学生姓名:</span>
                        <span class="value">${plan.studentName}</span>
                    </div>
                    <div class="overview-item">
                        <span class="label">辅导科目:</span>
                        <span class="value">${plan.subject}</span>
                    </div>
                    <div class="overview-item">
                        <span class="label">当前成绩:</span>
                        <span class="value">${plan.currentScore}分</span>
                    </div>
                    <div class="overview-item">
                        <span class="label">目标成绩:</span>
                        <span class="value">${plan.targetScore}分</span>
                    </div>
                    <div class="overview-item">
                        <span class="label">预计时长:</span>
                        <span class="value">${plan.duration}</span>
                    </div>
                    <div class="overview-item">
                        <span class="label">方案状态:</span>
                        <span class="value status ${plan.status}">${plan.status}</span>
                    </div>
                </div>
                
                <div class="plan-weak-points">
                    <h4>薄弱知识点</h4>
                    <div class="weak-points-list">
                        ${plan.weakPoints.map(point => `
                            <span class="weak-point-tag">${point}</span>
                        `).join('')}
                    </div>
                </div>
                
                <div class="plan-progress">
                    <h4>学习进度</h4>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 30%"></div>
                    </div>
                    <p class="progress-text">已完成 30% (预计还需 ${plan.duration})</p>
                </div>
                
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="GradeManagement.closeModal()">关闭</button>
                    <button type="button" class="btn btn-primary">编辑方案</button>
                </div>
            </div>
        `);
    },
    
    // 显示模态框
    showModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-container">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="GradeManagement.closeModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-content">
                    ${content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 点击背景关闭模态框
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
    
    // 显示通知
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // 自动关闭
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    },
    
    // 显示加载覆盖层
    showLoadingOverlay(message = '加载中...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
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
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    if (typeof GradeManagement !== 'undefined') {
        GradeManagement.init();
    }
});