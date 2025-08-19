import 'package:flutter/material.dart';

/// 应用尺寸常量定义
/// 
/// 定义了整个应用的尺寸规范，包括：
/// - 间距（内边距、外边距、组件间距）
/// - 圆角半径
/// - 组件尺寸（按钮、输入框、图标等）
/// - 布局尺寸（容器、卡片、列表等）
/// - 响应式断点
class AppDimensions {
  // 私有构造函数，防止实例化
  AppDimensions._();

  // 基础间距单位
  static const double baseSpacing = 8.0;
  
  // 间距系列
  static const double spacingTiny = baseSpacing * 0.5;    // 4.0
  static const double spacingSmall = baseSpacing;         // 8.0
  static const double spacingMedium = baseSpacing * 2;    // 16.0
  static const double spacingLarge = baseSpacing * 3;     // 24.0
  static const double spacingXLarge = baseSpacing * 4;    // 32.0
  static const double spacingXXLarge = baseSpacing * 6;   // 48.0
  
  // 内边距系列
  static const double paddingTiny = spacingTiny;
  static const double paddingSmall = spacingSmall;
  static const double paddingMedium = spacingMedium;
  static const double paddingLarge = spacingLarge;
  static const double paddingXLarge = spacingXLarge;
  static const double paddingXXLarge = spacingXXLarge;
  
  // 外边距系列
  static const double marginTiny = spacingTiny;
  static const double marginSmall = spacingSmall;
  static const double marginMedium = spacingMedium;
  static const double marginLarge = spacingLarge;
  static const double marginXLarge = spacingXLarge;
  static const double marginXXLarge = spacingXXLarge;
  
  // 圆角半径系列
  static const double radiusNone = 0.0;
  static const double radiusSmall = 4.0;
  static const double radiusMedium = 8.0;
  static const double radiusLarge = 12.0;
  static const double radiusXLarge = 16.0;
  static const double radiusXXLarge = 24.0;
  static const double radiusCircular = 999.0;
  
  // 边框宽度
  static const double borderWidthThin = 0.5;
  static const double borderWidthNormal = 1.0;
  static const double borderWidthThick = 2.0;
  static const double borderWidthBold = 3.0;
  
  // 阴影相关
  static const double elevationNone = 0.0;
  static const double elevationLow = 2.0;
  static const double elevationMedium = 4.0;
  static const double elevationHigh = 8.0;
  static const double elevationVeryHigh = 16.0;
  
  // 模糊半径
  static const double blurRadiusSmall = 4.0;
  static const double blurRadiusMedium = 8.0;
  static const double blurRadiusLarge = 16.0;
  
  // 按钮尺寸
  static const double buttonHeightSmall = 32.0;
  static const double buttonHeightMedium = 40.0;
  static const double buttonHeightLarge = 48.0;
  static const double buttonHeightXLarge = 56.0;
  
  static const double buttonMinWidth = 64.0;
  static const double buttonPaddingHorizontal = paddingMedium;
  static const double buttonPaddingVertical = paddingSmall;
  
  // 输入框尺寸
  static const double inputHeightSmall = 36.0;
  static const double inputHeightMedium = 44.0;
  static const double inputHeightLarge = 52.0;
  
  static const double inputPaddingHorizontal = paddingMedium;
  static const double inputPaddingVertical = paddingSmall;
  
  // 图标尺寸
  static const double iconSizeTiny = 12.0;
  static const double iconSizeSmall = 16.0;
  static const double iconSizeMedium = 24.0;
  static const double iconSizeLarge = 32.0;
  static const double iconSizeXLarge = 48.0;
  static const double iconSizeXXLarge = 64.0;
  
  // 头像尺寸
  static const double avatarSizeSmall = 32.0;
  static const double avatarSizeMedium = 48.0;
  static const double avatarSizeLarge = 64.0;
  static const double avatarSizeXLarge = 96.0;
  
  // 卡片尺寸
  static const double cardPadding = paddingMedium;
  static const double cardMargin = marginSmall;
  static const double cardRadius = radiusMedium;
  static const double cardElevation = elevationLow;
  
  // 列表项尺寸
  static const double listItemHeight = 56.0;
  static const double listItemHeightSmall = 48.0;
  static const double listItemHeightLarge = 72.0;
  static const double listItemPadding = paddingMedium;
  
  // 应用栏尺寸
  static const double appBarHeight = 56.0;
  static const double appBarElevation = elevationLow;
  
  // 底部导航栏尺寸
  static const double bottomNavHeight = 60.0;
  static const double bottomNavElevation = elevationMedium;
  
  // 抽屉尺寸
  static const double drawerWidth = 280.0;
  static const double drawerHeaderHeight = 160.0;
  
  // 对话框尺寸
  static const double dialogMaxWidth = 400.0;
  static const double dialogMinWidth = 280.0;
  static const double dialogPadding = paddingLarge;
  static const double dialogRadius = radiusLarge;
  
