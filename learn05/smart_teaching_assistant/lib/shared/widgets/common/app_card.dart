import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

/// 智能教学助手 - 统一卡片组件
/// 基于UI 2.0设计规范，提供多种卡片样式和布局
class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final Color? backgroundColor;
  final Color? borderColor;
  final double? borderWidth;
  final BorderRadius? borderRadius;
  final List<BoxShadow>? boxShadow;
  final double? elevation;
  final VoidCallback? onTap;
  final bool isHoverable;
  final AppCardType type;

  const AppCard({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.backgroundColor,
    this.borderColor,
    this.borderWidth,
    this.borderRadius,
    this.boxShadow,
    this.elevation,
    this.onTap,
    this.isHoverable = false,
    this.type = AppCardType.basic,
  }) : super(key: key);

  /// 基础卡片
  const AppCard.basic({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.isHoverable = false,
  }) : type = AppCardType.basic,
       backgroundColor = null,
       borderColor = null,
       borderWidth = null,
       borderRadius = null,
       boxShadow = null,
       elevation = null,
       super(key: key);

  /// 强调卡片 - 带阴影
  const AppCard.elevated({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.isHoverable = true,
  }) : type = AppCardType.elevated,
       backgroundColor = null,
       borderColor = null,
       borderWidth = null,
       borderRadius = null,
       boxShadow = null,
       elevation = null,
       super(key: key);

  /// 边框卡片
  const AppCard.outlined({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.isHoverable = false,
  }) : type = AppCardType.outlined,
       backgroundColor = null,
       borderColor = null,
       borderWidth = null,
       borderRadius = null,
       boxShadow = null,
       elevation = null,
       super(key: key);

  /// 成功状态卡片
  const AppCard.success({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.isHoverable = false,
  }) : type = AppCardType.success,
       backgroundColor = null,
       borderColor = null,
       borderWidth = null,
       borderRadius = null,
       boxShadow = null,
       elevation = null,
       super(key: key);

  /// 警告状态卡片
  const AppCard.warning({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.isHoverable = false,
  }) : type = AppCardType.warning,
       backgroundColor = null,
       borderColor = null,
       borderWidth = null,
       borderRadius = null,
       boxShadow = null,
       elevation = null,
       super(key: key);

  /// 错误状态卡片
  const AppCard.error({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.isHoverable = false,
  }) : type = AppCardType.error,
       backgroundColor = null,
       borderColor = null,
       borderWidth = null,
       borderRadius = null,
       boxShadow = null,
       elevation = null,
       super(key: key);

  /// AI智能卡片 - 渐变背景
  const AppCard.ai({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.isHoverable = true,
  }) : type = AppCardType.ai,
       backgroundColor = null,
       borderColor = null,
       borderWidth = null,
       borderRadius = null,
       boxShadow = null,
       elevation = null,
       super(key: key);

  @override
  Widget build(BuildContext context) {
    final cardConfig = _getCardConfig();
    
    Widget card = Container(
      margin: margin ?? cardConfig.margin,
      decoration: _buildDecoration(cardConfig),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: borderRadius ?? cardConfig.borderRadius,
          hoverColor: isHoverable ? cardConfig.hoverColor : null,
          splashColor: onTap != null ? cardConfig.splashColor : null,
          child: Container(
            padding: padding ?? cardConfig.padding,
            child: child,
          ),
        ),
      ),
    );

    if (isHoverable && onTap != null) {
      return _HoverableCard(
        child: card,
        hoverElevation: cardConfig.hoverElevation,
      );
    }

    return card;
  }

  /// 构建装饰
  BoxDecoration _buildDecoration(_CardConfig config) {
    // AI卡片使用渐变背景
    if (type == AppCardType.ai) {
      return BoxDecoration(
        gradient: LinearGradient(
          colors: [AppTheme.purple500, AppTheme.purple600],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: borderRadius ?? config.borderRadius,
        boxShadow: boxShadow ?? config.boxShadow,
        border: borderColor != null || config.borderColor != null
            ? Border.all(
                color: borderColor ?? config.borderColor!,
                width: borderWidth ?? config.borderWidth,
              )
            : null,
      );
    }

    return BoxDecoration(
      color: backgroundColor ?? config.backgroundColor,
      borderRadius: borderRadius ?? config.borderRadius,
      boxShadow: boxShadow ?? config.boxShadow,
      border: borderColor != null || config.borderColor != null
          ? Border.all(
              color: borderColor ?? config.borderColor!,
              width: borderWidth ?? config.borderWidth,
            )
          : null,
    );
  }

  /// 获取卡片配置
  _CardConfig _getCardConfig() {
    switch (type) {
      case AppCardType.basic:
        return _CardConfig(
          backgroundColor: AppTheme.bgPrimary,
          borderRadius: BorderRadius.circular(AppTheme.radiusXl),
          padding: EdgeInsets.all(AppTheme.space4),
          margin: EdgeInsets.all(AppTheme.space2),
          boxShadow: AppTheme.shadowXs,
          borderColor: AppTheme.borderLight,
          borderWidth: 1,
          hoverColor: AppTheme.gray50.withOpacity(0.5),
          splashColor: AppTheme.primary100.withOpacity(0.3),
          hoverElevation: 2,
        );
      case AppCardType.elevated:
        return _CardConfig(
          backgroundColor: AppTheme.bgPrimary,
          borderRadius: BorderRadius.circular(AppTheme.radiusXl),
          padding: EdgeInsets.all(AppTheme.space6),
          margin: EdgeInsets.all(AppTheme.space3),
          boxShadow: AppTheme.shadowMd,
          hoverColor: AppTheme.gray50.withOpacity(0.5),
          splashColor: AppTheme.primary100.withOpacity(0.3),
          hoverElevation: 8,
        );
      case AppCardType.outlined:
        return _CardConfig(
          backgroundColor: AppTheme.bgPrimary,
          borderRadius: BorderRadius.circular(AppTheme.radiusXl),
          padding: EdgeInsets.all(AppTheme.space4),
          margin: EdgeInsets.all(AppTheme.space2),
          borderColor: AppTheme.borderDefault,
          borderWidth: 1.5,
          hoverColor: AppTheme.gray50.withOpacity(0.5),
          splashColor: AppTheme.primary100.withOpacity(0.3),
          hoverElevation: 1,
        );
      case AppCardType.success:
        return _CardConfig(
          backgroundColor: AppTheme.secondary50,
          borderRadius: BorderRadius.circular(AppTheme.radiusXl),
          padding: EdgeInsets.all(AppTheme.space4),
          margin: EdgeInsets.all(AppTheme.space2),
          borderColor: AppTheme.secondary200,
          borderWidth: 1,
          boxShadow: AppTheme.shadowSm,
          hoverColor: AppTheme.secondary100.withOpacity(0.5),
          splashColor: AppTheme.secondary200.withOpacity(0.3),
          hoverElevation: 2,
        );
      case AppCardType.warning:
        return _CardConfig(
          backgroundColor: AppTheme.accent50,
          borderRadius: BorderRadius.circular(AppTheme.radiusXl),
          padding: EdgeInsets.all(AppTheme.space4),
          margin: EdgeInsets.all(AppTheme.space2),
          borderColor: AppTheme.accent200,
          borderWidth: 1,
          boxShadow: AppTheme.shadowSm,
          hoverColor: AppTheme.accent100.withOpacity(0.5),
          splashColor: AppTheme.accent200.withOpacity(0.3),
          hoverElevation: 2,
        );
      case AppCardType.error:
        return _CardConfig(
          backgroundColor: AppTheme.error50,
          borderRadius: BorderRadius.circular(AppTheme.radiusXl),
          padding: EdgeInsets.all(AppTheme.space4),
          margin: EdgeInsets.all(AppTheme.space2),
          borderColor: AppTheme.error500,
          borderWidth: 1,
          boxShadow: AppTheme.shadowSm,
          hoverColor: AppTheme.error100.withOpacity(0.5),
          splashColor: AppTheme.error500.withOpacity(0.3),
          hoverElevation: 2,
        );
      case AppCardType.ai:
        return _CardConfig(
          backgroundColor: Colors.transparent,
          borderRadius: BorderRadius.circular(AppTheme.radiusXl),
          padding: EdgeInsets.all(AppTheme.space6),
          margin: EdgeInsets.all(AppTheme.space3),
          boxShadow: AppTheme.shadowLg,
          hoverColor: Colors.white.withOpacity(0.1),
          splashColor: Colors.white.withOpacity(0.2),
          hoverElevation: 12,
        );
    }
  }
}

