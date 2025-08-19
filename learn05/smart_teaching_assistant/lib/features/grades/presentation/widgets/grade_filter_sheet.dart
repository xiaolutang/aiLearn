import 'package:flutter/material.dart';
import '../../../../core/models/grade_model.dart';
import '../../../../shared/themes/app_theme.dart';

class GradeFilterSheet extends StatefulWidget {
  final Function(GradeQueryParams) onApplyFilter;

  const GradeFilterSheet({
    Key? key,
    required this.onApplyFilter,
  }) : super(key: key);

  @override
  State<GradeFilterSheet> createState() => _GradeFilterSheetState();
}

class _GradeFilterSheetState extends State<GradeFilterSheet> {
  String? _selectedExamId;
  String? _selectedSubjectId;
  String? _selectedClassId;
  String? _selectedStudentId;
  double? _minScore;
  double? _maxScore;
  DateTime? _startDate;
  DateTime? _endDate;
  String? _sortBy;
  String? _sortOrder;

  final List<String> _sortOptions = [
    'score',
    'scoreRate',
    'studentName',
    'examDate',
    'createdAt',
  ];

  final List<String> _sortOrderOptions = ['asc', 'desc'];

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 40,
            height: 4,
            margin: const EdgeInsets.only(top: 12),
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      '筛选条件',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    TextButton(
                      onPressed: _resetFilters,
                      child: Text(
                        '重置',
                        style: TextStyle(color: AppTheme.primaryColor),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                _buildFilterSection(
                  '考试',
                  DropdownButtonFormField<String>(
                    value: _selectedExamId,
                    decoration: const InputDecoration(
                      hintText: '选择考试',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(
                        value: 'exam1',
                        child: Text('期中考试'),
                      ),
                      DropdownMenuItem(
                        value: 'exam2',
                        child: Text('期末考试'),
                      ),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _selectedExamId = value;
                      });
                    },
                  ),
                ),
                const SizedBox(height: 16),
                _buildFilterSection(
                  '科目',
                  DropdownButtonFormField<String>(
                    value: _selectedSubjectId,
                    decoration: const InputDecoration(
                      hintText: '选择科目',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(
                        value: 'math',
                        child: Text('数学'),
                      ),
                      DropdownMenuItem(
                        value: 'chinese',
                        child: Text('语文'),
                      ),
                      DropdownMenuItem(
                        value: 'english',
                        child: Text('英语'),
                      ),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _selectedSubjectId = value;
                      });
                    },
                  ),
                ),
                const SizedBox(height: 16),
                _buildFilterSection(
                  '班级',
                  DropdownButtonFormField<String>(
                    value: _selectedClassId,
                    decoration: const InputDecoration(
                      hintText: '选择班级',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(
                        value: 'class1',
                        child: Text('一年级一班'),
                      ),
                      DropdownMenuItem(
                        value: 'class2',
                        child: Text('一年级二班'),
                      ),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _selectedClassId = value;
                      });
                    },
                  ),
                ),
                const SizedBox(height: 16),
                _buildFilterSection(
                  '分数范围',
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          decoration: const InputDecoration(
                            hintText: '最低分',
                            border: OutlineInputBorder(),
                          ),
                          keyboardType: TextInputType.number,
                          onChanged: (value) {
                            _minScore = double.tryParse(value);
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: TextFormField(
                          decoration: const InputDecoration(
                            hintText: '最高分',
                            border: OutlineInputBorder(),
                          ),
                          keyboardType: TextInputType.number,
                          onChanged: (value) {
                            _maxScore = double.tryParse(value);
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                _buildFilterSection(
                  '日期范围',
                  Row(
                    children: [
                      Expanded(
                        child: InkWell(
                          onTap: () => _selectDate(context, true),
                          child: Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              border: Border.all(color: Colors.grey),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              _startDate != null
                                  ? _formatDate(_startDate!)
                                  : '开始日期',
                              style: TextStyle(
                                color: _startDate != null
                                    ? Colors.black
                                    : Colors.grey[600],
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: InkWell(
                          onTap: () => _selectDate(context, false),
                          child: Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              border: Border.all(color: Colors.grey),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              _endDate != null
                                  ? _formatDate(_endDate!)
                                  : '结束日期',
                              style: TextStyle(
                                color: _endDate != null
                                    ? Colors.black
                                    : Colors.grey[600],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                _buildFilterSection(
                  '排序',
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _sortBy,
                          decoration: const InputDecoration(
                            hintText: '排序字段',
                            border: OutlineInputBorder(),
                          ),
                          items: _sortOptions.map((option) {
                            return DropdownMenuItem(
                              value: option,
                              child: Text(_getSortOptionLabel(option)),
                            );
                          }).toList(),
                          onChanged: (value) {
                            setState(() {
                              _sortBy = value;
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _sortOrder,
                          decoration: const InputDecoration(
                            hintText: '排序方式',
                            border: OutlineInputBorder(),
                          ),
                          items: _sortOrderOptions.map((option) {
                            return DropdownMenuItem(
                              value: option,
                              child: Text(option == 'asc' ? '升序' : '降序'),
                            );
                          }).toList(),
                          onChanged: (value) {
                            setState(() {
                              _sortOrder = value;
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('取消'),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: _applyFilters,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.primaryColor,
                          foregroundColor: Colors.white,
                        ),
                        child: const Text('应用筛选'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterSection(String title, Widget child) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        child,
      ],
    );
  }

  String _getSortOptionLabel(String option) {
    switch (option) {
      case 'score':
        return '分数';
      case 'scoreRate':
        return '得分率';
      case 'studentName':
        return '学生姓名';
      case 'examDate':
        return '考试日期';
      case 'createdAt':
        return '录入时间';
      default:
        return option;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }

  Future<void> _selectDate(BuildContext context, bool isStartDate) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() {
        if (isStartDate) {
          _startDate = picked;
        } else {
          _endDate = picked;
        }
      });
    }
  }

  void _resetFilters() {
    setState(() {
      _selectedExamId = null;
      _selectedSubjectId = null;
      _selectedClassId = null;
      _selectedStudentId = null;
      _minScore = null;
      _maxScore = null;
      _startDate = null;
      _endDate = null;
      _sortBy = null;
      _sortOrder = null;
    });
  }

  void _applyFilters() {
    final params = GradeQueryParams(
      examId: _selectedExamId,
      subjectId: _selectedSubjectId,
      classId: _selectedClassId,
      studentId: _selectedStudentId,
      startDate: _startDate,
      endDate: _endDate,
      sortBy: _sortBy,
      sortOrder: _sortOrder,
    );
    
    widget.onApplyFilter(params);
    Navigator.of(context).pop();
  }
}