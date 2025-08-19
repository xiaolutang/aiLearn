import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

/// 智能教学助手 - 统一加载指示器组件
/// 基于UI 2.0设计规范，提供多种加载样式和尺寸
class AppLoading extends StatelessWidget {
  final AppLoadingType type;
  final AppLoadingSize size;
  final Color? color;
  final String? message;
  final bool overlay;
  final Color? overlayColor;
  final double? strokeWidth;
  final double? value;

  const AppLoading({
    Key? key,
    this.type = AppLoadingType.circular,
    this.size = AppLoadingSize.medium,
    this.color,
    this.message,
    this.overlay = false,
    this.overlayColor,
    this.strokeWidth,
    this.value,
  }) : super(key: key);

  /// 圆形加载指示器
  const AppLoading.circular({
    Key? key,
    this.size = AppLoadingSize.medium,
    this.color,
    this.message,
    this.overlay = false,
    this.overlayColor,
    this.strokeWidth,
    this.value,
  }) : type = AppLoadingType.circular,
       super(key: key);

  /// 线性加载指示器
  const AppLoading.linear({
    Key? key,
    this.size = AppLoadingSize.medium,
    this.color,
    this.message,
    this.overlay = false,
    this.overlayColor,
    this.strokeWidth,
    this.value,
  }) : type = AppLoadingType.linear,
       super(key: key);

  /// 点状加载指示器
  const AppLoading.dots({
    Key? key,
    this.size = AppLoadingSize.medium,
    this.color,
    this.message,
    this.overlay = false,
    this.overlayColor,
  }) : type = AppLoadingType.dots,
       strokeWidth = null,
       value = null,
       super(key: key);

  /// 脉冲加载指示器
  const AppLoading.pulse({
    Key? key,
    this.size = AppLoadingSize.medium,
    this.color,
    this.message,
    this.overlay = false,
    this.overlayColor,
  }) : type = AppLoadingType.pulse,
       strokeWidth = null,
       value = null,
       super(key: key);

  /// 全屏加载遮罩
  const AppLoading.overlay({
    Key? key,
    this.type = AppLoadingType.circular,
    this.size = AppLoadingSize.large,
    this.color,
    this.message = '加载中...',
    this.overlayColor,
    this.strokeWidth,
    this.value,
  }) : overlay = true,
       super(key: key);

  @override
  Widget build(BuildContext context) {
    final loadingConfig = _getLoadingConfig();
    final loadingColor = color ?? AppTheme.primary500;
    
    Widget loadingWidget = _buildLoadingWidget(loadingConfig, loadingColor);
    
    // 添加消息文本
    if (message != null) {
      loadingWidget = Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          loadingWidget,
          SizedBox(height: AppTheme.space3),
          Text(
            message!,
            style: TextStyle(
              fontSize: loadingConfig.messageFontSize,
              fontWeight: AppTheme.fontNormal,
              color: AppTheme.textSecondary,
              height: AppTheme.leadingNormal,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      );
    }
    
    // 添加遮罩层
    if (overlay) {
      return Container(
        color: overlayColor ?? AppTheme.bgOverlay,
        child: Center(
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
            child: loadingWidget,
          ),
        ),
      );
    }
    
    return loadingWidget;
  }

  /// 构建加载组件
  Widget _buildLoadingWidget(_LoadingConfig config, Color loadingColor) {
    switch (type) {
      case AppLoadingType.circular:
        return SizedBox(
          width: config.size,
          height: config.size,
          child: CircularProgressIndicator(
            value: value,
            strokeWidth: strokeWidth ?? config.strokeWidth,
            valueColor: AlwaysStoppedAnimation<Color>(loadingColor),
            backgroundColor: loadingColor.withOpacity(0.2),
          ),
        );
        
      case AppLoadingType.linear:
        return SizedBox(
          width: config.size,
          height: config.strokeWidth,
          child: LinearProgressIndicator(
            value: value,
            valueColor: AlwaysStoppedAnimation<Color>(loadingColor),
            backgroundColor: loadingColor.withOpacity(0.2),
          ),
        );
        
      case AppLoadingType.dots:
        return _DotsLoading(
          size: config.size,
          color: loadingColor,
        );
        
      case AppLoadingType.pulse:
        return _PulseLoading(
          size: config.size,
          color: loadingColor,
        );
    }
  }

