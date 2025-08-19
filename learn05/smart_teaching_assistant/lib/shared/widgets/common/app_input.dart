import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../themes/app_theme.dart';

/// 智能教学助手 - 统一输入框组件
/// 基于UI 2.0设计规范，提供多种输入框样式和功能
class AppInput extends StatefulWidget {
  final String? label;
  final String? placeholder;
  final String? helperText;
  final String? errorText;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final TextEditingController? controller;
  final ValueChanged<String>? onChanged;
  final VoidCallback? onTap;
  final ValueChanged<String>? onSubmitted;
  final FocusNode? focusNode;
  final TextInputType? keyboardType;
  final List<TextInputFormatter>? inputFormatters;
  final bool obscureText;
  final bool enabled;
  final bool readOnly;
  final int? maxLines;
  final int? minLines;
  final int? maxLength;
  final TextCapitalization textCapitalization;
  final TextInputAction? textInputAction;
  final String? initialValue;
  final FormFieldValidator<String>? validator;
  final AutovalidateMode? autovalidateMode;
  final AppInputType type;
  final AppInputSize size;
  final bool showCounter;
  final EdgeInsetsGeometry? contentPadding;
  final Color? fillColor;
  final Color? borderColor;
  final double? borderRadius;

  const AppInput({
    Key? key,
    this.label,
    this.placeholder,
    this.helperText,
    this.errorText,
    this.prefixIcon,
    this.suffixIcon,
    this.controller,
    this.onChanged,
    this.onTap,
    this.onSubmitted,
    this.focusNode,
    this.keyboardType,
    this.inputFormatters,
    this.obscureText = false,
    this.enabled = true,
    this.readOnly = false,
    this.maxLines = 1,
    this.minLines,
    this.maxLength,
    this.textCapitalization = TextCapitalization.none,
    this.textInputAction,
    this.initialValue,
    this.validator,
    this.autovalidateMode,
    this.type = AppInputType.outlined,
    this.size = AppInputSize.medium,
    this.showCounter = false,
    this.contentPadding,
    this.fillColor,
    this.borderColor,
    this.borderRadius,
  }) : super(key: key);

  /// 搜索输入框
  const AppInput.search({
    Key? key,
    this.placeholder = '搜索...',
    this.controller,
    this.onChanged,
    this.onSubmitted,
    this.focusNode,
    this.enabled = true,
    this.size = AppInputSize.medium,
    this.contentPadding,
    this.fillColor,
    this.borderRadius,
  }) : label = null,
       helperText = null,
       errorText = null,
       prefixIcon = const Icon(Icons.search),
       suffixIcon = null,
       onTap = null,
       keyboardType = TextInputType.text,
       inputFormatters = null,
       obscureText = false,
       readOnly = false,
       maxLines = 1,
       minLines = null,
       maxLength = null,
       textCapitalization = TextCapitalization.none,
       textInputAction = TextInputAction.search,
       initialValue = null,
       validator = null,
       autovalidateMode = null,
       type = AppInputType.filled,
       showCounter = false,
       borderColor = null,
       super(key: key);

  @override
  State<AppInput> createState() => _AppInputState();
}

class _AppInputState extends State<AppInput> {
  late bool _obscureText;
  late FocusNode _focusNode;
  bool _isFocused = false;

  @override
  void initState() {
    super.initState();
    _obscureText = widget.obscureText;
    _focusNode = widget.focusNode ?? FocusNode();
    _focusNode.addListener(_onFocusChange);
  }

  @override
  void dispose() {
    if (widget.focusNode == null) {
      _focusNode.dispose();
    } else {
      _focusNode.removeListener(_onFocusChange);
    }
    super.dispose();
  }

  void _onFocusChange() {
    setState(() {
      _isFocused = _focusNode.hasFocus;
    });
  }

  void _toggleObscureText() {
    setState(() {
      _obscureText = !_obscureText;
    });
  }

