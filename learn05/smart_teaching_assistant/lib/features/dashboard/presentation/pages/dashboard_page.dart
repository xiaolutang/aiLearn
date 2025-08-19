import 'package:flutter/material.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_text_styles.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../shared/widgets/custom_button.dart';

/// 仪表板页面
/// 
/// 应用的主页面，提供：
/// - 快速导航
/// - 数据概览
/// - 功能入口
/// - 用户信息
class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int _selectedIndex = 0;
  
  final List<DashboardItem> _dashboardItems = [
    DashboardItem(
      title: '成绩管理',
      subtitle: '录入和管理学生成绩',
      icon: Icons.grade,
      color: AppColors.primary,
      route: '/grades',
    ),
    DashboardItem(
      title: '数据分析',
      subtitle: '查看成绩统计和趋势',
      icon: Icons.analytics,
      color: AppColors.secondary,
      route: '/analytics',
    ),
    DashboardItem(
      title: 'AI辅导',
      subtitle: '智能学习建议和辅导',
      icon: Icons.psychology,
      color: AppColors.success,
      route: '/ai-tutoring',
    ),
    DashboardItem(
      title: '班级管理',
      subtitle: '管理班级和学生信息',
      icon: Icons.class_,
      color: AppColors.warning,
      route: '/classes',
    ),
    DashboardItem(
      title: '用户中心',
      subtitle: '个人信息和设置',
      icon: Icons.person,
      color: AppColors.info,
      route: '/profile',
    ),
    DashboardItem(
      title: '系统设置',
      subtitle: '应用配置和偏好设置',
      icon: Icons.settings,
      color: AppColors.textSecondary,
      route: '/settings',
    ),
  ];
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: _buildAppBar(),
      body: _buildBody(),
      bottomNavigationBar: _buildBottomNavigationBar(),
      floatingActionButton: _buildFloatingActionButton(),
    );
  }
  
  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: AppColors.primary,
      elevation: 0,
      title: Text(
        '智能教学助手',
        style: AppTextStyles.headlineMedium.copyWith(
          color: Colors.white,
          fontWeight: FontWeight.bold,
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.notifications_outlined, color: Colors.white),
          onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('通知功能开发中')),
            );
          },
        ),
        IconButton(
          icon: const Icon(Icons.search, color: Colors.white),
          onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('搜索功能开发中')),
            );
          },
        ),
        const SizedBox(width: AppDimensions.spacingSmall),
      ],
    );
  }
  
  Widget _buildBody() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppDimensions.paddingMedium),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildWelcomeCard(),
          const SizedBox(height: AppDimensions.spacingLarge),
          _buildQuickStats(),
          const SizedBox(height: AppDimensions.spacingLarge),
          _buildFunctionGrid(),
          const SizedBox(height: AppDimensions.spacingLarge),
          _buildRecentActivity(),
        ],
      ),
    );
  }
  
  Widget _buildWelcomeCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppDimensions.paddingLarge),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppColors.primary, AppColors.primary.withOpacity(0.8)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppDimensions.radiusLarge),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow,
            offset: const Offset(0, 4),
            blurRadius: AppDimensions.blurRadiusMedium,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '欢迎回来！',
            style: AppTextStyles.headlineLarge.copyWith(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: AppDimensions.spacingSmall),
          Text(
            '今天是美好的一天，让我们开始教学工作吧！',
            style: AppTextStyles.bodyLarge.copyWith(
              color: Colors.white.withOpacity(0.9),
            ),
          ),
          const SizedBox(height: AppDimensions.spacingMedium),
          Row(
            children: [
              Icon(
                Icons.wb_sunny,
                color: Colors.white.withOpacity(0.9),
                size: AppDimensions.iconSizeSmall,
              ),
              const SizedBox(width: AppDimensions.spacingTiny),
              Text(
                '${DateTime.now().year}年${DateTime.now().month}月${DateTime.now().day}日',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: Colors.white.withOpacity(0.8),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildQuickStats() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            title: '学生总数',
            value: '156',
            icon: Icons.people,
            color: AppColors.primary,
          ),
        ),
        const SizedBox(width: AppDimensions.spacingMedium),
        Expanded(
          child: _buildStatCard(
            title: '班级数量',
            value: '8',
            icon: Icons.class_,
            color: AppColors.secondary,
          ),
        ),
        const SizedBox(width: AppDimensions.spacingMedium),
        Expanded(
          child: _buildStatCard(
            title: '平均分',
            value: '85.6',
            icon: Icons.trending_up,
            color: AppColors.success,
          ),
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
      padding: const EdgeInsets.all(AppDimensions.paddingMedium),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMedium),
        border: Border.all(color: AppColors.outline),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow,
            offset: const Offset(0, 2),
            blurRadius: AppDimensions.blurRadiusSmall,
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(
            icon,
            color: color,
            size: AppDimensions.iconSizeLarge,
          ),
          const SizedBox(height: AppDimensions.spacingSmall),
          Text(
            value,
            style: AppTextStyles.headlineMedium.copyWith(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: AppDimensions.spacingTiny),
          Text(
            title,
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
  
  Widget _buildFunctionGrid() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '功能模块',
          style: AppTextStyles.headlineMedium.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: AppDimensions.spacingMedium),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: AppDimensions.spacingMedium,
            mainAxisSpacing: AppDimensions.spacingMedium,
            childAspectRatio: 1.2,
          ),
          itemCount: _dashboardItems.length,
          itemBuilder: (context, index) {
            return _buildFunctionCard(_dashboardItems[index]);
          },
        ),
      ],
    );
  }
  
  Widget _buildFunctionCard(DashboardItem item) {
    return GestureDetector(
      onTap: () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${item.title}功能开发中')),
        );
      },
      child: Container(
        padding: const EdgeInsets.all(AppDimensions.paddingMedium),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMedium),
          border: Border.all(color: AppColors.outline),
          boxShadow: [
            BoxShadow(
              color: AppColors.shadow,
              offset: const Offset(0, 2),
              blurRadius: AppDimensions.blurRadiusSmall,
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: item.color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(AppDimensions.radiusSmall),
              ),
              child: Icon(
                item.icon,
                color: item.color,
                size: AppDimensions.iconSizeMedium,
              ),
            ),
            const SizedBox(height: AppDimensions.spacingSmall),
            Text(
              item.title,
              style: AppTextStyles.bodyLarge.copyWith(
                color: AppColors.textPrimary,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppDimensions.spacingTiny),
            Text(
              item.subtitle,
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildRecentActivity() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '最近活动',
              style: AppTextStyles.headlineMedium.copyWith(
                color: AppColors.textPrimary,
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('查看全部功能开发中')),
                );
              },
              child: Text(
                '查看全部',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.primary,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: AppDimensions.spacingMedium),
        Container(
          padding: const EdgeInsets.all(AppDimensions.paddingMedium),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(AppDimensions.radiusMedium),
            border: Border.all(color: AppColors.outline),
          ),
          child: Column(
            children: [
              _buildActivityItem(
                icon: Icons.grade,
                title: '录入了高一(1)班数学成绩',
                time: '2小时前',
                color: AppColors.primary,
              ),
              const Divider(),
              _buildActivityItem(
                icon: Icons.analytics,
                title: '生成了月度成绩分析报告',
                time: '1天前',
                color: AppColors.secondary,
              ),
              const Divider(),
              _buildActivityItem(
                icon: Icons.psychology,
                title: 'AI为张三同学生成学习建议',
                time: '2天前',
                color: AppColors.success,
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildActivityItem({
    required IconData icon,
    required String title,
    required String time,
    required Color color,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppDimensions.spacingSmall),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(AppDimensions.radiusSmall),
            ),
            child: Icon(
              icon,
              color: color,
              size: AppDimensions.iconSizeSmall,
            ),
          ),
          const SizedBox(width: AppDimensions.spacingMedium),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: AppDimensions.spacingTiny),
                Text(
                  time,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildBottomNavigationBar() {
    return BottomNavigationBar(
      currentIndex: _selectedIndex,
      onTap: (index) {
        setState(() {
          _selectedIndex = index;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('导航到${_getNavTitle(index)}')),
        );
      },
      type: BottomNavigationBarType.fixed,
      backgroundColor: AppColors.surface,
      selectedItemColor: AppColors.primary,
      unselectedItemColor: AppColors.textSecondary,
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.dashboard),
          label: '首页',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.grade),
          label: '成绩',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.analytics),
          label: '分析',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person),
          label: '我的',
        ),
      ],
    );
  }
  
  Widget _buildFloatingActionButton() {
    return FloatingActionButton(
      onPressed: () {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('快速添加功能开发中')),
        );
      },
      backgroundColor: AppColors.primary,
      child: const Icon(Icons.add, color: Colors.white),
    );
  }
  
  String _getNavTitle(int index) {
    switch (index) {
      case 0:
        return '首页';
      case 1:
        return '成绩管理';
      case 2:
        return '数据分析';
      case 3:
        return '个人中心';
      default:
        return '未知';
    }
  }
}

/// 仪表板项目数据模型
class DashboardItem {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  final String route;
  
  const DashboardItem({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.route,
  });
}