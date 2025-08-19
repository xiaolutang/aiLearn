import 'package:json_annotation/json_annotation.dart';

part 'tutoring_model.g.dart';

/// AI辅导消息模型
@JsonSerializable()
class TutoringMessage {
  final String id;
  final String sessionId;
  final String role; // 'user', 'assistant', 'system'
  final String content;
  final String? type; // 'text', 'image', 'file', 'code'
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final bool isRead;

  const TutoringMessage({
    required this.id,
    required this.sessionId,
    required this.role,
    required this.content,
    this.type,
    this.metadata,
    required this.createdAt,
    this.isRead = false,
  });

  factory TutoringMessage.fromJson(Map<String, dynamic> json) =>
      _$TutoringMessageFromJson(json);

  Map<String, dynamic> toJson() => _$TutoringMessageToJson(this);

  /// 是否是用户消息
  bool get isUser => role == 'user';

  /// 是否是助手消息
  bool get isAssistant => role == 'assistant';

  /// 是否是系统消息
  bool get isSystem => role == 'system';
}

/// 辅导方案模型
@JsonSerializable()
class TutoringPlan {
  final String id;
  final String studentId;
  final String studentName;
  final String subjectId;
  final String subjectName;
  final String title;
  final String description;
  final String difficulty; // 'easy', 'medium', 'hard'
  final int estimatedHours;
  final List<String> objectives;
  final List<TutoringModule> modules;
  final String status; // 'draft', 'active', 'completed', 'paused'
  final DateTime startDate;
  final DateTime? endDate;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String createdBy;
  final Map<String, dynamic>? metadata;

  const TutoringPlan({
    required this.id,
    required this.studentId,
    required this.studentName,
    required this.subjectId,
    required this.subjectName,
    required this.title,
    required this.description,
    required this.difficulty,
    required this.estimatedHours,
    required this.objectives,
    required this.modules,
    required this.status,
    required this.startDate,
    this.endDate,
    required this.createdAt,
    required this.updatedAt,
    required this.createdBy,
    this.metadata,
  });

  factory TutoringPlan.fromJson(Map<String, dynamic> json) =>
      _$TutoringPlanFromJson(json);

  Map<String, dynamic> toJson() => _$TutoringPlanToJson(this);

  /// 计算完成进度
  double get completionProgress {
    if (modules.isEmpty) return 0.0;
    final completedModules = modules.where((m) => m.isCompleted).length;
    return completedModules / modules.length;
  }

  /// 是否已完成
  bool get isCompleted => status == 'completed';

  /// 是否进行中
  bool get isActive => status == 'active';
}

/// 辅导模块模型
@JsonSerializable()
class TutoringModule {
  final String id;
  final String planId;
  final String title;
  final String description;
  final int orderIndex;
  final String type; // 'lesson', 'exercise', 'assessment'
  final List<String> topics;
  final List<TutoringResource> resources;
  final List<Exercise> exercises;
  final String status; // 'pending', 'in_progress', 'completed'
  final int estimatedMinutes;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final Map<String, dynamic>? progress;

  const TutoringModule({
    required this.id,
    required this.planId,
    required this.title,
    required this.description,
    required this.orderIndex,
    required this.type,
    required this.topics,
    required this.resources,
    required this.exercises,
    required this.status,
    required this.estimatedMinutes,
    this.startedAt,
    this.completedAt,
    this.progress,
  });

  factory TutoringModule.fromJson(Map<String, dynamic> json) =>
      _$TutoringModuleFromJson(json);

  Map<String, dynamic> toJson() => _$TutoringModuleToJson(this);

  /// 是否已完成
  bool get isCompleted => status == 'completed';

  /// 是否进行中
  bool get isInProgress => status == 'in_progress';
}

/// 辅导资源模型
@JsonSerializable()
class TutoringResource {
  final String id;
  final String title;
  final String type; // 'video', 'document', 'link', 'image'
  final String url;
  final String? description;
  final int? duration; // 秒数，适用于视频
  final int? fileSize; // 字节数
  final Map<String, dynamic>? metadata;

  const TutoringResource({
    required this.id,
    required this.title,
    required this.type,
    required this.url,
    this.description,
    this.duration,
    this.fileSize,
    this.metadata,
  });

  factory TutoringResource.fromJson(Map<String, dynamic> json) =>
      _$TutoringResourceFromJson(json);

  Map<String, dynamic> toJson() => _$TutoringResourceToJson(this);
}

/// 练习题模型
@JsonSerializable()
class Exercise {
  final String id;
  final String moduleId;
  final String question;
  final String type; // 'multiple_choice', 'true_false', 'short_answer', 'essay'
  final List<String>? options; // 选择题选项
  final String? correctAnswer;
  final String? explanation;
  final String difficulty; // 'easy', 'medium', 'hard'
  final List<String> topics;
  final int points;
  final Map<String, dynamic>? metadata;

  const Exercise({
    required this.id,
    required this.moduleId,
    required this.question,
    required this.type,
    this.options,
    this.correctAnswer,
    this.explanation,
    required this.difficulty,
    required this.topics,
    required this.points,
    this.metadata,
  });

