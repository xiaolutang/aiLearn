import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_text_styles.dart';
import '../../core/constants/app_dimensions.dart';

/// 自定义按钮组件
/// 
/// 提供统一的按钮样式和功能，包括：
/// - 多种按钮类型（主要、次要、文本、轮廓）
/// - 多种尺寸（小、中、大）
/// - 加载状态显示
/// - 禁用状态
/// - 图标支持
/// - 响应式设计
class CustomButton extends StatefulWidget {
  /// 按钮文本
  final String text;
  
  /// 点击回调
  final VoidCallback? onPressed;
  
  /// 按钮类型
  final ButtonType type;
  
  /// 按钮尺寸
  final ButtonSize size;
  
  /// 是否显示加载状态
  final bool isLoading;
  
  /// 是否启用
  final bool enabled;
  
  /// 按钮宽度
  final double? width;
  
  /// 按钮高度
  final double? height;
  
  /// 前缀图标
  final IconData? prefixIcon;
  
  /// 后缀图标
  final IconData? suffixIcon;
  
  /// 自定义颜色
  final Color? backgroundColor;
  
  /// 自定义文本颜色
  final Color? textColor;
  
  /// 自定义边框颜色
  final Color? borderColor;
  
  /// 圆角半径
  final double? borderRadius;
  
  /// 内边距
  final EdgeInsets? padding;
  
  /// 外边距
  final EdgeInsets? margin;
  
  /// 阴影高度
  final double? elevation;
  
  /// 文本样式
  final TextStyle? textStyle;
  
  /// 加载指示器颜色
  final Color? loadingColor;
  
  /// 加载指示器大小
  final double? loadingSize;
  
  /// 是否展开填充父容器
  final bool expanded;
  
  /// 按钮形状
  final ButtonShape shape;
  
  const CustomButton({
    super.key,
    required this.text,
    this.onPressed,
    this.type = ButtonType.primary,
    this.size = ButtonSize.medium,
    this.isLoading = false,
    this.enabled = true,
    this.width,
    this.height,
    this.prefixIcon,
    this.suffixIcon,
    this.backgroundColor,
    this.textColor,
    this.borderColor,
    this.borderRadius,
    this.padding,
    this.margin,
    this.elevation,
    this.textStyle,
    this.loadingColor,
    this.loadingSize,
    this.expanded = false,
    this.shape = ButtonShape.rounded,
  });

  @override
  State<CustomButton> createState() => _CustomButtonState();
}

