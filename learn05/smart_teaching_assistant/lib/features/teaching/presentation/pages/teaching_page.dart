import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../../../shared/themes/app_theme.dart';

class TeachingPage extends StatefulWidget {
  const TeachingPage({Key? key}) : super(key: key);

  @override
  State<TeachingPage> createState() => _TeachingPageState();
}

class _TeachingPageState extends State<TeachingPage> with TickerProviderStateMixin {
  late TabController _tabController;
  bool _isClassActive = false;
  String _currentLessonTitle = '';
  int _currentStudentCount = 0;
  Duration _classDuration = Duration.zero;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('上课管理'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        actions: [
          if (_isClassActive)
            IconButton(
              icon: const Icon(Icons.stop_circle),
              onPressed: () {
                _endClass();
              },
              tooltip: '结束上课',
            ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              _showClassSettings();
            },
            tooltip: '课堂设置',
          ),
          SizedBox(width: 8.w),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: '课堂概览'),
            Tab(text: 'AI学情'),
            Tab(text: '互动工具'),
            Tab(text: '课堂记录'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildClassOverviewTab(),
          _buildAIAnalysisTab(),
          _buildInteractiveToolsTab(),
          _buildClassRecordsTab(),
        ],
      ),
      floatingActionButton: !_isClassActive
          ? FloatingActionButton.extended(
              onPressed: () {
                _startClass();
              },
              backgroundColor: AppTheme.successColor,
              foregroundColor: Colors.white,
              icon: const Icon(Icons.play_arrow),
              label: const Text('开始上课'),
            )
          : null,
    );
  }

  Widget _buildClassOverviewTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 课堂状态卡片
          _buildClassStatusCard(),
          SizedBox(height: 16.h),
          
          // 今日课程
          _buildSectionTitle('今日课程'),
          SizedBox(height: 12.h),
          _buildTodayLessonsCard(),
          SizedBox(height: 20.h),
          
          // 快捷操作
          _buildSectionTitle('快捷操作'),
          SizedBox(height: 12.h),
          _buildQuickActionsGrid(),
          SizedBox(height: 20.h),
          
          // 课堂统计
          _buildSectionTitle('课堂统计'),
          SizedBox(height: 12.h),
          _buildClassStatistics(),
        ],
      ),
    );
  }

  Widget _buildAIAnalysisTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // AI学情分析概览
          _buildAIAnalysisOverview(),
          SizedBox(height: 16.h),
          
          // 学生参与度分析
          _buildSectionTitle('学生参与度分析'),
          SizedBox(height: 12.h),
          _buildParticipationAnalysis(),
          SizedBox(height: 20.h),
          
          // 知识点掌握情况
          _buildSectionTitle('知识点掌握情况'),
          SizedBox(height: 12.h),
          _buildKnowledgeAnalysis(),
          SizedBox(height: 20.h),
          
          // AI教学建议
          _buildSectionTitle('AI教学建议'),
          SizedBox(height: 12.h),
          _buildAITeachingSuggestions(),
        ],
      ),
    );
  }

  Widget _buildInteractiveToolsTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 互动工具网格
          _buildInteractiveToolsGrid(),
          SizedBox(height: 20.h),
          
          // 实时互动
          _buildSectionTitle('实时互动'),
          SizedBox(height: 12.h),
          _buildRealTimeInteraction(),
          SizedBox(height: 20.h),
          
          // 课堂活动
          _buildSectionTitle('课堂活动'),
          SizedBox(height: 12.h),
          _buildClassActivities(),
        ],
      ),
    );
  }

  Widget _buildClassRecordsTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 课堂记录控制
          _buildRecordingControls(),
          SizedBox(height: 16.h),
          
          // 历史记录
          _buildSectionTitle('历史记录'),
          SizedBox(height: 12.h),
          _buildHistoryRecords(),
          SizedBox(height: 20.h),
          
          // 课堂笔记
          _buildSectionTitle('课堂笔记'),
          SizedBox(height: 12.h),
          _buildClassNotes(),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: TextStyle(
        fontSize: 18.sp,
        fontWeight: FontWeight.bold,
        color: AppTheme.textPrimaryColor,
      ),
    );
  }

  Widget _buildClassStatusCard() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16.r),
      ),
      child: Container(
        width: double.infinity,
        padding: EdgeInsets.all(20.w),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16.r),
          gradient: LinearGradient(
            colors: _isClassActive
                ? [AppTheme.successColor, AppTheme.successColor.withOpacity(0.8)]
                : [AppTheme.primaryColor, AppTheme.primaryColor.withOpacity(0.8)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _isClassActive ? Icons.play_circle_filled : Icons.pause_circle_filled,
                  color: Colors.white,
                  size: 32.sp,
                ),
                SizedBox(width: 12.w),
                Expanded(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _isClassActive ? '课堂进行中' : '课堂未开始',
                        style: TextStyle(
                          fontSize: 20.sp,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      if (_isClassActive && _currentLessonTitle.isNotEmpty)
                        Text(
                          _currentLessonTitle,
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: Colors.white.withOpacity(0.9),
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
            if (_isClassActive) ...[
              SizedBox(height: 16.h),
              Row(
                children: [
                  _buildStatusItem('上课时长', '${_classDuration.inMinutes}分钟'),
                  SizedBox(width: 24.w),
                  _buildStatusItem('在线学生', '$_currentStudentCount人'),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12.sp,
            color: Colors.white.withOpacity(0.8),
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 16.sp,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildTodayLessonsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          children: [
            _buildLessonItem(
              '第1节',
              '数学 - 函数的概念',
              '高一(1)班',
              '08:00-08:45',
              true,
            ),
            Divider(height: 20.h),
            _buildLessonItem(
              '第2节',
              '物理 - 牛顿第一定律',
              '高一(2)班',
              '09:00-09:45',
              false,
            ),
            Divider(height: 20.h),
            _buildLessonItem(
              '第3节',
              '英语 - Unit 3 Reading',
              '高一(1)班',
              '10:00-10:45',
              false,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLessonItem(
    String period,
    String subject,
    String className,
    String time,
    bool isActive,
  ) {
    return Row(
      children: [
        Container(
          width: 60.w,
          height: 60.h,
          decoration: BoxDecoration(
            color: isActive ? AppTheme.successColor : AppTheme.backgroundColor,
            borderRadius: BorderRadius.circular(12.r),
            border: Border.all(
              color: isActive ? AppTheme.successColor : AppTheme.borderColor,
            ),
          ),
          child: Center(
            child: Text(
              period,
              style: TextStyle(
                fontSize: 12.sp,
                fontWeight: FontWeight.bold,
                color: isActive ? Colors.white : AppTheme.textSecondaryColor,
              ),
            ),
          ),
        ),
        SizedBox(width: 12.w),
        Expanded(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                subject,
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              SizedBox(height: 4.h),
              Row(
                children: [
                  Icon(
                    Icons.group,
                    size: 14.sp,
                    color: AppTheme.textSecondaryColor,
                  ),
                  SizedBox(width: 4.w),
                  Text(
                    className,
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: AppTheme.textSecondaryColor,
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Icon(
                    Icons.access_time,
                    size: 14.sp,
                    color: AppTheme.textSecondaryColor,
                  ),
                  SizedBox(width: 4.w),
                  Text(
                    time,
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: AppTheme.textSecondaryColor,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        if (isActive)
          Container(
            padding: EdgeInsets.symmetric(
              horizontal: 8.w,
              vertical: 4.h,
            ),
            decoration: BoxDecoration(
              color: AppTheme.successColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12.r),
            ),
            child: Text(
              '进行中',
              style: TextStyle(
                fontSize: 10.sp,
                color: AppTheme.successColor,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildQuickActionsGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 3,
      crossAxisSpacing: 12.w,
      mainAxisSpacing: 12.h,
      childAspectRatio: 1.2,
      children: [
        _buildQuickActionCard(
          '点名签到',
          Icons.how_to_reg,
          AppTheme.primaryColor,
          () => _showAttendanceDialog(),
        ),
        _buildQuickActionCard(
          '随机提问',
          Icons.quiz,
          AppTheme.infoColor,
          () => _randomQuestion(),
        ),
        _buildQuickActionCard(
          '课堂投票',
          Icons.poll,
          AppTheme.warningColor,
          () => _startVoting(),
        ),
        _buildQuickActionCard(
          '分组讨论',
          Icons.groups,
          AppTheme.successColor,
          () => _startGroupDiscussion(),
        ),
        _buildQuickActionCard(
          '屏幕分享',
          Icons.screen_share,
          AppTheme.errorColor,
          () => _shareScreen(),
        ),
        _buildQuickActionCard(
          '课堂练习',
          Icons.assignment,
          AppTheme.primaryColor,
          () => _startExercise(),
        ),
      ],
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
          padding: EdgeInsets.all(12.w),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                color: color,
                size: 28.sp,
              ),
              SizedBox(height: 8.h),
              Text(
                title,
                style: TextStyle(
                  fontSize: 12.sp,
                  fontWeight: FontWeight.w500,
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

  Widget _buildClassStatistics() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard('出勤率', '95%', Icons.people, AppTheme.successColor),
        ),
        SizedBox(width: 12.w),
        Expanded(
          child: _buildStatCard('参与度', '87%', Icons.trending_up, AppTheme.infoColor),
        ),
        SizedBox(width: 12.w),
        Expanded(
          child: _buildStatCard('互动次数', '23', Icons.chat, AppTheme.warningColor),
        ),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: color,
              size: 24.sp,
            ),
            SizedBox(height: 8.h),
            Text(
              value,
              style: TextStyle(
                fontSize: 18.sp,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimaryColor,
              ),
            ),
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

  Widget _buildAIAnalysisOverview() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16.r),
      ),
      child: Container(
        width: double.infinity,
        padding: EdgeInsets.all(20.w),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16.r),
          gradient: LinearGradient(
            colors: [AppTheme.infoColor, AppTheme.infoColor.withOpacity(0.8)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_awesome,
                  color: Colors.white,
                  size: 28.sp,
                ),
                SizedBox(width: 12.w),
                Text(
                  'AI学情分析',
                  style: TextStyle(
                    fontSize: 20.sp,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16.h),
            Text(
              '基于课堂互动数据，AI为您提供实时学情分析和个性化教学建议',
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.white.withOpacity(0.9),
              ),
            ),
            SizedBox(height: 16.h),
            Row(
              children: [
                _buildAIMetric('整体理解度', '78%'),
                SizedBox(width: 24.w),
                _buildAIMetric('注意力指数', '85%'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAIMetric(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12.sp,
            color: Colors.white.withOpacity(0.8),
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 18.sp,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildParticipationAnalysis() {
    return Card(
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
                  Icons.trending_up,
                  color: AppTheme.successColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  '参与度趋势',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16.h),
            Container(
              height: 120.h,
              decoration: BoxDecoration(
                color: AppTheme.backgroundColor,
                borderRadius: BorderRadius.circular(8.r),
              ),
              child: Center(
                child: Text(
                  '参与度图表\n(集成图表库后显示)',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
              ),
            ),
            SizedBox(height: 12.h),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildParticipationItem('积极参与', '12人', AppTheme.successColor),
                _buildParticipationItem('一般参与', '8人', AppTheme.warningColor),
                _buildParticipationItem('较少参与', '3人', AppTheme.errorColor),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildParticipationItem(String label, String count, Color color) {
    return Column(
      children: [
        Container(
          width: 12.w,
          height: 12.h,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        SizedBox(height: 4.h),
        Text(
          count,
          style: TextStyle(
            fontSize: 14.sp,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 10.sp,
            color: AppTheme.textSecondaryColor,
          ),
        ),
      ],
    );
  }

  Widget _buildKnowledgeAnalysis() {
    return Card(
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
                  Icons.psychology,
                  color: AppTheme.infoColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  '知识点掌握分析',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16.h),
            _buildKnowledgeItem('函数的定义', 0.85, AppTheme.successColor),
            SizedBox(height: 8.h),
            _buildKnowledgeItem('函数的性质', 0.72, AppTheme.warningColor),
            SizedBox(height: 8.h),
            _buildKnowledgeItem('函数的应用', 0.58, AppTheme.errorColor),
          ],
        ),
      ),
    );
  }

  Widget _buildKnowledgeItem(String knowledge, double progress, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              knowledge,
              style: TextStyle(
                fontSize: 14.sp,
                fontWeight: FontWeight.w500,
                color: AppTheme.textPrimaryColor,
              ),
            ),
            Text(
              '${(progress * 100).toInt()}%',
              style: TextStyle(
                fontSize: 12.sp,
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        SizedBox(height: 4.h),
        LinearProgressIndicator(
          value: progress,
          backgroundColor: AppTheme.backgroundColor,
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ],
    );
  }

  Widget _buildAITeachingSuggestions() {
    return Card(
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
                  Icons.lightbulb,
                  color: AppTheme.warningColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  'AI教学建议',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16.h),
            _buildSuggestionItem(
              '建议增加互动环节',
              '检测到学生注意力有所下降，建议进行一次课堂互动',
              Icons.chat_bubble,
            ),
            SizedBox(height: 12.h),
            _buildSuggestionItem(
              '重点讲解函数应用',
              '该知识点掌握度较低，建议增加实例讲解',
              Icons.priority_high,
            ),
            SizedBox(height: 12.h),
            _buildSuggestionItem(
              '关注后排学生',
              '后排部分学生参与度较低，建议重点关注',
              Icons.visibility,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionItem(String title, String description, IconData icon) {
    return Container(
      padding: EdgeInsets.all(12.w),
      decoration: BoxDecoration(
        color: AppTheme.warningColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8.r),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: AppTheme.warningColor,
            size: 20.sp,
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                SizedBox(height: 2.h),
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
    );
  }

  Widget _buildInteractiveToolsGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12.w,
      mainAxisSpacing: 12.h,
      childAspectRatio: 1.5,
      children: [
        _buildInteractiveToolCard(
          '实时问答',
          '学生可以实时提问',
          Icons.question_answer,
          AppTheme.primaryColor,
          () => _openQASession(),
        ),
        _buildInteractiveToolCard(
          '白板工具',
          '共享电子白板',
          Icons.draw,
          AppTheme.infoColor,
          () => _openWhiteboard(),
        ),
        _buildInteractiveToolCard(
          '课堂测验',
          '快速测验理解度',
          Icons.quiz,
          AppTheme.successColor,
          () => _startQuiz(),
        ),
        _buildInteractiveToolCard(
          '举手发言',
          '学生举手申请发言',
          Icons.pan_tool,
          AppTheme.warningColor,
          () => _openHandRaising(),
        ),
      ],
    );
  }

  Widget _buildInteractiveToolCard(
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
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                icon,
                color: color,
                size: 32.sp,
              ),
              SizedBox(height: 12.h),
              Text(
                title,
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.bold,
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
      ),
    );
  }

  Widget _buildRealTimeInteraction() {
    return Card(
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
                  Icons.chat,
                  color: AppTheme.primaryColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  '实时互动消息',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const Spacer(),
                Text(
                  '3条新消息',
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: AppTheme.primaryColor,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16.h),
            Container(
              height: 120.h,
              decoration: BoxDecoration(
                color: AppTheme.backgroundColor,
                borderRadius: BorderRadius.circular(8.r),
              ),
              child: ListView(
                padding: EdgeInsets.all(8.w),
                children: [
                  _buildInteractionMessage('张三', '老师，这个公式我不太理解'),
                  _buildInteractionMessage('李四', '能再讲一遍吗？'),
                  _buildInteractionMessage('王五', '我明白了，谢谢老师'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInteractionMessage(String student, String message) {
    return Container(
      margin: EdgeInsets.only(bottom: 8.h),
      padding: EdgeInsets.all(8.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8.r),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            student,
            style: TextStyle(
              fontSize: 12.sp,
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryColor,
            ),
          ),
          SizedBox(height: 2.h),
          Text(
            message,
            style: TextStyle(
              fontSize: 12.sp,
              color: AppTheme.textPrimaryColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildClassActivities() {
    return Column(
      children: [
        _buildActivityItem(
          '小组讨论',
          '正在进行中',
          '剩余 5 分钟',
          AppTheme.successColor,
          true,
        ),
        SizedBox(height: 12.h),
        _buildActivityItem(
          '课堂投票',
          '已结束',
          '参与率 95%',
          AppTheme.textSecondaryColor,
          false,
        ),
        SizedBox(height: 12.h),
        _buildActivityItem(
          '随机提问',
          '待开始',
          '点击开始',
          AppTheme.primaryColor,
          false,
        ),
      ],
    );
  }

  Widget _buildActivityItem(
    String title,
    String status,
    String detail,
    Color color,
    bool isActive,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Row(
          children: [
            Container(
              width: 8.w,
              height: 40.h,
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(4.r),
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
                  Row(
                    children: [
                      Container(
                        padding: EdgeInsets.symmetric(
                          horizontal: 8.w,
                          vertical: 2.h,
                        ),
                        decoration: BoxDecoration(
                          color: color.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(10.r),
                        ),
                        child: Text(
                          status,
                          style: TextStyle(
                            fontSize: 10.sp,
                            color: color,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      SizedBox(width: 8.w),
                      Text(
                        detail,
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: AppTheme.textSecondaryColor,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            if (isActive)
              IconButton(
                onPressed: () {
                  // 停止活动
                },
                icon: Icon(
                  Icons.stop,
                  color: AppTheme.errorColor,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecordingControls() {
    return Card(
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
                  Icons.videocam,
                  color: AppTheme.errorColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  '课堂录制',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16.h),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      _startRecording();
                    },
                    icon: const Icon(Icons.fiber_manual_record),
                    label: const Text('开始录制'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.errorColor,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                SizedBox(width: 12.w),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      _takeScreenshot();
                    },
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('截图'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppTheme.primaryColor,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryRecords() {
    return Column(
      children: [
        _buildRecordItem(
          '2024-01-15 数学课',
          '45分钟',
          '高一(1)班',
          '125MB',
        ),
        SizedBox(height: 12.h),
        _buildRecordItem(
          '2024-01-14 物理课',
          '40分钟',
          '高一(2)班',
          '98MB',
        ),
        SizedBox(height: 12.h),
        _buildRecordItem(
          '2024-01-13 英语课',
          '45分钟',
          '高一(1)班',
          '110MB',
        ),
      ],
    );
  }

  Widget _buildRecordItem(
    String title,
    String duration,
    String className,
    String size,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Row(
          children: [
            Icon(
              Icons.play_circle_filled,
              color: AppTheme.primaryColor,
              size: 32.sp,
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
                  Row(
                    children: [
                      Text(
                        duration,
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: AppTheme.textSecondaryColor,
                        ),
                      ),
                      SizedBox(width: 8.w),
                      Text(
                        '•',
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: AppTheme.textSecondaryColor,
                        ),
                      ),
                      SizedBox(width: 8.w),
                      Text(
                        className,
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: AppTheme.textSecondaryColor,
                        ),
                      ),
                      SizedBox(width: 8.w),
                      Text(
                        '•',
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: AppTheme.textSecondaryColor,
                        ),
                      ),
                      SizedBox(width: 8.w),
                      Text(
                        size,
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: AppTheme.textSecondaryColor,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            PopupMenuButton(
              icon: Icon(
                Icons.more_vert,
                color: AppTheme.textSecondaryColor,
              ),
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'play',
                  child: Text('播放'),
                ),
                const PopupMenuItem(
                  value: 'download',
                  child: Text('下载'),
                ),
                const PopupMenuItem(
                  value: 'share',
                  child: Text('分享'),
                ),
                const PopupMenuItem(
                  value: 'delete',
                  child: Text('删除'),
                ),
              ],
              onSelected: (value) {
                // 处理菜单选择
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildClassNotes() {
    return Card(
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
                  Icons.note_add,
                  color: AppTheme.primaryColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  '课堂笔记',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () {
                    _addNote();
                  },
                  child: const Text('添加笔记'),
                ),
              ],
            ),
            SizedBox(height: 16.h),
            Container(
              width: double.infinity,
              height: 120.h,
              padding: EdgeInsets.all(12.w),
              decoration: BoxDecoration(
                color: AppTheme.backgroundColor,
                borderRadius: BorderRadius.circular(8.r),
                border: Border.all(color: AppTheme.borderColor),
              ),
              child: TextField(
                maxLines: null,
                decoration: InputDecoration(
                  hintText: '在此记录课堂要点、学生反馈等...',
                  border: InputBorder.none,
                  hintStyle: TextStyle(
                    color: AppTheme.textSecondaryColor,
                    fontSize: 14.sp,
                  ),
                ),
                style: TextStyle(
                  fontSize: 14.sp,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 事件处理方法
  void _startClass() {
    setState(() {
      _isClassActive = true;
      _currentLessonTitle = '数学 - 函数的概念';
      _currentStudentCount = 23;
      _classDuration = const Duration(minutes: 15);
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('课堂已开始')),
    );
  }

  void _endClass() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('结束上课'),
        content: const Text('确定要结束当前课堂吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              setState(() {
                _isClassActive = false;
                _currentLessonTitle = '';
                _currentStudentCount = 0;
                _classDuration = Duration.zero;
              });
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('课堂已结束')),
              );
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  void _showClassSettings() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('课堂设置功能开发中...')),
    );
  }

  void _showAttendanceDialog() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('点名签到功能开发中...')),
    );
  }

  void _randomQuestion() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('随机提问功能开发中...')),
    );
  }

  void _startVoting() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('课堂投票功能开发中...')),
    );
  }

  void _startGroupDiscussion() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('分组讨论功能开发中...')),
    );
  }

  void _shareScreen() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('屏幕分享功能开发中...')),
    );
  }

  void _startExercise() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('课堂练习功能开发中...')),
    );
  }

  void _openQASession() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('实时问答功能开发中...')),
    );
  }

  void _openWhiteboard() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('白板工具功能开发中...')),
    );
  }

  void _startQuiz() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('课堂测验功能开发中...')),
    );
  }

  void _openHandRaising() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('举手发言功能开发中...')),
    );
  }

  void _startRecording() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('开始录制功能开发中...')),
    );
  }

  void _takeScreenshot() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('截图功能开发中...')),
    );
  }

  void _addNote() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('添加笔记功能开发中...')),
    );
  }
}