  factory Exercise.fromJson(Map<String, dynamic> json) =>
      _$ExerciseFromJson(json);

  Map<String, dynamic> toJson() => _$ExerciseToJson(this);
}

/// 练习结果模型
@JsonSerializable()
class ExerciseResult {
  final String id;
  final String exerciseId;
  final String studentId;
  final String studentAnswer;
  final bool isCorrect;
  final int pointsEarned;
  final int timeSpent; // 秒数
  final DateTime submittedAt;
  final String? feedback;
  final Map<String, dynamic>? details;

  const ExerciseResult({
    required this.id,
    required this.exerciseId,
    required this.studentId,
    required this.studentAnswer,
    required this.isCorrect,
    required this.pointsEarned,
    required this.timeSpent,
    required this.submittedAt,
    this.feedback,
    this.details,
  });

  factory ExerciseResult.fromJson(Map<String, dynamic> json) =>
      _$ExerciseResultFromJson(json);

  Map<String, dynamic> toJson() => _$ExerciseResultToJson(this);
}

/// 学习建议模型
@JsonSerializable()
class LearningRecommendation {
  final String id;
  final String studentId;
  final String subjectId;
  final String type; // 'study_plan', 'exercise_recommendation', 'resource_suggestion'
  final String title;
  final String description;
  final String priority; // 'high', 'medium', 'low'
  final List<String> reasons;
  final List<String> actionItems;
  final List<TutoringResource> recommendedResources;
  final DateTime createdAt;
  final DateTime? expiresAt;
  final bool isRead;
  final Map<String, dynamic>? metadata;

  const LearningRecommendation({
    required this.id,
    required this.studentId,
    required this.subjectId,
    required this.type,
    required this.title,
    required this.description,
    required this.priority,
    required this.reasons,
    required this.actionItems,
    required this.recommendedResources,
    required this.createdAt,
    this.expiresAt,
    required this.isRead,
    this.metadata,
  });

  factory LearningRecommendation.fromJson(Map<String, dynamic> json) =>
      _$LearningRecommendationFromJson(json);

  Map<String, dynamic> toJson() => _$LearningRecommendationToJson(this);

  /// 是否已过期
  bool get isExpired {
    if (expiresAt == null) return false;
    return DateTime.now().isAfter(expiresAt!);
  }
}

/// 学习进度模型
@JsonSerializable()
class LearningProgress {
  final String id;
  final String studentId;
  final String subjectId;
  final String planId;
  final double overallProgress; // 0.0 - 1.0
  final int completedModules;
  final int totalModules;
  final int completedExercises;
  final int totalExercises;
  final double averageScore;
  final int totalTimeSpent; // 秒数
  final DateTime lastActivityAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? details;

  const LearningProgress({
    required this.id,
    required this.studentId,
    required this.subjectId,
    required this.planId,
    required this.overallProgress,
    required this.completedModules,
    required this.totalModules,
    required this.completedExercises,
    required this.totalExercises,
    required this.averageScore,
    required this.totalTimeSpent,
    required this.lastActivityAt,
    required this.updatedAt,
    this.details,
  });

  factory LearningProgress.fromJson(Map<String, dynamic> json) =>
      _$LearningProgressFromJson(json);

  Map<String, dynamic> toJson() => _$LearningProgressToJson(this);

  /// 模块完成率
  double get moduleCompletionRate {
    if (totalModules == 0) return 0.0;
    return completedModules / totalModules;
  }

  /// 练习完成率
  double get exerciseCompletionRate {
    if (totalExercises == 0) return 0.0;
    return completedExercises / totalExercises;
  }
}

/// 知识点掌握情况模型
@JsonSerializable()
class KnowledgePointMastery {
  final String id;
  final String studentId;
  final String subjectId;
  final String knowledgePointId;
  final String knowledgePointName;
  final double masteryLevel; // 0.0 - 1.0
  final String masteryStatus; // 'not_started', 'learning', 'mastered', 'needs_review'
  final int practiceCount;
  final double averageScore;
  final DateTime lastPracticeAt;
  final DateTime updatedAt;
  final List<String> relatedTopics;
  final Map<String, dynamic>? analytics;

  const KnowledgePointMastery({
    required this.id,
    required this.studentId,
    required this.subjectId,
    required this.knowledgePointId,
    required this.knowledgePointName,
    required this.masteryLevel,
    required this.masteryStatus,
    required this.practiceCount,
    required this.averageScore,
    required this.lastPracticeAt,
    required this.updatedAt,
    required this.relatedTopics,
    this.analytics,
  });

  factory KnowledgePointMastery.fromJson(Map<String, dynamic> json) =>
      _$KnowledgePointMasteryFromJson(json);

  Map<String, dynamic> toJson() => _$KnowledgePointMasteryToJson(this);

  /// 是否已掌握
  bool get isMastered => masteryStatus == 'mastered';

  /// 是否需要复习
  bool get needsReview => masteryStatus == 'needs_review';
}