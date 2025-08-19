import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_text_styles.dart';
import '../../core/constants/app_dimensions.dart';

/// 自定义文本输入框组件
/// 
/// 提供统一的文本输入框样式和功能，包括：
/// - 标签和提示文本
/// - 前缀和后缀图标
/// - 验证和错误显示
/// - 密码显示/隐藏
/// - 多种输入类型支持
/// - 响应式设计
class CustomTextField extends StatefulWidget {
  /// 文本控制器
  final TextEditingController? controller;
  
  /// 标签文本
  final String? labelText;
  
  /// 提示文本
  final String? hintText;
  
  /// 帮助文本
  final String? helperText;
  
  /// 前缀图标
  final IconData? prefixIcon;
  
  /// 后缀图标
  final Widget? suffixIcon;
  
  /// 是否隐藏文本（密码输入）
  final bool obscureText;
  
  /// 键盘类型
  final TextInputType? keyboardType;
  
  /// 文本输入动作
  final TextInputAction? textInputAction;
  
  /// 验证函数
  final String? Function(String?)? validator;
  
  /// 值变化回调
  final void Function(String)? onChanged;
  
  /// 提交回调
  final void Function(String)? onSubmitted;
  
  /// 焦点变化回调
  final void Function(bool)? onFocusChanged;
  
  /// 是否启用
  final bool enabled;
  
  /// 是否只读
  final bool readOnly;
  
  /// 最大行数
  final int? maxLines;
  
  /// 最小行数
  final int? minLines;
  
  /// 最大长度
  final int? maxLength;
  
  /// 输入格式化器
  final List<TextInputFormatter>? inputFormatters;
  
  /// 自动焦点
  final bool autofocus;
  
  /// 自动填充提示
  final Iterable<String>? autofillHints;
  
  /// 文本对齐方式
  final TextAlign textAlign;
  
  /// 文本样式
  final TextStyle? textStyle;
  
  /// 填充颜色
  final Color? fillColor;
  
  /// 边框颜色
  final Color? borderColor;
  
  /// 聚焦边框颜色
  final Color? focusedBorderColor;
  
  /// 错误边框颜色
  final Color? errorBorderColor;
  
  /// 圆角半径
  final double? borderRadius;
  
  /// 内容内边距
  final EdgeInsets? contentPadding;
  
  /// 是否显示边框
  final bool showBorder;
  
  /// 是否填充背景
  final bool filled;
  
  /// 尺寸大小
  final TextFieldSize size;
  
  const CustomTextField({
    super.key,
    this.controller,
    this.labelText,
    this.hintText,
    this.helperText,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.keyboardType,
    this.textInputAction,
    this.validator,
    this.onChanged,
    this.onSubmitted,
    this.onFocusChanged,
    this.enabled = true,
    this.readOnly = false,
    this.maxLines = 1,
    this.minLines,
    this.maxLength,
    this.inputFormatters,
    this.autofocus = false,
    this.autofillHints,
    this.textAlign = TextAlign.start,
    this.textStyle,
    this.fillColor,
    this.borderColor,
    this.focusedBorderColor,
    this.errorBorderColor,
    this.borderRadius,
    this.contentPadding,
    this.showBorder = true,
    this.filled = true,
    this.size = TextFieldSize.medium,
  });

  @override
  State<CustomTextField> createState() => _CustomTextFieldState();
}

class _CustomTextFieldState extends State<CustomTextField> {
  late FocusNode _focusNode;
  bool _isFocused = false;
  String? _errorText;

  @override
  void initState() {
    super.initState();
    _focusNode = FocusNode();
    _focusNode.addListener(_onFocusChanged);
  }

  @override
  void dispose() {
    _focusNode.removeListener(_onFocusChanged);
    _focusNode.dispose();
    super.dispose();
  }

  void _onFocusChanged() {
    setState(() {
      _isFocused = _focusNode.hasFocus;
    });
    widget.onFocusChanged?.call(_isFocused);
  }

