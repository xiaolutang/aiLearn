import 'package:flutter/material.dart';

/// 智能教学助手2.0设计系统
/// 基于UI 2.0设计稿的优化主题配置
class AppTheme {
  // ===== 主色调 - 教育蓝色系 =====
  static const Color primary50 = Color(0xFFF0F8FF);
  static const Color primary100 = Color(0xFFE0F2FE);
  static const Color primary200 = Color(0xFFBAE6FD);
  static const Color primary300 = Color(0xFF7DD3FC);
  static const Color primary400 = Color(0xFF38BDF8);
  static const Color primary500 = Color(0xFF0EA5E9); // 主品牌色 - 清新蓝
  static const Color primary600 = Color(0xFF0284C7);
  static const Color primary700 = Color(0xFF0369A1);
  static const Color primary800 = Color(0xFF075985);
  static const Color primary900 = Color(0xFF0C4A6E);
  
  // 兼容性别名
  static const Color primaryColor = primary500;
  static const Color primaryLightColor = primary300;
  static const Color primaryDarkColor = primary700;
  
  // ===== 辅助色 - 智能绿色系 =====
  static const Color secondary50 = Color(0xFFF0FDF4);
  static const Color secondary100 = Color(0xFFDCFCE7);
  static const Color secondary200 = Color(0xFFBBF7D0);
  static const Color secondary300 = Color(0xFF86EFAC);
  static const Color secondary400 = Color(0xFF4ADE80);
  static const Color secondary500 = Color(0xFF22C55E); // 智能绿
  static const Color secondary600 = Color(0xFF16A34A);
  static const Color secondary700 = Color(0xFF15803D);
  static const Color secondary800 = Color(0xFF166534);
  static const Color secondary900 = Color(0xFF14532D);
  
  // 兼容性别名
  static const Color accentColor = secondary500;
  static const Color secondaryColor = secondary300;
  
  // ===== 强调色 - 活力橙色系 =====
  static const Color accent50 = Color(0xFFFFF7ED);
  static const Color accent100 = Color(0xFFFFEDD5);
  static const Color accent200 = Color(0xFFFED7AA);
  static const Color accent300 = Color(0xFFFDBA74);
  static const Color accent400 = Color(0xFFFB923C);
  static const Color accent500 = Color(0xFFF97316); // 活力橙
  static const Color accent600 = Color(0xFFEA580C);
  static const Color accent700 = Color(0xFFC2410C);
  static const Color accent800 = Color(0xFF9A3412);
  static const Color accent900 = Color(0xFF7C2D12);
  
  // ===== AI智能色 - 紫色系 =====
  static const Color purple50 = Color(0xFFFAF5FF);
  static const Color purple100 = Color(0xFFF3E8FF);
  static const Color purple200 = Color(0xFFE9D5FF);
  static const Color purple300 = Color(0xFFD8B4FE);
  static const Color purple400 = Color(0xFFC084FC);
  static const Color purple500 = Color(0xFFA855F7); // AI紫
  static const Color purple600 = Color(0xFF9333EA);
  static const Color purple700 = Color(0xFF7C3AED);
  static const Color purple800 = Color(0xFF6B21A8);
  static const Color purple900 = Color(0xFF581C87);
  
  // ===== 功能色彩 =====
  static const Color success50 = Color(0xFFF0FDF4);
  static const Color success100 = Color(0xFFDCFCE7);
  static const Color success500 = Color(0xFF22C55E);
  static const Color success600 = Color(0xFF16A34A);
  static const Color successColor = success500;
  
  static const Color warning50 = Color(0xFFFFFBEB);
  static const Color warning100 = Color(0xFFFEF3C7);
  static const Color warning500 = Color(0xFFF59E0B);
  static const Color warning600 = Color(0xFFD97706);
  static const Color warningColor = warning500;
  
  static const Color error50 = Color(0xFFFEF2F2);
  static const Color error100 = Color(0xFFFEE2E2);
  static const Color error500 = Color(0xFFEF4444);
  static const Color error600 = Color(0xFFDC2626);
  static const Color errorColor = error500;
  
