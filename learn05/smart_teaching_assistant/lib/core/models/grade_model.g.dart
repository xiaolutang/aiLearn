// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'grade_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Grade _$GradeFromJson(Map<String, dynamic> json) => Grade(
      id: json['id'] as String,
      studentId: json['studentId'] as String,
      studentName: json['studentName'] as String,
      subjectId: json['subjectId'] as String,
      subjectName: json['subjectName'] as String,
      examId: json['examId'] as String,
      examName: json['examName'] as String,
      score: (json['score'] as num).toDouble(),
      totalScore: (json['totalScore'] as num).toDouble(),
      rank: json['rank'] as String?,
      level: json['level'] as String?,
      examDate: DateTime.parse(json['examDate'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      remark: json['remark'] as String?,
    );

Map<String, dynamic> _$GradeToJson(Grade instance) => <String, dynamic>{
      'id': instance.id,
      'studentId': instance.studentId,
      'studentName': instance.studentName,
      'subjectId': instance.subjectId,
      'subjectName': instance.subjectName,
      'examId': instance.examId,
      'examName': instance.examName,
      'score': instance.score,
      'totalScore': instance.totalScore,
      'rank': instance.rank,
      'level': instance.level,
      'examDate': instance.examDate.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'remark': instance.remark,
    };

Exam _$ExamFromJson(Map<String, dynamic> json) => Exam(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      classId: json['classId'] as String,
      className: json['className'] as String,
      examDate: DateTime.parse(json['examDate'] as String),
      status: json['status'] as String,
      subjects: (json['subjects'] as List<dynamic>)
          .map((e) => Subject.fromJson(e as Map<String, dynamic>))
          .toList(),
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$ExamToJson(Exam instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'classId': instance.classId,
      'className': instance.className,
      'examDate': instance.examDate.toIso8601String(),
      'status': instance.status,
      'subjects': instance.subjects,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };

Subject _$SubjectFromJson(Map<String, dynamic> json) => Subject(
      id: json['id'] as String,
      name: json['name'] as String,
      code: json['code'] as String,
      totalScore: (json['totalScore'] as num).toDouble(),
      description: json['description'] as String?,
      isRequired: json['isRequired'] as bool? ?? true,
    );

Map<String, dynamic> _$SubjectToJson(Subject instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'code': instance.code,
      'totalScore': instance.totalScore,
      'description': instance.description,
      'isRequired': instance.isRequired,
    };

GradeStatistics _$GradeStatisticsFromJson(Map<String, dynamic> json) =>
    GradeStatistics(
      examId: json['examId'] as String,
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
      levelDistribution:
          Map<String, int>.from(json['levelDistribution'] as Map),
    );

Map<String, dynamic> _$GradeStatisticsToJson(GradeStatistics instance) =>
    <String, dynamic>{
      'examId': instance.examId,
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
      'levelDistribution': instance.levelDistribution,
    };

StudentGradeAnalysis _$StudentGradeAnalysisFromJson(
        Map<String, dynamic> json) =>
    StudentGradeAnalysis(
      studentId: json['studentId'] as String,
      studentName: json['studentName'] as String,
      grades: (json['grades'] as List<dynamic>)
          .map((e) => Grade.fromJson(e as Map<String, dynamic>))
          .toList(),
      averageScore: (json['averageScore'] as num).toDouble(),
      overallLevel: json['overallLevel'] as String,
      strengths:
          (json['strengths'] as List<dynamic>).map((e) => e as String).toList(),
      weaknesses: (json['weaknesses'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      recommendations: (json['recommendations'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      subjectAverages: (json['subjectAverages'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, (e as num).toDouble()),
      ),
      subjectTrends: Map<String, String>.from(json['subjectTrends'] as Map),
    );

Map<String, dynamic> _$StudentGradeAnalysisToJson(
        StudentGradeAnalysis instance) =>
    <String, dynamic>{
      'studentId': instance.studentId,
      'studentName': instance.studentName,
      'grades': instance.grades,
      'averageScore': instance.averageScore,
      'overallLevel': instance.overallLevel,
      'strengths': instance.strengths,
      'weaknesses': instance.weaknesses,
      'recommendations': instance.recommendations,
      'subjectAverages': instance.subjectAverages,
      'subjectTrends': instance.subjectTrends,
    };

GradeInputRequest _$GradeInputRequestFromJson(Map<String, dynamic> json) =>
    GradeInputRequest(
      examId: json['examId'] as String,
      subjectId: json['subjectId'] as String,
      grades: (json['grades'] as List<dynamic>)
          .map((e) => StudentGradeInput.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$GradeInputRequestToJson(GradeInputRequest instance) =>
    <String, dynamic>{
      'examId': instance.examId,
      'subjectId': instance.subjectId,
      'grades': instance.grades,
    };

StudentGradeInput _$StudentGradeInputFromJson(Map<String, dynamic> json) =>
    StudentGradeInput(
      studentId: json['studentId'] as String,
      score: (json['score'] as num).toDouble(),
      remark: json['remark'] as String?,
    );

Map<String, dynamic> _$StudentGradeInputToJson(StudentGradeInput instance) =>
    <String, dynamic>{
      'studentId': instance.studentId,
      'score': instance.score,
      'remark': instance.remark,
    };

GradeQueryParams _$GradeQueryParamsFromJson(Map<String, dynamic> json) =>
    GradeQueryParams(
      studentId: json['studentId'] as String?,
      classId: json['classId'] as String?,
      examId: json['examId'] as String?,
      subjectId: json['subjectId'] as String?,
      startDate: json['startDate'] == null
          ? null
          : DateTime.parse(json['startDate'] as String),
      endDate: json['endDate'] == null
          ? null
          : DateTime.parse(json['endDate'] as String),
      page: json['page'] as int? ?? 1,
      pageSize: json['pageSize'] as int? ?? 20,
      sortBy: json['sortBy'] as String?,
      sortOrder: json['sortOrder'] as String? ?? 'desc',
    );

Map<String, dynamic> _$GradeQueryParamsToJson(GradeQueryParams instance) =>
    <String, dynamic>{
      'studentId': instance.studentId,
      'classId': instance.classId,
      'examId': instance.examId,
      'subjectId': instance.subjectId,
      'startDate': instance.startDate?.toIso8601String(),
      'endDate': instance.endDate?.toIso8601String(),
      'page': instance.page,
      'pageSize': instance.pageSize,
      'sortBy': instance.sortBy,
      'sortOrder': instance.sortOrder,
    };

GradeResponse _$GradeResponseFromJson(Map<String, dynamic> json) =>
    GradeResponse(
      grades: (json['grades'] as List<dynamic>)
          .map((e) => Grade.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: json['total'] as int,
      page: json['page'] as int,
      pageSize: json['pageSize'] as int,
      hasMore: json['hasMore'] as bool,
    );

Map<String, dynamic> _$GradeResponseToJson(GradeResponse instance) =>
    <String, dynamic>{
      'grades': instance.grades,
      'total': instance.total,
      'page': instance.page,
      'pageSize': instance.pageSize,
      'hasMore': instance.hasMore,
    };
