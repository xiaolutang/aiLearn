import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../core/providers/grade_provider.dart';
import '../../../../core/models/grade_model.dart' hide GradeStatistics;
import '../../../../core/data/repositories/grade_repository.dart' show GradeStatistics;
import '../../../../shared/themes/app_theme.dart';
import '../../../../core/utils/app_logger.dart';
import '../widgets/grade_statistics_card.dart';

class GradeAnalysisPage extends StatefulWidget {
  const GradeAnalysisPage({Key? key}) : super(key: key);

  @override
  State<GradeAnalysisPage> createState() => _GradeAnalysisPageState();
}

class _GradeAnalysisPageState extends State<GradeAnalysisPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String? _selectedStudentId;
  String? _selectedClassId;
  
  @override
  void initState() {
    super.initState();
    AppLogger.info('GradeAnalysisPage: 页面初始化');
    _tabController = TabController(length: 3, vsync: this);
    
    // 监听标签页切换
    _tabController.addListener(_onTabChanged);
    
    // 初始化数据
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadInitialData();
    });
  }

  @override
  void dispose() {
    AppLogger.debug('GradeAnalysisPage: 页面销毁，清理资源');
    _tabController.removeListener(_onTabChanged);
    _tabController.dispose();
    super.dispose();
  }

  void _onTabChanged() {
    if (_tabController.indexIsChanging) {
      final tabNames = ['班级分析', '学生分析', '科目分析'];
      AppLogger.info('GradeAnalysisPage: 用户切换标签页', {
        'tabIndex': _tabController.index,
        'tabName': tabNames[_tabController.index]
      });
    }
  }

  Future<void> _loadInitialData() async {
    AppLogger.info('GradeAnalysisPage: 开始加载初始数据');
    try {
      final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
      await gradeProvider.loadGrades();
      await gradeProvider.loadStatistics();
      AppLogger.info('GradeAnalysisPage: 初始数据加载完成');
    } catch (e, stackTrace) {
      AppLogger.error('GradeAnalysisPage: 初始数据加载失败', e, stackTrace);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('成绩分析'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: '班级分析'),
            Tab(text: '学生分析'),
            Tab(text: '科目分析'),
          ],
        ),
      ),
      body: Consumer<GradeProvider>(
        builder: (context, gradeProvider, child) {
          return TabBarView(
            controller: _tabController,
            children: [
              _buildClassAnalysis(gradeProvider),
              _buildStudentAnalysis(gradeProvider),
              _buildSubjectAnalysis(gradeProvider),
            ],
          );
        },
      ),
    );
  }

  Widget _buildClassAnalysis(GradeProvider gradeProvider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '班级成绩统计',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          if (gradeProvider.isLoading)
            const Center(child: CircularProgressIndicator())
          else if (gradeProvider.statistics == null)
            const Center(
              child: Text(
                '暂无统计数据',
                style: TextStyle(fontSize: 16),
              ),
            )
          else
            GradeStatisticsCard(
              statistics: gradeProvider.statistics!,
              margin: const EdgeInsets.only(bottom: 12),
            ),
          const SizedBox(height: 24),
          _buildClassTrendChart(gradeProvider),
        ],
      ),
    );
  }

  Widget _buildStudentAnalysis(GradeProvider gradeProvider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '学生选择',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            value: _selectedStudentId,
            decoration: const InputDecoration(
              labelText: '选择学生',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(
                value: 'student1',
                child: Text('张三'),
              ),
              DropdownMenuItem(
                value: 'student2',
                child: Text('李四'),
              ),
              DropdownMenuItem(
                value: 'student3',
                child: Text('王五'),
              ),
            ],
            onChanged: (value) {
              AppLogger.info('GradeAnalysisPage: 用户选择学生', {'studentId': value});
              setState(() {
                _selectedStudentId = value;
              });
              if (value != null) {
                _loadStudentAnalysis(value);
              }
            },
          ),
          const SizedBox(height: 24),
          if (_selectedStudentId != null) ...
            _buildStudentAnalysisContent(gradeProvider),
        ],
      ),
    );
  }

  Widget _buildSubjectAnalysis(GradeProvider gradeProvider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '科目成绩分析',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          if (gradeProvider.availableSubjects.isEmpty)
            const Center(
              child: Text(
                '暂无科目数据',
                style: TextStyle(fontSize: 16),
              ),
            )
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: gradeProvider.availableSubjects.length,
              itemBuilder: (context, index) {
                final subjectName = gradeProvider.availableSubjects[index];
                final subject = Subject(
                  id: subjectName,
                  name: subjectName,
                  code: subjectName,
                  totalScore: 100.0,
                );
                return _buildSubjectCard(subject, gradeProvider);
              },
            ),
        ],
      ),
    );
  }

  List<Widget> _buildStudentAnalysisContent(GradeProvider gradeProvider) {
    // 模拟学生分析数据
    final studentAnalysis = StudentGradeAnalysis(
      studentId: _selectedStudentId!,
      studentName: _getStudentName(_selectedStudentId!),
      grades: [],
      averageScore: 87.5,
      overallLevel: '良好',
      strengths: ['数学', '物理'],
      weaknesses: ['英语', '语文'],
      recommendations: [
        '加强英语词汇积累，多做阅读理解练习',
        '提高语文作文水平，多阅读优秀范文',
        '保持数学优势，可以尝试更有挑战性的题目',
      ],
      subjectAverages: {
        '数学': 92.0,
        '物理': 89.0,
        '化学': 85.0,
        '英语': 78.0,
        '语文': 81.0,
      },
      subjectTrends: {
        '数学': 'improving',
        '物理': 'stable',
        '化学': 'improving',
        '英语': 'declining',
        '语文': 'stable',
      },
    );

    return [
      Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${studentAnalysis.studentName} 的成绩分析',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _buildInfoItem('平均分', '${studentAnalysis.averageScore}'),
                  ),
                  Expanded(
                    child: _buildInfoItem('总体水平', studentAnalysis.overallLevel),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
      const SizedBox(height: 16),
      Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '各科成绩',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              ...studentAnalysis.subjectAverages.entries.map((entry) {
                final trend = studentAnalysis.subjectTrends[entry.key] ?? 'stable';
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: Text(entry.key),
                      ),
                      Expanded(
                        child: Text('${entry.value}分'),
                      ),
                      Icon(
                        _getTrendIcon(trend),
                        color: _getTrendColor(trend),
                        size: 16,
                      ),
                    ],
                  ),
                );
              }).toList(),
            ],
          ),
        ),
      ),
      const SizedBox(height: 16),
      Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '优势科目',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: studentAnalysis.strengths.map((subject) {
                  return Chip(
                    label: Text(subject),
                    backgroundColor: Colors.green.shade100,
                    labelStyle: TextStyle(color: Colors.green.shade700),
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
              const Text(
                '薄弱科目',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: studentAnalysis.weaknesses.map((subject) {
                  return Chip(
                    label: Text(subject),
                    backgroundColor: Colors.orange.shade100,
                    labelStyle: TextStyle(color: Colors.orange.shade700),
                  );
                }).toList(),
              ),
            ],
          ),
        ),
      ),
      const SizedBox(height: 16),
      Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '学习建议',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              ...studentAnalysis.recommendations.asMap().entries.map((entry) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${entry.key + 1}. ',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: AppTheme.primaryColor,
                        ),
                      ),
                      Expanded(
                        child: Text(entry.value),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ],
          ),
        ),
      ),
    ];
  }

  Widget _buildClassTrendChart(GradeProvider gradeProvider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '班级成绩趋势',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Container(
              height: 200,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade300),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Center(
                child: Text(
                  '趋势图表\n(待集成图表库)',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSubjectCard(Subject subject, GradeProvider gradeProvider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    subject.name,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Text(
                  '总分: ${subject.totalScore}',
                  style: TextStyle(
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
            if (subject.description != null) ...[
              const SizedBox(height: 8),
              Text(
                subject.description!,
                style: TextStyle(
                  color: Colors.grey.shade600,
                ),
              ),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildSubjectStat('平均分', '85.2'),
                ),
                Expanded(
                  child: _buildSubjectStat('及格率', '92%'),
                ),
                Expanded(
                  child: _buildSubjectStat('优秀率', '68%'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSubjectStat(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppTheme.primaryColor,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }

  Widget _buildInfoItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  IconData _getTrendIcon(String trend) {
    switch (trend) {
      case 'improving':
        return Icons.trending_up;
      case 'declining':
        return Icons.trending_down;
      default:
        return Icons.trending_flat;
    }
  }

  Color _getTrendColor(String trend) {
    switch (trend) {
      case 'improving':
        return Colors.green;
      case 'declining':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Future<void> _loadStudentAnalysis(String studentId) async {
    AppLogger.info('GradeAnalysisPage: 开始加载学生分析数据', {'studentId': studentId});
    try {
      final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
      await gradeProvider.loadGrades();
      AppLogger.info('GradeAnalysisPage: 学生分析数据加载完成', {'studentId': studentId});
    } catch (e, stackTrace) {
      AppLogger.error('GradeAnalysisPage: 学生分析数据加载失败 - studentId: $studentId', e, stackTrace);
    }
  }

  String _getStudentName(String studentId) {
    switch (studentId) {
      case 'student1':
        return '张三';
      case 'student2':
        return '李四';
      case 'student3':
        return '王五';
      default:
        return '未知学生';
    }
  }
}