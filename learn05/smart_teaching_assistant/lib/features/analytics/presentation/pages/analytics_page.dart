import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
// import '../../../../core/theme/app_theme.dart';
// import '../../data/providers/analytics_provider.dart';

class AnalyticsPage extends StatefulWidget {
  const AnalyticsPage({super.key});

  @override
  State<AnalyticsPage> createState() => _AnalyticsPageState();
}

class _AnalyticsPageState extends State<AnalyticsPage> {
  @override
  void initState() {
    super.initState();
    // WidgetsBinding.instance.addPostFrameCallback((_) {
    //   context.read<AnalyticsProvider>().loadAnalyticsData();
    // });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      body: Column(
        children: [
          _buildTopNavigation(),
          Expanded(
            child: SingleChildScrollView(
              padding: EdgeInsets.all(24.w),
              child: Column(
                children: [
                  _buildPageHeader(),
                  SizedBox(height: 24.h),
                  _buildAIAnalysisPanel(),
                  SizedBox(height: 24.h),
                  _buildMainContent(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopNavigation() {
    return Container(
      height: 64.h,
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 8,
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
                    gradient: const LinearGradient(
                      colors: [Color(0xFF1890FF), Color(0xFF096DD9)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                  child: Icon(
                    Icons.school,
                    color: Colors.white,
                    size: 16.sp,
                  ),
                ),
                SizedBox(width: 12.w),
                Text(
                  '智能教学助手',
                  style: TextStyle(
                    fontSize: 18.sp,
                    fontWeight: FontWeight.w600,
                    color: const Color(0xFF262626),
                  ),
                ),
              ],
            ),
            SizedBox(width: 40.w),
            // Navigation Menu
            Expanded(
              child: Row(
                children: [
                  _buildNavItem('工作台', false),
                  _buildNavItem('备课', false),
                  _buildNavItem('上课', false),
                  _buildNavItem('成绩', false),
                  _buildNavItem('分析', true),
                ],
              ),
            ),
            // User Avatar
            Container(
              width: 32.w,
              height: 32.h,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF1890FF), Color(0xFF096DD9)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16.r),
              ),
              child: Center(
                child: Text(
                  '张',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w500,
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
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 20.w),
      height: 64.h,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 14.sp,
              color: isActive ? const Color(0xFF1890FF) : const Color(0xFF595959),
              fontWeight: isActive ? FontWeight.w500 : FontWeight.normal,
            ),
          ),
          if (isActive)
            Container(
              margin: EdgeInsets.only(top: 4.h),
              height: 2.h,
              width: 20.w,
              decoration: BoxDecoration(
                color: const Color(0xFF1890FF),
                borderRadius: BorderRadius.circular(1.r),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildPageHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          '学情分析',
          style: TextStyle(
            fontSize: 24.sp,
            fontWeight: FontWeight.w600,
            color: const Color(0xFF262626),
          ),
        ),
        Row(
          children: [
            _buildActionButton(
              icon: Icons.file_download,
              text: '导出报告',
              isPrimary: false,
            ),
            SizedBox(width: 12.w),
            _buildActionButton(
              icon: Icons.refresh,
              text: '刷新分析',
              isPrimary: true,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String text,
    required bool isPrimary,
  }) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
      decoration: BoxDecoration(
        color: isPrimary ? const Color(0xFF1890FF) : Colors.white,
        border: Border.all(
          color: isPrimary ? const Color(0xFF1890FF) : const Color(0xFFD9D9D9),
        ),
        borderRadius: BorderRadius.circular(6.r),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            size: 16.sp,
            color: isPrimary ? Colors.white : const Color(0xFF595959),
          ),
          SizedBox(width: 6.w),
          Text(
            text,
            style: TextStyle(
              fontSize: 14.sp,
              color: isPrimary ? Colors.white : const Color(0xFF595959),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAIAnalysisPanel() {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFF0F8FF), Color(0xFFE6F7FF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        border: Border.all(color: const Color(0xFFBAE7FF)),
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF1890FF).withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Stack(
        children: [
          // Background decoration
          Positioned(
            top: -50,
            right: -50,
            child: Container(
              width: 200.w,
              height: 200.h,
              decoration: BoxDecoration(
                color: const Color(0xFF1890FF).withOpacity(0.08),
                borderRadius: BorderRadius.circular(100.r),
              ),
            ),
          ),
          Positioned(
            bottom: -30,
            left: -30,
            child: Container(
              width: 120.w,
              height: 120.h,
              decoration: BoxDecoration(
                color: const Color(0xFF52C41A).withOpacity(0.05),
                borderRadius: BorderRadius.circular(60.r),
              ),
            ),
          ),
          Padding(
            padding: EdgeInsets.all(24.w),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildAIHeader(),
                SizedBox(height: 20.h),
                _buildAnalysisSummary(),
                SizedBox(height: 20.h),
                _buildGenerateButton(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAIHeader() {
    return Row(
      children: [
        Container(
          width: 48.w,
          height: 48.h,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF1890FF), Color(0xFF096DD9)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(12.r),
          ),
          child: Icon(
            Icons.smart_toy,
            color: Colors.white,
            size: 24.sp,
          ),
        ),
        SizedBox(width: 16.w),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'AI智能学情分析',
              style: TextStyle(
                fontSize: 20.sp,
                fontWeight: FontWeight.w600,
                color: const Color(0xFF262626),
              ),
            ),
            SizedBox(height: 4.h),
            Text(
              '基于最新成绩数据和学习行为的综合分析',
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF8C8C8C),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildAnalysisSummary() {
    // Mock data for now
    return Row(
      children: [
        Expanded(
          child: _buildSummaryItem(
            icon: Icons.people,
            iconColor: const Color(0xFF1890FF),
            iconBg: const Color(0xFFE6F7FF),
            number: '45',
            label: '分析学生数',
          ),
        ),
        SizedBox(width: 20.w),
        Expanded(
          child: _buildSummaryItem(
            icon: Icons.warning,
            iconColor: const Color(0xFFFA8C16),
            iconBg: const Color(0xFFFFF7E6),
            number: '8',
            label: '需关注学生',
          ),
        ),
        SizedBox(width: 20.w),
        Expanded(
          child: _buildSummaryItem(
            icon: Icons.trending_up,
            iconColor: const Color(0xFF52C41A),
            iconBg: const Color(0xFFF6FFED),
            number: '12',
            label: '进步学生',
          ),
        ),
        SizedBox(width: 20.w),
        Expanded(
          child: _buildSummaryItem(
            icon: Icons.track_changes,
            iconColor: const Color(0xFF722ED1),
            iconBg: const Color(0xFFF9F0FF),
            number: '5',
            label: '薄弱知识点',
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryItem({
    required IconData icon,
    required Color iconColor,
    required Color iconBg,
    required String number,
    required String label,
  }) {
    return Container(
      padding: EdgeInsets.all(20.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            width: 40.w,
            height: 40.h,
            decoration: BoxDecoration(
              color: iconBg,
              borderRadius: BorderRadius.circular(10.r),
            ),
            child: Icon(
              icon,
              color: iconColor,
              size: 20.sp,
            ),
          ),
          SizedBox(height: 12.h),
          Text(
            number,
            style: TextStyle(
              fontSize: 24.sp,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF262626),
            ),
          ),
          SizedBox(height: 4.h),
          Text(
            label,
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF8C8C8C),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGenerateButton() {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1890FF), Color(0xFF096DD9)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(8.r),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF1890FF).withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(8.r),
          onTap: () {
            // TODO: 生成个性化辅导方案
          },
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: 24.w, vertical: 12.h),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.rocket_launch,
                  color: Colors.white,
                  size: 16.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  '生成个性化辅导方案',
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w500,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMainContent() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 2,
          child: _buildMainPanel(),
        ),
        SizedBox(width: 24.w),
        Expanded(
          flex: 1,
          child: _buildSidePanel(),
        ),
      ],
    );
  }

  Widget _buildMainPanel() {
    return Column(
      children: [
        _buildAttentionStudentsCard(),
        SizedBox(height: 24.h),
        _buildKnowledgeAnalysisCard(),
      ],
    );
  }

  Widget _buildAttentionStudentsCard() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildCardHeader(
            title: '需重点关注学生',
            icon: Icons.warning,
            iconColor: const Color(0xFFFA8C16),
            iconBg: const Color(0xFFFFF7E6),
          ),
          Padding(
            padding: EdgeInsets.all(24.w),
            child: Column(
              children: [
                _buildAttentionChart(),
                SizedBox(height: 20.h),
                _buildStudentGrid(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildKnowledgeAnalysisCard() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildCardHeader(
            title: '知识点掌握情况',
            icon: Icons.track_changes,
            iconColor: const Color(0xFF722ED1),
            iconBg: const Color(0xFFF9F0FF),
          ),
          Padding(
            padding: EdgeInsets.all(24.w),
            child: Column(
              children: [
                _buildKnowledgeChart(),
                SizedBox(height: 24.h),
                _buildKnowledgeList(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCardHeader({
    required String title,
    required IconData icon,
    required Color iconColor,
    required Color iconBg,
  }) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 24.w, vertical: 20.h),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: const Color(0xFFF0F0F0),
            width: 1.w,
          ),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 24.w,
            height: 24.h,
            decoration: BoxDecoration(
              color: iconBg,
              borderRadius: BorderRadius.circular(6.r),
            ),
            child: Icon(
              icon,
              color: iconColor,
              size: 14.sp,
            ),
          ),
          SizedBox(width: 8.w),
          Text(
            title,
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF262626),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAttentionChart() {
    return Container(
      height: 120.h,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFFFF7E6), Color(0xFFFFE7BA)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12.r),
        border: Border.all(
          color: const Color(0xFFFA8C16).withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.trending_down,
                    size: 32.sp,
                    color: const Color(0xFFFA8C16),
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    '成绩趋势分析',
                    style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w500,
                      color: const Color(0xFFFA8C16),
                    ),
                  ),
                ],
              ),
            ),
          ),
          Container(
            width: 1.w,
            height: 60.h,
            color: const Color(0xFFFA8C16).withOpacity(0.3),
          ),
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(16.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '关注指标',
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: const Color(0xFF8C8C8C),
                    ),
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    '连续下降: 8人',
                    style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w500,
                      color: const Color(0xFFFA8C16),
                    ),
                  ),
                  Text(
                    '低于平均: 12人',
                    style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w500,
                      color: const Color(0xFFFA8C16),
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

  Widget _buildStudentGrid() {
    // Mock data for now
    final mockStudents = [
      {'name': '张小明', 'id': '2023001', 'score': 65, 'change': -8},
      {'name': '李小红', 'id': '2023002', 'score': 58, 'change': -12},
      {'name': '王小华', 'id': '2023003', 'score': 72, 'change': -5},
      {'name': '刘小强', 'id': '2023004', 'score': 61, 'change': -15},
    ];
    
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16.w,
        mainAxisSpacing: 16.h,
        childAspectRatio: 1.2,
      ),
      itemCount: mockStudents.length,
      itemBuilder: (context, index) {
        final student = mockStudents[index];
        return _buildStudentCard(student);
      },
    );
  }

  Widget _buildStudentCard(Map<String, dynamic> student) {
    return Container(
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0xFFF0F0F0)),
        borderRadius: BorderRadius.circular(8.r),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40.w,
                height: 40.h,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1890FF), Color(0xFF096DD9)],
                  ),
                  borderRadius: BorderRadius.circular(20.r),
                ),
                child: Center(
                  child: Text(
                    student['name'][0],
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),
              SizedBox(width: 12.w),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      student['name'],
                      style: TextStyle(
                        fontSize: 16.sp,
                        fontWeight: FontWeight.w500,
                        color: const Color(0xFF262626),
                      ),
                    ),
                    Text(
                      student['id'],
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: const Color(0xFF8C8C8C),
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 2.h),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFF7E6),
                  borderRadius: BorderRadius.circular(12.r),
                ),
                child: Text(
                  '需关注',
                  style: TextStyle(
                    fontSize: 10.sp,
                    fontWeight: FontWeight.w500,
                    color: const Color(0xFFFA8C16),
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: 12.h),
          Row(
            children: [
              Expanded(
                child: Column(
                  children: [
                    Text(
                      '${student['score']}',
                      style: TextStyle(
                        fontSize: 16.sp,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFFFF4D4F),
                      ),
                    ),
                    Text(
                      '最新成绩',
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: const Color(0xFF8C8C8C),
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  children: [
                    Text(
                      '${student['change']}',
                      style: TextStyle(
                        fontSize: 16.sp,
                        fontWeight: FontWeight.w600,
                        color: student['change'] < 0
                            ? const Color(0xFFFF4D4F)
                            : const Color(0xFF52C41A),
                      ),
                    ),
                    Text(
                      '成绩变化',
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: const Color(0xFF8C8C8C),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildKnowledgeChart() {
    return Container(
      height: 200.h,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFF9F0FF), Color(0xFFE6F7FF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12.r),
        border: Border.all(
          color: const Color(0xFF722ED1).withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.bar_chart,
              size: 48.sp,
              color: const Color(0xFF722ED1).withOpacity(0.6),
            ),
            SizedBox(height: 12.h),
            Text(
              '知识点掌握度分布图',
              style: TextStyle(
                fontSize: 16.sp,
                fontWeight: FontWeight.w500,
                color: const Color(0xFF722ED1),
              ),
            ),
            SizedBox(height: 4.h),
            Text(
              '等待图表库集成',
              style: TextStyle(
                fontSize: 12.sp,
                color: const Color(0xFF8C8C8C),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKnowledgeList() {
    // Mock data for now
    final mockKnowledge = [
      {'name': '函数与方程', 'description': '一次函数、二次函数的性质与应用', 'mastery': 65.0},
      {'name': '几何图形', 'description': '三角形、四边形的性质与计算', 'mastery': 78.0},
      {'name': '数据统计', 'description': '平均数、中位数、众数的计算', 'mastery': 45.0},
      {'name': '概率初步', 'description': '简单事件的概率计算', 'mastery': 82.0},
    ];
    
    return Column(
      children: mockKnowledge.map((knowledge) {
        return _buildKnowledgeItem(knowledge);
      }).toList(),
    );
  }

  Widget _buildKnowledgeItem(Map<String, dynamic> knowledge) {
    final mastery = knowledge['mastery'] as double;
    Color statusColor;
    IconData statusIcon;
    
    if (mastery >= 90) {
      statusColor = const Color(0xFF52C41A);
      statusIcon = Icons.check_circle;
    } else if (mastery >= 70) {
      statusColor = const Color(0xFFFA8C16);
      statusIcon = Icons.radio_button_unchecked;
    } else {
      statusColor = const Color(0xFFFF4D4F);
      statusIcon = Icons.cancel;
    }

    return Container(
      margin: EdgeInsets.only(bottom: 16.h),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0xFFF0F0F0)),
        borderRadius: BorderRadius.circular(8.r),
      ),
      child: Row(
        children: [
          Icon(
            statusIcon,
            color: statusColor,
            size: 20.sp,
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  knowledge['name'],
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w500,
                    color: const Color(0xFF262626),
                  ),
                ),
                SizedBox(height: 4.h),
                Text(
                  knowledge['description'],
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: const Color(0xFF8C8C8C),
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${mastery.toInt()}%',
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.w600,
                  color: statusColor,
                ),
              ),
              Text(
                '掌握度',
                style: TextStyle(
                  fontSize: 12.sp,
                  color: const Color(0xFF8C8C8C),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSidePanel() {
    return Column(
      children: [
        _buildInsightsCard(),
        SizedBox(height: 24.h),
        _buildRecommendationsCard(),
      ],
    );
  }

  Widget _buildInsightsCard() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildCardHeader(
            title: '关键洞察',
            icon: Icons.lightbulb,
            iconColor: const Color(0xFFFA8C16),
            iconBg: const Color(0xFFFFF7E6),
          ),
          Padding(
            padding: EdgeInsets.all(24.w),
            child: Column(
              children: [
                _buildInsightItem(
                  '班级整体数学成绩呈下降趋势，需要重点关注基础知识的巩固',
                  Icons.trending_down,
                  const Color(0xFFFF4D4F),
                ),
                _buildInsightItem(
                  '函数与方程章节掌握度较低，建议增加相关练习',
                  Icons.functions,
                  const Color(0xFFFA8C16),
                ),
                _buildInsightItem(
                  '8名学生连续两次考试成绩下滑，需要个别辅导',
                  Icons.person_search,
                  const Color(0xFF722ED1),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationsCard() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildCardHeader(
            title: 'AI建议',
            icon: Icons.smart_toy,
            iconColor: const Color(0xFF1890FF),
            iconBg: const Color(0xFFE6F7FF),
          ),
          Padding(
            padding: EdgeInsets.all(24.w),
            child: Column(
              children: [
                _buildRecommendationItem(
                  '针对性练习',
                  '为薄弱学生推送基础运算专项练习',
                  Icons.assignment,
                  const Color(0xFF1890FF),
                ),
                _buildRecommendationItem(
                  '分层教学',
                  '根据学生水平调整教学内容和进度',
                  Icons.layers,
                  const Color(0xFF52C41A),
                ),
                _buildRecommendationItem(
                  '个别辅导',
                  '课后为重点关注学生提供一对一指导',
                  Icons.person,
                  const Color(0xFFFA8C16),
                ),
                SizedBox(height: 16.h),
                _buildGeneratePlanButton(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightItem(String insight, IconData icon, Color color) {
    return Container(
      margin: EdgeInsets.only(bottom: 12.h),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.withOpacity(0.05), color.withOpacity(0.02)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12.r),
        border: Border.all(
          color: color.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 32.w,
            height: 32.h,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8.r),
            ),
            child: Icon(
              icon,
              color: color,
              size: 16.sp,
            ),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: Text(
              insight,
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF262626),
                height: 1.4,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationItem(String title, String description, IconData icon, Color color) {
    return Container(
      margin: EdgeInsets.only(bottom: 12.h),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            color.withOpacity(0.05),
            color.withOpacity(0.02),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12.r),
        border: Border.all(
          color: color.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40.w,
            height: 40.h,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10.r),
            ),
            child: Icon(
              icon,
              color: color,
              size: 20.sp,
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
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w600,
                    color: color.withOpacity(0.9),
                  ),
                ),
                SizedBox(height: 4.h),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: const Color(0xFF6B7280),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGeneratePlanButton() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF52C41A), Color(0xFF389E0D)],
        ),
        borderRadius: BorderRadius.circular(8.r),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(8.r),
          onTap: () {
            // TODO: 生成详细辅导方案
          },
          child: Padding(
            padding: EdgeInsets.symmetric(vertical: 12.h),
            child: Text(
              '生成详细辅导方案',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14.sp,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
          ),
        ),
      ),
    );
  }
}