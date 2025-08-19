// 课堂助手页面交互功能

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initClassroomPage();
});

// 初始化课堂助手页面
function initClassroomPage() {
    initStatusUpdates();
    initStudentMonitoring();
    initInteractionTabs();
    initQuestionForm();
    initToolButtons();
    initAnswerStats();
    loadMockData();
}

// 初始化状态更新
function initStatusUpdates() {
    // 模拟实时状态更新
    setInterval(() => {
        updateClassroomStatus();
        updateStudentStats();
    }, 5000);
}

// 更新课堂状态
function updateClassroomStatus() {
    const statusItems = document.querySelectorAll('.status-item');
    
    statusItems.forEach(item => {
        const valueElement = item.querySelector('.status-value');
        if (valueElement) {
            const currentValue = parseInt(valueElement.textContent);
            // 模拟数据变化
            const change = Math.floor(Math.random() * 3) - 1; // -1, 0, 1
            const newValue = Math.max(0, currentValue + change);
            valueElement.textContent = newValue;
        }
    });
}

// 初始化学生监控
function initStudentMonitoring() {
    const viewButtons = document.querySelectorAll('.view-btn');
    
    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // 移除所有活跃状态
            viewButtons.forEach(b => b.classList.remove('active'));
            // 添加当前按钮的活跃状态
            this.classList.add('active');
            
            // 切换视图
            const viewType = this.dataset.view;
            switchStudentView(viewType);
        });
    });
    
    // 初始化学生卡片事件
    initStudentCards();
}

// 初始化学生卡片
function initStudentCards() {
    const studentCards = document.querySelectorAll('.student-card');
    
    studentCards.forEach(card => {
        // 添加点击事件
        card.addEventListener('click', function() {
            showStudentDetails(this);
        });
        
        // 初始化操作按钮
        const actionBtns = card.querySelectorAll('.action-btn');
        actionBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                handleStudentAction(this, card);
            });
        });
    });
}

// 切换学生视图
function switchStudentView(viewType) {
    const studentsGrid = document.querySelector('.students-grid');
    
    if (viewType === 'grid') {
        studentsGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(200px, 1fr))';
    } else if (viewType === 'list') {
        studentsGrid.style.gridTemplateColumns = '1fr';
    }
    
    // 添加切换动画
    studentsGrid.style.opacity = '0.5';
    setTimeout(() => {
        studentsGrid.style.opacity = '1';
    }, 200);
}

// 显示学生详情
function showStudentDetails(studentCard) {
    const studentName = studentCard.querySelector('.student-info h4').textContent;
    const studentId = studentCard.dataset.studentId;
    
    // 这里可以打开模态框或跳转到详情页
    console.log(`显示学生详情: ${studentName} (ID: ${studentId})`);
    
    // 添加选中效果
    document.querySelectorAll('.student-card').forEach(card => {
        card.classList.remove('selected');
    });
    studentCard.classList.add('selected');
}

// 处理学生操作
function handleStudentAction(button, studentCard) {
    const action = button.dataset.action;
    const studentName = studentCard.querySelector('.student-info h4').textContent;
    
    switch(action) {
        case 'mute':
            toggleStudentMute(studentCard);
            break;
        case 'focus':
            focusOnStudent(studentCard);
            break;
        case 'message':
            sendMessageToStudent(studentCard);
            break;
        default:
            console.log(`执行操作: ${action} for ${studentName}`);
    }
}

// 切换学生静音状态
function toggleStudentMute(studentCard) {
    const muteBtn = studentCard.querySelector('[data-action="mute"]');
    const isMuted = muteBtn.classList.contains('muted');
    
    if (isMuted) {
        muteBtn.classList.remove('muted');
        muteBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    } else {
        muteBtn.classList.add('muted');
        muteBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
    }
}

