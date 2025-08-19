import 'package:flutter/material.dart';
import '../../../../core/models/grade_model.dart';
import '../../../../shared/themes/app_theme.dart';

class GradeStatisticsCard extends StatelessWidget {
  final GradeStatistics statistics;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry? margin;

  const GradeStatisticsCard({
    Key? key,
    required this.statistics,
    this.onTap,
    this.margin,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: margin ?? const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '成绩统计',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${statistics.totalStudents}人',
                      style: TextStyle(
                        color: AppTheme.primaryColor,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _buildStatItem(
                      '平均分',
                      statistics.averageScore.toStringAsFixed(1),
                      Icons.trending_up,
                      _getScoreColor(statistics.averageScore / 100.0),
                    ),
                  ),
                  Expanded(
                    child: _buildStatItem(
                      '最高分',
                      statistics.maxScore.toStringAsFixed(1),
                      Icons.star,
                      AppTheme.successColor,
                    ),
                  ),
                  Expanded(
                    child: _buildStatItem(
                      '最低分',
                      statistics.minScore.toStringAsFixed(1),
                      Icons.trending_down,
                      AppTheme.errorColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _buildStatItem(
                      '总数',
                      '${statistics.totalStudents}',
                      Icons.check_circle,
                      AppTheme.primaryColor,
                    ),
                  ),
                  Expanded(
                    child: _buildStatItem(
                      '及格率',
                      '${(statistics.passRate * 100).toStringAsFixed(1)}%',
                      Icons.emoji_events,
                      _getPassRateColor(statistics.passRate),
                    ),
                  ),
                  Expanded(
                    child: _buildStatItem(
                      '优秀率',
                      '${(statistics.excellentRate * 100).toStringAsFixed(1)}%',
                      Icons.analytics,
                      _getExcellentRateColor(statistics.excellentRate),
                    ),
                  ),
                ],
              ),
              // 统计信息已完整显示
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(
          icon,
          color: color,
          size: 20,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: AppTheme.textSecondaryColor,
          ),
        ),
      ],
    );
  }

  Color _getScoreColor(double scoreRate) {
    if (scoreRate >= 0.9) {
      return AppTheme.successColor;
    } else if (scoreRate >= 0.8) {
      return AppTheme.primaryColor;
    } else if (scoreRate >= 0.6) {
      return AppTheme.warningColor;
    } else {
      return AppTheme.errorColor;
    }
  }

  Color _getPassRateColor(double passRate) {
    if (passRate >= 0.9) {
      return AppTheme.successColor;
    } else if (passRate >= 0.7) {
      return AppTheme.primaryColor;
    } else if (passRate >= 0.5) {
      return AppTheme.warningColor;
    } else {
      return AppTheme.errorColor;
    }
  }

  Color _getExcellentRateColor(double excellentRate) {
    if (excellentRate >= 0.5) {
      return AppTheme.successColor;
    } else if (excellentRate >= 0.3) {
      return AppTheme.primaryColor;
    } else if (excellentRate >= 0.1) {
      return AppTheme.warningColor;
    } else {
      return AppTheme.errorColor;
    }
  }
}