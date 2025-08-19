import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

/// 响应式设计工具类
/// 提供跨平台适配和响应式布局功能
class ResponsiveUtils {
  /// 屏幕断点定义
  static const double mobileBreakpoint = 600;
  static const double tabletBreakpoint = 1024;
  static const double desktopBreakpoint = 1440;

  /// 获取当前设备类型
  static DeviceType getDeviceType(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    
    if (width < mobileBreakpoint) {
      return DeviceType.mobile;
    } else if (width < tabletBreakpoint) {
      return DeviceType.tablet;
    } else {
      return DeviceType.desktop;
    }
  }

  /// 判断是否为移动设备
  static bool isMobile(BuildContext context) {
    return getDeviceType(context) == DeviceType.mobile;
  }

  /// 判断是否为平板设备
  static bool isTablet(BuildContext context) {
    return getDeviceType(context) == DeviceType.tablet;
  }

  /// 判断是否为桌面设备
  static bool isDesktop(BuildContext context) {
    return getDeviceType(context) == DeviceType.desktop;
  }

  /// 获取响应式值
  static T getResponsiveValue<T>({
    required BuildContext context,
    required T mobile,
    T? tablet,
    T? desktop,
  }) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return mobile;
      case DeviceType.tablet:
        return tablet ?? mobile;
      case DeviceType.desktop:
        return desktop ?? tablet ?? mobile;
    }
  }

  /// 获取响应式列数
  static int getResponsiveColumns(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 1,
      tablet: 2,
      desktop: 3,
    );
  }

  /// 获取响应式网格列数
  static int getGridColumns(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 2,
      tablet: 3,
      desktop: 4,
    );
  }

  /// 获取响应式边距
  static EdgeInsets getResponsivePadding(BuildContext context) {
    return EdgeInsets.all(
      getResponsiveValue(
        context: context,
        mobile: 16.w,
        tablet: 24.w,
        desktop: 32.w,
      ),
    );
  }

  /// 获取响应式字体大小
  static double getResponsiveFontSize({
    required BuildContext context,
    required double baseFontSize,
  }) {
    return getResponsiveValue(
      context: context,
      mobile: baseFontSize.sp,
      tablet: (baseFontSize * 1.1).sp,
      desktop: (baseFontSize * 1.2).sp,
    );
  }

  /// 获取响应式图标大小
  static double getResponsiveIconSize(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 24.w,
      tablet: 28.w,
      desktop: 32.w,
    );
  }

  /// 获取响应式卡片高度
  static double getCardHeight(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 120.h,
      tablet: 140.h,
      desktop: 160.h,
    );
  }

  /// 获取响应式按钮高度
  static double getButtonHeight(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 48.h,
      tablet: 52.h,
      desktop: 56.h,
    );
  }

  /// 获取响应式应用栏高度
  static double getAppBarHeight(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: kToolbarHeight,
      tablet: kToolbarHeight + 8,
      desktop: kToolbarHeight + 16,
    );
  }

  /// 获取响应式侧边栏宽度
  static double getSidebarWidth(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 280.w,
      tablet: 320.w,
      desktop: 360.w,
    );
  }

  /// 获取响应式内容最大宽度
  static double getMaxContentWidth(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: double.infinity,
      tablet: 800.w,
      desktop: 1200.w,
    );
  }

  /// 获取响应式网格间距
  static double getGridSpacing(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 8.w,
      tablet: 12.w,
      desktop: 16.w,
    );
  }

  /// 获取响应式圆角半径
  static double getBorderRadius(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 8.r,
      tablet: 12.r,
      desktop: 16.r,
    );
  }

  /// 判断是否应该显示侧边栏
  static bool shouldShowSidebar(BuildContext context) {
    return !isMobile(context);
  }

  /// 判断是否应该使用底部导航
  static bool shouldUseBottomNavigation(BuildContext context) {
    return isMobile(context);
  }

  /// 获取响应式对话框宽度
  static double getDialogWidth(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return getResponsiveValue(
      context: context,
      mobile: screenWidth * 0.9,
      tablet: 500.w,
      desktop: 600.w,
    );
  }

  /// 获取响应式表格列宽
  static Map<int, TableColumnWidth> getTableColumnWidths(BuildContext context) {
    if (isMobile(context)) {
      return {
        0: const FlexColumnWidth(2),
        1: const FlexColumnWidth(3),
        2: const FlexColumnWidth(2),
      };
    } else {
      return {
        0: const FlexColumnWidth(1),
        1: const FlexColumnWidth(2),
        2: const FlexColumnWidth(1),
        3: const FlexColumnWidth(1),
      };
    }
  }

  /// 获取响应式列表项高度
  static double getListItemHeight(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 72.h,
      tablet: 80.h,
      desktop: 88.h,
    );
  }

  /// 获取响应式浮动按钮大小
  static double getFabSize(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 56.w,
      tablet: 64.w,
      desktop: 72.w,
    );
  }

  /// 获取响应式底部导航栏高度
  static double getBottomNavHeight(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 60.h,
      tablet: 70.h,
      desktop: 80.h,
    );
  }

  /// 获取响应式搜索栏高度
  static double getSearchBarHeight(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 40.h,
      tablet: 44.h,
      desktop: 48.h,
    );
  }

  /// 获取响应式卡片边距
  static EdgeInsets getCardMargin(BuildContext context) {
    return EdgeInsets.symmetric(
      horizontal: getResponsiveValue(
        context: context,
        mobile: 16.w,
        tablet: 20.w,
        desktop: 24.w,
      ),
      vertical: getResponsiveValue(
        context: context,
        mobile: 8.h,
        tablet: 10.h,
        desktop: 12.h,
      ),
    );
  }

  /// 获取响应式内容边距
  static EdgeInsets getContentPadding(BuildContext context) {
    return EdgeInsets.symmetric(
      horizontal: getResponsiveValue(
        context: context,
        mobile: 16.w,
        tablet: 24.w,
        desktop: 32.w,
      ),
      vertical: getResponsiveValue(
        context: context,
        mobile: 12.h,
        tablet: 16.h,
        desktop: 20.h,
      ),
    );
  }

  /// 获取响应式分隔线高度
  static double getDividerHeight(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 1.h,
      tablet: 1.5.h,
      desktop: 2.h,
    );
  }

  /// 获取响应式阴影模糊半径
  static double getShadowBlurRadius(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: 4.r,
      tablet: 6.r,
      desktop: 8.r,
    );
  }

  /// 获取响应式动画持续时间
  static Duration getAnimationDuration(BuildContext context) {
    return getResponsiveValue(
      context: context,
      mobile: const Duration(milliseconds: 200),
      tablet: const Duration(milliseconds: 250),
      desktop: const Duration(milliseconds: 300),
    );
  }
}

