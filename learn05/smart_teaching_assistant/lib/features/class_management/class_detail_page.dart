import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/models/class_model.dart';
import '../../core/providers/class_provider.dart';
import 'add_class_page.dart';

class ClassDetailPage extends StatefulWidget {
  final SchoolClass schoolClass;

  const ClassDetailPage({
    super.key,
    required this.schoolClass,
  });

  @override
  State<ClassDetailPage> createState() => _ClassDetailPageState();
}

class _ClassDetailPageState extends State<ClassDetailPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<Map<String, dynamic>> _students = [];
  bool _isLoadingStudents = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadClassStudents();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadClassStudents() async {
    setState(() {
      _isLoadingStudents = true;
    });

    try {
      final classProvider = Provider.of<ClassProvider>(context, listen: false);
      final students = await classProvider.getClassStudents(widget.schoolClass.id);
      setState(() {
        _students = students;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('加载学生列表失败: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isLoadingStudents = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.schoolClass.name),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () => _navigateToEdit(),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '班级信息', icon: Icon(Icons.info)),
            Tab(text: '学生列表', icon: Icon(Icons.people)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildClassInfoTab(),
          _buildStudentsTab(),
        ],
      ),
    );
  }

  Widget _buildClassInfoTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildClassHeader(),
          const SizedBox(height: 24),
          _buildBasicInfo(),
          const SizedBox(height: 24),
          _buildStatistics(),
          const SizedBox(height: 24),
          _buildAdditionalInfo(),
        ],
      ),
    );
  }

  Widget _buildClassHeader() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            CircleAvatar(
              radius: 40,
              backgroundColor: Theme.of(context).colorScheme.primary,
              child: Text(
                widget.schoolClass.name.isNotEmpty
                    ? widget.schoolClass.name[0].toUpperCase()
                    : 'C',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).colorScheme.onPrimary,
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.schoolClass.name,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '年级: ${widget.schoolClass.grade}',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${widget.schoolClass.studentCount}名学生',
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.onPrimaryContainer,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBasicInfo() {
    return _buildInfoSection(
      title: '基本信息',
      icon: Icons.info,
      children: [
        _buildInfoRow('班级名称', widget.schoolClass.name),
        _buildInfoRow('年级', widget.schoolClass.grade),
        _buildInfoRow('学生人数', '${widget.schoolClass.studentCount}人'),
        if (widget.schoolClass.description != null &&
            widget.schoolClass.description!.isNotEmpty)
          _buildInfoRow('班级描述', widget.schoolClass.description!),
      ],
    );
  }

  Widget _buildStatistics() {
    return _buildInfoSection(
      title: '统计信息',
      icon: Icons.analytics,
      children: [
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                title: '总人数',
                value: '${widget.schoolClass.studentCount}',
                icon: Icons.people,
                color: Colors.blue,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                title: '在读人数',
                value: '${_students.where((s) => s['status'] == '在读').length}',
                icon: Icons.school,
                color: Colors.green,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                title: '男生',
                value: '${_students.where((s) => s['gender'] == '男').length}',
                icon: Icons.male,
                color: Colors.orange,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                title: '女生',
                value: '${_students.where((s) => s['gender'] == '女').length}',
                icon: Icons.female,
                color: Colors.pink,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: color.withOpacity(0.8),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAdditionalInfo() {
    return _buildInfoSection(
      title: '其他信息',
      icon: Icons.more_horiz,
      children: [
        _buildInfoRow(
          '创建时间',
          '${widget.schoolClass.createdAt.year}-${widget.schoolClass.createdAt.month.toString().padLeft(2, '0')}-${widget.schoolClass.createdAt.day.toString().padLeft(2, '0')} ${widget.schoolClass.createdAt.hour.toString().padLeft(2, '0')}:${widget.schoolClass.createdAt.minute.toString().padLeft(2, '0')}',
        ),
        _buildInfoRow(
          '更新时间',
          '${widget.schoolClass.updatedAt.year}-${widget.schoolClass.updatedAt.month.toString().padLeft(2, '0')}-${widget.schoolClass.updatedAt.day.toString().padLeft(2, '0')} ${widget.schoolClass.updatedAt.hour.toString().padLeft(2, '0')}:${widget.schoolClass.updatedAt.minute.toString().padLeft(2, '0')}',
        ),
      ],
    );
  }

  Widget _buildStudentsTab() {
    if (_isLoadingStudents) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_students.isEmpty) {
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
              '该班级暂无学生',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => _addStudentToClass(),
              child: const Text('添加学生'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadClassStudents,
      child: ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemCount: _students.length,
        itemBuilder: (context, index) {
          final student = _students[index];
          return _buildStudentCard(student);
        },
      ),
    );
  }

  Widget _buildStudentCard(Map<String, dynamic> student) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.secondary,
          child: Text(
            student['name']?.isNotEmpty == true
                ? student['name'][0].toUpperCase()
                : 'S',
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSecondary,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          student['name'] ?? '未知',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('学号: ${student['student_id'] ?? '未知'}'),
            Text('性别: ${student['gender'] ?? '未知'}'),
            Text('状态: ${student['status'] ?? '未知'}'),
          ],
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) => _handleStudentAction(value, student),
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'remove',
              child: ListTile(
                leading: Icon(Icons.remove_circle, color: Colors.red),
                title: Text('移出班级', style: TextStyle(color: Colors.red)),
                contentPadding: EdgeInsets.zero,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoSection({
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  icon,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: TextStyle(
                fontWeight: FontWeight.w500,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  void _handleStudentAction(String action, Map<String, dynamic> student) {
    switch (action) {
      case 'remove':
        _showRemoveStudentConfirmation(student);
        break;
    }
  }

  void _showRemoveStudentConfirmation(Map<String, dynamic> student) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认移出'),
        content: Text('确定要将学生 "${student['name']}" 从班级中移出吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _removeStudentFromClass(student);
            },
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('移出'),
          ),
        ],
      ),
    );
  }

  Future<void> _removeStudentFromClass(Map<String, dynamic> student) async {
    final classProvider = Provider.of<ClassProvider>(context, listen: false);
    
    final success = await classProvider.removeStudentFromClass(
      widget.schoolClass.id,
      student['id'],
    );
    
    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('学生 "${student['name']}" 已从班级中移出'),
            backgroundColor: Colors.green,
          ),
        );
        _loadClassStudents(); // 重新加载学生列表
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(classProvider.error ?? '移出失败'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _addStudentToClass() {
    // TODO: 实现添加学生到班级的功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('添加学生功能即将推出'),
      ),
    );
  }

  void _navigateToEdit() {
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => AddClassPage(schoolClass: widget.schoolClass),
          ),
        )
        .then((result) {
          if (result == true) {
            // 如果编辑成功，返回上一页并刷新
            Navigator.of(context).pop(true);
          }
        });
  }
}