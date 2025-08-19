// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'exam_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Exam _$ExamFromJson(Map<String, dynamic> json) => Exam(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      type: json['type'] as String,
      subjectId: json['subjectId'] as String,
      subjectName: json['subjectName'] as String,
      classId: json['classId'] as String,
      className: json['className'] as String,
      examDate: DateTime.parse(json['examDate'] as String),
      duration: json['duration'] as int,
      totalScore: (json['totalScore'] as num).toDouble(),
      status: json['status'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      createdBy: json['createdBy'] as String,
      settings: json['settings'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ExamToJson(Exam instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'type': instance.type,
      'subjectId': instance.subjectId,
      'subjectName': instance.subjectName,
      'classId': instance.classId,
      'className': instance.className,
      'examDate': instance.examDate.toIso8601String(),
      'duration': instance.duration,
      'totalScore': instance.totalScore,
      'status': instance.status,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'createdBy': instance.createdBy,
      'settings': instance.settings,
    };

Subject _$SubjectFromJson(Map<String, dynamic> json) => Subject(
      id: json['id'] as String,
      name: json['name'] as String,
      code: json['code'] as String,
      description: json['description'] as String,
      category: json['category'] as String,
      credits: json['credits'] as int,
      gradeLevel: json['gradeLevel'] as String,
      teacherId: json['teacherId'] as String,
      teacherName: json['teacherName'] as String?,
      isActive: json['isActive'] as bool,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$SubjectToJson(Subject instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'code': instance.code,
      'description': instance.description,
      'category': instance.category,
      'credits': instance.credits,
      'gradeLevel': instance.gradeLevel,
      'teacherId': instance.teacherId,
      'teacherName': instance.teacherName,
      'isActive': instance.isActive,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'metadata': instance.metadata,
    };

ExamStatistics _$ExamStatisticsFromJson(Map<String, dynamic> json) =>
    ExamStatistics(
      examId: json['examId'] as String,
      examName: json['examName'] as String,
      totalStudents: json['totalStudents'] as int,
      submittedCount: json['submittedCount'] as int,
      averageScore: (json['averageScore'] as num).toDouble(),
      maxScore: (json['maxScore'] as num).toDouble(),
      minScore: (json['minScore'] as num).toDouble(),
      standardDeviation: (json['standardDeviation'] as num).toDouble(),
      passRate: (json['passRate'] as num).toDouble(),
      excellentRate: (json['excellentRate'] as num).toDouble(),
      scoreDistribution:
          Map<String, int>.from(json['scoreDistribution'] as Map),
      questionStatistics: (json['questionStatistics'] as List<dynamic>)
          .map(
              (e) => ExamQuestionStatistics.fromJson(e as Map<String, dynamic>))
          .toList(),
      calculatedAt: DateTime.parse(json['calculatedAt'] as String),
    );

Map<String, dynamic> _$ExamStatisticsToJson(ExamStatistics instance) =>
    <String, dynamic>{
      'examId': instance.examId,
      'examName': instance.examName,
      'totalStudents': instance.totalStudents,
      'submittedCount': instance.submittedCount,
      'averageScore': instance.averageScore,
      'maxScore': instance.maxScore,
      'minScore': instance.minScore,
      'standardDeviation': instance.standardDeviation,
      'passRate': instance.passRate,
      'excellentRate': instance.excellentRate,
      'scoreDistribution': instance.scoreDistribution,
      'questionStatistics': instance.questionStatistics,
      'calculatedAt': instance.calculatedAt.toIso8601String(),
    };

ExamQuestionStatistics _$ExamQuestionStatisticsFromJson(
        Map<String, dynamic> json) =>
    ExamQuestionStatistics(
      questionId: json['questionId'] as String,
      questionText: json['questionText'] as String,
      questionType: json['questionType'] as String,
      averageScore: (json['averageScore'] as num).toDouble(),
      maxScore: (json['maxScore'] as num).toDouble(),
      correctCount: json['correctCount'] as int,
      totalAttempts: json['totalAttempts'] as int,
      correctRate: (json['correctRate'] as num).toDouble(),
      answerDistribution:
          Map<String, int>.from(json['answerDistribution'] as Map),
      commonMistakes: (json['commonMistakes'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$ExamQuestionStatisticsToJson(
        ExamQuestionStatistics instance) =>
    <String, dynamic>{
      'questionId': instance.questionId,
      'questionText': instance.questionText,
      'questionType': instance.questionType,
      'averageScore': instance.averageScore,
      'maxScore': instance.maxScore,
      'correctCount': instance.correctCount,
      'totalAttempts': instance.totalAttempts,
      'correctRate': instance.correctRate,
      'answerDistribution': instance.answerDistribution,
      'commonMistakes': instance.commonMistakes,
    };

Semester _$SemesterFromJson(Map<String, dynamic> json) => Semester(
      id: json['id'] as String,
      name: json['name'] as String,
      academicYear: json['academicYear'] as String,
      startDate: DateTime.parse(json['startDate'] as String),
      endDate: DateTime.parse(json['endDate'] as String),
      isActive: json['isActive'] as bool,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$SemesterToJson(Semester instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'academicYear': instance.academicYear,
      'startDate': instance.startDate.toIso8601String(),
      'endDate': instance.endDate.toIso8601String(),
      'isActive': instance.isActive,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };

Grade _$GradeFromJson(Map<String, dynamic> json) => Grade(
      id: json['id'] as String,
      name: json['name'] as String,
      level: json['level'] as String,
      description: json['description'] as String,
      subjectIds: (json['subjectIds'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      studentCount: json['studentCount'] as int,
      classCount: json['classCount'] as int,
      isActive: json['isActive'] as bool,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$GradeToJson(Grade instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'level': instance.level,
      'description': instance.description,
      'subjectIds': instance.subjectIds,
      'studentCount': instance.studentCount,
      'classCount': instance.classCount,
      'isActive': instance.isActive,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };
