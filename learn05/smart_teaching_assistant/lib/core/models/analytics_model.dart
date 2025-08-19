import 'package:json_annotation/json_annotation.dart';

part 'analytics_model.g.dart';

/// 班级成绩统计模型
@JsonSerializable()
class ClassStatistics {
  final String classId;
  final String className;
  final String subjectId;
  final String subjectName;
  final double averageScore;
  final double maxScore;
  final double minScore;
  final double passRate;
  final double excellentRate;
  final int totalStudents;
  final int passedStudents;
  final int excellentStudents;
  final DateTime statisticsDate;
  final Map<String, dynamic>? distribution;

  const ClassStatistics({
    required this.classId,
    required this.className,
    required this.subjectId,
    required this.subjectName,
    required this.averageScore,
    required this.maxScore,
    required this.minScore,
    required this.passRate,
    required this.excellentRate,
    required this.totalStudents,
    required this.passedStudents,
    required this.excellentStudents,
    required this.statisticsDate,
    this.distribution,
  });

  factory ClassStatistics.fromJson(Map<String, dynamic> json) =>
      _$ClassStatisticsFromJson(json);

  Map<String, dynamic> toJson() => _$ClassStatisticsToJson(this);
}

/// 学生个人分析模型
@JsonSerializable()
class StudentAnalysis {
  final String studentId;
  final String studentName;
  final String subjectId;
  final String subjectName;
  final double currentScore;
  final double averageScore;
  final double bestScore;
  final double worstScore;
  final String trend; // 'improving', 'declining', 'stable'
  final int classRank;
  final int gradeRank;
  final List<String> strengths;
  final List<String> weaknesses;
  final List<String> recommendations;
  final DateTime analysisDate;
  final Map<String, dynamic>? details;

  const StudentAnalysis({
    required this.studentId,
    required this.studentName,
    required this.subjectId,
    required this.subjectName,
    required this.currentScore,
    required this.averageScore,
    required this.bestScore,
    required this.worstScore,
    required this.trend,
    required this.classRank,
    required this.gradeRank,
    required this.strengths,
    required this.weaknesses,
    required this.recommendations,
    required this.analysisDate,
    this.details,
  });

  factory StudentAnalysis.fromJson(Map<String, dynamic> json) =>
      _$StudentAnalysisFromJson(json);

  Map<String, dynamic> toJson() => _$StudentAnalysisToJson(this);
}

/// 年级排名分析模型
@JsonSerializable()
class GradeRankingAnalysis {
  final String gradeId;
  final String gradeName;
  final String subjectId;
  final String subjectName;
  final List<StudentRankingInfo> rankings;
  final double gradeAverage;
  final double gradeMax;
  final double gradeMin;
  final int totalStudents;
  final DateTime analysisDate;
  final Map<String, dynamic>? statistics;

  const GradeRankingAnalysis({
    required this.gradeId,
    required this.gradeName,
    required this.subjectId,
    required this.subjectName,
    required this.rankings,
    required this.gradeAverage,
    required this.gradeMax,
    required this.gradeMin,
    required this.totalStudents,
    required this.analysisDate,
    this.statistics,
  });

  factory GradeRankingAnalysis.fromJson(Map<String, dynamic> json) =>
      _$GradeRankingAnalysisFromJson(json);

  Map<String, dynamic> toJson() => _$GradeRankingAnalysisToJson(this);
}

/// 学生排名信息模型
@JsonSerializable()
class StudentRankingInfo {
  final String studentId;
  final String studentName;
  final String classId;
  final String className;
  final double score;
  final int rank;
  final double percentile;

  const StudentRankingInfo({
    required this.studentId,
    required this.studentName,
    required this.classId,
    required this.className,
    required this.score,
    required this.rank,
    required this.percentile,
  });

  factory StudentRankingInfo.fromJson(Map<String, dynamic> json) =>
      _$StudentRankingInfoFromJson(json);

  Map<String, dynamic> toJson() => _$StudentRankingInfoToJson(this);
}

/// 趋势分析数据模型
@JsonSerializable()
class TrendAnalysisData {
  final String entityId; // 学生ID或班级ID
  final String entityType; // 'student' 或 'class'
  final String subjectId;
  final String subjectName;
  final List<TrendDataPoint> dataPoints;
  final String trendDirection; // 'up', 'down', 'stable'
  final double trendSlope;
  final double correlation;
  final DateTime analysisDate;
  final Map<String, dynamic>? metadata;

  const TrendAnalysisData({
    required this.entityId,
    required this.entityType,
    required this.subjectId,
    required this.subjectName,
    required this.dataPoints,
    required this.trendDirection,
    required this.trendSlope,
    required this.correlation,
    required this.analysisDate,
    this.metadata,
  });

  factory TrendAnalysisData.fromJson(Map<String, dynamic> json) =>
      _$TrendAnalysisDataFromJson(json);

  Map<String, dynamic> toJson() => _$TrendAnalysisDataToJson(this);
}

/// 趋势数据点模型
@JsonSerializable()
class TrendDataPoint {
  final DateTime date;
  final double value;
  final String? label;
  final Map<String, dynamic>? metadata;

  const TrendDataPoint({
    required this.date,
    required this.value,
    this.label,
    this.metadata,
  });

  factory TrendDataPoint.fromJson(Map<String, dynamic> json) =>
      _$TrendDataPointFromJson(json);

  Map<String, dynamic> toJson() => _$TrendDataPointToJson(this);
}

/// 对比分析结果模型
@JsonSerializable()
class ComparisonAnalysisResult {
  final String comparisonType; // 'student_vs_class', 'class_vs_grade', etc.
  final String subjectId;
  final String subjectName;
  final ComparisonEntity entity1;
  final ComparisonEntity entity2;
  final double scoreDifference;
  final double percentageDifference;
  final String comparisonResult; // 'better', 'worse', 'equal'
  final List<String> insights;
  final DateTime analysisDate;
  final Map<String, dynamic>? details;

  const ComparisonAnalysisResult({
    required this.comparisonType,
    required this.subjectId,
    required this.subjectName,
    required this.entity1,
    required this.entity2,
    required this.scoreDifference,
    required this.percentageDifference,
    required this.comparisonResult,
    required this.insights,
    required this.analysisDate,
    this.details,
  });

  factory ComparisonAnalysisResult.fromJson(Map<String, dynamic> json) =>
      _$ComparisonAnalysisResultFromJson(json);

  Map<String, dynamic> toJson() => _$ComparisonAnalysisResultToJson(this);
}

/// 对比实体模型
@JsonSerializable()
class ComparisonEntity {
  final String id;
  final String name;
  final String type; // 'student', 'class', 'grade'
  final double score;
  final int? rank;
  final Map<String, dynamic>? metadata;

  const ComparisonEntity({
    required this.id,
    required this.name,
    required this.type,
    required this.score,
    this.rank,
    this.metadata,
  });

  factory ComparisonEntity.fromJson(Map<String, dynamic> json) =>
      _$ComparisonEntityFromJson(json);

  Map<String, dynamic> toJson() => _$ComparisonEntityToJson(this);
}