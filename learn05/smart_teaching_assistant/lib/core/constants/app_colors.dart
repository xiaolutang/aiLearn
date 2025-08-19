import 'package:flutter/material.dart';

/// 应用颜色常量定义
/// 
/// 定义了整个应用的颜色主题，包括：
/// - 主色调和辅助色
/// - 文本颜色
/// - 背景颜色
/// - 状态颜色（成功、警告、错误）
/// - 边框和分割线颜色
class AppColors {
  // 私有构造函数，防止实例化
  AppColors._();

  // 主色调
  static const Color primary = Color(0xFF2196F3);  // 蓝色主色
  static const Color primaryLight = Color(0xFF64B5F6);
  static const Color primaryDark = Color(0xFF1976D2);
  
  // 辅助色
  static const Color secondary = Color(0xFF03DAC6);  // 青色辅助色
  static const Color secondaryLight = Color(0xFF4FE6D7);
  static const Color secondaryDark = Color(0xFF00A693);
  
  // 背景颜色
  static const Color background = Color(0xFFF5F5F5);  // 浅灰背景
  static const Color surface = Color(0xFFFFFFFF);     // 白色表面
  static const Color surfaceVariant = Color(0xFFF8F9FA);
  
  // 文本颜色
  static const Color textPrimary = Color(0xFF212121);    // 主要文本
  static const Color textSecondary = Color(0xFF757575);  // 次要文本
  static const Color textHint = Color(0xFF9E9E9E);       // 提示文本
  static const Color textDisabled = Color(0xFFBDBDBD);   // 禁用文本
  static const Color textOnPrimary = Color(0xFFFFFFFF);  // 主色上的文本
  
  // 状态颜色
  static const Color success = Color(0xFF4CAF50);   // 成功绿色
  static const Color warning = Color(0xFFFF9800);   // 警告橙色
  static const Color error = Color(0xFFF44336);     // 错误红色
  static const Color info = Color(0xFF2196F3);      // 信息蓝色
  
  // 边框和分割线
  static const Color border = Color(0xFFE0E0E0);       // 边框颜色
  static const Color divider = Color(0xFFEEEEEE);      // 分割线颜色
  static const Color outline = Color(0xFF9E9E9E);      // 轮廓颜色
  
  // 阴影颜色
  static const Color shadow = Color(0x1F000000);       // 阴影颜色
  static const Color shadowLight = Color(0x0A000000);  // 浅阴影
  
  // 覆盖层颜色
  static const Color overlay = Color(0x80000000);      // 半透明覆盖
  static const Color overlayLight = Color(0x40000000); // 浅覆盖
  
  // 输入框颜色
  static const Color inputFill = Color(0xFFF8F9FA);    // 输入框填充
  static const Color inputBorder = Color(0xFFE1E5E9);  // 输入框边框
  static const Color inputFocused = Color(0xFF2196F3); // 输入框聚焦
  
  // 按钮颜色
  static const Color buttonPrimary = Color(0xFF2196F3);     // 主按钮
  static const Color buttonSecondary = Color(0xFFE3F2FD);   // 次按钮
  static const Color buttonDisabled = Color(0xFFE0E0E0);    // 禁用按钮
  static const Color buttonText = Color(0xFFFFFFFF);        // 按钮文本
  static const Color buttonTextSecondary = Color(0xFF2196F3); // 次按钮文本
  
  // 卡片颜色
  static const Color cardBackground = Color(0xFFFFFFFF);    // 卡片背景
  static const Color cardBorder = Color(0xFFE0E0E0);       // 卡片边框
  
  // 导航颜色
  static const Color navigationBackground = Color(0xFFFFFFFF); // 导航背景
  static const Color navigationSelected = Color(0xFF2196F3);   // 导航选中
  static const Color navigationUnselected = Color(0xFF9E9E9E); // 导航未选中
  
  // 图表颜色
  static const List<Color> chartColors = [
    Color(0xFF2196F3),  // 蓝色
    Color(0xFF4CAF50),  // 绿色
    Color(0xFFFF9800),  // 橙色
    Color(0xFF9C27B0),  // 紫色
    Color(0xFFF44336),  // 红色
    Color(0xFF00BCD4),  // 青色
    Color(0xFFFFEB3B),  // 黄色
    Color(0xFF795548),  // 棕色
  ];
  
  // 渐变色
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF2196F3), Color(0xFF1976D2)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient successGradient = LinearGradient(
    colors: [Color(0xFF4CAF50), Color(0xFF388E3C)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient warningGradient = LinearGradient(
    colors: [Color(0xFFFF9800), Color(0xFFF57C00)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient errorGradient = LinearGradient(
    colors: [Color(0xFFF44336), Color(0xFFD32F2F)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  // 深色主题颜色（预留）
  static const Color darkBackground = Color(0xFF121212);
  static const Color darkSurface = Color(0xFF1E1E1E);
  static const Color darkTextPrimary = Color(0xFFFFFFFF);
  static const Color darkTextSecondary = Color(0xFFB3B3B3);
  
  /// 根据亮度获取对应的文本颜色
  static Color getTextColorForBackground(Color backgroundColor) {
    final luminance = backgroundColor.computeLuminance();
    return luminance > 0.5 ? textPrimary : textOnPrimary;
  }
  
  /// 获取颜色的半透明版本
  static Color withOpacity(Color color, double opacity) {
    return color.withOpacity(opacity);
  }
  
  /// 获取图表颜色（循环使用）
  static Color getChartColor(int index) {
    return chartColors[index % chartColors.length];
  }
}