import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

/// 智能教学助手 - 统一底部导航栏组件
/// 基于UI 2.0设计规范，提供多种导航样式和功能
class AppBottomNavigation extends StatelessWidget {
  final int currentIndex;
  final List<AppBottomNavigationItem> items;
  final ValueChanged<int>? onTap;
  final AppBottomNavigationType type;
  final Color? backgroundColor;
  final double? elevation;
  final bool showLabels;
  final double? iconSize;
  final TextStyle? labelStyle;
  final TextStyle? unselectedLabelStyle;
  final Color? selectedItemColor;
  final Color? unselectedItemColor;
  final EdgeInsetsGeometry? contentPadding;

  const AppBottomNavigation({
    Key? key,
    required this.currentIndex,
    required this.items,
    this.onTap,
    this.type = AppBottomNavigationType.fixed,
    this.backgroundColor,
    this.elevation,
    this.showLabels = true,
    this.iconSize,
    this.labelStyle,
    this.unselectedLabelStyle,
    this.selectedItemColor,
    this.unselectedItemColor,
    this.contentPadding,
  }) : assert(items.length >= 2 && items.length <= 5),
       super(key: key);

  /// 固定底部导航栏
  const AppBottomNavigation.fixed({
    Key? key,
    required this.currentIndex,
    required this.items,
    this.onTap,
    this.backgroundColor,
    this.elevation,
    this.showLabels = true,
    this.iconSize,
    this.labelStyle,
    this.unselectedLabelStyle,
    this.selectedItemColor,
    this.unselectedItemColor,
    this.contentPadding,
  }) : type = AppBottomNavigationType.fixed,
       assert(items.length >= 2 && items.length <= 5),
       super(key: key);

  /// 浮动底部导航栏
  const AppBottomNavigation.floating({
    Key? key,
    required this.currentIndex,
    required this.items,
    this.onTap,
    this.backgroundColor,
    this.elevation,
    this.showLabels = true,
    this.iconSize,
    this.labelStyle,
    this.unselectedLabelStyle,
    this.selectedItemColor,
    this.unselectedItemColor,
    this.contentPadding,
  }) : type = AppBottomNavigationType.floating,
       assert(items.length >= 2 && items.length <= 5),
       super(key: key);

  @override
  Widget build(BuildContext context) {
    final config = _getNavigationConfig();
    
    switch (type) {
      case AppBottomNavigationType.fixed:
        return _buildFixedNavigation(config);
      case AppBottomNavigationType.floating:
        return _buildFloatingNavigation(config);
    }
  }

  /// 构建固定导航栏
  Widget _buildFixedNavigation(_NavigationConfig config) {
    return Container(
      decoration: BoxDecoration(
        color: backgroundColor ?? config.backgroundColor,
        border: Border(
          top: BorderSide(
            color: AppTheme.borderLight,
            width: 1,
          ),
        ),
        boxShadow: elevation != null ? [
          BoxShadow(
            color: AppTheme.shadowColor,
            blurRadius: elevation!,
            offset: Offset(0, -elevation! / 2),
          ),
        ] : null,
      ),
      child: SafeArea(
        child: Container(
          padding: contentPadding ?? config.contentPadding,
          child: Row(
            children: items.asMap().entries.map((entry) {
              final index = entry.key;
              final item = entry.value;
              final isSelected = index == currentIndex;
              
              return Expanded(
                child: _buildNavigationItem(
                  item: item,
                  isSelected: isSelected,
                  config: config,
                  onTap: () => onTap?.call(index),
                ),
              );
            }).toList(),
          ),
        ),
      ),
    );
  }

