import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import '../../../../shared/themes/app_theme.dart';

class LessonsPage extends StatefulWidget {
  const LessonsPage({Key? key}) : super(key: key);

  @override
  State<LessonsPage> createState() => _LessonsPageState();
}

class _LessonsPageState extends State<LessonsPage> with TickerProviderStateMixin {
  late TabController _rightPanelController;
  String _selectedLessonId = '1';
  String _currentLessonTitle = '函数的概念与性质';
  
  @override
  void initState() {
    super.initState();
    _rightPanelController = TabController(length: 2, vsync: this);
  }
  
  @override
  void dispose() {
    _rightPanelController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _buildTopNavigation(),
          Expanded(
            child: Row(
              children: [
                _buildSidebar(),
                Expanded(child: _buildWorkspace()),
                _buildRightPanel(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 顶部导航栏
  Widget _buildTopNavigation() {
    return Container(
      height: 64.h,
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: EdgeInsets.symmetric(horizontal: 24.w),
        child: Row(
          children: [
            // Logo
            Row(
              children: [
                Container(
                  width: 32.w,
                  height: 32.h,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [AppTheme.primaryColor, AppTheme.primaryColor.withOpacity(0.8)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                  child: const Center(
                    child: Text('🎓', style: TextStyle(fontSize: 16)),
                  ),
                ),
                SizedBox(width: 12.w),
                Text(
                  '智能教学助手',
                  style: TextStyle(
                    fontSize: 18.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
            
            SizedBox(width: 48.w),
            
            // 导航菜单
            Row(
              children: [
                _buildNavItem('工作台', false),
                _buildNavItem('备课', true),
                _buildNavItem('上课', false),
                _buildNavItem('成绩', false),
                _buildNavItem('分析', false),
              ],
            ),
            
            const Spacer(),
            
            // 用户头像
            Container(
              width: 32.w,
              height: 32.h,
              decoration: BoxDecoration(
                color: AppTheme.primaryColor,
                borderRadius: BorderRadius.circular(16.r),
              ),
              child: const Center(
                child: Text(
                  '张',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildNavItem(String title, bool isActive) {
    return GestureDetector(
      onTap: () {
        // 导航逻辑
        if (title == '工作台') {
          context.go('/dashboard');
        } else if (title == '成绩') {
          context.go('/grades');
        } else if (title == '分析') {
          context.go('/analytics');
        }
      },
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
        margin: EdgeInsets.symmetric(horizontal: 4.w),
        decoration: BoxDecoration(
          color: isActive ? AppTheme.primaryColor.withOpacity(0.1) : Colors.transparent,
          borderRadius: BorderRadius.circular(6.r),
          border: isActive ? Border.all(
            color: AppTheme.primaryColor.withOpacity(0.2),
          ) : null,
        ),
        child: Text(
          title,
          style: TextStyle(
            fontSize: 14.sp,
            color: isActive ? AppTheme.primaryColor : AppTheme.textSecondaryColor,
            fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
          ),
        ),
      ),
    );
  }
  
  // 左侧边栏
  Widget _buildSidebar() {
    return Container(
      width: 280.w,
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(
          right: BorderSide(color: Color(0xFFF0F0F0)),
        ),
      ),
      child: Column(
        children: [
          // 侧边栏头部
          Container(
            padding: EdgeInsets.all(24.w),
            decoration: const BoxDecoration(
              border: Border(
                bottom: BorderSide(color: Color(0xFFF0F0F0)),
              ),
            ),
            child: SizedBox(
              width: double.infinity,
              height: 44.h,
              child: ElevatedButton(
                onPressed: () {
                  context.push('/lessons/create');
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.white,
                  elevation: 2,
                  shadowColor: AppTheme.primaryColor.withOpacity(0.3),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 18.w,
                      height: 18.h,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(9.r),
                      ),
                      child: const Icon(Icons.add, size: 14, color: Colors.white),
                    ),
                    SizedBox(width: 8.w),
                    const Text(
                      '新建教案',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          
          // 教案列表
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(16.w),
              child: Column(
                children: [
                  // 列表头部
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '我的教案',
                        style: TextStyle(
                          fontSize: 14.sp,
                          fontWeight: FontWeight.w500,
                          color: AppTheme.textPrimaryColor,
                        ),
                      ),
                      TextButton(
                        onPressed: () {},
                        child: Text(
                          '筛选',
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: AppTheme.textSecondaryColor,
                          ),
                        ),
                      ),
                    ],
                  ),
                  
                  SizedBox(height: 16.h),
                  
                  // 教案项目
                  Expanded(
                    child: ListView(
                      children: [
                        _buildLessonItem(
                          '函数的概念与性质',
                          '草稿',
                          '高一数学',
                          '今天',
                          true,
                          '1',
                        ),
                        _buildLessonItem(
                          '二次函数图像与性质',
                          '已完成',
                          '高一数学',
                          '昨天',
                          false,
                          '2',
                        ),
                        _buildLessonItem(
                          '指数函数与对数函数',
                          '已完成',
                          '高一数学',
                          '3天前',
                          false,
                          '3',
                        ),
                        _buildLessonItem(
                          '三角函数基础',
                          '草稿',
                          '高一数学',
                          '1周前',
                          false,
                          '4',
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildLessonItem(
    String title,
    String status,
    String subject,
    String time,
    bool isActive,
    String id,
  ) {
    final isDraft = status == '草稿';
    final isSelected = _selectedLessonId == id;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedLessonId = id;
          _currentLessonTitle = title;
        });
      },
      child: Container(
        padding: EdgeInsets.all(12.w),
        margin: EdgeInsets.only(bottom: 8.h),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.primaryColor.withOpacity(0.08) : Colors.white,
          border: Border.all(
            color: isSelected ? AppTheme.primaryColor : const Color(0xFFF0F0F0),
          ),
          borderRadius: BorderRadius.circular(8.r),
          boxShadow: isSelected ? [
            BoxShadow(
              color: AppTheme.primaryColor.withOpacity(0.1),
              offset: const Offset(0, 2),
              blurRadius: 4,
            ),
          ] : [
            BoxShadow(
              color: Colors.black.withOpacity(0.02),
              offset: const Offset(0, 1),
              blurRadius: 2,
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    title,
                    style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w500,
                      color: isSelected ? AppTheme.primaryColor : AppTheme.textPrimaryColor,
                    ),
                  ),
                ),
                if (isSelected)
                  Icon(
                    Icons.check_circle,
                    size: 16.sp,
                    color: AppTheme.primaryColor,
                  ),
              ],
            ),
            SizedBox(height: 8.h),
            Row(
              children: [
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 3.h),
                  decoration: BoxDecoration(
                    color: isDraft ? const Color(0xFFFFF7E6) : const Color(0xFFF6FFED),
                    borderRadius: BorderRadius.circular(10.r),
                    border: Border.all(
                      color: isDraft ? const Color(0xFFFFD591) : const Color(0xFFB7EB8F),
                      width: 0.5,
                    ),
                  ),
                  child: Text(
                    status,
                    style: TextStyle(
                      fontSize: 10.sp,
                      color: isDraft ? const Color(0xFFFA8C16) : const Color(0xFF52C41A),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                SizedBox(width: 8.w),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF5F5F5),
                    borderRadius: BorderRadius.circular(4.r),
                  ),
                  child: Text(
                    subject,
                    style: TextStyle(
                      fontSize: 10.sp,
                      color: AppTheme.textSecondaryColor,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                const Spacer(),
                Text(
                  time,
                  style: TextStyle(
                    fontSize: 11.sp,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  // 主工作区
  Widget _buildWorkspace() {
    return Container(
      color: Colors.white,
      child: Column(
        children: [
          // 工作区头部
          Container(
            padding: EdgeInsets.all(24.w),
            decoration: const BoxDecoration(
              border: Border(
                bottom: BorderSide(color: Color(0xFFF0F0F0)),
              ),
            ),
            child: Row(
              children: [
                Text(
                  _currentLessonTitle,
                  style: TextStyle(
                    fontSize: 20.sp,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const Spacer(),
                Row(
                  children: [
                    _buildActionButton('预览', false),
                    SizedBox(width: 12.w),
                    _buildActionButton('导出', false),
                    SizedBox(width: 12.w),
                    _buildActionButton('保存', true),
                  ],
                ),
              ],
            ),
          ),
          
          // 工作区内容
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(24.w),
              child: Column(
                children: [
                  // AI助手面板
                  _buildAIPanel(),
                  
                  SizedBox(height: 24.h),
                  
                  // 教案编辑器
                  Expanded(
                    child: _buildLessonEditor(),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildActionButton(String text, bool isPrimary) {
    return ElevatedButton(
      onPressed: () {},
      style: ElevatedButton.styleFrom(
        backgroundColor: isPrimary ? AppTheme.primaryColor : Colors.white,
        foregroundColor: isPrimary ? Colors.white : AppTheme.textPrimaryColor,
        elevation: 0,
        side: BorderSide(
          color: isPrimary ? AppTheme.primaryColor : const Color(0xFFD9D9D9),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(6.r),
        ),
        padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
      ),
      child: Text(
        text,
        style: TextStyle(fontSize: 14.sp),
      ),
    );
  }
  
  Widget _buildAIPanel() {
    return Container(
      padding: EdgeInsets.all(20.w),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFF0F8FF), Color(0xFFE6F7FF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        border: Border.all(color: const Color(0xFFBAE7FF)),
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // AI头部
          Row(
            children: [
              Container(
                width: 32.w,
                height: 32.h,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [AppTheme.primaryColor, AppTheme.primaryColor.withOpacity(0.8)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(8.r),
                ),
                child: const Center(
                  child: Text('🤖', style: TextStyle(fontSize: 16)),
                ),
              ),
              SizedBox(width: 12.w),
              Text(
                'AI教案助手',
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
            ],
          ),
          
          SizedBox(height: 16.h),
          
          // 输入组
          Row(
            children: [
              Expanded(
                child: TextField(
                  decoration: InputDecoration(
                    hintText: '描述您的教学需求，AI将为您生成教案内容...',
                    hintStyle: TextStyle(
                      fontSize: 14.sp,
                      color: AppTheme.textSecondaryColor,
                    ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(6.r),
                      borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(6.r),
                      borderSide: BorderSide(color: AppTheme.primaryColor),
                    ),
                    contentPadding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 8.h),
                  ),
                ),
              ),
              SizedBox(width: 12.w),
              ElevatedButton(
                onPressed: () {},
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(6.r),
                  ),
                  padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 8.h),
                ),
                child: const Text('生成内容'),
              ),
            ],
          ),
          
          SizedBox(height: 16.h),
          
          // 建议标签
          Wrap(
            spacing: 8.w,
            children: [
              _buildSuggestionTag('生成教学目标'),
              _buildSuggestionTag('设计互动环节'),
              _buildSuggestionTag('创建练习题'),
              _buildSuggestionTag('优化教学流程'),
              _buildSuggestionTag('生成课件大纲'),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildSuggestionTag(String text) {
    return GestureDetector(
      onTap: () {},
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
        decoration: BoxDecoration(
          color: AppTheme.primaryColor.withOpacity(0.05),
          border: Border.all(color: AppTheme.primaryColor.withOpacity(0.2)),
          borderRadius: BorderRadius.circular(16.r),
        ),
        child: Text(
          text,
          style: TextStyle(
            fontSize: 12.sp,
            color: AppTheme.primaryColor,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }
  
  Widget _buildLessonEditor() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFF0F0F0)),
        borderRadius: BorderRadius.circular(8.r),
      ),
      child: Column(
        children: [
          // 编辑器工具栏
          Container(
            padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
            decoration: const BoxDecoration(
              color: Color(0xFFFAFAFA),
              border: Border(
                bottom: BorderSide(color: Color(0xFFF0F0F0)),
              ),
            ),
            child: Row(
              children: [
                _buildToolbarButton('B', '粗体'),
                _buildToolbarButton('I', '斜体'),
                _buildToolbarButton('U', '下划线'),
                Container(
                  width: 1,
                  height: 20.h,
                  color: const Color(0xFFD9D9D9),
                  margin: EdgeInsets.symmetric(horizontal: 4.w),
                ),
                _buildToolbarButton('H', '标题'),
                _buildToolbarButton('≡', '列表'),
                _buildToolbarButton('🔗', '链接'),
                Container(
                  width: 1,
                  height: 20.h,
                  color: const Color(0xFFD9D9D9),
                  margin: EdgeInsets.symmetric(horizontal: 4.w),
                ),
                _buildToolbarButton('🖼️', '插入图片'),
                _buildToolbarButton('⊞', '插入表格'),
              ],
            ),
          ),
          
          // 编辑器内容
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(20.w),
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildLessonSection(
                      '教学目标',
                      Column(
                        children: [
                          _buildObjectiveItem('理解函数的概念，掌握函数的三种表示方法'),
                          _buildObjectiveItem('能够判断给定关系是否为函数关系'),
                          _buildObjectiveItem('掌握函数的定义域、值域的求法'),
                          _buildObjectiveItem('了解函数的单调性、奇偶性等基本性质'),
                        ],
                      ),
                    ),
                    
                    SizedBox(height: 32.h),
                    
                    _buildLessonSection(
                      '教学重难点',
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          RichText(
                            text: TextSpan(
                              style: TextStyle(
                                fontSize: 14.sp,
                                color: const Color(0xFF595959),
                                height: 1.8,
                              ),
                              children: const [
                                TextSpan(
                                  text: '重点：',
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                TextSpan(text: '函数概念的理解，函数三种表示方法的掌握'),
                              ],
                            ),
                          ),
                          SizedBox(height: 8.h),
                          RichText(
                            text: TextSpan(
                              style: TextStyle(
                                fontSize: 14.sp,
                                color: const Color(0xFF595959),
                                height: 1.8,
                              ),
                              children: const [
                                TextSpan(
                                  text: '难点：',
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                TextSpan(text: '抽象函数概念的理解，函数性质的综合应用'),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    SizedBox(height: 32.h),
                    
                    _buildLessonSection(
                      '教学过程',
                      Column(
                        children: [
                          _buildActivityCard('1', '导入新课', '5分钟', '通过生活中的实例（如温度与时间的关系）引入函数概念，激发学生学习兴趣。'),
                          _buildActivityCard('2', '概念讲解', '15分钟', '详细讲解函数的定义，强调对应关系的唯一性，通过图示帮助学生理解。'),
                          _buildActivityCard('3', '互动练习', '10分钟', '学生分组讨论，判断给定的关系是否为函数，教师巡视指导。'),
                          _buildActivityCard('4', '例题分析', '12分钟', '通过典型例题，讲解函数定义域、值域的求法，强化概念理解。'),
                          _buildActivityCard('5', '课堂小结', '3分钟', '总结本节课重点内容，布置课后作业，预告下节课内容。'),
                        ],
                      ),
                    ),
                    
                    SizedBox(height: 32.h),
                    
                    _buildLessonSection(
                      '板书设计',
                      Text(
                        '1. 函数的定义\n2. 函数的三种表示方法\n3. 定义域与值域\n4. 典型例题',
                        style: TextStyle(
                          fontSize: 14.sp,
                          color: const Color(0xFF595959),
                          height: 1.8,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildToolbarButton(String icon, String tooltip) {
    return Tooltip(
      message: tooltip,
      child: GestureDetector(
        onTap: () {},
        child: Container(
          width: 32.w,
          height: 32.h,
          margin: EdgeInsets.symmetric(horizontal: 4.w),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(4.r),
          ),
          child: Center(
            child: Text(
              icon,
              style: TextStyle(
                fontSize: 14.sp,
                color: AppTheme.textPrimaryColor,
              ),
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildLessonSection(String title, Widget content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: EdgeInsets.only(bottom: 8.h),
          decoration: const BoxDecoration(
            border: Border(
              bottom: BorderSide(color: Color(0xFFF0F0F0), width: 2),
            ),
          ),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimaryColor,
            ),
          ),
        ),
        SizedBox(height: 12.h),
        content,
      ],
    );
  }
  
  Widget _buildObjectiveItem(String text) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4.h),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 4.w,
            height: 4.w,
            margin: EdgeInsets.only(top: 8.h, right: 12.w),
            decoration: BoxDecoration(
              color: AppTheme.primaryColor,
              shape: BoxShape.circle,
            ),
          ),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF595959),
                height: 1.8,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildActivityCard(String number, String title, String time, String description) {
    return Container(
      margin: EdgeInsets.only(bottom: 12.h),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: const Color(0xFFF9F9F9),
        border: Border.all(color: const Color(0xFFE8E8E8)),
        borderRadius: BorderRadius.circular(6.r),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 24.w,
                height: 24.h,
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor,
                  borderRadius: BorderRadius.circular(4.r),
                ),
                child: Center(
                  child: Text(
                    number,
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              SizedBox(width: 8.w),
              Text(
                title,
                style: TextStyle(
                  fontSize: 14.sp,
                  fontWeight: FontWeight.w500,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              const Spacer(),
              Text(
                time,
                style: TextStyle(
                  fontSize: 12.sp,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
            ],
          ),
          SizedBox(height: 8.h),
          Text(
            description,
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF595959),
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }
  
  // 右侧面板
  Widget _buildRightPanel() {
    return Container(
      width: 320.w,
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(
          left: BorderSide(color: Color(0xFFF0F0F0)),
        ),
      ),
      child: Column(
        children: [
          // 面板标签
          Container(
            decoration: const BoxDecoration(
              border: Border(
                bottom: BorderSide(color: Color(0xFFF0F0F0)),
              ),
            ),
            child: TabBar(
              controller: _rightPanelController,
              indicatorColor: AppTheme.primaryColor,
              labelColor: AppTheme.primaryColor,
              unselectedLabelColor: AppTheme.textSecondaryColor,
              tabs: const [
                Tab(text: '资源库'),
                Tab(text: '模板'),
              ],
            ),
          ),
          
          // 面板内容
          Expanded(
            child: TabBarView(
              controller: _rightPanelController,
              children: [
                _buildResourceTab(),
                _buildTemplateTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildResourceTab() {
    return Padding(
      padding: EdgeInsets.all(20.w),
      child: ListView(
        children: [
          _buildResourceItem(
            '函数概念PPT模板',
            '课件 • 24页 • 2MB',
          ),
          _buildResourceItem(
            '函数性质练习题',
            '习题 • 15题 • PDF',
          ),
          _buildResourceItem(
            '函数图像动画',
            '动画 • 3分钟 • MP4',
          ),
          _buildResourceItem(
            '互动小游戏：函数配对',
            '游戏 • H5 • 在线',
          ),
        ],
      ),
    );
  }
  
  Widget _buildResourceItem(String title, String meta) {
    return GestureDetector(
      onTap: () {},
      child: Container(
        padding: EdgeInsets.all(12.w),
        margin: EdgeInsets.only(bottom: 12.h),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFFF0F0F0)),
          borderRadius: BorderRadius.circular(6.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.02),
              offset: const Offset(0, 1),
              blurRadius: 2,
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 14.sp,
                fontWeight: FontWeight.w500,
                color: AppTheme.textPrimaryColor,
              ),
            ),
            SizedBox(height: 4.h),
            Text(
              meta,
              style: TextStyle(
                fontSize: 12.sp,
                color: AppTheme.textSecondaryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildTemplateTab() {
    return Padding(
      padding: EdgeInsets.all(20.w),
      child: GridView.count(
        crossAxisCount: 2,
        crossAxisSpacing: 12.w,
        mainAxisSpacing: 12.h,
        childAspectRatio: 1.2,
        children: [
          _buildTemplateCard('📝', '标准教案'),
          _buildTemplateCard('🎯', '目标导向'),
          _buildTemplateCard('🔄', '翻转课堂'),
          _buildTemplateCard('👥', '合作学习'),
        ],
      ),
    );
  }
  
  Widget _buildTemplateCard(String icon, String name) {
    return GestureDetector(
      onTap: () {},
      child: Container(
        padding: EdgeInsets.all(16.w),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFFF0F0F0)),
          borderRadius: BorderRadius.circular(8.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.02),
              offset: const Offset(0, 1),
              blurRadius: 2,
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 32.w,
              height: 32.h,
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(6.r),
              ),
              child: Center(
                child: Text(
                  icon,
                  style: const TextStyle(fontSize: 18),
                ),
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              name,
              style: TextStyle(
                fontSize: 12.sp,
                color: AppTheme.textPrimaryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMyLessonsTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 统计卡片
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  '本周备课',
                  '8',
                  Icons.calendar_today,
                  AppTheme.primaryColor,
                ),
              ),
              SizedBox(width: 12.w),
              Expanded(
                child: _buildStatCard(
                  '总备课数',
                  '45',
                  Icons.book,
                  AppTheme.infoColor,
                ),
              ),
            ],
          ),
          SizedBox(height: 24.h),
          
          // 快捷操作
          Text(
            '快捷操作',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 16.h),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: 12.w,
            mainAxisSpacing: 12.h,
            childAspectRatio: 1.5,
            children: [
              _buildQuickActionCard(
                '新建备课',
                Icons.add_circle_outline,
                AppTheme.primaryColor,
                () => context.push('/lessons/create'),
              ),
              _buildQuickActionCard(
                '导入教案',
                Icons.file_upload_outlined,
                AppTheme.successColor,
                () => _showImportDialog(),
              ),
              _buildQuickActionCard(
                '模板库',
                Icons.library_books_outlined,
                AppTheme.infoColor,
                () => _showTemplateLibrary(),
              ),
              _buildQuickActionCard(
                'AI助手',
                Icons.smart_toy_outlined,
                AppTheme.warningColor,
                () => _showAIAssistant(),
              ),
            ],
          ),
          SizedBox(height: 24.h),
          
          // 最近备课
          Text(
            '最近备课',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 16.h),
          _buildRecentLessons(),
        ],
      ),
    );
  }

  Widget _buildMaterialAnalysisTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '教材分析工具',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 16.h),
          
          // 教材分析功能卡片
          _buildAnalysisCard(
            '知识点分析',
            '智能识别教材中的核心知识点',
            Icons.psychology_outlined,
            AppTheme.primaryColor,
            () {},
          ),
          SizedBox(height: 12.h),
          _buildAnalysisCard(
            '难点识别',
            '自动标记学习难点和重点',
            Icons.warning_amber_outlined,
            AppTheme.warningColor,
            () {},
          ),
          SizedBox(height: 12.h),
          _buildAnalysisCard(
            '关联分析',
            '分析知识点间的关联关系',
            Icons.account_tree_outlined,
            AppTheme.infoColor,
            () {},
          ),
          SizedBox(height: 12.h),
          _buildAnalysisCard(
            '学情匹配',
            '根据学生水平匹配教学内容',
            Icons.people_outline,
            AppTheme.successColor,
            () {},
          ),
        ],
      ),
    );
  }

  Widget _buildLessonPlanningTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '环节策划',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 16.h),
          
          // 环节策划步骤
          _buildPlanningStep(
            1,
            '导入环节',
            '设计课程导入方式',
            Icons.play_circle_outline,
            AppTheme.primaryColor,
            true,
          ),
          _buildPlanningStep(
            2,
            '新课讲授',
            '规划新知识点讲解',
            Icons.school_outlined,
            AppTheme.infoColor,
            false,
          ),
          _buildPlanningStep(
            3,
            '练习巩固',
            '设计练习和巩固活动',
            Icons.fitness_center_outlined,
            AppTheme.successColor,
            false,
          ),
          _buildPlanningStep(
            4,
            '总结反思',
            '课程总结和反思环节',
            Icons.summarize_outlined,
            AppTheme.warningColor,
            false,
          ),
          
          SizedBox(height: 24.h),
          
          // 智能推荐
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12.r),
            ),
            child: Padding(
              padding: EdgeInsets.all(16.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.lightbulb_outline,
                        color: AppTheme.warningColor,
                        size: 24.sp,
                      ),
                      SizedBox(width: 8.w),
                      Text(
                        'AI智能推荐',
                        style: TextStyle(
                          fontSize: 16.sp,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.textPrimaryColor,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 12.h),
                  Text(
                    '基于您的教学风格和学生特点，为您推荐最适合的教学环节设计',
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: AppTheme.textSecondaryColor,
                    ),
                  ),
                  SizedBox(height: 16.h),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        _showAIRecommendations();
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.warningColor,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8.r),
                        ),
                      ),
                      child: const Text('获取AI推荐'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          children: [
            Icon(
              icon,
              size: 32.sp,
              color: color,
            ),
            SizedBox(height: 8.h),
            Text(
              value,
              style: TextStyle(
                fontSize: 24.sp,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimaryColor,
              ),
            ),
            SizedBox(height: 4.h),
            Text(
              title,
              style: TextStyle(
                fontSize: 12.sp,
                color: AppTheme.textSecondaryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionCard(
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12.r),
        child: Padding(
          padding: EdgeInsets.all(16.w),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 32.sp,
                color: color,
              ),
              SizedBox(height: 8.h),
              Text(
                title,
                style: TextStyle(
                  fontSize: 14.sp,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimaryColor,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecentLessons() {
    return Column(
      children: [
        _buildLessonCard(
          '高一数学 - 函数的概念',
          '2024-01-15',
          '已完成',
          AppTheme.successColor,
          () {
            context.push('/lessons/detail/1');
          },
        ),
        SizedBox(height: 12.h),
        _buildLessonCard(
          '高一数学 - 二次函数',
          '2024-01-16',
          '进行中',
          AppTheme.warningColor,
          () {
            context.push('/lessons/detail/2');
          },
        ),
        SizedBox(height: 12.h),
        _buildLessonCard(
          '高一数学 - 函数的性质',
          '2024-01-17',
          '待开始',
          AppTheme.textSecondaryColor,
          () {
            context.push('/lessons/detail/3');
          },
        ),
      ],
    );
  }

  Widget _buildLessonCard(
    String title,
    String date,
    String status,
    Color statusColor,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12.r),
        child: Padding(
          padding: EdgeInsets.all(16.w),
          child: Row(
            children: [
              Container(
                width: 48.w,
                height: 48.w,
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8.r),
                ),
                child: Icon(
                  Icons.book_outlined,
                  color: AppTheme.primaryColor,
                  size: 24.sp,
                ),
              ),
              SizedBox(width: 12.w),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16.sp,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textPrimaryColor,
                      ),
                    ),
                    SizedBox(height: 4.h),
                    Text(
                      date,
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: AppTheme.textSecondaryColor,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: EdgeInsets.symmetric(
                  horizontal: 8.w,
                  vertical: 4.h,
                ),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12.r),
                ),
                child: Text(
                  status,
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: statusColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAnalysisCard(
    String title,
    String description,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12.r),
        child: Padding(
          padding: EdgeInsets.all(16.w),
          child: Row(
            children: [
              Container(
                width: 48.w,
                height: 48.w,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8.r),
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 24.sp,
                ),
              ),
              SizedBox(width: 12.w),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16.sp,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textPrimaryColor,
                      ),
                    ),
                    SizedBox(height: 4.h),
                    Text(
                      description,
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: AppTheme.textSecondaryColor,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right,
                color: AppTheme.textSecondaryColor,
                size: 20.sp,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPlanningStep(
    int step,
    String title,
    String description,
    IconData icon,
    Color color,
    bool isActive,
  ) {
    return Container(
      margin: EdgeInsets.only(bottom: 16.h),
      child: Row(
        children: [
          Container(
            width: 40.w,
            height: 40.w,
            decoration: BoxDecoration(
              color: isActive ? color : color.withOpacity(0.3),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                step.toString(),
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16.sp,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          SizedBox(width: 16.w),
          Expanded(
            child: Card(
              elevation: isActive ? 4 : 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.r),
                side: isActive
                    ? BorderSide(color: color, width: 2)
                    : BorderSide.none,
              ),
              child: Padding(
                padding: EdgeInsets.all(16.w),
                child: Row(
                  children: [
                    Icon(
                      icon,
                      color: isActive ? color : AppTheme.textSecondaryColor,
                      size: 24.sp,
                    ),
                    SizedBox(width: 12.w),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            title,
                            style: TextStyle(
                              fontSize: 16.sp,
                              fontWeight: FontWeight.w600,
                              color: isActive
                                  ? AppTheme.textPrimaryColor
                                  : AppTheme.textSecondaryColor,
                            ),
                          ),
                          SizedBox(height: 4.h),
                          Text(
                            description,
                            style: TextStyle(
                              fontSize: 12.sp,
                              color: AppTheme.textSecondaryColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }



  void _showImportDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('导入教案'),
        content: const Text('选择要导入的教案文件'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 导入教案逻辑
            },
            child: const Text('选择文件'),
          ),
        ],
      ),
    );
  }

  void _showTemplateLibrary() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('模板库'),
        content: const Text('选择备课模板'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 选择模板逻辑
            },
            child: const Text('选择'),
          ),
        ],
      ),
    );
  }

  void _showAIAssistant() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('AI备课助手'),
        content: const Text('AI助手将帮助您快速生成备课内容'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // AI助手逻辑
            },
            child: const Text('开始'),
          ),
        ],
      ),
    );
  }

  void _showAIRecommendations() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('AI智能推荐'),
        content: const Text('基于您的教学数据，AI为您推荐最佳教学环节'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 应用推荐逻辑
            },
            child: const Text('应用推荐'),
          ),
        ],
      ),
    );
  }
}