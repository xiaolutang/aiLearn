import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../utils/responsive_utils.dart';

/// 响应式布局组件
/// 提供自适应的主布局结构
class ResponsiveLayout extends StatelessWidget {
  final Widget body;
  final Widget? sidebar;
  final Widget? bottomNavigationBar;
  final FloatingActionButton? floatingActionButton;
  final PreferredSizeWidget? appBar;
  final Widget? drawer;
  final Widget? endDrawer;
  final Color? backgroundColor;
  final bool extendBody;
  final bool extendBodyBehindAppBar;

  const ResponsiveLayout({
    super.key,
    required this.body,
    this.sidebar,
    this.bottomNavigationBar,
    this.floatingActionButton,
    this.appBar,
    this.drawer,
    this.endDrawer,
    this.backgroundColor,
    this.extendBody = false,
    this.extendBodyBehindAppBar = false,
  });

  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      builder: (context, deviceType) {
        switch (deviceType) {
          case DeviceType.mobile:
            return _buildMobileLayout(context);
          case DeviceType.tablet:
            return _buildTabletLayout(context);
          case DeviceType.desktop:
            return _buildDesktopLayout(context);
        }
      },
    );
  }

  /// 移动端布局
  Widget _buildMobileLayout(BuildContext context) {
    return Scaffold(
      appBar: appBar,
      body: ResponsiveContainer(
        child: body,
      ),
      bottomNavigationBar: bottomNavigationBar,
      floatingActionButton: floatingActionButton,
      drawer: drawer ?? sidebar,
      endDrawer: endDrawer,
      backgroundColor: backgroundColor,
      extendBody: extendBody,
      extendBodyBehindAppBar: extendBodyBehindAppBar,
    );
  }

  /// 平板布局
  Widget _buildTabletLayout(BuildContext context) {
    if (sidebar != null) {
      return Scaffold(
        appBar: appBar,
        body: Row(
          children: [
            // 侧边栏
            Container(
              width: ResponsiveUtils.getSidebarWidth(context),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                border: Border(
                  right: BorderSide(
                    color: Theme.of(context).dividerColor,
                    width: 1,
                  ),
                ),
              ),
              child: sidebar!,
            ),
            // 主内容区域
            Expanded(
              child: ResponsiveContainer(
                child: body,
              ),
            ),
          ],
        ),
        floatingActionButton: floatingActionButton,
        endDrawer: endDrawer,
        backgroundColor: backgroundColor,
        extendBody: extendBody,
        extendBodyBehindAppBar: extendBodyBehindAppBar,
      );
    }

    return _buildMobileLayout(context);
  }

  /// 桌面端布局
  Widget _buildDesktopLayout(BuildContext context) {
    if (sidebar != null) {
      return Scaffold(
        appBar: appBar,
        body: Row(
          children: [
            // 侧边栏
            Container(
              width: ResponsiveUtils.getSidebarWidth(context),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                border: Border(
                  right: BorderSide(
                    color: Theme.of(context).dividerColor,
                    width: 1,
                  ),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: ResponsiveUtils.getShadowBlurRadius(context),
                    offset: const Offset(2, 0),
                  ),
                ],
              ),
              child: sidebar!,
            ),
            // 主内容区域
            Expanded(
              child: Container(
                constraints: BoxConstraints(
                  maxWidth: ResponsiveUtils.getMaxContentWidth(context),
                ),
                child: ResponsiveContainer(
                  child: body,
                ),
              ),
            ),
          ],
        ),
        floatingActionButton: floatingActionButton,
        endDrawer: endDrawer,
        backgroundColor: backgroundColor,
        extendBody: extendBody,
        extendBodyBehindAppBar: extendBodyBehindAppBar,
      );
    }

    return Scaffold(
      appBar: appBar,
      body: Center(
        child: Container(
          constraints: BoxConstraints(
            maxWidth: ResponsiveUtils.getMaxContentWidth(context),
          ),
          child: ResponsiveContainer(
            child: body,
          ),
        ),
      ),
      floatingActionButton: floatingActionButton,
      drawer: drawer,
      endDrawer: endDrawer,
      backgroundColor: backgroundColor,
      extendBody: extendBody,
      extendBodyBehindAppBar: extendBodyBehindAppBar,
    );
  }
}

