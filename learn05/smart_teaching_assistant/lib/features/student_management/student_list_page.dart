import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/providers/student_provider.dart';
import '../../core/providers/class_provider.dart';
import '../../core/models/student_model.dart';
import 'student_detail_page.dart';
import 'add_student_page.dart';

class StudentListPage extends StatefulWidget {
  const StudentListPage({super.key});

  @override
  State<StudentListPage> createState() => _StudentListPageState();
}

class _StudentListPageState extends State<StudentListPage> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  String? _selectedClassId;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final studentProvider = Provider.of<StudentProvider>(context, listen: false);
    final classProvider = Provider.of<ClassProvider>(context, listen: false);
    
    await Future.wait([
      studentProvider.fetchStudents(),
      classProvider.fetchClasses(),
    ]);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('学生管理'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _navigateToAddStudent(),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _loadData(),
          ),
        ],
      ),
      body: Column(
        children: [
          _buildSearchAndFilter(),
          Expanded(
            child: _buildStudentList(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _navigateToAddStudent(),
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildSearchAndFilter() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // 搜索框
          TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: '搜索学生姓名、学号或邮箱',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _searchController.clear();
                        setState(() {
                          _searchQuery = '';
                        });
                      },
                    )
                  : null,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.0),
              ),
            ),
            onChanged: (value) {
              setState(() {
                _searchQuery = value;
              });
            },
          ),
          const SizedBox(height: 12),
          // 班级筛选
          Consumer<ClassProvider>(
            builder: (context, classProvider, child) {
              return DropdownButtonFormField<String?>(
                value: _selectedClassId,
                decoration: InputDecoration(
                  labelText: '筛选班级',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                ),
                items: [
                  const DropdownMenuItem<String?>(
                    value: null,
                    child: Text('全部班级'),
                  ),
                  ...classProvider.classes.map((schoolClass) {
                    return DropdownMenuItem<String?>(
                      value: schoolClass.id,
                      child: Text('${schoolClass.grade} - ${schoolClass.name}'),
                    );
                  }),
                ],
                onChanged: (value) {
                  setState(() {
                    _selectedClassId = value;
                  });
                  _filterStudents();
                },
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildStudentList() {
    return Consumer<StudentProvider>(
      builder: (context, studentProvider, child) {
        if (studentProvider.isLoading) {
          return const Center(
            child: CircularProgressIndicator(),
          );
        }

        if (studentProvider.errorMessage != null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.error_outline,
                  size: 64,
                  color: Theme.of(context).colorScheme.error,
                ),
                const SizedBox(height: 16),
                Text(
                  studentProvider.errorMessage!,
                  style: Theme.of(context).textTheme.bodyLarge,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => _loadData(),
                  child: const Text('重试'),
                ),
              ],
            ),
          );
        }

        final filteredStudents = _getFilteredStudents(studentProvider.students);

        if (filteredStudents.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.people_outline,
                  size: 64,
                  color: Theme.of(context).colorScheme.outline,
                ),
                const SizedBox(height: 16),
                Text(
                  _searchQuery.isNotEmpty || _selectedClassId != null
                      ? '没有找到符合条件的学生'
                      : '暂无学生数据',
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => _navigateToAddStudent(),
                  child: const Text('添加学生'),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: _loadData,
          child: ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: filteredStudents.length,
            itemBuilder: (context, index) {
              final student = filteredStudents[index];
              return _buildStudentCard(student);
            },
          ),
        );
      },
    );
  }

  Widget _buildStudentCard(Student student) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.primary,
          child: Text(
            student.name.isNotEmpty ? student.name[0].toUpperCase() : 'S',
            style: TextStyle(
              color: Theme.of(context).colorScheme.onPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          student.name,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('学号: ${student.studentNumber}'),
            // 邮箱字段暂未在模型中定义
            if (student.classId != null) _buildClassInfo(student.classId!),
          ],
        ),
        trailing: PopupMenuButton<String>(
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
        onTap: () => _navigateToStudentDetail(student),
      ),
    );
  }

  Widget _buildClassInfo(String classId) {
    return Consumer<ClassProvider>(
      builder: (context, classProvider, child) {
        final schoolClass = classProvider.classes
            .where((c) => c.id == classId)
            .isNotEmpty ? classProvider.classes.where((c) => c.id == classId).first : null;
        
        if (schoolClass != null) {
          return Text('班级: ${schoolClass.grade} - ${schoolClass.name}');
        }
        return Text('班级: $classId');
      },
    );
  }

  List<Student> _getFilteredStudents(List<Student> students) {
    var filtered = students;

    // 按班级筛选
    if (_selectedClassId != null) {
      filtered = filtered.where((s) => s.classId == _selectedClassId).toList();
    }

    // 按搜索关键词筛选
    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.toLowerCase();
      filtered = filtered.where((student) {
        return student.name.toLowerCase().contains(query) ||
               student.studentNumber.toLowerCase().contains(query);
      }).toList();
    }

    return filtered;
  }

  void _filterStudents() {
    final studentProvider = Provider.of<StudentProvider>(context, listen: false);
    studentProvider.fetchStudents(classId: _selectedClassId);
  }

  void _handleMenuAction(String action, Student student) {
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
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => const AddStudentPage(),
          ),
        )
        .then((_) => _loadData());
  }

  void _navigateToStudentDetail(Student student) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => StudentDetailPage(student: student),
      ),
    );
  }

  void _navigateToEditStudent(Student student) {
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => AddStudentPage(student: student),
          ),
        )
        .then((_) => _loadData());
  }

  void _showDeleteConfirmation(Student student) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除学生 "${student.name}" 吗？此操作不可撤销。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
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
    final studentProvider = Provider.of<StudentProvider>(context, listen: false);
    
    final success = await studentProvider.deleteStudent(student.id);
    
    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('学生 "${student.name}" 已删除'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(studentProvider.errorMessage ?? '删除失败'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}