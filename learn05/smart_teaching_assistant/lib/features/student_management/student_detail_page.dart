import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/models/student_model.dart';
import '../../core/providers/class_provider.dart';
import 'add_student_page.dart';

class StudentDetailPage extends StatefulWidget {
  final Student student;

  const StudentDetailPage({
    super.key,
    required this.student,
  });

  @override
  State<StudentDetailPage> createState() => _StudentDetailPageState();
}

class _StudentDetailPageState extends State<StudentDetailPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadClassInfo();
    });
  }

  Future<void> _loadClassInfo() async {
    if (widget.student.classId != null) {
      final classProvider = Provider.of<ClassProvider>(context, listen: false);
      await classProvider.getClassById(widget.student.classId!);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.student.name),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () => _navigateToEdit(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStudentHeader(),
            const SizedBox(height: 24),
            _buildBasicInfo(),
            const SizedBox(height: 24),
            _buildContactInfo(),
            const SizedBox(height: 24),
            _buildClassInfo(),
            const SizedBox(height: 24),
            _buildAdditionalInfo(),
          ],
        ),
      ),
    );
  }

  Widget _buildStudentHeader() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            CircleAvatar(
              radius: 40,
              backgroundColor: Theme.of(context).colorScheme.primary,
              child: Text(
                widget.student.name.isNotEmpty 
                    ? widget.student.name[0].toUpperCase() 
                    : 'S',
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
                    widget.student.name,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '学号: ${widget.student.studentNumber}',
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
                      '在校',
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
      icon: Icons.person,
      children: [
        _buildInfoRow('姓名', widget.student.name),
        _buildInfoRow('学号', widget.student.studentNumber),
        _buildInfoRow('性别', widget.student.gender ?? '未知'),
        if (widget.student.birthDate != null)
          _buildInfoRow(
            '出生日期', 
            '${widget.student.birthDate!.year}-${widget.student.birthDate!.month.toString().padLeft(2, '0')}-${widget.student.birthDate!.day.toString().padLeft(2, '0')}',
          ),
        // 状态字段暂未在模型中定义
      ],
    );
  }

  Widget _buildContactInfo() {
    return _buildInfoSection(
      title: '联系信息',
      icon: Icons.contact_phone,
      children: [
        // 邮箱字段暂未在模型中定义
        if (widget.student.phone != null && widget.student.phone!.isNotEmpty)
          _buildInfoRow('电话', widget.student.phone!),
        if (widget.student.address != null && widget.student.address!.isNotEmpty)
          _buildInfoRow('地址', widget.student.address!),
        if (widget.student.parentPhone != null && widget.student.parentPhone!.isNotEmpty)
          _buildInfoRow('家长电话', widget.student.parentPhone!),
      ],
    );
  }

  Widget _buildClassInfo() {
    return Consumer<ClassProvider>(
      builder: (context, classProvider, child) {
        final schoolClass = widget.student.classId != null
            ? classProvider.classes
                .where((c) => c.id == widget.student.classId)
                .isNotEmpty
                ? classProvider.classes
                    .where((c) => c.id == widget.student.classId)
                    .first
                : null
            : null;

        return _buildInfoSection(
          title: '班级信息',
          icon: Icons.school,
          children: [
            if (schoolClass != null) ...[
              _buildInfoRow('班级', '${schoolClass.grade} - ${schoolClass.name}'),
              _buildInfoRow('年级', schoolClass.grade),
              if (schoolClass.description != null && schoolClass.description!.isNotEmpty)
                _buildInfoRow('班级描述', schoolClass.description!),
              _buildInfoRow('班级人数', '${schoolClass.studentCount}人'),
            ] else if (widget.student.classId != null) ...[
              _buildInfoRow('班级ID', widget.student.classId!),
            ] else ...[
              const Text(
                '暂未分配班级',
                style: TextStyle(
                  fontStyle: FontStyle.italic,
                  color: Colors.grey,
                ),
              ),
            ],
          ],
        );
      },
    );
  }

  Widget _buildAdditionalInfo() {
    return _buildInfoSection(
      title: '其他信息',
      icon: Icons.info,
      children: [
        _buildInfoRow(
          '创建时间',
          widget.student.createdAt != null
              ? '${widget.student.createdAt!.year}-${widget.student.createdAt!.month.toString().padLeft(2, '0')}-${widget.student.createdAt!.day.toString().padLeft(2, '0')} ${widget.student.createdAt!.hour.toString().padLeft(2, '0')}:${widget.student.createdAt!.minute.toString().padLeft(2, '0')}'
              : '未知',
        ),
        _buildInfoRow(
          '更新时间',
          widget.student.updatedAt != null
              ? '${widget.student.updatedAt!.year}-${widget.student.updatedAt!.month.toString().padLeft(2, '0')}-${widget.student.updatedAt!.day.toString().padLeft(2, '0')} ${widget.student.updatedAt!.hour.toString().padLeft(2, '0')}:${widget.student.updatedAt!.minute.toString().padLeft(2, '0')}'
              : '未知',
        ),
      ],
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

  void _navigateToEdit() {
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => AddStudentPage(student: widget.student),
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