import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/models/student_model.dart';
import '../../core/providers/student_provider.dart';
import '../../core/providers/class_provider.dart';
import '../../core/utils/app_logger.dart';

class AddStudentPage extends StatefulWidget {
  final Student? student; // 如果不为null，则为编辑模式

  const AddStudentPage({super.key, this.student});

  @override
  State<AddStudentPage> createState() => _AddStudentPageState();
}

class _AddStudentPageState extends State<AddStudentPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _studentIdController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  final _parentNameController = TextEditingController();
  final _parentPhoneController = TextEditingController();

  String _selectedGender = '男';
  String _selectedStatus = '在读';
  String? _selectedClassId;
  DateTime? _selectedDateOfBirth;
  bool _isLoading = false;

  bool get _isEditMode => widget.student != null;

  @override
  void initState() {
    super.initState();
    AppLogger.info('AddStudentPage: 页面初始化', {
      'isEditMode': _isEditMode,
      'studentId': widget.student?.id
    });
    _initializeForm();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadClasses();
    });
  }

  void _initializeForm() {
    if (_isEditMode) {
      final student = widget.student!;
      _nameController.text = student.name;
      _studentIdController.text = student.studentNumber;
      // 邮箱字段暂未在模型中定义
      _phoneController.text = student.phone ?? '';
      _addressController.text = student.address ?? '';
      // 家长姓名字段暂未在模型中定义
      _parentPhoneController.text = student.parentPhone ?? '';
      _selectedGender = student.gender ?? '男';
      // 状态字段暂未在模型中定义，使用默认值
      _selectedClassId = student.classId;
      _selectedDateOfBirth = student.birthDate;
    }
  }

  Future<void> _loadClasses() async {
    AppLogger.debug('AddStudentPage: 开始加载班级列表');
    try {
      final classProvider = Provider.of<ClassProvider>(context, listen: false);
      await classProvider.fetchClasses();
      AppLogger.info('AddStudentPage: 班级列表加载成功', {
        'classCount': classProvider.classes.length
      });
    } catch (e) {
      AppLogger.error('AddStudentPage: 班级列表加载失败', e);
    }
  }

  @override
  void dispose() {
    AppLogger.debug('AddStudentPage: 页面销毁，清理资源');
    _nameController.dispose();
    _studentIdController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    _parentNameController.dispose();
    _parentPhoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditMode ? '编辑学生' : '添加学生'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildBasicInfoSection(),
              const SizedBox(height: 24),
              _buildContactInfoSection(),
              const SizedBox(height: 24),
              _buildClassInfoSection(),
              const SizedBox(height: 24),
              _buildParentInfoSection(),
              const SizedBox(height: 32),
              _buildActionButtons(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBasicInfoSection() {
    return _buildSection(
      title: '基本信息',
      icon: Icons.person,
      children: [
        TextFormField(
          controller: _nameController,
          decoration: const InputDecoration(
            labelText: '姓名 *',
            border: OutlineInputBorder(),
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return '请输入学生姓名';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _studentIdController,
          decoration: const InputDecoration(
            labelText: '学号 *',
            border: OutlineInputBorder(),
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return '请输入学号';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _selectedGender,
                decoration: const InputDecoration(
                  labelText: '性别',
                  border: OutlineInputBorder(),
                ),
                items: ['男', '女'].map((gender) {
                  return DropdownMenuItem(
                    value: gender,
                    child: Text(gender),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedGender = value!;
                  });
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _selectedStatus,
                decoration: const InputDecoration(
                  labelText: '状态',
                  border: OutlineInputBorder(),
                ),
                items: ['在读', '休学', '毕业', '退学'].map((status) {
                  return DropdownMenuItem(
                    value: status,
                    child: Text(status),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedStatus = value!;
                  });
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        InkWell(
          onTap: () => _selectDateOfBirth(),
          child: InputDecorator(
            decoration: const InputDecoration(
              labelText: '出生日期',
              border: OutlineInputBorder(),
              suffixIcon: Icon(Icons.calendar_today),
            ),
            child: Text(
              _selectedDateOfBirth != null
                  ? '${_selectedDateOfBirth!.year}-${_selectedDateOfBirth!.month.toString().padLeft(2, '0')}-${_selectedDateOfBirth!.day.toString().padLeft(2, '0')}'
                  : '请选择出生日期',
              style: TextStyle(
                color: _selectedDateOfBirth != null
                    ? Theme.of(context).textTheme.bodyLarge?.color
                    : Theme.of(context).hintColor,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildContactInfoSection() {
    return _buildSection(
      title: '联系信息',
      icon: Icons.contact_phone,
      children: [
        TextFormField(
          controller: _emailController,
          decoration: const InputDecoration(
            labelText: '邮箱',
            border: OutlineInputBorder(),
          ),
          keyboardType: TextInputType.emailAddress,
          validator: (value) {
            if (value != null && value.isNotEmpty) {
              if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                return '请输入有效的邮箱地址';
              }
            }
            return null;
          },
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _phoneController,
          decoration: const InputDecoration(
            labelText: '电话',
            border: OutlineInputBorder(),
          ),
          keyboardType: TextInputType.phone,
          validator: (value) {
            if (value != null && value.isNotEmpty) {
              if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(value)) {
                return '请输入有效的手机号码';
              }
            }
            return null;
          },
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _addressController,
          decoration: const InputDecoration(
            labelText: '地址',
            border: OutlineInputBorder(),
          ),
          maxLines: 2,
        ),
      ],
    );
  }

  Widget _buildClassInfoSection() {
    return _buildSection(
      title: '班级信息',
      icon: Icons.school,
      children: [
        Consumer<ClassProvider>(
          builder: (context, classProvider, child) {
            if (classProvider.isLoading) {
              return const Center(
                child: CircularProgressIndicator(),
              );
            }

            return DropdownButtonFormField<String?>(
              value: _selectedClassId,
              decoration: const InputDecoration(
                labelText: '班级',
                border: OutlineInputBorder(),
              ),
              items: [
                const DropdownMenuItem<String?>(
                  value: null,
                  child: Text('暂不分配班级'),
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
              },
            );
          },
        ),
      ],
    );
  }

  Widget _buildParentInfoSection() {
    return _buildSection(
      title: '家长信息',
      icon: Icons.family_restroom,
      children: [
        TextFormField(
          controller: _parentNameController,
          decoration: const InputDecoration(
            labelText: '家长姓名',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _parentPhoneController,
          decoration: const InputDecoration(
            labelText: '家长电话',
            border: OutlineInputBorder(),
          ),
          keyboardType: TextInputType.phone,
          validator: (value) {
            if (value != null && value.isNotEmpty) {
              if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(value)) {
                return '请输入有效的手机号码';
              }
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildSection({
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

  Widget _buildActionButtons() {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton(
            onPressed: _isLoading ? null : () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: ElevatedButton(
            onPressed: _isLoading ? null : _saveStudent,
            child: Text(_isEditMode ? '更新' : '保存'),
          ),
        ),
      ],
    );
  }

  Future<void> _selectDateOfBirth() async {
    AppLogger.debug('AddStudentPage: 用户点击选择出生日期');
    final date = await showDatePicker(
      context: context,
      initialDate: _selectedDateOfBirth ?? DateTime.now().subtract(const Duration(days: 365 * 18)),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );

    if (date != null) {
      AppLogger.info('AddStudentPage: 用户选择了出生日期', {
        'selectedDate': date.toIso8601String()
      });
      setState(() {
        _selectedDateOfBirth = date;
      });
    } else {
      AppLogger.debug('AddStudentPage: 用户取消了出生日期选择');
    }
  }

  Future<void> _saveStudent() async {
    AppLogger.info('AddStudentPage: 用户点击保存学生', {
      'isEditMode': _isEditMode,
      'studentId': widget.student?.id
    });
    
    if (!_formKey.currentState!.validate()) {
      AppLogger.warning('AddStudentPage: 表单验证失败');
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final studentProvider = Provider.of<StudentProvider>(context, listen: false);
      
      final studentData = {
        'name': _nameController.text.trim(),
        'student_id': _studentIdController.text.trim(),
        'email': _emailController.text.trim(),
        'phone': _phoneController.text.trim(),
        'address': _addressController.text.trim(),
        'gender': _selectedGender,
        'status': _selectedStatus,
        'class_id': _selectedClassId,
        'date_of_birth': _selectedDateOfBirth?.toIso8601String(),
        'parent_name': _parentNameController.text.trim(),
        'parent_phone': _parentPhoneController.text.trim(),
      };

      AppLogger.debug('AddStudentPage: 准备提交学生数据', {
        'studentName': studentData['name'],
        'studentId': studentData['student_id'],
        'classId': studentData['class_id']
      });

      bool success;
      if (_isEditMode) {
        success = await studentProvider.updateStudent(
          widget.student!.id,
          studentData,
        );
      } else {
        success = await studentProvider.createStudent(studentData);
      }

      if (mounted) {
        if (success) {
          AppLogger.info('AddStudentPage: 学生保存成功', {
            'isEditMode': _isEditMode,
            'studentName': studentData['name']
          });
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(_isEditMode ? '学生信息更新成功' : '学生添加成功'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.of(context).pop(true);
        } else {
          AppLogger.error('AddStudentPage: 学生保存失败', {
            'errorMessage': studentProvider.errorMessage,
            'isEditMode': _isEditMode
          });
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(studentProvider.errorMessage ?? '操作失败'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      AppLogger.error('AddStudentPage: 学生保存异常', e);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('操作失败: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
}