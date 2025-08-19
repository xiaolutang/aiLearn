import 'package:json_annotation/json_annotation.dart';

part 'grade_model.g.dart';

/// 成绩模型
@JsonSerializable()
class Grade {
  final String id;
  final String studentId;
  final String studentName;
  final String subjectId;
  final String subjectName;
  final String examId;
  final String examName;
  final double score;
  final double totalScore;
  final String? rank; // 排名
  final String? level; // 等级 (A, B, C, D)
  final DateTime examDate;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? remark; // 备注
  
  const Grade({
    required this.id,
    required this.studentId,
    required this.studentName,
    required this.subjectId,
    required this.subjectName,
    required this.examId,
    required this.examName,
    required this.score,
    required this.totalScore,
    this.rank,
    this.level,
    required this.examDate,
    required this.createdAt,
    required this.updatedAt,
    this.remark,
  });
  
  /// 计算得分率
  double get scoreRate => score / totalScore;
  
  /// 是否及格 (60%)
  bool get isPassed => scoreRate >= 0.6;
  
  /// 获取等级颜色
  String get levelColor {
    switch (level) {
      case 'A':
        return '#4CAF50'; // 绿色
      case 'B':
        return '#2196F3'; // 蓝色
      case 'C':
        return '#FF9800'; // 橙色
      case 'D':
        return '#F44336'; // 红色
      default:
        return '#9E9E9E'; // 灰色
    }
  }
  
  factory Grade.fromJson(Map<String, dynamic> json) => _$GradeFromJson(json);
  Map<String, dynamic> toJson() => _$GradeToJson(this);
  
  Grade copyWith({
    String? id,
    String? studentId,
    String? studentName,
    String? subjectId,
    String? subjectName,
    String? examId,
    String? examName,
    double? score,
    double? totalScore,
    String? rank,
    String? level,
    DateTime? examDate,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? remark,
  }) {
    return Grade(
      id: id ?? this.id,
      studentId: studentId ?? this.studentId,
      studentName: studentName ?? this.studentName,
      subjectId: subjectId ?? this.subjectId,
      subjectName: subjectName ?? this.subjectName,
      examId: examId ?? this.examId,
      examName: examName ?? this.examName,
      score: score ?? this.score,
      totalScore: totalScore ?? this.totalScore,
      rank: rank ?? this.rank,
      level: level ?? this.level,
      examDate: examDate ?? this.examDate,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      remark: remark ?? this.remark,
    );
  }
}

/// 考试模型
@JsonSerializable()
class Exam {
  final String id;
  final String name;
  final String description;
  final String classId;
  final String className;
  final DateTime examDate;
  final String status; // 'upcoming', 'ongoing', 'completed'
  final List<Subject> subjects;
  final DateTime createdAt;
  final DateTime updatedAt;
  
  const Exam({
    required this.id,
    required this.name,
    required this.description,
    required this.classId,
    required this.className,
    required this.examDate,
    required this.status,
    required this.subjects,
    required this.createdAt,
    required this.updatedAt,
  });
  
  factory Exam.fromJson(Map<String, dynamic> json) => _$ExamFromJson(json);
  Map<String, dynamic> toJson() => _$ExamToJson(this);
}

/// 科目模型
@JsonSerializable()
class Subject {
  final String id;
  final String name;
  final String code;
  final double totalScore;
  final String? description;
  final bool isRequired; // 是否必修
  
  const Subject({
    required this.id,
    required this.name,
    required this.code,
    required this.totalScore,
    this.description,
    this.isRequired = true,
  });
  
  factory Subject.fromJson(Map<String, dynamic> json) => _$SubjectFromJson(json);
  Map<String, dynamic> toJson() => _$SubjectToJson(this);
}

