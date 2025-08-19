import 'dart:io';

import '../datasources/local_data_source.dart';
import '../datasources/remote_data_source.dart';
import '../../models/api_response.dart';
import '../../services/connectivity_service.dart';
import '../../utils/app_logger.dart';
import 'base_repository.dart';

/// AI辅导方案数据模型
class TutoringSolution {
  final String id;
  final String title;
  final String description;
  final String content;
  final String subject;
  final String grade;
  final List<String> topics;
  final String difficulty;
  final int estimatedTime;
  final double score;
  final String reasoning;
  final List<String> tags;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final bool isRecommended;
  final String? teacherId;
  final String? studentId;
  final String? classId;
  final double? rating;

  TutoringSolution({
    required this.id,
    required this.title,
    required this.description,
    required this.content,
    required this.subject,
    required this.grade,
    required this.topics,
    required this.difficulty,
    required this.estimatedTime,
    required this.score,
    required this.reasoning,
    required this.tags,
    this.metadata,
    required this.createdAt,
    this.updatedAt,
    this.isRecommended = false,
    this.teacherId,
    this.studentId,
    this.classId,
    this.rating,
  });

  factory TutoringSolution.fromJson(Map<String, dynamic> json) {
    return TutoringSolution(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      content: json['content'] ?? '',
      subject: json['subject'] ?? '',
      grade: json['grade'] ?? '',
      topics: List<String>.from(json['topics'] ?? []),
      difficulty: json['difficulty'] ?? '',
      estimatedTime: json['estimated_time'] ?? 0,
      score: (json['score'] ?? 0).toDouble(),
      reasoning: json['reasoning'] ?? '',
      tags: List<String>.from(json['tags'] ?? []),
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      isRecommended: json['is_recommended'] ?? false,
      teacherId: json['teacher_id'],
      studentId: json['student_id'],
      classId: json['class_id'],
      rating: json['rating']?.toDouble(),
    );
  }

  // Getter方法用于兼容性
  String get subjectName => subject;
  String get type => difficulty;

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'content': content,
      'subject': subject,
      'grade': grade,
      'topics': topics,
      'difficulty': difficulty,
      'estimated_time': estimatedTime,
      'score': score,
      'reasoning': reasoning,
      'tags': tags,
      'metadata': metadata,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'is_recommended': isRecommended,
      'teacher_id': teacherId,
      'student_id': studentId,
      'class_id': classId,
      'rating': rating,
    };
  }

  TutoringSolution copyWith({
    String? id,
    String? title,
    String? description,
    String? content,
    String? subject,
    String? grade,
    List<String>? topics,
    String? difficulty,
    int? estimatedTime,
    double? score,
    String? reasoning,
    List<String>? tags,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? isRecommended,
    String? teacherId,
    String? studentId,
    String? classId,
    double? rating,
  }) {
    return TutoringSolution(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      content: content ?? this.content,
      subject: subject ?? this.subject,
      grade: grade ?? this.grade,
      topics: topics ?? this.topics,
      difficulty: difficulty ?? this.difficulty,
      estimatedTime: estimatedTime ?? this.estimatedTime,
      score: score ?? this.score,
      reasoning: reasoning ?? this.reasoning,
      tags: tags ?? this.tags,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isRecommended: isRecommended ?? this.isRecommended,
      teacherId: teacherId ?? this.teacherId,
      studentId: studentId ?? this.studentId,
      classId: classId ?? this.classId,
      rating: rating ?? this.rating,
    );
  }

  @override
  String toString() {
    return 'TutoringSolution{id: $id, title: $title, subject: $subject, score: $score}';
  }
}

/// AI辅导请求数据模型
class TutoringRequest {
  final String? id;
  final String subject;
  final String grade;
  final String topic;
  final String? studentLevel;
  final String? learningObjective;
  final String? specificRequirements;
  final List<String>? weakPoints;
  final String? preferredStyle;
  final int? timeLimit;
  final Map<String, dynamic>? context;
  final String? teacherId;
  final String? studentId;
  final String? classId;
  final DateTime? createdAt;

  TutoringRequest({
    this.id,
    required this.subject,
    required this.grade,
    required this.topic,
    this.studentLevel,
    this.learningObjective,
    this.specificRequirements,
    this.weakPoints,
    this.preferredStyle,
    this.timeLimit,
    this.context,
    this.teacherId,
    this.studentId,
    this.classId,
    this.createdAt,
  });