/// 响应式应用栏
class ResponsiveAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final Widget? leading;
  final bool automaticallyImplyLeading;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final double? elevation;
  final bool centerTitle;
  final Widget? flexibleSpace;
  final PreferredSizeWidget? bottom;

  const ResponsiveAppBar({
    super.key,
    required this.title,
    this.actions,
    this.leading,
    this.automaticallyImplyLeading = true,
    this.backgroundColor,
    this.foregroundColor,
    this.elevation,
    this.centerTitle = true,
    this.flexibleSpace,
    this.bottom,
  });

  @override
  Widget build(BuildContext context) {
    final iconSize = ResponsiveUtils.getResponsiveIconSize(context);

    return AppBar(
      title: ResponsiveText(
        title,
        baseFontSize: 20,
        fontWeight: FontWeight.w600,
      ),
      actions: actions?.map((action) {
        if (action is IconButton) {
          return IconButton(
            onPressed: action.onPressed,
            icon: action.icon,
            iconSize: iconSize,
            tooltip: action.tooltip,
          );
        }
        return action;
      }).toList(),
      leading: leading,
      automaticallyImplyLeading: automaticallyImplyLeading,
      backgroundColor: backgroundColor,
      foregroundColor: foregroundColor,
      elevation: elevation,
      centerTitle: centerTitle,
      flexibleSpace: flexibleSpace,
      bottom: bottom,
    );
  }

  @override
  Size get preferredSize {
    return Size.fromHeight(
      kToolbarHeight + (bottom?.preferredSize.height ?? 0),
    );
  }
}

/// 响应式底部导航栏
class ResponsiveBottomNavigationBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int>? onTap;
  final List<BottomNavigationBarItem> items;
  final BottomNavigationBarType? type;
  final Color? backgroundColor;
  final Color? selectedItemColor;
  final Color? unselectedItemColor;
  final double? selectedFontSize;
  final double? unselectedFontSize;
  final double? iconSize;

  const ResponsiveBottomNavigationBar({
    super.key,
    required this.currentIndex,
    required this.items,
    this.onTap,
    this.type,
    this.backgroundColor,
    this.selectedItemColor,
    this.unselectedItemColor,
    this.selectedFontSize,
    this.unselectedFontSize,
    this.iconSize,
  });

  @override
  Widget build(BuildContext context) {
    final responsiveIconSize = iconSize ?? ResponsiveUtils.getResponsiveIconSize(context);
    final responsiveSelectedFontSize = selectedFontSize ?? ResponsiveUtils.getResponsiveFontSize(
      context: context,
      baseFontSize: 12,
    );
    final responsiveUnselectedFontSize = unselectedFontSize ?? ResponsiveUtils.getResponsiveFontSize(
      context: context,
      baseFontSize: 10,
    );

    return Container(
      height: ResponsiveUtils.getBottomNavHeight(context),
      child: BottomNavigationBar(
        currentIndex: currentIndex,
        onTap: onTap,
        items: items,
        type: type ?? BottomNavigationBarType.fixed,
        backgroundColor: backgroundColor,
        selectedItemColor: selectedItemColor,
        unselectedItemColor: unselectedItemColor,
        selectedFontSize: responsiveSelectedFontSize,
        unselectedFontSize: responsiveUnselectedFontSize,
        iconSize: responsiveIconSize,
      ),
    );
  }
}

/// 响应式侧边栏
class ResponsiveSidebar extends StatelessWidget {
  final List<ResponsiveSidebarItem> items;
  final int? selectedIndex;
  final ValueChanged<int>? onItemTap;
  final Widget? header;
  final Widget? footer;
  final Color? backgroundColor;
  final EdgeInsets? padding;

  const ResponsiveSidebar({
    super.key,
    required this.items,
    this.selectedIndex,
    this.onItemTap,
    this.header,
    this.footer,
    this.backgroundColor,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final responsivePadding = padding ?? ResponsiveUtils.getContentPadding(context);

    return Container(
      color: backgroundColor ?? Theme.of(context).colorScheme.surface,
      child: Column(
        children: [
          if (header != null) header!,
          Expanded(
            child: ListView.builder(
              padding: responsivePadding,
              itemCount: items.length,
              itemBuilder: (context, index) {
                final item = items[index];
                final isSelected = selectedIndex == index;

                return ResponsiveSidebarTile(
                  item: item,
                  isSelected: isSelected,
                  onTap: () => onItemTap?.call(index),
                );
              },
            ),
          ),
          if (footer != null) footer!,
        ],
      ),
    );
  }
}

/// 响应式侧边栏项目
class ResponsiveSidebarItem {
  final String title;
  final IconData icon;
  final String? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;

  const ResponsiveSidebarItem({
    required this.title,
    required this.icon,
    this.subtitle,
    this.trailing,
    this.onTap,
  });
}

/// 响应式侧边栏瓦片
class ResponsiveSidebarTile extends StatelessWidget {
  final ResponsiveSidebarItem item;
  final bool isSelected;
  final VoidCallback? onTap;

