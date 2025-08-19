import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import '../../../../shared/themes/app_theme.dart';
import '../../../../routes/app_router.dart';
import '../../../../shared/widgets/layout/responsive_layout.dart';
import '../../../../shared/utils/responsive_utils.dart';
import 'responsive_dashboard_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _selectedIndex = 0;
  
  final List<Widget> _pages = [
    const DashboardPage(),
    const GradesOverviewPage(),
    const StudentsOverviewPage(),
    const ProfilePage(),
  ];

  final List<ResponsiveSidebarItem> _sidebarItems = [
    const ResponsiveSidebarItem(
      title: '首页',
      icon: Icons.dashboard_outlined,
    ),
    const ResponsiveSidebarItem(
      title: '成绩',
      icon: Icons.grade_outlined,
    ),
    const ResponsiveSidebarItem(
      title: '学生',
      icon: Icons.people_outlined,
    ),
    const ResponsiveSidebarItem(
      title: '我的',
      icon: Icons.person_outlined,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return ResponsiveLayout(
      appBar: ResponsiveAppBar(
        title: '智能教学助手',
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              // 通知功能
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () {
              context.go('/settings');
            },
          ),
        ],
      ),
      body: _pages[_selectedIndex],
      sidebar: ResponsiveUtils.shouldShowSidebar(context)
          ? ResponsiveSidebar(
              items: _sidebarItems,
              selectedIndex: _selectedIndex,
              onItemTap: (index) {
                setState(() {
                  _selectedIndex = index;
                });
              },
              header: Container(
                padding: ResponsiveUtils.getContentPadding(context),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircleAvatar(
                      radius: 30.r,
                      backgroundColor: AppTheme.primaryColor,
                      child: Icon(
                        Icons.school,
                        size: 30.w,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(height: 12.h),
                    ResponsiveText(
                      '智能教学助手',
                      baseFontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                    SizedBox(height: 4.h),
                    ResponsiveText(
                      '让教学更智能',
                      baseFontSize: 12,
                      color: AppTheme.textSecondaryColor,
                    ),
                  ],
                ),
              ),
            )
          : null,
      bottomNavigationBar: ResponsiveUtils.shouldUseBottomNavigation(context)
          ? ResponsiveBottomNavigationBar(
              currentIndex: _selectedIndex,
              onTap: (index) {
                setState(() {
                  _selectedIndex = index;
                });
              },
              selectedItemColor: AppTheme.primaryColor,
              unselectedItemColor: AppTheme.textSecondaryColor,
              items: const [
                BottomNavigationBarItem(
                  icon: Icon(Icons.dashboard_outlined),
                  activeIcon: Icon(Icons.dashboard),
                  label: '首页',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.grade_outlined),
                  activeIcon: Icon(Icons.grade),
                  label: '成绩',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.people_outlined),
                  activeIcon: Icon(Icons.people),
                  label: '学生',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.person_outlined),
                  activeIcon: Icon(Icons.person),
                  label: '我的',
                ),
              ],
            )
          : null,
    );
  }
}

// 仪表板页面
class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const ResponsiveDashboardPage();
  }


}

// 成绩概览页面
class GradesOverviewPage extends StatelessWidget {
  const GradesOverviewPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('成绩概览'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: const Center(
        child: Text('成绩概览页面'),
      ),
    );
  }
}