/// 设备类型枚举
enum DeviceType {
  mobile,
  tablet,
  desktop,
}

/// 响应式布局构建器
class ResponsiveBuilder extends StatelessWidget {
  final Widget Function(BuildContext context, DeviceType deviceType) builder;
  final Widget? mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveBuilder({
    super.key,
    required this.builder,
  })  : mobile = null,
        tablet = null,
        desktop = null;

  const ResponsiveBuilder.widgets({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  }) : builder = _defaultBuilder;

  static Widget _defaultBuilder(BuildContext context, DeviceType deviceType) {
    throw UnimplementedError('Builder not provided');
  }

  @override
  Widget build(BuildContext context) {
    final deviceType = ResponsiveUtils.getDeviceType(context);

    if (mobile != null || tablet != null || desktop != null) {
      switch (deviceType) {
        case DeviceType.mobile:
          return mobile ?? tablet ?? desktop!;
        case DeviceType.tablet:
          return tablet ?? mobile ?? desktop!;
        case DeviceType.desktop:
          return desktop ?? tablet ?? mobile!;
      }
    }

    return builder(context, deviceType);
  }
}

/// 响应式网格视图
class ResponsiveGridView extends StatelessWidget {
  final List<Widget> children;
  final double? spacing;
  final EdgeInsets? padding;
  final ScrollPhysics? physics;
  final bool shrinkWrap;