/// 成绩统计模型
@JsonSerializable()
class GradeStatistics {
  final String examId;
  final String subjectId;
  final String subjectName;
  final double averageScore;
  final double maxScore;
  final double minScore;
  final double passRate; // 及格率
  final double excellentRate; // 优秀率 (90%+)
  final int totalStudents;
  final int passedStudents;
  final int excellentStudents;
  final Map<String, int> levelDistribution; // 等级分布
  
  const GradeStatistics({
    required this.examId,
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
    required this.levelDistribution,
  });
  
  factory GradeStatistics.fromJson(Map<String, dynamic> json) => _$GradeStatisticsFromJson(json);
  Map<String, dynamic> toJson() => _$GradeStatisticsToJson(this);
}

/// 学生成绩分析模型
@JsonSerializable()
class StudentGradeAnalysis {
  final String studentId;
  final String studentName;
  final List<Grade> grades;
  final double averageScore;
  final String overallLevel;
  final List<String> strengths; // 优势科目
  final List<String> weaknesses; // 薄弱科目
  final List<String> recommendations; // 学习建议
  final Map<String, double> subjectAverages; // 各科平均分
  final Map<String, String> subjectTrends; // 各科趋势 ('improving', 'stable', 'declining')
  
  const StudentGradeAnalysis({
    required this.studentId,
    required this.studentName,
    required this.grades,
    required this.averageScore,
    required this.overallLevel,
    required this.strengths,
    required this.weaknesses,
    required this.recommendations,
    required this.subjectAverages,
    required this.subjectTrends,
  });
  
  factory StudentGradeAnalysis.fromJson(Map<String, dynamic> json) => _$StudentGradeAnalysisFromJson(json);
  Map<String, dynamic> toJson() => _$StudentGradeAnalysisToJson(this);
}

/// 成绩录入请求模型
@JsonSerializable()
class GradeInputRequest {
  final String examId;
  final String subjectId;
  final List<StudentGradeInput> grades;
  
  const GradeInputRequest({
    required this.examId,
    required this.subjectId,
    required this.grades,
  });
  
  factory GradeInputRequest.fromJson(Map<String, dynamic> json) => _$GradeInputRequestFromJson(json);
  Map<String, dynamic> toJson() => _$GradeInputRequestToJson(this);
}

/// 学生成绩录入模型
@JsonSerializable()
class StudentGradeInput {
  final String studentId;
  final double score;
  final String? remark;
  
  const StudentGradeInput({
    required this.studentId,
    required this.score,
    this.remark,
  });
  
  factory StudentGradeInput.fromJson(Map<String, dynamic> json) => _$StudentGradeInputFromJson(json);
  Map<String, dynamic> toJson() => _$StudentGradeInputToJson(this);
}

/// 成绩查询参数模型
@JsonSerializable()
class GradeQueryParams {
  final String? studentId;
  final String? classId;
  final String? examId;
  final String? subjectId;
  final DateTime? startDate;
  final DateTime? endDate;
  final int page;
  final int pageSize;
  final String? sortBy; // 'score', 'examDate', 'studentName'
  final String? sortOrder; // 'asc', 'desc'
  
  const GradeQueryParams({
    this.studentId,
    this.classId,
    this.examId,
    this.subjectId,
    this.startDate,
    this.endDate,
    this.page = 1,
    this.pageSize = 20,
    this.sortBy,
    this.sortOrder = 'desc',
  });
  
  factory GradeQueryParams.fromJson(Map<String, dynamic> json) => _$GradeQueryParamsFromJson(json);
  Map<String, dynamic> toJson() => _$GradeQueryParamsToJson(this);
}

/// 成绩响应模型
@JsonSerializable()
class GradeResponse {
  final List<Grade> grades;
  final int total;
  final int page;
  final int pageSize;
  final bool hasMore;
  
  const GradeResponse({
    required this.grades,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.hasMore,
  });
  
  factory GradeResponse.fromJson(Map<String, dynamic> json) => _$GradeResponseFromJson(json);
  Map<String, dynamic> toJson() => _$GradeResponseToJson(this);
}