  void _onChanged(String value) {
    // 实时验证
    if (widget.validator != null) {
      setState(() {
        _errorText = widget.validator!(value);
      });
    }
    widget.onChanged?.call(value);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (widget.labelText != null) ..._buildLabel(),
        _buildTextField(),
        if (widget.helperText != null || _errorText != null) ..._buildHelperText(),
      ],
    );
  }

  List<Widget> _buildLabel() {
    return [
      Text(
        widget.labelText!,
        style: AppTextStyles.labelMedium.copyWith(
          color: _isFocused 
              ? widget.focusedBorderColor ?? AppColors.primary
              : AppColors.textSecondary,
          fontWeight: _isFocused ? FontWeight.w600 : FontWeight.w500,
        ),
      ),
      const SizedBox(height: AppDimensions.spacingSmall),
    ];
  }

  Widget _buildTextField() {
    final hasError = _errorText != null;
    
    return TextFormField(
      controller: widget.controller,
      focusNode: _focusNode,
      obscureText: widget.obscureText,
      keyboardType: widget.keyboardType,
      textInputAction: widget.textInputAction,
      onChanged: _onChanged,
      onFieldSubmitted: widget.onSubmitted,
      enabled: widget.enabled,
      readOnly: widget.readOnly,
      maxLines: widget.maxLines,
      minLines: widget.minLines,
      maxLength: widget.maxLength,
      inputFormatters: widget.inputFormatters,
      autofocus: widget.autofocus,
      autofillHints: widget.autofillHints,
      textAlign: widget.textAlign,
      style: widget.textStyle ?? _getTextStyle(),
      decoration: _buildInputDecoration(hasError),
      validator: widget.validator,
    );
  }

  List<Widget> _buildHelperText() {
    final text = _errorText ?? widget.helperText;
    final isError = _errorText != null;
    
    return [
      const SizedBox(height: AppDimensions.spacingTiny),
      Text(
        text!,
        style: AppTextStyles.bodySmall.copyWith(
          color: isError ? AppColors.error : AppColors.textSecondary,
        ),
      ),
    ];
  }

  TextStyle _getTextStyle() {
    switch (widget.size) {
      case TextFieldSize.small:
        return AppTextStyles.bodySmall;
      case TextFieldSize.medium:
        return AppTextStyles.bodyMedium;
      case TextFieldSize.large:
        return AppTextStyles.bodyLarge;
    }
  }

  double _getHeight() {
    switch (widget.size) {
      case TextFieldSize.small:
        return AppDimensions.inputHeightSmall;
      case TextFieldSize.medium:
        return AppDimensions.inputHeightMedium;
      case TextFieldSize.large:
        return AppDimensions.inputHeightLarge;
    }
  }

  EdgeInsets _getContentPadding() {
    if (widget.contentPadding != null) {
      return widget.contentPadding!;
    }
    
    switch (widget.size) {
      case TextFieldSize.small:
        return const EdgeInsets.symmetric(
          horizontal: AppDimensions.paddingSmall,
          vertical: AppDimensions.paddingTiny,
        );
      case TextFieldSize.medium:
        return const EdgeInsets.symmetric(
          horizontal: AppDimensions.paddingMedium,
          vertical: AppDimensions.paddingSmall,
        );
      case TextFieldSize.large:
        return const EdgeInsets.symmetric(
          horizontal: AppDimensions.paddingMedium,
          vertical: AppDimensions.paddingMedium,
        );
    }
  }

  InputDecoration _buildInputDecoration(bool hasError) {
    final borderRadius = BorderRadius.circular(
      widget.borderRadius ?? AppDimensions.radiusMedium,
    );
    
    final borderColor = hasError 
        ? (widget.errorBorderColor ?? AppColors.error)
        : _isFocused 
            ? (widget.focusedBorderColor ?? AppColors.primary)
            : (widget.borderColor ?? AppColors.inputBorder);
    
    final fillColor = widget.fillColor ?? 
        (widget.enabled ? AppColors.inputFill : AppColors.surfaceVariant);
    
    return InputDecoration(
      hintText: widget.hintText,
      hintStyle: AppTextStyles.inputHint,
      prefixIcon: widget.prefixIcon != null 
          ? Icon(
              widget.prefixIcon,
              color: _isFocused 
                  ? AppColors.primary 
                  : AppColors.textSecondary,
              size: _getIconSize(),
            )
          : null,
      suffixIcon: widget.suffixIcon,
      filled: widget.filled,
      fillColor: fillColor,
      contentPadding: _getContentPadding(),
      border: widget.showBorder 
          ? OutlineInputBorder(
              borderRadius: borderRadius,
              borderSide: BorderSide(
                color: AppColors.inputBorder,
                width: AppDimensions.borderWidthNormal,
              ),
            )
          : InputBorder.none,
      enabledBorder: widget.showBorder 
          ? OutlineInputBorder(
              borderRadius: borderRadius,
              borderSide: BorderSide(
                color: widget.borderColor ?? AppColors.inputBorder,
                width: AppDimensions.borderWidthNormal,
              ),
            )
          : InputBorder.none,
      focusedBorder: widget.showBorder 
          ? OutlineInputBorder(
              borderRadius: borderRadius,
              borderSide: BorderSide(
                color: widget.focusedBorderColor ?? AppColors.primary,
                width: AppDimensions.borderWidthThick,
              ),
            )
          : InputBorder.none,
      errorBorder: widget.showBorder 
          ? OutlineInputBorder(
              borderRadius: borderRadius,
              borderSide: BorderSide(
                color: widget.errorBorderColor ?? AppColors.error,
                width: AppDimensions.borderWidthNormal,
              ),
            )
          : InputBorder.none,
      focusedErrorBorder: widget.showBorder 
          ? OutlineInputBorder(
              borderRadius: borderRadius,
              borderSide: BorderSide(
                color: widget.errorBorderColor ?? AppColors.error,
                width: AppDimensions.borderWidthThick,
              ),
            )
          : InputBorder.none,
      disabledBorder: widget.showBorder 
          ? OutlineInputBorder(
              borderRadius: borderRadius,
              borderSide: BorderSide(
                color: AppColors.border,
                width: AppDimensions.borderWidthNormal,
              ),
            )
          : InputBorder.none,
      counterText: '', // 隐藏字符计数器
      errorText: null, // 不使用内置错误显示
    );
  }

  double _getIconSize() {
    switch (widget.size) {
      case TextFieldSize.small:
        return AppDimensions.iconSizeSmall;
      case TextFieldSize.medium:
        return AppDimensions.iconSizeMedium;
      case TextFieldSize.large:
        return AppDimensions.iconSizeLarge;
    }
  }
}

/// 文本输入框尺寸枚举
enum TextFieldSize {
  small,
  medium,
  large,
}

/// 预定义的文本输入框样式
class TextFieldStyles {
  static const CustomTextField email = CustomTextField(
    keyboardType: TextInputType.emailAddress,
    prefixIcon: Icons.email_outlined,
    autofillHints: [AutofillHints.email],
  );
  
  static const CustomTextField password = CustomTextField(
    obscureText: true,
    prefixIcon: Icons.lock_outline,
    autofillHints: [AutofillHints.password],
  );
  
  static const CustomTextField phone = CustomTextField(
    keyboardType: TextInputType.phone,
    prefixIcon: Icons.phone_outlined,
    autofillHints: [AutofillHints.telephoneNumber],
  );
  
  static const CustomTextField search = CustomTextField(
    prefixIcon: Icons.search,
    textInputAction: TextInputAction.search,
  );
  
  static const CustomTextField multiline = CustomTextField(
    maxLines: null,
    minLines: 3,
    textInputAction: TextInputAction.newline,
  );
}