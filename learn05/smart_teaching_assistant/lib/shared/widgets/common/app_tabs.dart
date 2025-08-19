import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

/// 智能教学助手 - 统一标签页组件
/// 基于UI 2.0设计规范，提供多种标签页样式和功能
class AppTabs extends StatelessWidget {
  final List<AppTab> tabs;
  final int currentIndex;
  final ValueChanged<int>? onTap;
  final AppTabsType type;
  final Color? backgroundColor;
  final Color? indicatorColor;
  final Color? selectedLabelColor;
  final Color? unselectedLabelColor;
  final TextStyle? labelStyle;
  final TextStyle? unselectedLabelStyle;
  final EdgeInsetsGeometry? labelPadding;
  final EdgeInsetsGeometry? indicatorPadding;
  final double? indicatorWeight;
  final bool isScrollable;
  final double? tabHeight;
  final MainAxisAlignment? mainAxisAlignment;

  const AppTabs({
    Key? key,
    required this.tabs,
    required this.currentIndex,
    this.onTap,
    this.type = AppTabsType.line,
    this.backgroundColor,
    this.indicatorColor,
    this.selectedLabelColor,
    this.unselectedLabelColor,
    this.labelStyle,
    this.unselectedLabelStyle,
    this.labelPadding,
    this.indicatorPadding,
    this.indicatorWeight,
    this.isScrollable = false,
    this.tabHeight,
    this.mainAxisAlignment,
  }) : super(key: key);

  /// 线性标签页
  const AppTabs.line({
    Key? key,
    required this.tabs,
    required this.currentIndex,
    this.onTap,
    this.backgroundColor,
    this.indicatorColor,
    this.selectedLabelColor,
    this.unselectedLabelColor,
    this.labelStyle,
    this.unselectedLabelStyle,
    this.labelPadding,
    this.indicatorPadding,
    this.indicatorWeight,
    this.isScrollable = false,
    this.tabHeight,
    this.mainAxisAlignment,
  }) : type = AppTabsType.line,
       super(key: key);

  /// 卡片标签页
  const AppTabs.card({
    Key? key,
    required this.tabs,
    required this.currentIndex,
    this.onTap,
    this.backgroundColor,
    this.indicatorColor,
    this.selectedLabelColor,
    this.unselectedLabelColor,
    this.labelStyle,
    this.unselectedLabelStyle,
    this.labelPadding,
    this.indicatorPadding,
    this.indicatorWeight,
    this.isScrollable = false,
    this.tabHeight,
    this.mainAxisAlignment,
  }) : type = AppTabsType.card,
       super(key: key);

  /// 按钮标签页
  const AppTabs.button({
    Key? key,
    required this.tabs,
    required this.currentIndex,
    this.onTap,
    this.backgroundColor,
    this.indicatorColor,
    this.selectedLabelColor,
    this.unselectedLabelColor,
    this.labelStyle,
    this.unselectedLabelStyle,
    this.labelPadding,
    this.indicatorPadding,
    this.indicatorWeight,
    this.isScrollable = false,
    this.tabHeight,
    this.mainAxisAlignment,
  }) : type = AppTabsType.button,
       super(key: key);

  @override
  Widget build(BuildContext context) {
    final config = _getTabsConfig();
    
    switch (type) {
      case AppTabsType.line:
        return _buildLineTabs(config);
      case AppTabsType.card:
        return _buildCardTabs(config);
      case AppTabsType.button:
        return _buildButtonTabs(config);
    }
  }

  /// 构建线性标签页
  Widget _buildLineTabs(_TabsConfig config) {
    return Container(
      height: tabHeight ?? config.tabHeight,
      decoration: BoxDecoration(
        color: backgroundColor ?? config.backgroundColor,
        border: Border(
          bottom: BorderSide(
            color: AppTheme.borderLight,
            width: 1,
          ),
        ),
      ),
      child: TabBar(
        tabs: tabs.map((tab) => _buildLineTab(tab, config)).toList(),
        isScrollable: isScrollable,
        indicatorColor: indicatorColor ?? config.indicatorColor,
        indicatorWeight: indicatorWeight ?? config.indicatorWeight,
        indicatorPadding: indicatorPadding ?? config.indicatorPadding,
        labelColor: selectedLabelColor ?? config.selectedLabelColor,
        unselectedLabelColor: unselectedLabelColor ?? config.unselectedLabelColor,
        labelStyle: labelStyle ?? config.labelStyle,
        unselectedLabelStyle: unselectedLabelStyle ?? config.unselectedLabelStyle,
        labelPadding: labelPadding ?? config.labelPadding,
        onTap: onTap,
      ),
    );
  }