  // 底部弹窗尺寸
  static const double bottomSheetRadius = radiusLarge;
  static const double bottomSheetMaxHeight = 0.9; // 屏幕高度的90%
  
  // 标签页尺寸
  static const double tabHeight = 48.0;
  static const double tabMinWidth = 72.0;
  static const double tabPadding = paddingMedium;
  
  // 进度条尺寸
  static const double progressBarHeight = 4.0;
  static const double progressBarRadius = radiusSmall;
  
  // 滑块尺寸
  static const double sliderHeight = 40.0;
  static const double sliderThumbRadius = 10.0;
  static const double sliderTrackHeight = 4.0;
  
  // 开关尺寸
  static const double switchWidth = 51.0;
  static const double switchHeight = 31.0;
  static const double switchThumbRadius = 10.0;
  
  // 复选框和单选框尺寸
  static const double checkboxSize = 20.0;
  static const double radioSize = 20.0;
  
  // 分割线尺寸
  static const double dividerHeight = 1.0;
  static const double dividerIndent = paddingMedium;
  
  // 响应式断点
  static const double breakpointMobile = 600.0;
  static const double breakpointTablet = 900.0;
  static const double breakpointDesktop = 1200.0;
  static const double breakpointLargeDesktop = 1600.0;
  
  // 容器最大宽度
  static const double containerMaxWidthMobile = 400.0;
  static const double containerMaxWidthTablet = 600.0;
  static const double containerMaxWidthDesktop = 800.0;
  static const double containerMaxWidthLarge = 1200.0;
  
  // 网格布局
  static const double gridSpacing = spacingMedium;
  static const double gridCrossAxisSpacing = spacingMedium;
  static const double gridMainAxisSpacing = spacingMedium;
  
  // 图表尺寸
  static const double chartHeight = 300.0;
  static const double chartPadding = paddingMedium;
  static const double chartLegendHeight = 40.0;
  
  // 表格尺寸
  static const double tableRowHeight = 48.0;
  static const double tableHeaderHeight = 56.0;
  static const double tableCellPadding = paddingSmall;
  
  // 工具方法
  
  /// 获取响应式间距
  static double getResponsiveSpacing(BuildContext context, double baseSpacing) {
    final screenWidth = MediaQuery.of(context).size.width;
    if (screenWidth < breakpointMobile) {
      return baseSpacing * 0.8; // 小屏幕减少间距
    } else if (screenWidth < breakpointTablet) {
      return baseSpacing; // 中等屏幕正常间距
    } else {
      return baseSpacing * 1.2; // 大屏幕增加间距
    }
  }
  
  /// 获取响应式内边距
  static EdgeInsets getResponsivePadding(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    if (screenWidth < breakpointMobile) {
      return const EdgeInsets.all(paddingSmall);
    } else if (screenWidth < breakpointTablet) {
      return const EdgeInsets.all(paddingMedium);
    } else {
      return const EdgeInsets.all(paddingLarge);
    }
  }
  
  /// 获取响应式容器宽度
  static double getResponsiveWidth(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    if (screenWidth < breakpointMobile) {
      return containerMaxWidthMobile;
    } else if (screenWidth < breakpointTablet) {
      return containerMaxWidthTablet;
    } else if (screenWidth < breakpointDesktop) {
      return containerMaxWidthDesktop;
    } else {
      return containerMaxWidthLarge;
    }
  }
  
  /// 判断是否为移动端
  static bool isMobile(BuildContext context) {
    return MediaQuery.of(context).size.width < breakpointMobile;
  }
  
  /// 判断是否为平板端
  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= breakpointMobile && width < breakpointDesktop;
  }
  
  /// 判断是否为桌面端
  static bool isDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= breakpointDesktop;
  }
  
  /// 获取网格列数
  static int getGridColumns(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    if (screenWidth < breakpointMobile) {
      return 1; // 移动端1列
    } else if (screenWidth < breakpointTablet) {
      return 2; // 小平板2列
    } else if (screenWidth < breakpointDesktop) {
      return 3; // 大平板3列
    } else {
      return 4; // 桌面端4列
    }
  }
  
  /// 获取安全区域内边距
  static EdgeInsets getSafeAreaPadding(BuildContext context) {
    final mediaQuery = MediaQuery.of(context);
    return EdgeInsets.only(
      top: mediaQuery.padding.top,
      bottom: mediaQuery.padding.bottom,
      left: mediaQuery.padding.left,
      right: mediaQuery.padding.right,
    );
  }
  
  /// 创建对称内边距
  static EdgeInsets symmetric({
    double horizontal = 0.0,
    double vertical = 0.0,
  }) {
    return EdgeInsets.symmetric(
      horizontal: horizontal,
      vertical: vertical,
    );
  }
  
  /// 创建只有特定方向的内边距
  static EdgeInsets only({
    double left = 0.0,
    double top = 0.0,
    double right = 0.0,
    double bottom = 0.0,
  }) {
    return EdgeInsets.only(
      left: left,
      top: top,
      right: right,
      bottom: bottom,
    );
  }
}