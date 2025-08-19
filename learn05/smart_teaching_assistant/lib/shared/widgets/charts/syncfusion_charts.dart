import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_charts/charts.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

/// Syncfusion图表组件集合
/// 提供更高级的数据可视化图表

/// 高级折线图
class AdvancedLineChart extends StatelessWidget {
  final List<ChartSeries> series;
  final String title;
  final String xAxisTitle;
  final String yAxisTitle;
  final double height;
  final bool enableZooming;
  final bool enableTooltip;

  const AdvancedLineChart({
    super.key,
    required this.series,
    this.title = '数据趋势图',
    this.xAxisTitle = 'X轴',
    this.yAxisTitle = 'Y轴',
    this.height = 300,
    this.enableZooming = true,
    this.enableTooltip = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height.h,
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          SizedBox(height: 16.h),
          Expanded(
            child: SfCartesianChart(
              primaryXAxis: CategoryAxis(
                title: AxisTitle(text: xAxisTitle),
                majorGridLines: const MajorGridLines(width: 0),
              ),
              primaryYAxis: NumericAxis(
                title: AxisTitle(text: yAxisTitle),
                axisLine: const AxisLine(width: 0),
                majorTickLines: const MajorTickLines(size: 0),
              ),
              tooltipBehavior: enableTooltip ? TooltipBehavior(enable: true) : null,
              zoomPanBehavior: enableZooming
                  ? ZoomPanBehavior(
                      enablePinching: true,
                      enablePanning: true,
                      enableDoubleTapZooming: true,
                    )
                  : null,
              series: series,
            ),
          ),
        ],
      ),
    );
  }
}

/// 高级柱状图
class AdvancedColumnChart extends StatelessWidget {
  final List<ChartSeries> series;
  final String title;
  final String xAxisTitle;
  final String yAxisTitle;
  final double height;
  final bool enableAnimation;
  final bool enableTooltip;

  const AdvancedColumnChart({
    super.key,
    required this.series,
    this.title = '柱状图',
    this.xAxisTitle = 'X轴',
    this.yAxisTitle = 'Y轴',
    this.height = 300,
    this.enableAnimation = true,
    this.enableTooltip = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height.h,
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          SizedBox(height: 16.h),
          Expanded(
            child: SfCartesianChart(
              primaryXAxis: CategoryAxis(
                title: AxisTitle(text: xAxisTitle),
                majorGridLines: const MajorGridLines(width: 0),
              ),
              primaryYAxis: NumericAxis(
                title: AxisTitle(text: yAxisTitle),
                axisLine: const AxisLine(width: 0),
                majorTickLines: const MajorTickLines(size: 0),
              ),
              tooltipBehavior: enableTooltip ? TooltipBehavior(enable: true) : null,
              series: series,
            ),
          ),
        ],
      ),
    );
  }
}

/// 高级饼图
class AdvancedPieChart extends StatelessWidget {
  final List<PieSeries> series;
  final String title;
  final double height;
  final bool enableTooltip;
  final bool enableLegend;

  const AdvancedPieChart({
    super.key,
    required this.series,
    this.title = '饼图',
    this.height = 300,
    this.enableTooltip = true,
    this.enableLegend = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height.h,
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          SizedBox(height: 16.h),
          Expanded(
            child: SfCircularChart(
              tooltipBehavior: enableTooltip ? TooltipBehavior(enable: true) : null,
              legend: enableLegend
                  ? Legend(
                      isVisible: true,
                      position: LegendPosition.bottom,
                    )
                  : null,
              series: series,
            ),
          ),
        ],
      ),
    );
  }
}

/// 散点图
class ScatterChart extends StatelessWidget {
  final List<ChartSeries> series;
  final String title;
  final String xAxisTitle;
  final String yAxisTitle;
  final double height;
  final bool enableTooltip;