class _CustomButtonState extends State<CustomButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 100),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    if (_isEnabled) {
      setState(() {
        _isPressed = true;
      });
      _animationController.forward();
    }
  }

  void _onTapUp(TapUpDetails details) {
    _resetPressState();
  }

  void _onTapCancel() {
    _resetPressState();
  }

  void _resetPressState() {
    if (_isPressed) {
      setState(() {
        _isPressed = false;
      });
      _animationController.reverse();
    }
  }

  bool get _isEnabled => widget.enabled && !widget.isLoading && widget.onPressed != null;

  @override
  Widget build(BuildContext context) {
    Widget button = AnimatedBuilder(
      animation: _scaleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: _buildButton(),
        );
      },
    );

    if (widget.margin != null) {
      button = Padding(
        padding: widget.margin!,
        child: button,
      );
    }

    if (widget.expanded) {
      button = SizedBox(
        width: double.infinity,
        child: button,
      );
    }

    return button;
  }

  Widget _buildButton() {
    final buttonStyle = _getButtonStyle();
    
    return GestureDetector(
      onTapDown: _onTapDown,
      onTapUp: _onTapUp,
      onTapCancel: _onTapCancel,
      child: Container(
        width: widget.width,
        height: widget.height ?? _getHeight(),
        decoration: _getDecoration(),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: _isEnabled ? widget.onPressed : null,
            borderRadius: BorderRadius.circular(_getBorderRadius()),
            child: Container(
              padding: widget.padding ?? _getPadding(),
              child: _buildContent(),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildContent() {
    if (widget.isLoading) {
      return _buildLoadingContent();
    }

    final children = <Widget>[];
    
    if (widget.prefixIcon != null) {
      children.add(Icon(
        widget.prefixIcon,
        size: _getIconSize(),
        color: _getTextColor(),
      ));
      children.add(SizedBox(width: _getIconSpacing()));
    }
    
    children.add(Flexible(
      child: Text(
        widget.text,
        style: _getTextStyle(),
        textAlign: TextAlign.center,
        overflow: TextOverflow.ellipsis,
      ),
    ));
    
    if (widget.suffixIcon != null) {
      children.add(SizedBox(width: _getIconSpacing()));
      children.add(Icon(
        widget.suffixIcon,
        size: _getIconSize(),
        color: _getTextColor(),
      ));
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      mainAxisSize: MainAxisSize.min,
      children: children,
    );
  }

  Widget _buildLoadingContent() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: widget.loadingSize ?? _getLoadingSize(),
          height: widget.loadingSize ?? _getLoadingSize(),
          child: CircularProgressIndicator(
            strokeWidth: 2.0,
            valueColor: AlwaysStoppedAnimation<Color>(
              widget.loadingColor ?? _getTextColor(),
            ),
          ),
        ),
        SizedBox(width: _getIconSpacing()),
        Text(
          '加载中...',
          style: _getTextStyle(),
        ),
      ],
    );
  }

  ButtonStyle _getButtonStyle() {
    return ButtonStyle(
      backgroundColor: MaterialStateProperty.resolveWith<Color>(
        (Set<MaterialState> states) {
          if (states.contains(MaterialState.disabled)) {
            return AppColors.buttonDisabled;
          }
          return _getBackgroundColor();
        },
      ),
      foregroundColor: MaterialStateProperty.all<Color>(_getTextColor()),
      elevation: MaterialStateProperty.all<double>(widget.elevation ?? _getElevation()),
      shape: MaterialStateProperty.all<RoundedRectangleBorder>(
        RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(_getBorderRadius()),
          side: _getBorderSide(),
        ),
      ),
      padding: MaterialStateProperty.all<EdgeInsets>(
        widget.padding ?? _getPadding(),
      ),
      minimumSize: MaterialStateProperty.all<Size>(
        Size(widget.width ?? 0, widget.height ?? _getHeight()),
      ),
    );
  }

  Decoration _getDecoration() {
    return BoxDecoration(
      color: _isEnabled ? _getBackgroundColor() : AppColors.buttonDisabled,
      borderRadius: BorderRadius.circular(_getBorderRadius()),
      border: _getBorder(),
      boxShadow: _getBoxShadow(),
    );
  }

  Color _getBackgroundColor() {
    if (widget.backgroundColor != null) {
      return widget.backgroundColor!;
    }
    
    switch (widget.type) {
      case ButtonType.primary:
        return AppColors.buttonPrimary;
      case ButtonType.secondary:
        return AppColors.buttonSecondary;
      case ButtonType.outline:
        return Colors.transparent;
      case ButtonType.text:
        return Colors.transparent;
      case ButtonType.danger:
        return AppColors.error;
      case ButtonType.success:
        return AppColors.success;
      case ButtonType.warning:
        return AppColors.warning;
    }
  }

  Color _getTextColor() {
    if (widget.textColor != null) {
      return widget.textColor!;
    }
    
    if (!_isEnabled) {
      return AppColors.textDisabled;
    }
    
    switch (widget.type) {
      case ButtonType.primary:
      case ButtonType.danger:
      case ButtonType.success:
      case ButtonType.warning:
        return AppColors.buttonText;
      case ButtonType.secondary:
      case ButtonType.outline:
      case ButtonType.text:
        return AppColors.buttonTextSecondary;
    }
  }

  TextStyle _getTextStyle() {
    final baseStyle = widget.textStyle ?? _getBaseTextStyle();
    return baseStyle.copyWith(
      color: _getTextColor(),
      fontWeight: FontWeight.w600,
    );
  }

  TextStyle _getBaseTextStyle() {
    switch (widget.size) {
      case ButtonSize.small:
        return AppTextStyles.buttonSmall;
      case ButtonSize.medium:
        return AppTextStyles.buttonMedium;
      case ButtonSize.large:
        return AppTextStyles.buttonLarge;
    }
  }

  double _getHeight() {
    switch (widget.size) {
      case ButtonSize.small:
        return AppDimensions.buttonHeightSmall;
      case ButtonSize.medium:
        return AppDimensions.buttonHeightMedium;
      case ButtonSize.large:
        return AppDimensions.buttonHeightLarge;
    }
  }

  EdgeInsets _getPadding() {
    switch (widget.size) {
      case ButtonSize.small:
        return const EdgeInsets.symmetric(
          horizontal: AppDimensions.paddingSmall,
          vertical: AppDimensions.paddingTiny,
        );
      case ButtonSize.medium:
        return const EdgeInsets.symmetric(
          horizontal: AppDimensions.paddingMedium,
          vertical: AppDimensions.paddingSmall,
        );
      case ButtonSize.large:
        return const EdgeInsets.symmetric(
          horizontal: AppDimensions.paddingLarge,
          vertical: AppDimensions.paddingMedium,
        );
    }
  }

  double _getBorderRadius() {
    if (widget.borderRadius != null) {
      return widget.borderRadius!;
    }
    
    switch (widget.shape) {
      case ButtonShape.rectangular:
        return 0;
      case ButtonShape.rounded:
        return AppDimensions.radiusMedium;
      case ButtonShape.circular:
        return _getHeight() / 2;
    }
  }

  BorderSide _getBorderSide() {
    if (widget.type == ButtonType.outline) {
      return BorderSide(
        color: widget.borderColor ?? AppColors.primary,
        width: AppDimensions.borderWidthNormal,
      );
    }
    return BorderSide.none;
  }

  Border? _getBorder() {
    if (widget.type == ButtonType.outline) {
      return Border.all(
        color: widget.borderColor ?? AppColors.primary,
        width: AppDimensions.borderWidthNormal,
      );
    }
    return null;
  }

  double _getElevation() {
    if (widget.type == ButtonType.text || widget.type == ButtonType.outline) {
      return 0;
    }
    return AppDimensions.elevationLow;
  }

  List<BoxShadow>? _getBoxShadow() {
    if (widget.type == ButtonType.text || widget.type == ButtonType.outline) {
      return null;
    }
    
    if (!_isEnabled) {
      return null;
    }
    
    return [
      BoxShadow(
        color: AppColors.shadow,
        offset: const Offset(0, 2),
        blurRadius: AppDimensions.blurRadiusSmall,
        spreadRadius: 0,
      ),
    ];
  }

  double _getIconSize() {
    switch (widget.size) {
      case ButtonSize.small:
        return AppDimensions.iconSizeSmall;
      case ButtonSize.medium:
        return AppDimensions.iconSizeMedium;
      case ButtonSize.large:
        return AppDimensions.iconSizeLarge;
    }
  }

  double _getIconSpacing() {
    switch (widget.size) {
      case ButtonSize.small:
        return AppDimensions.spacingTiny;
      case ButtonSize.medium:
        return AppDimensions.spacingSmall;
      case ButtonSize.large:
        return AppDimensions.spacingSmall;
    }
  }

  double _getLoadingSize() {
    switch (widget.size) {
      case ButtonSize.small:
        return 14;
      case ButtonSize.medium:
        return 16;
      case ButtonSize.large:
        return 18;
    }
  }
}

