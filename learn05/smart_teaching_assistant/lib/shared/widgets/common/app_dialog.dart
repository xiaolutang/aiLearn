import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';
import 'app_button.dart';
import 'app_loading.dart';

/// 智能教学助手 - 统一对话框组件
/// 基于UI 2.0设计规范，提供多种对话框样式和功能
class AppDialog {
  /// 显示信息对话框
  static Future<bool?> showInfo({
    required BuildContext context,
    required String title,
    required String content,
    String? confirmText,
    String? cancelText,
    VoidCallback? onConfirm,
    VoidCallback? onCancel,
    bool barrierDismissible = true,
  }) {
    return showDialog<bool>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (context) => _AppDialogWidget(
        type: AppDialogType.info,
        title: title,
        content: content,
        confirmText: confirmText ?? '确定',
        cancelText: cancelText,
        onConfirm: onConfirm,
        onCancel: onCancel,
      ),
    );
  }

  /// 显示成功对话框
  static Future<bool?> showSuccess({
    required BuildContext context,
    required String title,
    required String content,
    String? confirmText,
    VoidCallback? onConfirm,
    bool barrierDismissible = true,
  }) {
    return showDialog<bool>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (context) => _AppDialogWidget(
        type: AppDialogType.success,
        title: title,
        content: content,
        confirmText: confirmText ?? '确定',
        onConfirm: onConfirm,
      ),
    );
  }

  /// 显示警告对话框
  static Future<bool?> showWarning({
    required BuildContext context,
    required String title,
    required String content,
    String? confirmText,
    String? cancelText,
    VoidCallback? onConfirm,
    VoidCallback? onCancel,
    bool barrierDismissible = true,
  }) {
    return showDialog<bool>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (context) => _AppDialogWidget(
        type: AppDialogType.warning,
        title: title,
        content: content,
        confirmText: confirmText ?? '确定',
        cancelText: cancelText ?? '取消',
        onConfirm: onConfirm,
        onCancel: onCancel,
      ),
    );
  }

  /// 显示错误对话框
  static Future<bool?> showError({
    required BuildContext context,
    required String title,
    required String content,
    String? confirmText,
    VoidCallback? onConfirm,
    bool barrierDismissible = true,
  }) {
    return showDialog<bool>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (context) => _AppDialogWidget(
        type: AppDialogType.error,
        title: title,
        content: content,
        confirmText: confirmText ?? '确定',
        onConfirm: onConfirm,
      ),
    );
  }

  /// 显示确认对话框
  static Future<bool?> showConfirm({
    required BuildContext context,
    required String title,
    required String content,
    String? confirmText,
    String? cancelText,
    VoidCallback? onConfirm,
    VoidCallback? onCancel,
    bool barrierDismissible = true,
    bool isDangerous = false,
  }) {
    return showDialog<bool>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (context) => _AppDialogWidget(
        type: isDangerous ? AppDialogType.danger : AppDialogType.confirm,
        title: title,
        content: content,
        confirmText: confirmText ?? '确定',
        cancelText: cancelText ?? '取消',
        onConfirm: onConfirm,
        onCancel: onCancel,
      ),
    );
  }

  /// 显示加载对话框
  static Future<void> showLoading({
    required BuildContext context,
    String? message,
    bool barrierDismissible = false,
  }) {
    return showDialog<void>(
      context: context,
      barrierDismissible: barrierDismissible,
      builder: (context) => _LoadingDialog(message: message),
    );
  }

  /// 显示自定义对话框
  static Future<T?> showCustom<T>({
    required BuildContext context,
    required Widget child,
    bool barrierDismissible = true,
    Color? barrierColor,
    String? barrierLabel,
    Duration transitionDuration = const Duration(milliseconds: 200),
  }) {
    return showDialog<T>(
      context: context,
      barrierDismissible: barrierDismissible,
      barrierColor: barrierColor,
      barrierLabel: barrierLabel,
      builder: (context) => child,
    );
  }

  /// 关闭对话框
  static void dismiss(BuildContext context, [dynamic result]) {
    if (Navigator.canPop(context)) {
      Navigator.pop(context, result);
    }
  }
}

/// 对话框组件实现
class _AppDialogWidget extends StatelessWidget {
  final AppDialogType type;
  final String title;
  final String content;
  final String confirmText;
  final String? cancelText;
  final VoidCallback? onConfirm;
  final VoidCallback? onCancel;