// 学生概览页面
class StudentsOverviewPage extends StatelessWidget {
  const StudentsOverviewPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('学生管理'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // 搜索功能
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(16.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 统计卡片
              Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      '学生总数',
                      '156',
                      Icons.people,
                      AppTheme.primaryColor,
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: _buildStatCard(
                      '班级数量',
                      '8',
                      Icons.class_,
                      AppTheme.infoColor,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 20.h),
              
              // 快捷操作
              Text(
                '快捷操作',
                style: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              SizedBox(height: 16.h),
              Row(
                children: [
                  Expanded(
                    child: _buildActionCard(
                      context,
                      '学生管理',
                      '查看和管理所有学生信息',
                      Icons.people_outline,
                      AppTheme.primaryColor,
                      () {
                        context.push(AppRouter.students);
                      },
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: _buildActionCard(
                      context,
                      '班级管理',
                      '查看和管理班级信息',
                      Icons.class_outlined,
                      AppTheme.infoColor,
                      () {
                        context.push(AppRouter.classes);
                      },
                    ),
                  ),
                ],
              ),
              SizedBox(height: 20.h),
              
              // 最近活动
              Text(
                '最近活动',
                style: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              SizedBox(height: 16.h),
              _buildRecentStudentActivity(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          children: [
            Icon(
              icon,
              size: 32.sp,
              color: color,
            ),
            SizedBox(height: 8.h),
            Text(
              value,
              style: TextStyle(
                fontSize: 24.sp,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimaryColor,
              ),
            ),
            SizedBox(height: 4.h),
            Text(
              title,
              style: TextStyle(
                fontSize: 12.sp,
                color: AppTheme.textSecondaryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard(
    BuildContext context,
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12.r),
        child: Padding(
          padding: EdgeInsets.all(16.w),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 48.w,
                height: 48.w,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12.r),
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 24.sp,
                ),
              ),
              SizedBox(height: 12.h),
              Text(
                title,
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textPrimaryColor,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              SizedBox(height: 4.h),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 12.sp,
                  color: AppTheme.textSecondaryColor,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecentStudentActivity() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          children: [
            _buildActivityItem(
              '新增学生：李明',
              '高一(3)班',
              '2小时前',
              Icons.person_add,
              AppTheme.successColor,
            ),
            Divider(height: 24.h),
            _buildActivityItem(
              '学生转班：王小红',
              '从高一(1)班转至高一(2)班',
              '1天前',
              Icons.swap_horiz,
              AppTheme.warningColor,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityItem(
    String title,
    String subtitle,
    String time,
    IconData icon,
    Color color,
  ) {
    return Row(
      children: [
        Container(
          width: 40.w,
          height: 40.w,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8.r),
          ),
          child: Icon(
            icon,
            color: color,
            size: 20.sp,
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
                  fontSize: 14.sp,
                  fontWeight: FontWeight.w500,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              SizedBox(height: 2.h),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 12.sp,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
            ],
          ),
        ),
        Text(
          time,
          style: TextStyle(
            fontSize: 11.sp,
            color: AppTheme.textSecondaryColor,
          ),
        ),
      ],
    );
  }
}

// 个人资料页面
class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return ResponsiveLayout(
      appBar: ResponsiveAppBar(
        title: '个人中心',
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: ResponsiveUtils.getResponsivePadding(context),
        child: Column(
          children: [
            // 用户信息卡片
            ResponsiveCard(
              child: Padding(
                padding: ResponsiveUtils.getResponsivePadding(context),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: ResponsiveUtils.getResponsiveValue(context: context, mobile: 30, tablet: 35, desktop: 40).toDouble(),
                      backgroundColor: AppTheme.primaryColor,
                      child: Icon(
                        Icons.person,
                        size: ResponsiveUtils.getResponsiveValue(context: context, mobile: 30, tablet: 35, desktop: 40).toDouble(),
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(width: 16.w),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          ResponsiveText(
                            '张老师',
                            baseFontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textPrimaryColor,
                          ),
                          SizedBox(height: 4.h),
                          ResponsiveText(
                            '数学教师',
                            baseFontSize: 14,
                            color: AppTheme.textSecondaryColor,
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.edit_outlined),
                      onPressed: () {
                        // 编辑个人信息
                      },
                    ),
                  ],
                ),
              ),
            ),
            SizedBox(height: 24.h),
            
            // 功能列表
            _buildMenuItem(
              context,
              '设置',
              Icons.settings_outlined,
              () {},
            ),
            _buildMenuItem(
              context,
              '帮助与反馈',
              Icons.help_outline,
              () {},
            ),
            _buildMenuItem(
              context,
              '关于我们',
              Icons.info_outline,
              () {},
            ),
            _buildMenuItem(
              context,
              '退出登录',
              Icons.logout,
              () {
                context.go(AppRouter.login);
              },
              isDestructive: true,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context,
    String title,
    IconData icon,
    VoidCallback onTap, {
    bool isDestructive = false,
  }) {
    return Card(
      elevation: 1,
      margin: EdgeInsets.only(bottom: 8.h),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8.r),
      ),
      child: ListTile(
        leading: Icon(
          icon,
          color: isDestructive ? AppTheme.errorColor : AppTheme.textSecondaryColor,
        ),
        title: Text(
          title,
          style: TextStyle(
            color: isDestructive ? AppTheme.errorColor : AppTheme.textPrimaryColor,
            fontWeight: FontWeight.w500,
          ),
        ),
        trailing: const Icon(
          Icons.chevron_right,
          color: AppTheme.textSecondaryColor,
        ),
        onTap: onTap,
      ),
    );
  }
}