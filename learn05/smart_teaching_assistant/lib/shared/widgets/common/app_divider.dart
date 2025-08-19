import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

/// 智能教学助手 - 统一分割线组件
/// 基于UI 2.0设计规范，提供多种分割线样式和功能
class AppDivider extends StatelessWidget {
  final AppDividerType type;
  final double? height;
  final double? thickness;
  final double? indent;
  final double? endIndent;
  final Color? color;
  final String? text;
  final Widget? child;
  final TextStyle? textStyle;
  final EdgeInsetsGeometry? textPadding;
  final bool dashed;
  final double? dashWidth;
  final double? dashGap;

  const AppDivider({
    Key? key,
    this.type = AppDividerType.horizontal,
    this.height,
    this.thickness,
    this.indent,
    this.endIndent,
    this.color,
    this.text,
    this.child,
    this.textStyle,
    this.textPadding,
    this.dashed = false,
    this.dashWidth,
    this.dashGap,
  }) : super(key: key);

  /// 水平分割线
  const AppDivider.horizontal({
    Key? key,
    this.height,
    this.thickness,
    this.indent,
    this.endIndent,
    this.color,
    this.text,
    this.child,
    this.textStyle,
    this.textPadding,
    this.dashed = false,
    this.dashWidth,
    this.dashGap,
  }) : type = AppDividerType.horizontal,
       super(key: key);

  /// 垂直分割线
  const AppDivider.vertical({
    Key? key,
    this.height,
    this.thickness,
    this.indent,
    this.endIndent,
    this.color,
    this.dashed = false,
    this.dashWidth,
    this.dashGap,
  }) : type = AppDividerType.vertical,
       text = null,
       child = null,
       textStyle = null,
       textPadding = null,
       super(key: key);

  /// 带文字的分割线
  const AppDivider.withText({
    Key? key,
    required String this.text,
    this.height,
    this.thickness,
    this.indent,
    this.endIndent,
    this.color,
    this.textStyle,
    this.textPadding,
    this.dashed = false,
    this.dashWidth,
    this.dashGap,
  }) : type = AppDividerType.horizontal,
       child = null,
       super(key: key);

  /// 带自定义组件的分割线
  const AppDivider.withChild({
    Key? key,
    required Widget this.child,
    this.height,
    this.thickness,
    this.indent,
    this.endIndent,
    this.color,
    this.textPadding,
    this.dashed = false,
    this.dashWidth,
    this.dashGap,
  }) : type = AppDividerType.horizontal,
       text = null,
       textStyle = null,
       super(key: key);

  /// 虚线分割线
  const AppDivider.dashed({
    Key? key,
    this.type = AppDividerType.horizontal,
    this.height,
    this.thickness,
    this.indent,
    this.endIndent,
    this.color,
    this.dashWidth,
    this.dashGap,
  }) : dashed = true,
       text = null,
       child = null,
       textStyle = null,
       textPadding = null,
       super(key: key);

  @override
  Widget build(BuildContext context) {
    final config = _getDividerConfig();
    
    switch (type) {
      case AppDividerType.horizontal:
        return _buildHorizontalDivider(config);
      case AppDividerType.vertical:
        return _buildVerticalDivider(config);
    }
  }

  /// 构建水平分割线
  Widget _buildHorizontalDivider(_DividerConfig config) {
    if (text != null || child != null) {
      return _buildDividerWithContent(config);
    }
    
    if (dashed) {
      return _buildDashedHorizontalDivider(config);
    }
    
    return Container(
      height: height ?? config.height,
      margin: EdgeInsets.only(
        left: indent ?? 0,
        right: endIndent ?? 0,
      ),
      child: Divider(
        height: height ?? config.height,
        thickness: thickness ?? config.thickness,
        color: color ?? config.color,
        indent: 0,
        endIndent: 0,
      ),
    );
  }

  /// 构建垂直分割线
  Widget _buildVerticalDivider(_DividerConfig config) {
    if (dashed) {
      return _buildDashedVerticalDivider(config);
    }
    
    return Container(
      width: thickness ?? config.thickness,
      margin: EdgeInsets.only(
        top: indent ?? 0,
        bottom: endIndent ?? 0,
      ),
      child: VerticalDivider(
        width: thickness ?? config.thickness,
        thickness: thickness ?? config.thickness,
        color: color ?? config.color,
        indent: 0,
        endIndent: 0,
      ),
    );
  }

