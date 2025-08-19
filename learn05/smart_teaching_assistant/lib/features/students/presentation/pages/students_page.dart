import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import '../../../../shared/themes/app_theme.dart';
import '../../../../shared/widgets/layout/responsive_layout.dart';
import '../../../../shared/utils/responsive_utils.dart';
import '../../../../core/providers/student_provider.dart';
import '../../../../core/models/student_model.dart';
import '../../../../core/utils/app_logger.dart';
import '../../../student_management/add_student_page.dart';
import '../../../student_management/student_detail_page.dart';

class StudentsPage extends StatefulWidget {
  const StudentsPage({super.key});

  @override
  State<StudentsPage> createState() => _StudentsPageState();
}

class _StudentsPageState extends State<StudentsPage> with TickerProviderStateMixin {
  late TabController _tabController;
  String _searchQuery = '';
  String? _selectedClassId;
  
  @override
  void initState() {
    super.initState();
    AppLogger.info('StudentsPage: 页面初始化');
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(_onTabChanged);
    _loadData();
  }
  
  @override
  void dispose() {
    AppLogger.debug('StudentsPage: 页面销毁，清理资源');
    _tabController.removeListener(_onTabChanged);
    _tabController.dispose();
    super.dispose();
  }
  
  void _onTabChanged() {
    if (_tabController.indexIsChanging) {
      final tabNames = ['学生列表', '班级分布', '统计分析'];
      AppLogger.debug('StudentsPage: 用户切换标签页', {
        'fromIndex': _tabController.previousIndex,
        'toIndex': _tabController.index,
        'tabName': tabNames[_tabController.index]
      });
    }
  }
  
  Future<void> _loadData() async {
    AppLogger.info('StudentsPage: 开始加载学生数据');
    try {
      final studentProvider = Provider.of<StudentProvider>(context, listen: false);
      await studentProvider.loadStudents();
      AppLogger.info('StudentsPage: 学生数据加载完成', {
        'studentsCount': studentProvider.students.length
      });
    } catch (e, stackTrace) {
      AppLogger.error('StudentsPage: 学生数据加载失败', e, stackTrace);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return ResponsiveLayout(
      appBar: ResponsiveAppBar(
        title: '学生管理',
        actions: [
          ResponsiveButton(
            onPressed: () => _navigateToAddStudent(),
            icon: Icons.add,
            text: ResponsiveUtils.isDesktop(context) ? '添加学生' : '',
          ),
        ],
        bottom: TabBar(
           controller: _tabController,
           tabs: const [
             Tab(text: '学生列表', icon: Icon(Icons.people)),
             Tab(text: '班级分布', icon: Icon(Icons.class_)),
             Tab(text: '统计分析', icon: Icon(Icons.analytics)),
           ],
         ),
      ),
      body: Column(
        children: [
          _buildSearchAndFilter(),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildStudentList(),
                _buildClassDistribution(),
                _buildStatistics(),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSearchAndFilter() {
    return ResponsiveCard(
      margin: EdgeInsets.all(ResponsiveUtils.getGridSpacing(context)),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: TextField(
                  decoration: InputDecoration(
                    hintText: '搜索学生姓名或学号',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                  ),
                  onChanged: (value) {
                    AppLogger.debug('StudentsPage: 用户搜索学生', {
                      'searchQuery': value,
                      'queryLength': value.length
                    });
                    setState(() {
                      _searchQuery = value;
                    });
                  },
                ),
              ),
              SizedBox(width: ResponsiveUtils.getGridSpacing(context)),
              ResponsiveButton(
                   onPressed: () {
                     AppLogger.debug('StudentsPage: 用户点击筛选按钮');
                     _showFilterDialog();
                   },
                   icon: Icons.filter_list,
                   text: ResponsiveUtils.isDesktop(context) ? '筛选' : '',
                 ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildStudentList() {
    return Consumer<StudentProvider>(
      builder: (context, studentProvider, child) {
        if (studentProvider.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (studentProvider.errorMessage != null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.error_outline,
                  size: 64.sp,
                  color: Colors.red,
                ),
                SizedBox(height: 16.h),
                ResponsiveText(
                   '加载失败: ${studentProvider.errorMessage}',
                   baseFontSize: 16,
                   color: Colors.red,
                 ),
                SizedBox(height: 16.h),
                ResponsiveButton(
                  onPressed: () {
                    AppLogger.info('StudentsPage: 用户点击重试按钮');
                    _loadData();
                  },
                  text: '重试',
                ),
              ],
            ),
          );
        }
        
        final filteredStudents = _filterStudents(studentProvider.students);
        
        if (filteredStudents.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.people_outline,
                  size: 64.sp,
                  color: Colors.grey,
                ),
                SizedBox(height: 16.h),
                ResponsiveText(
                  _searchQuery.isNotEmpty ? '没有找到符合条件的学生' : '暂无学生数据',
                  baseFontSize: 16,
                  color: Colors.grey,
                ),
                SizedBox(height: 16.h),
                ResponsiveButton(
                  onPressed: () {
                    AppLogger.debug('StudentsPage: 用户从空状态点击添加学生');
                    _navigateToAddStudent();
                  },
                  text: '添加学生',
                ),
              ],
            ),
          );
        }
        
        return ResponsiveGridView(
          children: filteredStudents.map((student) => _buildStudentCard(student)).toList(),
        );
      },
    );
  }
  
