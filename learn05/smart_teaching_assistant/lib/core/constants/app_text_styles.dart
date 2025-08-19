import 'package:flutter/material.dart';
import 'app_colors.dart';

/// 应用文本样式常量定义
/// 
/// 定义了整个应用的文本样式，包括：
/// - 标题样式（大、中、小）
/// - 正文样式（大、中、小）
/// - 按钮文本样式
/// - 标签和说明文本样式
/// - 特殊用途文本样式
class AppTextStyles {
  // 私有构造函数，防止实例化
  AppTextStyles._();

  // 基础字体
  static const String _fontFamily = 'PingFang SC';
  static const String _fallbackFontFamily = 'Helvetica Neue';
  
  // 字体权重
  static const FontWeight light = FontWeight.w300;
  static const FontWeight regular = FontWeight.w400;
  static const FontWeight medium = FontWeight.w500;
  static const FontWeight semiBold = FontWeight.w600;
  static const FontWeight bold = FontWeight.w700;
  
  // 标题样式
  static const TextStyle headlineLarge = TextStyle(
    fontSize: 32,
    fontWeight: bold,
    height: 1.25,
    letterSpacing: -0.5,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  static const TextStyle headlineMedium = TextStyle(
    fontSize: 28,
    fontWeight: bold,
    height: 1.29,
    letterSpacing: -0.25,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  static const TextStyle headlineSmall = TextStyle(
    fontSize: 24,
    fontWeight: semiBold,
    height: 1.33,
    letterSpacing: 0,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  // 标题样式
  static const TextStyle titleLarge = TextStyle(
    fontSize: 22,
    fontWeight: semiBold,
    height: 1.27,
    letterSpacing: 0,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  static const TextStyle titleMedium = TextStyle(
    fontSize: 16,
    fontWeight: medium,
    height: 1.5,
    letterSpacing: 0.15,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  static const TextStyle titleSmall = TextStyle(
    fontSize: 14,
    fontWeight: medium,
    height: 1.43,
    letterSpacing: 0.1,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  // 正文样式
  static const TextStyle bodyLarge = TextStyle(
    fontSize: 16,
    fontWeight: regular,
    height: 1.5,
    letterSpacing: 0.5,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  static const TextStyle bodyMedium = TextStyle(
    fontSize: 14,
    fontWeight: regular,
    height: 1.43,
    letterSpacing: 0.25,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  static const TextStyle bodySmall = TextStyle(
    fontSize: 12,
    fontWeight: regular,
    height: 1.33,
    letterSpacing: 0.4,
    fontFamily: _fontFamily,
    color: AppColors.textSecondary,
  );
  
  // 标签样式
  static const TextStyle labelLarge = TextStyle(
    fontSize: 14,
    fontWeight: medium,
    height: 1.43,
    letterSpacing: 0.1,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  static const TextStyle labelMedium = TextStyle(
    fontSize: 12,
    fontWeight: medium,
    height: 1.33,
    letterSpacing: 0.5,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  static const TextStyle labelSmall = TextStyle(
    fontSize: 11,
    fontWeight: medium,
    height: 1.45,
    letterSpacing: 0.5,
    fontFamily: _fontFamily,
    color: AppColors.textSecondary,
  );
  
  // 按钮文本样式
  static const TextStyle buttonLarge = TextStyle(
    fontSize: 16,
    fontWeight: semiBold,
    height: 1.25,
    letterSpacing: 0.5,
    fontFamily: _fontFamily,
    color: AppColors.buttonText,
  );
  
  static const TextStyle buttonMedium = TextStyle(
    fontSize: 14,
    fontWeight: semiBold,
    height: 1.43,
    letterSpacing: 0.25,
    fontFamily: _fontFamily,
    color: AppColors.buttonText,
  );
  
  static const TextStyle buttonSmall = TextStyle(
    fontSize: 12,
    fontWeight: semiBold,
    height: 1.33,
    letterSpacing: 0.4,
    fontFamily: _fontFamily,
    color: AppColors.buttonText,
  );
  
  // 链接文本样式
  static const TextStyle linkLarge = TextStyle(
    fontSize: 16,
    fontWeight: medium,
    height: 1.5,
    letterSpacing: 0.5,
    fontFamily: _fontFamily,
    color: AppColors.primary,
    decoration: TextDecoration.underline,
  );
  
  static const TextStyle linkMedium = TextStyle(
    fontSize: 14,
    fontWeight: medium,
    height: 1.43,
    letterSpacing: 0.25,
    fontFamily: _fontFamily,
    color: AppColors.primary,
    decoration: TextDecoration.underline,
  );
  
  static const TextStyle linkSmall = TextStyle(
    fontSize: 12,
    fontWeight: medium,
    height: 1.33,
    letterSpacing: 0.4,
    fontFamily: _fontFamily,
    color: AppColors.primary,
    decoration: TextDecoration.underline,
  );
  
  // 输入框文本样式
  static const TextStyle inputText = TextStyle(
    fontSize: 16,
    fontWeight: regular,
    height: 1.5,
    letterSpacing: 0.5,
    fontFamily: _fontFamily,
    color: AppColors.textPrimary,
  );
  
  static const TextStyle inputLabel = TextStyle(
    fontSize: 14,
    fontWeight: medium,
    height: 1.43,
    letterSpacing: 0.25,
    fontFamily: _fontFamily,
    color: AppColors.textSecondary,
  );
  
  static const TextStyle inputHint = TextStyle(
    fontSize: 16,
    fontWeight: regular,
    height: 1.5,
    letterSpacing: 0.5,
    fontFamily: _fontFamily,
    color: AppColors.textHint,
  );
  
  static const TextStyle inputError = TextStyle(
    fontSize: 12,
    fontWeight: regular,
    height: 1.33,
    letterSpacing: 0.4,
    fontFamily: _fontFamily,
    color: AppColors.error,
  );
  
  // 特殊用途样式
  static const TextStyle caption = TextStyle(
    fontSize: 12,
    fontWeight: regular,
    height: 1.33,
    letterSpacing: 0.4,
    fontFamily: _fontFamily,
    color: AppColors.textSecondary,
  );
  
  static const TextStyle overline = TextStyle(
    fontSize: 10,
    fontWeight: medium,
    height: 1.6,
    letterSpacing: 1.5,
    fontFamily: _fontFamily,
    color: AppColors.textSecondary,
  );
  
  // 数字显示样式
  static const TextStyle numberLarge = TextStyle(
    fontSize: 32,
    fontWeight: bold,
    height: 1.25,
    letterSpacing: -0.5,
    fontFamily: 'SF Mono',
    color: AppColors.primary,
  );
  
  static const TextStyle numberMedium = TextStyle(
    fontSize: 24,
    fontWeight: semiBold,
    height: 1.33,
    letterSpacing: 0,
    fontFamily: 'SF Mono',
    color: AppColors.primary,
  );
  
  static const TextStyle numberSmall = TextStyle(
    fontSize: 16,
    fontWeight: medium,
    height: 1.5,
    letterSpacing: 0.5,
    fontFamily: 'SF Mono',
    color: AppColors.textPrimary,
  );
  
  // 代码样式
  static const TextStyle code = TextStyle(
    fontSize: 14,
    fontWeight: regular,
    height: 1.43,
    letterSpacing: 0,
    fontFamily: 'SF Mono',
    color: AppColors.textPrimary,
    backgroundColor: AppColors.surfaceVariant,
  );
  
  // 工具方法
  
  /// 创建带有指定颜色的文本样式
  static TextStyle withColor(TextStyle style, Color color) {
    return style.copyWith(color: color);
  }
  
  /// 创建带有指定字体大小的文本样式
  static TextStyle withFontSize(TextStyle style, double fontSize) {
    return style.copyWith(fontSize: fontSize);
  }
  
  /// 创建带有指定字体权重的文本样式
  static TextStyle withFontWeight(TextStyle style, FontWeight fontWeight) {
    return style.copyWith(fontWeight: fontWeight);
  }
  
  /// 创建带有指定行高的文本样式
  static TextStyle withHeight(TextStyle style, double height) {
    return style.copyWith(height: height);
  }
  
  /// 创建带有指定字母间距的文本样式
  static TextStyle withLetterSpacing(TextStyle style, double letterSpacing) {
    return style.copyWith(letterSpacing: letterSpacing);
  }
  
  /// 创建带有装饰的文本样式
  static TextStyle withDecoration(TextStyle style, TextDecoration decoration) {
    return style.copyWith(decoration: decoration);
  }
  
  /// 获取响应式字体大小
  static double getResponsiveFontSize(BuildContext context, double baseFontSize) {
    final screenWidth = MediaQuery.of(context).size.width;
    if (screenWidth < 600) {
      return baseFontSize * 0.9; // 小屏幕
    } else if (screenWidth < 1200) {
      return baseFontSize; // 中等屏幕
    } else {
      return baseFontSize * 1.1; // 大屏幕
    }
  }
  
  /// 根据主题亮度调整文本样式
  static TextStyle adaptToTheme(TextStyle style, Brightness brightness) {
    if (brightness == Brightness.dark) {
      return style.copyWith(
        color: style.color == AppColors.textPrimary 
            ? AppColors.darkTextPrimary 
            : style.color == AppColors.textSecondary 
                ? AppColors.darkTextSecondary 
                : style.color,
      );
    }
    return style;
  }
}