  const _AppDialogWidget({
    Key? key,
    required this.type,
    required this.title,
    required this.content,
    required this.confirmText,
    this.cancelText,
    this.onConfirm,
    this.onCancel,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final config = _getDialogConfig();
    
    return Dialog(
      backgroundColor: Colors.transparent,
      child: Container(
        constraints: BoxConstraints(
          maxWidth: 400,
          minWidth: 280,
        ),
        decoration: BoxDecoration(
          color: AppTheme.bgPrimary,
          borderRadius: BorderRadius.circular(AppTheme.radiusXl),
          boxShadow: [
            BoxShadow(
              color: AppTheme.shadowColor,
              blurRadius: 16,
              offset: Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 头部
            Container(
              padding: EdgeInsets.all(AppTheme.space6),
              child: Column(
                children: [
                  // 图标
                  if (config.icon != null) ...[
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: config.iconBackgroundColor,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        config.icon,
                        color: config.iconColor,
                        size: 24,
                      ),
                    ),
                    SizedBox(height: AppTheme.space4),
                  ],
                  
                  // 标题
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: AppTheme.textXl,
                      fontWeight: AppTheme.fontSemibold,
                      color: AppTheme.textPrimary,
                      height: AppTheme.leadingTight,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  
                  SizedBox(height: AppTheme.space3),
                  
                  // 内容
                  Text(
                    content,
                    style: TextStyle(
                      fontSize: AppTheme.textBase,
                      fontWeight: AppTheme.fontNormal,
                      color: AppTheme.textSecondary,
                      height: AppTheme.leadingNormal,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
            
            // 分割线
            Divider(
              height: 1,
              thickness: 1,
              color: AppTheme.borderLight,
            ),
            
            // 按钮区域
            Container(
              padding: EdgeInsets.all(AppTheme.space4),
              child: Row(
                children: [
                  // 取消按钮
                  if (cancelText != null) ...[
                    Expanded(
                      child: AppButton(
                        text: cancelText!,
                        type: AppButtonType.secondary,
                        size: AppButtonSize.medium,
                        onPressed: () {
                          Navigator.pop(context, false);
                          onCancel?.call();
                        },
                      ),
                    ),
                    SizedBox(width: AppTheme.space3),
                  ],
                  
                  // 确认按钮
                  Expanded(
                    child: AppButton(
                      text: confirmText,
                      type: config.confirmButtonType,
                      size: AppButtonSize.medium,
                      onPressed: () {
                        Navigator.pop(context, true);
                        onConfirm?.call();
                      },
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 获取对话框配置
  _DialogConfig _getDialogConfig() {
    switch (type) {
      case AppDialogType.info:
        return _DialogConfig(
          icon: Icons.info_outline,
          iconColor: AppTheme.info500,
          iconBackgroundColor: AppTheme.info100,
          confirmButtonType: AppButtonType.primary,
        );
      case AppDialogType.success:
        return _DialogConfig(
          icon: Icons.check_circle_outline,
          iconColor: AppTheme.success500,
          iconBackgroundColor: AppTheme.success100,
          confirmButtonType: AppButtonType.success,
        );
      case AppDialogType.warning:
        return _DialogConfig(
          icon: Icons.warning_amber_outlined,
          iconColor: AppTheme.warning500,
          iconBackgroundColor: AppTheme.warning100,
          confirmButtonType: AppButtonType.warning,
        );
      case AppDialogType.error:
        return _DialogConfig(
          icon: Icons.error_outline,
          iconColor: AppTheme.error500,
          iconBackgroundColor: AppTheme.error100,
          confirmButtonType: AppButtonType.danger,
        );
      case AppDialogType.confirm:
        return _DialogConfig(
          icon: Icons.help_outline,
          iconColor: AppTheme.primary500,
          iconBackgroundColor: AppTheme.primary100,
          confirmButtonType: AppButtonType.primary,
        );
      case AppDialogType.danger:
        return _DialogConfig(
          icon: Icons.warning_outlined,
          iconColor: AppTheme.error500,
          iconBackgroundColor: AppTheme.error100,
          confirmButtonType: AppButtonType.danger,
        );
    }
  }
}

/// 加载对话框组件
class _LoadingDialog extends StatelessWidget {
  final String? message;

  const _LoadingDialog({
    Key? key,
    this.message,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: Container(
        padding: EdgeInsets.all(AppTheme.space6),
        decoration: BoxDecoration(
          color: AppTheme.bgPrimary,
          borderRadius: BorderRadius.circular(AppTheme.radiusLg),
          boxShadow: [
            BoxShadow(
              color: AppTheme.shadowColor,
              blurRadius: 8,
              offset: Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            AppLoading.circular(
              size: AppLoadingSize.large,
              color: AppTheme.primary500,
            ),
            if (message != null) ...[
              SizedBox(height: AppTheme.space4),
              Text(
                message!,
                style: TextStyle(
                  fontSize: AppTheme.textBase,
                  fontWeight: AppTheme.fontNormal,
                  color: AppTheme.textSecondary,
                  height: AppTheme.leadingNormal,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// 对话框类型枚举
enum AppDialogType {
  info,     // 信息
  success,  // 成功
  warning,  // 警告
  error,    // 错误
  confirm,  // 确认
  danger,   // 危险操作
}

/// 对话框配置类
class _DialogConfig {
  final IconData? icon;
  final Color? iconColor;
  final Color? iconBackgroundColor;
  final AppButtonType confirmButtonType;

  const _DialogConfig({
    this.icon,
    this.iconColor,
    this.iconBackgroundColor,
    required this.confirmButtonType,
  });
}