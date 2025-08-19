import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import '../../../../shared/themes/app_theme.dart';

class CreateLessonPage extends StatefulWidget {
  const CreateLessonPage({Key? key}) : super(key: key);

  @override
  State<CreateLessonPage> createState() => _CreateLessonPageState();
}

class _CreateLessonPageState extends State<CreateLessonPage> with TickerProviderStateMixin {
  late TabController _tabController;
  final _formKey = GlobalKey<FormState>();
  
  // 表单控制器
  final _titleController = TextEditingController();
  final _subjectController = TextEditingController();
  final _gradeController = TextEditingController();
  final _classController = TextEditingController();
  final _objectiveController = TextEditingController();
  final _keyPointsController = TextEditingController();
  final _difficultiesController = TextEditingController();
  
  String _selectedLessonType = '新授课';
  String _selectedDuration = '45分钟';
  DateTime _selectedDate = DateTime.now();
  TimeOfDay _selectedTime = TimeOfDay.now();
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    _titleController.dispose();
    _subjectController.dispose();
    _gradeController.dispose();
    _classController.dispose();
    _objectiveController.dispose();
    _keyPointsController.dispose();
    _difficultiesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('新建备课'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        actions: [
          TextButton(
            onPressed: () {
              _saveDraft();
            },
            child: Text(
              '保存草稿',
              style: TextStyle(color: Colors.white),
            ),
          ),
          SizedBox(width: 8.w),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: [
            Tab(text: '基本信息'),
            Tab(text: '教学设计'),
            Tab(text: '资源上传'),
          ],
        ),
      ),
      body: Form(
        key: _formKey,
        child: TabBarView(
          controller: _tabController,
          children: [
            _buildBasicInfoTab(),
            _buildTeachingDesignTab(),
            _buildResourcesTab(),
          ],
        ),
      ),
      bottomNavigationBar: Container(
        padding: EdgeInsets.all(16.w),
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 4,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () {
                  context.pop();
                },
                style: OutlinedButton.styleFrom(
                  padding: EdgeInsets.symmetric(vertical: 12.h),
                  side: BorderSide(color: AppTheme.primaryColor),
                ),
                child: Text(
                  '取消',
                  style: TextStyle(color: AppTheme.primaryColor),
                ),
              ),
            ),
            SizedBox(width: 16.w),
            Expanded(
              child: ElevatedButton(
                onPressed: () {
                  _createLesson();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(vertical: 12.h),
                ),
                child: const Text('创建备课'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBasicInfoTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 课程标题
          _buildSectionTitle('课程信息'),
          SizedBox(height: 16.h),
          
          TextFormField(
            controller: _titleController,
            decoration: InputDecoration(
              labelText: '课程标题 *',
              hintText: '请输入课程标题',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.r),
              ),
              prefixIcon: const Icon(Icons.title),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入课程标题';
              }
              return null;
            },
          ),
          SizedBox(height: 16.h),
          
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _subjectController,
                  decoration: InputDecoration(
                    labelText: '学科 *',
                    hintText: '如：数学',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    prefixIcon: const Icon(Icons.book),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return '请输入学科';
                    }
                    return null;
                  },
                ),
              ),
              SizedBox(width: 16.w),
              Expanded(
                child: TextFormField(
                  controller: _gradeController,
                  decoration: InputDecoration(
                    labelText: '年级 *',
                    hintText: '如：高一',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    prefixIcon: const Icon(Icons.school),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return '请输入年级';
                    }
                    return null;
                  },
                ),
              ),
            ],
          ),
          SizedBox(height: 16.h),
          
          TextFormField(
            controller: _classController,
            decoration: InputDecoration(
              labelText: '授课班级 *',
              hintText: '如：高一(1)班',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.r),
              ),
              prefixIcon: const Icon(Icons.group),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入授课班级';
              }
              return null;
            },
          ),
          SizedBox(height: 24.h),
          
          // 课程设置
          _buildSectionTitle('课程设置'),
          SizedBox(height: 16.h),
          
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedLessonType,
                  decoration: InputDecoration(
                    labelText: '课程类型',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    prefixIcon: const Icon(Icons.category),
                  ),
                  items: ['新授课', '复习课', '练习课', '实验课', '讲评课']
                      .map((type) => DropdownMenuItem(
                            value: type,
                            child: Text(type),
                          ))
                      .toList(),
                  onChanged: (value) {
                    setState(() {
                      _selectedLessonType = value!;
                    });
                  },
                ),
              ),
              SizedBox(width: 16.w),
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedDuration,
                  decoration: InputDecoration(
                    labelText: '课时时长',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    prefixIcon: const Icon(Icons.timer),
                  ),
                  items: ['40分钟', '45分钟', '50分钟', '90分钟']
                      .map((duration) => DropdownMenuItem(
                            value: duration,
                            child: Text(duration),
                          ))
                      .toList(),
                  onChanged: (value) {
                    setState(() {
                      _selectedDuration = value!;
                    });
                  },
                ),
              ),
            ],
          ),
          SizedBox(height: 16.h),
          
          Row(
            children: [
              Expanded(
                child: InkWell(
                  onTap: () => _selectDate(),
                  child: InputDecorator(
                    decoration: InputDecoration(
                      labelText: '授课日期',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8.r),
                      ),
                      prefixIcon: const Icon(Icons.calendar_today),
                    ),
                    child: Text(
                      '${_selectedDate.year}-${_selectedDate.month.toString().padLeft(2, '0')}-${_selectedDate.day.toString().padLeft(2, '0')}',
                    ),
                  ),
                ),
              ),
              SizedBox(width: 16.w),
              Expanded(
                child: InkWell(
                  onTap: () => _selectTime(),
                  child: InputDecorator(
                    decoration: InputDecoration(
                      labelText: '授课时间',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8.r),
                      ),
                      prefixIcon: const Icon(Icons.access_time),
                    ),
                    child: Text(
                      '${_selectedTime.hour.toString().padLeft(2, '0')}:${_selectedTime.minute.toString().padLeft(2, '0')}',
                    ),
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: 24.h),
          
          // AI助手建议
          _buildAISuggestionCard(),
        ],
      ),
    );
  }

  Widget _buildTeachingDesignTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 教学目标
          _buildSectionTitle('教学目标'),
          SizedBox(height: 16.h),
          
          TextFormField(
            controller: _objectiveController,
            decoration: InputDecoration(
              labelText: '教学目标 *',
              hintText: '请描述本节课的教学目标',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.r),
              ),
              prefixIcon: const Icon(Icons.flag),
            ),
            maxLines: 3,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入教学目标';
              }
              return null;
            },
          ),
          SizedBox(height: 24.h),
          
          // 教学重难点
          _buildSectionTitle('教学重难点'),
          SizedBox(height: 16.h),
          
          TextFormField(
            controller: _keyPointsController,
            decoration: InputDecoration(
              labelText: '教学重点 *',
              hintText: '请描述本节课的教学重点',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.r),
              ),
              prefixIcon: const Icon(Icons.star),
            ),
            maxLines: 3,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入教学重点';
              }
              return null;
            },
          ),
          SizedBox(height: 16.h),
          
          TextFormField(
            controller: _difficultiesController,
            decoration: InputDecoration(
              labelText: '教学难点 *',
              hintText: '请描述本节课的教学难点',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.r),
              ),
              prefixIcon: const Icon(Icons.warning),
            ),
            maxLines: 3,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入教学难点';
              }
              return null;
            },
          ),
          SizedBox(height: 24.h),
          
          // 教学流程设计
          _buildSectionTitle('教学流程设计'),
          SizedBox(height: 16.h),
          
          _buildTeachingStepDesigner(),
          SizedBox(height: 24.h),
          
          // AI教学建议
          _buildAITeachingSuggestion(),
        ],
      ),
    );
  }

  Widget _buildResourcesTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 课件资源
          _buildResourceUploadSection(
            '课件资源',
            Icons.slideshow,
            AppTheme.primaryColor,
            '支持 PPT、PDF 等格式',
          ),
          SizedBox(height: 20.h),
          
          // 视频资源
          _buildResourceUploadSection(
            '视频资源',
            Icons.video_library,
            AppTheme.infoColor,
            '支持 MP4、AVI 等格式',
          ),
          SizedBox(height: 20.h),
          
          // 练习资源
          _buildResourceUploadSection(
            '练习资源',
            Icons.quiz,
            AppTheme.successColor,
            '支持 DOC、PDF 等格式',
          ),
          SizedBox(height: 20.h),
          
          // 其他资源
          _buildResourceUploadSection(
            '其他资源',
            Icons.attach_file,
            AppTheme.warningColor,
            '支持各种文件格式',
          ),
          SizedBox(height: 24.h),
          
          // 资源库推荐
          _buildResourceLibraryCard(),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: TextStyle(
        fontSize: 18.sp,
        fontWeight: FontWeight.bold,
        color: AppTheme.textPrimaryColor,
      ),
    );
  }

  Widget _buildAISuggestionCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_awesome,
                  color: AppTheme.primaryColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  'AI智能建议',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12.h),
            Container(
              padding: EdgeInsets.all(12.w),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8.r),
              ),
              child: Text(
                '根据您输入的课程信息，AI建议：\n1. 可以通过生活实例导入新概念\n2. 建议安排15-20分钟的互动环节\n3. 准备3-5个层次递进的练习题',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: AppTheme.textPrimaryColor,
                  height: 1.5,
                ),
              ),
            ),
            SizedBox(height: 12.h),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  _getAISuggestions();
                },
                icon: const Icon(Icons.refresh),
                label: const Text('获取更多建议'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppTheme.primaryColor,
                  side: BorderSide(color: AppTheme.primaryColor),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTeachingStepDesigner() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.timeline,
                  color: AppTheme.primaryColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  '教学环节设计',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const Spacer(),
                TextButton.icon(
                  onPressed: () {
                    _addTeachingStep();
                  },
                  icon: const Icon(Icons.add),
                  label: const Text('添加环节'),
                ),
              ],
            ),
            SizedBox(height: 16.h),
            
            // 默认教学环节
            _buildStepItem('导入环节', '5分钟', '通过实例引入新知识', true),
            _buildStepItem('新课讲授', '25分钟', '系统讲解核心内容', true),
            _buildStepItem('练习巩固', '10分钟', '通过练习加深理解', true),
            _buildStepItem('总结反思', '5分钟', '总结重点，布置作业', true),
          ],
        ),
      ),
    );
  }

  Widget _buildStepItem(String title, String duration, String description, bool isDefault) {
    return Container(
      margin: EdgeInsets.only(bottom: 12.h),
      padding: EdgeInsets.all(12.w),
      decoration: BoxDecoration(
        color: AppTheme.backgroundColor,
        borderRadius: BorderRadius.circular(8.r),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Row(
        children: [
          Container(
            width: 8.w,
            height: 40.h,
            decoration: BoxDecoration(
              color: AppTheme.primaryColor,
              borderRadius: BorderRadius.circular(4.r),
            ),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 14.sp,
                        fontWeight: FontWeight.w500,
                        color: AppTheme.textPrimaryColor,
                      ),
                    ),
                    SizedBox(width: 8.w),
                    Container(
                      padding: EdgeInsets.symmetric(
                        horizontal: 6.w,
                        vertical: 2.h,
                      ),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10.r),
                      ),
                      child: Text(
                        duration,
                        style: TextStyle(
                          fontSize: 10.sp,
                          color: AppTheme.primaryColor,
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 4.h),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
              ],
            ),
          ),
          if (!isDefault)
            IconButton(
              onPressed: () {
                // 删除自定义环节
              },
              icon: Icon(
                Icons.delete_outline,
                color: AppTheme.errorColor,
                size: 18.sp,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildAITeachingSuggestion() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.lightbulb,
                  color: AppTheme.warningColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  'AI教学建议',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12.h),
            Text(
              '基于您的教学设计，AI为您推荐：',
              style: TextStyle(
                fontSize: 14.sp,
                color: AppTheme.textSecondaryColor,
              ),
            ),
            SizedBox(height: 8.h),
            _buildSuggestionItem('互动方式', '建议采用小组讨论的形式增加学生参与度'),
            _buildSuggestionItem('教学工具', '可以使用几何画板演示函数图像变化'),
            _buildSuggestionItem('练习设计', '从简单到复杂，设计3个层次的练习题'),
            SizedBox(height: 12.h),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  _generateAILesson();
                },
                icon: const Icon(Icons.auto_awesome),
                label: const Text('AI生成完整教案'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.warningColor,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionItem(String title, String content) {
    return Padding(
      padding: EdgeInsets.only(bottom: 8.h),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.circle,
            size: 6.sp,
            color: AppTheme.warningColor,
          ),
          SizedBox(width: 8.w),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: TextStyle(
                  fontSize: 13.sp,
                  color: AppTheme.textPrimaryColor,
                ),
                children: [
                  TextSpan(
                    text: '$title：',
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                  TextSpan(text: content),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResourceUploadSection(
    String title,
    IconData icon,
    Color color,
    String description,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  icon,
                  color: color,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12.h),
            Container(
              width: double.infinity,
              height: 100.h,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8.r),
                border: Border.all(
                  color: color.withOpacity(0.3),
                  style: BorderStyle.solid,
                ),
              ),
              child: InkWell(
                onTap: () {
                  _uploadResource(title);
                },
                borderRadius: BorderRadius.circular(8.r),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.cloud_upload,
                      color: color,
                      size: 32.sp,
                    ),
                    SizedBox(height: 8.h),
                    Text(
                      '点击上传文件',
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: color,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    SizedBox(height: 4.h),
                    Text(
                      description,
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: AppTheme.textSecondaryColor,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResourceLibraryCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.library_books,
                  color: AppTheme.infoColor,
                  size: 20.sp,
                ),
                SizedBox(width: 8.w),
                Text(
                  '资源库推荐',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12.h),
            Text(
              '根据您的课程内容，为您推荐以下资源：',
              style: TextStyle(
                fontSize: 14.sp,
                color: AppTheme.textSecondaryColor,
              ),
            ),
            SizedBox(height: 12.h),
            _buildResourceItem('函数概念教学课件', '优质PPT模板', Icons.slideshow),
            _buildResourceItem('函数图像动画演示', '交互式动画', Icons.animation),
            _buildResourceItem('函数练习题库', '分层练习题', Icons.quiz),
            SizedBox(height: 12.h),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  _browseResourceLibrary();
                },
                icon: const Icon(Icons.explore),
                label: const Text('浏览更多资源'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppTheme.infoColor,
                  side: BorderSide(color: AppTheme.infoColor),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResourceItem(String title, String description, IconData icon) {
    return Container(
      margin: EdgeInsets.only(bottom: 8.h),
      padding: EdgeInsets.all(12.w),
      decoration: BoxDecoration(
        color: AppTheme.backgroundColor,
        borderRadius: BorderRadius.circular(8.r),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: AppTheme.infoColor,
            size: 20.sp,
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w500,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: () {
              // 添加到备课
            },
            icon: Icon(
              Icons.add_circle_outline,
              color: AppTheme.infoColor,
              size: 18.sp,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
      });
    }
  }

  Future<void> _selectTime() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _selectedTime,
    );
    if (picked != null && picked != _selectedTime) {
      setState(() {
        _selectedTime = picked;
      });
    }
  }

  void _saveDraft() {
    // 保存草稿逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('草稿已保存')),
    );
  }

  void _createLesson() {
    if (_formKey.currentState!.validate()) {
      // 创建备课逻辑
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('备课创建成功')),
      );
      context.pop();
    } else {
      // 切换到第一个有错误的Tab
      _tabController.animateTo(0);
    }
  }

  void _getAISuggestions() {
    // 获取AI建议逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('正在获取AI建议...')),
    );
  }

  void _addTeachingStep() {
    // 添加教学环节逻辑
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加教学环节'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              decoration: const InputDecoration(
                labelText: '环节名称',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16.h),
            TextField(
              decoration: const InputDecoration(
                labelText: '时长（分钟）',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16.h),
            TextField(
              decoration: const InputDecoration(
                labelText: '环节描述',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 添加环节逻辑
            },
            child: const Text('添加'),
          ),
        ],
      ),
    );
  }

  void _generateAILesson() {
    // AI生成教案逻辑
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('AI生成教案'),
        content: const Text('AI将根据您输入的信息生成完整的教案，是否继续？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('AI正在生成教案，请稍候...')),
              );
            },
            child: const Text('生成'),
          ),
        ],
      ),
    );
  }

  void _uploadResource(String resourceType) {
    // 上传资源逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('正在上传$resourceType...')),
    );
  }

  void _browseResourceLibrary() {
    // 浏览资源库逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('正在打开资源库...')),
    );
  }
}