  @override
  Widget build(BuildContext context) {
    final inputConfig = _getInputConfig();
    final hasError = widget.errorText != null && widget.errorText!.isNotEmpty;
    
    Widget? suffixIcon = widget.suffixIcon;
    
    // 密码输入框的显示/隐藏切换按钮
    if (widget.obscureText) {
      suffixIcon = IconButton(
        icon: Icon(
          _obscureText ? Icons.visibility_off : Icons.visibility,
          color: _isFocused ? AppTheme.primary500 : AppTheme.textSecondary,
        ),
        onPressed: _toggleObscureText,
        splashRadius: 20,
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 标签
        if (widget.label != null) ...[
          Text(
            widget.label!,
            style: TextStyle(
              fontSize: inputConfig.labelFontSize,
              fontWeight: AppTheme.fontMedium,
              color: hasError ? AppTheme.error500 : AppTheme.textPrimary,
              height: AppTheme.leadingTight,
            ),
          ),
          SizedBox(height: AppTheme.space2),
        ],
        
        // 输入框
        TextFormField(
          controller: widget.controller,
          focusNode: _focusNode,
          initialValue: widget.initialValue,
          decoration: _buildInputDecoration(inputConfig, hasError, suffixIcon),
          style: TextStyle(
            fontSize: inputConfig.fontSize,
            fontWeight: AppTheme.fontNormal,
            color: widget.enabled ? AppTheme.textPrimary : AppTheme.textTertiary,
            height: AppTheme.leadingNormal,
          ),
          obscureText: _obscureText,
          enabled: widget.enabled,
          readOnly: widget.readOnly,
          maxLines: widget.maxLines,
          minLines: widget.minLines,
          maxLength: widget.maxLength,
          keyboardType: widget.keyboardType,
          textInputAction: widget.textInputAction,
          textCapitalization: widget.textCapitalization,
          inputFormatters: widget.inputFormatters,
          validator: widget.validator,
          autovalidateMode: widget.autovalidateMode,
          onChanged: widget.onChanged,
          onTap: widget.onTap,
          onFieldSubmitted: widget.onSubmitted,
          buildCounter: widget.showCounter ? null : (_, {required currentLength, required isFocused, maxLength}) => null,
        ),
        
        // 帮助文本或错误文本
        if (widget.helperText != null || widget.errorText != null) ...[
          SizedBox(height: AppTheme.space1),
          Text(
            widget.errorText ?? widget.helperText!,
            style: TextStyle(
              fontSize: AppTheme.textSm,
              fontWeight: AppTheme.fontNormal,
              color: hasError ? AppTheme.error500 : AppTheme.textSecondary,
              height: AppTheme.leadingTight,
            ),
          ),
        ],
      ],
    );
  }

  /// 构建输入框装饰
  InputDecoration _buildInputDecoration(_InputConfig config, bool hasError, Widget? suffixIcon) {
    final borderColor = hasError 
        ? AppTheme.error500 
        : _isFocused 
            ? AppTheme.primary500 
            : widget.borderColor ?? config.borderColor;
    
    final fillColor = widget.fillColor ?? config.fillColor;
    
    switch (widget.type) {
      case AppInputType.outlined:
        return InputDecoration(
          hintText: widget.placeholder,
          hintStyle: TextStyle(
            fontSize: config.fontSize,
            fontWeight: AppTheme.fontNormal,
            color: AppTheme.textPlaceholder,
          ),
          prefixIcon: widget.prefixIcon,
          suffixIcon: suffixIcon,
          filled: fillColor != null,
          fillColor: fillColor,
          contentPadding: widget.contentPadding ?? config.contentPadding,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide(
              color: config.borderColor,
              width: config.borderWidth,
            ),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide(
              color: config.borderColor,
              width: config.borderWidth,
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide(
              color: borderColor,
              width: config.focusedBorderWidth,
            ),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide(
              color: AppTheme.error500,
              width: config.borderWidth,
            ),
          ),
          focusedErrorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide(
              color: AppTheme.error500,
              width: config.focusedBorderWidth,
            ),
          ),
          disabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide(
              color: AppTheme.borderLight,
              width: config.borderWidth,
            ),
          ),
        );
        
