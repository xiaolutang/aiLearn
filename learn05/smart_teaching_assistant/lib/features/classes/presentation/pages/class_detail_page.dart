import 'package:flutter/material.dart';

class ClassDetailPage extends StatefulWidget {
  final String classId;
  
  const ClassDetailPage({Key? key, required this.classId}) : super(key: key);

  @override
  State<ClassDetailPage> createState() => _ClassDetailPageState();
}

class _ClassDetailPageState extends State<ClassDetailPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('班级详情'),
        backgroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Text(
          '班级详情页面 - ID: ${widget.classId}',
          style: const TextStyle(fontSize: 18),
        ),
      ),
    );
  }
}