  /// 构建带内容的分割线
  Widget _buildDividerWithContent(_DividerConfig config) {
    final contentWidget = child ?? Text(
      text!,
      style: textStyle ?? config.textStyle,
    );
    
    return Container(
      height: height ?? config.height,
      child: Row(
        children: [
          if (indent != null) SizedBox(width: indent!),
          Expanded(
            child: dashed 
                ? _buildDashedLine(config, isHorizontal: true)
                : Divider(
                    height: 1,
                    thickness: thickness ?? config.thickness,
                    color: color ?? config.color,
                  ),
          ),
          Container(
            padding: textPadding ?? EdgeInsets.symmetric(
              horizontal: AppTheme.space3,
            ),
            child: contentWidget,
          ),
          Expanded(
            child: dashed 
                ? _buildDashedLine(config, isHorizontal: true)
                : Divider(
                    height: 1,
                    thickness: thickness ?? config.thickness,
                    color: color ?? config.color,
                  ),
          ),
          if (endIndent != null) SizedBox(width: endIndent!),
        ],
      ),
    );
  }

  /// 构建虚线水平分割线
  Widget _buildDashedHorizontalDivider(_DividerConfig config) {
    return Container(
      height: height ?? config.height,
      margin: EdgeInsets.only(
        left: indent ?? 0,
        right: endIndent ?? 0,
      ),
      child: Center(
        child: _buildDashedLine(config, isHorizontal: true),
      ),
    );
  }

  /// 构建虚线垂直分割线
  Widget _buildDashedVerticalDivider(_DividerConfig config) {
    return Container(
      width: thickness ?? config.thickness,
      margin: EdgeInsets.only(
        top: indent ?? 0,
        bottom: endIndent ?? 0,
      ),
      child: Center(
        child: _buildDashedLine(config, isHorizontal: false),
      ),
    );
  }

  /// 构建虚线
  Widget _buildDashedLine(_DividerConfig config, {required bool isHorizontal}) {
    return CustomPaint(
      painter: _DashedLinePainter(
        color: color ?? config.color,
        strokeWidth: thickness ?? config.thickness,
        dashWidth: dashWidth ?? config.dashWidth,
        dashGap: dashGap ?? config.dashGap,
        isHorizontal: isHorizontal,
      ),
      child: isHorizontal 
          ? SizedBox(height: thickness ?? config.thickness)
          : SizedBox(width: thickness ?? config.thickness),
    );
  }

  /// 获取分割线配置
  _DividerConfig _getDividerConfig() {
    return _DividerConfig(
      height: 16.0,
      thickness: 1.0,
      color: AppTheme.borderLight,
      textStyle: TextStyle(
        fontSize: AppTheme.textSm,
        fontWeight: AppTheme.fontNormal,
        color: AppTheme.textSecondary,
      ),
      dashWidth: 4.0,
      dashGap: 4.0,
    );
  }
}

/// 分割线类型枚举
enum AppDividerType {
  horizontal, // 水平
  vertical,   // 垂直
}

/// 分割线配置类
class _DividerConfig {
  final double height;
  final double thickness;
  final Color color;
  final TextStyle textStyle;
  final double dashWidth;
  final double dashGap;

  const _DividerConfig({
    required this.height,
    required this.thickness,
    required this.color,
    required this.textStyle,
    required this.dashWidth,
    required this.dashGap,
  });
}

/// 虚线绘制器
class _DashedLinePainter extends CustomPainter {
  final Color color;
  final double strokeWidth;
  final double dashWidth;
  final double dashGap;
  final bool isHorizontal;

  _DashedLinePainter({
    required this.color,
    required this.strokeWidth,
    required this.dashWidth,
    required this.dashGap,
    required this.isHorizontal,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke;

    final path = Path();
    
    if (isHorizontal) {
      double startX = 0;
      while (startX < size.width) {
        final endX = (startX + dashWidth).clamp(0.0, size.width);
        path.moveTo(startX, size.height / 2);
        path.lineTo(endX, size.height / 2);
        startX += dashWidth + dashGap;
      }
    } else {
      double startY = 0;
      while (startY < size.height) {
        final endY = (startY + dashWidth).clamp(0.0, size.height);
        path.moveTo(size.width / 2, startY);
        path.lineTo(size.width / 2, endY);
        startY += dashWidth + dashGap;
      }
    }

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return oldDelegate is! _DashedLinePainter ||
        oldDelegate.color != color ||
        oldDelegate.strokeWidth != strokeWidth ||
        oldDelegate.dashWidth != dashWidth ||
        oldDelegate.dashGap != dashGap ||
        oldDelegate.isHorizontal != isHorizontal;
  }
}