import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

/// 智能教学助手 - 统一头像组件
/// 基于UI 2.0设计规范，提供多种头像样式和功能
class AppAvatar extends StatelessWidget {
  final String? imageUrl;
  final String? name;
  final Widget? child;
  final AppAvatarSize size;
  final AppAvatarShape shape;
  final Color? backgroundColor;
  final Color? textColor;
  final TextStyle? textStyle;
  final double? borderWidth;
  final Color? borderColor;
  final Widget? badge;
  final VoidCallback? onTap;
  final String? heroTag;
  final BoxFit? fit;
  final Widget? placeholder;
  final Widget? errorWidget;

  const AppAvatar({
    Key? key,
    this.imageUrl,
    this.name,
    this.child,
    this.size = AppAvatarSize.medium,
    this.shape = AppAvatarShape.circle,
    this.backgroundColor,
    this.textColor,
    this.textStyle,
    this.borderWidth,
    this.borderColor,
    this.badge,
    this.onTap,
    this.heroTag,
    this.fit,
    this.placeholder,
    this.errorWidget,
  }) : super(key: key);

  /// 图片头像
  const AppAvatar.image({
    Key? key,
    required String this.imageUrl,
    this.size = AppAvatarSize.medium,
    this.shape = AppAvatarShape.circle,
    this.borderWidth,
    this.borderColor,
    this.badge,
    this.onTap,
    this.heroTag,
    this.fit,
    this.placeholder,
    this.errorWidget,
  }) : name = null,
       child = null,
       backgroundColor = null,
       textColor = null,
       textStyle = null,
       super(key: key);

  /// 文字头像
  const AppAvatar.text({
    Key? key,
    required String this.name,
    this.size = AppAvatarSize.medium,
    this.shape = AppAvatarShape.circle,
    this.backgroundColor,
    this.textColor,
    this.textStyle,
    this.borderWidth,
    this.borderColor,
    this.badge,
    this.onTap,
    this.heroTag,
  }) : imageUrl = null,
       child = null,
       fit = null,
       placeholder = null,
       errorWidget = null,
       super(key: key);

  /// 自定义头像
  const AppAvatar.custom({
    Key? key,
    required Widget this.child,
    this.size = AppAvatarSize.medium,
    this.shape = AppAvatarShape.circle,
    this.backgroundColor,
    this.borderWidth,
    this.borderColor,
    this.badge,
    this.onTap,
    this.heroTag,
  }) : imageUrl = null,
       name = null,
       textColor = null,
       textStyle = null,
       fit = null,
       placeholder = null,
       errorWidget = null,
       super(key: key);

  @override
  Widget build(BuildContext context) {
    final config = _getAvatarConfig();
    
    Widget avatar = _buildAvatar(config);
    
    // 添加边框
    if (borderWidth != null && borderWidth! > 0) {
      avatar = _buildBorderedAvatar(avatar, config);
    }
    
    // 添加徽章
    if (badge != null) {
      avatar = _buildAvatarWithBadge(avatar, config);
    }
    
    // 添加点击事件
    if (onTap != null) {
      avatar = _buildClickableAvatar(avatar, config);
    }
    
    // 添加Hero动画
    if (heroTag != null) {
      avatar = Hero(
        tag: heroTag!,
        child: avatar,
      );
    }
    
    return avatar;
  }

  /// 构建头像
  Widget _buildAvatar(_AvatarConfig config) {
    Widget content;
    
    if (child != null) {
      content = child!;
    } else if (imageUrl != null && imageUrl!.isNotEmpty) {
      content = _buildImageAvatar(config);
    } else if (name != null && name!.isNotEmpty) {
      content = _buildTextAvatar(config);
    } else {
      content = _buildDefaultAvatar(config);
    }
    
    return Container(
      width: config.size,
      height: config.size,
      decoration: BoxDecoration(
        color: backgroundColor ?? config.backgroundColor,
        borderRadius: shape == AppAvatarShape.circle 
            ? BorderRadius.circular(config.size / 2)
            : BorderRadius.circular(config.borderRadius),
      ),
      clipBehavior: Clip.antiAlias,
      child: content,
    );
  }

