import 'dart:io';

import '../datasources/local_data_source.dart';
import '../datasources/remote_data_source.dart';
import '../../models/api_response.dart';
import '../../services/connectivity_service.dart';
import '../../utils/app_logger.dart';
import 'base_repository.dart';

/// 分页响应模型
class PaginatedResponse<T> {
  final List<T> data;
  final int total;
  final int page;
  final int pageSize;
  final int totalPages;

  PaginatedResponse({
    required this.data,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.totalPages,
  });

  factory PaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function(dynamic) fromJsonT,
  ) {
    return PaginatedResponse<T>(
      data: (json['data'] as List).map((item) => fromJsonT(item)).toList(),
      total: json['total'] ?? 0,
      page: json['page'] ?? 1,
      pageSize: json['page_size'] ?? 20,
      totalPages: json['total_pages'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'data': data,
      'total': total,
      'page': page,
      'page_size': pageSize,
      'total_pages': totalPages,
    };
  }
}

/// 学科数据模型
class Subject {
  final String id;
  final String name;
  final String code;
  final String? description;
  final String? category;
  final String? grade;
  final int? creditHours;
  final String? teacherId;
  final String? teacherName;
  final String? color;
  final String? icon;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final bool isActive;

  Subject({
    required this.id,
    required this.name,
    required this.code,
    this.description,
    this.category,
    this.grade,
    this.creditHours,
    this.teacherId,
    this.teacherName,
    this.color,
    this.icon,
    this.metadata,
    required this.createdAt,
    this.updatedAt,
    this.isActive = true,
  });

  factory Subject.fromJson(Map<String, dynamic> json) {
    return Subject(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      code: json['code'] ?? '',
      description: json['description'],
      category: json['category'],
      grade: json['grade'],
      creditHours: json['credit_hours'],
      teacherId: json['teacher_id'],
      teacherName: json['teacher_name'],
      color: json['color'],
      icon: json['icon'],
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'code': code,
      'description': description,
      'category': category,
      'grade': grade,
      'credit_hours': creditHours,
      'teacher_id': teacherId,
      'teacher_name': teacherName,
      'color': color,
      'icon': icon,
      'metadata': metadata,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'is_active': isActive,
    };
  }

  Subject copyWith({
    String? id,
    String? name,
    String? code,
    String? description,
    String? category,
    String? grade,
    int? creditHours,
    String? teacherId,
    String? teacherName,
    String? color,
    String? icon,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? isActive,
  }) {
    return Subject(
      id: id ?? this.id,
      name: name ?? this.name,
      code: code ?? this.code,
      description: description ?? this.description,
      category: category ?? this.category,
      grade: grade ?? this.grade,
      creditHours: creditHours ?? this.creditHours,
      teacherId: teacherId ?? this.teacherId,
      teacherName: teacherName ?? this.teacherName,
      color: color ?? this.color,
      icon: icon ?? this.icon,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isActive: isActive ?? this.isActive,
    );
  }

