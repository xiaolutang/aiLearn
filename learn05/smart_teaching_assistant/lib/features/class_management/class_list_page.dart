import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/providers/class_provider.dart';
import '../../core/models/class_model.dart';
import 'class_detail_page.dart';
import 'add_class_page.dart';

class ClassListPage extends StatefulWidget {
  const ClassListPage({super.key});

  @override
  State<ClassListPage> createState() => _ClassListPageState();
}

class _ClassListPageState extends State<ClassListPage> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  String? _selectedGrade;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final classProvider = Provider.of<ClassProvider>(context, listen: false);
    await classProvider.fetchClasses();
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
        title: const Text('班级管理'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _navigateToAddClass(),
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
            child: _buildClassList(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _navigateToAddClass(),
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
              hintText: '搜索班级名称或描述',
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
          // 年级筛选
          Consumer<ClassProvider>(
            builder: (context, classProvider, child) {
              final grades = classProvider.getGrades();
              return DropdownButtonFormField<String?>(
                value: _selectedGrade,
                decoration: InputDecoration(
                  labelText: '筛选年级',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                ),
                items: [
                  const DropdownMenuItem<String?>(
                    value: null,
                    child: Text('全部年级'),
                  ),
                  ...grades.map((grade) {
                    return DropdownMenuItem<String?>(
                      value: grade,
                      child: Text(grade),
                    );
                  }),
                ],
                onChanged: (value) {
                  setState(() {
                    _selectedGrade = value;
                  });
                },
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildClassList() {
    return Consumer<ClassProvider>(
      builder: (context, classProvider, child) {
        if (classProvider.isLoading) {
          return const Center(
            child: CircularProgressIndicator(),
          );
        }

        if (classProvider.error != null) {
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
                  classProvider.error!,
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

        final filteredClasses = _getFilteredClasses(classProvider.classes);

        if (filteredClasses.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.school_outlined,
                  size: 64,
                  color: Theme.of(context).colorScheme.outline,
                ),
                const SizedBox(height: 16),
                Text(
                  _searchQuery.isNotEmpty || _selectedGrade != null
                      ? '没有找到符合条件的班级'
                      : '暂无班级数据',
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => _navigateToAddClass(),
                  child: const Text('添加班级'),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: _loadData,
          child: ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: filteredClasses.length,
            itemBuilder: (context, index) {
              final schoolClass = filteredClasses[index];
              return _buildClassCard(schoolClass);
            },
          ),
        );
      },
    );
  }

  Widget _buildClassCard(SchoolClass schoolClass) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.primary,
          child: Text(
            schoolClass.name.isNotEmpty ? schoolClass.name[0].toUpperCase() : 'C',
            style: TextStyle(
              color: Theme.of(context).colorScheme.onPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          schoolClass.name,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('年级: ${schoolClass.grade}'),
            Text('学生人数: ${schoolClass.studentCount}人'),
            if (schoolClass.description != null && schoolClass.description!.isNotEmpty)
              Text(
                schoolClass.description!,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
          ],
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) => _handleMenuAction(value, schoolClass),
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
              value: 'students',
              child: ListTile(
                leading: Icon(Icons.people),
                title: Text('管理学生'),
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
        onTap: () => _navigateToClassDetail(schoolClass),
      ),
    );
  }

  List<SchoolClass> _getFilteredClasses(List<SchoolClass> classes) {
    var filtered = classes;

    // 按年级筛选
    if (_selectedGrade != null) {
      filtered = filtered.where((c) => c.grade == _selectedGrade).toList();
    }

    // 按搜索关键词筛选
    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.toLowerCase();
      filtered = filtered.where((schoolClass) {
        return schoolClass.name.toLowerCase().contains(query) ||
               schoolClass.grade.toLowerCase().contains(query) ||
               (schoolClass.description?.toLowerCase().contains(query) ?? false);
      }).toList();
    }

    return filtered;
  }

  void _handleMenuAction(String action, SchoolClass schoolClass) {
    switch (action) {
      case 'view':
        _navigateToClassDetail(schoolClass);
        break;
      case 'edit':
        _navigateToEditClass(schoolClass);
        break;
      case 'students':
        _navigateToClassStudents(schoolClass);
        break;
      case 'delete':
        _showDeleteConfirmation(schoolClass);
        break;
    }
  }

  void _navigateToAddClass() {
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => const AddClassPage(),
          ),
        )
        .then((_) => _loadData());
  }

  void _navigateToClassDetail(SchoolClass schoolClass) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ClassDetailPage(schoolClass: schoolClass),
      ),
    );
  }

  void _navigateToEditClass(SchoolClass schoolClass) {
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => AddClassPage(schoolClass: schoolClass),
          ),
        )
        .then((_) => _loadData());
  }

  void _navigateToClassStudents(SchoolClass schoolClass) {
    // TODO: 实现班级学生管理页面
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('班级学生管理功能即将推出'),
      ),
    );
  }

  void _showDeleteConfirmation(SchoolClass schoolClass) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除班级 "${schoolClass.name}" 吗？此操作不可撤销。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _deleteClass(schoolClass);
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

  Future<void> _deleteClass(SchoolClass schoolClass) async {
    final classProvider = Provider.of<ClassProvider>(context, listen: false);
    
    final success = await classProvider.deleteClass(schoolClass.id);
    
    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('班级 "${schoolClass.name}" 已删除'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(classProvider.error ?? '删除失败'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}