  /// 获取加载配置
  _LoadingConfig _getLoadingConfig() {
    switch (size) {
      case AppLoadingSize.small:
        return _LoadingConfig(
          size: 16,
          strokeWidth: 2,
          messageFontSize: AppTheme.textSm,
        );
      case AppLoadingSize.medium:
        return _LoadingConfig(
          size: 24,
          strokeWidth: 3,
          messageFontSize: AppTheme.textBase,
        );
      case AppLoadingSize.large:
        return _LoadingConfig(
          size: 32,
          strokeWidth: 4,
          messageFontSize: AppTheme.textLg,
        );
      case AppLoadingSize.extraLarge:
        return _LoadingConfig(
          size: 48,
          strokeWidth: 5,
          messageFontSize: AppTheme.textXl,
        );
    }
  }
}

/// 点状加载动画
class _DotsLoading extends StatefulWidget {
  final double size;
  final Color color;

  const _DotsLoading({
    Key? key,
    required this.size,
    required this.color,
  }) : super(key: key);

  @override
  State<_DotsLoading> createState() => _DotsLoadingState();
}

class _DotsLoadingState extends State<_DotsLoading>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;

  @override
  void initState() {
    super.initState();
    _controllers = List.generate(
      3,
      (index) => AnimationController(
        duration: const Duration(milliseconds: 600),
        vsync: this,
      ),
    );
    
    _animations = _controllers.map((controller) {
      return Tween<double>(begin: 0.4, end: 1.0).animate(
        CurvedAnimation(
          parent: controller,
          curve: Curves.easeInOut,
        ),
      );
    }).toList();
    
    _startAnimation();
  }

  void _startAnimation() {
    for (int i = 0; i < _controllers.length; i++) {
      Future.delayed(Duration(milliseconds: i * 200), () {
        if (mounted) {
          _controllers[i].repeat(reverse: true);
        }
      });
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final dotSize = widget.size / 4;
    
    return SizedBox(
      width: widget.size,
      height: dotSize,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: List.generate(3, (index) {
          return AnimatedBuilder(
            animation: _animations[index],
            builder: (context, child) {
              return Opacity(
                opacity: _animations[index].value,
                child: Container(
                  width: dotSize,
                  height: dotSize,
                  decoration: BoxDecoration(
                    color: widget.color,
                    shape: BoxShape.circle,
                  ),
                ),
              );
            },
          );
        }),
      ),
    );
  }
}

/// 脉冲加载动画
class _PulseLoading extends StatefulWidget {
  final double size;
  final Color color;

  const _PulseLoading({
    Key? key,
    required this.size,
    required this.color,
  }) : super(key: key);

  @override
  State<_PulseLoading> createState() => _PulseLoadingState();
}

class _PulseLoadingState extends State<_PulseLoading>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _opacityAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );
    
    _opacityAnimation = Tween<double>(begin: 1.0, end: 0.3).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );
    
    _controller.repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Opacity(
            opacity: _opacityAnimation.value,
            child: Container(
              width: widget.size,
              height: widget.size,
              decoration: BoxDecoration(
                color: widget.color,
                shape: BoxShape.circle,
              ),
            ),
          ),
        );
      },
    );
  }
}

/// 加载类型枚举
enum AppLoadingType {
  circular,  // 圆形进度条
  linear,    // 线性进度条
  dots,      // 点状动画
  pulse,     // 脉冲动画
}

/// 加载尺寸枚举
enum AppLoadingSize {
  small,      // 小尺寸
  medium,     // 中等尺寸
  large,      // 大尺寸
  extraLarge, // 超大尺寸
}

/// 加载配置类
class _LoadingConfig {
  final double size;
  final double strokeWidth;
  final double messageFontSize;

  const _LoadingConfig({
    required this.size,
    required this.strokeWidth,
    required this.messageFontSize,
  });
}