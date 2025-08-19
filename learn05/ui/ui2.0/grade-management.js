/**
 * 成绩管理模块交互逻辑
 * 包含成绩录入、统计分析、学生档案、报告导出等功能的JavaScript实现
 */

class GradeManagementModule {
    constructor() {
        this.currentTab = 'grade-entry';
        this.students = [];
        this.grades = [];
        this.subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治'];
        this.classes = ['高一(1)班', '高一(2)班', '高一(3)班', '高一(4)班'];
        this.semesters = ['2024春季学期', '2023秋季学期', '2023春季学期'];
        
        this.init();
    }

    init() {
        this.initTabs();
        this.initGradeEntry();
        this.initStatistics();
        this.initStudentProfiles();
        this.initReportExport();
        this.loadMockData();
    }

    // 标签页切换
    initTabs() {
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

    onTabChange(tabId) {
        switch(tabId) {
            case 'grade-entry':
                this.refreshGradeTable();
                break;
            case 'statistics':
                this.refreshStatistics();
                break;
            case 'student-profiles':
                this.refreshStudentList();
                break;
            case 'report-export':
                this.refreshExportHistory();
                break;
        }
    }

    // 成绩录入功能
    initGradeEntry() {
        // 配置表单事件
        const configForm = document.querySelector('.config-form');
        if (configForm) {
            configForm.addEventListener('change', () => {
                this.refreshGradeTable();
            });
        }

        // 批量操作按钮
        const batchButtons = document.querySelectorAll('.table-actions .btn');
        batchButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.textContent.trim();
                this.handleBatchAction(action);
            });
        });

        // 成绩输入事件
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('grade-input')) {
                this.handleGradeInput(e.target);
            }
        });
    }

    refreshGradeTable() {
        const tableBody = document.querySelector('.grade-table tbody');
        if (!tableBody) return;

        const selectedClass = document.querySelector('select[name="class"]')?.value || this.classes[0];
        const selectedSubject = document.querySelector('select[name="subject"]')?.value || this.subjects[0];
        const examType = document.querySelector('input[name="examType"]:checked')?.value || 'midterm';

        // 生成学生成绩表格
        const classStudents = this.students.filter(s => s.class === selectedClass);
        
        tableBody.innerHTML = classStudents.map((student, index) => {
            const grade = this.getStudentGrade(student.id, selectedSubject, examType);
            const level = this.getGradeLevel(grade);
            
            return `
                <tr>
                    <td>${index + 1}</td>
                    <td>${student.name}</td>
                    <td>${student.id}</td>
                    <td>
                        <input type="number" 
                               class="grade-input" 
                               data-student="${student.id}" 
                               data-subject="${selectedSubject}"
                               data-exam="${examType}"
                               value="${grade || ''}" 
                               min="0" 
                               max="100" 
                               placeholder="--">
                    </td>
                    <td>
                        <span class="grade-level ${level.toLowerCase()}">${level}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline" onclick="gradeModule.showStudentDetail('${student.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        this.updateTableSummary(classStudents, selectedSubject, examType);
    }

    handleGradeInput(input) {
        const studentId = input.dataset.student;
        const subject = input.dataset.subject;
        const examType = input.dataset.exam;
        const grade = parseFloat(input.value);

        if (isNaN(grade) || grade < 0 || grade > 100) {
            input.classList.add('error');
            return;
        }

        input.classList.remove('error');
        
        // 保存成绩
        this.saveGrade(studentId, subject, examType, grade);
        
        // 更新等级显示
        const row = input.closest('tr');
        const levelCell = row.querySelector('.grade-level');
        const level = this.getGradeLevel(grade);
        levelCell.textContent = level;
        levelCell.className = `grade-level ${level.toLowerCase()}`;
        
        // 更新统计信息
        this.updateTableSummary();
    }

    saveGrade(studentId, subject, examType, grade) {
        const existingIndex = this.grades.findIndex(g => 
            g.studentId === studentId && 
            g.subject === subject && 
            g.examType === examType
        );

        const gradeData = {
            studentId,
            subject,
            examType,
            grade,
            timestamp: new Date().toISOString()
        };

        if (existingIndex >= 0) {
            this.grades[existingIndex] = gradeData;
        } else {
            this.grades.push(gradeData);
        }

        this.showNotification('成绩保存成功', 'success');
    }

    getStudentGrade(studentId, subject, examType) {
        const grade = this.grades.find(g => 
            g.studentId === studentId && 
            g.subject === subject && 
            g.examType === examType
        );
        return grade ? grade.grade : null;
    }

    getGradeLevel(grade) {
        if (!grade) return '--';
        if (grade >= 90) return '优秀';
        if (grade >= 80) return '良好';
        if (grade >= 70) return '中等';
        if (grade >= 60) return '及格';
        return '不及格';
    }

    updateTableSummary() {
        const gradeInputs = document.querySelectorAll('.grade-input');
        const grades = Array.from(gradeInputs)
            .map(input => parseFloat(input.value))
            .filter(grade => !isNaN(grade));

        if (grades.length === 0) return;

        const total = grades.length;
        const average = (grades.reduce((sum, grade) => sum + grade, 0) / total).toFixed(1);
        const highest = Math.max(...grades);
        const lowest = Math.min(...grades);
        const passCount = grades.filter(grade => grade >= 60).length;
        const passRate = ((passCount / total) * 100).toFixed(1);

        const summaryElement = document.querySelector('.table-summary');
        if (summaryElement) {
            summaryElement.innerHTML = `
                <span>总人数: <strong>${total}</strong></span>
                <span>平均分: <strong>${average}</strong></span>
                <span>最高分: <strong>${highest}</strong></span>
                <span>最低分: <strong>${lowest}</strong></span>
                <span>及格率: <strong>${passRate}%</strong></span>
            `;
        }
    }

    handleBatchAction(action) {
        switch(action) {
            case '快速录入':
                this.showQuickEntryModal();
                break;
            case '导入成绩':
                this.showImportModal();
                break;
            case '导出模板':
                this.exportTemplate();
                break;
            case '保存成绩':
                this.saveAllGrades();
                break;
        }
    }

    // 统计分析功能
    initStatistics() {
        // 筛选器事件
        const filterForm = document.querySelector('.analysis-filters');
        if (filterForm) {
            filterForm.addEventListener('change', () => {
                this.refreshStatistics();
            });
        }

        // 图表操作按钮
        document.addEventListener('click', (e) => {
            if (e.target.closest('.chart-actions .btn')) {
                const action = e.target.textContent.trim();
                this.handleChartAction(action, e.target.closest('.chart-card'));
            }
        });
    }

    refreshStatistics() {
        this.updateStatisticsOverview();
        this.updateCharts();
        this.updateAIAnalysis();
    }

    updateStatisticsOverview() {
        const selectedClass = document.querySelector('.analysis-filters select[name="class"]')?.value;
        const selectedSubject = document.querySelector('.analysis-filters select[name="subject"]')?.value;
        
        // 计算统计数据
        const stats = this.calculateStatistics(selectedClass, selectedSubject);
        
        // 更新统计卡片
        const statCards = document.querySelectorAll('.stat-card');
        const statData = [
            { value: stats.totalStudents, label: '学生总数' },
            { value: stats.averageScore.toFixed(1), label: '平均分' },
            { value: `${stats.passRate.toFixed(1)}%`, label: '及格率' },
            { value: `${stats.excellentRate.toFixed(1)}%`, label: '优秀率' }
        ];
        
        statCards.forEach((card, index) => {
            if (statData[index]) {
                const valueElement = card.querySelector('.stat-value');
                const labelElement = card.querySelector('.stat-label');
                if (valueElement) valueElement.textContent = statData[index].value;
                if (labelElement) labelElement.textContent = statData[index].label;
            }
        });
    }

    calculateStatistics(className, subject) {
        let filteredGrades = this.grades;
        
        if (className && className !== 'all') {
            const classStudents = this.students.filter(s => s.class === className);
            const studentIds = classStudents.map(s => s.id);
            filteredGrades = filteredGrades.filter(g => studentIds.includes(g.studentId));
        }
        
        if (subject && subject !== 'all') {
            filteredGrades = filteredGrades.filter(g => g.subject === subject);
        }
        
        const grades = filteredGrades.map(g => g.grade);
        const totalStudents = new Set(filteredGrades.map(g => g.studentId)).size;
        
        return {
            totalStudents,
            averageScore: grades.length > 0 ? grades.reduce((sum, grade) => sum + grade, 0) / grades.length : 0,
            passRate: grades.length > 0 ? (grades.filter(grade => grade >= 60).length / grades.length) * 100 : 0,
            excellentRate: grades.length > 0 ? (grades.filter(grade => grade >= 90).length / grades.length) * 100 : 0
        };
    }

    updateCharts() {
        // 这里应该集成真实的图表库，如Chart.js
        // 暂时显示占位内容
        const chartContents = document.querySelectorAll('.chart-content');
        chartContents.forEach(content => {
            if (!content.querySelector('canvas')) {
                content.innerHTML = `
                    <div class="chart-placeholder">
                        <i class="fas fa-chart-bar fa-3x"></i>
                        <p>图表数据加载中...</p>
                    </div>
                `;
            }
        });
    }

    updateAIAnalysis() {
        const analysisContainer = document.querySelector('.analysis-insights');
        if (!analysisContainer) return;

        const insights = this.generateAIInsights();
        
        analysisContainer.innerHTML = insights.map(insight => `
            <div class="insight-item">
                <div class="insight-title">${insight.title}</div>
                <div class="insight-content">${insight.content}</div>
                ${insight.suggestions ? `
                    <div class="insight-suggestions">
                        <ul>
                            ${insight.suggestions.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    generateAIInsights() {
        return [
            {
                title: '成绩分布分析',
                content: '当前班级成绩呈正态分布，大部分学生成绩集中在70-85分区间。',
                suggestions: [
                    '针对60分以下学生制定个性化辅导计划',
                    '为90分以上学生提供拓展学习资源'
                ]
            },
            {
                title: '学科对比分析',
                content: '数学和物理成绩相对较低，语文和英语成绩表现良好。',
                suggestions: [
                    '加强理科基础知识训练',
                    '增加数理化实践练习时间'
                ]
            },
            {
                title: '进步趋势分析',
                content: '与上次考试相比，整体平均分提升了3.2分，及格率提升了5%。',
                suggestions: [
                    '继续保持当前教学方法',
                    '关注个别退步学生的学习状态'
                ]
            }
        ];
    }

    // 学生档案功能
    initStudentProfiles() {
        // 搜索功能
        const searchForm = document.querySelector('.search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.searchStudents();
            });
        }

        // 筛选器
        const filterSelects = document.querySelectorAll('.search-filters select');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => {
                this.filterStudents();
            });
        });

        // 学生卡片点击事件
        document.addEventListener('click', (e) => {
            if (e.target.closest('.student-card')) {
                const studentId = e.target.closest('.student-card').dataset.studentId;
                this.showStudentDetail(studentId);
            }
        });
    }

    refreshStudentList() {
        const container = document.querySelector('.student-grid');
        if (!container) return;

        container.innerHTML = this.students.map(student => {
            const stats = this.getStudentStats(student.id);
            
            return `
                <div class="student-card" data-student-id="${student.id}">
                    <div class="student-card-header">
                        <div class="student-avatar">${student.name.charAt(0)}</div>
                        <div class="student-info">
                            <div class="student-name">${student.name}</div>
                            <div class="student-id">${student.id}</div>
                        </div>
                        <span class="student-status ${stats.status}">${stats.statusText}</span>
                    </div>
                    <div class="student-metrics">
                        <div class="metric-item">
                            <div class="metric-value">${stats.averageScore}</div>
                            <div class="metric-label">平均分</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${stats.rank}</div>
                            <div class="metric-label">班级排名</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    getStudentStats(studentId) {
        const studentGrades = this.grades.filter(g => g.studentId === studentId);
        const averageScore = studentGrades.length > 0 
            ? (studentGrades.reduce((sum, g) => sum + g.grade, 0) / studentGrades.length).toFixed(1)
            : '--';
        
        let status = 'good';
        let statusText = '良好';
        
        if (averageScore >= 90) {
            status = 'excellent';
            statusText = '优秀';
        } else if (averageScore < 70) {
            status = 'attention';
            statusText = '需关注';
        }
        
        return {
            averageScore,
            rank: Math.floor(Math.random() * 30) + 1, // 模拟排名
            status,
            statusText
        };
    }

    searchStudents() {
        const searchInput = document.querySelector('.search-form input[type="text"]');
        const keyword = searchInput?.value.trim().toLowerCase();
        
        if (!keyword) {
            this.refreshStudentList();
            return;
        }
        
        const filteredStudents = this.students.filter(student => 
            student.name.toLowerCase().includes(keyword) ||
            student.id.toLowerCase().includes(keyword)
        );
        
        this.renderStudentList(filteredStudents);
    }

    filterStudents() {
        const classFilter = document.querySelector('.search-filters select[name="class"]')?.value;
        const statusFilter = document.querySelector('.search-filters select[name="status"]')?.value;
        
        let filteredStudents = this.students;
        
        if (classFilter && classFilter !== 'all') {
            filteredStudents = filteredStudents.filter(s => s.class === classFilter);
        }
        
        if (statusFilter && statusFilter !== 'all') {
            filteredStudents = filteredStudents.filter(s => {
                const stats = this.getStudentStats(s.id);
                return stats.status === statusFilter;
            });
        }
        
        this.renderStudentList(filteredStudents);
    }

    renderStudentList(students) {
        const container = document.querySelector('.student-grid');
        if (!container) return;

        if (students.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-user-slash fa-3x"></i>
                    <p>未找到符合条件的学生</p>
                </div>
            `;
            return;
        }

        container.innerHTML = students.map(student => {
            const stats = this.getStudentStats(student.id);
            
            return `
                <div class="student-card" data-student-id="${student.id}">
                    <div class="student-card-header">
                        <div class="student-avatar">${student.name.charAt(0)}</div>
                        <div class="student-info">
                            <div class="student-name">${student.name}</div>
                            <div class="student-id">${student.id}</div>
                        </div>
                        <span class="student-status ${stats.status}">${stats.statusText}</span>
                    </div>
                    <div class="student-metrics">
                        <div class="metric-item">
                            <div class="metric-value">${stats.averageScore}</div>
                            <div class="metric-label">平均分</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${stats.rank}</div>
                            <div class="metric-label">班级排名</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    showStudentDetail(studentId) {
        const student = this.students.find(s => s.id === studentId);
        if (!student) return;

        const studentGrades = this.grades.filter(g => g.studentId === studentId);
        const stats = this.getStudentStats(studentId);

        const modalContent = `
            <div class="student-detail-content">
                <div class="detail-section">
                    <h4>基本信息</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">姓名</div>
                            <div class="detail-value">${student.name}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">学号</div>
                            <div class="detail-value">${student.id}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">班级</div>
                            <div class="detail-value">${student.class}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">状态</div>
                            <div class="detail-value">
                                <span class="student-status ${stats.status}">${stats.statusText}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>成绩概览</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">平均分</div>
                            <div class="detail-value">${stats.averageScore}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">班级排名</div>
                            <div class="detail-value">${stats.rank}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">考试次数</div>
                            <div class="detail-value">${studentGrades.length}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">最高分</div>
                            <div class="detail-value">${studentGrades.length > 0 ? Math.max(...studentGrades.map(g => g.grade)) : '--'}</div>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>各科成绩</h4>
                    <div class="grade-table-wrapper">
                        <table class="grade-table">
                            <thead>
                                <tr>
                                    <th>科目</th>
                                    <th>期中考试</th>
                                    <th>期末考试</th>
                                    <th>平时成绩</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${this.subjects.map(subject => {
                                    const midterm = studentGrades.find(g => g.subject === subject && g.examType === 'midterm');
                                    const final = studentGrades.find(g => g.subject === subject && g.examType === 'final');
                                    const regular = studentGrades.find(g => g.subject === subject && g.examType === 'regular');
                                    
                                    return `
                                        <tr>
                                            <td>${subject}</td>
                                            <td>${midterm ? midterm.grade : '--'}</td>
                                            <td>${final ? final.grade : '--'}</td>
                                            <td>${regular ? regular.grade : '--'}</td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        this.showModal('学生详情', modalContent);
    }

    // 报告导出功能
    initReportExport() {
        // 报告类型选择
        const reportTypes = document.querySelectorAll('input[name="reportType"]');
        reportTypes.forEach(radio => {
            radio.addEventListener('change', () => {
                this.updateReportPreview();
            });
        });

        // 输出格式选择
        const formatOptions = document.querySelectorAll('input[name="format"]');
        formatOptions.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateExportButton();
            });
        });

        // 导出按钮
        const exportBtn = document.querySelector('.export-config .btn-primary');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportReport();
            });
        }

        // 预览按钮
        const previewBtn = document.querySelector('.preview-actions .btn-outline');
        if (previewBtn) {
            previewBtn.addEventListener('click', () => {
                this.generateReportPreview();
            });
        }
    }

    updateReportPreview() {
        const selectedType = document.querySelector('input[name="reportType"]:checked')?.value;
        const previewContent = document.querySelector('.preview-content');
        
        if (!previewContent) return;
        
        if (selectedType) {
            previewContent.innerHTML = `
                <div class="preview-placeholder">
                    <i class="fas fa-file-alt fa-3x"></i>
                    <p>点击"生成预览"查看${this.getReportTypeName(selectedType)}报告</p>
                </div>
            `;
        }
    }

    getReportTypeName(type) {
        const typeNames = {
            'class-summary': '班级成绩汇总',
            'student-detail': '学生成绩详情',
            'subject-analysis': '学科分析',
            'progress-tracking': '进步跟踪'
        };
        return typeNames[type] || '报告';
    }

    updateExportButton() {
        const selectedFormats = document.querySelectorAll('input[name="format"]:checked');
        const exportBtn = document.querySelector('.export-config .btn-primary');
        
        if (exportBtn) {
            exportBtn.disabled = selectedFormats.length === 0;
        }
    }

    generateReportPreview() {
        const previewContent = document.querySelector('.preview-content');
        if (!previewContent) return;

        previewContent.innerHTML = '<div class="loading"><i class="fas fa-spinner"></i> 生成预览中...</div>';

        setTimeout(() => {
            previewContent.innerHTML = `
                <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h3 style="text-align: center; margin-bottom: 20px;">班级成绩汇总报告</h3>
                    <div style="margin-bottom: 20px;">
                        <strong>班级：</strong> 高一(1)班 &nbsp;&nbsp;
                        <strong>学期：</strong> 2024春季学期 &nbsp;&nbsp;
                        <strong>生成时间：</strong> ${new Date().toLocaleDateString()}
                    </div>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        <thead>
                            <tr style="background: #f5f5f5;">
                                <th style="border: 1px solid #ddd; padding: 8px;">科目</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">平均分</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">及格率</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">优秀率</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td style="border: 1px solid #ddd; padding: 8px;">语文</td><td style="border: 1px solid #ddd; padding: 8px;">82.5</td><td style="border: 1px solid #ddd; padding: 8px;">95%</td><td style="border: 1px solid #ddd; padding: 8px;">25%</td></tr>
                            <tr><td style="border: 1px solid #ddd; padding: 8px;">数学</td><td style="border: 1px solid #ddd; padding: 8px;">78.3</td><td style="border: 1px solid #ddd; padding: 8px;">88%</td><td style="border: 1px solid #ddd; padding: 8px;">20%</td></tr>
                            <tr><td style="border: 1px solid #ddd; padding: 8px;">英语</td><td style="border: 1px solid #ddd; padding: 8px;">85.1</td><td style="border: 1px solid #ddd; padding: 8px;">92%</td><td style="border: 1px solid #ddd; padding: 8px;">30%</td></tr>
                        </tbody>
                    </table>
                    <div style="text-align: center; color: #666; font-size: 12px;">
                        这是报告预览，实际导出的报告将包含更详细的数据和图表
                    </div>
                </div>
            `;
        }, 1500);
    }

    exportReport() {
        const selectedType = document.querySelector('input[name="reportType"]:checked')?.value;
        const selectedFormats = Array.from(document.querySelectorAll('input[name="format"]:checked')).map(cb => cb.value);
        
        if (!selectedType || selectedFormats.length === 0) {
            this.showNotification('请选择报告类型和输出格式', 'warning');
            return;
        }

        this.showNotification('报告导出中...', 'info');

        // 模拟导出过程
        setTimeout(() => {
            const reportName = `${this.getReportTypeName(selectedType)}_${new Date().toLocaleDateString()}`;
            
            // 添加到导出历史
            this.addExportHistory({
                name: reportName,
                type: selectedType,
                formats: selectedFormats,
                date: new Date().toISOString(),
                size: '2.5MB'
            });
            
            this.showNotification('报告导出成功', 'success');
            this.refreshExportHistory();
        }, 2000);
    }

    addExportHistory(report) {
        if (!this.exportHistory) {
            this.exportHistory = [];
        }
        this.exportHistory.unshift(report);
    }

    refreshExportHistory() {
        const historyList = document.querySelector('.history-list');
        if (!historyList || !this.exportHistory) return;

        if (this.exportHistory.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-file-export fa-3x"></i>
                    <p>暂无导出记录</p>
                </div>
            `;
            return;
        }

        historyList.innerHTML = this.exportHistory.map(report => `
            <div class="history-item">
                <div class="history-info">
                    <div class="history-title">${report.name}</div>
                    <div class="history-meta">
                        ${new Date(report.date).toLocaleString()} • ${report.size} • ${report.formats.join(', ')}
                    </div>
                </div>
                <div class="history-actions">
                    <button class="btn btn-sm btn-outline" onclick="gradeModule.downloadReport('${report.name}')">
                        <i class="fas fa-download"></i> 下载
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="gradeModule.deleteReport('${report.name}')">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </div>
            </div>
        `).join('');
    }

    downloadReport(reportName) {
        this.showNotification(`正在下载 ${reportName}`, 'info');
        // 这里应该实现真实的下载逻辑
    }

    deleteReport(reportName) {
        if (confirm(`确定要删除报告 "${reportName}" 吗？`)) {
            this.exportHistory = this.exportHistory.filter(r => r.name !== reportName);
            this.refreshExportHistory();
            this.showNotification('报告已删除', 'success');
        }
    }

    // 模态框功能
    showModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="modal-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // 关闭事件
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    showQuickEntryModal() {
        const content = `
            <form class="quick-entry-form">
                <div class="form-group">
                    <label>选择学生</label>
                    <select name="student" required>
                        <option value="">请选择学生</option>
                        ${this.students.map(s => `<option value="${s.id}">${s.name} (${s.id})</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>科目</label>
                    <select name="subject" required>
                        ${this.subjects.map(s => `<option value="${s}">${s}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>考试类型</label>
                    <select name="examType" required>
                        <option value="midterm">期中考试</option>
                        <option value="final">期末考试</option>
                        <option value="regular">平时成绩</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>成绩</label>
                    <input type="number" name="grade" min="0" max="100" required>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-outline" onclick="this.closest('.modal').remove()">取消</button>
                    <button type="submit" class="btn btn-primary">保存</button>
                </div>
            </form>
        `;

        this.showModal('快速录入成绩', content);

        // 表单提交事件
        document.querySelector('.quick-entry-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            this.saveGrade(
                formData.get('student'),
                formData.get('subject'),
                formData.get('examType'),
                parseFloat(formData.get('grade'))
            );
            
            e.target.closest('.modal').remove();
            this.refreshGradeTable();
        });
    }

    showImportModal() {
        const content = `
            <div class="import-interface">
                <div class="import-steps">
                    <div class="import-step active">
                        <div class="step-number">1</div>
                        <span>上传文件</span>
                    </div>
                    <div class="import-step">
                        <div class="step-number">2</div>
                        <span>数据预览</span>
                    </div>
                    <div class="import-step">
                        <div class="step-number">3</div>
                        <span>导入完成</span>
                    </div>
                </div>
                
                <div class="upload-area">
                    <div class="upload-placeholder">
                        <i class="fas fa-cloud-upload-alt fa-3x"></i>
                        <p>拖拽Excel文件到此处，或点击选择文件</p>
                        <p style="font-size: 12px; color: #999;">支持 .xlsx, .xls 格式</p>
                    </div>
                    <input type="file" accept=".xlsx,.xls" style="display: none;">
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn btn-outline" onclick="this.closest('.modal').remove()">取消</button>
                    <button type="button" class="btn btn-outline">下载模板</button>
                    <button type="button" class="btn btn-primary" disabled>下一步</button>
                </div>
            </div>
        `;

        this.showModal('导入成绩', content);
    }

    exportTemplate() {
        this.showNotification('正在下载成绩录入模板...', 'info');
        // 这里应该实现真实的模板下载逻辑
    }

    saveAllGrades() {
        const gradeInputs = document.querySelectorAll('.grade-input');
        let savedCount = 0;
        
        gradeInputs.forEach(input => {
            const grade = parseFloat(input.value);
            if (!isNaN(grade) && grade >= 0 && grade <= 100) {
                this.saveGrade(
                    input.dataset.student,
                    input.dataset.subject,
                    input.dataset.exam,
                    grade
                );
                savedCount++;
            }
        });
        
        this.showNotification(`成功保存 ${savedCount} 条成绩记录`, 'success');
    }

    // 工具方法
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // 加载模拟数据
    loadMockData() {
        // 模拟学生数据
        this.students = [
            { id: 'S001', name: '张三', class: '高一(1)班' },
            { id: 'S002', name: '李四', class: '高一(1)班' },
            { id: 'S003', name: '王五', class: '高一(1)班' },
            { id: 'S004', name: '赵六', class: '高一(1)班' },
            { id: 'S005', name: '钱七', class: '高一(1)班' },
            { id: 'S006', name: '孙八', class: '高一(2)班' },
            { id: 'S007', name: '周九', class: '高一(2)班' },
            { id: 'S008', name: '吴十', class: '高一(2)班' }
        ];

        // 模拟成绩数据
        this.grades = [];
        this.students.forEach(student => {
            this.subjects.forEach(subject => {
                ['midterm', 'final', 'regular'].forEach(examType => {
                    if (Math.random() > 0.3) { // 70%的概率有成绩
                        this.grades.push({
                            studentId: student.id,
                            subject,
                            examType,
                            grade: Math.floor(Math.random() * 40) + 60, // 60-100分
                            timestamp: new Date().toISOString()
                        });
                    }
                });
            });
        });

        // 模拟导出历史
        this.exportHistory = [
            {
                name: '班级成绩汇总_2024-01-15',
                type: 'class-summary',
                formats: ['PDF', 'Excel'],
                date: '2024-01-15T10:30:00.000Z',
                size: '2.1MB'
            },
            {
                name: '学科分析报告_2024-01-10',
                type: 'subject-analysis',
                formats: ['PDF'],
                date: '2024-01-10T14:20:00.000Z',
                size: '1.8MB'
            }
        ];
    }
}

// 初始化模块
let gradeModule;
document.addEventListener('DOMContentLoaded', () => {
    gradeModule = new GradeManagementModule();
});