  Widget _buildStudentCard(Student student) {
    return ResponsiveCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 24.r,
                backgroundColor: AppTheme.primaryColor,
                child: ResponsiveText(
                  student.name.isNotEmpty ? student.name[0] : 'S',
                  baseFontSize: 18,
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(width: 12.w),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    ResponsiveText(
                      student.name,
                      baseFontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                    SizedBox(height: 4.h),
                    ResponsiveText(
                       '学号: ${student.studentNumber}',
                       baseFontSize: 12,
                       color: Colors.grey[600],
                     ),
                  ],
                ),
              ),
              PopupMenuButton<String>(
                onSelected: (value) => _handleMenuAction(value, student),
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'view',
                    child: ListTile(
                      leading: Icon(Icons.visibility),
                      title: Text('查看详情'),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                  const PopupMenuItem(
                    value: 'edit',
                    child: ListTile(
                      leading: Icon(Icons.edit),
                      title: Text('编辑'),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                  const PopupMenuItem(
                    value: 'delete',
                    child: ListTile(
                      leading: Icon(Icons.delete, color: Colors.red),
                      title: Text('删除', style: TextStyle(color: Colors.red)),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                ],
              ),
            ],
          ),
          SizedBox(height: 12.h),
          Row(
            children: [
              Icon(Icons.class_, size: 16.sp, color: Colors.grey[600]),
              SizedBox(width: 4.w),
              ResponsiveText(
                 '班级ID: ${student.classId}',
                 baseFontSize: 12,
                 color: Colors.grey[600],
               ),
              const Spacer(),
              Icon(Icons.phone, size: 16.sp, color: Colors.grey[600]),
              SizedBox(width: 4.w),
              ResponsiveText(
                student.phone ?? '无',
                baseFontSize: 12,
                color: Colors.grey[600],
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildClassDistribution() {
    return Consumer<StudentProvider>(
      builder: (context, studentProvider, child) {
        final classDistribution = _getClassDistribution(studentProvider.students);
        
        return SingleChildScrollView(
          padding: EdgeInsets.all(ResponsiveUtils.getGridSpacing(context)),
          child: ResponsiveGridView(
            children: classDistribution.entries.map((entry) {
              return ResponsiveCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.class_,
                          color: AppTheme.primaryColor,
                          size: 24.sp,
                        ),
                        SizedBox(width: 8.w),
                        Expanded(
                          child: ResponsiveText(
                            entry.key,
                            baseFontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 12.h),
                    ResponsiveText(
                      '学生人数: ${entry.value}',
                      baseFontSize: 14,
                      color: Colors.grey[600],
                    ),
                    SizedBox(height: 8.h),
                    LinearProgressIndicator(
                      value: entry.value / studentProvider.students.length,
                      backgroundColor: Colors.grey[300],
                      valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        );
      },
    );
  }
  
  Widget _buildStatistics() {
    return Consumer<StudentProvider>(
      builder: (context, studentProvider, child) {
        final stats = _calculateStatistics(studentProvider.students);
        
        return SingleChildScrollView(
          padding: EdgeInsets.all(ResponsiveUtils.getGridSpacing(context)),
          child: ResponsiveGridView(
            children: [
              _buildStatCard('总学生数', '${studentProvider.students.length}', Icons.people, AppTheme.primaryColor),
              _buildStatCard('班级数', '${stats['classCount']}', Icons.class_, Colors.green),
              _buildStatCard('男生', '${stats['maleCount']}', Icons.male, Colors.blue),
              _buildStatCard('女生', '${stats['femaleCount']}', Icons.female, Colors.pink),
              _buildStatCard('有联系方式', '${stats['hasPhoneCount']}', Icons.phone, Colors.orange),
              _buildStatCard('无联系方式', '${stats['noPhoneCount']}', Icons.phone_disabled, Colors.red),
            ],
          ),
        );
      },
    );
  }
  
  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return ResponsiveCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(
                icon,
                color: color,
                size: 24.sp,
              ),
              SizedBox(width: 8.w),
              Expanded(
                child: ResponsiveText(
                  title,
                  baseFontSize: 14,
                  color: Colors.black54,
                ),
              ),
            ],
          ),
          SizedBox(height: 8.h),
          ResponsiveText(
            value,
            baseFontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ],
      ),
    );
  }
  
  List<Student> _filterStudents(List<Student> students) {
    return students.where((student) {
      final matchesSearch = _searchQuery.isEmpty ||
           student.name.toLowerCase().contains(_searchQuery.toLowerCase()) ||
           student.studentNumber.toLowerCase().contains(_searchQuery.toLowerCase());
      
      final matchesClass = _selectedClassId == null ||
          student.classId == _selectedClassId;
      
      return matchesSearch && matchesClass;
    }).toList();
  }
  
  Map<String, int> _getClassDistribution(List<Student> students) {
    final distribution = <String, int>{};
    for (final student in students) {
       final className = '班级${student.classId}';
       distribution[className] = (distribution[className] ?? 0) + 1;
     }
    return distribution;
  }
  
  Map<String, int> _calculateStatistics(List<Student> students) {
    final classNames = students.map((s) => s.classId).toSet();
    final maleCount = students.where((s) => s.gender == 'male').length;
    final femaleCount = students.where((s) => s.gender == 'female').length;
    final hasPhoneCount = students.where((s) => s.phone != null && s.phone!.isNotEmpty).length;
    
    return {
      'classCount': classNames.length,
      'maleCount': maleCount,
      'femaleCount': femaleCount,
      'hasPhoneCount': hasPhoneCount,
      'noPhoneCount': students.length - hasPhoneCount,
    };
  }
  
  void _showFilterDialog() {
    AppLogger.debug('StudentsPage: 显示筛选对话框');
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('筛选条件'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // TODO: 添加班级筛选、性别筛选等
            const Text('筛选功能即将推出'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              AppLogger.debug('StudentsPage: 用户取消筛选');
              Navigator.of(context).pop();
            },
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              AppLogger.debug('StudentsPage: 用户确认筛选');
              Navigator.of(context).pop();
              // TODO: 应用筛选条件
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
  
  void _handleMenuAction(String action, Student student) {
    AppLogger.debug('StudentsPage: 用户选择菜单操作', {
      'action': action,
      'studentId': student.id,
      'studentName': student.name
    });
    
    switch (action) {
      case 'view':
        _navigateToStudentDetail(student);
        break;
      case 'edit':
        _navigateToEditStudent(student);
        break;
      case 'delete':
        _showDeleteConfirmation(student);
        break;
    }
  }
  
  void _navigateToAddStudent() {
    AppLogger.info('StudentsPage: 导航到添加学生页面');
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => const AddStudentPage(),
          ),
        )
        .then((_) {
          AppLogger.debug('StudentsPage: 从添加学生页面返回，重新加载数据');
          _loadData();
        });
  }
  
  void _navigateToStudentDetail(Student student) {
    AppLogger.info('StudentsPage: 导航到学生详情页面', {
      'studentId': student.id,
      'studentName': student.name
    });
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => StudentDetailPage(student: student),
      ),
    );
  }
  
  void _navigateToEditStudent(Student student) {
    AppLogger.info('StudentsPage: 导航到编辑学生页面', {
      'studentId': student.id,
      'studentName': student.name
    });
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => AddStudentPage(student: student),
          ),
        )
        .then((_) {
          AppLogger.debug('StudentsPage: 从编辑学生页面返回，重新加载数据');
          _loadData();
        });
  }
  
