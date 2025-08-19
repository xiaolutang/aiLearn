// 备课助手页面交互功能
class LessonPrepManager {
    constructor() {
        this.currentSlide = 1;
        this.totalSlides = 5;
        this.init();
    }

    init() {
        this.initTabs();
        this.initToolbar();
        this.initAIChat();
        this.initResourceLibrary();
        this.initTemplateLibrary();
        this.initSlideEditor();
        this.initPanelToggles();
    }

    // 标签页切换
    initTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const target = btn.dataset.tab;
                
                // 移除所有活动状态
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                // 添加活动状态
                btn.classList.add('active');
                document.getElementById(target).classList.add('active');
            });
        });
    }

    // 工具栏功能
    initToolbar() {
        const toolbarBtns = document.querySelectorAll('.toolbar-btn');
        
        toolbarBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleToolbarAction(action, btn);
            });
        });
    }

    handleToolbarAction(action, btn) {
        switch(action) {
            case 'bold':
            case 'italic':
            case 'underline':
                btn.classList.toggle('active');
                document.execCommand(action);
                break;
            case 'align-left':
            case 'align-center':
            case 'align-right':
                document.querySelectorAll('[data-action^="align-"]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.execCommand('justify' + action.split('-')[1]);
                break;
            case 'list-ul':
                btn.classList.toggle('active');
                document.execCommand('insertUnorderedList');
                break;
            case 'list-ol':
                btn.classList.toggle('active');
                document.execCommand('insertOrderedList');
                break;
            case 'image':
                this.insertImage();
                break;
            case 'link':
                this.insertLink();
                break;
        }
    }

    insertImage() {
        const url = prompt('请输入图片URL:');
        if (url) {
            document.execCommand('insertImage', false, url);
        }
    }

    insertLink() {
        const url = prompt('请输入链接URL:');
        if (url) {
            document.execCommand('createLink', false, url);
        }
    }

    // AI聊天功能
    initAIChat() {
        const chatInput = document.querySelector('.ai-chat .form-input');
        const sendBtn = document.querySelector('.ai-chat .btn-primary');
        const promptBtns = document.querySelectorAll('.prompt-btn');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendMessage(chatInput.value);
                chatInput.value = '';
            });
        }
        
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage(chatInput.value);
                    chatInput.value = '';
                }
            });
        }
        
        promptBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.sendMessage(btn.textContent);
            });
        });
    }

    sendMessage(message) {
        if (!message.trim()) return;
        
        const chatMessages = document.querySelector('.chat-messages');
        
        // 添加用户消息
        this.addMessage(chatMessages, 'user', message);
        
        // 模拟AI回复
        setTimeout(() => {
            const aiResponse = this.generateAIResponse(message);
            this.addMessage(chatMessages, 'ai', aiResponse);
        }, 1000);
    }

    addMessage(container, type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? 'U' : 'AI';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `<p>${content}</p>`;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        container.appendChild(messageDiv);
        
        // 滚动到底部
        container.scrollTop = container.scrollHeight;
    }

    generateAIResponse(message) {
        const responses = {
            '生成课件大纲': '我为您生成了一个关于"数学函数"的课件大纲：<ul><li>函数的定义与概念</li><li>函数的表示方法</li><li>函数的性质</li><li>常见函数类型</li><li>函数的应用实例</li></ul>',
            '推荐教学资源': '根据您的课程内容，我推荐以下资源：<ul><li>互动数学工具：GeoGebra</li><li>视频资源：Khan Academy数学课程</li><li>练习题库：数学竞赛题集</li><li>课件模板：现代简约风格模板</li></ul>',
            '优化教学方法': '针对这个主题，建议采用以下教学方法：<ul><li>问题导入法：从实际问题引入函数概念</li><li>可视化教学：使用图表和动画展示函数关系</li><li>互动练习：设计小组讨论和实践活动</li><li>分层教学：为不同水平学生提供差异化内容</li></ul>'
        };
        
        return responses[message] || '感谢您的提问！我正在为您分析课程内容，稍后会为您提供详细的建议和资源推荐。';
    }

    // 资源库功能
    initResourceLibrary() {
        const resourceTabs = document.querySelectorAll('.resource-tab');
        const searchInput = document.querySelector('.resource-search input');
        
        resourceTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                resourceTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.loadResourcesByType(tab.dataset.type);
            });
        });
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchResources(e.target.value);
            });
        }
    }

    loadResourcesByType(type) {
        const resourceGrid = document.querySelector('.resource-grid');
        const resources = this.getResourcesByType(type);
        
        resourceGrid.innerHTML = resources.map(resource => `
            <div class="resource-item" data-id="${resource.id}">
                <div class="resource-preview">
                    <i class="${resource.icon}"></i>
                </div>
                <div class="resource-info">
                    <span class="resource-name">${resource.name}</span>
                    <span class="resource-size">${resource.size}</span>
                </div>
            </div>
        `).join('');
        
        // 添加点击事件
        resourceGrid.querySelectorAll('.resource-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectResource(item.dataset.id);
            });
        });
    }

    getResourcesByType(type) {
        const allResources = {
            images: [
                { id: 1, name: '函数图像.png', size: '256KB', icon: 'fas fa-image' },
                { id: 2, name: '数学公式.jpg', size: '128KB', icon: 'fas fa-image' },
                { id: 3, name: '几何图形.svg', size: '64KB', icon: 'fas fa-image' }
            ],
            videos: [
                { id: 4, name: '函数概念讲解.mp4', size: '15.2MB', icon: 'fas fa-video' },
                { id: 5, name: '实例演示.mp4', size: '8.7MB', icon: 'fas fa-video' }
            ],
            documents: [
                { id: 6, name: '教学大纲.pdf', size: '2.1MB', icon: 'fas fa-file-pdf' },
                { id: 7, name: '练习题集.docx', size: '1.5MB', icon: 'fas fa-file-word' },
                { id: 8, name: '参考资料.pptx', size: '3.2MB', icon: 'fas fa-file-powerpoint' }
            ]
        };
        
        return allResources[type] || [];
    }

    searchResources(query) {
        // 实现资源搜索功能
        console.log('搜索资源:', query);
    }

    selectResource(resourceId) {
        console.log('选择资源:', resourceId);
        // 实现资源选择功能
    }

    // 模板库功能
    initTemplateLibrary() {
        const templateGrid = document.querySelector('.template-grid');
        
        if (templateGrid) {
            templateGrid.addEventListener('click', (e) => {
                const templateItem = e.target.closest('.template-item');
                if (templateItem) {
                    this.selectTemplate(templateItem.dataset.id);
                }
            });
        }
    }

    selectTemplate(templateId) {
        console.log('选择模板:', templateId);
        // 实现模板选择功能
    }

    // 幻灯片编辑器
    initSlideEditor() {
        const slideThumbnails = document.querySelectorAll('.slide-thumbnail');
        
        slideThumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', () => {
                slideThumbnails.forEach(t => t.classList.remove('active'));
                thumbnail.classList.add('active');
                this.loadSlide(thumbnail.dataset.slide);
            });
        });
    }

    loadSlide(slideNumber) {
        this.currentSlide = parseInt(slideNumber);
        console.log('加载幻灯片:', slideNumber);
        // 实现幻灯片加载功能
    }

    // 面板折叠功能
    initPanelToggles() {
        const panelToggles = document.querySelectorAll('.panel-toggle');
        
        panelToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                const panel = toggle.closest('.sidebar-panel');
                const content = panel.querySelector('.panel-content');
                
                if (content.style.display === 'none') {
                    content.style.display = 'block';
                    toggle.innerHTML = '<i class="fas fa-chevron-up"></i>';
                } else {
                    content.style.display = 'none';
                    toggle.innerHTML = '<i class="fas fa-chevron-down"></i>';
                }
            });
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new LessonPrepManager();
});

// 工具卡片点击效果
document.addEventListener('DOMContentLoaded', () => {
    const toolCards = document.querySelectorAll('.tool-card');
    
    toolCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // 创建涟漪效果
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
            
            // 模拟功能跳转
            const toolType = this.dataset.tool;
            console.log('点击工具:', toolType);
        });
    });
});

// 添加涟漪效果样式
const style = document.createElement('style');
style.textContent = `
    .tool-card {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);