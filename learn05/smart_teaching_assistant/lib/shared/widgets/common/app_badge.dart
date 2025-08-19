import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

/// 智能教学助手 - 统一徽章组件
/// 基于UI 2.0设计规范，提供多种徽章样式和功能
class AppBadge extends StatelessWidget {
  final String? text;
  final int? count;
  final Widget? child;
  final AppBadgeType type;
  final AppBadgeSize size;
  final Color? backgroundColor;
  final Color? textColor;
  final Color? borderColor;
  final bool showZero;
  final int? maxCount;
  final bool dot;
  final EdgeInsetsGeometry? padding;
  final double? borderRadius;
  final TextStyle? textStyle;
  final Offset? offset;

  const AppBadge({
    Key? key,
    this.text,
    this.count,
    this.child,
    this.type = AppBadgeType.primary,
    this.size = AppBadgeSize.medium,
    this.backgroundColor,
    this.textColor,
    this.borderColor,
    this.showZero = false,
    this.maxCount = 99,
    this.dot = false,
    this.padding,
    this.borderRadius,
    this.textStyle,
    this.offset,
  }) : assert(text != null || count != null || dot, 'Either text, count, or dot must be provided'),
       super(key: key);

  /// 数字徽章
  const AppBadge.count({
    Key? key,
    required int this.count,
    this.child,
    this.type = AppBadgeType.primary,
    this.size = AppBadgeSize.medium,
    this.backgroundColor,
    this.textColor,
    this.borderColor,
    this.showZero = false,
    this.maxCount = 99,
    this.padding,
    this.borderRadius,
    this.textStyle,
    this.offset,
  }) : text = null,
       dot = false,
       super(key: key);

  /// 文本徽章
  const AppBadge.text({
    Key? key,
    required String this.text,
    this.child,
    this.type = AppBadgeType.primary,
    this.size = AppBadgeSize.medium,
    this.backgroundColor,
    this.textColor,
    this.borderColor,
    this.padding,
    this.borderRadius,
    this.textStyle,
    this.offset,
  }) : count = null,
       showZero = false,
       maxCount = null,
       dot = false,
       super(key: key);

  /// 点状徽章
  const AppBadge.dot({
    Key? key,
    this.child,
    this.type = AppBadgeType.primary,
    this.size = AppBadgeSize.medium,
    this.backgroundColor,
    this.borderColor,
    this.offset,
  }) : text = null,
       count = null,
       textColor = null,
       showZero = false,
       maxCount = null,
       dot = true,
       padding = null,
       borderRadius = null,
       textStyle = null,
       super(key: key);

  @override
  Widget build(BuildContext context) {
    final config = _getBadgeConfig();
    
    // 如果有子组件，使用Stack布局
    if (child != null) {
      return Stack(
        clipBehavior: Clip.none,
        children: [
          child!,
          if (_shouldShowBadge())
            Positioned(
              top: (offset?.dy ?? 0) - config.badgeSize / 2,
              right: (offset?.dx ?? 0) - config.badgeSize / 2,
              child: _buildBadge(config),
            ),
        ],
      );
    }
    
    // 如果没有子组件，直接显示徽章
    return _shouldShowBadge() ? _buildBadge(config) : const SizedBox.shrink();
  }

  /// 构建徽章
  Widget _buildBadge(_BadgeConfig config) {
    if (dot) {
      return _buildDotBadge(config);
    }
    
    return _buildTextBadge(config);
  }

  /// 构建点状徽章
  Widget _buildDotBadge(_BadgeConfig config) {
    return Container(
      width: config.dotSize,
      height: config.dotSize,
      decoration: BoxDecoration(
        color: backgroundColor ?? config.backgroundColor,
        shape: BoxShape.circle,
        border: borderColor != null ? Border.all(
          color: borderColor!,
          width: 1,
        ) : null,
        boxShadow: [
          BoxShadow(
            color: AppTheme.shadowColor,
            blurRadius: 2,
            offset: Offset(0, 1),
          ),
        ],
      ),
    );
  }