  const ResponsiveGridView({
    super.key,
    required this.children,
    this.spacing,
    this.padding,
    this.physics,
    this.shrinkWrap = false,
  });

  @override
  Widget build(BuildContext context) {
    final columns = ResponsiveUtils.getGridColumns(context);
    final gridSpacing = spacing ?? ResponsiveUtils.getGridSpacing(context);
    final gridPadding = padding ?? ResponsiveUtils.getResponsivePadding(context);

    return GridView.count(
      crossAxisCount: columns,
      crossAxisSpacing: gridSpacing,
      mainAxisSpacing: gridSpacing,
      padding: gridPadding,
      physics: physics,
      shrinkWrap: shrinkWrap,
      children: children,
    );
  }
}

/// 响应式容器
class ResponsiveContainer extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final double? maxWidth;
  final Color? backgroundColor;
  final BorderRadius? borderRadius;

  const ResponsiveContainer({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.maxWidth,
    this.backgroundColor,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    final responsivePadding = padding ?? ResponsiveUtils.getContentPadding(context);
    final responsiveMargin = margin ?? ResponsiveUtils.getCardMargin(context);
    final responsiveMaxWidth = maxWidth ?? ResponsiveUtils.getMaxContentWidth(context);
    final responsiveBorderRadius = borderRadius ?? BorderRadius.circular(ResponsiveUtils.getBorderRadius(context));

    return Container(
      constraints: BoxConstraints(maxWidth: responsiveMaxWidth),
      margin: responsiveMargin,
      padding: responsivePadding,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: responsiveBorderRadius,
      ),
      child: child,
    );
  }
}

/// 响应式文本
class ResponsiveText extends StatelessWidget {
  final String text;
  final double baseFontSize;
  final FontWeight? fontWeight;
  final Color? color;
  final TextAlign? textAlign;
  final int? maxLines;
  final TextOverflow? overflow;

  const ResponsiveText(
    this.text, {
    super.key,
    required this.baseFontSize,
    this.fontWeight,
    this.color,
    this.textAlign,
    this.maxLines,
    this.overflow,
  });

  @override
  Widget build(BuildContext context) {
    final fontSize = ResponsiveUtils.getResponsiveFontSize(
      context: context,
      baseFontSize: baseFontSize,
    );

    return Text(
      text,
      style: TextStyle(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color,
      ),
      textAlign: textAlign,
      maxLines: maxLines,
      overflow: overflow,
    );
  }
}

/// 响应式按钮
class ResponsiveButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final Color? backgroundColor;
  final Color? textColor;
  final double? width;
  final IconData? icon;

  const ResponsiveButton({
    super.key,
    required this.text,
    this.onPressed,
    this.backgroundColor,
    this.textColor,
    this.width,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final buttonHeight = ResponsiveUtils.getButtonHeight(context);
    final fontSize = ResponsiveUtils.getResponsiveFontSize(
      context: context,
      baseFontSize: 16,
    );
    final borderRadius = ResponsiveUtils.getBorderRadius(context);

    return SizedBox(
      height: buttonHeight,
      width: width,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: backgroundColor,
          foregroundColor: textColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(borderRadius),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              Icon(icon, size: ResponsiveUtils.getResponsiveIconSize(context)),
              SizedBox(width: 8.w),
            ],
            Text(
              text,
              style: TextStyle(fontSize: fontSize),
            ),
          ],
        ),
      ),
    );
  }
}