/// 可悬停卡片组件
class _HoverableCard extends StatefulWidget {
  final Widget child;
  final double hoverElevation;

  const _HoverableCard({
    Key? key,
    required this.child,
    required this.hoverElevation,
  }) : super(key: key);

  @override
  State<_HoverableCard> createState() => _HoverableCardState();
}

class _HoverableCardState extends State<_HoverableCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _elevationAnimation;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: AppTheme.transitionBase,
      vsync: this,
    );
    _elevationAnimation = Tween<double>(
      begin: 0,
      end: widget.hoverElevation,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: AppTheme.curveEaseOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => _onHover(true),
      onExit: (_) => _onHover(false),
      child: AnimatedBuilder(
        animation: _elevationAnimation,
        builder: (context, child) {
          return Transform.translate(
            offset: Offset(0, -_elevationAnimation.value / 4),
            child: widget.child,
          );
        },
      ),
    );
  }

  void _onHover(bool isHovered) {
    if (_isHovered != isHovered) {
      setState(() {
        _isHovered = isHovered;
      });
      if (isHovered) {
        _animationController.forward();
      } else {
        _animationController.reverse();
      }
    }
  }
}

/// 卡片类型枚举
enum AppCardType {
  basic,    // 基础卡片
  elevated, // 强调卡片
  outlined, // 边框卡片
  success,  // 成功状态
  warning,  // 警告状态
  error,    // 错误状态
  ai,       // AI智能卡片
}

/// 卡片配置类
class _CardConfig {
  final Color backgroundColor;
  final BorderRadius borderRadius;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry margin;
  final List<BoxShadow>? boxShadow;
  final Color? borderColor;
  final double borderWidth;
  final Color hoverColor;
  final Color splashColor;
  final double hoverElevation;

  const _CardConfig({
    required this.backgroundColor,
    required this.borderRadius,
    required this.padding,
    required this.margin,
    this.boxShadow,
    this.borderColor,
    this.borderWidth = 0,
    required this.hoverColor,
    required this.splashColor,
    required this.hoverElevation,
  });
}