  factory TutoringRequest.fromJson(Map<String, dynamic> json) {
    return TutoringRequest(
      id: json['id'],
      subject: json['subject'] ?? '',
      grade: json['grade'] ?? '',
      topic: json['topic'] ?? '',
      studentLevel: json['student_level'],
      learningObjective: json['learning_objective'],
      specificRequirements: json['specific_requirements'],
      weakPoints: json['weak_points'] != null ? List<String>.from(json['weak_points']) : null,
      preferredStyle: json['preferred_style'],
      timeLimit: json['time_limit'],
      context: json['context'] as Map<String, dynamic>?,
      teacherId: json['teacher_id'],
      studentId: json['student_id'],
      classId: json['class_id'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'subject': subject,
      'grade': grade,
      'topic': topic,
      if (studentLevel != null) 'student_level': studentLevel,
      if (learningObjective != null) 'learning_objective': learningObjective,
      if (specificRequirements != null) 'specific_requirements': specificRequirements,
      if (weakPoints != null) 'weak_points': weakPoints,
      if (preferredStyle != null) 'preferred_style': preferredStyle,
      if (timeLimit != null) 'time_limit': timeLimit,
      if (context != null) 'context': context,
      if (teacherId != null) 'teacher_id': teacherId,
      if (studentId != null) 'student_id': studentId,
      if (classId != null) 'class_id': classId,
      if (createdAt != null) 'created_at': createdAt!.toIso8601String(),
    };
  }

  TutoringRequest copyWith({
    String? id,
    String? subject,
    String? grade,
    String? topic,
    String? studentLevel,
    String? learningObjective,
    String? specificRequirements,
    List<String>? weakPoints,
    String? preferredStyle,
    int? timeLimit,
    Map<String, dynamic>? context,
    String? teacherId,
    String? studentId,
    String? classId,
    DateTime? createdAt,
  }) {
    return TutoringRequest(
      id: id ?? this.id,
      subject: subject ?? this.subject,
      grade: grade ?? this.grade,
      topic: topic ?? this.topic,
      studentLevel: studentLevel ?? this.studentLevel,
      learningObjective: learningObjective ?? this.learningObjective,
      specificRequirements: specificRequirements ?? this.specificRequirements,
      weakPoints: weakPoints ?? this.weakPoints,
      preferredStyle: preferredStyle ?? this.preferredStyle,
      timeLimit: timeLimit ?? this.timeLimit,
      context: context ?? this.context,
      teacherId: teacherId ?? this.teacherId,
      studentId: studentId ?? this.studentId,
      classId: classId ?? this.classId,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  String toString() {
    return 'TutoringRequest{subject: $subject, grade: $grade, topic: $topic}';
  }
}

/// 辅导历史记录数据模型
class TutoringHistory {
  final String id;
  final TutoringRequest request;
  final List<TutoringSolution> solutions;
  final String? selectedSolutionId;
  final Map<String, dynamic>? feedback;
  final double? rating;
  final String? comments;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final String status;

  TutoringHistory({
    required this.id,
    required this.request,
    required this.solutions,
    this.selectedSolutionId,
    this.feedback,
    this.rating,
    this.comments,
    required this.createdAt,
    this.updatedAt,
    required this.status,
  });

  factory TutoringHistory.fromJson(Map<String, dynamic> json) {
    return TutoringHistory(
      id: json['id'] ?? '',
      request: TutoringRequest.fromJson(json['request'] as Map<String, dynamic>),
      solutions: (json['solutions'] as List)
          .map((item) => TutoringSolution.fromJson(item as Map<String, dynamic>))
          .toList(),
      selectedSolutionId: json['selected_solution_id'],
      feedback: json['feedback'] as Map<String, dynamic>?,
      rating: json['rating']?.toDouble(),
      comments: json['comments'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      status: json['status'] ?? 'pending',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'request': request.toJson(),
      'solutions': solutions.map((solution) => solution.toJson()).toList(),
      'selected_solution_id': selectedSolutionId,
      'feedback': feedback,
      'rating': rating,
      'comments': comments,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'status': status,
    };
  }

  @override
  String toString() {
    return 'TutoringHistory{id: $id, status: $status, solutionsCount: ${solutions.length}}';
  }
}

/// AI辅导统计数据模型
class TutoringStatistics {
  final int totalRequests;
  final int completedRequests;
  final int pendingRequests;
  final Map<String, int> subjectDistribution;
  final Map<String, int> gradeDistribution;
  final Map<String, int> difficultyDistribution;
  final double averageRating;
  final double averageResponseTime;
  final int totalSolutions;
  final Map<String, int> popularTopics;
  final Map<String, double> successRates;

  TutoringStatistics({
    required this.totalRequests,
    required this.completedRequests,
    required this.pendingRequests,
    required this.subjectDistribution,
    required this.gradeDistribution,
    required this.difficultyDistribution,
    required this.averageRating,
    required this.averageResponseTime,
    required this.totalSolutions,
    required this.popularTopics,
    required this.successRates,
  });

  factory TutoringStatistics.fromJson(Map<String, dynamic> json) {
    return TutoringStatistics(
      totalRequests: json['total_requests'] ?? 0,
      completedRequests: json['completed_requests'] ?? 0,
      pendingRequests: json['pending_requests'] ?? 0,
      subjectDistribution: Map<String, int>.from(
        (json['subject_distribution'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
      gradeDistribution: Map<String, int>.from(
        (json['grade_distribution'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
      difficultyDistribution: Map<String, int>.from(
        (json['difficulty_distribution'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
      averageRating: (json['average_rating'] ?? 0).toDouble(),
      averageResponseTime: (json['average_response_time'] ?? 0).toDouble(),
      totalSolutions: json['total_solutions'] ?? 0,
      popularTopics: Map<String, int>.from(
        (json['popular_topics'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
      successRates: Map<String, double>.from(
        (json['success_rates'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toDouble()),
        ),
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_requests': totalRequests,
      'completed_requests': completedRequests,
      'pending_requests': pendingRequests,
      'subject_distribution': subjectDistribution,
      'grade_distribution': gradeDistribution,
      'difficulty_distribution': difficultyDistribution,
      'average_rating': averageRating,
      'average_response_time': averageResponseTime,
      'total_solutions': totalSolutions,
      'popular_topics': popularTopics,
      'success_rates': successRates,
    };
  }
}

/// AI辅导仓库接口
abstract class TutoringRepository {
  /// 生成AI辅导方案
  Future<ApiResponse<List<TutoringSolution>>> generateTutoringSolutions(TutoringRequest request);

  /// 获取辅导方案详情
  Future<ApiResponse<TutoringSolution>> getTutoringSolution(String solutionId);

  /// 获取推荐的辅导方案
  Future<ApiResponse<List<TutoringSolution>>> getRecommendedSolutions({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    int limit = 10,
  });

  /// 评价辅导方案
  Future<ApiResponse<bool>> rateTutoringSolution(
    String solutionId,
    double rating,
    String? comments,
    Map<String, dynamic>? feedback,
  );

  /// 收藏辅导方案
  Future<ApiResponse<bool>> favoriteTutoringSolution(String solutionId);

  /// 取消收藏辅导方案
  Future<ApiResponse<bool>> unfavoriteTutoringSolution(String solutionId);

  /// 获取收藏的辅导方案
  Future<ApiResponse<List<TutoringSolution>>> getFavoriteSolutions({
    String? subject,
    String? grade,
    int page = 1,
    int pageSize = 20,
  });

  /// 获取辅导历史
  Future<ApiResponse<PaginatedResponse<TutoringHistory>>> getTutoringHistory({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    String? status,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  });

  /// 获取单个辅导历史
  Future<ApiResponse<TutoringHistory>> getTutoringHistoryById(String historyId);

  /// 删除辅导历史
  Future<ApiResponse<bool>> deleteTutoringHistory(String historyId);

  /// 批量删除辅导历史
  Future<ApiResponse<bool>> deleteTutoringHistoryBatch(List<String> historyIds);

  /// 更新辅导历史状态
  Future<ApiResponse<bool>> updateTutoringHistoryStatus(String historyId, String status);

  /// 获取辅导统计
  Future<ApiResponse<TutoringStatistics>> getTutoringStatistics({
    String? subject,
    String? grade,
    String? teacherId,
    String? studentId,
    String? classId,
    DateTime? startDate,
    DateTime? endDate,
  });

  /// 搜索辅导方案
  Future<ApiResponse<List<TutoringSolution>>> searchTutoringSolutions(
    String query, {
    String? subject,
    String? grade,
    String? difficulty,
    List<String>? tags,
    int limit = 10,
  });

  /// 导出辅导历史
  Future<ApiResponse<String>> exportTutoringHistory({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    DateTime? startDate,
    DateTime? endDate,
    String format = 'excel',
  });

  // tutoring_provider.dart中调用的方法
  /// 获取所有辅导方案
  Future<ApiResponse<List<TutoringSolution>>> getSolutions();

  /// 根据ID获取辅导方案
  Future<ApiResponse<TutoringSolution>> getSolution(String solutionId);

  /// 生成单个辅导方案
  Future<ApiResponse<TutoringSolution>> generateSolution({
    required String studentId,
    required String subjectId,
    required String problemDescription,
    String? difficulty,
    String? type,
    Map<String, dynamic>? additionalContext,
  });

  /// 创建辅导方案
  Future<ApiResponse<TutoringSolution>> createSolution(Map<String, dynamic> solutionData);

  /// 更新辅导方案
  Future<ApiResponse<TutoringSolution>> updateSolution(String solutionId, Map<String, dynamic> solutionData);

  /// 删除辅导方案
  Future<ApiResponse<bool>> deleteSolution(String solutionId);

  /// 批量删除辅导方案
  Future<ApiResponse<bool>> deleteSolutionsBatch(List<String> solutionIds);

  /// 评价辅导方案（简化版本）
  Future<ApiResponse<TutoringSolution>> rateSolution(
    String solutionId,
    int rating, {
    String? feedback,
  });

  /// 开始辅导会话
  Future<ApiResponse<String>> startTutoringSession({
    required String studentId,
    required String subjectId,
    String? problemDescription,
    Map<String, dynamic>? context,
  });

  /// 发送消息
  Future<ApiResponse<Map<String, dynamic>>> sendMessage(
    String sessionId,
    String message,
  );

  /// 结束会话
  Future<ApiResponse<void>> endSession(String sessionId);

  /// 获取会话历史
  Future<ApiResponse<List<dynamic>>> getSessionHistory(String sessionId);
}

/// AI辅导仓库实现类
class TutoringRepositoryImpl extends BaseRepository implements TutoringRepository {
  static const String _cacheKeyPrefix = 'tutoring_';
  static const String _historyCacheKeyPrefix = 'tutoring_history_';
  static const String _statisticsCacheKey = 'tutoring_statistics';
  static const Duration _cacheExpiry = Duration(minutes: 15);
  static const Duration _historyCacheExpiry = Duration(hours: 1);

  TutoringRepositoryImpl({
    required RemoteDataSource remoteDataSource,
    required LocalDataSource localDataSource,
    required ConnectivityService connectivityService,
  }) : super(
          remoteDataSource: remoteDataSource,
          localDataSource: localDataSource,
          connectivityService: connectivityService,
        );

  @override
  Future<ApiResponse<List<TutoringSolution>>> generateTutoringSolutions(TutoringRequest request) async {
    try {
      final response = await remoteDataSource.post<List<TutoringSolution>>(
        '/api/v1/ai-tutoring/generate',
        body: request.toJson(),
        fromJson: (data) => (data as List)
            .map((item) => TutoringSolution.fromJson(item as Map<String, dynamic>))
            .toList(),
      );

      if (response.success && response.data != null) {
        // 缓存生成的方案
        final cacheKey = _buildSolutionsCacheKey(request);
        await localDataSource.cacheData(cacheKey, response.data!.map((s) => s.toJson()).toList());
        
        AppLogger.info('TutoringRepository: AI辅导方案生成成功', {
          'subject': request.subject,
          'grade': request.grade,
          'topic': request.topic,
          'solutionsCount': response.data!.length,
        });
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: AI辅导方案生成失败', e, stackTrace);
      
      // 尝试从本地获取默认方案
      final defaultSolutions = await _getDefaultSolutions(request);
      if (defaultSolutions.isNotEmpty) {
        return ApiResponse.success(
          data: defaultSolutions,
          message: '网络异常，已为您提供默认辅导方案',
        );
      }
      
      return ApiResponse.error(message: 'AI辅导方案生成失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<TutoringSolution>> getTutoringSolution(String solutionId) async {
    final cacheKey = '${_cacheKeyPrefix}solution_$solutionId';

    return fetchData<TutoringSolution>(
      remoteCall: () => _fetchSolutionFromRemote(solutionId),
      localCall: () => _fetchSolutionFromLocal(solutionId),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<List<TutoringSolution>>> getRecommendedSolutions({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    int limit = 10,
  }) async {
    final cacheKey = _buildRecommendedCacheKey(
      subject: subject,
      grade: grade,
      studentId: studentId,
      classId: classId,
      limit: limit,
    );

    return fetchData<List<TutoringSolution>>(
      remoteCall: () => _fetchRecommendedFromRemote(
        subject: subject,
        grade: grade,
        studentId: studentId,
        classId: classId,
        limit: limit,
      ),
      localCall: () => _fetchRecommendedFromLocal(cacheKey),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<bool>> rateTutoringSolution(
    String solutionId,
    double rating,
    String? comments,
    Map<String, dynamic>? feedback,
  ) async {
    return syncToServer<Map<String, dynamic>>(
      data: {
        'solution_id': solutionId,
        'rating': rating,
        if (comments != null) 'comments': comments,
        if (feedback != null) 'feedback': feedback,
      },
      uploadCall: (data) => _rateSolutionRemote(solutionId, rating, comments, feedback),
      syncKey: 'rate_solution_${solutionId}_${DateTime.now().millisecondsSinceEpoch}',
    );
  }

  @override
  Future<ApiResponse<bool>> favoriteTutoringSolution(String solutionId) async {
    return syncToServer<String>(
      data: solutionId,
      uploadCall: (id) => _favoriteSolutionRemote(id),
      syncKey: 'favorite_solution_$solutionId',
    );
  }

  @override
  Future<ApiResponse<bool>> unfavoriteTutoringSolution(String solutionId) async {
    return syncToServer<String>(
      data: solutionId,
      uploadCall: (id) => _unfavoriteSolutionRemote(id),
      syncKey: 'unfavorite_solution_$solutionId',
    );
  }

  @override
  Future<ApiResponse<List<TutoringSolution>>> getFavoriteSolutions({
    String? subject,
    String? grade,
    int page = 1,
    int pageSize = 20,
  }) async {
    final cacheKey = _buildFavoritesCacheKey(
      subject: subject,
      grade: grade,
      page: page,
      pageSize: pageSize,
    );

    return fetchData<List<TutoringSolution>>(
      remoteCall: () => _fetchFavoritesFromRemote(
        subject: subject,
        grade: grade,
        page: page,
        pageSize: pageSize,
      ),
      localCall: () => _fetchFavoritesFromLocal(cacheKey),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<PaginatedResponse<TutoringHistory>>> getTutoringHistory({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    String? status,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  }) async {
    final cacheKey = _buildHistoryCacheKey(
      subject: subject,
      grade: grade,
      studentId: studentId,
      classId: classId,
      status: status,
      page: page,
      pageSize: pageSize,
    );

    return fetchData<PaginatedResponse<TutoringHistory>>(
      remoteCall: () => _fetchHistoryFromRemote(
        subject: subject,
        grade: grade,
        studentId: studentId,
        classId: classId,
        status: status,
        page: page,
        pageSize: pageSize,
      ),
      localCall: () => _fetchHistoryFromLocal(cacheKey),
      cacheKey: cacheKey,
      forceRefresh: forceRefresh,
      cacheExpiry: _historyCacheExpiry,
    );
  }

  @override
  Future<ApiResponse<TutoringHistory>> getTutoringHistoryById(String historyId) async {
    final cacheKey = '${_historyCacheKeyPrefix}single_$historyId';

    return fetchData<TutoringHistory>(
      remoteCall: () => _fetchHistoryByIdFromRemote(historyId),
      localCall: () => _fetchHistoryByIdFromLocal(historyId),
      cacheKey: cacheKey,
      cacheExpiry: _historyCacheExpiry,
    );
  }

  @override
  Future<ApiResponse<bool>> deleteTutoringHistory(String historyId) async {
    return syncToServer<String>(
      data: historyId,
      uploadCall: (id) => _deleteHistoryRemote(id),
      syncKey: 'delete_history_$historyId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearHistoryCache(historyId);
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> deleteTutoringHistoryBatch(List<String> historyIds) async {
    return syncToServer<List<String>>(
      data: historyIds,
      uploadCall: (ids) => _deleteHistoryBatchRemote(ids),
      syncKey: 'delete_history_batch_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        for (final historyId in historyIds) {
          _clearHistoryCache(historyId);
        }
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> updateTutoringHistoryStatus(String historyId, String status) async {
    return syncToServer<Map<String, dynamic>>(
      data: {'status': status},
      uploadCall: (data) => _updateHistoryStatusRemote(historyId, status),
      syncKey: 'update_history_status_$historyId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearHistoryCache(historyId);
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<TutoringStatistics>> getTutoringStatistics({
    String? subject,
    String? grade,
    String? teacherId,
    String? studentId,
    String? classId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final cacheKey = _buildStatisticsCacheKey(
      subject: subject,
      grade: grade,
      teacherId: teacherId,
      studentId: studentId,
      classId: classId,
      startDate: startDate,
      endDate: endDate,
    );

    return fetchData<TutoringStatistics>(
      remoteCall: () => _fetchStatisticsFromRemote(
        subject: subject,
        grade: grade,
        teacherId: teacherId,
        studentId: studentId,
        classId: classId,
        startDate: startDate,
        endDate: endDate,
      ),
      localCall: () => _fetchStatisticsFromLocal(cacheKey),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<List<TutoringSolution>>> searchTutoringSolutions(
    String query, {
    String? subject,
    String? grade,
    String? difficulty,
    List<String>? tags,
    int limit = 10,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'q': query,
        'limit': limit,
        if (subject != null) 'subject': subject,
        if (grade != null) 'grade': grade,
        if (difficulty != null) 'difficulty': difficulty,
        if (tags != null && tags.isNotEmpty) 'tags': tags.join(','),
      };

      final response = await remoteDataSource.get<List<TutoringSolution>>(
        '/api/v1/ai-tutoring/search',
        queryParameters: queryParams,
        fromJson: (data) => (data as List)
            .map((item) => TutoringSolution.fromJson(item as Map<String, dynamic>))
            .toList(),
      );

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 辅导方案搜索失败', e, stackTrace);
      return ApiResponse.error(message: '辅导方案搜索失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<String>> exportTutoringHistory({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    DateTime? startDate,
    DateTime? endDate,
    String format = 'excel',
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'format': format,
        if (subject != null) 'subject': subject,
        if (grade != null) 'grade': grade,
        if (studentId != null) 'student_id': studentId,
        if (classId != null) 'class_id': classId,
        if (startDate != null) 'start_date': startDate.toIso8601String(),
        if (endDate != null) 'end_date': endDate.toIso8601String(),
      };

      final response = await remoteDataSource.get<String>(
        '/api/v1/ai-tutoring/export',
        queryParameters: queryParams,
        fromJson: (data) => data as String,
      );

      if (response.success) {
        AppLogger.info('TutoringRepository: 辅导历史导出成功', {
          'subject': subject,
          'grade': grade,
          'format': format,
        });
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 辅导历史导出失败', e, stackTrace);
      return ApiResponse.error(message: '辅导历史导出失败: ${e.toString()}');
    }
  }

  // 私有方法实现

  /// 获取默认辅导方案
  Future<List<TutoringSolution>> _getDefaultSolutions(TutoringRequest request) async {
    try {
      final defaultData = await localDataSource.getDefaultData<List<dynamic>>('tutoring_solutions');
      if (defaultData != null) {
        return defaultData
            .map((item) => TutoringSolution.fromJson(item as Map<String, dynamic>))
            .where((solution) => 
              solution.subject == request.subject && 
              solution.grade == request.grade
            )
            .take(3)
            .toList();
      }
    } catch (e) {
      AppLogger.warning('TutoringRepository: 获取默认辅导方案失败', {'error': e.toString()});
    }
    return [];
  }

  /// 从远程获取辅导方案详情
  Future<ApiResponse<TutoringSolution>> _fetchSolutionFromRemote(String solutionId) async {
    return remoteDataSource.get<TutoringSolution>(
      '/api/v1/ai-tutoring/solutions/$solutionId',
      fromJson: (data) => TutoringSolution.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取辅导方案详情
  Future<TutoringSolution?> _fetchSolutionFromLocal(String solutionId) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>('${_cacheKeyPrefix}solution_$solutionId');
    if (cachedData != null) {
      return TutoringSolution.fromJson(cachedData);
    }
    return null;
  }

  /// 从远程获取推荐方案
  Future<ApiResponse<List<TutoringSolution>>> _fetchRecommendedFromRemote({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    int limit = 10,
  }) async {
    final queryParams = <String, dynamic>{
      'limit': limit,
      if (subject != null) 'subject': subject,
      if (grade != null) 'grade': grade,
      if (studentId != null) 'student_id': studentId,
      if (classId != null) 'class_id': classId,
    };

    return remoteDataSource.get<List<TutoringSolution>>(
      '/api/v1/ai-tutoring/recommended',
      queryParameters: queryParams,
      fromJson: (data) => (data as List)
          .map((item) => TutoringSolution.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  /// 从本地获取推荐方案
  Future<List<TutoringSolution>?> _fetchRecommendedFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<List<dynamic>>(cacheKey);
    if (cachedData != null) {
      return cachedData
          .map((item) => TutoringSolution.fromJson(item as Map<String, dynamic>))
          .toList();
    }
    return null;
  }

  /// 远程评价方案
  Future<ApiResponse<bool>> _rateSolutionRemote(
    String solutionId,
    double rating,
    String? comments,
    Map<String, dynamic>? feedback,
  ) async {
    final response = await remoteDataSource.post<Map<String, dynamic>>(
      '/api/v1/ai-tutoring/solutions/$solutionId/rate',
      body: {
        'rating': rating,
        if (comments != null) 'comments': comments,
        if (feedback != null) 'feedback': feedback,
      },
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程收藏方案
  Future<ApiResponse<bool>> _favoriteSolutionRemote(String solutionId) async {
    final response = await remoteDataSource.post<Map<String, dynamic>>(
      '/api/v1/ai-tutoring/solutions/$solutionId/favorite',
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程取消收藏方案
  Future<ApiResponse<bool>> _unfavoriteSolutionRemote(String solutionId) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/ai-tutoring/solutions/$solutionId/favorite',
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 从远程获取收藏方案
  Future<ApiResponse<List<TutoringSolution>>> _fetchFavoritesFromRemote({
    String? subject,
    String? grade,
    int page = 1,
    int pageSize = 20,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
      if (subject != null) 'subject': subject,
      if (grade != null) 'grade': grade,
    };

    return remoteDataSource.get<List<TutoringSolution>>(
      '/api/v1/ai-tutoring/favorites',
      queryParameters: queryParams,
      fromJson: (data) => (data as List)
          .map((item) => TutoringSolution.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  /// 从本地获取收藏方案
  Future<List<TutoringSolution>?> _fetchFavoritesFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<List<dynamic>>(cacheKey);
    if (cachedData != null) {
      return cachedData
          .map((item) => TutoringSolution.fromJson(item as Map<String, dynamic>))
          .toList();
    }
    return null;
  }

  /// 从远程获取辅导历史
  Future<ApiResponse<PaginatedResponse<TutoringHistory>>> _fetchHistoryFromRemote({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    String? status,
    int page = 1,
    int pageSize = 20,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
      if (subject != null) 'subject': subject,
      if (grade != null) 'grade': grade,
      if (studentId != null) 'student_id': studentId,
      if (classId != null) 'class_id': classId,
      if (status != null) 'status': status,
    };

    return remoteDataSource.get<PaginatedResponse<TutoringHistory>>(
      '/api/v1/ai-tutoring/history',
      queryParameters: queryParams,
      fromJson: (data) => PaginatedResponse.fromJson(
        data as Map<String, dynamic>,
        (item) => TutoringHistory.fromJson(item as Map<String, dynamic>),
      ),
    );
  }

  /// 从本地获取辅导历史
  Future<PaginatedResponse<TutoringHistory>?> _fetchHistoryFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>(cacheKey);
    if (cachedData != null) {
      return PaginatedResponse.fromJson(
        cachedData,
        (item) => TutoringHistory.fromJson(item as Map<String, dynamic>),
      );
    }
    return null;
  }

  /// 从远程获取单个辅导历史
  Future<ApiResponse<TutoringHistory>> _fetchHistoryByIdFromRemote(String historyId) async {
    return remoteDataSource.get<TutoringHistory>(
      '/api/v1/ai-tutoring/history/$historyId',
      fromJson: (data) => TutoringHistory.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取单个辅导历史
  Future<TutoringHistory?> _fetchHistoryByIdFromLocal(String historyId) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>('${_historyCacheKeyPrefix}single_$historyId');
    if (cachedData != null) {
      return TutoringHistory.fromJson(cachedData);
    }
    return null;
  }

  /// 远程删除辅导历史
  Future<ApiResponse<bool>> _deleteHistoryRemote(String historyId) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/ai-tutoring/history/$historyId',
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程批量删除辅导历史
  Future<ApiResponse<bool>> _deleteHistoryBatchRemote(List<String> historyIds) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/ai-tutoring/history/batch',
      headers: {'Content-Type': 'application/json'},
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程更新辅导历史状态
  Future<ApiResponse<bool>> _updateHistoryStatusRemote(String historyId, String status) async {
    final response = await remoteDataSource.put<Map<String, dynamic>>(
      '/api/v1/ai-tutoring/history/$historyId',
      body: {'status': status},
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 从远程获取统计数据
  Future<ApiResponse<TutoringStatistics>> _fetchStatisticsFromRemote({
    String? subject,
    String? grade,
    String? teacherId,
    String? studentId,
    String? classId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = <String, dynamic>{
      if (subject != null) 'subject': subject,
      if (grade != null) 'grade': grade,
      if (teacherId != null) 'teacher_id': teacherId,
      if (studentId != null) 'student_id': studentId,
      if (classId != null) 'class_id': classId,
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
    };

    return remoteDataSource.get<TutoringStatistics>(
      '/api/v1/ai-tutoring/statistics',
      queryParameters: queryParams,
      fromJson: (data) => TutoringStatistics.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取统计数据
  Future<TutoringStatistics?> _fetchStatisticsFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>(cacheKey);
    if (cachedData != null) {
      return TutoringStatistics.fromJson(cachedData);
    }
    return null;
  }

  /// 构建方案缓存键
  String _buildSolutionsCacheKey(TutoringRequest request) {
    final parts = <String>[
      _cacheKeyPrefix,
      'solutions',
      request.subject,
      request.grade,
      request.topic.hashCode.toString(),
    ];
    return parts.join('_');
  }

  /// 构建推荐缓存键
  String _buildRecommendedCacheKey({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    int limit = 10,
  }) {
    final parts = <String>[
      _cacheKeyPrefix,
      'recommended',
      if (subject != null) 'subject_$subject',
      if (grade != null) 'grade_$grade',
      if (studentId != null) 'student_$studentId',
      if (classId != null) 'class_$classId',
      'limit_$limit',
    ];
    return parts.join('_');
  }

  /// 构建收藏缓存键
  String _buildFavoritesCacheKey({
    String? subject,
    String? grade,
    int page = 1,
    int pageSize = 20,
  }) {
    final parts = <String>[
      _cacheKeyPrefix,
      'favorites',
      if (subject != null) 'subject_$subject',
      if (grade != null) 'grade_$grade',
      'page_$page',
      'size_$pageSize',
    ];
    return parts.join('_');
  }

  /// 构建历史缓存键
  String _buildHistoryCacheKey({
    String? subject,
    String? grade,
    String? studentId,
    String? classId,
    String? status,
    int page = 1,
    int pageSize = 20,
  }) {
    final parts = <String>[
      _historyCacheKeyPrefix,
      'list',
      if (subject != null) 'subject_$subject',
      if (grade != null) 'grade_$grade',
      if (studentId != null) 'student_$studentId',
      if (classId != null) 'class_$classId',
      if (status != null) 'status_$status',
      'page_$page',
      'size_$pageSize',
    ];
    return parts.join('_');
  }

  /// 构建统计缓存键
  String _buildStatisticsCacheKey({
    String? subject,
    String? grade,
    String? teacherId,
    String? studentId,
    String? classId,
    DateTime? startDate,
    DateTime? endDate,
  }) {
    final parts = <String>[
      _statisticsCacheKey,
      if (subject != null) 'subject_$subject',
      if (grade != null) 'grade_$grade',
      if (teacherId != null) 'teacher_$teacherId',
      if (studentId != null) 'student_$studentId',
      if (classId != null) 'class_$classId',
      if (startDate != null) 'start_${startDate.millisecondsSinceEpoch}',
      if (endDate != null) 'end_${endDate.millisecondsSinceEpoch}',
    ];
    return parts.join('_');
  }

  /// 清除历史缓存
  Future<void> _clearHistoryCache(String historyId) async {
    try {
      await clearCache('${_historyCacheKeyPrefix}single_$historyId');
      AppLogger.debug('TutoringRepository: 已清除辅导历史缓存', {'historyId': historyId});
    } catch (e) {
      AppLogger.warning('TutoringRepository: 清除辅导历史缓存失败', {
        'historyId': historyId,
        'error': e.toString(),
      });
    }
  }

  @override
  Future<void> _syncSingleItem(Map<String, dynamic> item) async {
    final syncKey = item['syncKey'] as String;
    final data = item['data'];
    
    try {
      if (syncKey.startsWith('rate_solution_')) {
        final solutionId = (data as Map<String, dynamic>)['solution_id'] as String;
        final rating = data['rating'] as double;
        final comments = data['comments'] as String?;
        final feedback = data['feedback'] as Map<String, dynamic>?;
        await _rateSolutionRemote(solutionId, rating, comments, feedback);
      } else if (syncKey.startsWith('favorite_solution_')) {
        await _favoriteSolutionRemote(data as String);
      } else if (syncKey.startsWith('unfavorite_solution_')) {
        await _unfavoriteSolutionRemote(data as String);
      } else if (syncKey.startsWith('delete_history_batch_')) {
        await _deleteHistoryBatchRemote(data as List<String>);
      } else if (syncKey.startsWith('delete_history_')) {
        await _deleteHistoryRemote(data as String);
      } else if (syncKey.startsWith('update_history_status_')) {
        final historyId = syncKey.split('_').last;
        final status = (data as Map<String, dynamic>)['status'] as String;
        await _updateHistoryStatusRemote(historyId, status);
      }
      
      // 同步成功，清除标记
      await localDataSource.clearSyncMark(syncKey);
      AppLogger.info('TutoringRepository: 单项同步成功', {'syncKey': syncKey});
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 单项同步失败', e, stackTrace);
      rethrow;
    }
  }

  // 新增方法实现
  @override
  Future<ApiResponse<List<TutoringSolution>>> getSolutions() async {
    try {
      final response = await remoteDataSource.get<List<TutoringSolution>>(
        '/api/v1/ai-tutoring/solutions',
        fromJson: (data) => (data as List)
            .map((item) => TutoringSolution.fromJson(item as Map<String, dynamic>))
            .toList(),
      );
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 获取辅导方案列表失败', e, stackTrace);
      return ApiResponse.error(message: '获取辅导方案列表失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<TutoringSolution>> getSolution(String solutionId) async {
    return getTutoringSolution(solutionId);
  }

  @override
  Future<ApiResponse<TutoringSolution>> generateSolution({
    required String studentId,
    required String subjectId,
    required String problemDescription,
    String? difficulty,
    String? type,
    Map<String, dynamic>? additionalContext,
  }) async {
    try {
      final requestData = {
        'student_id': studentId,
        'subject_id': subjectId,
        'problem_description': problemDescription,
        if (difficulty != null) 'difficulty': difficulty,
        if (type != null) 'type': type,
        if (additionalContext != null) 'additional_context': additionalContext,
      };

      final response = await remoteDataSource.post<TutoringSolution>(
        '/api/v1/ai-tutoring/generate-single',
        body: requestData,
        fromJson: (data) => TutoringSolution.fromJson(data as Map<String, dynamic>),
      );
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 生成单个辅导方案失败', e, stackTrace);
      return ApiResponse.error(message: '生成辅导方案失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<TutoringSolution>> createSolution(Map<String, dynamic> solutionData) async {
    try {
      final response = await remoteDataSource.post<TutoringSolution>(
        '/api/v1/ai-tutoring/solutions',
        body: solutionData,
        fromJson: (data) => TutoringSolution.fromJson(data as Map<String, dynamic>),
      );
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 创建辅导方案失败', e, stackTrace);
      return ApiResponse.error(message: '创建辅导方案失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<TutoringSolution>> updateSolution(String solutionId, Map<String, dynamic> solutionData) async {
    try {
      final response = await remoteDataSource.put<TutoringSolution>(
        '/api/v1/ai-tutoring/solutions/$solutionId',
        body: solutionData,
        fromJson: (data) => TutoringSolution.fromJson(data as Map<String, dynamic>),
      );
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 更新辅导方案失败', e, stackTrace);
      return ApiResponse.error(message: '更新辅导方案失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> deleteSolution(String solutionId) async {
    try {
      final response = await remoteDataSource.delete<Map<String, dynamic>>(
        '/api/v1/ai-tutoring/solutions/$solutionId',
        fromJson: (data) => data as Map<String, dynamic>,
      );
      return response.transform<bool>((data) => response.success);
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 删除辅导方案失败', e, stackTrace);
      return ApiResponse.error(message: '删除辅导方案失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> deleteSolutionsBatch(List<String> solutionIds) async {
    try {
      final response = await remoteDataSource.post<Map<String, dynamic>>(
        '/api/v1/ai-tutoring/solutions/batch/delete',
        body: {'solution_ids': solutionIds},
        fromJson: (data) => data as Map<String, dynamic>,
      );
      return response.transform<bool>((data) => response.success);
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 批量删除辅导方案失败', e, stackTrace);
      return ApiResponse.error(message: '批量删除辅导方案失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<TutoringSolution>> rateSolution(
    String solutionId,
    int rating, {
    String? feedback,
  }) async {
    try {
      final requestData = {
        'rating': rating,
        if (feedback != null) 'feedback': feedback,
      };

      final response = await remoteDataSource.post<TutoringSolution>(
        '/api/v1/ai-tutoring/solutions/$solutionId/rate',
        body: requestData,
        fromJson: (data) => TutoringSolution.fromJson(data as Map<String, dynamic>),
      );
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 评价辅导方案失败', e, stackTrace);
      return ApiResponse.error(message: '评价辅导方案失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<String>> startTutoringSession({
    required String studentId,
    required String subjectId,
    String? problemDescription,
    Map<String, dynamic>? context,
  }) async {
    try {
      final requestData = {
        'student_id': studentId,
        'subject_id': subjectId,
        if (problemDescription != null) 'problem_description': problemDescription,
        if (context != null) 'context': context,
      };

      final response = await remoteDataSource.post<String>(
        '/api/v1/ai-tutoring/sessions',
        body: requestData,
        fromJson: (data) => data['session_id'] as String,
      );
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 开始辅导会话失败', e, stackTrace);
      return ApiResponse.error(message: '开始辅导会话失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<Map<String, dynamic>>> sendMessage(
    String sessionId,
    String message,
  ) async {
    try {
      final response = await remoteDataSource.post<Map<String, dynamic>>(
        '/api/v1/ai-tutoring/sessions/$sessionId/messages',
        body: {
          'message': message,
        },
        fromJson: (data) => data as Map<String, dynamic>,
      );
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 发送消息失败', e, stackTrace);
      return ApiResponse.error(message: '发送消息失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<void>> endSession(String sessionId) async {
    try {
      final response = await remoteDataSource.post<void>(
        '/api/v1/ai-tutoring/sessions/$sessionId/end',
        body: {},
        fromJson: (data) => null,
      );
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 结束会话失败', e, stackTrace);
      return ApiResponse.error(message: '结束会话失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<List<dynamic>>> getSessionHistory(String sessionId) async {
    try {
      final response = await remoteDataSource.get<List<dynamic>>(
        '/api/v1/ai-tutoring/sessions/$sessionId/history',
        fromJson: (data) => data['messages'] as List<dynamic>,
      );
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('TutoringRepository: 获取会话历史失败', e, stackTrace);
      return ApiResponse.error(message: '获取会话历史失败: ${e.toString()}');
    }
  }
}