import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import '../../../../core/providers/grade_provider.dart';
import '../../../../core/models/grade_model.dart' show Grade, GradeStatistics;
import '../../../../core/data/repositories/grade_repository.dart' hide Grade, GradeStatistics;
import '../../../../shared/themes/app_theme.dart';
import '../widgets/grade_card.dart';
import '../widgets/grade_filter_sheet.dart';
import '../widgets/grade_statistics_card.dart';
import 'grade_input_page.dart';
import 'grade_analysis_page.dart';

class GradesPage extends StatefulWidget {
  const GradesPage({Key? key}) : super(key: key);

  @override
  State<GradesPage> createState() => _GradesPageState();
}

class _GradesPageState extends State<GradesPage> {
  final ScrollController _scrollController = ScrollController();
  String _selectedFilter = '全部学生';
  String _selectedExam = '期中考试';
  String _searchQuery = '';
  String _selectedSubject = '全部';
  String _selectedClass = '全部';
  
  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    
    // 初始化数据
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadInitialData();
    });
  }
  
  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }
  
  void _onScroll() {
    if (_scrollController.position.pixels ==
        _scrollController.position.maxScrollExtent) {
      final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
      gradeProvider.loadMoreGrades();
    }
  }
  
  Future<void> _loadInitialData() async {
    final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
    await Future.wait<void>([
      gradeProvider.loadGrades(forceRefresh: true),
      gradeProvider.loadExams(refresh: true),
      gradeProvider.loadSubjects(refresh: true),
    ]);
  }
  
  Future<void> _refreshData() async {
    final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
    await gradeProvider.loadGrades(forceRefresh: true);
  }
  
  void _showFilterSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => GradeFilterSheet(
        onApplyFilter: (params) {
          final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
          gradeProvider.loadGrades(forceRefresh: true);
        },
      ),
    );
  }
  
  void _navigateToGradeInput() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const GradeInputPage(),
      ),
    );
  }
  
  void _navigateToGradeAnalysis() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const GradeAnalysisPage(),
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _buildTopNavigation(),
          Expanded(
            child: Consumer<GradeProvider>(
              builder: (context, gradeProvider, child) {
                return Column(
                  children: [
                    _buildPageHeader(),
                    _buildStatisticsCards(),
                    Expanded(
                      child: _buildMainContent(gradeProvider),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
  
  // 构建顶部导航栏
  Widget _buildTopNavigation() {
    return Container(
      height: 60.h,
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Logo区域
          Container(
            padding: EdgeInsets.symmetric(horizontal: 24.w),
            child: Row(
              children: [
                Container(
                  width: 32.w,
                  height: 32.w,
                  decoration: BoxDecoration(
                    color: Colors.blue,
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                  child: const Icon(
                    Icons.school,
                    color: Colors.white,
                    size: 20,
                  ),
                ),
                SizedBox(width: 12.w),
                Text(
                  '智能教学助手',
                  style: TextStyle(
                    fontSize: 18.sp,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
              ],
            ),
          ),
          
          // 导航菜单
          Expanded(
            child: Row(
              children: [
                _buildNavItem('工作台', false),
                _buildNavItem('备课', false),
                _buildNavItem('上课', false),
                _buildNavItem('成绩', true),
                _buildNavItem('分析', false),
              ],
            ),
          ),
          
          // 用户头像
          Container(
            margin: EdgeInsets.only(right: 24.w),
            child: CircleAvatar(
              radius: 18.r,
              backgroundColor: Colors.blue,
              child: const Text(
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
    );
  }
  
  Widget _buildNavItem(String title, bool isActive) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 8.w),
      padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
      decoration: BoxDecoration(
        color: isActive ? Colors.blue.withOpacity(0.1) : Colors.transparent,
        borderRadius: BorderRadius.circular(6.r),
      ),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14.sp,
          color: isActive ? Colors.blue : Colors.black54,
          fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
        ),
      ),
    );
  }
  
  // 构建页面头部
  Widget _buildPageHeader() {
    return Container(
      padding: EdgeInsets.all(24.w),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '成绩管理',
            style: TextStyle(
              fontSize: 24.sp,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          Row(
            children: [
              _buildActionButton(
                icon: Icons.assessment,
                label: '导出报告',
                onPressed: () {},
              ),
              SizedBox(width: 12.w),
              _buildActionButton(
                icon: Icons.upload_file,
                label: '批量导入',
                onPressed: () {},
              ),
              SizedBox(width: 12.w),
              _buildActionButton(
                icon: Icons.add,
                label: '录入成绩',
                isPrimary: true,
                onPressed: _navigateToGradeInput,
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
    bool isPrimary = false,
  }) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(
        icon,
        size: 16.sp,
        color: isPrimary ? Colors.white : Colors.black54,
      ),
      label: Text(
        label,
        style: TextStyle(
          fontSize: 14.sp,
          color: isPrimary ? Colors.white : Colors.black54,
        ),
      ),
      style: ElevatedButton.styleFrom(
        backgroundColor: isPrimary ? Colors.blue : Colors.grey[100],
        elevation: 0,
        padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(6.r),
        ),
      ),
    );
  }
  
  // 构建统计卡片
  Widget _buildStatisticsCards() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 24.w, vertical: 16.h),
      child: Row(
        children: [
          Expanded(
            child: _buildStatCard(
              title: '学生总数',
              value: '156',
              change: '+3 较上学期',
              icon: Icons.group,
              gradient: const LinearGradient(
                colors: [Color(0xFF667eea), Color(0xFF764ba2)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),
          SizedBox(width: 16.w),
          Expanded(
            child: _buildStatCard(
              title: '班级平均分',
              value: '85.6',
              change: '+2.3 较上次',
              icon: Icons.trending_up,
              gradient: const LinearGradient(
                colors: [Color(0xFF11998e), Color(0xFF38ef7d)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),
          SizedBox(width: 16.w),
          Expanded(
            child: _buildStatCard(
              title: '优秀率',
              value: '68%',
              change: '+5% 较上次',
              icon: Icons.emoji_events,
              gradient: const LinearGradient(
                colors: [Color(0xFFf093fb), Color(0xFFf5576c)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),
          SizedBox(width: 16.w),
          Expanded(
            child: _buildStatCard(
              title: '进步学生',
              value: '23',
              change: '+8 较上次',
              icon: Icons.rocket_launch,
              gradient: const LinearGradient(
                colors: [Color(0xFF4facfe), Color(0xFF00f2fe)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildStatCard({
    required String title,
    required String value,
    required String change,
    required IconData icon,
    required LinearGradient gradient,
  }) {
    return Container(
      padding: EdgeInsets.all(20.w),
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: gradient.colors.first.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: EdgeInsets.all(12.w),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12.r),
                ),
                child: Icon(
                  icon,
                  color: Colors.white,
                  size: 24.sp,
                ),
              ),
              Icon(
                Icons.more_vert,
                color: Colors.white.withOpacity(0.7),
                size: 20.sp,
              ),
            ],
          ),
          SizedBox(height: 20.h),
          Text(
            value,
            style: TextStyle(
              fontSize: 32.sp,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          SizedBox(height: 4.h),
          Text(
            title,
            style: TextStyle(
              fontSize: 14.sp,
              color: Colors.white.withOpacity(0.9),
              fontWeight: FontWeight.w500,
            ),
          ),
          SizedBox(height: 8.h),
          Row(
            children: [
              Icon(
                Icons.trending_up,
                color: Colors.white.withOpacity(0.8),
                size: 16.sp,
              ),
              SizedBox(width: 4.w),
              Text(
                change,
                style: TextStyle(
                  fontSize: 12.sp,
                  color: Colors.white.withOpacity(0.8),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  // 构建主要内容区域
  Widget _buildMainContent(GradeProvider gradeProvider) {
    return Container(
      margin: EdgeInsets.all(24.w),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 主面板
          Expanded(
            flex: 3,
            child: _buildMainPanel(gradeProvider),
          ),
          SizedBox(width: 24.w),
          // 右侧面板
          Expanded(
            flex: 1,
            child: _buildRightPanel(),
          ),
        ],
      ),
    );
  }
  
  Widget _buildMainPanel(GradeProvider gradeProvider) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildPanelHeader(),
          Expanded(
            child: _buildGradeTable(gradeProvider),
          ),
          _buildPagination(),
        ],
      ),
    );
  }
  
  Widget _buildPanelHeader() {
    return Container(
      padding: EdgeInsets.all(20.w),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: Colors.grey[200]!,
            width: 1,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '高一(3)班 - 数学期中考试',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          Row(
            children: [
              _buildFilterDropdown(
                value: _selectedFilter,
                items: ['全部学生', '优秀学生', '需关注学生'],
                onChanged: (value) {
                  setState(() {
                    _selectedFilter = value!;
                  });
                },
              ),
              SizedBox(width: 12.w),
              _buildFilterDropdown(
                value: _selectedExam,
                items: ['期中考试', '期末考试', '月考'],
                onChanged: (value) {
                  setState(() {
                    _selectedExam = value!;
                  });
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildFilterDropdown({
    required String value,
    required List<String> items,
    required ValueChanged<String?> onChanged,
  }) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(6.r),
      ),
      child: DropdownButton<String>(
        value: value,
        items: items.map((item) {
          return DropdownMenuItem(
            value: item,
            child: Text(
              item,
              style: TextStyle(fontSize: 14.sp),
            ),
          );
        }).toList(),
        onChanged: onChanged,
        underline: const SizedBox(),
        isDense: true,
      ),
    );
  }
  
  Widget _buildGradeTable(GradeProvider gradeProvider) {
    if (gradeProvider.error != null) {
      return _buildErrorWidget(gradeProvider.error!, () {
        gradeProvider.clearError();
        _loadInitialData();
      });
    }
    
    if (gradeProvider.grades.isEmpty && !gradeProvider.isLoading) {
      return _buildEmptyWidget(
        '暂无成绩数据',
        '点击右上角按钮开始录入成绩',
        Icons.grade,
      );
    }
    
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade200),
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Column(
        children: [
          _buildTableHeaderRow(),
          Expanded(
            child: ListView.builder(
              itemCount: gradeProvider.grades.take(6).length,
              itemBuilder: (context, index) {
                final grade = gradeProvider.grades[index];
                return _buildTableRowWidget(grade, index);
              },
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildTableHeaderRow() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 16.h),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.grey.shade50, Colors.grey.shade100],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(12.r),
          topRight: Radius.circular(12.r),
        ),
        border: Border(
          bottom: BorderSide(
            color: Colors.grey.shade300,
            width: 1,
          ),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              '学生信息',
              style: TextStyle(
                fontSize: 15.sp,
                fontWeight: FontWeight.w700,
                color: Colors.black87,
              ),
            ),
          ),
          Expanded(
            child: Text(
              '语文',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15.sp,
                fontWeight: FontWeight.w700,
                color: Colors.black87,
              ),
            ),
          ),
          Expanded(
            child: Text(
              '数学',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15.sp,
                fontWeight: FontWeight.w700,
                color: Colors.black87,
              ),
            ),
          ),
          Expanded(
            child: Text(
              '英语',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15.sp,
                fontWeight: FontWeight.w700,
                color: Colors.black87,
              ),
            ),
          ),
          Expanded(
            child: Text(
              '总分',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15.sp,
                fontWeight: FontWeight.w700,
                color: Colors.black87,
              ),
            ),
          ),
          Expanded(
            child: Text(
              '趋势',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15.sp,
                fontWeight: FontWeight.w700,
                color: Colors.black87,
              ),
            ),
          ),
          Expanded(
            child: Text(
              '操作',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15.sp,
                fontWeight: FontWeight.w700,
                color: Colors.black87,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildTableRowWidget(Grade grade, int index) {
    return InkWell(
      onTap: () => _showGradeDetail(grade),
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 16.h),
        decoration: BoxDecoration(
          color: index.isEven ? Colors.white : Colors.grey.shade50,
          border: Border(
            bottom: BorderSide(
              color: Colors.grey.shade200,
              width: 0.5,
            ),
          ),
        ),
        child: Row(
          children: [
            Expanded(
              flex: 2,
              child: _buildStudentCellWidget(grade),
            ),
            Expanded(
              child: _buildScoreCellWidget('95', _getScoreColor(95)),
            ),
            Expanded(
              child: _buildScoreCellWidget('88', _getScoreColor(88)),
            ),
            Expanded(
              child: _buildScoreCellWidget('92', _getScoreColor(92)),
            ),
            Expanded(
              child: _buildScoreCellWidget('275', _getScoreColor(275, isTotal: true)),
            ),
            Expanded(
              child: _buildTrendCellWidget(true),
            ),
            Expanded(
              child: _buildActionCellWidget(grade),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildTableCell(String text, {bool isHeader = false}) {
    return Container(
      padding: EdgeInsets.all(12.w),
      child: Text(
        text,
        style: TextStyle(
          fontSize: isHeader ? 14.sp : 13.sp,
          fontWeight: isHeader ? FontWeight.w600 : FontWeight.normal,
          color: isHeader ? Colors.black87 : Colors.black54,
        ),
        textAlign: TextAlign.center,
      ),
    );
  }
  
  Widget _buildStudentCellWidget(Grade grade) {
    return Row(
      children: [
        CircleAvatar(
          radius: 18.r,
          backgroundColor: Colors.blue,
          child: Text(
            grade.studentName.isNotEmpty ? grade.studentName[0] : '?',
            style: TextStyle(
              color: Colors.white,
              fontSize: 14.sp,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        SizedBox(width: 12.w),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                grade.studentName,
                style: TextStyle(
                  fontSize: 14.sp,
                  fontWeight: FontWeight.w600,
                  color: Colors.black87,
                ),
              ),
              SizedBox(height: 2.h),
              Text(
                grade.studentId,
                style: TextStyle(
                  fontSize: 12.sp,
                  color: Colors.black54,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildScoreCellWidget(String score, Color color) {
    return Text(
      score,
      style: TextStyle(
        fontSize: 15.sp,
        fontWeight: FontWeight.bold,
        color: color,
      ),
      textAlign: TextAlign.center,
    );
  }
  
  Color _getScoreColor(double score, {bool isTotal = false}) {
    if (isTotal) {
      if (score >= 270) return Colors.green;
      if (score >= 240) return Colors.blue;
      if (score >= 180) return Colors.orange;
      return Colors.red;
    } else {
      if (score >= 90) return Colors.green;
      if (score >= 80) return Colors.blue;
      if (score >= 60) return Colors.orange;
      return Colors.red;
    }
  }
  
  Widget _buildTrendCellWidget(bool isUp) {
    return Icon(
      isUp ? Icons.trending_up : Icons.trending_down,
      color: isUp ? Colors.green : Colors.red,
      size: 18.sp,
    );
  }
  
  Widget _buildActionCellWidget(Grade grade) {
    return PopupMenuButton<String>(
      onSelected: (value) {
        switch (value) {
          case 'edit':
            _editGrade(grade);
            break;
          case 'delete':
            _deleteGrade(grade);
            break;
        }
      },
      itemBuilder: (context) => [
        const PopupMenuItem(
          value: 'edit',
          child: Text('编辑'),
        ),
        const PopupMenuItem(
          value: 'delete',
          child: Text('删除'),
        ),
      ],
      child: Icon(
        Icons.more_horiz,
        size: 18.sp,
        color: Colors.black54,
      ),
    );
  }
  
  Widget _buildPagination() {
    return Container(
      padding: EdgeInsets.all(20.w),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(
            color: Colors.grey[200]!,
            width: 1,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '显示 1-10 条，共 45 条记录',
            style: TextStyle(
              fontSize: 14.sp,
              color: Colors.black54,
            ),
          ),
          Row(
            children: [
              _buildPageButton('‹', false),
              _buildPageButton('1', true),
              _buildPageButton('2', false),
              _buildPageButton('3', false),
              _buildPageButton('4', false),
              _buildPageButton('5', false),
              _buildPageButton('›', false),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildPageButton(String text, bool isActive) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 2.w),
      child: TextButton(
        onPressed: () {},
        style: TextButton.styleFrom(
          backgroundColor: isActive ? Colors.blue : Colors.transparent,
          foregroundColor: isActive ? Colors.white : Colors.black54,
          minimumSize: Size(32.w, 32.w),
          padding: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(4.r),
          ),
        ),
        child: Text(
          text,
          style: TextStyle(fontSize: 14.sp),
        ),
      ),
    );
  }
  
  Widget _buildRightPanel() {
    return Column(
      children: [
        _buildAnalysisCard(),
        SizedBox(height: 16.h),
        _buildKnowledgeCard(),
        SizedBox(height: 16.h),
        Expanded(
          child: _buildAISuggestions(),
        ),
      ],
    );
  }
  
  Widget _buildAnalysisCard() {
    return Container(
      padding: EdgeInsets.all(24.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: EdgeInsets.all(8.w),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    child: Icon(
                      Icons.analytics,
                      color: Colors.blue,
                      size: 20.sp,
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Text(
                    '成绩分析',
                    style: TextStyle(
                      fontSize: 18.sp,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
              Icon(
                Icons.more_vert,
                color: Colors.black54,
                size: 20.sp,
              ),
            ],
          ),
          SizedBox(height: 20.h),
          // 图表区域
          Container(
            height: 180.h,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.blue.shade50, Colors.blue.shade100],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12.r),
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.bar_chart,
                    size: 48.sp,
                    color: Colors.blue,
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    '成绩分布图表',
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w600,
                      color: Colors.blue.shade700,
                    ),
                  ),
                  Text(
                    '等待图表库集成',
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: Colors.blue.shade600,
                    ),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 20.h),
          _buildInsightItem('✓', '优秀率较上次提升5%', Colors.green),
          _buildInsightItem('!', '6名学生需重点关注', Colors.orange),
          _buildInsightItem('i', '函数知识点掌握较弱', Colors.blue),
        ],
      ),
    );
  }
  
  Widget _buildKnowledgeCard() {
    return Container(
      padding: EdgeInsets.all(24.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: EdgeInsets.all(8.w),
                    decoration: BoxDecoration(
                      color: Colors.purple.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    child: Icon(
                      Icons.psychology,
                      color: Colors.purple,
                      size: 20.sp,
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Text(
                    '知识点掌握',
                    style: TextStyle(
                      fontSize: 18.sp,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
              Icon(
                Icons.more_vert,
                color: Colors.black54,
                size: 20.sp,
              ),
            ],
          ),
          SizedBox(height: 20.h),
          // 图表区域
          Container(
            height: 140.h,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.purple.shade50, Colors.purple.shade100],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12.r),
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.radar,
                    size: 40.sp,
                    color: Colors.purple,
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    '知识点掌握度',
                    style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w600,
                      color: Colors.purple.shade700,
                    ),
                  ),
                  Text(
                    '等待图表库集成',
                    style: TextStyle(
                      fontSize: 11.sp,
                      color: Colors.purple.shade600,
                    ),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 16.h),
          // 知识点列表
          Column(
            children: [
              _buildKnowledgeItem('基础运算', 95, Colors.green),
              _buildKnowledgeItem('函数性质', 72, Colors.orange),
              _buildKnowledgeItem('综合应用', 68, Colors.orange),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildAISuggestions() {
    return Container(
      padding: EdgeInsets.all(24.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: EdgeInsets.all(8.w),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Colors.amber.shade200, Colors.amber.shade300],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    child: Icon(
                      Icons.auto_awesome,
                      color: Colors.amber.shade700,
                      size: 20.sp,
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Text(
                    'AI智能建议',
                    style: TextStyle(
                      fontSize: 18.sp,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 4.h),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12.r),
                ),
                child: Text(
                  '3条新建议',
                  style: TextStyle(
                    fontSize: 11.sp,
                    color: Colors.green.shade700,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: 20.h),
          Expanded(
            child: ListView(
              children: [
                _buildSuggestionItem(
                  '针对几何图形薄弱知识点，建议增加练习题',
                  '基于班级平均掌握度72%的分析结果',
                  Icons.assignment,
                  Colors.blue,
                  '高优先级',
                ),
                _buildSuggestionItem(
                  '张三、李四等学生需要个别辅导',
                  '这些学生在多个知识点上表现不佳',
                  Icons.person,
                  Colors.green,
                  '中优先级',
                ),
                _buildSuggestionItem(
                  '建议在下次考试中加强应用题考查',
                  '应用题得分率偏低，需要重点关注',
                  Icons.quiz,
                  Colors.orange,
                  '低优先级',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildInsightItem(String icon, String text, Color color) {
    return Container(
      margin: EdgeInsets.only(bottom: 8.h),
      child: Row(
        children: [
          Container(
            width: 20.w,
            height: 20.w,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10.r),
            ),
            child: Center(
              child: Text(
                icon,
                style: TextStyle(
                  fontSize: 12.sp,
                  color: color,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          SizedBox(width: 8.w),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 13.sp,
                color: Colors.black54,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildKnowledgeItem(String title, int percentage, Color color) {
    return Container(
      margin: EdgeInsets.only(bottom: 12.h),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12.r),
        border: Border.all(
          color: color.withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                SizedBox(height: 4.h),
                Text(
                  '掌握度: $percentage%',
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: Colors.black54,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8.w, vertical: 4.h),
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(12.r),
            ),
            child: Text(
              '$percentage%',
              style: TextStyle(
                fontSize: 12.sp,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionItem(
    String title,
    String description,
    IconData icon,
    Color color,
    String priority,
  ) {
    return Container(
      margin: EdgeInsets.only(bottom: 16.h),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        border: Border.all(
          color: color.withOpacity(0.2),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: EdgeInsets.all(6.w),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(6.r),
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
                  title,
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
              ),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
                decoration: BoxDecoration(
                  color: _getPriorityColor(priority).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8.r),
                ),
                child: Text(
                  priority,
                  style: TextStyle(
                    fontSize: 10.sp,
                    color: _getPriorityColor(priority),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: 8.h),
          Text(
            description,
            style: TextStyle(
              fontSize: 12.sp,
              color: Colors.black54,
              height: 1.3,
            ),
          ),
        ],
      ),
    );
  }



  Color _getPriorityColor(String priority) {
    switch (priority) {
      case '高优先级':
        return Colors.red;
      case '中优先级':
        return Colors.orange;
      case '低优先级':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  Widget _buildGradesList(GradeProvider gradeProvider) {
    if (gradeProvider.error != null) {
      return _buildErrorWidget(gradeProvider.error!, () {
        gradeProvider.clearError();
        _loadInitialData();
      });
    }
    
    if (gradeProvider.grades.isEmpty && !gradeProvider.isLoading) {
      return _buildEmptyWidget(
        '暂无成绩数据',
        '点击右下角按钮开始录入成绩',
        Icons.grade,
      );
    }
    
    return RefreshIndicator(
      onRefresh: _refreshData,
      child: ListView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(16),
        itemCount: gradeProvider.grades.length + (gradeProvider.hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == gradeProvider.grades.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: CircularProgressIndicator(),
              ),
            );
          }
          
          final grade = gradeProvider.grades[index];
          return GradeCard(
            grade: grade,
            onTap: () => _showGradeDetail(grade),
            onEdit: () => _editGrade(grade),
            onDelete: () => _deleteGrade(grade),
          );
        },
      ),
    );
  }
  
  Widget _buildStatistics(GradeProvider gradeProvider) {
    if (gradeProvider.statistics == null && !gradeProvider.isLoading) {
      return _buildEmptyWidget(
        '暂无统计数据',
        '请先选择考试查看统计信息',
        Icons.bar_chart,
      );
    }

    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        children: [
          // 统计卡片网格
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  title: '总人数',
                  value: '${gradeProvider.grades.length}',
                  change: '+0 较上次',
                  icon: Icons.people,
                  gradient: LinearGradient(
                    colors: [AppTheme.primaryColor, AppTheme.primaryColor.withOpacity(0.8)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
              ),
              SizedBox(width: 16.w),
              Expanded(
                child: _buildStatCard(
                  title: '平均分',
                  value: gradeProvider.grades.isEmpty
                      ? '0'
                      : (gradeProvider.grades.map((g) => g.score).reduce((a, b) => a + b) /
                              gradeProvider.grades.length)
                          .toStringAsFixed(1),
                  change: '+2.3 较上次',
                  icon: Icons.trending_up,
                  gradient: const LinearGradient(
                    colors: [Colors.green, Color(0xFF4CAF50)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
              ),
              SizedBox(width: 16.w),
              Expanded(
                child: _buildStatCard(
                  title: '最高分',
                  value: gradeProvider.grades.isEmpty
                      ? '0'
                      : gradeProvider.grades.map((g) => g.score).reduce((a, b) => a > b ? a : b).toString(),
                  change: '+5 较上次',
                  icon: Icons.star,
                  gradient: const LinearGradient(
                    colors: [Colors.orange, Color(0xFFFF9800)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
              ),
              SizedBox(width: 16.w),
              Expanded(
                child: _buildStatCard(
                  title: '最低分',
                  value: gradeProvider.grades.isEmpty
                      ? '0'
                      : gradeProvider.grades.map((g) => g.score).reduce((a, b) => a < b ? a : b).toString(),
                  change: '-2 较上次',
                  icon: Icons.trending_down,
                  gradient: const LinearGradient(
                    colors: [Colors.red, Color(0xFFF44336)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: 24.h),
          // 图表区域
          Container(
            height: 300.h,
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: BorderRadius.circular(8.r),
            ),
            child: const Center(
              child: Text(
                '📊 图表区域\n等待图表库集成',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.black54,
                ),
              ),
            ),
          ),
          SizedBox(height: 24.h),
          // 原有统计卡片
          if (gradeProvider.statistics != null)
            Container(
              margin: EdgeInsets.only(bottom: 16.h),
              child: GradeStatisticsCard(
                statistics: gradeProvider.statistics!,
                onTap: () => _showStatisticsDetail(gradeProvider.statistics!),
              ),
            ),
        ],
      ),
    );
  }
  
  Widget _buildExamManagement(GradeProvider gradeProvider) {
    if (gradeProvider.availableExamIds.isEmpty && !gradeProvider.isLoading) {
      return _buildEmptyWidget(
        '暂无考试类型',
        '系统暂未配置考试类型',
        Icons.quiz,
      );
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: gradeProvider.availableExamIds.length,
      itemBuilder: (context, index) {
        final examType = gradeProvider.availableExamIds[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Theme.of(context).primaryColor,
              child: Icon(
                Icons.quiz,
                color: Colors.white,
              ),
            ),
            title: Text(
              examType,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Text(
              '考试类型: $examType',
              style: TextStyle(
                color: Colors.black54,
                fontSize: 12,
              ),
            ),
            trailing: PopupMenuButton(
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'grades',
                  child: Text('查看成绩'),
                ),
                const PopupMenuItem(
                  value: 'statistics',
                  child: Text('统计分析'),
                ),
              ],
              onSelected: (value) => _handleExamTypeAction(examType, value),
            ),
            onTap: () => _showExamTypeDetail(examType),
          ),
        );
      },
    );
  }
  
  Widget _buildErrorWidget(String error, VoidCallback onRetry) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.red,
          ),
          const SizedBox(height: 16),
          Text(
            '加载失败',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            error,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.black54,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: onRetry,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
            ),
            child: const Text('重试'),
          ),
        ],
      ),
    );
  }
  
  Widget _buildEmptyWidget(String title, String subtitle, IconData icon) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            icon,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          Text(
            title,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            subtitle,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.black54,
            ),
          ),
        ],
      ),
    );
  }
  
  Color _getExamStatusColor(String status) {
    switch (status) {
      case 'upcoming':
        return Colors.orange;
      case 'ongoing':
        return Colors.blue;
      case 'completed':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }
  
  IconData _getExamStatusIcon(String status) {
    switch (status) {
      case 'upcoming':
        return Icons.schedule;
      case 'ongoing':
        return Icons.play_arrow;
      case 'completed':
        return Icons.check;
      default:
        return Icons.help;
    }
  }
  
  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }


  
  void _showGradeDetail(Grade grade) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${grade.studentName} - ${grade.subjectName}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('考试: ${grade.examName}'),
            const SizedBox(height: 8),
            Text('成绩: ${grade.score}/${grade.totalScore}'),
            const SizedBox(height: 8),
            Text('得分率: ${(grade.scoreRate * 100).toStringAsFixed(1)}%'),
            if (grade.level != null) ...[
              const SizedBox(height: 8),
              Text('等级: ${grade.level}'),
            ],
            if (grade.rank != null) ...[
              const SizedBox(height: 8),
              Text('排名: ${grade.rank}'),
            ],
            if (grade.remark != null && grade.remark!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text('备注: ${grade.remark}'),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }
  
  void _editGrade(Grade grade) {
    // TODO: 实现编辑成绩功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('编辑功能开发中...')),
    );
  }
  
  void _deleteGrade(Grade grade) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除 ${grade.studentName} 的 ${grade.subjectName} 成绩吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop();
              final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
              final success = await gradeProvider.deleteGrade(grade.id);
              if (success) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('删除成功')),
                );
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(gradeProvider.error ?? '删除失败'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            },
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }
  


  void _showStatisticsDetail(GradeStatistics statistics) {
    // TODO: 实现统计详情页面
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('统计详情功能开发中...')),
    );
  }
  

  
  void _handleExamTypeAction(String examType, String action) {
    switch (action) {
      case 'grades':
        // TODO: 查看考试类型成绩
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('查看 $examType 成绩')),
        );
        break;
      case 'statistics':
        // TODO: 查看考试类型统计
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('查看 $examType 统计')),
        );
        break;
    }
  }
  
  void _showExamTypeDetail(String examType) {
    // TODO: 显示考试类型详情
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('查看 $examType 详情')),
    );
  }
}