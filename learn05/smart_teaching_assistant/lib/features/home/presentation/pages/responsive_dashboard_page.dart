import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../../../shared/themes/app_theme.dart';
import '../../../../shared/utils/responsive_utils.dart';
import '../../../../shared/widgets/layout/responsive_layout.dart';

/// 响应式工作台页面
/// 根据设备类型自动适配布局和交互方式
class ResponsiveDashboardPage extends StatelessWidget {
  const ResponsiveDashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      builder: (context, deviceType) {
        switch (deviceType) {
          case DeviceType.mobile:
            return _buildMobileLayout(context);
          case DeviceType.tablet:
            return _buildTabletLayout(context);
          case DeviceType.desktop:
            return _buildDesktopLayout(context);
        }
      },
    );
  }

  /// 移动端布局
  Widget _buildMobileLayout(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: SafeArea(
        child: Column(
          children: [
            // 移动端顶部导航栏
            _buildMobileTopNavigation(context),
            // 主要内容区域
            Expanded(
              child: SingleChildScrollView(
                padding: ResponsiveUtils.getContentPadding(context),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 欢迎区域
                    _buildWelcomeSection(context),
                    SizedBox(height: 24.h),
                    // 快速统计
                    _buildQuickStats(context),
                    SizedBox(height: 24.h),
                    // 功能卡片网格
                    _buildMobileFeatureGrid(context),
                    SizedBox(height: 24.h),
                    // 最近活动
                    _buildRecentActivity(context),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 平板布局
  Widget _buildTabletLayout(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: SafeArea(
        child: Column(
          children: [
            // 平板顶部导航栏
            _buildTabletTopNavigation(context),
            // 主要内容区域
            Expanded(
              child: SingleChildScrollView(
                padding: ResponsiveUtils.getContentPadding(context),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 欢迎区域
                    _buildWelcomeSection(context),
                    SizedBox(height: 32.h),
                    // 功能卡片网格
                    _buildTabletFeatureGrid(context),
                    SizedBox(height: 32.h),
                    // 最近活动
                    _buildRecentActivity(context),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 桌面端布局
  Widget _buildDesktopLayout(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: SafeArea(
        child: Column(
          children: [
            // 桌面端顶部导航栏
            _buildDesktopTopNavigation(context),
            // 主要内容区域
            Expanded(
              child: Center(
                child: Container(
                  constraints: BoxConstraints(
                    maxWidth: ResponsiveUtils.getMaxContentWidth(context),
                  ),
                  child: SingleChildScrollView(
                    padding: ResponsiveUtils.getContentPadding(context),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // 欢迎区域
                        _buildWelcomeSection(context),
                        SizedBox(height: 40.h),
                        // 桌面端双列布局
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // 左侧：功能卡片
                            Expanded(
                              flex: 2,
                              child: _buildDesktopFeatureGrid(context),
                            ),
                            SizedBox(width: 32.w),
                            // 右侧：最近活动
                            Expanded(
                              flex: 1,
                              child: _buildRecentActivity(context),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 移动端顶部导航栏
  Widget _buildMobileTopNavigation(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Logo和标题
          Row(
            children: [
              Container(
                width: 32.w,
                height: 32.w,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(8.r),
                ),
                child: Center(
                  child: Text(
                    '🎓',
                    style: TextStyle(fontSize: 18.sp),
                  ),
                ),
              ),
              SizedBox(width: 8.w),
              Text(
                '智能教学助手',
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF1E293B),
                ),
              ),
            ],
          ),
          const Spacer(),
          // 通知按钮
          Container(
            width: 36.w,
            height: 36.w,
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(18.r),
            ),
            child: IconButton(
              icon: Text(
                '🔔',
                style: TextStyle(fontSize: 16.sp),
              ),
              onPressed: () {},
            ),
          ),
          SizedBox(width: 8.w),
          // 用户头像
          Container(
            width: 36.w,
            height: 36.w,
            decoration: BoxDecoration(
              color: AppTheme.primaryColor,
              borderRadius: BorderRadius.circular(18.r),
            ),
            child: Center(
              child: Text(
                '张',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14.sp,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 平板顶部导航栏
  Widget _buildTabletTopNavigation(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 24.w, vertical: 16.h),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Logo和标题
          Row(
            children: [
              Container(
                width: 36.w,
                height: 36.w,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(10.r),
                ),
                child: Center(
                  child: Text(
                    '🎓',
                    style: TextStyle(fontSize: 20.sp),
                  ),
                ),
              ),
              SizedBox(width: 10.w),
              Text(
                '智能教学助手',
                style: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF1E293B),
                ),
              ),
            ],
          ),
          SizedBox(width: 24.w),
          // 导航菜单
          _buildNavMenu(context),
          const Spacer(),
          // 搜索框
          Flexible(
            child: Container(
              constraints: BoxConstraints(maxWidth: 280.w),
              height: 36.h,
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(18.r),
              ),
              child: TextField(
                decoration: InputDecoration(
                  hintText: '搜索课程、学生...',
                  hintStyle: TextStyle(
                    color: const Color(0xFF64748B),
                    fontSize: 13.sp,
                  ),
                  prefixIcon: Icon(
                    Icons.search,
                    color: const Color(0xFF64748B),
                    size: 18.sp,
                  ),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(vertical: 6.h),
                ),
              ),
            ),
          ),
          SizedBox(width: 12.w),
          // 通知按钮
          Container(
            width: 36.w,
            height: 36.w,
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(18.r),
            ),
            child: IconButton(
              icon: Text(
                '🔔',
                style: TextStyle(fontSize: 16.sp),
              ),
              onPressed: () {},
            ),
          ),
          SizedBox(width: 10.w),
          // 用户头像
          Container(
            width: 36.w,
            height: 36.w,
            decoration: BoxDecoration(
              color: AppTheme.primaryColor,
              borderRadius: BorderRadius.circular(18.r),
            ),
            child: Center(
              child: Text(
                '张',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14.sp,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 桌面端顶部导航栏
  Widget _buildDesktopTopNavigation(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 32.w, vertical: 16.h),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Logo和标题
          Row(
            children: [
              Container(
                width: 40.w,
                height: 40.w,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12.r),
                ),
                child: Center(
                  child: Text(
                    '🎓',
                    style: TextStyle(fontSize: 24.sp),
                  ),
                ),
              ),
              SizedBox(width: 12.w),
              Text(
                '智能教学助手',
                style: TextStyle(
                  fontSize: 20.sp,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF1E293B),
                ),
              ),
            ],
          ),
          SizedBox(width: 32.w),
          // 导航菜单
          _buildNavMenu(context),
          const Spacer(),
          // 搜索框
          Flexible(
            child: Container(
              constraints: BoxConstraints(maxWidth: 300.w),
              height: 40.h,
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(20.r),
              ),
              child: TextField(
                decoration: InputDecoration(
                  hintText: '搜索课程、学生...',
                  hintStyle: TextStyle(
                    color: const Color(0xFF64748B),
                    fontSize: 14.sp,
                  ),
                  prefixIcon: Icon(
                    Icons.search,
                    color: const Color(0xFF64748B),
                    size: 20.sp,
                  ),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(vertical: 8.h),
                ),
              ),
            ),
          ),
          SizedBox(width: 16.w),
          // 通知按钮
          Container(
            width: 40.w,
            height: 40.w,
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(20.r),
            ),
            child: IconButton(
              icon: Text(
                '🔔',
                style: TextStyle(fontSize: 18.sp),
              ),
              onPressed: () {},
            ),
          ),
          SizedBox(width: 12.w),
          // 用户头像
          Container(
            width: 40.w,
            height: 40.w,
            decoration: BoxDecoration(
              color: AppTheme.primaryColor,
              borderRadius: BorderRadius.circular(20.r),
            ),
            child: Center(
              child: Text(
                '张',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16.sp,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 导航菜单
  Widget _buildNavMenu(BuildContext context) {
    return Row(
      children: [
        _buildNavItem(context, '工作台', true),
        _buildNavItem(context, '备课', false),
        _buildNavItem(context, '上课', false),
        _buildNavItem(context, '成绩', false),
        _buildNavItem(context, '分析', false),
      ],
    );
  }

  /// 导航项
  Widget _buildNavItem(BuildContext context, String title, bool isActive) {
    final deviceType = ResponsiveUtils.getDeviceType(context);
    final fontSize = deviceType == DeviceType.desktop ? 14.sp : 13.sp;
    final padding = deviceType == DeviceType.desktop 
        ? EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h)
        : EdgeInsets.symmetric(horizontal: 12.w, vertical: 6.h);
    
    return Container(
      margin: EdgeInsets.only(right: deviceType == DeviceType.desktop ? 24.w : 16.w),
      padding: padding,
      decoration: BoxDecoration(
        color: isActive ? AppTheme.primaryColor.withOpacity(0.1) : Colors.transparent,
        borderRadius: BorderRadius.circular(8.r),
      ),
      child: Text(
        title,
        style: TextStyle(
          fontSize: fontSize,
          fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
          color: isActive ? AppTheme.primaryColor : const Color(0xFF64748B),
        ),
      ),
    );
  }

  /// 欢迎区域
  Widget _buildWelcomeSection(BuildContext context) {
    final deviceType = ResponsiveUtils.getDeviceType(context);
    final padding = ResponsiveUtils.getResponsiveValue(
      context: context,
      mobile: 20.w,
      tablet: 28.w,
      desktop: 32.w,
    );
    
    return Container(
      padding: EdgeInsets.all(padding),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(ResponsiveUtils.getBorderRadius(context)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '早上好，张老师！',
                      style: TextStyle(
                        fontSize: ResponsiveUtils.getResponsiveValue(
                          context: context,
                          mobile: 24.sp,
                          tablet: 28.sp,
                          desktop: 32.sp,
                        ),
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(height: 8.h),
                    Text(
                      '今天是美好的一天，让我们开始教学工作吧！',
                      style: TextStyle(
                        fontSize: ResponsiveUtils.getResponsiveValue(
                          context: context,
                          mobile: 14.sp,
                          tablet: 15.sp,
                          desktop: 16.sp,
                        ),
                        color: Colors.white.withOpacity(0.9),
                      ),
                    ),
                  ],
                ),
              ),
              if (deviceType != DeviceType.mobile) ...[
                Container(
                  width: ResponsiveUtils.getResponsiveValue(
                    context: context,
                    mobile: 60.w,
                    tablet: 70.w,
                    desktop: 80.w,
                  ),
                  height: ResponsiveUtils.getResponsiveValue(
                    context: context,
                    mobile: 60.w,
                    tablet: 70.w,
                    desktop: 80.w,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(
                      ResponsiveUtils.getResponsiveValue(
                        context: context,
                        mobile: 30.r,
                        tablet: 35.r,
                        desktop: 40.r,
                      ),
                    ),
                  ),
                  child: Center(
                    child: Text(
                      '👋',
                      style: TextStyle(
                        fontSize: ResponsiveUtils.getResponsiveValue(
                          context: context,
                          mobile: 30.sp,
                          tablet: 35.sp,
                          desktop: 40.sp,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ),
          if (deviceType != DeviceType.mobile) ...[
            SizedBox(height: 24.h),
            _buildQuickStats(context),
          ],
        ],
      ),
    );
  }

  /// 快速统计
  Widget _buildQuickStats(BuildContext context) {
    final deviceType = ResponsiveUtils.getDeviceType(context);
    
    if (deviceType == DeviceType.mobile) {
      // 移动端：2x2网格布局
      return Container(
        padding: EdgeInsets.all(16.w),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(ResponsiveUtils.getBorderRadius(context)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '快速统计',
              style: TextStyle(
                fontSize: 16.sp,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF1E293B),
              ),
            ),
            SizedBox(height: 16.h),
            Row(
              children: [
                Expanded(child: _buildQuickStat(context, '学生总数', '156', '👥')),
                SizedBox(width: 16.w),
                Expanded(child: _buildQuickStat(context, '班级数量', '6', '🏫')),
              ],
            ),
            SizedBox(height: 16.h),
            Row(
              children: [
                Expanded(child: _buildQuickStat(context, '本周作业', '24', '📝')),
                SizedBox(width: 16.w),
                Expanded(child: _buildQuickStat(context, '平均成绩', '85.6', '📊')),
              ],
            ),
          ],
        ),
      );
    } else {
      // 平板和桌面端：水平布局
      return Container(
        padding: EdgeInsets.all(20.w),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.15),
          borderRadius: BorderRadius.circular(12.r),
        ),
        child: Row(
          children: [
            Expanded(child: _buildQuickStat(context, '学生总数', '156', '👥')),
            Container(
              width: 1,
              height: 40.h,
              color: Colors.white.withOpacity(0.3),
            ),
            Expanded(child: _buildQuickStat(context, '班级数量', '6', '🏫')),
            Container(
              width: 1,
              height: 40.h,
              color: Colors.white.withOpacity(0.3),
            ),
            Expanded(child: _buildQuickStat(context, '本周作业', '24', '📝')),
            Container(
              width: 1,
              height: 40.h,
              color: Colors.white.withOpacity(0.3),
            ),
            Expanded(child: _buildQuickStat(context, '平均成绩', '85.6', '📊')),
          ],
        ),
      );
    }
  }

  /// 快速统计项
  Widget _buildQuickStat(BuildContext context, String label, String value, String emoji) {
    final deviceType = ResponsiveUtils.getDeviceType(context);
    final isInWelcomeSection = deviceType != DeviceType.mobile;
    
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: ResponsiveUtils.getResponsiveValue(
              context: context,
              mobile: 20.sp,
              tablet: 22.sp,
              desktop: 24.sp,
            ),
            fontWeight: FontWeight.bold,
            color: isInWelcomeSection ? Colors.white : const Color(0xFF1E293B),
          ),
        ),
        SizedBox(height: 4.h),
        Text(
          label,
          style: TextStyle(
            fontSize: ResponsiveUtils.getResponsiveValue(
              context: context,
              mobile: 12.sp,
              tablet: 13.sp,
              desktop: 14.sp,
            ),
            color: isInWelcomeSection 
                ? Colors.white.withOpacity(0.8) 
                : const Color(0xFF64748B),
          ),
        ),
      ],
    );
  }

  /// 移动端功能卡片网格
  Widget _buildMobileFeatureGrid(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '功能模块',
          style: TextStyle(
            fontSize: 18.sp,
            fontWeight: FontWeight.bold,
            color: const Color(0xFF1E293B),
          ),
        ),
        SizedBox(height: 16.h),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 12.w,
          mainAxisSpacing: 12.h,
          childAspectRatio: 1.0,
          children: _getFeatureCards(context),
        ),
      ],
    );
  }

  /// 平板功能卡片网格
  Widget _buildTabletFeatureGrid(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '功能模块',
          style: TextStyle(
            fontSize: 20.sp,
            fontWeight: FontWeight.bold,
            color: const Color(0xFF1E293B),
          ),
        ),
        SizedBox(height: 20.h),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 20.w,
          mainAxisSpacing: 20.h,
          childAspectRatio: 1.2,
          children: _getFeatureCards(context),
        ),
      ],
    );
  }

  /// 桌面端功能卡片网格
  Widget _buildDesktopFeatureGrid(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '功能模块',
          style: TextStyle(
            fontSize: 22.sp,
            fontWeight: FontWeight.bold,
            color: const Color(0xFF1E293B),
          ),
        ),
        SizedBox(height: 24.h),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 24.w,
          mainAxisSpacing: 24.h,
          childAspectRatio: 1.3,
          children: _getFeatureCards(context),
        ),
      ],
    );
  }

  /// 获取功能卡片列表
  List<Widget> _getFeatureCards(BuildContext context) {
    return [
      _buildFeatureCard(
        context: context,
        title: '智能备课',
        description: 'AI助力，轻松备课',
        emoji: '📚',
        gradient: const LinearGradient(
          colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        stats: '12个教案',
        onTap: () {},
      ),
      _buildFeatureCard(
        context: context,
        title: '互动教学',
        description: '课堂互动，提升效果',
        emoji: '🎯',
        gradient: const LinearGradient(
          colors: [Color(0xFF06B6D4), Color(0xFF3B82F6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        stats: '3节今日课程',
        onTap: () {},
      ),
      _buildFeatureCard(
        context: context,
        title: '成绩管理',
        description: '智能统计，一目了然',
        emoji: '📊',
        gradient: const LinearGradient(
          colors: [Color(0xFF10B981), Color(0xFF059669)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        stats: '8份待录入',
        onTap: () {},
      ),
      _buildFeatureCard(
        context: context,
        title: '学情分析',
        description: '数据驱动，精准教学',
        emoji: '📈',
        gradient: const LinearGradient(
          colors: [Color(0xFFF59E0B), Color(0xFFEF4444)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        stats: '5名需关注',
        onTap: () {},
      ),
    ];
  }

  /// 功能卡片
  Widget _buildFeatureCard({
    required BuildContext context,
    required String title,
    required String description,
    required String emoji,
    required LinearGradient gradient,
    required String stats,
    required VoidCallback onTap,
  }) {
    final deviceType = ResponsiveUtils.getDeviceType(context);
    final padding = ResponsiveUtils.getResponsiveValue(
      context: context,
      mobile: 16.w,
      tablet: 20.w,
      desktop: 24.w,
    );
    
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.all(padding),
        decoration: BoxDecoration(
          gradient: gradient,
          borderRadius: BorderRadius.circular(ResponsiveUtils.getBorderRadius(context)),
          boxShadow: [
            BoxShadow(
              color: gradient.colors.first.withOpacity(0.3),
              blurRadius: ResponsiveUtils.getResponsiveValue(
                context: context,
                mobile: 15,
                tablet: 18,
                desktop: 20,
              ),
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: ResponsiveUtils.getResponsiveValue(
                    context: context,
                    mobile: 40.w,
                    tablet: 44.w,
                    desktop: 48.w,
                  ),
                  height: ResponsiveUtils.getResponsiveValue(
                    context: context,
                    mobile: 40.w,
                    tablet: 44.w,
                    desktop: 48.w,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(
                      ResponsiveUtils.getResponsiveValue(
                        context: context,
                        mobile: 12.r,
                        tablet: 14.r,
                        desktop: 16.r,
                      ),
                    ),
                  ),
                  child: Center(
                    child: Text(
                      emoji,
                      style: TextStyle(
                        fontSize: ResponsiveUtils.getResponsiveValue(
                          context: context,
                          mobile: 20.sp,
                          tablet: 22.sp,
                          desktop: 24.sp,
                        ),
                      ),
                    ),
                  ),
                ),
                const Spacer(),
                Container(
                  width: ResponsiveUtils.getResponsiveValue(
                    context: context,
                    mobile: 28.w,
                    tablet: 30.w,
                    desktop: 32.w,
                  ),
                  height: ResponsiveUtils.getResponsiveValue(
                    context: context,
                    mobile: 28.w,
                    tablet: 30.w,
                    desktop: 32.w,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(
                      ResponsiveUtils.getResponsiveValue(
                        context: context,
                        mobile: 14.r,
                        tablet: 15.r,
                        desktop: 16.r,
                      ),
                    ),
                  ),
                  child: Icon(
                    Icons.arrow_forward_ios,
                    color: Colors.white,
                    size: ResponsiveUtils.getResponsiveValue(
                      context: context,
                      mobile: 12.sp,
                      tablet: 13.sp,
                      desktop: 14.sp,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: ResponsiveUtils.getResponsiveValue(
              context: context,
              mobile: 16.h,
              tablet: 18.h,
              desktop: 20.h,
            )),
            Text(
              title,
              style: TextStyle(
                fontSize: ResponsiveUtils.getResponsiveValue(
                  context: context,
                  mobile: 16.sp,
                  tablet: 17.sp,
                  desktop: 18.sp,
                ),
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 6.h),
            Text(
              description,
              style: TextStyle(
                fontSize: ResponsiveUtils.getResponsiveValue(
                  context: context,
                  mobile: 12.sp,
                  tablet: 13.sp,
                  desktop: 14.sp,
                ),
                color: Colors.white.withOpacity(0.8),
                height: 1.4,
              ),
            ),
            const Spacer(),
            Container(
              padding: EdgeInsets.symmetric(
                horizontal: ResponsiveUtils.getResponsiveValue(
                  context: context,
                  mobile: 10.w,
                  tablet: 11.w,
                  desktop: 12.w,
                ),
                vertical: ResponsiveUtils.getResponsiveValue(
                  context: context,
                  mobile: 4.h,
                  tablet: 5.h,
                  desktop: 6.h,
                ),
              ),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(20.r),
              ),
              child: Text(
                stats,
                style: TextStyle(
                  fontSize: ResponsiveUtils.getResponsiveValue(
                    context: context,
                    mobile: 11.sp,
                    tablet: 12.sp,
                    desktop: 12.sp,
                  ),
                  fontWeight: FontWeight.w500,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 最近活动
  Widget _buildRecentActivity(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '最近活动',
              style: TextStyle(
                fontSize: ResponsiveUtils.getResponsiveValue(
                  context: context,
                  mobile: 18.sp,
                  tablet: 20.sp,
                  desktop: 20.sp,
                ),
                fontWeight: FontWeight.bold,
                color: const Color(0xFF1E293B),
              ),
            ),
            TextButton(
              onPressed: () {},
              child: Text(
                '查看全部',
                style: TextStyle(
                  color: AppTheme.primaryColor,
                  fontSize: ResponsiveUtils.getResponsiveValue(
                    context: context,
                    mobile: 13.sp,
                    tablet: 14.sp,
                    desktop: 14.sp,
                  ),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
        SizedBox(height: 12.h),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(ResponsiveUtils.getBorderRadius(context)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 20,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            children: [
              _buildActivityItem(
                context: context,
                title: '录入学生成绩',
                description: '三年级2班数学测验成绩已录入完成',
                time: '2小时前',
                emoji: '📊',
                color: const Color(0xFF10B981),
              ),
              _buildActivityItem(
                context: context,
                title: '生成教学分析',
                description: '本周教学效果分析报告已生成',
                time: '4小时前',
                emoji: '📈',
                color: const Color(0xFF3B82F6),
              ),
              _buildActivityItem(
                context: context,
                title: '创建备课方案',
                description: '语文第五单元备课方案制作完成',
                time: '1天前',
                emoji: '📚',
                color: const Color(0xFF8B5CF6),
              ),
              _buildActivityItem(
                context: context,
                title: '学生作业批改',
                description: '三年级1班语文作业批改完成',
                time: '2天前',
                emoji: '✅',
                color: const Color(0xFFF59E0B),
                isLast: true,
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// 活动项
  Widget _buildActivityItem({
    required BuildContext context,
    required String title,
    required String description,
    required String time,
    required String emoji,
    required Color color,
    bool isLast = false,
  }) {
    final padding = ResponsiveUtils.getResponsiveValue(
      context: context,
      mobile: 12.w,
      tablet: 14.w,
      desktop: 16.w,
    );
    
    return Container(
      padding: EdgeInsets.all(padding),
      decoration: BoxDecoration(
        border: isLast ? null : Border(
          bottom: BorderSide(
            color: const Color(0xFFF1F5F9),
            width: 1,
          ),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: ResponsiveUtils.getResponsiveValue(
              context: context,
              mobile: 40.w,
              tablet: 44.w,
              desktop: 48.w,
            ),
            height: ResponsiveUtils.getResponsiveValue(
              context: context,
              mobile: 40.w,
              tablet: 44.w,
              desktop: 48.w,
            ),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(
                ResponsiveUtils.getResponsiveValue(
                  context: context,
                  mobile: 10.r,
                  tablet: 11.r,
                  desktop: 12.r,
                ),
              ),
            ),
            child: Center(
              child: Text(
                emoji,
                style: TextStyle(
                  fontSize: ResponsiveUtils.getResponsiveValue(
                    context: context,
                    mobile: 18.sp,
                    tablet: 19.sp,
                    desktop: 20.sp,
                  ),
                ),
              ),
            ),
          ),
          SizedBox(width: ResponsiveUtils.getResponsiveValue(
            context: context,
            mobile: 12.w,
            tablet: 14.w,
            desktop: 16.w,
          )),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: ResponsiveUtils.getResponsiveValue(
                      context: context,
                      mobile: 14.sp,
                      tablet: 15.sp,
                      desktop: 15.sp,
                    ),
                    fontWeight: FontWeight.w600,
                    color: const Color(0xFF1E293B),
                  ),
                ),
                SizedBox(height: 3.h),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: ResponsiveUtils.getResponsiveValue(
                      context: context,
                      mobile: 12.sp,
                      tablet: 13.sp,
                      desktop: 13.sp,
                    ),
                    color: const Color(0xFF64748B),
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(
              horizontal: ResponsiveUtils.getResponsiveValue(
                context: context,
                mobile: 6.w,
                tablet: 7.w,
                desktop: 8.w,
              ),
              vertical: ResponsiveUtils.getResponsiveValue(
                context: context,
                mobile: 3.h,
                tablet: 4.h,
                desktop: 4.h,
              ),
            ),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(6.r),
            ),
            child: Text(
              time,
              style: TextStyle(
                fontSize: ResponsiveUtils.getResponsiveValue(
                  context: context,
                  mobile: 10.sp,
                  tablet: 11.sp,
                  desktop: 11.sp,
                ),
                color: const Color(0xFF64748B),
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}