  static const Color info50 = Color(0xFFF0F9FF);
  static const Color info100 = Color(0xFFE0F2FE);
  static const Color info500 = Color(0xFF0EA5E9);
  static const Color info600 = Color(0xFF0284C7);
  static const Color infoColor = info500;
  
  // ===== 中性色彩 =====
  static const Color gray50 = Color(0xFFFAFAFA);
  static const Color gray100 = Color(0xFFF5F5F5);
  static const Color gray200 = Color(0xFFEEEEEE);
  static const Color gray300 = Color(0xFFE0E0E0);
  static const Color gray400 = Color(0xFFBDBDBD);
  static const Color gray500 = Color(0xFF9E9E9E);
  static const Color gray600 = Color(0xFF757575);
  static const Color gray700 = Color(0xFF616161);
  static const Color gray800 = Color(0xFF424242);
  static const Color gray900 = Color(0xFF212121);
  
  // ===== 文本色彩 - 护眼优化 =====
  static const Color textPrimary = Color(0xFF1A1A1A);
  static const Color textSecondary = Color(0xFF666666);
  static const Color textTertiary = Color(0xFF999999);
  static const Color textPlaceholder = Color(0xFFCCCCCC);
  static const Color textInverse = Color(0xFFFFFFFF);
  static const Color textMuted = Color(0xFF8A8A8A);
  
  // 兼容性别名
  static const Color textPrimaryColor = textPrimary;
  static const Color textSecondaryColor = textSecondary;
  static const Color textHintColor = textPlaceholder;
  
  // ===== 背景色彩 - 层次优化 =====
  static const Color bgPrimary = Color(0xFFFFFFFF);
  static const Color bgSecondary = Color(0xFFFAFAFA);
  static const Color bgTertiary = Color(0xFFF5F5F5);
  static const Color bgQuaternary = Color(0xFFF0F0F0);
  static const Color bgOverlay = Color(0x66000000);
  
  // 兼容性别名
  static const Color backgroundColor = bgSecondary;
  static const Color surfaceColor = bgPrimary;
  static const Color cardColor = bgPrimary;
  
  // ===== 边框色彩 =====
  static const Color borderLight = Color(0xFFF0F0F0);
  static const Color borderDefault = Color(0xFFE0E0E0);
  static const Color borderStrong = Color(0xFFCCCCCC);
  
  // 兼容性别名
  static const Color borderColor = borderDefault;
  static const Color dividerColor = borderLight;
  
  // ===== 阴影色彩 =====
  static const Color shadowColor = Color(0x1A000000);
  static const Color shadowLight = Color(0x0A000000);
  static const Color shadowMedium = Color(0x1A000000);
  static const Color shadowStrong = Color(0x33000000);
  
  // ===== 字体大小 - 优化的字体层级 =====
  static const double textXs = 10.0;
  static const double textSm = 12.0;
  static const double textBase = 14.0;
  static const double textLg = 16.0;
  static const double textXl = 18.0;
  static const double text2xl = 20.0;
  static const double text3xl = 24.0;
  static const double text4xl = 28.0;
  static const double text5xl = 32.0;
  static const double text6xl = 36.0;
  
  // 兼容性别名
  static const double fontSizeSmall = textSm;
  static const double fontSizeMedium = textBase;
  static const double fontSizeLarge = textLg;
  static const double fontSizeXLarge = textXl;
  static const double fontSizeXXLarge = text2xl;
  static const double fontSizeTitle = text3xl;
  static const double fontSizeHeading = text4xl;
  
  // ===== 字体粗细 =====
  static const FontWeight fontThin = FontWeight.w100;
  static const FontWeight fontExtraLight = FontWeight.w200;
  static const FontWeight fontLight = FontWeight.w300;
  static const FontWeight fontNormal = FontWeight.w400;
  static const FontWeight fontMedium = FontWeight.w500;
  static const FontWeight fontSemibold = FontWeight.w600;
  static const FontWeight fontBold = FontWeight.w700;
  static const FontWeight fontExtraBold = FontWeight.w800;
  static const FontWeight fontBlack = FontWeight.w900;
  