  void _showDeleteConfirmation(Student student) {
    AppLogger.warning('StudentsPage: 显示删除确认对话框', {
      'studentId': student.id,
      'studentName': student.name
    });
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除学生 "${student.name}" 吗？此操作不可撤销。'),
        actions: [
          TextButton(
            onPressed: () {
              AppLogger.debug('StudentsPage: 用户取消删除学生', {
                'studentId': student.id,
                'studentName': student.name
              });
              Navigator.of(context).pop();
            },
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              AppLogger.warning('StudentsPage: 用户确认删除学生', {
                'studentId': student.id,
                'studentName': student.name
              });
              Navigator.of(context).pop();
              _deleteStudent(student);
            },
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }
  
  Future<void> _deleteStudent(Student student) async {
    AppLogger.info('StudentsPage: 开始删除学生', {
      'studentId': student.id,
      'studentName': student.name
    });
    
    try {
      final studentProvider = Provider.of<StudentProvider>(context, listen: false);
      await studentProvider.deleteStudent(student.id);
      
      AppLogger.info('StudentsPage: 学生删除成功', {
        'studentId': student.id,
        'studentName': student.name
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('学生 "${student.name}" 已删除'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e, stackTrace) {
      AppLogger.error('StudentsPage: 学生删除失败', e, stackTrace);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('删除失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}