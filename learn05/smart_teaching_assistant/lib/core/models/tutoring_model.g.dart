// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tutoring_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TutoringMessage _$TutoringMessageFromJson(Map<String, dynamic> json) =>
    TutoringMessage(
      id: json['id'] as String,
      sessionId: json['sessionId'] as String,
      role: json['role'] as String,
      content: json['content'] as String,
      type: json['type'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      isRead: json['isRead'] as bool? ?? false,
    );

Map<String, dynamic> _$TutoringMessageToJson(TutoringMessage instance) =>
    <String, dynamic>{
      'id': instance.id,
      'sessionId': instance.sessionId,
      'role': instance.role,
      'content': instance.content,
      'type': instance.type,
      'metadata': instance.metadata,
      'createdAt': instance.createdAt.toIso8601String(),
      'isRead': instance.isRead,
    };

TutoringPlan _$TutoringPlanFromJson(Map<String, dynamic> json) => TutoringPlan(
      id: json['id'] as String,
      studentId: json['studentId'] as String,
      studentName: json['studentName'] as String,
      subjectId: json['subjectId'] as String,
      subjectName: json['subjectName'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      difficulty: json['difficulty'] as String,
      estimatedHours: json['estimatedHours'] as int,
      objectives: (json['objectives'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      modules: (json['modules'] as List<dynamic>)
          .map((e) => TutoringModule.fromJson(e as Map<String, dynamic>))
          .toList(),
      status: json['status'] as String,
      startDate: DateTime.parse(json['startDate'] as String),
      endDate: json['endDate'] == null
          ? null
          : DateTime.parse(json['endDate'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      createdBy: json['createdBy'] as String,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$TutoringPlanToJson(TutoringPlan instance) =>
    <String, dynamic>{
      'id': instance.id,
      'studentId': instance.studentId,
      'studentName': instance.studentName,
      'subjectId': instance.subjectId,
      'subjectName': instance.subjectName,
      'title': instance.title,
      'description': instance.description,
      'difficulty': instance.difficulty,
      'estimatedHours': instance.estimatedHours,
      'objectives': instance.objectives,
      'modules': instance.modules,
      'status': instance.status,
      'startDate': instance.startDate.toIso8601String(),
      'endDate': instance.endDate?.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'createdBy': instance.createdBy,
      'metadata': instance.metadata,
    };

TutoringModule _$TutoringModuleFromJson(Map<String, dynamic> json) =>
    TutoringModule(
      id: json['id'] as String,
      planId: json['planId'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      orderIndex: json['orderIndex'] as int,
      type: json['type'] as String,
      topics:
          (json['topics'] as List<dynamic>).map((e) => e as String).toList(),
      resources: (json['resources'] as List<dynamic>)
          .map((e) => TutoringResource.fromJson(e as Map<String, dynamic>))
          .toList(),
      exercises: (json['exercises'] as List<dynamic>)
          .map((e) => Exercise.fromJson(e as Map<String, dynamic>))
          .toList(),
      status: json['status'] as String,
      estimatedMinutes: json['estimatedMinutes'] as int,
      startedAt: json['startedAt'] == null
          ? null
          : DateTime.parse(json['startedAt'] as String),
      completedAt: json['completedAt'] == null
          ? null
          : DateTime.parse(json['completedAt'] as String),
      progress: json['progress'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$TutoringModuleToJson(TutoringModule instance) =>
    <String, dynamic>{
      'id': instance.id,
      'planId': instance.planId,
      'title': instance.title,
      'description': instance.description,
      'orderIndex': instance.orderIndex,
      'type': instance.type,
      'topics': instance.topics,
      'resources': instance.resources,
      'exercises': instance.exercises,
      'status': instance.status,
      'estimatedMinutes': instance.estimatedMinutes,
      'startedAt': instance.startedAt?.toIso8601String(),
      'completedAt': instance.completedAt?.toIso8601String(),
      'progress': instance.progress,
    };

TutoringResource _$TutoringResourceFromJson(Map<String, dynamic> json) =>
    TutoringResource(
      id: json['id'] as String,
      title: json['title'] as String,
      type: json['type'] as String,
      url: json['url'] as String,
      description: json['description'] as String?,
      duration: json['duration'] as int?,
      fileSize: json['fileSize'] as int?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$TutoringResourceToJson(TutoringResource instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'type': instance.type,
      'url': instance.url,
      'description': instance.description,
      'duration': instance.duration,
      'fileSize': instance.fileSize,
      'metadata': instance.metadata,
    };

Exercise _$ExerciseFromJson(Map<String, dynamic> json) => Exercise(
      id: json['id'] as String,
      moduleId: json['moduleId'] as String,
      question: json['question'] as String,
      type: json['type'] as String,
      options:
          (json['options'] as List<dynamic>?)?.map((e) => e as String).toList(),
      correctAnswer: json['correctAnswer'] as String?,
      explanation: json['explanation'] as String?,
      difficulty: json['difficulty'] as String,
      topics:
          (json['topics'] as List<dynamic>).map((e) => e as String).toList(),
      points: json['points'] as int,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ExerciseToJson(Exercise instance) => <String, dynamic>{
      'id': instance.id,
      'moduleId': instance.moduleId,
      'question': instance.question,
      'type': instance.type,
      'options': instance.options,
      'correctAnswer': instance.correctAnswer,
      'explanation': instance.explanation,
      'difficulty': instance.difficulty,
      'topics': instance.topics,
      'points': instance.points,
      'metadata': instance.metadata,
    };

ExerciseResult _$ExerciseResultFromJson(Map<String, dynamic> json) =>
    ExerciseResult(
      id: json['id'] as String,
      exerciseId: json['exerciseId'] as String,
      studentId: json['studentId'] as String,
      studentAnswer: json['studentAnswer'] as String,
      isCorrect: json['isCorrect'] as bool,
      pointsEarned: json['pointsEarned'] as int,
      timeSpent: json['timeSpent'] as int,
      submittedAt: DateTime.parse(json['submittedAt'] as String),
      feedback: json['feedback'] as String?,
      details: json['details'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ExerciseResultToJson(ExerciseResult instance) =>
    <String, dynamic>{
      'id': instance.id,
      'exerciseId': instance.exerciseId,
      'studentId': instance.studentId,
      'studentAnswer': instance.studentAnswer,
      'isCorrect': instance.isCorrect,
      'pointsEarned': instance.pointsEarned,
      'timeSpent': instance.timeSpent,
      'submittedAt': instance.submittedAt.toIso8601String(),
      'feedback': instance.feedback,
      'details': instance.details,
    };

LearningRecommendation _$LearningRecommendationFromJson(
        Map<String, dynamic> json) =>
    LearningRecommendation(
      id: json['id'] as String,
      studentId: json['studentId'] as String,
      subjectId: json['subjectId'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      priority: json['priority'] as String,
      reasons:
          (json['reasons'] as List<dynamic>).map((e) => e as String).toList(),
      actionItems: (json['actionItems'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      recommendedResources: (json['recommendedResources'] as List<dynamic>)
          .map((e) => TutoringResource.fromJson(e as Map<String, dynamic>))
          .toList(),
      createdAt: DateTime.parse(json['createdAt'] as String),
      expiresAt: json['expiresAt'] == null
          ? null
          : DateTime.parse(json['expiresAt'] as String),
      isRead: json['isRead'] as bool,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$LearningRecommendationToJson(
        LearningRecommendation instance) =>
    <String, dynamic>{
      'id': instance.id,
      'studentId': instance.studentId,
      'subjectId': instance.subjectId,
      'type': instance.type,
      'title': instance.title,
      'description': instance.description,
      'priority': instance.priority,
      'reasons': instance.reasons,
      'actionItems': instance.actionItems,
      'recommendedResources': instance.recommendedResources,
      'createdAt': instance.createdAt.toIso8601String(),
      'expiresAt': instance.expiresAt?.toIso8601String(),
      'isRead': instance.isRead,
      'metadata': instance.metadata,
    };

LearningProgress _$LearningProgressFromJson(Map<String, dynamic> json) =>
    LearningProgress(
      id: json['id'] as String,
      studentId: json['studentId'] as String,
      subjectId: json['subjectId'] as String,
      planId: json['planId'] as String,
      overallProgress: (json['overallProgress'] as num).toDouble(),
      completedModules: json['completedModules'] as int,
      totalModules: json['totalModules'] as int,
      completedExercises: json['completedExercises'] as int,
      totalExercises: json['totalExercises'] as int,
      averageScore: (json['averageScore'] as num).toDouble(),
      totalTimeSpent: json['totalTimeSpent'] as int,
      lastActivityAt: DateTime.parse(json['lastActivityAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      details: json['details'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$LearningProgressToJson(LearningProgress instance) =>
    <String, dynamic>{
      'id': instance.id,
      'studentId': instance.studentId,
      'subjectId': instance.subjectId,
      'planId': instance.planId,
      'overallProgress': instance.overallProgress,
      'completedModules': instance.completedModules,
      'totalModules': instance.totalModules,
      'completedExercises': instance.completedExercises,
      'totalExercises': instance.totalExercises,
      'averageScore': instance.averageScore,
      'totalTimeSpent': instance.totalTimeSpent,
      'lastActivityAt': instance.lastActivityAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'details': instance.details,
    };

KnowledgePointMastery _$KnowledgePointMasteryFromJson(
        Map<String, dynamic> json) =>
    KnowledgePointMastery(
      id: json['id'] as String,
      studentId: json['studentId'] as String,
      subjectId: json['subjectId'] as String,
      knowledgePointId: json['knowledgePointId'] as String,
      knowledgePointName: json['knowledgePointName'] as String,
      masteryLevel: (json['masteryLevel'] as num).toDouble(),
      masteryStatus: json['masteryStatus'] as String,
      practiceCount: json['practiceCount'] as int,
      averageScore: (json['averageScore'] as num).toDouble(),
      lastPracticeAt: DateTime.parse(json['lastPracticeAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      relatedTopics: (json['relatedTopics'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      analytics: json['analytics'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$KnowledgePointMasteryToJson(
        KnowledgePointMastery instance) =>
    <String, dynamic>{
      'id': instance.id,
      'studentId': instance.studentId,
      'subjectId': instance.subjectId,
      'knowledgePointId': instance.knowledgePointId,
      'knowledgePointName': instance.knowledgePointName,
      'masteryLevel': instance.masteryLevel,
      'masteryStatus': instance.masteryStatus,
      'practiceCount': instance.practiceCount,
      'averageScore': instance.averageScore,
      'lastPracticeAt': instance.lastPracticeAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'relatedTopics': instance.relatedTopics,
      'analytics': instance.analytics,
    };
