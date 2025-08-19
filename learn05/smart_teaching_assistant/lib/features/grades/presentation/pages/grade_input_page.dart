import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../core/providers/grade_provider.dart';
import '../../../../core/models/grade_model.dart';
import '../../../../shared/themes/app_theme.dart';
import '../../../../core/utils/app_logger.dart';

class GradeInputPage extends StatefulWidget {
  const GradeInputPage({Key? key}) : super(key: key);

  @override
  State<GradeInputPage> createState() => _GradeInputPageState();
}

class _GradeInputPageState extends State<GradeInputPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _formKey = GlobalKey<FormState>();
  
  // 单个录入表单字段
  String? _selectedExamId;
  String? _selectedSubjectId;
  String? _selectedStudentId;
  final _scoreController = TextEditingController();
  final _totalScoreController = TextEditingController();
  final _remarkController = TextEditingController();
  
  // 批量录入
  final List<StudentGradeInput> _batchGrades = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    AppLogger.info('GradeInputPage: 页面初始化');
    _tabController = TabController(length: 2, vsync: this);
    
    // 初始化数据
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadInitialData();
    });
  }

  @override
  void dispose() {
    AppLogger.debug('GradeInputPage: 页面销毁，清理资源');
    _tabController.dispose();
    _scoreController.dispose();
    _totalScoreController.dispose();
    _remarkController.dispose();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    AppLogger.info('GradeInputPage: 开始加载初始数据');
    final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
    
    try {
      await gradeProvider.loadGrades();
      AppLogger.info('GradeInputPage: 初始数据加载完成', {
        'examsCount': gradeProvider.availableExamIds.length,
        'subjectsCount': gradeProvider.availableSubjects.length
      });
    } catch (e, stackTrace) {
      AppLogger.error('GradeInputPage: 初始数据加载失败', e, stackTrace);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('录入成绩'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: '单个录入'),
            Tab(text: '批量录入'),
          ],
        ),
      ),
      body: Consumer<GradeProvider>(
        builder: (context, gradeProvider, child) {
          return TabBarView(
            controller: _tabController,
            children: [
              _buildSingleInput(gradeProvider),
              _buildBatchInput(gradeProvider),
            ],
          );
        },
      ),
    );
  }

  Widget _buildSingleInput(GradeProvider gradeProvider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '基本信息',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _selectedExamId,
              decoration: const InputDecoration(
                labelText: '选择考试',
                border: OutlineInputBorder(),
              ),
              items: gradeProvider.availableExamIds.map((examType) {
                 return DropdownMenuItem<String>(
                   value: examType,
                   child: Text(examType),
                 );
               }).toList(),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请选择考试';
                }
                return null;
              },
              onChanged: (value) {
                AppLogger.debug('GradeInputPage: 用户选择考试', {'examId': value});
                setState(() {
                  _selectedExamId = value;
                });
              },
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _selectedSubjectId,
              decoration: const InputDecoration(
                labelText: '选择科目',
                border: OutlineInputBorder(),
              ),
              items: gradeProvider.availableSubjects.map((subjectName) {
                 return DropdownMenuItem<String>(
                   value: subjectName,
                   child: Text(subjectName),
                 );
               }).toList(),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请选择科目';
                }
                return null;
              },
              onChanged: (value) {
                AppLogger.debug('GradeInputPage: 用户选择科目', {'subjectId': value});
                setState(() {
                  _selectedSubjectId = value;
                });
              },
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
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请选择学生';
                }
                return null;
              },
              onChanged: (value) {
                AppLogger.debug('GradeInputPage: 用户选择学生', {'studentId': value});
                setState(() {
                  _selectedStudentId = value;
                });
              },
            ),
            const SizedBox(height: 24),
            const Text(
              '成绩信息',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _scoreController,
                    decoration: const InputDecoration(
                      labelText: '得分',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.number,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入得分';
                      }
                      final score = double.tryParse(value);
                      if (score == null || score < 0) {
                        return '请输入有效的分数';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextFormField(
                    controller: _totalScoreController,
                    decoration: const InputDecoration(
                      labelText: '总分',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.number,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入总分';
                      }
                      final totalScore = double.tryParse(value);
                      if (totalScore == null || totalScore <= 0) {
                        return '请输入有效的总分';
                      }
                      final score = double.tryParse(_scoreController.text);
                      if (score != null && score > totalScore) {
                        return '得分不能大于总分';
                      }
                      return null;
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _remarkController,
              decoration: const InputDecoration(
                labelText: '备注（可选）',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _submitSingleGrade,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('提交成绩'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBatchInput(GradeProvider gradeProvider) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          color: AppTheme.backgroundColor,
          child: Row(
            children: [
              Expanded(
                child: Text(
                  '批量录入 (${_batchGrades.length}条)',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              ElevatedButton.icon(
                onPressed: _addBatchGrade,
                icon: const Icon(Icons.add),
                label: const Text('添加'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: _batchGrades.isEmpty
              ? const Center(
                  child: Text(
                    '点击添加按钮开始批量录入',
                    style: TextStyle(fontSize: 16),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _batchGrades.length,
                  itemBuilder: (context, index) {
                    final grade = _batchGrades[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        title: Text('学生: ${_getStudentName(grade.studentId)}'),
                        subtitle: Text(
                          '分数: ${grade.score}\n'
                          '备注: ${grade.remark ?? '无'}',
                        ),
                        trailing: IconButton(
                          onPressed: () => _removeBatchGrade(index),
                          icon: const Icon(Icons.delete, color: Colors.red),
                        ),
                        onTap: () => _editBatchGrade(index),
                      ),
                    );
                  },
                ),
        ),
        if (_batchGrades.isNotEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _submitBatchGrades,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text('提交全部成绩 (${_batchGrades.length}条)'),
              ),
            ),
          ),
      ],
    );
  }

  Future<void> _submitSingleGrade() async {
    AppLogger.info('GradeInputPage: 用户点击提交单个成绩');
    
    if (!_formKey.currentState!.validate()) {
      AppLogger.warning('GradeInputPage: 单个成绩表单验证失败');
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
      
      final gradeInput = GradeInputRequest(
        examId: _selectedExamId!,
        subjectId: _selectedSubjectId!,
        grades: [
          StudentGradeInput(
            studentId: _selectedStudentId!,
            score: double.parse(_scoreController.text),
            remark: _remarkController.text.isNotEmpty ? _remarkController.text : null,
          ),
        ],
      );

      AppLogger.info('GradeInputPage: 开始提交单个成绩', {
        'examId': _selectedExamId,
        'subjectId': _selectedSubjectId,
        'studentId': _selectedStudentId,
        'score': _scoreController.text,
        'hasRemark': _remarkController.text.isNotEmpty
      });

      // 批量创建成绩记录
        bool success = true;
        for (final gradeInput in _batchGrades) {
          final grade = Grade(
              id: '',
              studentId: gradeInput.studentId,
              studentName: '学生${gradeInput.studentId}',
              subjectId: _selectedSubjectId ?? '',
              subjectName: _selectedSubjectId ?? '未知科目',
              examId: _selectedExamId ?? '',
              examName: _selectedExamId ?? '未知考试',
              score: gradeInput.score,
              totalScore: 100.0,
              examDate: DateTime.now(),
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            );
          final result = await gradeProvider.createGrade(grade);
          if (!result) {
            success = false;
            break;
          }
        }
      
      if (success) {
        AppLogger.info('GradeInputPage: 单个成绩录入成功');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('成绩录入成功')),
        );
        _clearSingleForm();
      } else {
        AppLogger.warning('GradeInputPage: 单个成绩录入失败', {
          'error': gradeProvider.error
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(gradeProvider.error ?? '录入失败'),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    } catch (e, stackTrace) {
      AppLogger.error('GradeInputPage: 单个成绩录入异常', e, stackTrace);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('录入失败: $e'),
          backgroundColor: AppTheme.errorColor,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _submitBatchGrades() async {
    AppLogger.info('GradeInputPage: 用户点击提交批量成绩', {
      'gradesCount': _batchGrades.length
    });
    
    if (_batchGrades.isEmpty) {
      AppLogger.warning('GradeInputPage: 批量成绩列表为空，无法提交');
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
      
      final gradeInput = GradeInputRequest(
        examId: _selectedExamId ?? 'default_exam',
        subjectId: _selectedSubjectId ?? 'default_subject',
        grades: _batchGrades,
      );

      AppLogger.info('GradeInputPage: 开始提交批量成绩', {
        'examId': _selectedExamId ?? 'default_exam',
        'subjectId': _selectedSubjectId ?? 'default_subject',
        'gradesCount': _batchGrades.length
      });

      // 批量创建成绩记录
       bool success = true;
       for (final studentGrade in gradeInput.grades) {
         final grade = Grade(
            id: '',
            studentId: studentGrade.studentId,
            studentName: '学生${studentGrade.studentId}',
            subjectId: gradeInput.subjectId,
            subjectName: gradeInput.subjectId,
            examId: gradeInput.examId,
            examName: gradeInput.examId,
            score: studentGrade.score,
            totalScore: 100.0,
            examDate: DateTime.now(),
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          );
         final result = await gradeProvider.createGrade(grade);
         if (!result) {
           success = false;
           break;
         }
       }
      
      if (success) {
        AppLogger.info('GradeInputPage: 批量成绩录入成功', {
          'gradesCount': _batchGrades.length
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('批量录入成功 (${_batchGrades.length}条)')),
        );
        _clearBatchGrades();
      } else {
        AppLogger.warning('GradeInputPage: 批量成绩录入失败', {
          'error': gradeProvider.error,
          'gradesCount': _batchGrades.length
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(gradeProvider.error ?? '批量录入失败'),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    } catch (e, stackTrace) {
      AppLogger.error('GradeInputPage: 批量成绩录入异常', e, stackTrace);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('批量录入失败: $e'),
          backgroundColor: AppTheme.errorColor,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _addBatchGrade() {
    AppLogger.debug('GradeInputPage: 用户点击添加批量成绩');
    // TODO: 实现添加批量成绩对话框
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('批量添加功能开发中...')),
    );
  }

  void _editBatchGrade(int index) {
    AppLogger.debug('GradeInputPage: 用户点击编辑批量成绩', {'index': index});
    // TODO: 实现编辑批量成绩对话框
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('编辑功能开发中...')),
    );
  }

  void _removeBatchGrade(int index) {
    AppLogger.debug('GradeInputPage: 用户删除批量成绩项', {
      'index': index,
      'remainingCount': _batchGrades.length - 1
    });
    setState(() {
      _batchGrades.removeAt(index);
    });
  }

  void _clearSingleForm() {
    AppLogger.debug('GradeInputPage: 清空单个成绩表单');
    setState(() {
      _selectedExamId = null;
      _selectedSubjectId = null;
      _selectedStudentId = null;
    });
    _scoreController.clear();
    _totalScoreController.clear();
    _remarkController.clear();
  }

  void _clearBatchGrades() {
    AppLogger.debug('GradeInputPage: 清空批量成绩列表', {
      'clearedCount': _batchGrades.length
    });
    setState(() {
      _batchGrades.clear();
    });
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

  String _getSubjectName(String subjectId) {
    final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
    return gradeProvider.availableSubjects.firstWhere(
       (s) => s == subjectId,
       orElse: () => '未知科目',
     );
  }
}