  // ===== 行高 =====
  static const double leadingTight = 1.2;
  static const double leadingSnug = 1.3;
  static const double leadingNormal = 1.4;
  static const double leadingRelaxed = 1.5;
  static const double leadingLoose = 1.6;
  
  // ===== 间距系统 - 8px基础单位 =====
  static const double space1 = 4.0;   // 0.25rem
  static const double space2 = 8.0;   // 0.5rem
  static const double space3 = 12.0;  // 0.75rem
  static const double space4 = 16.0;  // 1rem
  static const double space5 = 20.0;  // 1.25rem
  static const double space6 = 24.0;  // 1.5rem
  static const double space8 = 32.0;  // 2rem
  static const double space10 = 40.0; // 2.5rem
  static const double space12 = 48.0; // 3rem
  static const double space16 = 64.0; // 4rem
  static const double space20 = 80.0; // 5rem
  static const double space24 = 96.0; // 6rem
  
  // 兼容性别名
  static const double paddingSmall = space2;
  static const double paddingMedium = space4;
  static const double paddingLarge = space6;
  static const double paddingXLarge = space8;
  
  // ===== 圆角系统 =====
  static const double radiusNone = 0.0;
  static const double radiusSm = 2.0;
  static const double radiusBase = 4.0;
  static const double radiusMd = 6.0;
  static const double radiusLg = 8.0;
  static const double radiusXl = 12.0;
  static const double radius2xl = 16.0;
  static const double radius3xl = 24.0;
  static const double radiusFull = 9999.0;
  
  // 兼容性别名
  static const double radiusSmall = radiusBase;
  static const double radiusMedium = radiusLg;
  static const double radiusLarge = radiusXl;
  static const double radiusXLarge = radius2xl;
  
  // ===== 阴影系统 =====
  static const List<BoxShadow> shadowXs = [
    BoxShadow(
      color: Color(0x0A000000),
      blurRadius: 1,
      offset: Offset(0, 1),
    ),
  ];
  
  static const List<BoxShadow> shadowSm = [
    BoxShadow(
      color: Color(0x0A000000),
      blurRadius: 2,
      offset: Offset(0, 1),
    ),
    BoxShadow(
      color: Color(0x0F000000),
      blurRadius: 1,
      offset: Offset(0, 1),
    ),
  ];
  
  static const List<BoxShadow> shadowMd = [
    BoxShadow(
      color: Color(0x0A000000),
      blurRadius: 4,
      offset: Offset(0, 4),
    ),
    BoxShadow(
      color: Color(0x0F000000),
      blurRadius: 2,
      offset: Offset(0, 2),
    ),
  ];
  
  static const List<BoxShadow> shadowLg = [
    BoxShadow(
      color: Color(0x0A000000),
      blurRadius: 8,
      offset: Offset(0, 8),
    ),
    BoxShadow(
      color: Color(0x0F000000),
      blurRadius: 4,
      offset: Offset(0, 4),
    ),
  ];
  
  static const List<BoxShadow> shadowXl = [
    BoxShadow(
      color: Color(0x0A000000),
      blurRadius: 16,
      offset: Offset(0, 16),
    ),
    BoxShadow(
      color: Color(0x0F000000),
      blurRadius: 8,
      offset: Offset(0, 8),
    ),
  ];
  
  // ===== 过渡动画 =====
  static const Duration transitionFast = Duration(milliseconds: 150);
  static const Duration transitionBase = Duration(milliseconds: 200);
  static const Duration transitionSlow = Duration(milliseconds: 300);
  static const Duration transitionSlower = Duration(milliseconds: 500);
  
  static const Curve curveEaseInOut = Curves.easeInOut;
  static const Curve curveEaseOut = Curves.easeOut;
  static const Curve curveEaseIn = Curves.easeIn;
  static const Curve curveBounce = Curves.bounceOut;
  
