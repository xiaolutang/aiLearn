import 'dart:io';

import '../datasources/local_data_source.dart';
import '../datasources/remote_data_source.dart';
import '../../models/api_response.dart';
import '../../models/student_model.dart';
import '../../services/connectivity_service.dart';
import '../../utils/app_logger.dart';
import 'base_repository.dart';
import 'student_repository.dart';

/// 班级数据模型
class ClassModel {
  final String id;
  final String name;
  final String? description;
  final String grade;
  final String? teacherId;
  final String? teacherName;
  final int studentCount;
  final String? classRoom;
  final String? schedule;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final bool isActive;
  final List<Student>? students;

  ClassModel({
    required this.id,
    required this.name,
    this.description,
    required this.grade,
    this.teacherId,
    this.teacherName,
    this.studentCount = 0,
    this.classRoom,
    this.schedule,
    this.metadata,
    required this.createdAt,
    this.updatedAt,
    this.isActive = true,
    this.students,
  });

  factory ClassModel.fromJson(Map<String, dynamic> json) {
    return ClassModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'],
      grade: json['grade'] ?? '',
      teacherId: json['teacher_id'],
      teacherName: json['teacher_name'],
      studentCount: json['student_count'] ?? 0,
      classRoom: json['class_room'],
      schedule: json['schedule'],
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      isActive: json['is_active'] ?? true,
      students: json['students'] != null
          ? (json['students'] as List)
              .map((item) => Student.fromJson(item as Map<String, dynamic>))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'grade': grade,
      'teacher_id': teacherId,
      'teacher_name': teacherName,
      'student_count': studentCount,
      'class_room': classRoom,
      'schedule': schedule,
      'metadata': metadata,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'is_active': isActive,
      'students': students?.map((student) => student.toJson()).toList(),
    };
  }

  ClassModel copyWith({
    String? id,
    String? name,
    String? description,
    String? grade,
    String? teacherId,
    String? teacherName,
    int? studentCount,
    String? classRoom,
    String? schedule,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? isActive,
    List<Student>? students,
  }) {
    return ClassModel(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      grade: grade ?? this.grade,
      teacherId: teacherId ?? this.teacherId,
      teacherName: teacherName ?? this.teacherName,
      studentCount: studentCount ?? this.studentCount,
      classRoom: classRoom ?? this.classRoom,
      schedule: schedule ?? this.schedule,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isActive: isActive ?? this.isActive,
      students: students ?? this.students,
    );
  }

  @override
  String toString() {
    return 'ClassModel{id: $id, name: $name, grade: $grade, studentCount: $studentCount}';
  }
}

/// 班级统计数据模型
class ClassStatistics {
  final int totalClasses;
  final int activeClasses;
  final int inactiveClasses;
  final Map<String, int> gradeDistribution;
  final Map<String, int> studentCountDistribution;
  final double averageStudentCount;
  final int maxStudentCount;
  final int minStudentCount;
  final Map<String, int> teacherDistribution;

  ClassStatistics({
    required this.totalClasses,
    required this.activeClasses,
    required this.inactiveClasses,
    required this.gradeDistribution,
    required this.studentCountDistribution,
    required this.averageStudentCount,
    required this.maxStudentCount,
    required this.minStudentCount,
    required this.teacherDistribution,
  });

