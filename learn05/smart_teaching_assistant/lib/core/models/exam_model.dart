import 'package:json_annotation/json_annotation.dart';

part 'exam_model.g.dart';

/// 考试模型
@JsonSerializable()
class Exam {
  final String id;
  final String name;
  final String description;
  final String type; // 'quiz', 'midterm', 'final', 'assignment'
  final String subjectId;
  final String subjectName;
  final String classId;
  final String className;
  final DateTime examDate;
  final int duration; // 考试时长（分钟）
  final double totalScore;
  final String status; // 'scheduled', 'in_progress', 'completed', 'cancelled'
  final DateTime createdAt;
  final DateTime updatedAt;
  final String createdBy;
  final Map<String, dynamic>? settings;

  const Exam({
    required this.id,
    required this.name,
    required this.description,
    required this.type,
    required this.subjectId,
    required this.subjectName,
    required this.classId,
    required this.className,
    required this.examDate,
    required this.duration,
    required this.totalScore,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    required this.createdBy,
    this.settings,
  });

  factory Exam.fromJson(Map<String, dynamic> json) => _$ExamFromJson(json);

  Map<String, dynamic> toJson() => _$ExamToJson(this);

  /// 是否已完成
  bool get isCompleted => status == 'completed';

  /// 是否进行中
  bool get isInProgress => status == 'in_progress';

  /// 是否已安排
  bool get isScheduled => status == 'scheduled';

  /// 是否已取消
  bool get isCancelled => status == 'cancelled';

  /// 考试是否已开始
  bool get hasStarted => DateTime.now().isAfter(examDate);

  /// 考试是否已结束
  bool get hasEnded {
    final endTime = examDate.add(Duration(minutes: duration));
    return DateTime.now().isAfter(endTime);
  }
}

/// 科目模型
@JsonSerializable()
class Subject {
  final String id;
  final String name;
  final String code;
  final String description;
  final String category; // 'core', 'elective', 'extracurricular'
  final int credits;
  final String gradeLevel;
  final String teacherId;
  final String? teacherName;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? metadata;

  const Subject({
    required this.id,
    required this.name,
    required this.code,
    required this.description,
    required this.category,
    required this.credits,
    required this.gradeLevel,
    required this.teacherId,
    this.teacherName,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
  });

  factory Subject.fromJson(Map<String, dynamic> json) => _$SubjectFromJson(json);

  Map<String, dynamic> toJson() => _$SubjectToJson(this);
}

/// 考试统计模型
@JsonSerializable()
class ExamStatistics {
  final String examId;
  final String examName;
  final int totalStudents;
  final int submittedCount;
  final double averageScore;
  final double maxScore;
  final double minScore;
  final double standardDeviation;
  final double passRate;
  final double excellentRate;
  final Map<String, int> scoreDistribution;
  final List<ExamQuestionStatistics> questionStatistics;
  final DateTime calculatedAt;

  const ExamStatistics({
    required this.examId,
    required this.examName,
    required this.totalStudents,
    required this.submittedCount,
    required this.averageScore,
    required this.maxScore,
    required this.minScore,
    required this.standardDeviation,
    required this.passRate,
    required this.excellentRate,
    required this.scoreDistribution,
    required this.questionStatistics,
    required this.calculatedAt,
  });

  factory ExamStatistics.fromJson(Map<String, dynamic> json) =>
      _$ExamStatisticsFromJson(json);

  Map<String, dynamic> toJson() => _$ExamStatisticsToJson(this);

  /// 提交率
  double get submissionRate {
    if (totalStudents == 0) return 0.0;
    return submittedCount / totalStudents;
  }
}

/// 考试题目统计模型
@JsonSerializable()
class ExamQuestionStatistics {
  final String questionId;
  final String questionText;
  final String questionType;
  final double averageScore;
  final double maxScore;
  final int correctCount;
  final int totalAttempts;
  final double correctRate;
  final Map<String, int> answerDistribution;
  final List<String> commonMistakes;

  const ExamQuestionStatistics({
    required this.questionId,
    required this.questionText,
    required this.questionType,
    required this.averageScore,
    required this.maxScore,
    required this.correctCount,
    required this.totalAttempts,
    required this.correctRate,
    required this.answerDistribution,
    required this.commonMistakes,
  });

  factory ExamQuestionStatistics.fromJson(Map<String, dynamic> json) =>
      _$ExamQuestionStatisticsFromJson(json);

  Map<String, dynamic> toJson() => _$ExamQuestionStatisticsToJson(this);
}

/// 学期模型
@JsonSerializable()
class Semester {
  final String id;
  final String name;
  final String academicYear;
  final DateTime startDate;
  final DateTime endDate;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Semester({
    required this.id,
    required this.name,
    required this.academicYear,
    required this.startDate,
    required this.endDate,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Semester.fromJson(Map<String, dynamic> json) => _$SemesterFromJson(json);

  Map<String, dynamic> toJson() => _$SemesterToJson(this);

  /// 学期是否进行中
  bool get isCurrent {
    final now = DateTime.now();
    return now.isAfter(startDate) && now.isBefore(endDate);
  }

  /// 学期是否已结束
  bool get isEnded => DateTime.now().isAfter(endDate);

  /// 学期是否未开始
  bool get isUpcoming => DateTime.now().isBefore(startDate);
}

/// 年级模型
@JsonSerializable()
class Grade {
  final String id;
  final String name;
  final String level; // '1', '2', '3', etc.
  final String description;
  final List<String> subjectIds;
  final int studentCount;
  final int classCount;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Grade({
    required this.id,
    required this.name,
    required this.level,
    required this.description,
    required this.subjectIds,
    required this.studentCount,
    required this.classCount,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Grade.fromJson(Map<String, dynamic> json) => _$GradeFromJson(json);

  Map<String, dynamic> toJson() => _$GradeToJson(this);
}