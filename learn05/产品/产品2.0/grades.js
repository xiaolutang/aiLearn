// 成绩管理页面JavaScript

// 全局变量
let currentPage = 1;
let pageSize = 20;
let totalRecords = 156;
let currentView = 'table';
let selectedStudents = [];
let gradesData = [];

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
    loadGradesData();
    bindEvents();
    animateOverviewCards();
});

// 初始化页面
function initializePage() {
    // 设置当前日期
    const now = new Date();
    const dateStr = now.toLocaleDateString('zh-CN');
    
    // 初始化过滤器
    initializeFilters();
    
    // 初始化分页
    updatePagination();
    
    console.log('成绩管理页面初始化完成');
}

// 绑定事件
function bindEvents() {
    // 头部按钮事件
    document.getElementById('addGradeBtn')?.addEventListener('click', openGradeModal);
    document.getElementById('importBtn')?.addEventListener('click', openImportModal);
    document.getElementById('exportBtn')?.addEventListener('click', exportGrades);
    
    // 视图切换
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            switchView(this.dataset.view);
        });
    });
    
    // 过滤器事件
    document.getElementById('classFilter')?.addEventListener('change', applyFilters);
    document.getElementById('subjectFilter')?.addEventListener('change', applyFilters);
    document.getElementById('examFilter')?.addEventListener('change', applyFilters);
    document.getElementById('studentSearch')?.addEventListener('input', searchStudents);
    
    // 表格操作
    document.getElementById('selectAll')?.addEventListener('change', toggleSelectAll);
    document.getElementById('batchEditBtn')?.addEventListener('click', batchEdit);
    document.getElementById('batchDeleteBtn')?.addEventListener('click', batchDelete);
    
    // 分页控件
    document.getElementById('prevPage')?.addEventListener('click', () => changePage(currentPage - 1));
    document.getElementById('nextPage')?.addEventListener('click', () => changePage(currentPage + 1));
    
    // 模态框事件
    bindModalEvents();
    
    // 图表控件事件
    bindChartEvents();
}

// 绑定模态框事件
function bindModalEvents() {
    // 成绩录入模态框
    document.getElementById('closeModal')?.addEventListener('click', closeGradeModal);
    document.getElementById('cancelBtn')?.addEventListener('click', closeGradeModal);
    document.getElementById('saveGradeBtn')?.addEventListener('click', saveGrade);
    
    // 导入模态框
    document.getElementById('closeImportModal')?.addEventListener('click', closeImportModal);
    document.getElementById('cancelImportBtn')?.addEventListener('click', closeImportModal);
    document.getElementById('selectFileBtn')?.addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    document.getElementById('fileInput')?.addEventListener('change', handleFileSelect);
    document.getElementById('confirmImportBtn')?.addEventListener('click', confirmImport);
    
    // 拖拽上传
    const uploadZone = document.getElementById('uploadZone');
    if (uploadZone) {
        uploadZone.addEventListener('dragover', handleDragOver);
        uploadZone.addEventListener('dragleave', handleDragLeave);
        uploadZone.addEventListener('drop', handleFileDrop);
        uploadZone.addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
    }
    
    // 点击模态框背景关闭
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
            }
        });
    });
}

// 绑定图表事件
function bindChartEvents() {
    // 图表科目切换
    document.getElementById('chartSubject')?.addEventListener('change', updateDistributionChart);
    
    // 趋势分析按钮
    document.querySelectorAll('[data-period]').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            updateTrendChart(this.dataset.period);
        });
    });
    
    // 对比分析按钮
    document.querySelectorAll('[data-type]').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('[data-type]').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            updateComparisonChart(this.dataset.type);
        });
    });
}

// 动画显示概览卡片
function animateOverviewCards() {
    const cards = document.querySelectorAll('.overview-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
                
                // 数字动画
                const valueElement = card.querySelector('.card-value');
                if (valueElement) {
                    const target = parseFloat(valueElement.dataset.target);
                    animateNumber(valueElement, 0, target, 1000);
                }
            }, 100);
        }, index * 200);
    });
}

// 数字动画
function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    const isDecimal = end % 1 !== 0;
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (end - start) * easeOutCubic(progress);
        element.textContent = isDecimal ? current.toFixed(1) : Math.floor(current);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// 缓动函数
function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}

// 加载成绩数据
function loadGradesData() {
    // 模拟成绩数据
    gradesData = generateMockGradesData();
    renderGradesTable();
    updateStatistics();
}