  factory ClassStatistics.fromJson(Map<String, dynamic> json) {
    return ClassStatistics(
      totalClasses: json['total_classes'] ?? 0,
      activeClasses: json['active_classes'] ?? 0,
      inactiveClasses: json['inactive_classes'] ?? 0,
      gradeDistribution: Map<String, int>.from(
        (json['grade_distribution'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
      studentCountDistribution: Map<String, int>.from(
        (json['student_count_distribution'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
      averageStudentCount: (json['average_student_count'] ?? 0).toDouble(),
      maxStudentCount: json['max_student_count'] ?? 0,
      minStudentCount: json['min_student_count'] ?? 0,
      teacherDistribution: Map<String, int>.from(
        (json['teacher_distribution'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_classes': totalClasses,
      'active_classes': activeClasses,
      'inactive_classes': inactiveClasses,
      'grade_distribution': gradeDistribution,
      'student_count_distribution': studentCountDistribution,
      'average_student_count': averageStudentCount,
      'max_student_count': maxStudentCount,
      'min_student_count': minStudentCount,
      'teacher_distribution': teacherDistribution,
    };
  }
}

/// 班级仓库接口
abstract class ClassRepository {
  /// 获取班级列表
  Future<ApiResponse<PaginatedResponse<ClassModel>>> getClasses({
    String? grade,
    String? teacherId,
    String? searchQuery,
    bool? isActive,
    bool includeStudents = false,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  });

  /// 获取单个班级
  Future<ApiResponse<ClassModel>> getClass(String classId, {bool includeStudents = false});

  /// 创建班级
  Future<ApiResponse<ClassModel>> createClass(Map<String, dynamic> classData);

  /// 批量创建班级
  Future<ApiResponse<List<ClassModel>>> createClassesBatch(List<Map<String, dynamic>> classesData);

  /// 更新班级
  Future<ApiResponse<ClassModel>> updateClass(String classId, Map<String, dynamic> classData);

  /// 删除班级
  Future<ApiResponse<bool>> deleteClass(String classId);

  /// 批量删除班级
  Future<ApiResponse<bool>> deleteClassesBatch(List<String> classIds);

  /// 激活/停用班级
  Future<ApiResponse<bool>> toggleClassStatus(String classId, bool isActive);

  /// 获取班级学生列表
  Future<ApiResponse<List<Student>>> getClassStudents(String classId);

  /// 添加学生到班级
  Future<ApiResponse<bool>> addStudentToClass(String classId, String studentId);

  /// 从班级移除学生
  Future<ApiResponse<bool>> removeStudentFromClass(String classId, String studentId);

  /// 批量添加学生到班级
  Future<ApiResponse<bool>> addStudentsToClass(String classId, List<String> studentIds);

  /// 批量从班级移除学生
  Future<ApiResponse<bool>> removeStudentsFromClass(String classId, List<String> studentIds);

  /// 转移学生到其他班级
  Future<ApiResponse<bool>> transferStudent(String studentId, String fromClassId, String toClassId);

  /// 获取班级统计
  Future<ApiResponse<ClassStatistics>> getClassStatistics({
    String? grade,
    String? teacherId,
  });

  /// 导入班级数据
  Future<ApiResponse<Map<String, dynamic>>> importClasses(
    String filePath, {
    String? grade,
  });

  /// 导出班级数据
  Future<ApiResponse<String>> exportClasses({
    String? grade,
    String? teacherId,
    String format = 'excel',
  });

  /// 搜索班级
  Future<ApiResponse<List<ClassModel>>> searchClasses(String query, {
    String? grade,
    int limit = 10,
  });
}

/// 班级仓库实现类
class ClassRepositoryImpl extends BaseRepository implements ClassRepository {
  static const String _cacheKeyPrefix = 'classes_';
  static const String _statisticsCacheKey = 'class_statistics';
  static const Duration _cacheExpiry = Duration(minutes: 30);

  ClassRepositoryImpl({
    required RemoteDataSource remoteDataSource,
    required LocalDataSource localDataSource,
    required ConnectivityService connectivityService,
  }) : super(
          remoteDataSource: remoteDataSource,
          localDataSource: localDataSource,
          connectivityService: connectivityService,
        );

  @override
  Future<ApiResponse<PaginatedResponse<ClassModel>>> getClasses({
    String? grade,
    String? teacherId,
    String? searchQuery,
    bool? isActive,
    bool includeStudents = false,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  }) async {
    final cacheKey = _buildClassesCacheKey(
      grade: grade,
      teacherId: teacherId,
      searchQuery: searchQuery,
      isActive: isActive,
      includeStudents: includeStudents,
      page: page,
      pageSize: pageSize,
    );

    return fetchData<PaginatedResponse<ClassModel>>(
      remoteCall: () => _fetchClassesFromRemote(
        grade: grade,
        teacherId: teacherId,
        searchQuery: searchQuery,
        isActive: isActive,
        includeStudents: includeStudents,
        page: page,
        pageSize: pageSize,
      ),
      localCall: () => _fetchClassesFromLocal(cacheKey),
      cacheKey: cacheKey,
      forceRefresh: forceRefresh,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<ClassModel>> getClass(String classId, {bool includeStudents = false}) async {
    final cacheKey = '${_cacheKeyPrefix}single_${classId}_students_$includeStudents';

    return fetchData<ClassModel>(
      remoteCall: () => _fetchClassFromRemote(classId, includeStudents: includeStudents),
      localCall: () => _fetchClassFromLocal(classId),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<ClassModel>> createClass(Map<String, dynamic> classData) async {
    return syncToServer<Map<String, dynamic>>(
      data: classData,
      uploadCall: (data) => _createClassRemote(data),
      syncKey: 'create_class_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success && response.data == true) {
        // 清除相关缓存
        _clearRelatedCache();
        // 返回创建的ClassModel对象
        return ApiResponse.success(
          data: ClassModel.fromJson(classData..['id'] = 'temp_${DateTime.now().millisecondsSinceEpoch}'),
          message: response.message,
        );
      }
      return ApiResponse<ClassModel>.error(message: response.message);
    });
  }

  @override
  Future<ApiResponse<List<ClassModel>>> createClassesBatch(List<Map<String, dynamic>> classesData) async {
    return syncToServer<List<Map<String, dynamic>>>(
      data: classesData,
      uploadCall: (data) => _createClassesBatchRemote(data),
      syncKey: 'create_classes_batch_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success && response.data == true) {
        // 清除相关缓存
        _clearRelatedCache();
        // 返回创建的ClassModel对象列表
        final classes = classesData.map((data) => 
          ClassModel.fromJson(data..['id'] = 'temp_${DateTime.now().millisecondsSinceEpoch}')
        ).toList();
        return ApiResponse.success(
          data: classes,
          message: response.message,
        );
      }
      return ApiResponse<List<ClassModel>>.error(message: response.message);
    });
  }

  @override
  Future<ApiResponse<ClassModel>> updateClass(String classId, Map<String, dynamic> classData) async {
    return syncToServer<Map<String, dynamic>>(
      data: classData,
      uploadCall: (data) => _updateClassRemote(classId, data),
      syncKey: 'update_class_$classId',
    ).then((response) {
      if (response.success && response.data == true) {
        // 清除相关缓存
        _clearRelatedCache();
        _clearClassCache(classId);
        // 返回更新的ClassModel对象
        return ApiResponse.success(
          data: ClassModel.fromJson(classData..['id'] = classId),
          message: response.message,
        );
      }
      return ApiResponse<ClassModel>.error(message: response.message);
    });
  }

  @override
  Future<ApiResponse<bool>> deleteClass(String classId) async {
    return syncToServer<String>(
      data: classId,
      uploadCall: (id) => _deleteClassRemote(id),
      syncKey: 'delete_class_$classId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        _clearClassCache(classId);
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> deleteClassesBatch(List<String> classIds) async {
    return syncToServer<List<String>>(
      data: classIds,
      uploadCall: (ids) => _deleteClassesBatchRemote(ids),
      syncKey: 'delete_classes_batch_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        for (final classId in classIds) {
          _clearClassCache(classId);
        }
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> toggleClassStatus(String classId, bool isActive) async {
    return syncToServer<Map<String, dynamic>>(
      data: {'is_active': isActive},
      uploadCall: (data) => _updateClassRemote(classId, data),
      syncKey: 'toggle_class_status_$classId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        _clearClassCache(classId);
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<List<Student>>> getClassStudents(String classId) async {
    final cacheKey = '${_cacheKeyPrefix}students_$classId';

    return fetchData<List<Student>>(
      remoteCall: () => _fetchClassStudentsFromRemote(classId),
      localCall: () => _fetchClassStudentsFromLocal(classId),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<bool>> addStudentToClass(String classId, String studentId) async {
    return syncToServer<Map<String, dynamic>>(
      data: {'class_id': classId, 'student_id': studentId},
      uploadCall: (data) => _addStudentToClassRemote(classId, studentId),
      syncKey: 'add_student_to_class_${classId}_$studentId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        _clearClassCache(classId);
        clearCache('${_cacheKeyPrefix}students_$classId');
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> removeStudentFromClass(String classId, String studentId) async {
    return syncToServer<Map<String, dynamic>>(
      data: {'class_id': classId, 'student_id': studentId},
      uploadCall: (data) => _removeStudentFromClassRemote(classId, studentId),
      syncKey: 'remove_student_from_class_${classId}_$studentId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        _clearClassCache(classId);
        clearCache('${_cacheKeyPrefix}students_$classId');
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> addStudentsToClass(String classId, List<String> studentIds) async {
    return syncToServer<Map<String, dynamic>>(
      data: {'class_id': classId, 'student_ids': studentIds},
      uploadCall: (data) => _addStudentsToClassRemote(classId, studentIds),
      syncKey: 'add_students_to_class_${classId}_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        _clearClassCache(classId);
        clearCache('${_cacheKeyPrefix}students_$classId');
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> removeStudentsFromClass(String classId, List<String> studentIds) async {
    return syncToServer<Map<String, dynamic>>(
      data: {'class_id': classId, 'student_ids': studentIds},
      uploadCall: (data) => _removeStudentsFromClassRemote(classId, studentIds),
      syncKey: 'remove_students_from_class_${classId}_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        _clearClassCache(classId);
        clearCache('${_cacheKeyPrefix}students_$classId');
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> transferStudent(String studentId, String fromClassId, String toClassId) async {
    return syncToServer<Map<String, dynamic>>(
      data: {
        'student_id': studentId,
        'from_class_id': fromClassId,
        'to_class_id': toClassId,
      },
      uploadCall: (data) => _transferStudentRemote(studentId, fromClassId, toClassId),
      syncKey: 'transfer_student_${studentId}_${fromClassId}_$toClassId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        _clearClassCache(fromClassId);
        _clearClassCache(toClassId);
        clearCache('${_cacheKeyPrefix}students_$fromClassId');
        clearCache('${_cacheKeyPrefix}students_$toClassId');
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<ClassStatistics>> getClassStatistics({
    String? grade,
    String? teacherId,
  }) async {
    final cacheKey = _buildStatisticsCacheKey(
      grade: grade,
      teacherId: teacherId,
    );

    return fetchData<ClassStatistics>(
      remoteCall: () => _fetchStatisticsFromRemote(
        grade: grade,
        teacherId: teacherId,
      ),
      localCall: () => _fetchStatisticsFromLocal(cacheKey),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<Map<String, dynamic>>> importClasses(
    String filePath, {
    String? grade,
  }) async {
    try {
      final response = await remoteDataSource.uploadFile<Map<String, dynamic>>(
        '/api/v1/classroom/import',
        File(filePath),
        fields: {
          if (grade != null) 'grade': grade,
        },
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success) {
        // 导入成功，清除相关缓存
        _clearRelatedCache();
        AppLogger.info('ClassRepository: 班级导入成功', {
          'filePath': filePath,
          'grade': grade,
        });
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('ClassRepository: 班级导入失败', e, stackTrace);
      return ApiResponse.error(message: '班级导入失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<String>> exportClasses({
    String? grade,
    String? teacherId,
    String format = 'excel',
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'format': format,
        if (grade != null) 'grade': grade,
        if (teacherId != null) 'teacher_id': teacherId,
      };

      final response = await remoteDataSource.get<String>(
        '/api/v1/classroom/export',
        queryParameters: queryParams,
        fromJson: (data) => data as String,
      );

      if (response.success) {
        AppLogger.info('ClassRepository: 班级导出成功', {
          'grade': grade,
          'teacherId': teacherId,
          'format': format,
        });
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('ClassRepository: 班级导出失败', e, stackTrace);
      return ApiResponse.error(message: '班级导出失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<List<ClassModel>>> searchClasses(String query, {
    String? grade,
    int limit = 10,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'q': query,
        'limit': limit,
        if (grade != null) 'grade': grade,
      };

      final response = await remoteDataSource.get<List<ClassModel>>(
        '/api/v1/classroom/search',
        queryParameters: queryParams,
        fromJson: (data) => (data as List)
            .map((item) => ClassModel.fromJson(item as Map<String, dynamic>))
            .toList(),
      );

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('ClassRepository: 班级搜索失败', e, stackTrace);
      return ApiResponse.error(message: '班级搜索失败: ${e.toString()}');
    }
  }

  // 私有方法实现

  /// 从远程获取班级列表
  Future<ApiResponse<PaginatedResponse<ClassModel>>> _fetchClassesFromRemote({
    String? grade,
    String? teacherId,
    String? searchQuery,
    bool? isActive,
    bool includeStudents = false,
    int page = 1,
    int pageSize = 20,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
      'include_students': includeStudents,
      if (grade != null) 'grade': grade,
      if (teacherId != null) 'teacher_id': teacherId,
      if (searchQuery != null) 'search': searchQuery,
      if (isActive != null) 'is_active': isActive,
    };

    return remoteDataSource.get<PaginatedResponse<ClassModel>>(
      '/api/v1/classroom/',
      queryParameters: queryParams,
      fromJson: (data) => PaginatedResponse.fromJson(
        data as Map<String, dynamic>,
        (item) => ClassModel.fromJson(item as Map<String, dynamic>),
      ),
    );
  }

  /// 从本地获取班级列表
  Future<PaginatedResponse<ClassModel>?> _fetchClassesFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>(cacheKey);
    if (cachedData != null) {
      return PaginatedResponse.fromJson(
        cachedData,
        (item) => ClassModel.fromJson(item as Map<String, dynamic>),
      );
    }

    // 如果没有缓存，尝试获取默认数据
    final defaultData = await localDataSource.getDefaultData<List<dynamic>>('classes');
    if (defaultData != null) {
      final classes = defaultData
          .map((item) => ClassModel.fromJson(item as Map<String, dynamic>))
          .toList();
      return PaginatedResponse<ClassModel>(
        items: classes,
        total: classes.length,
        page: 1,
        pageSize: classes.length,
        totalPages: 1,
        hasNext: false,
        hasPrevious: false,
      );
    }

    return null;
  }

  /// 从远程获取单个班级
  Future<ApiResponse<ClassModel>> _fetchClassFromRemote(String classId, {bool includeStudents = false}) async {
    final queryParams = <String, dynamic>{
      'include_students': includeStudents,
    };

    return remoteDataSource.get<ClassModel>(
      '/api/v1/classroom/$classId',
      queryParameters: queryParams,
      fromJson: (data) => ClassModel.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取单个班级
  Future<ClassModel?> _fetchClassFromLocal(String classId) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>('${_cacheKeyPrefix}single_$classId');
    if (cachedData != null) {
      return ClassModel.fromJson(cachedData);
    }
    return null;
  }

  /// 从远程获取班级学生列表
  Future<ApiResponse<List<Student>>> _fetchClassStudentsFromRemote(String classId) async {
    return remoteDataSource.get<List<Student>>(
      '/api/v1/classroom/$classId/students',
      fromJson: (data) => (data as List)
          .map((item) => Student.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  /// 从本地获取班级学生列表
  Future<List<Student>?> _fetchClassStudentsFromLocal(String classId) async {
    final cachedData = await localDataSource.getCachedData<List<dynamic>>('${_cacheKeyPrefix}students_$classId');
    if (cachedData != null) {
      return cachedData
          .map((item) => Student.fromJson(item as Map<String, dynamic>))
          .toList();
    }
    return null;
  }

  /// 远程创建班级
  Future<ApiResponse<bool>> _createClassRemote(Map<String, dynamic> classData) async {
    final response = await remoteDataSource.post<Map<String, dynamic>>(
      '/api/v1/classroom/',
      body: classData,
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程批量创建班级
  Future<ApiResponse<bool>> _createClassesBatchRemote(List<Map<String, dynamic>> classesData) async {
    final response = await remoteDataSource.post<List<dynamic>>(
      '/api/v1/classroom/batch',
      body: {'classes': classesData},
      fromJson: (data) => data as List<dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程更新班级
  Future<ApiResponse<bool>> _updateClassRemote(String classId, Map<String, dynamic> classData) async {
    final response = await remoteDataSource.put<Map<String, dynamic>>(
      '/api/v1/classroom/$classId',
      body: classData,
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程删除班级
  Future<ApiResponse<bool>> _deleteClassRemote(String classId) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/classroom/$classId',
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程批量删除班级
  Future<ApiResponse<bool>> _deleteClassesBatchRemote(List<String> classIds) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/classroom/batch',
      headers: {'Content-Type': 'application/json'},
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程添加学生到班级
  Future<ApiResponse<bool>> _addStudentToClassRemote(String classId, String studentId) async {
    final response = await remoteDataSource.post<Map<String, dynamic>>(
      '/api/v1/classroom/$classId/students',
      body: {'student_id': studentId},
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程从班级移除学生
  Future<ApiResponse<bool>> _removeStudentFromClassRemote(String classId, String studentId) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/classroom/$classId/students/$studentId',
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程批量添加学生到班级
  Future<ApiResponse<bool>> _addStudentsToClassRemote(String classId, List<String> studentIds) async {
    final response = await remoteDataSource.post<Map<String, dynamic>>(
      '/api/v1/classroom/$classId/students/batch',
      body: {'student_ids': studentIds},
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程批量从班级移除学生
  Future<ApiResponse<bool>> _removeStudentsFromClassRemote(String classId, List<String> studentIds) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/classroom/$classId/students/batch',
      headers: {'Content-Type': 'application/json'},
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程转移学生
  Future<ApiResponse<bool>> _transferStudentRemote(String studentId, String fromClassId, String toClassId) async {
    final response = await remoteDataSource.post<Map<String, dynamic>>(
      '/api/v1/classroom/transfer-student',
      body: {
        'student_id': studentId,
        'from_class_id': fromClassId,
        'to_class_id': toClassId,
      },
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 从远程获取统计数据
  Future<ApiResponse<ClassStatistics>> _fetchStatisticsFromRemote({
    String? grade,
    String? teacherId,
  }) async {
    final queryParams = <String, dynamic>{
      if (grade != null) 'grade': grade,
      if (teacherId != null) 'teacher_id': teacherId,
    };

    return remoteDataSource.get<ClassStatistics>(
      '/api/v1/classroom/statistics',
      queryParameters: queryParams,
      fromJson: (data) => ClassStatistics.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取统计数据
  Future<ClassStatistics?> _fetchStatisticsFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>(cacheKey);
    if (cachedData != null) {
      return ClassStatistics.fromJson(cachedData);
    }
    return null;
  }

  /// 构建班级缓存键
  String _buildClassesCacheKey({
    String? grade,
    String? teacherId,
    String? searchQuery,
    bool? isActive,
    bool includeStudents = false,
    int page = 1,
    int pageSize = 20,
  }) {
    final parts = <String>[
      _cacheKeyPrefix,
      'list',
      if (grade != null) 'grade_$grade',
      if (teacherId != null) 'teacher_$teacherId',
      if (searchQuery != null) 'search_${searchQuery.hashCode}',
      if (isActive != null) 'active_$isActive',
      'students_$includeStudents',
      'page_$page',
      'size_$pageSize',
    ];
    return parts.join('_');
  }

  /// 构建统计缓存键
  String _buildStatisticsCacheKey({
    String? grade,
    String? teacherId,
  }) {
    final parts = <String>[
      _statisticsCacheKey,
      if (grade != null) 'grade_$grade',
      if (teacherId != null) 'teacher_$teacherId',
    ];
    return parts.join('_');
  }

  /// 清除班级相关缓存
  Future<void> _clearClassCache(String classId) async {
    try {
      await clearCache('${_cacheKeyPrefix}single_$classId');
      await clearCache('${_cacheKeyPrefix}single_${classId}_students_true');
      await clearCache('${_cacheKeyPrefix}single_${classId}_students_false');
      await clearCache('${_cacheKeyPrefix}students_$classId');
      AppLogger.debug('ClassRepository: 已清除班级缓存', {'classId': classId});
    } catch (e) {
      AppLogger.warning('ClassRepository: 清除班级缓存失败', {
        'classId': classId,
        'error': e.toString(),
      });
    }
  }

  /// 清除相关缓存
  Future<void> _clearRelatedCache() async {
    try {
      // 这里应该清除所有相关的班级缓存
      // 在实际实现中，可以维护一个缓存键列表
      await clearAllCache();
      AppLogger.debug('ClassRepository: 已清除相关缓存');
    } catch (e) {
      AppLogger.warning('ClassRepository: 清除缓存失败', {'error': e.toString()});
    }
  }

  @override
  Future<void> _syncSingleItem(Map<String, dynamic> item) async {
    final syncKey = item['syncKey'] as String;
    final data = item['data'];
    
    try {
      if (syncKey.startsWith('create_class_')) {
        await _createClassRemote(data as Map<String, dynamic>);
      } else if (syncKey.startsWith('create_classes_batch_')) {
        await _createClassesBatchRemote(data as List<Map<String, dynamic>>);
      } else if (syncKey.startsWith('update_class_')) {
        final classId = syncKey.split('_').last;
        await _updateClassRemote(classId, data as Map<String, dynamic>);
      } else if (syncKey.startsWith('delete_class_')) {
        await _deleteClassRemote(data as String);
      } else if (syncKey.startsWith('delete_classes_batch_')) {
        await _deleteClassesBatchRemote(data as List<String>);
      } else if (syncKey.startsWith('toggle_class_status_')) {
        final classId = syncKey.split('_').last;
        await _updateClassRemote(classId, data as Map<String, dynamic>);
      } else if (syncKey.startsWith('add_student_to_class_')) {
        final parts = syncKey.split('_');
        final classId = parts[parts.length - 2];
        final studentId = parts.last;
        await _addStudentToClassRemote(classId, studentId);
      } else if (syncKey.startsWith('remove_student_from_class_')) {
        final parts = syncKey.split('_');
        final classId = parts[parts.length - 2];
        final studentId = parts.last;
        await _removeStudentFromClassRemote(classId, studentId);
      } else if (syncKey.startsWith('add_students_to_class_')) {
        final classId = (data as Map<String, dynamic>)['class_id'] as String;
        final studentIds = (data['student_ids'] as List).cast<String>();
        await _addStudentsToClassRemote(classId, studentIds);
      } else if (syncKey.startsWith('remove_students_from_class_')) {
        final classId = (data as Map<String, dynamic>)['class_id'] as String;
        final studentIds = (data['student_ids'] as List).cast<String>();
        await _removeStudentsFromClassRemote(classId, studentIds);
      } else if (syncKey.startsWith('transfer_student_')) {
        final studentId = (data as Map<String, dynamic>)['student_id'] as String;
        final fromClassId = data['from_class_id'] as String;
        final toClassId = data['to_class_id'] as String;
        await _transferStudentRemote(studentId, fromClassId, toClassId);
      }
      
      // 同步成功，清除标记
      await localDataSource.clearSyncMark(syncKey);
      AppLogger.info('ClassRepository: 单项同步成功', {'syncKey': syncKey});
    } catch (e, stackTrace) {
      AppLogger.error('ClassRepository: 单项同步失败', e, stackTrace);
      rethrow;
    }
  }
}