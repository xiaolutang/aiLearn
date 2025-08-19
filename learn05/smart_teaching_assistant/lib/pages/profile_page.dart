import 'package:flutter/material.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  String selectedMenuItem = 'basic_info';
  
  // 表单控制器
  final _nameController = TextEditingController(text: '张老师');
  final _phoneController = TextEditingController(text: '138****8888');
  final _emailController = TextEditingController(text: 'zhang@school.edu.cn');
  final _schoolController = TextEditingController(text: '北京市第一中学');
  final _teacherIdController = TextEditingController(text: 'T20220001');
  final _officeController = TextEditingController(text: '教学楼3楼301室');
  final _officePhoneController = TextEditingController(text: '010-12345678');
  final _addressController = TextEditingController(text: '北京市朝阳区xxx街道xxx号');
  final _bioController = TextEditingController(text: '热爱教育事业，专注于高中数学教学，具有丰富的教学经验和扎实的专业基础。致力于培养学生的数学思维和解题能力，注重因材施教，关注每一位学生的成长。');
  
  String selectedGender = 'female';
  String selectedSubject = 'math';
  String selectedGrade = 'grade1';
  String selectedPosition = 'teacher';
  
  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _schoolController.dispose();
    _teacherIdController.dispose();
    _officeController.dispose();
    _officePhoneController.dispose();
    _addressController.dispose();
    _bioController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: _buildAppBar(),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              _buildPageHeader(),
              const SizedBox(height: 24),
              _buildProfileCard(),
              const SizedBox(height: 24),
              _buildContentLayout(),
            ],
          ),
        ),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: Colors.white,
      elevation: 0,
      shadowColor: Colors.black.withOpacity(0.06),
      surfaceTintColor: Colors.transparent,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back, color: Color(0xFF262626)),
        onPressed: () => Navigator.pop(context),
      ),
      title: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF1890FF), Color(0xFF096DD9)],
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Center(
              child: Text('🎓', style: TextStyle(fontSize: 16)),
            ),
          ),
          const SizedBox(width: 12),
          const Text(
            '智能教学助手',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Color(0xFF262626),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPageHeader() {
    return Row(
      children: [
        Text(
          '个人中心',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w600,
            color: Color(0xFF262626),
          ),
        ),
      ],
    );
  }

  Widget _buildProfileCard() {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF1890FF), Color(0xFF096DD9)],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF1890FF).withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Stack(
        children: [
          // 背景装饰
          Positioned(
            top: -150,
            right: -60,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
            ),
          ),
          // 内容
          Padding(
            padding: const EdgeInsets.all(32),
            child: Row(
              children: [
                // 头像
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: Colors.white.withOpacity(0.3),
                      width: 3,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: const Center(
                    child: Text(
                      '张',
                      style: TextStyle(
                        fontSize: 32,
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 24),
                // 个人信息
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '张老师',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '高中数学教师',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.white.withOpacity(0.9),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '北京市第一中学',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white.withOpacity(0.8),
                        ),
                      ),
                    ],
                  ),
                ),
                // 统计数据
                Row(
                  children: [
                    _buildStatItem('3', '任教班级'),
                    const SizedBox(width: 32),
                    _buildStatItem('156', '学生总数'),
                    const SizedBox(width: 32),
                    _buildStatItem('2.5', '教龄(年)'),
                  ],
                ),
                const SizedBox(width: 24),
                // 编辑按钮
                GestureDetector(
                  onTap: () {
                    // TODO: 编辑资料功能
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      border: Border.all(
                        color: Colors.white.withOpacity(0.4),
                        width: 1.5,
                      ),
                      borderRadius: BorderRadius.circular(10),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.15),
                          blurRadius: 8,
                          offset: const Offset(0, 3),
                        ),
                      ],
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Text(
                          '✏️',
                          style: TextStyle(fontSize: 14),
                        ),
                        const SizedBox(width: 6),
                        const Text(
                          '编辑资料',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.white,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String number, String label) {
    return Column(
      children: [
        Text(
          number,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.white.withOpacity(0.8),
          ),
        ),
      ],
    );
  }

  Widget _buildContentLayout() {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth > 1024) {
          // 桌面布局
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: 300,
                child: _buildSidebarMenu(),
              ),
              const SizedBox(width: 24),
              Expanded(
                child: _buildContentArea(),
              ),
            ],
          );
        } else {
          // 移动端布局
          return Column(
            children: [
              _buildContentArea(),
              const SizedBox(height: 24),
              _buildSidebarMenu(),
            ],
          );
        }
      },
    );
  }

  Widget _buildSidebarMenu() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildMenuSection(
            '个人信息',
            [
              _buildMenuItem('👤', '基本信息', 'basic_info'),
              _buildMenuItem('🔒', '安全设置', 'security'),
              _buildMenuItem('📊', '教学统计', 'statistics'),
            ],
          ),
          _buildMenuSection(
            '系统设置',
            [
              _buildMenuItem('⚙️', '偏好设置', 'preferences'),
              _buildMenuItem('🔔', '通知设置', 'notifications'),
              _buildMenuItem('🎨', '界面设置', 'interface'),
            ],
          ),
          _buildMenuSection(
            '其他',
            [
              _buildMenuItem('❓', '帮助中心', 'help'),
              _buildMenuItem('📝', '意见反馈', 'feedback'),
              _buildMenuItem('ℹ️', '关于我们', 'about'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMenuSection(String title, List<Widget> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 12),
          child: Text(
            title.toUpperCase(),
            style: const TextStyle(
              fontSize: 12,
              color: Color(0xFF8C8C8C),
              fontWeight: FontWeight.w500,
              letterSpacing: 0.5,
            ),
          ),
        ),
        ...items,
        const SizedBox(height: 12),
      ],
    );
  }

  Widget _buildMenuItem(String icon, String title, String key) {
    final isActive = selectedMenuItem == key;
    
    return GestureDetector(
      onTap: () {
        setState(() {
          selectedMenuItem = key;
        });
      },
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFFE6F7FF) : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: isActive
              ? Border.all(
                  color: const Color(0xFF91D5FF),
                  width: 1,
                )
              : null,
          boxShadow: isActive ? [
            BoxShadow(
              color: const Color(0xFF1890FF).withOpacity(0.1),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ] : null,
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            children: [
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: isActive ? const Color(0xFF1890FF).withOpacity(0.1) : Colors.transparent,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Center(
                  child: Text(
                    icon,
                    style: const TextStyle(fontSize: 16),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                title,
                style: TextStyle(
                  fontSize: 14,
                  color: isActive ? const Color(0xFF1890FF) : const Color(0xFF595959),
                  fontWeight: isActive ? FontWeight.w500 : FontWeight.normal,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildContentArea() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildContentHeader(),
          _buildContentBody(),
        ],
      ),
    );
  }

  Widget _buildContentHeader() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: Color(0xFFF0F0F0),
          ),
        ),
      ),
      child: Row(
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _getContentTitle(),
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF262626),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                _getContentSubtitle(),
                style: const TextStyle(
                  fontSize: 14,
                  color: Color(0xFF8C8C8C),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _getContentTitle() {
    switch (selectedMenuItem) {
      case 'basic_info':
        return '基本信息';
      case 'security':
        return '安全设置';
      case 'statistics':
        return '教学统计';
      case 'preferences':
        return '偏好设置';
      case 'notifications':
        return '通知设置';
      case 'interface':
        return '界面设置';
      case 'help':
        return '帮助中心';
      case 'feedback':
        return '意见反馈';
      case 'about':
        return '关于我们';
      default:
        return '基本信息';
    }
  }

  String _getContentSubtitle() {
    switch (selectedMenuItem) {
      case 'basic_info':
        return '管理您的个人信息和教学资料';
      case 'security':
        return '管理您的账户安全设置';
      case 'statistics':
        return '查看您的教学数据统计';
      case 'preferences':
        return '自定义您的使用偏好';
      case 'notifications':
        return '管理通知和提醒设置';
      case 'interface':
        return '自定义界面主题和布局';
      case 'help':
        return '获取使用帮助和支持';
      case 'feedback':
        return '向我们提供宝贵的意见和建议';
      case 'about':
        return '了解更多关于智能教学助手';
      default:
        return '管理您的个人信息和教学资料';
    }
  }

  Widget _buildContentBody() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: _getContentWidget(),
    );
  }

  Widget _getContentWidget() {
    switch (selectedMenuItem) {
      case 'basic_info':
        return _buildBasicInfoForm();
      case 'security':
        return _buildSecuritySettings();
      case 'statistics':
        return _buildTeachingStatistics();
      case 'preferences':
        return _buildPreferences();
      case 'notifications':
        return _buildNotificationSettings();
      case 'interface':
        return _buildInterfaceSettings();
      case 'help':
        return _buildHelpCenter();
      case 'feedback':
        return _buildFeedback();
      case 'about':
        return _buildAbout();
      default:
        return _buildBasicInfoForm();
    }
  }

  Widget _buildBasicInfoForm() {
    return Column(
      children: [
        _buildFormSection(
          '👤',
          '个人信息',
          [
            Row(
              children: [
                Expanded(
                  child: _buildFormItem('姓名', _nameController),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: _buildDropdownItem(
                    '性别',
                    selectedGender,
                    [
                      DropdownMenuItem(value: 'male', child: Text('男')),
                      DropdownMenuItem(value: 'female', child: Text('女')),
                    ],
                    (value) => setState(() => selectedGender = value!),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: _buildFormItem('手机号码', _phoneController),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: _buildFormItem('邮箱地址', _emailController),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: _buildDateFormItem('出生日期', '1990-05-15'),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: _buildFormItem('身份证号', TextEditingController(text: '110101199005****')),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 32),
        _buildFormSection(
          '🏫',
          '工作信息',
          [
            Row(
              children: [
                Expanded(
                  child: _buildFormItem('学校名称', _schoolController),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: _buildDropdownItem(
                    '任教学科',
                    selectedSubject,
                    [
                      DropdownMenuItem(value: 'math', child: Text('数学')),
                      DropdownMenuItem(value: 'chinese', child: Text('语文')),
                      DropdownMenuItem(value: 'english', child: Text('英语')),
                      DropdownMenuItem(value: 'physics', child: Text('物理')),
                      DropdownMenuItem(value: 'chemistry', child: Text('化学')),
                    ],
                    (value) => setState(() => selectedSubject = value!),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: _buildDropdownItem(
                    '任教年级',
                    selectedGrade,
                    [
                      DropdownMenuItem(value: 'grade1', child: Text('高一')),
                      DropdownMenuItem(value: 'grade2', child: Text('高二')),
                      DropdownMenuItem(value: 'grade3', child: Text('高三')),
                    ],
                    (value) => setState(() => selectedGrade = value!),
                  ),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: _buildFormItem('教师编号', _teacherIdController),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: _buildDateFormItem('入职时间', '2022-09-01'),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: _buildDropdownItem(
                    '职务',
                    selectedPosition,
                    [
                      DropdownMenuItem(value: 'teacher', child: Text('任课教师')),
                      DropdownMenuItem(value: 'head_teacher', child: Text('班主任')),
                      DropdownMenuItem(value: 'department_head', child: Text('教研组长')),
                      DropdownMenuItem(value: 'vice_principal', child: Text('副校长')),
                      DropdownMenuItem(value: 'principal', child: Text('校长')),
                    ],
                    (value) => setState(() => selectedPosition = value!),
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 32),
        _buildFormSection(
          '📍',
          '联系信息',
          [
            Row(
              children: [
                Expanded(
                  child: _buildFormItem('办公室地址', _officeController),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: _buildFormItem('办公电话', _officePhoneController),
                ),
              ],
            ),
            const SizedBox(height: 20),
            _buildFormItem('家庭住址', _addressController),
            const SizedBox(height: 20),
            _buildTextAreaItem('个人简介', _bioController),
          ],
        ),
        const SizedBox(height: 24),
        _buildFormActions(),
      ],
    );
  }

  Widget _buildFormSection(String icon, String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              icon,
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(width: 8),
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Color(0xFF262626),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        ...children,
      ],
    );
  }

  Widget _buildFormItem(String label, TextEditingController controller) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            color: Color(0xFF262626),
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFF1890FF), width: 2),
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildDropdownItem(
    String label,
    String value,
    List<DropdownMenuItem<String>> items,
    ValueChanged<String?> onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            color: Color(0xFF262626),
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        DropdownButtonFormField<String>(
          value: value,
          items: items,
          onChanged: onChanged,
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFF1890FF), width: 2),
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildDateFormItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            color: Color(0xFF262626),
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: TextEditingController(text: value),
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFF1890FF), width: 2),
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            suffixIcon: const Icon(Icons.calendar_today, size: 20),
          ),
          readOnly: true,
          onTap: () {
            // TODO: 实现日期选择器
          },
        ),
      ],
    );
  }

  Widget _buildTextAreaItem(String label, TextEditingController controller) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            color: Color(0xFF262626),
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          maxLines: 4,
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: Color(0xFF1890FF), width: 2),
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildFormActions() {
    return Container(
      padding: const EdgeInsets.only(top: 24),
      decoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: Color(0xFFF0F0F0)),
        ),
      ),
      child: Row(
        children: [
          ElevatedButton.icon(
            onPressed: () {
              // TODO: 保存修改
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('保存成功')),
              );
            },
            icon: const Text('💾'),
            label: const Text('保存修改'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1890FF),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              elevation: 2,
              shadowColor: const Color(0xFF1890FF).withOpacity(0.3),
            ),
          ),
          const SizedBox(width: 12),
          OutlinedButton.icon(
            onPressed: () {
              // TODO: 重置表单
            },
            icon: const Text('🔄'),
            label: const Text('重置'),
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF595959),
              side: const BorderSide(color: Color(0xFFD9D9D9)),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              backgroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSecuritySettings() {
    return Column(
      children: [
        _buildSettingItem(
          '修改密码',
          '定期修改密码以保护账户安全',
          ElevatedButton(
            onPressed: () {},
            child: const Text('修改'),
          ),
        ),
        _buildSettingItem(
          '两步验证',
          '启用两步验证增强账户安全性',
          _buildSwitch(false),
        ),
        _buildSettingItem(
          '登录通知',
          '新设备登录时发送通知',
          _buildSwitch(true),
        ),
      ],
    );
  }

  Widget _buildTeachingStatistics() {
    return Column(
      children: [
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          childAspectRatio: 2,
          crossAxisSpacing: 20,
          mainAxisSpacing: 20,
          children: [
            _buildStatCard('📚', '授课班级', '3', '个', const Color(0xFFE6F7FF), const Color(0xFF1890FF)),
            _buildStatCard('👥', '学生总数', '156', '人', const Color(0xFFF6FFED), const Color(0xFF52C41A)),
            _buildStatCard('📖', '课程数量', '24', '节', const Color(0xFFFFF7E6), const Color(0xFFFA8C16)),
            _buildStatCard('⏰', '教学时长', '480', '小时', const Color(0xFFF9F0FF), const Color(0xFF722ED1)),
          ],
        ),
      ],
    );
  }

  Widget _buildStatCard(String icon, String label, String value, String unit, Color bgColor, Color iconColor) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: bgColor,
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: iconColor.withOpacity(0.2),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Center(
              child: Text(
                icon,
                style: TextStyle(
                  fontSize: 24,
                  color: iconColor,
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            '$value$unit',
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Color(0xFF262626),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              color: Color(0xFF8C8C8C),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPreferences() {
    return Column(
      children: [
        _buildSettingItem(
          '语言设置',
          '选择界面显示语言',
          DropdownButton<String>(
            value: '中文',
            items: const [
              DropdownMenuItem(value: '中文', child: Text('中文')),
              DropdownMenuItem(value: 'English', child: Text('English')),
            ],
            onChanged: (value) {},
          ),
        ),
        _buildSettingItem(
          '自动保存',
          '自动保存编辑内容',
          _buildSwitch(true),
        ),
      ],
    );
  }

  Widget _buildNotificationSettings() {
    return Column(
      children: [
        _buildSettingItem(
          '系统通知',
          '接收系统重要通知',
          _buildSwitch(true),
        ),
        _buildSettingItem(
          '成绩提醒',
          '成绩录入和分析提醒',
          _buildSwitch(true),
        ),
        _buildSettingItem(
          '课程提醒',
          '上课时间提醒',
          _buildSwitch(false),
        ),
      ],
    );
  }

  Widget _buildInterfaceSettings() {
    return Column(
      children: [
        _buildSettingItem(
          '深色模式',
          '使用深色主题界面',
          _buildSwitch(false),
        ),
        _buildSettingItem(
          '紧凑布局',
          '使用更紧凑的界面布局',
          _buildSwitch(false),
        ),
      ],
    );
  }

  Widget _buildHelpCenter() {
    return Column(
      children: [
        Text(
          '帮助中心功能正在开发中...',
          style: TextStyle(
            fontSize: 16,
            color: Color(0xFF8C8C8C),
          ),
        ),
      ],
    );
  }

  Widget _buildFeedback() {
    return Column(
      children: [
        Text(
          '意见反馈功能正在开发中...',
          style: TextStyle(
            fontSize: 16,
            color: Color(0xFF8C8C8C),
          ),
        ),
      ],
    );
  }

  Widget _buildAbout() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFF6FFED), Color(0xFFE6F7FF)],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE6F7FF)),
      ),
      child: Column(
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF1890FF), Color(0xFF096DD9)],
              ),
              borderRadius: BorderRadius.circular(40),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF1890FF).withOpacity(0.3),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Center(
              child: Text(
                '🎓',
                style: TextStyle(fontSize: 32),
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            '智能教学助手 v1.0.0',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w600,
              color: Color(0xFF262626),
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            '智能教学助手是一款专为教师设计的教学管理工具，提供成绩管理、学情分析、备课辅助等功能，帮助教师提高教学效率。',
            style: TextStyle(
              fontSize: 14,
              color: Color(0xFF595959),
              height: 1.6,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFF1890FF).withOpacity(0.3)),
            ),
            child: const Text(
              '© 2024 智能教学助手团队',
              style: TextStyle(
                fontSize: 12,
                color: Color(0xFF8C8C8C),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingItem(String title, String description, Widget control) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFF0F0F0)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Color(0xFF262626),
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF8C8C8C),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          control,
        ],
      ),
    );
  }

  Widget _buildSwitch(bool value) {
    return Switch(
      value: value,
      onChanged: (newValue) {
        // TODO: 实现开关状态切换
      },
      activeColor: const Color(0xFF1890FF),
    );
  }
}