// 生成模拟成绩数据
function generateMockGradesData() {
    const data = [];
    const classes = ['高一(1)班', '高一(2)班', '高一(3)班'];
    const names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二'];
    
    for (let i = 1; i <= totalRecords; i++) {
        const math = Math.floor(Math.random() * 40) + 60;
        const chinese = Math.floor(Math.random() * 40) + 60;
        const english = Math.floor(Math.random() * 40) + 60;
        const physics = Math.floor(Math.random() * 40) + 60;
        const total = math + chinese + english + physics;
        const average = (total / 4).toFixed(1);
        
        data.push({
            id: i,
            studentId: `2024${String(i).padStart(3, '0')}`,
            name: names[Math.floor(Math.random() * names.length)] + i,
            class: classes[Math.floor(Math.random() * classes.length)],
            math: math,
            chinese: chinese,
            english: english,
            physics: physics,
            total: total,
            average: parseFloat(average),
            rank: 0
        });
    }
    
    // 计算排名
    data.sort((a, b) => b.total - a.total);
    data.forEach((student, index) => {
        student.rank = index + 1;
    });
    
    return data;
}

// 渲染成绩表格
function renderGradesTable() {
    const tbody = document.getElementById('gradesTableBody');
    if (!tbody) return;
    
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const pageData = gradesData.slice(startIndex, endIndex);
    
    tbody.innerHTML = pageData.map(student => {
        return `
            <tr data-student-id="${student.id}">
                <td>
                    <input type="checkbox" class="student-checkbox" value="${student.id}">
                </td>
                <td>${student.studentId}</td>
                <td>${student.name}</td>
                <td>${student.class}</td>
                <td class="score-cell ${getScoreClass(student.math)}">${student.math}</td>
                <td class="score-cell ${getScoreClass(student.chinese)}">${student.chinese}</td>
                <td class="score-cell ${getScoreClass(student.english)}">${student.english}</td>
                <td class="score-cell ${getScoreClass(student.physics)}">${student.physics}</td>
                <td class="score-cell">${student.total}</td>
                <td class="score-cell">${student.average}</td>
                <td class="rank-cell ${student.rank <= 10 ? 'rank-top' : ''}">${student.rank}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn edit" onclick="editStudent(${student.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete" onclick="deleteStudent(${student.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    // 绑定复选框事件
    tbody.querySelectorAll('.student-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedStudents);
    });
}

// 获取成绩样式类
function getScoreClass(score) {
    if (score >= 90) return 'score-excellent';
    if (score >= 80) return 'score-good';
    if (score >= 70) return 'score-average';
    if (score >= 60) return 'score-below';
    return 'score-fail';
}

// 更新统计信息
function updateStatistics() {
    const totalStudents = gradesData.length;
    const averageScore = gradesData.reduce((sum, student) => sum + student.average, 0) / totalStudents;
    const excellentCount = gradesData.filter(student => student.average >= 90).length;
    const excellentRate = (excellentCount / totalStudents * 100).toFixed(1);
    
    // 更新概览卡片（如果需要实时更新）
    console.log(`统计更新: 学生${totalStudents}人, 平均分${averageScore.toFixed(1)}, 优秀率${excellentRate}%`);
}

// 视图切换
function switchView(view) {
    currentView = view;
    
    // 更新按钮状态
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });
    
    // 切换视图
    const tableView = document.getElementById('tableView');
    const chartView = document.getElementById('chartView');
    
    if (view === 'table') {
        tableView.style.display = 'block';
        chartView.style.display = 'none';
    } else {
        tableView.style.display = 'none';
        chartView.style.display = 'block';
        initializeCharts();
    }
}

// 初始化图表
function initializeCharts() {
    updateDistributionChart();
    updateTrendChart('month');
    updateComparisonChart('average');
}

// 更新分布图表
function updateDistributionChart() {
    const chartContent = document.getElementById('distributionChart');
    if (chartContent) {
        chartContent.innerHTML = '<div style="text-align: center; color: var(--text-muted);">成绩分布图表 (模拟数据)</div>';
    }
}

// 更新趋势图表
function updateTrendChart(period) {
    const chartContent = document.getElementById('trendChart');
    if (chartContent) {
        chartContent.innerHTML = `<div style="text-align: center; color: var(--text-muted);">成绩趋势图表 - ${period} (模拟数据)</div>`;
    }
}

// 更新对比图表
function updateComparisonChart(type) {
    const chartContent = document.getElementById('comparisonChart');
    if (chartContent) {
        chartContent.innerHTML = `<div style="text-align: center; color: var(--text-muted);">班级对比图表 - ${type} (模拟数据)</div>`;
    }
}

// 应用过滤器
function applyFilters() {
    const classFilter = document.getElementById('classFilter')?.value;
    const subjectFilter = document.getElementById('subjectFilter')?.value;
    const examFilter = document.getElementById('examFilter')?.value;
    
    // 这里应该根据过滤条件重新加载数据
    console.log('应用过滤器:', { classFilter, subjectFilter, examFilter });
    
    // 重置到第一页
    currentPage = 1;
    renderGradesTable();
    updatePagination();
}

// 搜索学生
function searchStudents(e) {
    const keyword = e.target.value.toLowerCase();
    
    if (keyword) {
        // 过滤数据
        const filteredData = gradesData.filter(student => 
            student.name.toLowerCase().includes(keyword) || 
            student.studentId.includes(keyword)
        );
        
        // 更新表格显示
        console.log(`搜索结果: ${filteredData.length} 条记录`);
    } else {
        // 显示所有数据
        renderGradesTable();
    }
}

// 分页相关函数
function updatePagination() {
    const totalPages = Math.ceil(totalRecords / pageSize);
    const pageNumbers = document.getElementById('pageNumbers');
    const currentRange = document.getElementById('currentRange');
    const totalCount = document.getElementById('totalCount');
    
    // 更新信息显示
    const startRecord = (currentPage - 1) * pageSize + 1;
    const endRecord = Math.min(currentPage * pageSize, totalRecords);
    
    if (currentRange) currentRange.textContent = `${startRecord}-${endRecord}`;
    if (totalCount) totalCount.textContent = totalRecords;
    
    // 更新页码
    if (pageNumbers) {
        pageNumbers.innerHTML = generatePageNumbers(currentPage, totalPages);
        
        // 绑定页码点击事件
        pageNumbers.querySelectorAll('.page-number').forEach(btn => {
            btn.addEventListener('click', function() {
                const page = parseInt(this.dataset.page);
                changePage(page);
            });
        });
    }
    
    // 更新前后按钮状态
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
}

function generatePageNumbers(current, total) {
    const pages = [];
    const maxVisible = 5;
    
    let start = Math.max(1, current - Math.floor(maxVisible / 2));
    let end = Math.min(total, start + maxVisible - 1);
    
    if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1);
    }
    
    for (let i = start; i <= end; i++) {
        pages.push(`
            <button class="page-number ${i === current ? 'active' : ''}" data-page="${i}">
                ${i}
            </button>
        `);
    }
    
    return pages.join('');
}

function changePage(page) {
    const totalPages = Math.ceil(totalRecords / pageSize);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    renderGradesTable();
    updatePagination();
}

// 选择相关函数
function toggleSelectAll(e) {
    const checkboxes = document.querySelectorAll('.student-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = e.target.checked;
    });
    updateSelectedStudents();
}

function updateSelectedStudents() {
    const checkboxes = document.querySelectorAll('.student-checkbox:checked');
    selectedStudents = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    // 更新全选状态
    const selectAll = document.getElementById('selectAll');
    const allCheckboxes = document.querySelectorAll('.student-checkbox');
    
    if (selectAll) {
        selectAll.indeterminate = selectedStudents.length > 0 && selectedStudents.length < allCheckboxes.length;
        selectAll.checked = selectedStudents.length === allCheckboxes.length && allCheckboxes.length > 0;
    }
    
    // 更新批量操作按钮状态
    const batchEditBtn = document.getElementById('batchEditBtn');
    const batchDeleteBtn = document.getElementById('batchDeleteBtn');
    
    if (batchEditBtn) batchEditBtn.disabled = selectedStudents.length === 0;
    if (batchDeleteBtn) batchDeleteBtn.disabled = selectedStudents.length === 0;
}

// 模态框操作
function openGradeModal() {
    const modal = document.getElementById('gradeModal');
    if (modal) {
        modal.classList.add('show');
        // 清空表单
        document.getElementById('gradeForm')?.reset();
    }
}

function closeGradeModal() {
    const modal = document.getElementById('gradeModal');
    if (modal) {
        modal.classList.remove('show');
    }
}

function saveGrade() {
    const form = document.getElementById('gradeForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const gradeData = {
        studentName: document.getElementById('studentName')?.value,
        studentId: document.getElementById('studentId')?.value,
        studentClass: document.getElementById('studentClass')?.value,
        examType: document.getElementById('examType')?.value,
        mathScore: document.getElementById('mathScore')?.value,
        chineseScore: document.getElementById('chineseScore')?.value,
        englishScore: document.getElementById('englishScore')?.value,
        physicsScore: document.getElementById('physicsScore')?.value
    };
    
    // 验证数据
    if (!gradeData.studentName || !gradeData.studentId) {
        showNotification('请填写学生姓名和学号', 'error');
        return;
    }
    
    // 保存成绩
    console.log('保存成绩:', gradeData);
    showNotification('成绩保存成功', 'success');
    closeGradeModal();
    
    // 重新加载数据
    loadGradesData();
}

// 导入相关函数
function openImportModal() {
    const modal = document.getElementById('importModal');
    if (modal) {
        modal.classList.add('show');
        // 重置导入状态
        document.getElementById('importPreview').style.display = 'none';
        document.getElementById('confirmImportBtn').disabled = true;
    }
}

function closeImportModal() {
    const modal = document.getElementById('importModal');
    if (modal) {
        modal.classList.remove('show');
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

function processFile(file) {
    const allowedTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
        showNotification('不支持的文件格式，请选择 Excel 或 CSV 文件', 'error');
        return;
    }
    
    // 显示预览
    const preview = document.getElementById('importPreview');
    if (preview) {
        preview.style.display = 'block';
        preview.querySelector('.preview-table').innerHTML = `
            <div style="padding: 20px; text-align: center; color: var(--text-muted);">
                文件: ${file.name}<br>
                大小: ${(file.size / 1024).toFixed(1)} KB<br>
                <small>预览功能需要实际的文件解析实现</small>
            </div>
        `;
    }
    
    // 启用确认按钮
    document.getElementById('confirmImportBtn').disabled = false;
}

function confirmImport() {
    showNotification('成绩导入成功', 'success');
    closeImportModal();
    loadGradesData();
}

// 其他操作函数
function exportGrades() {
    showNotification('正在导出成绩报告...', 'info');
    
    // 模拟导出过程
    setTimeout(() => {
        showNotification('成绩报告导出成功', 'success');
    }, 2000);
}

function editStudent(studentId) {
    const student = gradesData.find(s => s.id === studentId);
    if (student) {
        // 填充表单数据
        document.getElementById('studentName').value = student.name;
        document.getElementById('studentId').value = student.studentId;
        document.getElementById('studentClass').value = student.class;
        document.getElementById('mathScore').value = student.math;
        document.getElementById('chineseScore').value = student.chinese;
        document.getElementById('englishScore').value = student.english;
        document.getElementById('physicsScore').value = student.physics;
        
        openGradeModal();
    }
}

function deleteStudent(studentId) {
    if (confirm('确定要删除这条成绩记录吗？')) {
        console.log('删除学生:', studentId);
        showNotification('成绩记录删除成功', 'success');
        loadGradesData();
    }
}

function batchEdit() {
    if (selectedStudents.length === 0) {
        showNotification('请先选择要编辑的学生', 'warning');
        return;
    }
    
    showNotification(`批量编辑 ${selectedStudents.length} 条记录`, 'info');
}

function batchDelete() {
    if (selectedStudents.length === 0) {
        showNotification('请先选择要删除的学生', 'warning');
        return;
    }
    
    if (confirm(`确定要删除选中的 ${selectedStudents.length} 条记录吗？`)) {
        console.log('批量删除:', selectedStudents);
        showNotification(`成功删除 ${selectedStudents.length} 条记录`, 'success');
        selectedStudents = [];
        loadGradesData();
    }
}

// 初始化过滤器
function initializeFilters() {
    // 可以在这里设置默认的过滤器选项
    console.log('过滤器初始化完成');
}

// 通知提示函数
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 12px 16px;
        box-shadow: var(--shadow-medium);
        z-index: 1001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    // 根据类型设置颜色
    switch (type) {
        case 'success':
            notification.style.borderLeftColor = 'var(--success-color)';
            notification.style.borderLeftWidth = '4px';
            break;
        case 'error':
            notification.style.borderLeftColor = 'var(--error-color)';
            notification.style.borderLeftWidth = '4px';
            break;
        case 'warning':
            notification.style.borderLeftColor = 'var(--warning-color)';
            notification.style.borderLeftWidth = '4px';
            break;
        default:
            notification.style.borderLeftColor = 'var(--info-color)';
            notification.style.borderLeftWidth = '4px';
    }
    
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

// 添加通知样式
const notificationStyles = `
.notification-content {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: var(--text-primary);
}

.notification-content i {
    font-size: 16px;
}
`;

// 注入样式
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);