// 聚焦学生
function focusOnStudent(studentCard) {
    // 移除其他学生的聚焦状态
    document.querySelectorAll('.student-card').forEach(card => {
        card.classList.remove('focused');
    });
    
    // 添加当前学生的聚焦状态
    studentCard.classList.add('focused');
    
    // 滚动到学生卡片
    studentCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// 发送消息给学生
function sendMessageToStudent(studentCard) {
    const studentName = studentCard.querySelector('.student-info h4').textContent;
    const message = prompt(`发送消息给 ${studentName}:`);
    
    if (message) {
        console.log(`发送消息给 ${studentName}: ${message}`);
        // 这里可以实现实际的消息发送功能
    }
}

// 初始化互动标签页
function initInteractionTabs() {
    const tabs = document.querySelectorAll('.interaction-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // 移除所有活跃状态
            tabs.forEach(t => t.classList.remove('active'));
            // 添加当前标签的活跃状态
            this.classList.add('active');
            
            // 切换内容
            const tabType = this.dataset.tab;
            switchInteractionContent(tabType);
        });
    });
}

// 切换互动内容
function switchInteractionContent(tabType) {
    const content = document.querySelector('.interaction-content');
    
    switch(tabType) {
        case 'question':
            content.innerHTML = getQuestionFormHTML();
            break;
        case 'poll':
            content.innerHTML = getPollFormHTML();
            break;
        case 'quiz':
            content.innerHTML = getQuizFormHTML();
            break;
        case 'discussion':
            content.innerHTML = getDiscussionHTML();
            break;
    }
    
    // 重新初始化表单事件
    initQuestionForm();
}

// 获取问答表单HTML
function getQuestionFormHTML() {
    return `
        <div class="question-form">
            <textarea class="question-input" placeholder="输入您的问题..."></textarea>
            <div class="question-options">
                <button class="option-btn" data-type="multiple">选择题</button>
                <button class="option-btn" data-type="text">文本题</button>
                <button class="option-btn" data-type="voice">语音题</button>
            </div>
            <button class="send-question-btn">发送问题</button>
        </div>
    `;
}

// 获取投票表单HTML
function getPollFormHTML() {
    return `
        <div class="question-form">
            <textarea class="question-input" placeholder="输入投票问题..."></textarea>
            <div class="poll-options">
                <input type="text" class="form-input" placeholder="选项 A">
                <input type="text" class="form-input" placeholder="选项 B">
                <input type="text" class="form-input" placeholder="选项 C">
                <input type="text" class="form-input" placeholder="选项 D">
            </div>
            <button class="send-question-btn">发起投票</button>
        </div>
    `;
}

// 获取测验表单HTML
function getQuizFormHTML() {
    return `
        <div class="question-form">
            <textarea class="question-input" placeholder="输入测验题目..."></textarea>
            <div class="quiz-settings">
                <label>时间限制: <input type="number" value="60" min="10" max="300"> 秒</label>
                <label>分值: <input type="number" value="10" min="1" max="100"> 分</label>
            </div>
            <button class="send-question-btn">开始测验</button>
        </div>
    `;
}

// 获取讨论HTML
function getDiscussionHTML() {
    return `
        <div class="discussion-area">
            <div class="discussion-messages">
                <div class="message">
                    <strong>张三:</strong> 这个概念我还不太理解...
                </div>
                <div class="message">
                    <strong>李四:</strong> 我觉得可以这样解释...
                </div>
            </div>
            <div class="discussion-input">
                <input type="text" class="form-input" placeholder="参与讨论...">
                <button class="btn btn-primary">发送</button>
            </div>
        </div>
    `;
}