  // ===== 主题数据 - 优化版 =====
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary500,
        brightness: Brightness.light,
        primary: primary500,
        secondary: secondary500,
        tertiary: accent500,
        surface: bgPrimary,
        background: bgSecondary,
        error: error500,
      ),
      scaffoldBackgroundColor: bgSecondary,
      
      // ===== AppBar主题 =====
      appBarTheme: AppBarTheme(
        backgroundColor: bgPrimary,
        foregroundColor: textPrimary,
        elevation: 0,
        shadowColor: shadowLight,
        surfaceTintColor: Colors.transparent,
        centerTitle: false,
        titleSpacing: space4,
        toolbarHeight: 64.0,
        titleTextStyle: TextStyle(
          fontSize: text2xl,
          fontWeight: fontSemibold,
          color: textPrimary,
        ),
        iconTheme: IconThemeData(
          color: textSecondary,
          size: 24.0,
        ),
        actionsIconTheme: IconThemeData(
          color: textSecondary,
          size: 24.0,
        ),
      ),
      
      // ===== 文本主题 =====
      textTheme: TextTheme(
        // 标题样式
        displayLarge: TextStyle(
          fontSize: text6xl,
          fontWeight: fontBold,
          color: textPrimary,
          height: leadingTight,
        ),
        displayMedium: TextStyle(
          fontSize: text5xl,
          fontWeight: fontBold,
          color: textPrimary,
          height: leadingTight,
        ),
        displaySmall: TextStyle(
          fontSize: text4xl,
          fontWeight: fontSemibold,
          color: textPrimary,
          height: leadingSnug,
        ),
        headlineLarge: TextStyle(
          fontSize: text3xl,
          fontWeight: fontSemibold,
          color: textPrimary,
          height: leadingSnug,
        ),
        headlineMedium: TextStyle(
          fontSize: text2xl,
          fontWeight: fontMedium,
          color: textPrimary,
          height: leadingNormal,
        ),
        headlineSmall: TextStyle(
          fontSize: textXl,
          fontWeight: fontMedium,
          color: textPrimary,
          height: leadingNormal,
        ),
        // 正文样式
        bodyLarge: TextStyle(
          fontSize: textLg,
          fontWeight: fontNormal,
          color: textPrimary,
          height: leadingRelaxed,
        ),
        bodyMedium: TextStyle(
          fontSize: textBase,
          fontWeight: fontNormal,
          color: textSecondary,
          height: leadingRelaxed,
        ),
        bodySmall: TextStyle(
          fontSize: textSm,
          fontWeight: fontNormal,
          color: textTertiary,
          height: leadingNormal,
        ),
        // 标签样式
        labelLarge: TextStyle(
          fontSize: textBase,
          fontWeight: fontMedium,
          color: textPrimary,
          height: leadingNormal,
        ),
        labelMedium: TextStyle(
          fontSize: textSm,
          fontWeight: fontMedium,
          color: textSecondary,
          height: leadingNormal,
        ),
        labelSmall: TextStyle(
          fontSize: textXs,
          fontWeight: fontMedium,
          color: textTertiary,
          height: leadingNormal,
        ),
      ),
      
      // ===== 按钮主题 =====
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary500,
          foregroundColor: Colors.white,
          elevation: 2,
          shadowColor: shadowLight,
          padding: EdgeInsets.symmetric(
            horizontal: space6,
            vertical: space3,
          ),
          minimumSize: Size(88, 44),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusLg),
          ),
          textStyle: TextStyle(
            fontSize: textBase,
            fontWeight: fontMedium,
          ),
        ).copyWith(
          backgroundColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.hovered)) return primary600;
          if (states.contains(MaterialState.pressed)) return primary700;
          if (states.contains(MaterialState.disabled)) return gray300;
          return primary500;
        }),
          elevation: MaterialStateProperty.resolveWith((states) {
            if (states.contains(MaterialState.hovered)) return 4;
            if (states.contains(MaterialState.pressed)) return 1;
            if (states.contains(MaterialState.disabled)) return 0;
            return 2;
          }),
        ),
      ),
      
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primary500,
          side: BorderSide(color: borderDefault, width: 1.5),
          padding: EdgeInsets.symmetric(
            horizontal: space6,
            vertical: space3,
          ),
          minimumSize: Size(88, 44),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusLg),
          ),
          textStyle: TextStyle(
            fontSize: textBase,
            fontWeight: fontMedium,
          ),
        ).copyWith(
          foregroundColor: MaterialStateProperty.resolveWith((states) {
            if (states.contains(MaterialState.hovered)) return primary600;
            if (states.contains(MaterialState.pressed)) return primary700;
            if (states.contains(MaterialState.disabled)) return gray400;
            return primary500;
          }),
          side: MaterialStateProperty.resolveWith((states) {
            if (states.contains(MaterialState.hovered)) return BorderSide(color: primary500, width: 1.5);
            if (states.contains(MaterialState.pressed)) return BorderSide(color: primary600, width: 1.5);
            if (states.contains(MaterialState.disabled)) return BorderSide(color: gray300, width: 1.5);
            return BorderSide(color: borderDefault, width: 1.5);
          }),
        ),
      ),
      
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primary500,
          padding: EdgeInsets.symmetric(
            horizontal: space4,
            vertical: space2,
          ),
          minimumSize: Size(64, 36),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusMd),
          ),
          textStyle: TextStyle(
            fontSize: textBase,
            fontWeight: fontMedium,
          ),
        ),
      ),
      
      // ===== 输入框主题 =====
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: bgTertiary,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusLg),
          borderSide: BorderSide(color: borderLight, width: 1),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusLg),
          borderSide: BorderSide(color: borderLight, width: 1),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusLg),
          borderSide: BorderSide(color: primary500, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusLg),
          borderSide: BorderSide(color: error500, width: 1),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusLg),
          borderSide: BorderSide(color: error500, width: 2),
        ),
        contentPadding: EdgeInsets.symmetric(
          horizontal: space4,
          vertical: space3,
        ),
        hintStyle: TextStyle(
          color: textTertiary,
          fontSize: textBase,
        ),
        labelStyle: TextStyle(
          color: textSecondary,
          fontSize: textBase,
        ),
        floatingLabelStyle: TextStyle(
          color: primary500,
          fontSize: textSm,
        ),
      ),
      
      // ===== 卡片主题 =====
      cardTheme: CardTheme(
        color: bgPrimary,
        elevation: 1,
        shadowColor: shadowLight,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusXl),
          side: BorderSide(color: borderLight, width: 1),
        ),
        margin: EdgeInsets.all(space2),
      ),
      
      // ===== 其他组件主题 =====
      dividerTheme: DividerThemeData(
        color: borderLight,
        thickness: 1,
        space: space4,
      ),
      
      chipTheme: ChipThemeData(
        backgroundColor: bgTertiary,
        selectedColor: primary100,
        disabledColor: gray200,
        labelStyle: TextStyle(
          color: textSecondary,
          fontSize: textSm,
        ),
        secondaryLabelStyle: TextStyle(
          color: primary700,
          fontSize: textSm,
        ),
        padding: EdgeInsets.symmetric(
          horizontal: space3,
          vertical: space1,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusFull),
        ),
      ),
      
      switchTheme: SwitchThemeData(
        thumbColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) return primary500;
          return gray400;
        }),
        trackColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) return primary200;
          return gray200;
        }),
      ),
      
      checkboxTheme: CheckboxThemeData(
        fillColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) return primary500;
          return Colors.transparent;
        }),
        checkColor: MaterialStateProperty.all(Colors.white),
        side: BorderSide(color: borderDefault, width: 2),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusBase),
        ),
      ),
    );
  }

  // ===== 暗色主题 =====
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary500,
        brightness: Brightness.dark,
        primary: primary400,
        secondary: secondary400,
        tertiary: accent400,
        surface: Color(0xFF1E1E1E),
        background: Color(0xFF121212),
        error: error500,
      ),
      scaffoldBackgroundColor: Color(0xFF121212),
      
      appBarTheme: AppBarTheme(
        backgroundColor: Color(0xFF1E1E1E),
        foregroundColor: Color(0xFFE0E0E0),
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontSize: text2xl,
          fontWeight: fontSemibold,
          color: Color(0xFFE0E0E0),
        ),
      ),
      
      cardTheme: CardTheme(
        color: Color(0xFF2D2D2D),
        elevation: 2,
        shadowColor: Color(0x40000000),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusXl),
        ),
      ),
    );
  }
}