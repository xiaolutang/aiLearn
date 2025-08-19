// 智能教学助手 - 工作台页面交互脚本

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
});

function initDashboard() {
    // 初始化统计卡片动画
    initStatCards();
    
    // 初始化图表
    initCharts();
    
    // 初始化快速入口卡片交互
    initQuickCards();
    
    // 初始化活动列表
    initActivityList();
}

// 统计卡片动画
function initStatCards() {
    const statCards = document.querySelectorAll('.stat-card');
    
    // 数字动画效果
    statCards.forEach((card, index) => {
        const numberElement = card.querySelector('.stat-number');
        const progressBar = card.querySelector('.progress-bar');
        
        // 延迟动画，创建波浪效果
        setTimeout(() => {
            // 数字计数动画
            animateNumber(numberElement);
            
            // 进度条动画
            if (progressBar) {
                const targetWidth = progressBar.style.width;
                progressBar.style.width = '0%';
                setTimeout(() => {
                    progressBar.style.width = targetWidth;
                }, 200);
            }
        }, index * 150);
    });
}

// 数字计数动画
function animateNumber(element) {
    const finalNumber = element.textContent;
    const isDecimal = finalNumber.includes('.');
    const hasUnit = /[^\d.]/.test(finalNumber);
    
    let numericValue = parseFloat(finalNumber.replace(/[^\d.]/g, ''));
    let unit = finalNumber.replace(/[\d.]/g, '');
    
    let currentNumber = 0;
    const increment = numericValue / 30; // 30帧动画
    
    const timer = setInterval(() => {
        currentNumber += increment;
        
        if (currentNumber >= numericValue) {
            currentNumber = numericValue;
            clearInterval(timer);
        }
        
        let displayNumber = isDecimal ? currentNumber.toFixed(1) : Math.floor(currentNumber);
        element.textContent = displayNumber + unit;
    }, 50);
}

// 图表初始化
function initCharts() {
    // 模拟图表数据
    const trendData = {
        labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        datasets: [{
            label: '学习活跃度',
            data: [65, 78, 82, 75, 88, 92, 85],
            borderColor: '#1890FF',
            backgroundColor: 'rgba(24, 144, 255, 0.1)',
            tension: 0.4
        }]
    };
    
    const subjectData = {
        labels: ['数学', '语文', '英语', '物理'],
        datasets: [{
            data: [85, 92, 78, 88],
            backgroundColor: ['#1890FF', '#52C41A', '#FAAD14', '#722ED1']
        }]
    };
    
    // 创建简单的图表占位符
    createChartPlaceholder('trendChart', '趋势图表');
    createChartPlaceholder('subjectChart', '饼状图表');
}

// 创建图表占位符
function createChartPlaceholder(canvasId, chartType) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // 清空画布
    ctx.clearRect(0, 0, width, height);
    
    // 绘制渐变背景
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, 'rgba(24, 144, 255, 0.1)');
    gradient.addColorStop(1, 'rgba(24, 144, 255, 0.05)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    
    // 绘制网格线
    ctx.strokeStyle = 'rgba(24, 144, 255, 0.1)';
    ctx.lineWidth = 1;
    
    // 垂直网格线
    for (let i = 0; i <= 6; i++) {
        const x = (width / 6) * i;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
    }
    
    // 水平网格线
    for (let i = 0; i <= 4; i++) {
        const y = (height / 4) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
    
    // 绘制示例数据线
    if (chartType === '趋势图表') {
        drawTrendLine(ctx, width, height);
    } else if (chartType === '饼状图表') {
        drawPieChart(ctx, width, height);
    }
}

// 绘制趋势线
function drawTrendLine(ctx, width, height) {
    const points = [
        { x: width * 0.1, y: height * 0.7 },
        { x: width * 0.25, y: height * 0.5 },
        { x: width * 0.4, y: height * 0.3 },
        { x: width * 0.55, y: height * 0.4 },
        { x: width * 0.7, y: height * 0.2 },
        { x: width * 0.85, y: height * 0.25 }
    ];
    
    // 绘制线条
    ctx.strokeStyle = '#1890FF';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    points.forEach((point, index) => {
        if (index === 0) {
            ctx.moveTo(point.x, point.y);
        } else {
            ctx.lineTo(point.x, point.y);
        }
    });
    
    ctx.stroke();
    
    // 绘制数据点
    ctx.fillStyle = '#1890FF';
    points.forEach(point => {
        ctx.beginPath();
        ctx.arc(point.x, point.y, 4, 0, Math.PI * 2);
        ctx.fill();
    });
}

// 绘制饼状图
function drawPieChart(ctx, width, height) {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;
    
    const data = [30, 25, 25, 20]; // 百分比
    const colors = ['#1890FF', '#52C41A', '#FAAD14', '#722ED1'];
    
    let currentAngle = -Math.PI / 2; // 从顶部开始
    
    data.forEach((value, index) => {
        const sliceAngle = (value / 100) * Math.PI * 2;
        
        ctx.fillStyle = colors[index];
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.closePath();
        ctx.fill();
        
        currentAngle += sliceAngle;
    });
}

// 快速入口卡片交互
function initQuickCards() {
    const quickCards = document.querySelectorAll('.quick-card');
    
    quickCards.forEach(card => {
        card.addEventListener('click', function() {
            const module = this.getAttribute('data-module');
            handleQuickCardClick(module);
        });
        
        // 添加涟漪效果
        card.addEventListener('click', function(e) {
            createRippleEffect(this, e);
        });
    });
}

// 处理快速卡片点击
function handleQuickCardClick(module) {
    const modulePages = {
        'lesson-prep': 'lesson-prep.html',
        'classroom': 'classroom.html',
        'grade-management': 'grade-management.html',
        'data-analysis': 'data-analysis.html'
    };
    
    if (modulePages[module]) {
        // 添加加载动画
        showLoadingOverlay();
        
        // 模拟页面跳转延迟
        setTimeout(() => {
            console.log(`导航到: ${modulePages[module]}`);
            hideLoadingOverlay();
            // window.location.href = modulePages[module];
        }, 800);
    }
}

// 创建涟漪效果
function createRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
        z-index: 1;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// 活动列表交互
function initActivityList() {
    const activityItems = document.querySelectorAll('.activity-item');
    
    activityItems.forEach(item => {
        item.addEventListener('click', function() {
            // 添加选中效果
            activityItems.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');
            
            // 显示活动详情
            showActivityDetails(this);
        });
    });
}

// 显示活动详情
function showActivityDetails(activityItem) {
    const title = activityItem.querySelector('h4').textContent;
    const time = activityItem.querySelector('.activity-time').textContent;
    
    console.log(`查看活动详情: ${title} - ${time}`);
    // 这里可以打开模态框或跳转到详情页面
}

// 加载动画
function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>正在加载...</p>
        </div>
    `;
    
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(4px);
    `;
    
    document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// 添加涟漪动画样式
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .activity-item.selected {
        background: linear-gradient(135deg, rgba(24, 144, 255, 0.1) 0%, rgba(24, 144, 255, 0.05) 100%);
        border-left-color: var(--primary-color);
    }
    
    .loading-spinner {
        text-align: center;
        color: var(--text-secondary);
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid rgba(24, 144, 255, 0.1);
        border-left-color: var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 16px;
    }
    
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
`;

document.head.appendChild(rippleStyle);