  /// 构建浮动导航栏
  Widget _buildFloatingNavigation(_NavigationConfig config) {
    return Container(
      margin: EdgeInsets.all(AppTheme.space4),
      child: SafeArea(
        child: Container(
          padding: contentPadding ?? config.contentPadding,
          decoration: BoxDecoration(
            color: backgroundColor ?? config.backgroundColor,
            borderRadius: BorderRadius.circular(AppTheme.radiusXl),
            boxShadow: [
              BoxShadow(
                color: AppTheme.shadowColor,
                blurRadius: elevation ?? 12,
                offset: Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: items.asMap().entries.map((entry) {
              final index = entry.key;
              final item = entry.value;
              final isSelected = index == currentIndex;
              
              return Expanded(
                child: _buildNavigationItem(
                  item: item,
                  isSelected: isSelected,
                  config: config,
                  onTap: () => onTap?.call(index),
                ),
              );
            }).toList(),
          ),
        ),
      ),
    );
  }

  /// 构建导航项
  Widget _buildNavigationItem({
    required AppBottomNavigationItem item,
    required bool isSelected,
    required _NavigationConfig config,
    required VoidCallback onTap,
  }) {
    final itemColor = isSelected 
        ? (selectedItemColor ?? config.selectedItemColor)
        : (unselectedItemColor ?? config.unselectedItemColor);
    
    final itemIconSize = iconSize ?? config.iconSize;
    
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        child: Container(
          padding: EdgeInsets.symmetric(
            vertical: AppTheme.space2,
            horizontal: AppTheme.space1,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 图标容器
              Container(
                padding: EdgeInsets.all(AppTheme.space1),
                decoration: isSelected ? BoxDecoration(
                  color: itemColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(AppTheme.radiusMd),
                ) : null,
                child: _buildIcon(
                  item: item,
                  isSelected: isSelected,
                  color: itemColor,
                  size: itemIconSize,
                ),
              ),
              
              // 标签
              if (showLabels && item.label != null) ...[
                SizedBox(height: AppTheme.space1),
                Text(
                  item.label!,
                  style: (isSelected ? labelStyle : unselectedLabelStyle) ?? TextStyle(
                    fontSize: config.labelFontSize,
                    fontWeight: isSelected ? AppTheme.fontMedium : AppTheme.fontNormal,
                    color: itemColor,
                    height: AppTheme.leadingTight,
                  ),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              
              // 徽章
              if (item.badge != null)
                Positioned(
                  right: 0,
                  top: 0,
                  child: item.badge!,
                ),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建图标
  Widget _buildIcon({
    required AppBottomNavigationItem item,
    required bool isSelected,
    required Color color,
    required double size,
  }) {
    Widget iconWidget;
    
    if (item.activeIcon != null && isSelected) {
      iconWidget = item.activeIcon!;
    } else {
      iconWidget = item.icon;
    }
    
    // 如果是IconData，应用颜色和大小
    if (iconWidget is Icon) {
      return Icon(
        (iconWidget as Icon).icon,
        color: color,
        size: size,
      );
    }
    
    // 如果是自定义Widget，直接返回
    return iconWidget;
  }

  /// 获取导航配置
  _NavigationConfig _getNavigationConfig() {
    return _NavigationConfig(
      backgroundColor: AppTheme.bgPrimary,
      selectedItemColor: AppTheme.primary500,
      unselectedItemColor: AppTheme.textSecondary,
      iconSize: 24,
      labelFontSize: AppTheme.textSm,
      contentPadding: EdgeInsets.symmetric(
        vertical: AppTheme.space2,
        horizontal: AppTheme.space4,
      ),
    );
  }
}

/// 底部导航项
class AppBottomNavigationItem {
  final Widget icon;
  final Widget? activeIcon;
  final String? label;
  final Widget? badge;
  final String? tooltip;

  const AppBottomNavigationItem({
    required this.icon,
    this.activeIcon,
    this.label,
    this.badge,
    this.tooltip,
  });
}

/// 底部导航类型枚举
enum AppBottomNavigationType {
  fixed,    // 固定导航栏
  floating, // 浮动导航栏
}

/// 导航配置类
class _NavigationConfig {
  final Color backgroundColor;
  final Color selectedItemColor;
  final Color unselectedItemColor;
  final double iconSize;
  final double labelFontSize;
  final EdgeInsetsGeometry contentPadding;

  const _NavigationConfig({
    required this.backgroundColor,
    required this.selectedItemColor,
    required this.unselectedItemColor,
    required this.iconSize,
    required this.labelFontSize,
    required this.contentPadding,
  });
}