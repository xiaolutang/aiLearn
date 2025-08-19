import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

/// 智能教学助手 - 统一按钮组件
/// 基于UI 2.0设计规范，提供多种按钮样式和状态
class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final AppButtonType type;
  final AppButtonSize size;
  final Widget? icon;
  final bool isLoading;
  final bool isFullWidth;
  final EdgeInsetsGeometry? padding;
  final BorderRadius? borderRadius;

  const AppButton({
    Key? key,
    required this.text,
    this.onPressed,
    this.type = AppButtonType.primary,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
    this.padding,
    this.borderRadius,
  }) : super(key: key);

  /// 主要按钮 - 教育蓝
  const AppButton.primary({
    Key? key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
    this.padding,
    this.borderRadius,
  }) : type = AppButtonType.primary, super(key: key);

  /// 次要按钮 - 优雅边框
  const AppButton.secondary({
    Key? key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
    this.padding,
    this.borderRadius,
  }) : type = AppButtonType.secondary, super(key: key);

  /// 成功按钮 - 智能绿
  const AppButton.success({
    Key? key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
    this.padding,
    this.borderRadius,
  }) : type = AppButtonType.success, super(key: key);

  /// 警告按钮 - 活力橙
  const AppButton.warning({
    Key? key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
    this.padding,
    this.borderRadius,
  }) : type = AppButtonType.warning, super(key: key);

  /// 危险按钮 - 错误红
  const AppButton.danger({
    Key? key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
    this.padding,
    this.borderRadius,
  }) : type = AppButtonType.danger, super(key: key);

  /// AI智能按钮 - 紫色渐变
  const AppButton.ai({
    Key? key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
    this.padding,
    this.borderRadius,
  }) : type = AppButtonType.ai, super(key: key);

  /// 文本按钮
  const AppButton.text({
    Key? key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
    this.padding,
    this.borderRadius,
  }) : type = AppButtonType.text, super(key: key);

  @override
  Widget build(BuildContext context) {
    final buttonConfig = _getButtonConfig();
    final sizeConfig = _getSizeConfig();
    
    Widget button;
    
    switch (type) {
      case AppButtonType.primary:
      case AppButtonType.success:
      case AppButtonType.warning:
      case AppButtonType.danger:
      case AppButtonType.ai:
        button = _buildElevatedButton(buttonConfig, sizeConfig);
        break;
      case AppButtonType.secondary:
        button = _buildOutlinedButton(buttonConfig, sizeConfig);
        break;
      case AppButtonType.text:
        button = _buildTextButton(buttonConfig, sizeConfig);
        break;
    }

    if (isFullWidth) {
      return SizedBox(
        width: double.infinity,
        child: button,
      );
    }

    return button;
  }

  /// 构建填充按钮
  Widget _buildElevatedButton(_ButtonConfig config, _SizeConfig sizeConfig) {
    return Container(
      decoration: type == AppButtonType.ai ? _buildAiGradient() : null,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: type == AppButtonType.ai ? Colors.transparent : config.backgroundColor,
          foregroundColor: config.foregroundColor,
          elevation: config.elevation,
          shadowColor: config.shadowColor,
          padding: padding ?? sizeConfig.padding,
          minimumSize: sizeConfig.minimumSize,
          shape: RoundedRectangleBorder(
            borderRadius: borderRadius ?? BorderRadius.circular(sizeConfig.borderRadius),
          ),
          textStyle: TextStyle(
            fontSize: sizeConfig.fontSize,
            fontWeight: AppTheme.fontMedium,
          ),
        ).copyWith(
          backgroundColor: MaterialStateProperty.resolveWith((states) {
            if (type == AppButtonType.ai) return Colors.transparent;
            if (states.contains(MaterialState.disabled)) return AppTheme.gray300;
            if (states.contains(MaterialState.hovered)) return config.hoverColor;
            if (states.contains(MaterialState.pressed)) return config.pressedColor;
            return config.backgroundColor;
          }),
          elevation: MaterialStateProperty.resolveWith((states) {
            if (states.contains(MaterialState.disabled)) return 0;
            if (states.contains(MaterialState.hovered)) return config.elevation + 2;
            if (states.contains(MaterialState.pressed)) return config.elevation - 1;
            return config.elevation;
          }),
        ),
        child: _buildButtonContent(config, sizeConfig),
      ),
    );
  }

  /// 构建边框按钮
  Widget _buildOutlinedButton(_ButtonConfig config, _SizeConfig sizeConfig) {
    return OutlinedButton(
      onPressed: isLoading ? null : onPressed,
      style: OutlinedButton.styleFrom(
        foregroundColor: config.foregroundColor,
        side: BorderSide(color: config.borderColor!, width: 1.5),
        padding: padding ?? sizeConfig.padding,
        minimumSize: sizeConfig.minimumSize,
        shape: RoundedRectangleBorder(
          borderRadius: borderRadius ?? BorderRadius.circular(sizeConfig.borderRadius),
        ),
        textStyle: TextStyle(
          fontSize: sizeConfig.fontSize,
          fontWeight: AppTheme.fontMedium,
        ),
      ).copyWith(
        foregroundColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.disabled)) return AppTheme.gray400;
          if (states.contains(MaterialState.hovered)) return config.hoverColor;
          if (states.contains(MaterialState.pressed)) return config.pressedColor;
          return config.foregroundColor;
        }),
        side: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.disabled)) return BorderSide(color: AppTheme.gray300, width: 1.5);
          if (states.contains(MaterialState.hovered)) return BorderSide(color: config.hoverColor!, width: 1.5);
          if (states.contains(MaterialState.pressed)) return BorderSide(color: config.pressedColor!, width: 1.5);
          return BorderSide(color: config.borderColor!, width: 1.5);
        }),
      ),
      child: _buildButtonContent(config, sizeConfig),
    );
  }

  /// 构建文本按钮
  Widget _buildTextButton(_ButtonConfig config, _SizeConfig sizeConfig) {
    return TextButton(
      onPressed: isLoading ? null : onPressed,
      style: TextButton.styleFrom(
        foregroundColor: config.foregroundColor,
        padding: padding ?? sizeConfig.padding,
        minimumSize: sizeConfig.minimumSize,
        shape: RoundedRectangleBorder(
          borderRadius: borderRadius ?? BorderRadius.circular(sizeConfig.borderRadius),
        ),
        textStyle: TextStyle(
          fontSize: sizeConfig.fontSize,
          fontWeight: AppTheme.fontMedium,
        ),
      ),
      child: _buildButtonContent(config, sizeConfig),
    );
  }

  /// 构建按钮内容
  Widget _buildButtonContent(_ButtonConfig config, _SizeConfig sizeConfig) {
    if (isLoading) {
      return SizedBox(
        height: sizeConfig.fontSize + 4,
        width: sizeConfig.fontSize + 4,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(config.foregroundColor),
        ),
      );
    }

    if (icon != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          icon!,
          SizedBox(width: AppTheme.space2),
          Text(text),
        ],
      );
    }

    return Text(text);
  }

  /// AI按钮渐变背景
  BoxDecoration _buildAiGradient() {
    return BoxDecoration(
      gradient: LinearGradient(
        colors: [AppTheme.purple500, AppTheme.purple600],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      borderRadius: borderRadius ?? BorderRadius.circular(_getSizeConfig().borderRadius),
      boxShadow: AppTheme.shadowMd,
    );
  }

  /// 获取按钮配置
  _ButtonConfig _getButtonConfig() {
    switch (type) {
      case AppButtonType.primary:
        return _ButtonConfig(
          backgroundColor: AppTheme.primary500,
          foregroundColor: Colors.white,
          hoverColor: AppTheme.primary600,
          pressedColor: AppTheme.primary700,
          elevation: 2,
          shadowColor: AppTheme.shadowLight,
        );
      case AppButtonType.secondary:
        return _ButtonConfig(
          backgroundColor: Colors.transparent,
          foregroundColor: AppTheme.primary500,
          borderColor: AppTheme.borderDefault,
          hoverColor: AppTheme.primary600,
          pressedColor: AppTheme.primary700,
          elevation: 0,
        );
      case AppButtonType.success:
        return _ButtonConfig(
          backgroundColor: AppTheme.secondary500,
          foregroundColor: Colors.white,
          hoverColor: AppTheme.secondary600,
          pressedColor: AppTheme.secondary700,
          elevation: 2,
          shadowColor: AppTheme.shadowLight,
        );
      case AppButtonType.warning:
        return _ButtonConfig(
          backgroundColor: AppTheme.accent500,
          foregroundColor: Colors.white,
          hoverColor: AppTheme.accent600,
          pressedColor: AppTheme.accent700,
          elevation: 2,
          shadowColor: AppTheme.shadowLight,
        );
      case AppButtonType.danger:
        return _ButtonConfig(
          backgroundColor: AppTheme.error500,
          foregroundColor: Colors.white,
          hoverColor: AppTheme.error600,
          pressedColor: AppTheme.error700,
          elevation: 2,
          shadowColor: AppTheme.shadowLight,
        );
      case AppButtonType.ai:
        return _ButtonConfig(
          backgroundColor: Colors.transparent,
          foregroundColor: Colors.white,
          hoverColor: AppTheme.purple600,
          pressedColor: AppTheme.purple700,
          elevation: 4,
          shadowColor: AppTheme.shadowLight,
        );
      case AppButtonType.text:
        return _ButtonConfig(
          backgroundColor: Colors.transparent,
          foregroundColor: AppTheme.primary500,
          hoverColor: AppTheme.primary600,
          pressedColor: AppTheme.primary700,
          elevation: 0,
        );
    }
  }

  /// 获取尺寸配置
  _SizeConfig _getSizeConfig() {
    switch (size) {
      case AppButtonSize.small:
        return _SizeConfig(
          padding: EdgeInsets.symmetric(
            horizontal: AppTheme.space4,
            vertical: AppTheme.space2,
          ),
          minimumSize: Size(64, 32),
          fontSize: AppTheme.textSm,
          borderRadius: AppTheme.radiusMd,
        );
      case AppButtonSize.medium:
        return _SizeConfig(
          padding: EdgeInsets.symmetric(
            horizontal: AppTheme.space6,
            vertical: AppTheme.space3,
          ),
          minimumSize: Size(88, 44),
          fontSize: AppTheme.textBase,
          borderRadius: AppTheme.radiusLg,
        );
      case AppButtonSize.large:
        return _SizeConfig(
          padding: EdgeInsets.symmetric(
            horizontal: AppTheme.space8,
            vertical: AppTheme.space4,
          ),
          minimumSize: Size(120, 52),
          fontSize: AppTheme.textLg,
          borderRadius: AppTheme.radiusXl,
        );
    }
  }
}

/// 按钮类型枚举
enum AppButtonType {
  primary,    // 主要按钮
  secondary,  // 次要按钮
  success,    // 成功按钮
  warning,    // 警告按钮
  danger,     // 危险按钮
  ai,         // AI智能按钮
  text,       // 文本按钮
}

/// 按钮尺寸枚举
enum AppButtonSize {
  small,   // 小尺寸
  medium,  // 中等尺寸
  large,   // 大尺寸
}

/// 按钮配置类
class _ButtonConfig {
  final Color backgroundColor;
  final Color foregroundColor;
  final Color? borderColor;
  final Color? hoverColor;
  final Color? pressedColor;
  final double elevation;
  final Color? shadowColor;

  const _ButtonConfig({
    required this.backgroundColor,
    required this.foregroundColor,
    this.borderColor,
    this.hoverColor,
    this.pressedColor,
    required this.elevation,
    this.shadowColor,
  });
}

/// 尺寸配置类
class _SizeConfig {
  final EdgeInsetsGeometry padding;
  final Size minimumSize;
  final double fontSize;
  final double borderRadius;

  const _SizeConfig({
    required this.padding,
    required this.minimumSize,
    required this.fontSize,
    required this.borderRadius,
  });
}