  /// 构建卡片标签页
  Widget _buildCardTabs(_TabsConfig config) {
    return Container(
      height: tabHeight ?? config.tabHeight,
      padding: EdgeInsets.all(AppTheme.space1),
      decoration: BoxDecoration(
        color: backgroundColor ?? AppTheme.gray100,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
      ),
      child: Row(
        mainAxisAlignment: mainAxisAlignment ?? MainAxisAlignment.spaceEvenly,
        children: tabs.asMap().entries.map((entry) {
          final index = entry.key;
          final tab = entry.value;
          final isSelected = index == currentIndex;
          
          return Expanded(
            child: _buildCardTab(
              tab: tab,
              isSelected: isSelected,
              config: config,
              onTap: () => onTap?.call(index),
            ),
          );
        }).toList(),
      ),
    );
  }

  /// 构建按钮标签页
  Widget _buildButtonTabs(_TabsConfig config) {
    return Container(
      height: tabHeight ?? config.tabHeight,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: tabs.asMap().entries.map((entry) {
            final index = entry.key;
            final tab = entry.value;
            final isSelected = index == currentIndex;
            
            return Padding(
              padding: EdgeInsets.only(
                right: index < tabs.length - 1 ? AppTheme.space2 : 0,
              ),
              child: _buildButtonTab(
                tab: tab,
                isSelected: isSelected,
                config: config,
                onTap: () => onTap?.call(index),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  /// 构建线性标签
  Widget _buildLineTab(AppTab tab, _TabsConfig config) {
    return Tab(
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (tab.icon != null) ...[
            tab.icon!,
            if (tab.text != null) SizedBox(width: AppTheme.space1),
          ],
          if (tab.text != null)
            Text(tab.text!),
          if (tab.badge != null) ...[
            SizedBox(width: AppTheme.space1),
            tab.badge!,
          ],
        ],
      ),
    );
  }

  /// 构建卡片标签
  Widget _buildCardTab({
    required AppTab tab,
    required bool isSelected,
    required _TabsConfig config,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppTheme.radiusMd),
        child: AnimatedContainer(
          duration: AppTheme.transitionFast,
          padding: labelPadding ?? EdgeInsets.symmetric(
            vertical: AppTheme.space2,
            horizontal: AppTheme.space3,
          ),
          decoration: BoxDecoration(
            color: isSelected 
                ? (selectedLabelColor ?? config.selectedLabelColor)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(AppTheme.radiusMd),
            boxShadow: isSelected ? [
              BoxShadow(
                color: AppTheme.shadowColor,
                blurRadius: 4,
                offset: Offset(0, 2),
              ),
            ] : null,
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (tab.icon != null) ...[
                IconTheme(
                  data: IconThemeData(
                    color: isSelected 
                        ? Colors.white
                        : (unselectedLabelColor ?? config.unselectedLabelColor),
                    size: 16,
                  ),
                  child: tab.icon!,
                ),
                if (tab.text != null) SizedBox(width: AppTheme.space1),
              ],
              if (tab.text != null)
                Text(
                  tab.text!,
                  style: TextStyle(
                    fontSize: AppTheme.textSm,
                    fontWeight: isSelected ? AppTheme.fontMedium : AppTheme.fontNormal,
                    color: isSelected 
                        ? Colors.white
                        : (unselectedLabelColor ?? config.unselectedLabelColor),
                  ),
                ),
              if (tab.badge != null) ...[
                SizedBox(width: AppTheme.space1),
                tab.badge!,
              ],
            ],
          ),
        ),
      ),
    );
  }

  /// 构建按钮标签
  Widget _buildButtonTab({
    required AppTab tab,
    required bool isSelected,
    required _TabsConfig config,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        child: AnimatedContainer(
          duration: AppTheme.transitionFast,
          padding: labelPadding ?? EdgeInsets.symmetric(
            vertical: AppTheme.space2,
            horizontal: AppTheme.space4,
          ),
          decoration: BoxDecoration(
            color: isSelected 
                ? (indicatorColor ?? config.indicatorColor)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(AppTheme.radiusLg),
            border: Border.all(
              color: isSelected 
                  ? (indicatorColor ?? config.indicatorColor)
                  : AppTheme.borderLight,
              width: 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (tab.icon != null) ...[
                IconTheme(
                  data: IconThemeData(
                    color: isSelected 
                        ? Colors.white
                        : (unselectedLabelColor ?? config.unselectedLabelColor),
                    size: 16,
                  ),
                  child: tab.icon!,
                ),
                if (tab.text != null) SizedBox(width: AppTheme.space1),
              ],
              if (tab.text != null)
                Text(
                  tab.text!,
                  style: TextStyle(
                    fontSize: AppTheme.textSm,
                    fontWeight: isSelected ? AppTheme.fontMedium : AppTheme.fontNormal,
                    color: isSelected 
                        ? Colors.white
                        : (unselectedLabelColor ?? config.unselectedLabelColor),
                  ),
                ),
              if (tab.badge != null) ...[
                SizedBox(width: AppTheme.space1),
                tab.badge!,
              ],
            ],
          ),
        ),
      ),
    );
  }