  @override
  String toString() {
    return 'Subject(id: $id, name: $name, code: $code, grade: $grade, isActive: $isActive)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Subject && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

/// 学科统计数据模型
class SubjectStatistics {
  final int totalSubjects;
  final int activeSubjects;
  final int inactiveSubjects;
  final Map<String, int> categoryDistribution;
  final Map<String, int> gradeDistribution;
  final Map<String, int> teacherDistribution;
  final double averageCreditHours;
  final int maxCreditHours;
  final int minCreditHours;

  SubjectStatistics({
    required this.totalSubjects,
    required this.activeSubjects,
    required this.inactiveSubjects,
    required this.categoryDistribution,
    required this.gradeDistribution,
    required this.teacherDistribution,
    required this.averageCreditHours,
    required this.maxCreditHours,
    required this.minCreditHours,
  });

  factory SubjectStatistics.fromJson(Map<String, dynamic> json) {
    return SubjectStatistics(
      totalSubjects: json['total_subjects'] ?? 0,
      activeSubjects: json['active_subjects'] ?? 0,
      inactiveSubjects: json['inactive_subjects'] ?? 0,
      categoryDistribution: Map<String, int>.from(json['category_distribution'] ?? {}),
      gradeDistribution: Map<String, int>.from(json['grade_distribution'] ?? {}),
      teacherDistribution: Map<String, int>.from(json['teacher_distribution'] ?? {}),
      averageCreditHours: (json['average_credit_hours'] ?? 0).toDouble(),
      maxCreditHours: json['max_credit_hours'] ?? 0,
      minCreditHours: json['min_credit_hours'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_subjects': totalSubjects,
      'active_subjects': activeSubjects,
      'inactive_subjects': inactiveSubjects,
      'category_distribution': categoryDistribution,
      'grade_distribution': gradeDistribution,
      'teacher_distribution': teacherDistribution,
      'average_credit_hours': averageCreditHours,
      'max_credit_hours': maxCreditHours,
      'min_credit_hours': minCreditHours,
    };
  }
}

/// 学科仓库接口
abstract class SubjectRepository {
  /// 获取学科列表
  Future<ApiResponse<PaginatedResponse<Subject>>> getSubjects({
    String? category,
    String? grade,
    String? teacherId,
    String? searchQuery,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  });

  /// 获取单个学科
  Future<ApiResponse<Subject>> getSubject(String subjectId);

  /// 根据学科代码获取学科
  Future<ApiResponse<Subject>> getSubjectByCode(String code);

  /// 创建学科
  Future<ApiResponse<Subject>> createSubject(Map<String, dynamic> subjectData);

  /// 批量创建学科
  Future<ApiResponse<List<Subject>>> createSubjectsBatch(List<Map<String, dynamic>> subjectsData);

  /// 更新学科
  Future<ApiResponse<Subject>> updateSubject(String subjectId, Map<String, dynamic> subjectData);

  /// 删除学科
  Future<ApiResponse<bool>> deleteSubject(String subjectId);

  /// 批量删除学科
  Future<ApiResponse<bool>> deleteSubjectsBatch(List<String> subjectIds);

  /// 激活/停用学科
  Future<ApiResponse<bool>> toggleSubjectStatus(String subjectId, bool isActive);

  /// 获取学科统计
  Future<ApiResponse<SubjectStatistics>> getSubjectStatistics({
    String? category,
    String? grade,
  });

  /// 导入学科数据
  Future<ApiResponse<Map<String, dynamic>>> importSubjects(
    String filePath, {
    String? category,
  });

  /// 导出学科数据
  Future<ApiResponse<String>> exportSubjects({
    String? category,
    String? grade,
    String format = 'excel',
  });

  /// 搜索学科
  Future<ApiResponse<List<Subject>>> searchSubjects(String query, {
    String? category,
    String? grade,
    int limit = 10,
  });
}

/// 学科仓库实现类
class SubjectRepositoryImpl extends BaseRepository implements SubjectRepository {
  static const String _cacheKeyPrefix = 'subjects_';
  static const String _statisticsCacheKey = 'subject_statistics';
  static const Duration _cacheExpiry = Duration(minutes: 30);

  SubjectRepositoryImpl({
    required RemoteDataSource remoteDataSource,
    required LocalDataSource localDataSource,
    required ConnectivityService connectivityService,
  }) : super(
          remoteDataSource: remoteDataSource,
          localDataSource: localDataSource,
          connectivityService: connectivityService,
        );

  @override

  @override
  Future<ApiResponse<PaginatedResponse<Subject>>> getSubjects({
    String? category,
    String? grade,
    String? teacherId,
    String? searchQuery,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  }) async {
    // 构建缓存键
    final cacheKey = '${_cacheKeyPrefix}list_${category ?? 'all'}_${grade ?? 'all'}_${teacherId ?? 'all'}_${searchQuery ?? ''}_${isActive ?? 'all'}_${page}_$pageSize';
    
    return await fetchData<PaginatedResponse<Subject>>(
      remoteCall: () async {
        // 构建查询参数
        final queryParams = <String, dynamic>{
          'page': page,
          'page_size': pageSize,
          if (category != null) 'category': category,
          if (grade != null) 'grade': grade,
          if (teacherId != null) 'teacher_id': teacherId,
          if (searchQuery != null && searchQuery.isNotEmpty) 'search': searchQuery,
          if (isActive != null) 'is_active': isActive,
        };

        // 从远程获取数据
        return await remoteDataSource.get<PaginatedResponse<Subject>>(
          '/api/v1/subjects',
          queryParameters: queryParams,
          fromJson: (data) => PaginatedResponse<Subject>.fromJson(
            data,
            (item) => Subject.fromJson(item as Map<String, dynamic>),
          ),
        );
      },
      localCall: () async {
        // 尝试从本地默认数据获取
        final defaultData = await localDataSource.getDefaultData('subjects');
        if (defaultData != null) {
          final subjects = (defaultData['data'] as List)
              .map((item) => Subject.fromJson(item as Map<String, dynamic>))
              .toList();
          
          // 应用筛选
          var filteredSubjects = subjects.where((subject) {
            if (category != null && subject.category != category) return false;
            if (grade != null && subject.grade != grade) return false;
            if (teacherId != null && subject.teacherId != teacherId) return false;
            if (isActive != null && subject.isActive != isActive) return false;
            if (searchQuery != null && searchQuery.isNotEmpty) {
              final query = searchQuery.toLowerCase();
              return subject.name.toLowerCase().contains(query) ||
                     subject.code.toLowerCase().contains(query) ||
                     (subject.description?.toLowerCase().contains(query) ?? false);
            }
            return true;
          }).toList();
          
          // 分页
          final startIndex = (page - 1) * pageSize;
          final endIndex = startIndex + pageSize;
          final paginatedSubjects = filteredSubjects.length > startIndex
              ? filteredSubjects.sublist(
                  startIndex,
                  endIndex > filteredSubjects.length ? filteredSubjects.length : endIndex,
                )
              : <Subject>[];
          
          return PaginatedResponse<Subject>(
            data: paginatedSubjects,
            total: filteredSubjects.length,
            page: page,
            pageSize: pageSize,
            totalPages: (filteredSubjects.length / pageSize).ceil(),
          );
        }
        return null;
      },
      cacheKey: cacheKey,
      forceRefresh: forceRefresh,
    );
  }

  @override
  Future<ApiResponse<Subject>> getSubject(String subjectId) async {
    final cacheKey = '${_cacheKeyPrefix}detail_$subjectId';
    
    return await fetchData<Subject>(
      remoteCall: () async {
        return await remoteDataSource.get<Subject>(
          '/api/v1/subjects/$subjectId',
          fromJson: (data) => Subject.fromJson(data as Map<String, dynamic>),
        );
      },
      localCall: () async {
        return null;
      },
      cacheKey: cacheKey,
      forceRefresh: false,
    );
  }

  @override
  Future<ApiResponse<Subject>> getSubjectByCode(String code) async {
    try {
      final response = await remoteDataSource.get<Subject>(
        '/api/v1/subjects/by-code/$code',
        fromJson: (data) => Subject.fromJson(data as Map<String, dynamic>),
      );

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 根据代码获取学科失败', e, stackTrace);
      return ApiResponse.error(message: '根据代码获取学科失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<Subject>> createSubject(Map<String, dynamic> subjectData) async {
    try {
      final response = await remoteDataSource.post<Subject>(
        '/api/v1/subjects',
        body: subjectData,
        fromJson: (data) => Subject.fromJson(data as Map<String, dynamic>),
      );

      // 清除相关缓存
      if (response.success) {
        await clearCacheByPrefix(_cacheKeyPrefix);
        await clearCache(_statisticsCacheKey);
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 创建学科失败', e, stackTrace);
      return ApiResponse.error(message: '创建学科失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<List<Subject>>> createSubjectsBatch(List<Map<String, dynamic>> subjectsData) async {
    try {
      final response = await remoteDataSource.post<List<Subject>>(
        '/api/v1/subjects/batch',
        body: {'subjects': subjectsData},
        fromJson: (data) => (data as List)
            .map((item) => Subject.fromJson(item as Map<String, dynamic>))
            .toList(),
      );

      // 清除相关缓存
      if (response.success) {
        await clearCacheByPrefix(_cacheKeyPrefix);
        await clearCache(_statisticsCacheKey);
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 批量创建学科失败', e, stackTrace);
      return ApiResponse.error(message: '批量创建学科失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<Subject>> updateSubject(String subjectId, Map<String, dynamic> subjectData) async {
    try {
      final response = await remoteDataSource.put<Subject>(
        '/api/v1/subjects/$subjectId',
        body: subjectData,
        fromJson: (data) => Subject.fromJson(data as Map<String, dynamic>),
      );

      // 清除相关缓存
      if (response.success) {
        await clearCacheByPrefix(_cacheKeyPrefix);
        await clearCache(_statisticsCacheKey);
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 更新学科失败', e, stackTrace);
      return ApiResponse.error(message: '更新学科失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> deleteSubject(String subjectId) async {
    try {
      final response = await remoteDataSource.delete<bool>(
        '/api/v1/subjects/$subjectId',
        fromJson: (data) => data['success'] ?? false,
      );

      // 清除相关缓存
      if (response.success) {
        await clearCacheByPrefix(_cacheKeyPrefix);
        await clearCache(_statisticsCacheKey);
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 删除学科失败', e, stackTrace);
      return ApiResponse.error(message: '删除学科失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> deleteSubjectsBatch(List<String> subjectIds) async {
    try {
      final response = await remoteDataSource.post<bool>(
        '/api/v1/subjects/batch-delete',
        body: {'subject_ids': subjectIds},
        fromJson: (data) => data['success'] ?? false,
      );

      // 清除相关缓存
      if (response.success) {
        await clearCacheByPrefix(_cacheKeyPrefix);
        await clearCache(_statisticsCacheKey);
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 批量删除学科失败', e, stackTrace);
      return ApiResponse.error(message: '批量删除学科失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> toggleSubjectStatus(String subjectId, bool isActive) async {
    try {
      final response = await remoteDataSource.patch<bool>(
        '/api/v1/subjects/$subjectId/status',
        body: {'is_active': isActive},
        fromJson: (data) => data['success'] ?? false,
      );

      // 清除相关缓存
      if (response.success) {
        await clearCacheByPrefix(_cacheKeyPrefix);
        await clearCache(_statisticsCacheKey);
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 切换学科状态失败', e, stackTrace);
      return ApiResponse.error(message: '切换学科状态失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<SubjectStatistics>> getSubjectStatistics({
    String? category,
    String? grade,
  }) async {
    final cacheKey = '${_statisticsCacheKey}_${category ?? 'all'}_${grade ?? 'all'}';
    
    return await fetchData<SubjectStatistics>(
      remoteCall: () async {
        final queryParams = <String, dynamic>{
          if (category != null) 'category': category,
          if (grade != null) 'grade': grade,
        };

        return await remoteDataSource.get<SubjectStatistics>(
          '/api/v1/subjects/statistics',
          queryParameters: queryParams,
          fromJson: (data) => SubjectStatistics.fromJson(data as Map<String, dynamic>),
        );
      },
      localCall: () async {
        return null;
      },
      cacheKey: cacheKey,
      forceRefresh: false,
    );
  }

  @override
  Future<ApiResponse<Map<String, dynamic>>> importSubjects(
    String filePath, {
    String? category,
  }) async {
    try {
      final file = File(filePath);
      if (!await file.exists()) {
        return ApiResponse.error(message: '文件不存在');
      }

      final formData = <String, dynamic>{
        'file': file,
        if (category != null) 'category': category,
      };

      final response = await remoteDataSource.uploadFile<Map<String, dynamic>>(
        '/api/v1/subjects/import',
        file,
        fields: category != null ? {'category': category} : {},
        fromJson: (data) => data as Map<String, dynamic>,
      );

      // 清除相关缓存
      if (response.success) {
        await clearCacheByPrefix(_cacheKeyPrefix);
        await clearCache(_statisticsCacheKey);
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 导入学科数据失败', e, stackTrace);
      return ApiResponse.error(message: '导入学科数据失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<String>> exportSubjects({
    String? category,
    String? grade,
    String format = 'excel',
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'format': format,
        if (category != null) 'category': category,
        if (grade != null) 'grade': grade,
      };

      final response = await remoteDataSource.get<String>(
        '/api/v1/subjects/export',
        queryParameters: queryParams,
        fromJson: (data) => data['file_path'] ?? '',
      );

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 导出学科数据失败', e, stackTrace);
      return ApiResponse.error(message: '导出学科数据失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<List<Subject>>> searchSubjects(String query, {
    String? category,
    String? grade,
    int limit = 10,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'q': query,
        'limit': limit,
        if (category != null) 'category': category,
        if (grade != null) 'grade': grade,
      };

      final response = await remoteDataSource.get<List<Subject>>(
        '/api/v1/subjects/search',
        queryParameters: queryParams,
        fromJson: (data) => (data as List)
            .map((item) => Subject.fromJson(item as Map<String, dynamic>))
            .toList(),
      );

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('SubjectRepository: 学科搜索失败', e, stackTrace);
      return ApiResponse.error(message: '学科搜索失败: ${e.toString()}');
    }
  }
}