import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import '../../../../shared/themes/app_theme.dart';

class LessonDetailPage extends StatefulWidget {
  final String lessonId;
  
  const LessonDetailPage({
    Key? key,
    required this.lessonId,
  }) : super(key: key);

  @override
  State<LessonDetailPage> createState() => _LessonDetailPageState();
}

class _LessonDetailPageState extends State<LessonDetailPage> with TickerProviderStateMixin {
  late TabController _tabController;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('备课详情'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              _showEditDialog();
            },
          ),
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {
              _shareLesson();
            },
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'duplicate':
                  _duplicateLesson();
                  break;
                case 'export':
                  _exportLesson();
                  break;
                case 'delete':
                  _deleteLesson();
                  break;
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'duplicate',
                child: Row(
                  children: [
                    Icon(Icons.copy),
                    SizedBox(width: 8),
                    Text('复制备课'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'export',
                child: Row(
                  children: [
                    Icon(Icons.download),
                    SizedBox(width: 8),
                    Text('导出'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete, color: Colors.red),
                    SizedBox(width: 8),
                    Text('删除', style: TextStyle(color: Colors.red)),
                  ],
                ),
              ),
            ],
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          isScrollable: true,
          tabs: [
               Tab(text: '基本信息'),
               Tab(text: '教学设计'),
               Tab(text: '资源材料'),
               Tab(text: '反思总结'),
             ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildBasicInfoTab(),
          _buildTeachingDesignTab(),
          _buildResourcesTab(),
          _buildReflectionTab(),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          _startTeaching();
        },
        backgroundColor: AppTheme.successColor,
        icon: Icon(Icons.play_arrow, color: Colors.white),
         label: Text('开始上课', style: TextStyle(color: Colors.white)),
      ),
    );
  }

  Widget _buildBasicInfoTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 课程标题卡片
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12.r),
            ),
            child: Padding(
              padding: EdgeInsets.all(20.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 60.w,
                        height: 60.w,
                        decoration: BoxDecoration(
                          color: AppTheme.primaryColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12.r),
                        ),
                        child: Icon(
                          Icons.book,
                          color: AppTheme.primaryColor,
                          size: 30.sp,
                        ),
                      ),
                      SizedBox(width: 16.w),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '高一数学 - 函数的概念',
                              style: TextStyle(
                                fontSize: 20.sp,
                                fontWeight: FontWeight.bold,
                                color: AppTheme.textPrimaryColor,
                              ),
                            ),
                            SizedBox(height: 8.h),
                            Row(
                              children: [
                                Container(
                                  padding: EdgeInsets.symmetric(
                                    horizontal: 8.w,
                                    vertical: 4.h,
                                  ),
                                  decoration: BoxDecoration(
                                    color: AppTheme.successColor.withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(12.r),
                                  ),
                                  child: Text(
                                    '已完成',
                                    style: TextStyle(
                                      fontSize: 12.sp,
                                      color: AppTheme.successColor,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ),
                                SizedBox(width: 8.w),
                                Text(
                                  '2024-01-15',
                                  style: TextStyle(
                                    fontSize: 12.sp,
                                    color: AppTheme.textSecondaryColor,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 20.h),
          
          // 基本信息
          _buildInfoSection(
            '基本信息',
            [
              _buildInfoItem('授课班级', '高一(1)班'),
              _buildInfoItem('授课时间', '2024-01-15 08:00-08:45'),
              _buildInfoItem('课程类型', '新授课'),
              _buildInfoItem('课时安排', '第1课时/共2课时'),
              _buildInfoItem('教学目标', '理解函数的概念，掌握函数的表示方法'),
            ],
          ),
          SizedBox(height: 20.h),
          
          // 教学重难点
          _buildInfoSection(
            '教学重难点',
            [
              _buildInfoItem('教学重点', '函数概念的理解和应用'),
              _buildInfoItem('教学难点', '函数定义域和值域的确定'),
              _buildInfoItem('关键问题', '如何让学生理解函数的本质'),
            ],
          ),
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
          // 教学流程
          Text(
            '教学流程',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 16.h),
          
          _buildTeachingStep(
            1,
            '导入环节',
            '5分钟',
            '通过生活中的实例引入函数概念',
            AppTheme.primaryColor,
            [
              '展示温度变化图表',
              '提问：温度与时间的关系',
              '引导学生思考对应关系',
            ],
          ),
          
          _buildTeachingStep(
            2,
            '新课讲授',
            '25分钟',
            '系统讲解函数的定义和性质',
            AppTheme.infoColor,
            [
              '函数的定义',
              '函数的三要素',
              '函数的表示方法',
              '典型例题分析',
            ],
          ),
          
          _buildTeachingStep(
            3,
            '练习巩固',
            '10分钟',
            '通过练习加深理解',
            AppTheme.successColor,
            [
              '基础练习题',
              '小组讨论',
              '学生展示',
            ],
          ),
          
          _buildTeachingStep(
            4,
            '总结反思',
            '5分钟',
            '总结本节课重点内容',
            AppTheme.warningColor,
            [
              '知识点回顾',
              '学习方法总结',
              '布置作业',
            ],
          ),
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
          // 教学资源
          Text(
            '教学资源',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 16.h),
          
          // 课件资源
          _buildResourceSection(
            '课件资源',
            Icons.slideshow,
            AppTheme.primaryColor,
            [
              _buildResourceItem('函数概念.pptx', '2.5MB', Icons.slideshow),
              _buildResourceItem('函数图像.pdf', '1.8MB', Icons.picture_as_pdf),
            ],
          ),
          SizedBox(height: 16.h),
          
          // 视频资源
          _buildResourceSection(
            '视频资源',
            Icons.video_library,
            AppTheme.infoColor,
            [
              _buildResourceItem('函数概念讲解.mp4', '45.2MB', Icons.play_circle),
              _buildResourceItem('函数应用实例.mp4', '32.1MB', Icons.play_circle),
            ],
          ),
          SizedBox(height: 16.h),
          
          // 练习资源
          _buildResourceSection(
            '练习资源',
            Icons.quiz,
            AppTheme.successColor,
            [
              _buildResourceItem('课堂练习.docx', '0.8MB', Icons.description),
              _buildResourceItem('课后作业.pdf', '1.2MB', Icons.assignment),
            ],
          ),
          SizedBox(height: 20.h),
          
          // 添加资源按钮
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                _showAddResourceDialog();
              },
              icon: const Icon(Icons.add),
              label: const Text('添加资源'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                foregroundColor: Colors.white,
                padding: EdgeInsets.symmetric(vertical: 12.h),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.r),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReflectionTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 教学反思
          _buildReflectionSection(
            '教学效果',
            Icons.trending_up,
            AppTheme.successColor,
            '本节课学生参与度较高，对函数概念的理解基本到位。通过生活实例导入，学生能够较好地理解抽象概念。',
          ),
          SizedBox(height: 16.h),
          
          _buildReflectionSection(
            '存在问题',
            Icons.warning_amber,
            AppTheme.warningColor,
            '部分学生对函数定义域的理解还不够深入，需要在后续课程中加强练习。时间安排稍显紧张，练习环节可以适当延长。',
          ),
          SizedBox(height: 16.h),
          
          _buildReflectionSection(
            '改进建议',
            Icons.lightbulb,
            AppTheme.infoColor,
            '1. 增加更多生活实例帮助理解\n2. 设计更多层次的练习题\n3. 合理分配各环节时间\n4. 加强与学生的互动',
          ),
          SizedBox(height: 20.h),
          
          // 学生反馈
          Text(
            '学生反馈',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 16.h),
          
          _buildFeedbackCard('张三', '老师讲得很清楚，例子很生动', 5),
          SizedBox(height: 12.h),
          _buildFeedbackCard('李四', '函数概念理解了，但练习题有点难', 4),
          SizedBox(height: 12.h),
          _buildFeedbackCard('王五', '希望能有更多的练习时间', 4),
          
          SizedBox(height: 20.h),
          
          // 添加反思按钮
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                _showAddReflectionDialog();
              },
              icon: const Icon(Icons.add),
              label: const Text('添加反思'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                foregroundColor: Colors.white,
                padding: EdgeInsets.symmetric(vertical: 12.h),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.r),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoSection(String title, List<Widget> items) {
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
            Text(
              title,
              style: TextStyle(
                fontSize: 16.sp,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimaryColor,
              ),
            ),
            SizedBox(height: 12.h),
            ...items,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoItem(String label, String value) {
    return Padding(
      padding: EdgeInsets.only(bottom: 8.h),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80.w,
            child: Text(
              label,
              style: TextStyle(
                fontSize: 14.sp,
                color: AppTheme.textSecondaryColor,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                fontSize: 14.sp,
                color: AppTheme.textPrimaryColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTeachingStep(
    int step,
    String title,
    String duration,
    String description,
    Color color,
    List<String> activities,
  ) {
    return Container(
      margin: EdgeInsets.only(bottom: 20.h),
      child: Card(
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
                  Container(
                    width: 32.w,
                    height: 32.w,
                    decoration: BoxDecoration(
                      color: color,
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        step.toString(),
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 14.sp,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          style: TextStyle(
                            fontSize: 16.sp,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textPrimaryColor,
                          ),
                        ),
                        Text(
                          duration,
                          style: TextStyle(
                            fontSize: 12.sp,
                            color: color,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              SizedBox(height: 12.h),
              Text(
                description,
                style: TextStyle(
                  fontSize: 14.sp,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
              SizedBox(height: 12.h),
              ...activities.map((activity) => Padding(
                padding: EdgeInsets.only(bottom: 4.h),
                child: Row(
                  children: [
                    Icon(
                      Icons.circle,
                      size: 6.sp,
                      color: color,
                    ),
                    SizedBox(width: 8.w),
                    Text(
                      activity,
                      style: TextStyle(
                        fontSize: 13.sp,
                        color: AppTheme.textPrimaryColor,
                      ),
                    ),
                  ],
                ),
              )).toList(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResourceSection(
    String title,
    IconData icon,
    Color color,
    List<Widget> items,
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
            ...items,
          ],
        ),
      ),
    );
  }

  Widget _buildResourceItem(String name, String size, IconData icon) {
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
            color: AppTheme.primaryColor,
            size: 20.sp,
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w500,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                Text(
                  size,
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
              // 下载或预览资源
            },
            icon: Icon(
              Icons.download,
              color: AppTheme.textSecondaryColor,
              size: 18.sp,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReflectionSection(
    String title,
    IconData icon,
    Color color,
    String content,
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
            Text(
              content,
              style: TextStyle(
                fontSize: 14.sp,
                color: AppTheme.textPrimaryColor,
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeedbackCard(String studentName, String feedback, int rating) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(12.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 16.r,
                  backgroundColor: AppTheme.primaryColor,
                  child: Text(
                    studentName[0],
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14.sp,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                SizedBox(width: 8.w),
                Text(
                  studentName,
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w500,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const Spacer(),
                Row(
                  children: List.generate(5, (index) {
                    return Icon(
                      index < rating ? Icons.star : Icons.star_border,
                      color: AppTheme.warningColor,
                      size: 16.sp,
                    );
                  }),
                ),
              ],
            ),
            SizedBox(height: 8.h),
            Text(
              feedback,
              style: TextStyle(
                fontSize: 13.sp,
                color: AppTheme.textSecondaryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showEditDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('编辑备课'),
        content: const Text('编辑备课内容'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 编辑逻辑
            },
            child: const Text('保存'),
          ),
        ],
      ),
    );
  }

  void _shareLesson() {
    // 分享备课逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('分享功能开发中...')),
    );
  }

  void _duplicateLesson() {
    // 复制备课逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('备课已复制')),
    );
  }

  void _exportLesson() {
    // 导出备课逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('导出功能开发中...')),
    );
  }

  void _deleteLesson() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('删除备课'),
        content: const Text('确定要删除这个备课吗？此操作不可撤销。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              context.pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('备课已删除')),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }

  void _startTeaching() {
    // 开始上课逻辑
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('开始上课功能开发中...')),
    );
  }

  void _showAddResourceDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加资源'),
        content: const Text('选择要添加的资源类型'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 添加资源逻辑
            },
            child: const Text('选择文件'),
          ),
        ],
      ),
    );
  }

  void _showAddReflectionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加反思'),
        content: TextField(
          decoration: const InputDecoration(
            labelText: '教学反思',
            border: OutlineInputBorder(),
          ),
          maxLines: 5,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 添加反思逻辑
            },
            child: const Text('保存'),
          ),
        ],
      ),
    );
  }
}