      case AppInputType.filled:
        return InputDecoration(
          hintText: widget.placeholder,
          hintStyle: TextStyle(
            fontSize: config.fontSize,
            fontWeight: AppTheme.fontNormal,
            color: AppTheme.textPlaceholder,
          ),
          prefixIcon: widget.prefixIcon,
          suffixIcon: suffixIcon,
          filled: true,
          fillColor: fillColor,
          contentPadding: widget.contentPadding ?? config.contentPadding,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide.none,
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide(
              color: borderColor,
              width: config.focusedBorderWidth,
            ),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide(
              color: AppTheme.error500,
              width: config.borderWidth,
            ),
          ),
          focusedErrorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(widget.borderRadius ?? config.borderRadius),
            borderSide: BorderSide(
              color: AppTheme.error500,
              width: config.focusedBorderWidth,
            ),
          ),
        );
        
      case AppInputType.underlined:
        return InputDecoration(
          hintText: widget.placeholder,
          hintStyle: TextStyle(
            fontSize: config.fontSize,
            fontWeight: AppTheme.fontNormal,
            color: AppTheme.textPlaceholder,
          ),
          prefixIcon: widget.prefixIcon,
          suffixIcon: suffixIcon,
          filled: fillColor != null,
          fillColor: fillColor,
          contentPadding: widget.contentPadding ?? config.contentPadding,
          border: UnderlineInputBorder(
            borderSide: BorderSide(
              color: config.borderColor,
              width: config.borderWidth,
            ),
          ),
          enabledBorder: UnderlineInputBorder(
            borderSide: BorderSide(
              color: config.borderColor,
              width: config.borderWidth,
            ),
          ),
          focusedBorder: UnderlineInputBorder(
            borderSide: BorderSide(
              color: borderColor,
              width: config.focusedBorderWidth,
            ),
          ),
          errorBorder: UnderlineInputBorder(
            borderSide: BorderSide(
              color: AppTheme.error500,
              width: config.borderWidth,
            ),
          ),
          focusedErrorBorder: UnderlineInputBorder(
            borderSide: BorderSide(
              color: AppTheme.error500,
              width: config.focusedBorderWidth,
            ),
          ),
          disabledBorder: UnderlineInputBorder(
            borderSide: BorderSide(
              color: AppTheme.borderLight,
              width: config.borderWidth,
            ),
          ),
        );
    }
  }

  /// 获取输入框配置
  _InputConfig _getInputConfig() {
    switch (widget.size) {
      case AppInputSize.small:
        return _InputConfig(
          fontSize: AppTheme.textSm,
          labelFontSize: AppTheme.textSm,
          contentPadding: EdgeInsets.symmetric(
            horizontal: AppTheme.space3,
            vertical: AppTheme.space2,
          ),
          borderRadius: AppTheme.radiusMd,
          borderWidth: 1,
          focusedBorderWidth: 2,
          borderColor: AppTheme.borderDefault,
          fillColor: widget.type == AppInputType.filled ? AppTheme.gray50 : null,
        );
      case AppInputSize.medium:
        return _InputConfig(
          fontSize: AppTheme.textBase,
          labelFontSize: AppTheme.textBase,
          contentPadding: EdgeInsets.symmetric(
            horizontal: AppTheme.space4,
            vertical: AppTheme.space3,
          ),
          borderRadius: AppTheme.radiusLg,
          borderWidth: 1,
          focusedBorderWidth: 2,
          borderColor: AppTheme.borderDefault,
          fillColor: widget.type == AppInputType.filled ? AppTheme.gray50 : null,
        );
      case AppInputSize.large:
        return _InputConfig(
          fontSize: AppTheme.textLg,
          labelFontSize: AppTheme.textLg,
          contentPadding: EdgeInsets.symmetric(
            horizontal: AppTheme.space6,
            vertical: AppTheme.space4,
          ),
          borderRadius: AppTheme.radiusXl,
          borderWidth: 1.5,
          focusedBorderWidth: 2.5,
          borderColor: AppTheme.borderDefault,
          fillColor: widget.type == AppInputType.filled ? AppTheme.gray50 : null,
        );
    }
  }
}

/// 输入框类型枚举
enum AppInputType {
  outlined,   // 边框输入框
  filled,     // 填充输入框
  underlined, // 下划线输入框
}

/// 输入框尺寸枚举
enum AppInputSize {
  small,   // 小尺寸
  medium,  // 中等尺寸
  large,   // 大尺寸
}

/// 输入框配置类
class _InputConfig {
  final double fontSize;
  final double labelFontSize;
  final EdgeInsetsGeometry contentPadding;
  final double borderRadius;
  final double borderWidth;
  final double focusedBorderWidth;
  final Color borderColor;
  final Color? fillColor;

  const _InputConfig({
    required this.fontSize,
    required this.labelFontSize,
    required this.contentPadding,
    required this.borderRadius,
    required this.borderWidth,
    required this.focusedBorderWidth,
    required this.borderColor,
    this.fillColor,
  });
}