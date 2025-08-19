// 智能教学助手2.0 - 数据分析页面交互脚本

class AnalyticsManager {
    constructor() {
        this.charts = {};
        this.currentData = {};
        this.init();
    }

    init() {
        this.loadData();
        this.initCharts();
        this.bindEvents();
        this.updateOverviewCards();
        this.updateInsights();
        this.updateRanking();
        this.updateSuggestions();
    }

    // 加载模拟数据
    loadData() {
        this.currentData = {
            overview: {
                totalStudents: 156,
                averageScore: 87.5,
                excellentRate: 68.2,
                totalHours: 1248
            },
            trends: {
                labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
                datasets: [{
                    label: '平均成绩',
                    data: [82, 85, 88, 86, 89, 87.5],
                    borderColor: '#1890ff',
                    backgroundColor: 'rgba(24, 144, 255, 0.1)',
                    tension: 0.4
                }]
            },
            classComparison: {
                labels: ['一班', '二班', '三班', '四班', '五班'],
                datasets: [{
                    label: '平均分',
                    data: [88, 85, 92, 87, 89],
                    backgroundColor: ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1']
                }]
            },
            subjectDistribution: {
                labels: ['语文', '数学', '英语', '物理', '化学'],
                datasets: [{
                    data: [85, 92, 78, 88, 83],
                    backgroundColor: ['#ff7875', '#73d13d', '#40a9ff', '#b37feb', '#ffb347']
                }]
            },
            behaviorAnalysis: {
                labels: ['课堂参与', '作业完成', '测验表现', '互动频率'],
                datasets: [{
                    label: '表现指数',
                    data: [85, 92, 78, 88],
                    backgroundColor: 'rgba(24, 144, 255, 0.2)',
                    borderColor: '#1890ff',
                    pointBackgroundColor: '#1890ff'
                }]
            },
            ranking: [
                { name: '张小明', class: '三班', score: 96 },
                { name: '李小红', class: '一班', score: 94 },
                { name: '王小华', class: '二班', score: 93 },
                { name: '陈小丽', class: '五班', score: 92 },
                { name: '刘小强', class: '四班', score: 91 }
            ]
        };
    }