  /// 获取标签页配置
  _TabsConfig _getTabsConfig() {
    return _TabsConfig(
      backgroundColor: AppTheme.bgPrimary,
      indicatorColor: AppTheme.primary500,
      selectedLabelColor: AppTheme.primary500,
      unselectedLabelColor: AppTheme.textSecondary,
      labelStyle: TextStyle(
        fontSize: AppTheme.textSm,
        fontWeight: AppTheme.fontMedium,
      ),
      unselectedLabelStyle: TextStyle(
        fontSize: AppTheme.textSm,
        fontWeight: AppTheme.fontNormal,
      ),
      labelPadding: EdgeInsets.symmetric(
        horizontal: AppTheme.space3,
        vertical: AppTheme.space2,
      ),
      indicatorPadding: EdgeInsets.symmetric(
        horizontal: AppTheme.space3,
      ),
      indicatorWeight: 2.0,
      tabHeight: 48.0,
    );
  }
}

/// 标签页项
class AppTab {
  final String? text;
  final Widget? icon;
  final Widget? badge;
  final String? tooltip;

  const AppTab({
    this.text,
    this.icon,
    this.badge,
    this.tooltip,
  }) : assert(text != null || icon != null, 'Either text or icon must be provided');

  /// 文本标签
  const AppTab.text({
    required String this.text,
    this.badge,
    this.tooltip,
  }) : icon = null;

  /// 图标标签
  const AppTab.icon({
    required Widget this.icon,
    this.badge,
    this.tooltip,
  }) : text = null;

  /// 图标+文本标签
  const AppTab.iconText({
    required String this.text,
    required Widget this.icon,
    this.badge,
    this.tooltip,
  });
}

/// 标签页类型枚举
enum AppTabsType {
  line,   // 线性标签页
  card,   // 卡片标签页
  button, // 按钮标签页
}

/// 标签页配置类
class _TabsConfig {
  final Color backgroundColor;
  final Color indicatorColor;
  final Color selectedLabelColor;
  final Color unselectedLabelColor;
  final TextStyle labelStyle;
  final TextStyle unselectedLabelStyle;
  final EdgeInsetsGeometry labelPadding;
  final EdgeInsetsGeometry indicatorPadding;
  final double indicatorWeight;
  final double tabHeight;

  const _TabsConfig({
    required this.backgroundColor,
    required this.indicatorColor,
    required this.selectedLabelColor,
    required this.unselectedLabelColor,
    required this.labelStyle,
    required this.unselectedLabelStyle,
    required this.labelPadding,
    required this.indicatorPadding,
    required this.indicatorWeight,
    required this.tabHeight,
  });
}