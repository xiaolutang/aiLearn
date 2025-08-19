import 'package:flutter/material.dart';
import '../../../../shared/themes/app_theme.dart';

class StudentDetailPage extends StatelessWidget {
  final String studentId;
  
  const StudentDetailPage({super.key, required this.studentId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('学生详情'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Text(
          '学生详情页面 - ID: $studentId',
          style: const TextStyle(fontSize: 18),
        ),
      ),
    );
  }
}