/// 按钮类型枚举
enum ButtonType {
  primary,    // 主要按钮
  secondary,  // 次要按钮
  outline,    // 轮廓按钮
  text,       // 文本按钮
  danger,     // 危险按钮
  success,    // 成功按钮
  warning,    // 警告按钮
}

/// 按钮尺寸枚举
enum ButtonSize {
  small,
  medium,
  large,
}

/// 按钮形状枚举
enum ButtonShape {
  rectangular, // 矩形
  rounded,     // 圆角
  circular,    // 圆形
}

/// 预定义的按钮样式
class ButtonStyles {
  static const CustomButton primary = CustomButton(
    text: '',
    type: ButtonType.primary,
  );
  
  static const CustomButton secondary = CustomButton(
    text: '',
    type: ButtonType.secondary,
  );
  
  static const CustomButton outline = CustomButton(
    text: '',
    type: ButtonType.outline,
  );
  
  static const CustomButton text = CustomButton(
    text: '',
    type: ButtonType.text,
  );
  
  static const CustomButton danger = CustomButton(
    text: '',
    type: ButtonType.danger,
  );
  
  static const CustomButton success = CustomButton(
    text: '',
    type: ButtonType.success,
  );
  
  static const CustomButton warning = CustomButton(
    text: '',
    type: ButtonType.warning,
  );
}