  /// 构建图片头像
  Widget _buildImageAvatar(_AvatarConfig config) {
    return Image.network(
      imageUrl!,
      width: config.size,
      height: config.size,
      fit: fit ?? BoxFit.cover,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return placeholder ?? _buildLoadingAvatar(config);
      },
      errorBuilder: (context, error, stackTrace) {
        return errorWidget ?? _buildErrorAvatar(config);
      },
    );
  }

  /// 构建文字头像
  Widget _buildTextAvatar(_AvatarConfig config) {
    final displayText = _getDisplayText();
    
    return Center(
      child: Text(
        displayText,
        style: textStyle ?? config.textStyle.copyWith(
          color: textColor ?? config.textColor,
        ),
        textAlign: TextAlign.center,
      ),
    );
  }

  /// 构建默认头像
  Widget _buildDefaultAvatar(_AvatarConfig config) {
    return Center(
      child: Icon(
        Icons.person,
        size: config.iconSize,
        color: textColor ?? config.textColor,
      ),
    );
  }

  /// 构建加载中头像
  Widget _buildLoadingAvatar(_AvatarConfig config) {
    return Container(
      color: AppTheme.gray100,
      child: Center(
        child: SizedBox(
          width: config.iconSize,
          height: config.iconSize,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(
              AppTheme.primary500,
            ),
          ),
        ),
      ),
    );
  }

  /// 构建错误头像
  Widget _buildErrorAvatar(_AvatarConfig config) {
    return Container(
      color: AppTheme.gray100,
      child: Center(
        child: Icon(
          Icons.broken_image,
          size: config.iconSize,
          color: AppTheme.textTertiary,
        ),
      ),
    );
  }

  /// 构建带边框的头像
  Widget _buildBorderedAvatar(Widget avatar, _AvatarConfig config) {
    return Container(
      width: config.size + (borderWidth! * 2),
      height: config.size + (borderWidth! * 2),
      decoration: BoxDecoration(
        color: borderColor ?? AppTheme.borderDefault,
        borderRadius: shape == AppAvatarShape.circle 
            ? BorderRadius.circular((config.size + borderWidth! * 2) / 2)
            : BorderRadius.circular(config.borderRadius + borderWidth!),
      ),
      child: Center(child: avatar),
    );
  }

  /// 构建带徽章的头像
  Widget _buildAvatarWithBadge(Widget avatar, _AvatarConfig config) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        avatar,
        Positioned(
          top: -4,
          right: -4,
          child: badge!,
        ),
      ],
    );
  }

  /// 构建可点击的头像
  Widget _buildClickableAvatar(Widget avatar, _AvatarConfig config) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: shape == AppAvatarShape.circle 
            ? BorderRadius.circular(config.size / 2)
            : BorderRadius.circular(config.borderRadius),
        child: avatar,
      ),
    );
  }

  /// 获取显示文本
  String _getDisplayText() {
    if (name == null || name!.isEmpty) return '';
    
    final words = name!.trim().split(RegExp(r'\s+'));
    if (words.length == 1) {
      // 单个词，取前两个字符
      return words[0].length > 1 
          ? words[0].substring(0, 2).toUpperCase()
          : words[0].toUpperCase();
    } else {
      // 多个词，取每个词的首字母
      return words.take(2)
          .map((word) => word.isNotEmpty ? word[0].toUpperCase() : '')
          .join('');
    }
  }

  /// 获取头像配置
  _AvatarConfig _getAvatarConfig() {
    switch (size) {
      case AppAvatarSize.small:
        return _AvatarConfig(
          size: 32,
          iconSize: 16,
          borderRadius: AppTheme.radiusSm,
          backgroundColor: AppTheme.gray200,
          textColor: AppTheme.textPrimary,
          textStyle: TextStyle(
            fontSize: AppTheme.textSm,
            fontWeight: AppTheme.fontMedium,
            height: 1.0,
          ),
        );
      case AppAvatarSize.medium:
        return _AvatarConfig(
          size: 40,
          iconSize: 20,
          borderRadius: AppTheme.radiusMd,
          backgroundColor: AppTheme.gray200,
          textColor: AppTheme.textPrimary,
          textStyle: TextStyle(
            fontSize: AppTheme.textBase,
            fontWeight: AppTheme.fontMedium,
            height: 1.0,
          ),
        );
      case AppAvatarSize.large:
        return _AvatarConfig(
          size: 56,
          iconSize: 28,
          borderRadius: AppTheme.radiusLg,
          backgroundColor: AppTheme.gray200,
          textColor: AppTheme.textPrimary,
          textStyle: TextStyle(
            fontSize: AppTheme.textLg,
            fontWeight: AppTheme.fontMedium,
            height: 1.0,
          ),
        );
      case AppAvatarSize.extraLarge:
        return _AvatarConfig(
          size: 80,
          iconSize: 40,
          borderRadius: AppTheme.radiusXl,
          backgroundColor: AppTheme.gray200,
          textColor: AppTheme.textPrimary,
          textStyle: TextStyle(
            fontSize: AppTheme.textXl,
            fontWeight: AppTheme.fontMedium,
            height: 1.0,
          ),
        );
    }
  }
}

/// 头像尺寸枚举
enum AppAvatarSize {
  small,      // 小 32x32
  medium,     // 中 40x40
  large,      // 大 56x56
  extraLarge, // 超大 80x80
}

/// 头像形状枚举
enum AppAvatarShape {
  circle,    // 圆形
  rounded,   // 圆角矩形
}

/// 头像配置类
class _AvatarConfig {
  final double size;
  final double iconSize;
  final double borderRadius;
  final Color backgroundColor;
  final Color textColor;
  final TextStyle textStyle;

  const _AvatarConfig({
    required this.size,
    required this.iconSize,
    required this.borderRadius,
    required this.backgroundColor,
    required this.textColor,
    required this.textStyle,
  });
}