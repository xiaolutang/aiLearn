// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'analytics_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ClassStatistics _$ClassStatisticsFromJson(Map<String, dynamic> json) =>
    ClassStatistics(
      classId: json['classId'] as String,
      className: json['className'] as String,
      subjectId: json['subjectId'] as String,
      subjectName: json['subjectName'] as String,
      averageScore: (json['averageScore'] as num).toDouble(),
      maxScore: (json['maxScore'] as num).toDouble(),
      minScore: (json['minScore'] as num).toDouble(),
      passRate: (json['passRate'] as num).toDouble(),
      excellentRate: (json['excellentRate'] as num).toDouble(),
      totalStudents: json['totalStudents'] as int,
      passedStudents: json['passedStudents'] as int,
      excellentStudents: json['excellentStudents'] as int,
      statisticsDate: DateTime.parse(json['statisticsDate'] as String),
      distribution: json['distribution'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ClassStatisticsToJson(ClassStatistics instance) =>
    <String, dynamic>{
      'classId': instance.classId,
      'className': instance.className,
      'subjectId': instance.subjectId,
      'subjectName': instance.subjectName,
      'averageScore': instance.averageScore,
      'maxScore': instance.maxScore,
      'minScore': instance.minScore,
      'passRate': instance.passRate,
      'excellentRate': instance.excellentRate,
      'totalStudents': instance.totalStudents,
      'passedStudents': instance.passedStudents,
      'excellentStudents': instance.excellentStudents,
      'statisticsDate': instance.statisticsDate.toIso8601String(),
      'distribution': instance.distribution,
    };

StudentAnalysis _$StudentAnalysisFromJson(Map<String, dynamic> json) =>
    StudentAnalysis(
      studentId: json['studentId'] as String,
      studentName: json['studentName'] as String,
      subjectId: json['subjectId'] as String,
      subjectName: json['subjectName'] as String,
      currentScore: (json['currentScore'] as num).toDouble(),
      averageScore: (json['averageScore'] as num).toDouble(),
      bestScore: (json['bestScore'] as num).toDouble(),
      worstScore: (json['worstScore'] as num).toDouble(),
      trend: json['trend'] as String,
      classRank: json['classRank'] as int,
      gradeRank: json['gradeRank'] as int,
      strengths:
          (json['strengths'] as List<dynamic>).map((e) => e as String).toList(),
      weaknesses: (json['weaknesses'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      recommendations: (json['recommendations'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      analysisDate: DateTime.parse(json['analysisDate'] as String),
      details: json['details'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$StudentAnalysisToJson(StudentAnalysis instance) =>
    <String, dynamic>{
      'studentId': instance.studentId,
      'studentName': instance.studentName,
      'subjectId': instance.subjectId,
      'subjectName': instance.subjectName,
      'currentScore': instance.currentScore,
      'averageScore': instance.averageScore,
      'bestScore': instance.bestScore,
      'worstScore': instance.worstScore,
      'trend': instance.trend,
      'classRank': instance.classRank,
      'gradeRank': instance.gradeRank,
      'strengths': instance.strengths,
      'weaknesses': instance.weaknesses,
      'recommendations': instance.recommendations,
      'analysisDate': instance.analysisDate.toIso8601String(),
      'details': instance.details,
    };

GradeRankingAnalysis _$GradeRankingAnalysisFromJson(
        Map<String, dynamic> json) =>
    GradeRankingAnalysis(
      gradeId: json['gradeId'] as String,
      gradeName: json['gradeName'] as String,
      subjectId: json['subjectId'] as String,
      subjectName: json['subjectName'] as String,
      rankings: (json['rankings'] as List<dynamic>)
          .map((e) => StudentRankingInfo.fromJson(e as Map<String, dynamic>))
          .toList(),
      gradeAverage: (json['gradeAverage'] as num).toDouble(),
      gradeMax: (json['gradeMax'] as num).toDouble(),
      gradeMin: (json['gradeMin'] as num).toDouble(),
      totalStudents: json['totalStudents'] as int,
      analysisDate: DateTime.parse(json['analysisDate'] as String),
      statistics: json['statistics'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$GradeRankingAnalysisToJson(
        GradeRankingAnalysis instance) =>
    <String, dynamic>{
      'gradeId': instance.gradeId,
      'gradeName': instance.gradeName,
      'subjectId': instance.subjectId,
      'subjectName': instance.subjectName,
      'rankings': instance.rankings,
      'gradeAverage': instance.gradeAverage,
      'gradeMax': instance.gradeMax,
      'gradeMin': instance.gradeMin,
      'totalStudents': instance.totalStudents,
      'analysisDate': instance.analysisDate.toIso8601String(),
      'statistics': instance.statistics,
    };

StudentRankingInfo _$StudentRankingInfoFromJson(Map<String, dynamic> json) =>
    StudentRankingInfo(
      studentId: json['studentId'] as String,
      studentName: json['studentName'] as String,
      classId: json['classId'] as String,
      className: json['className'] as String,
      score: (json['score'] as num).toDouble(),
      rank: json['rank'] as int,
      percentile: (json['percentile'] as num).toDouble(),
    );

Map<String, dynamic> _$StudentRankingInfoToJson(StudentRankingInfo instance) =>
    <String, dynamic>{
      'studentId': instance.studentId,
      'studentName': instance.studentName,
      'classId': instance.classId,
      'className': instance.className,
      'score': instance.score,
      'rank': instance.rank,
      'percentile': instance.percentile,
    };

TrendAnalysisData _$TrendAnalysisDataFromJson(Map<String, dynamic> json) =>
    TrendAnalysisData(
      entityId: json['entityId'] as String,
      entityType: json['entityType'] as String,
      subjectId: json['subjectId'] as String,
      subjectName: json['subjectName'] as String,
      dataPoints: (json['dataPoints'] as List<dynamic>)
          .map((e) => TrendDataPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
      trendDirection: json['trendDirection'] as String,
      trendSlope: (json['trendSlope'] as num).toDouble(),
      correlation: (json['correlation'] as num).toDouble(),
      analysisDate: DateTime.parse(json['analysisDate'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$TrendAnalysisDataToJson(TrendAnalysisData instance) =>
    <String, dynamic>{
      'entityId': instance.entityId,
      'entityType': instance.entityType,
      'subjectId': instance.subjectId,
      'subjectName': instance.subjectName,
      'dataPoints': instance.dataPoints,
      'trendDirection': instance.trendDirection,
      'trendSlope': instance.trendSlope,
      'correlation': instance.correlation,
      'analysisDate': instance.analysisDate.toIso8601String(),
      'metadata': instance.metadata,
    };

TrendDataPoint _$TrendDataPointFromJson(Map<String, dynamic> json) =>
    TrendDataPoint(
      date: DateTime.parse(json['date'] as String),
      value: (json['value'] as num).toDouble(),
      label: json['label'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$TrendDataPointToJson(TrendDataPoint instance) =>
    <String, dynamic>{
      'date': instance.date.toIso8601String(),
      'value': instance.value,
      'label': instance.label,
      'metadata': instance.metadata,
    };

ComparisonAnalysisResult _$ComparisonAnalysisResultFromJson(
        Map<String, dynamic> json) =>
    ComparisonAnalysisResult(
      comparisonType: json['comparisonType'] as String,
      subjectId: json['subjectId'] as String,
      subjectName: json['subjectName'] as String,
      entity1:
          ComparisonEntity.fromJson(json['entity1'] as Map<String, dynamic>),
      entity2:
          ComparisonEntity.fromJson(json['entity2'] as Map<String, dynamic>),
      scoreDifference: (json['scoreDifference'] as num).toDouble(),
      percentageDifference: (json['percentageDifference'] as num).toDouble(),
      comparisonResult: json['comparisonResult'] as String,
      insights:
          (json['insights'] as List<dynamic>).map((e) => e as String).toList(),
      analysisDate: DateTime.parse(json['analysisDate'] as String),
      details: json['details'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ComparisonAnalysisResultToJson(
        ComparisonAnalysisResult instance) =>
    <String, dynamic>{
      'comparisonType': instance.comparisonType,
      'subjectId': instance.subjectId,
      'subjectName': instance.subjectName,
      'entity1': instance.entity1,
      'entity2': instance.entity2,
      'scoreDifference': instance.scoreDifference,
      'percentageDifference': instance.percentageDifference,
      'comparisonResult': instance.comparisonResult,
      'insights': instance.insights,
      'analysisDate': instance.analysisDate.toIso8601String(),
      'details': instance.details,
    };

ComparisonEntity _$ComparisonEntityFromJson(Map<String, dynamic> json) =>
    ComparisonEntity(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      score: (json['score'] as num).toDouble(),
      rank: json['rank'] as int?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ComparisonEntityToJson(ComparisonEntity instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'type': instance.type,
      'score': instance.score,
      'rank': instance.rank,
      'metadata': instance.metadata,
    };