// 初始化问题表单
function initQuestionForm() {
    const questionInput = document.querySelector('.question-input');
    const optionBtns = document.querySelectorAll('.option-btn');
    const sendBtn = document.querySelector('.send-question-btn');
    
    if (optionBtns.length > 0) {
        optionBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                optionBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
    
    if (sendBtn) {
        sendBtn.addEventListener('click', function() {
            sendQuestion();
        });
    }
}

// 发送问题
function sendQuestion() {
    const questionInput = document.querySelector('.question-input');
    const activeOption = document.querySelector('.option-btn.active');
    
    if (!questionInput.value.trim()) {
        alert('请输入问题内容');
        return;
    }
    
    const questionData = {
        content: questionInput.value,
        type: activeOption ? activeOption.dataset.type : 'text',
        timestamp: new Date().toISOString()
    };
    
    console.log('发送问题:', questionData);
    
    // 清空输入
    questionInput.value = '';
    
    // 显示发送成功提示
    showNotification('问题已发送给所有学生', 'success');
    
    // 模拟更新答题统计
    setTimeout(() => {
        updateAnswerStats();
    }, 2000);
}

// 初始化工具按钮
function initToolButtons() {
    const toolBtns = document.querySelectorAll('.tool-btn');
    const managementBtns = document.querySelectorAll('.management-btn');
    
    toolBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const tool = this.dataset.tool;
            handleToolAction(tool);
        });
    });
    
    managementBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.dataset.action;
            handleManagementAction(action);
        });
    });
}

// 处理工具操作
function handleToolAction(tool) {
    switch(tool) {
        case 'screen-share':
            startScreenShare();
            break;
        case 'whiteboard':
            openWhiteboard();
            break;
        case 'breakout':
            createBreakoutRooms();
            break;
        case 'recording':
            toggleRecording();
            break;
        default:
            console.log(`使用工具: ${tool}`);
    }
}

// 处理管理操作
function handleManagementAction(action) {
    switch(action) {
        case 'mute-all':
            muteAllStudents();
            break;
        case 'end-class':
            endClass();
            break;
        case 'save-session':
            saveSession();
            break;
        default:
            console.log(`执行管理操作: ${action}`);
    }
}

// 开始屏幕共享
function startScreenShare() {
    console.log('开始屏幕共享');
    showNotification('屏幕共享已开始', 'info');
}

// 打开白板
function openWhiteboard() {
    console.log('打开白板');
    showNotification('白板已打开', 'info');
}

// 创建分组讨论
function createBreakoutRooms() {
    console.log('创建分组讨论');
    showNotification('分组讨论房间已创建', 'info');
}

// 切换录制状态
function toggleRecording() {
    const recordingStatus = document.querySelector('.status-item.recording');
    const isRecording = recordingStatus.style.display !== 'none';
    
    if (isRecording) {
        recordingStatus.style.display = 'none';
        showNotification('录制已停止', 'warning');
    } else {
        recordingStatus.style.display = 'flex';
        showNotification('录制已开始', 'success');
    }
}

// 静音所有学生
function muteAllStudents() {
    const studentCards = document.querySelectorAll('.student-card');
    studentCards.forEach(card => {
        const muteBtn = card.querySelector('[data-action="mute"]');
        if (muteBtn && !muteBtn.classList.contains('muted')) {
            muteBtn.classList.add('muted');
            muteBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        }
    });
    showNotification('所有学生已静音', 'info');
}

// 结束课堂
function endClass() {
    if (confirm('确定要结束当前课堂吗？')) {
        console.log('结束课堂');
        showNotification('课堂已结束', 'warning');
    }
}

// 保存会话
function saveSession() {
    console.log('保存会话');
    showNotification('会话已保存', 'success');
}

// 初始化答题统计
function initAnswerStats() {
    // 初始化进度条动画
    const progressBars = document.querySelectorAll('.progress-fill');
    progressBars.forEach(bar => {
        const percentage = bar.dataset.percentage || '0';
        setTimeout(() => {
            bar.style.width = percentage + '%';
        }, 500);
    });
}

// 更新答题统计
function updateAnswerStats() {
    const answerOptions = document.querySelectorAll('.answer-option');
    
    answerOptions.forEach(option => {
        const countElement = option.querySelector('.option-count');
        const percentageElement = option.querySelector('.option-percentage');
        const progressBar = option.querySelector('.progress-fill');
        
        if (countElement) {
            // 模拟答题数据更新
            const currentCount = parseInt(countElement.textContent);
            const newCount = currentCount + Math.floor(Math.random() * 3);
            countElement.textContent = newCount;
            
            // 更新百分比
            const totalStudents = 25; // 假设总学生数
            const percentage = Math.round((newCount / totalStudents) * 100);
            percentageElement.textContent = percentage + '%';
            
            // 更新进度条
            if (progressBar) {
                progressBar.style.width = percentage + '%';
            }
        }
    });
}