  const ResponsiveSidebarTile({
    super.key,
    required this.item,
    required this.isSelected,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final iconSize = ResponsiveUtils.getResponsiveIconSize(context);
    final borderRadius = ResponsiveUtils.getBorderRadius(context);
    final listItemHeight = ResponsiveUtils.getListItemHeight(context);

    return Container(
      height: listItemHeight,
      margin: EdgeInsets.symmetric(vertical: 2.h),
      decoration: BoxDecoration(
        color: isSelected
            ? Theme.of(context).colorScheme.primaryContainer
            : Colors.transparent,
        borderRadius: BorderRadius.circular(borderRadius),
      ),
      child: ListTile(
        leading: Icon(
          item.icon,
          size: iconSize,
          color: isSelected
              ? Theme.of(context).colorScheme.onPrimaryContainer
              : Theme.of(context).colorScheme.onSurface,
        ),
        title: ResponsiveText(
          item.title,
          baseFontSize: 16,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
          color: isSelected
              ? Theme.of(context).colorScheme.onPrimaryContainer
              : Theme.of(context).colorScheme.onSurface,
        ),
        subtitle: item.subtitle != null
            ? ResponsiveText(
                item.subtitle!,
                baseFontSize: 12,
                color: isSelected
                    ? Theme.of(context).colorScheme.onPrimaryContainer.withOpacity(0.7)
                    : Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
              )
            : null,
        trailing: item.trailing,
        onTap: onTap ?? item.onTap,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(borderRadius),
        ),
        contentPadding: EdgeInsets.symmetric(
          horizontal: 16.w,
          vertical: 8.h,
        ),
      ),
    );
  }
}

/// 响应式卡片
class ResponsiveCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? margin;
  final EdgeInsets? padding;
  final Color? color;
  final double? elevation;
  final BorderRadius? borderRadius;
  final VoidCallback? onTap;
  final Border? border;

  const ResponsiveCard({
    super.key,
    required this.child,
    this.margin,
    this.padding,
    this.color,
    this.elevation,
    this.borderRadius,
    this.onTap,
    this.border,
  });

  @override
  Widget build(BuildContext context) {
    final responsiveMargin = margin ?? ResponsiveUtils.getCardMargin(context);
    final responsivePadding = padding ?? ResponsiveUtils.getContentPadding(context);
    final responsiveBorderRadius = borderRadius ?? BorderRadius.circular(ResponsiveUtils.getBorderRadius(context));

    Widget cardChild = Container(
      margin: responsiveMargin,
      padding: responsivePadding,
      decoration: BoxDecoration(
        color: color ?? Theme.of(context).cardColor,
        borderRadius: responsiveBorderRadius,
        border: border,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: ResponsiveUtils.getShadowBlurRadius(context),
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: child,
    );

    if (onTap != null) {
      cardChild = InkWell(
        onTap: onTap,
        borderRadius: responsiveBorderRadius,
        child: cardChild,
      );
    }

    return cardChild;
  }
}

/// 响应式列表瓦片
class ResponsiveListTile extends StatelessWidget {
  final Widget? leading;
  final Widget? title;
  final Widget? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;
  final EdgeInsets? contentPadding;
  final bool dense;
  final bool enabled;

  const ResponsiveListTile({
    super.key,
    this.leading,
    this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
    this.contentPadding,
    this.dense = false,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    final responsiveContentPadding = contentPadding ?? ResponsiveUtils.getContentPadding(context);
    final listItemHeight = ResponsiveUtils.getListItemHeight(context);

    return Container(
      height: dense ? listItemHeight * 0.8 : listItemHeight,
      child: ListTile(
        leading: leading,
        title: title,
        subtitle: subtitle,
        trailing: trailing,
        onTap: enabled ? onTap : null,
        contentPadding: responsiveContentPadding,
        dense: dense,
        enabled: enabled,
      ),
    );
  }
}

/// 响应式分隔线
class ResponsiveDivider extends StatelessWidget {
  final double? height;
  final double? thickness;
  final Color? color;
  final double? indent;
  final double? endIndent;

  const ResponsiveDivider({
    super.key,
    this.height,
    this.thickness,
    this.color,
    this.indent,
    this.endIndent,
  });

  @override
  Widget build(BuildContext context) {
    final responsiveHeight = height ?? ResponsiveUtils.getDividerHeight(context);
    final responsiveThickness = thickness ?? ResponsiveUtils.getDividerHeight(context);

    return Divider(
      height: responsiveHeight,
      thickness: responsiveThickness,
      color: color,
      indent: indent,
      endIndent: endIndent,
    );
  }
}