  /// 构建文本徽章
  Widget _buildTextBadge(_BadgeConfig config) {
    final badgeText = _getBadgeText();
    
    return Container(
      constraints: BoxConstraints(
        minWidth: config.minWidth,
        minHeight: config.badgeSize,
      ),
      padding: padding ?? config.padding,
      decoration: BoxDecoration(
        color: backgroundColor ?? config.backgroundColor,
        borderRadius: BorderRadius.circular(
          borderRadius ?? config.borderRadius,
        ),
        border: borderColor != null ? Border.all(
          color: borderColor!,
          width: 1,
        ) : null,
        boxShadow: [
          BoxShadow(
            color: AppTheme.shadowColor,
            blurRadius: 2,
            offset: Offset(0, 1),
          ),
        ],
      ),
      child: Center(
        child: Text(
          badgeText,
          style: textStyle ?? config.textStyle.copyWith(
            color: textColor ?? config.textColor,
          ),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }

  /// 获取徽章文本
  String _getBadgeText() {
    if (text != null) {
      return text!;
    }
    
    if (count != null) {
      if (count! > (maxCount ?? 99)) {
        return '${maxCount}+';
      }
      return count.toString();
    }
    
    return '';
  }

  /// 是否应该显示徽章
  bool _shouldShowBadge() {
    if (dot) return true;
    if (text != null && text!.isNotEmpty) return true;
    if (count != null) {
      return count! > 0 || showZero;
    }
    return false;
  }

  /// 获取徽章配置
  _BadgeConfig _getBadgeConfig() {
    switch (type) {
      case AppBadgeType.primary:
        return _BadgeConfig(
          backgroundColor: AppTheme.primary500,
          textColor: Colors.white,
          textStyle: _getTextStyle(),
          padding: _getPadding(),
          borderRadius: _getBorderRadius(),
          badgeSize: _getBadgeSize(),
          minWidth: _getMinWidth(),
          dotSize: _getDotSize(),
        );
      case AppBadgeType.secondary:
        return _BadgeConfig(
          backgroundColor: AppTheme.gray500,
          textColor: Colors.white,
          textStyle: _getTextStyle(),
          padding: _getPadding(),
          borderRadius: _getBorderRadius(),
          badgeSize: _getBadgeSize(),
          minWidth: _getMinWidth(),
          dotSize: _getDotSize(),
        );
      case AppBadgeType.success:
        return _BadgeConfig(
          backgroundColor: AppTheme.success500,
          textColor: Colors.white,
          textStyle: _getTextStyle(),
          padding: _getPadding(),
          borderRadius: _getBorderRadius(),
          badgeSize: _getBadgeSize(),
          minWidth: _getMinWidth(),
          dotSize: _getDotSize(),
        );
      case AppBadgeType.warning:
        return _BadgeConfig(
          backgroundColor: AppTheme.warning500,
          textColor: Colors.white,
          textStyle: _getTextStyle(),
          padding: _getPadding(),
          borderRadius: _getBorderRadius(),
          badgeSize: _getBadgeSize(),
          minWidth: _getMinWidth(),
          dotSize: _getDotSize(),
        );
      case AppBadgeType.error:
        return _BadgeConfig(
          backgroundColor: AppTheme.error500,
          textColor: Colors.white,
          textStyle: _getTextStyle(),
          padding: _getPadding(),
          borderRadius: _getBorderRadius(),
          badgeSize: _getBadgeSize(),
          minWidth: _getMinWidth(),
          dotSize: _getDotSize(),
        );
      case AppBadgeType.info:
        return _BadgeConfig(
          backgroundColor: AppTheme.info500,
          textColor: Colors.white,
          textStyle: _getTextStyle(),
          padding: _getPadding(),
          borderRadius: _getBorderRadius(),
          badgeSize: _getBadgeSize(),
          minWidth: _getMinWidth(),
          dotSize: _getDotSize(),
        );
      case AppBadgeType.ai:
        return _BadgeConfig(
          backgroundColor: AppTheme.purple500,
          textColor: Colors.white,
          textStyle: _getTextStyle(),
          padding: _getPadding(),
          borderRadius: _getBorderRadius(),
          badgeSize: _getBadgeSize(),
          minWidth: _getMinWidth(),
          dotSize: _getDotSize(),
        );
    }
  }

  /// 获取文本样式
  TextStyle _getTextStyle() {
    switch (size) {
      case AppBadgeSize.small:
        return TextStyle(
          fontSize: AppTheme.textXs,
          fontWeight: AppTheme.fontMedium,
          height: 1.0,
        );
      case AppBadgeSize.medium:
        return TextStyle(
          fontSize: AppTheme.textSm,
          fontWeight: AppTheme.fontMedium,
          height: 1.0,
        );
      case AppBadgeSize.large:
        return TextStyle(
          fontSize: AppTheme.textBase,
          fontWeight: AppTheme.fontMedium,
          height: 1.0,
        );
    }
  }

  /// 获取内边距
  EdgeInsetsGeometry _getPadding() {
    switch (size) {
      case AppBadgeSize.small:
        return EdgeInsets.symmetric(
          horizontal: AppTheme.space1,
          vertical: AppTheme.space1,
        );
      case AppBadgeSize.medium:
        return EdgeInsets.symmetric(
          horizontal: AppTheme.space2,
          vertical: AppTheme.space1,
        );
      case AppBadgeSize.large:
        return EdgeInsets.symmetric(
          horizontal: AppTheme.space3,
          vertical: AppTheme.space2,
        );
    }
  }

  /// 获取圆角
  double _getBorderRadius() {
    switch (size) {
      case AppBadgeSize.small:
        return AppTheme.radiusSm;
      case AppBadgeSize.medium:
        return AppTheme.radiusMd;
      case AppBadgeSize.large:
        return AppTheme.radiusLg;
    }
  }

  /// 获取徽章尺寸
  double _getBadgeSize() {
    switch (size) {
      case AppBadgeSize.small:
        return 16;
      case AppBadgeSize.medium:
        return 20;
      case AppBadgeSize.large:
        return 24;
    }
  }

  /// 获取最小宽度
  double _getMinWidth() {
    switch (size) {
      case AppBadgeSize.small:
        return 16;
      case AppBadgeSize.medium:
        return 20;
      case AppBadgeSize.large:
        return 24;
    }
  }

  /// 获取点状徽章尺寸
  double _getDotSize() {
    switch (size) {
      case AppBadgeSize.small:
        return 6;
      case AppBadgeSize.medium:
        return 8;
      case AppBadgeSize.large:
        return 10;
    }
  }
}

/// 徽章类型枚举
enum AppBadgeType {
  primary,   // 主要
  secondary, // 次要
  success,   // 成功
  warning,   // 警告
  error,     // 错误
  info,      // 信息
  ai,        // AI
}

/// 徽章尺寸枚举
enum AppBadgeSize {
  small,  // 小
  medium, // 中
  large,  // 大
}

/// 徽章配置类
class _BadgeConfig {
  final Color backgroundColor;
  final Color textColor;
  final TextStyle textStyle;
  final EdgeInsetsGeometry padding;
  final double borderRadius;
  final double badgeSize;
  final double minWidth;
  final double dotSize;

  const _BadgeConfig({
    required this.backgroundColor,
    required this.textColor,
    required this.textStyle,
    required this.padding,
    required this.borderRadius,
    required this.badgeSize,
    required this.minWidth,
    required this.dotSize,
  });
}