    // 初始化图表
    initCharts() {
        // 成绩趋势图
        const trendsCtx = document.getElementById('trendsChart');
        if (trendsCtx) {
            this.charts.trends = new Chart(trendsCtx, {
                type: 'line',
                data: this.currentData.trends,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 70,
                            max: 100
                        }
                    }
                }
            });
        }

        // 班级对比图
        const comparisonCtx = document.getElementById('comparisonChart');
        if (comparisonCtx) {
            this.charts.comparison = new Chart(comparisonCtx, {
                type: 'bar',
                data: this.currentData.classComparison,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 70,
                            max: 100
                        }
                    }
                }
            });
        }

        // 学科分布图
        const distributionCtx = document.getElementById('distributionChart');
        if (distributionCtx) {
            this.charts.distribution = new Chart(distributionCtx, {
                type: 'doughnut',
                data: this.currentData.subjectDistribution,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // 学习行为分析图
        const behaviorCtx = document.getElementById('behaviorChart');
        if (behaviorCtx) {
            this.charts.behavior = new Chart(behaviorCtx, {
                type: 'radar',
                data: this.currentData.behaviorAnalysis,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    }

    // 绑定事件
    bindEvents() {
        // 图表控制按钮
        document.querySelectorAll('.chart-control-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const parent = e.target.closest('.chart-section');
                parent.querySelectorAll('.chart-control-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                const period = e.target.dataset.period;
                this.updateChartData(parent.id, period);
            });
        });

        // 详细报告按钮
        document.getElementById('detailedReportBtn')?.addEventListener('click', () => {
            this.openReportModal();
        });

        // 快速操作按钮
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleQuickAction(action);
            });
        });

        // 报告标签页切换
        document.querySelectorAll('.report-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchReportTab(e.target.dataset.tab);
            });
        });

        // 关闭模态框
        document.querySelectorAll('.modal .close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.closeModal(modal);
            });
        });

        // 点击模态框背景关闭
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });
    }

    // 更新概览卡片
    updateOverviewCards() {
        const data = this.currentData.overview;
        
        // 更新数值
        document.querySelector('[data-card="students"] .card-value').textContent = data.totalStudents;
        document.querySelector('[data-card="average"] .card-value').textContent = data.averageScore;
        document.querySelector('[data-card="excellent"] .card-value').textContent = data.excellentRate + '%';
        document.querySelector('[data-card="hours"] .card-value').textContent = data.totalHours;

        // 添加变化趋势（模拟数据）
        const changes = ['+12', '+2.3', '+5.8', '+156'];
        const changeTypes = ['positive', 'positive', 'positive', 'positive'];
        
        document.querySelectorAll('.card-change').forEach((change, index) => {
            change.textContent = changes[index];
            change.className = `card-change ${changeTypes[index]}`;
        });
    }

    // 更新智能洞察
    updateInsights() {
        const insights = [
            { text: '本月平均成绩较上月提升了', value: '2.3分', trend: 'positive' },
            { text: '优秀率达到', value: '68.2%', trend: 'positive' },
            { text: '数学科目表现最佳，平均分', value: '92分', trend: 'positive' },
            { text: '建议重点关注英语科目提升', value: '', trend: 'warning' }
        ];

        const container = document.querySelector('.insights-content');
        if (container) {
            container.innerHTML = insights.map(insight => `
                <div class="insight-item">
                    <div class="insight-text">
                        ${insight.text}
                        ${insight.value ? `<span class="insight-value">${insight.value}</span>` : ''}
                    </div>
                </div>
            `).join('');
        }
    }

    // 更新排行榜
    updateRanking() {
        const container = document.querySelector('.ranking-list');
        if (container) {
            container.innerHTML = this.currentData.ranking.map((student, index) => {
                const positionClass = index === 0 ? 'top1' : index === 1 ? 'top2' : index === 2 ? 'top3' : 'other';
                return `
                    <li class="ranking-item">
                        <div class="ranking-position ${positionClass}">${index + 1}</div>
                        <div class="ranking-info">
                            <div class="ranking-name">${student.name}</div>
                            <div class="ranking-class">${student.class}</div>
                        </div>
                        <div class="ranking-score">${student.score}</div>
                    </li>
                `;
            }).join('');
        }
    }

    // 更新学习建议
    updateSuggestions() {
        const suggestions = [
            '加强英语听力训练，提升整体英语水平',
            '鼓励学生多参与课堂互动，提高参与度',
            '针对薄弱学科制定个性化学习计划',
            '定期组织学习经验分享会',
            '增加实践性作业，提高应用能力'
        ];

        const container = document.querySelector('.suggestion-list');
        if (container) {
            container.innerHTML = suggestions.map(suggestion => `
                <li class="suggestion-item">
                    <i class="suggestion-icon fas fa-check-circle"></i>
                    <span class="suggestion-text">${suggestion}</span>
                </li>
            `).join('');
        }
    }

    // 更新图表数据
    updateChartData(chartId, period) {
        // 模拟不同时间段的数据
        const periodData = {
            week: {
                labels: ['周一', '周二', '周三', '周四', '周五'],
                data: [85, 87, 86, 89, 88]
            },
            month: {
                labels: ['第1周', '第2周', '第3周', '第4周'],
                data: [84, 86, 88, 87]
            },
            quarter: {
                labels: ['1月', '2月', '3月'],
                data: [82, 85, 88]
            }
        };

        const data = periodData[period] || this.currentData.trends;
        
        // 更新对应图表
        if (chartId.includes('trends') && this.charts.trends) {
            this.charts.trends.data.labels = data.labels;
            this.charts.trends.data.datasets[0].data = data.data;
            this.charts.trends.update();
        }
    }

    // 处理快速操作
    handleQuickAction(action) {
        switch (action) {
            case 'export':
                this.exportData();
                break;
            case 'print':
                this.printReport();
                break;
            case 'share':
                this.shareReport();
                break;
            case 'settings':
                this.openSettings();
                break;
            default:
                console.log('未知操作:', action);
        }
    }

    // 导出数据
    exportData() {
        // 模拟导出功能
        const data = JSON.stringify(this.currentData, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics_report_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showNotification('数据导出成功！', 'success');
    }

    // 打印报告
    printReport() {
        window.print();
    }

    // 分享报告
    shareReport() {
        if (navigator.share) {
            navigator.share({
                title: '数据分析报告',
                text: '智能教学助手数据分析报告',
                url: window.location.href
            });
        } else {
            // 复制链接到剪贴板
            navigator.clipboard.writeText(window.location.href).then(() => {
                this.showNotification('链接已复制到剪贴板！', 'success');
            });
        }
    }

    // 打开设置
    openSettings() {
        this.showNotification('设置功能开发中...', 'info');
    }

    // 打开详细报告模态框
    openReportModal() {
        const modal = document.getElementById('reportModal');
        if (modal) {
            modal.style.display = 'flex';
            this.initReportCharts();
        }
    }

    // 关闭模态框
    closeModal(modal) {
        modal.style.display = 'none';
    }

    // 切换报告标签页
    switchReportTab(tabName) {
        // 更新标签页状态
        document.querySelectorAll('.report-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // 显示对应内容
        document.querySelectorAll('.report-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`).classList.add('active');
    }

    // 初始化报告图表
    initReportCharts() {
        // 这里可以初始化模态框中的图表
        setTimeout(() => {
            const reportChartCtx = document.getElementById('reportChart');
            if (reportChartCtx && !this.charts.report) {
                this.charts.report = new Chart(reportChartCtx, {
                    type: 'line',
                    data: this.currentData.trends,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
        }, 100);
    }

    // 显示通知
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        // 添加样式
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: type === 'success' ? '#f6ffed' : type === 'error' ? '#fff2f0' : '#e6f7ff',
            color: type === 'success' ? '#52c41a' : type === 'error' ? '#ff4d4f' : '#1890ff',
            padding: '12px 16px',
            borderRadius: '6px',
            border: `1px solid ${type === 'success' ? '#b7eb8f' : type === 'error' ? '#ffccc7' : '#91d5ff'}`,
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            zIndex: '10000',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });

        document.body.appendChild(notification);

        // 显示动画
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // 自动隐藏
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new AnalyticsManager();
});

// 导出供其他模块使用
window.AnalyticsManager = AnalyticsManager;