  const ScatterChart({
    super.key,
    required this.series,
    this.title = '散点图',
    this.xAxisTitle = 'X轴',
    this.yAxisTitle = 'Y轴',
    this.height = 300,
    this.enableTooltip = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height.h,
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          SizedBox(height: 16.h),
          Expanded(
            child: SfCartesianChart(
              primaryXAxis: NumericAxis(
                title: AxisTitle(text: xAxisTitle),
                majorGridLines: const MajorGridLines(width: 0),
              ),
              primaryYAxis: NumericAxis(
                title: AxisTitle(text: yAxisTitle),
                axisLine: const AxisLine(width: 0),
                majorTickLines: const MajorTickLines(size: 0),
              ),
              tooltipBehavior: enableTooltip ? TooltipBehavior(enable: true) : null,
              series: series,
            ),
          ),
        ],
      ),
    );
  }
}

/// 面积图
class AreaChart extends StatelessWidget {
  final List<ChartSeries> series;
  final String title;
  final String xAxisTitle;
  final String yAxisTitle;
  final double height;
  final bool enableTooltip;

  const AreaChart({
    super.key,
    required this.series,
    this.title = '面积图',
    this.xAxisTitle = 'X轴',
    this.yAxisTitle = 'Y轴',
    this.height = 300,
    this.enableTooltip = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height.h,
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          SizedBox(height: 16.h),
          Expanded(
            child: SfCartesianChart(
              primaryXAxis: CategoryAxis(
                title: AxisTitle(text: xAxisTitle),
                majorGridLines: const MajorGridLines(width: 0),
              ),
              primaryYAxis: NumericAxis(
                title: AxisTitle(text: yAxisTitle),
                axisLine: const AxisLine(width: 0),
                majorTickLines: const MajorTickLines(size: 0),
              ),
              tooltipBehavior: enableTooltip ? TooltipBehavior(enable: true) : null,
              series: series,
            ),
          ),
        ],
      ),
    );
  }
}

/// 组合图表
class CombinationChart extends StatelessWidget {
  final List<ChartSeries> series;
  final String title;
  final String xAxisTitle;
  final String primaryYAxisTitle;
  final String? secondaryYAxisTitle;
  final double height;
  final bool enableTooltip;

  const CombinationChart({
    super.key,
    required this.series,
    this.title = '组合图表',
    this.xAxisTitle = 'X轴',
    this.primaryYAxisTitle = '主Y轴',
    this.secondaryYAxisTitle,
    this.height = 300,
    this.enableTooltip = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height.h,
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          SizedBox(height: 16.h),
          Expanded(
            child: SfCartesianChart(
              primaryXAxis: CategoryAxis(
                title: AxisTitle(text: xAxisTitle),
                majorGridLines: const MajorGridLines(width: 0),
              ),
              primaryYAxis: NumericAxis(
                title: AxisTitle(text: primaryYAxisTitle),
                axisLine: const AxisLine(width: 0),
                majorTickLines: const MajorTickLines(size: 0),
              ),
              axes: secondaryYAxisTitle != null
                  ? [
                      NumericAxis(
                        name: 'yAxis1',
                        opposedPosition: true,
                        title: AxisTitle(text: secondaryYAxisTitle!),
                        axisLine: const AxisLine(width: 0),
                        majorTickLines: const MajorTickLines(size: 0),
                      ),
                    ]
                  : null,
              tooltipBehavior: enableTooltip ? TooltipBehavior(enable: true) : null,
              legend: Legend(isVisible: true),
              series: series,
            ),
          ),
        ],
      ),
    );
  }
}

/// 数据模型类
class ChartData {
  final String x;
  final double y;
  final Color? color;

  ChartData(this.x, this.y, [this.color]);
}

/// 多系列数据模型
class MultiSeriesData {
  final String x;
  final double y1;
  final double y2;
  final double? y3;

  MultiSeriesData(this.x, this.y1, this.y2, [this.y3]);
}

/// 散点数据模型
class ScatterData {
  final double x;
  final double y;
  final double? size;
  final Color? color;

  ScatterData(this.x, this.y, [this.size, this.color]);
}