// 更新学生统计
function updateStudentStats() {
    const studentCards = document.querySelectorAll('.student-card');
    
    studentCards.forEach(card => {
        const statValues = card.querySelectorAll('.stat-value');
        statValues.forEach(value => {
            const currentValue = parseInt(value.textContent);
            const change = Math.floor(Math.random() * 2); // 0 or 1
            value.textContent = currentValue + change;
        });
    });
}

// 加载模拟数据
function loadMockData() {
    // 模拟学生数据
    const students = [
        { id: 1, name: '张三', status: 'online', avatar: 'Z', participation: 85, questions: 3 },
        { id: 2, name: '李四', status: 'online', avatar: 'L', participation: 92, questions: 5 },
        { id: 3, name: '王五', status: 'offline', avatar: 'W', participation: 67, questions: 1 },
        { id: 4, name: '赵六', status: 'online', avatar: 'Z', participation: 78, questions: 2 },
        { id: 5, name: '钱七', status: 'online', avatar: 'Q', participation: 95, questions: 7 }
    ];
    
    // 更新学生卡片数据
    const studentCards = document.querySelectorAll('.student-card');
    studentCards.forEach((card, index) => {
        if (students[index]) {
            const student = students[index];
            card.dataset.studentId = student.id;
            card.className = `student-card ${student.status}`;
            
            const avatar = card.querySelector('.student-avatar');
            const name = card.querySelector('.student-info h4');
            const status = card.querySelector('.student-info p');
            const participationValue = card.querySelector('.stat-value');
            
            if (avatar) avatar.textContent = student.avatar;
            if (name) name.textContent = student.name;
            if (status) status.textContent = student.status === 'online' ? '在线' : '离线';
            if (participationValue) participationValue.textContent = student.participation;
        }
    });
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 添加样式
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '6px',
        color: 'white',
        fontWeight: '500',
        zIndex: '9999',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease'
    });
    
    // 设置背景色
    const colors = {
        success: '#52c41a',
        error: '#ff4d4f',
        warning: '#faad14',
        info: '#1890ff'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // 添加到页面
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

// 添加CSS样式
const style = document.createElement('style');
style.textContent = `
    .student-card.selected {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2) !important;
    }
    
    .student-card.focused {
        transform: scale(1.02);
        z-index: 10;
    }
    
    .action-btn.muted {
        background: var(--error-color) !important;
        color: white !important;
        border-color: var(--error-color) !important;
    }
    
    .poll-options {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-sm);
        margin: var(--spacing-md) 0;
    }
    
    .quiz-settings {
        display: flex;
        gap: var(--spacing-md);
        margin: var(--spacing-md) 0;
    }
    
    .quiz-settings label {
        display: flex;
        align-items: center;
        gap: var(--spacing-xs);
        font-size: var(--font-size-sm);
    }
    
    .quiz-settings input {
        width: 80px;
        padding: var(--spacing-xs);
        border: 1px solid var(--border-light);
        border-radius: var(--border-radius-sm);
    }
    
    .discussion-area {
        display: flex;
        flex-direction: column;
        height: 300px;
    }
    
    .discussion-messages {
        flex: 1;
        overflow-y: auto;
        padding: var(--spacing-md);
        background: var(--bg-light);
        border-radius: var(--border-radius-md);
        margin-bottom: var(--spacing-md);
    }
    
    .discussion-messages .message {
        margin-bottom: var(--spacing-sm);
        padding: var(--spacing-xs) 0;
        font-size: var(--font-size-sm);
    }
    
    .discussion-input {
        display: flex;
        gap: var(--spacing-sm);
    }
    
    .discussion-input .form-input {
        flex: 1;
    }
`;
document.head.appendChild(style);