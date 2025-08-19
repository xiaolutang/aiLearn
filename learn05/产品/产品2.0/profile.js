// 智能教学助手2.0 - 个人中心页面交互脚本

class ProfileManager {
    constructor() {
        this.isEditing = false;
        this.originalData = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadUserData();
        this.updateActivityList();
        this.initSettings();
    }

    // 绑定事件
    bindEvents() {
        // 编辑资料按钮
        document.getElementById('editProfileBtn')?.addEventListener('click', () => {
            this.toggleEditMode();
        });

        // 保存更改按钮
        document.getElementById('saveChangesBtn')?.addEventListener('click', () => {
            this.saveProfile();
        });

        // 头像点击事件
        document.getElementById('profileAvatar')?.addEventListener('click', () => {
            this.openAvatarModal();
        });

        // 修改密码按钮
        document.getElementById('changePasswordBtn')?.addEventListener('click', () => {
            this.openPasswordModal();
        });

        // 快速操作按钮
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.closest('.quick-action-btn').dataset.action;
                this.handleQuickAction(action);
            });
        });

        // 设置开关
        document.querySelectorAll('.switch input').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                this.handleSettingChange(e.target.id, e.target.checked);
            });
        });

        // 下拉选择
        document.querySelectorAll('.form-select').forEach(select => {
            select.addEventListener('change', (e) => {
                this.handleSettingChange(e.target.id, e.target.value);
            });
        });

        // 密码模态框事件
        this.bindPasswordModalEvents();

        // 头像模态框事件
        this.bindAvatarModalEvents();

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

    // 加载用户数据
    loadUserData() {
        // 模拟用户数据
        this.userData = {
            fullName: '张明华',
            jobTitle: '高级数学教师',
            email: 'zhang.minghua@school.edu.cn',
            phone: '138****8888',
            department: 'math',
            workYears: 8,
            bio: '专注于数学教育8年，擅长运用现代化教学方法，致力于提升学生的数学思维能力和学习兴趣。',
            avatar: 'https://via.placeholder.com/120',
            settings: {
                twoFactorAuth: false,
                emailNotifications: true,
                smsNotifications: true,
                autoSave: true,
                themeMode: 'light',
                language: 'zh-CN'
            }
        };

        // 保存原始数据
        this.originalData = JSON.parse(JSON.stringify(this.userData));

        // 填充表单
        this.populateForm();
    }

    // 填充表单数据
    populateForm() {
        const data = this.userData;
        
        document.getElementById('fullName').value = data.fullName;
        document.getElementById('jobTitle').value = data.jobTitle;
        document.getElementById('email').value = data.email;
        document.getElementById('phone').value = data.phone;
        document.getElementById('department').value = data.department;
        document.getElementById('workYears').value = data.workYears;
        document.getElementById('bio').value = data.bio;

        // 设置项
        document.getElementById('twoFactorAuth').checked = data.settings.twoFactorAuth;
        document.getElementById('emailNotifications').checked = data.settings.emailNotifications;
        document.getElementById('smsNotifications').checked = data.settings.smsNotifications;
        document.getElementById('autoSave').checked = data.settings.autoSave;
        document.getElementById('themeMode').value = data.settings.themeMode;
        document.getElementById('language').value = data.settings.language;
    }

    // 切换编辑模式
    toggleEditMode() {
        this.isEditing = !this.isEditing;
        
        const editBtn = document.getElementById('editProfileBtn');
        const saveBtn = document.getElementById('saveChangesBtn');
        const formElements = document.querySelectorAll('#profileForm input, #profileForm select, #profileForm textarea');

        if (this.isEditing) {
            // 进入编辑模式
            editBtn.style.display = 'none';
            saveBtn.style.display = 'inline-flex';
            
            formElements.forEach(element => {
                element.removeAttribute('readonly');
                element.removeAttribute('disabled');
                element.classList.add('editing');
            });

            this.showNotification('现在可以编辑您的个人信息', 'info');
        } else {
            // 退出编辑模式
            this.exitEditMode();
        }
    }

    // 退出编辑模式
    exitEditMode() {
        this.isEditing = false;
        
        const editBtn = document.getElementById('editProfileBtn');
        const saveBtn = document.getElementById('saveChangesBtn');
        const formElements = document.querySelectorAll('#profileForm input, #profileForm select, #profileForm textarea');

        editBtn.style.display = 'inline-flex';
        saveBtn.style.display = 'none';
        
        formElements.forEach(element => {
            element.setAttribute('readonly', 'readonly');
            if (element.tagName === 'SELECT') {
                element.setAttribute('disabled', 'disabled');
            }
            element.classList.remove('editing');
        });
    }

    // 保存个人资料
    saveProfile() {
        // 收集表单数据
        const formData = {
            fullName: document.getElementById('fullName').value,
            jobTitle: document.getElementById('jobTitle').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            department: document.getElementById('department').value,
            workYears: parseInt(document.getElementById('workYears').value),
            bio: document.getElementById('bio').value
        };

        // 验证数据
        if (!this.validateProfileData(formData)) {
            return;
        }

        // 模拟保存
        setTimeout(() => {
            // 更新用户数据
            Object.assign(this.userData, formData);
            
            // 更新页面显示
            document.getElementById('profileName').textContent = formData.fullName;
            
            // 退出编辑模式
            this.exitEditMode();
            
            this.showNotification('个人信息保存成功！', 'success');
        }, 1000);
    }

    // 验证个人资料数据
    validateProfileData(data) {
        if (!data.fullName.trim()) {
            this.showNotification('请输入姓名', 'error');
            return false;
        }
        
        if (!data.email.trim() || !this.isValidEmail(data.email)) {
            this.showNotification('请输入有效的邮箱地址', 'error');
            return false;
        }
        
        if (data.workYears < 0 || data.workYears > 50) {
            this.showNotification('工作年限应在0-50年之间', 'error');
            return false;
        }
        
        return true;
    }

    // 验证邮箱格式
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // 处理设置变更
    handleSettingChange(settingId, value) {
        this.userData.settings[settingId] = value;
        
        // 特殊处理
        switch (settingId) {
            case 'themeMode':
                this.applyTheme(value);
                break;
            case 'language':
                this.changeLanguage(value);
                break;
            case 'twoFactorAuth':
                if (value) {
                    this.showNotification('两步验证已启用，请查收验证短信', 'success');
                } else {
                    this.showNotification('两步验证已关闭', 'info');
                }
                break;
        }
        
        // 自动保存设置
        this.saveSettings();
    }

    // 应用主题
    applyTheme(theme) {
        document.body.className = document.body.className.replace(/theme-\w+/g, '');
        if (theme !== 'auto') {
            document.body.classList.add(`theme-${theme}`);
        }
        this.showNotification(`已切换到${theme === 'light' ? '浅色' : theme === 'dark' ? '深色' : '自动'}模式`, 'success');
    }

    // 更改语言
    changeLanguage(language) {
        // 模拟语言切换
        this.showNotification(`语言已切换为${language === 'zh-CN' ? '简体中文' : language === 'zh-TW' ? '繁体中文' : 'English'}`, 'success');
    }

    // 保存设置
    saveSettings() {
        // 模拟保存到服务器
        localStorage.setItem('userSettings', JSON.stringify(this.userData.settings));
    }

    // 初始化设置
    initSettings() {
        // 从本地存储加载设置
        const savedSettings = localStorage.getItem('userSettings');
        if (savedSettings) {
            this.userData.settings = { ...this.userData.settings, ...JSON.parse(savedSettings) };
            this.populateForm();
        }
    }

    // 处理快速操作
    handleQuickAction(action) {
        switch (action) {
            case 'backup':
                this.backupData();
                break;
            case 'export':
                this.exportReport();
                break;
            case 'help':
                this.openHelp();
                break;
            case 'feedback':
                this.openFeedback();
                break;
            default:
                console.log('未知操作:', action);
        }
    }

    // 备份数据
    backupData() {
        const data = {
            userData: this.userData,
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `profile_backup_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showNotification('数据备份成功！', 'success');
    }

    // 导出报告
    exportReport() {
        this.showNotification('正在生成个人报告...', 'info');
        // 模拟导出过程
        setTimeout(() => {
            this.showNotification('个人报告导出成功！', 'success');
        }, 2000);
    }

    // 打开帮助
    openHelp() {
        window.open('https://help.example.com', '_blank');
    }

    // 打开反馈
    openFeedback() {
        this.showNotification('反馈功能开发中...', 'info');
    }

    // 更新活动列表
    updateActivityList() {
        const activities = [
            {
                icon: 'fas fa-file-plus',
                title: '创建了新课件',
                desc: '《二次函数的图像与性质》',
                time: '2小时前'
            },
            {
                icon: 'fas fa-chart-line',
                title: '录入了成绩',
                desc: '高一(3)班数学测验',
                time: '5小时前'
            },
            {
                icon: 'fas fa-chalkboard-teacher',
                title: '完成了课堂教学',
                desc: '高一(2)班数学课',
                time: '1天前'
            },
            {
                icon: 'fas fa-users',
                title: '添加了新学生',
                desc: '高一(1)班转入学生',
                time: '2天前'
            },
            {
                icon: 'fas fa-cog',
                title: '更新了个人设置',
                desc: '启用了邮件通知',
                time: '3天前'
            }
        ];

        const container = document.getElementById('activityList');
        if (container) {
            container.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="${activity.icon}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${activity.title}</div>
                        <div class="activity-desc">${activity.desc}</div>
                        <div class="activity-time">${activity.time}</div>
                    </div>
                </div>
            `).join('');
        }
    }

    // 密码模态框事件
    bindPasswordModalEvents() {
        // 确认修改密码
        document.getElementById('confirmPasswordChange')?.addEventListener('click', () => {
            this.changePassword();
        });

        // 密码强度检测
        document.getElementById('newPassword')?.addEventListener('input', (e) => {
            this.checkPasswordStrength(e.target.value);
        });

        // 确认密码验证
        document.getElementById('confirmPassword')?.addEventListener('input', (e) => {
            this.validatePasswordConfirm(e.target.value);
        });
    }

    // 头像模态框事件
    bindAvatarModalEvents() {
        const uploadArea = document.getElementById('uploadArea');
        const avatarInput = document.getElementById('avatarInput');
        const confirmBtn = document.getElementById('confirmAvatarChange');
        const reSelectBtn = document.getElementById('reSelectBtn');

        // 点击上传区域
        uploadArea?.addEventListener('click', () => {
            avatarInput.click();
        });

        // 拖拽上传
        uploadArea?.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea?.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea?.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleAvatarFile(files[0]);
            }
        });

        // 文件选择
        avatarInput?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleAvatarFile(e.target.files[0]);
            }
        });

        // 重新选择
        reSelectBtn?.addEventListener('click', () => {
            this.resetAvatarUpload();
        });

        // 确认更换
        confirmBtn?.addEventListener('click', () => {
            this.confirmAvatarChange();
        });
    }

    // 打开密码模态框
    openPasswordModal() {
        const modal = document.getElementById('passwordModal');
        if (modal) {
            modal.style.display = 'flex';
            // 清空表单
            document.getElementById('passwordForm').reset();
            this.resetPasswordStrength();
        }
    }

    // 打开头像模态框
    openAvatarModal() {
        const modal = document.getElementById('avatarModal');
        if (modal) {
            modal.style.display = 'flex';
            this.resetAvatarUpload();
        }
    }

    // 关闭模态框
    closeModal(modal) {
        modal.style.display = 'none';
    }

    // 修改密码
    changePassword() {
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // 验证
        if (!currentPassword || !newPassword || !confirmPassword) {
            this.showNotification('请填写所有密码字段', 'error');
            return;
        }

        if (newPassword !== confirmPassword) {
            this.showNotification('新密码和确认密码不匹配', 'error');
            return;
        }

        if (newPassword.length < 8) {
            this.showNotification('新密码长度至少8位', 'error');
            return;
        }

        // 模拟密码修改
        setTimeout(() => {
            this.closeModal(document.getElementById('passwordModal'));
            this.showNotification('密码修改成功！', 'success');
        }, 1000);
    }

    // 检查密码强度
    checkPasswordStrength(password) {
        const strengthBar = document.querySelector('.strength-bar');
        const strengthText = document.querySelector('.strength-text');
        
        let strength = 0;
        let strengthLabel = '弱';
        
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        strengthBar.className = 'strength-bar';
        
        if (strength >= 4) {
            strengthBar.classList.add('strong');
            strengthLabel = '强';
        } else if (strength >= 2) {
            strengthBar.classList.add('medium');
            strengthLabel = '中';
        } else if (strength >= 1) {
            strengthBar.classList.add('weak');
            strengthLabel = '弱';
        }
        
        strengthText.textContent = `密码强度：${strengthLabel}`;
    }

    // 重置密码强度
    resetPasswordStrength() {
        const strengthBar = document.querySelector('.strength-bar');
        const strengthText = document.querySelector('.strength-text');
        
        strengthBar.className = 'strength-bar';
        strengthText.textContent = '密码强度：弱';
    }

    // 验证确认密码
    validatePasswordConfirm(confirmPassword) {
        const newPassword = document.getElementById('newPassword').value;
        const confirmInput = document.getElementById('confirmPassword');
        
        if (confirmPassword && newPassword !== confirmPassword) {
            confirmInput.style.borderColor = '#ff4d4f';
        } else {
            confirmInput.style.borderColor = '#d9d9d9';
        }
    }

    // 处理头像文件
    handleAvatarFile(file) {
        // 验证文件类型
        if (!file.type.startsWith('image/')) {
            this.showNotification('请选择图片文件', 'error');
            return;
        }
        
        // 验证文件大小 (2MB)
        if (file.size > 2 * 1024 * 1024) {
            this.showNotification('图片大小不能超过2MB', 'error');
            return;
        }
        
        // 预览图片
        const reader = new FileReader();
        reader.onload = (e) => {
            this.showAvatarPreview(e.target.result);
        };
        reader.readAsDataURL(file);
    }

    // 显示头像预览
    showAvatarPreview(imageSrc) {
        const uploadArea = document.getElementById('uploadArea');
        const preview = document.getElementById('avatarPreview');
        const previewImage = document.getElementById('previewImage');
        const confirmBtn = document.getElementById('confirmAvatarChange');
        
        uploadArea.style.display = 'none';
        preview.style.display = 'block';
        previewImage.src = imageSrc;
        confirmBtn.disabled = false;
        
        this.newAvatarSrc = imageSrc;
    }

    // 重置头像上传
    resetAvatarUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const preview = document.getElementById('avatarPreview');
        const confirmBtn = document.getElementById('confirmAvatarChange');
        const avatarInput = document.getElementById('avatarInput');
        
        uploadArea.style.display = 'block';
        preview.style.display = 'none';
        confirmBtn.disabled = true;
        avatarInput.value = '';
        
        this.newAvatarSrc = null;
    }

    // 确认更换头像
    confirmAvatarChange() {
        if (this.newAvatarSrc) {
            // 更新头像
            document.getElementById('profileAvatar').src = this.newAvatarSrc;
            this.userData.avatar = this.newAvatarSrc;
            
            // 关闭模态框
            this.closeModal(document.getElementById('avatarModal'));
            
            this.showNotification('头像更换成功！', 'success');
        }
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
    new ProfileManager();
});

// 导出供其他模块使用
window.ProfileManager = ProfileManager;