/// 图表工具类
class ChartUtils {
  /// 创建折线图系列
  static LineSeries<ChartData, String> createLineSeries({
    required List<ChartData> data,
    required String name,
    Color color = Colors.blue,
    double width = 2,
    bool enableMarkers = true,
  }) {
    return LineSeries<ChartData, String>(
      dataSource: data,
      xValueMapper: (ChartData data, _) => data.x,
      yValueMapper: (ChartData data, _) => data.y,
      name: name,
      color: color,
      width: width,
      markerSettings: enableMarkers
          ? MarkerSettings(
              isVisible: true,
              color: color,
              borderColor: Colors.white,
              borderWidth: 2,
            )
          : const MarkerSettings(isVisible: false),
    );
  }

  /// 创建柱状图系列
  static ColumnSeries<ChartData, String> createColumnSeries({
    required List<ChartData> data,
    required String name,
    Color color = Colors.green,
    double spacing = 0.2,
  }) {
    return ColumnSeries<ChartData, String>(
      dataSource: data,
      xValueMapper: (ChartData data, _) => data.x,
      yValueMapper: (ChartData data, _) => data.y,
      name: name,
      color: color,
      spacing: spacing,
      borderRadius: BorderRadius.circular(4),
    );
  }

  /// 创建饼图系列
  static PieSeries<ChartData, String> createPieSeries({
    required List<ChartData> data,
    bool showLabels = true,
    bool showPercentage = true,
  }) {
    return PieSeries<ChartData, String>(
      dataSource: data,
      xValueMapper: (ChartData data, _) => data.x,
      yValueMapper: (ChartData data, _) => data.y,
      pointColorMapper: (ChartData data, _) => data.color,
      dataLabelSettings: DataLabelSettings(
        isVisible: showLabels,
        labelPosition: ChartDataLabelPosition.outside,
      ),
      explode: true,
      explodeIndex: 0,
    );
  }

  /// 创建散点图系列
  static ScatterSeries<ScatterData, double> createScatterSeries({
    required List<ScatterData> data,
    required String name,
    Color color = Colors.orange,
  }) {
    return ScatterSeries<ScatterData, double>(
      dataSource: data,
      xValueMapper: (ScatterData data, _) => data.x,
      yValueMapper: (ScatterData data, _) => data.y,
      pointColorMapper: (ScatterData data, _) => data.color ?? color,
      name: name,
    );
  }

  /// 创建面积图系列
  static AreaSeries<ChartData, String> createAreaSeries({
    required List<ChartData> data,
    required String name,
    Color color = Colors.purple,
    double opacity = 0.7,
  }) {
    return AreaSeries<ChartData, String>(
      dataSource: data,
      xValueMapper: (ChartData data, _) => data.x,
      yValueMapper: (ChartData data, _) => data.y,
      name: name,
      color: color.withOpacity(opacity),
      borderColor: color,
      borderWidth: 2,
    );
  }

  /// 生成示例数据
  static List<ChartData> generateSampleData() {
    return [
      ChartData('1月', 65),
      ChartData('2月', 70),
      ChartData('3月', 75),
      ChartData('4月', 80),
      ChartData('5月', 85),
      ChartData('6月', 90),
    ];
  }

  /// 生成成绩分布数据
  static List<ChartData> generateGradeDistribution() {
    return [
      ChartData('优秀', 25, Colors.green),
      ChartData('良好', 35, Colors.blue),
      ChartData('中等', 25, Colors.orange),
      ChartData('及格', 10, Colors.yellow),
      ChartData('不及格', 5, Colors.red),
    ];
  }

  /// 生成多系列数据
  static List<MultiSeriesData> generateMultiSeriesData() {
    return [
      MultiSeriesData('1月', 65, 70, 60),
      MultiSeriesData('2月', 70, 75, 65),
      MultiSeriesData('3月', 75, 80, 70),
      MultiSeriesData('4月', 80, 85, 75),
      MultiSeriesData('5月', 85, 90, 80),
      MultiSeriesData('6月', 90, 95, 85),
    ];
  }
}