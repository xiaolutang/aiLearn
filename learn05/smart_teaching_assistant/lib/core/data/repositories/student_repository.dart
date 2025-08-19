import 'dart:io';

import '../datasources/local_data_source.dart';
import '../datasources/remote_data_source.dart';
import '../../models/api_response.dart';
import '../../models/student_model.dart';
import '../../services/connectivity_service.dart';
import '../../utils/app_logger.dart';
import 'base_repository.dart';

/// 学生统计数据模型
class StudentStatistics {
  final int totalStudents;
  final int activeStudents;
  final int inactiveStudents;
  final Map<String, int> genderDistribution;
  final Map<String, int> gradeDistribution;
  final Map<String, int> classDistribution;
  final double averageAge;
  final DateTime? oldestBirthDate;
  final DateTime? youngestBirthDate;

  StudentStatistics({
    required this.totalStudents,
    required this.activeStudents,
    required this.inactiveStudents,
    required this.genderDistribution,
    required this.gradeDistribution,
    required this.classDistribution,
    required this.averageAge,
    this.oldestBirthDate,
    this.youngestBirthDate,
  });

  factory StudentStatistics.fromJson(Map<String, dynamic> json) {
    return StudentStatistics(
      totalStudents: json['total_students'] ?? 0,
      activeStudents: json['active_students'] ?? 0,
      inactiveStudents: json['inactive_students'] ?? 0,
      genderDistribution: Map<String, int>.from(
        (json['gender_distribution'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
      gradeDistribution: Map<String, int>.from(
        (json['grade_distribution'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
      classDistribution: Map<String, int>.from(
        (json['class_distribution'] ?? {}).map(
          (key, value) => MapEntry(key, (value ?? 0).toInt()),
        ),
      ),
      averageAge: (json['average_age'] ?? 0).toDouble(),
      oldestBirthDate: json['oldest_birth_date'] != null 
          ? DateTime.parse(json['oldest_birth_date']) 
          : null,
      youngestBirthDate: json['youngest_birth_date'] != null 
          ? DateTime.parse(json['youngest_birth_date']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_students': totalStudents,
      'active_students': activeStudents,
      'inactive_students': inactiveStudents,
      'gender_distribution': genderDistribution,
      'grade_distribution': gradeDistribution,
      'class_distribution': classDistribution,
      'average_age': averageAge,
      'oldest_birth_date': oldestBirthDate?.toIso8601String(),
      'youngest_birth_date': youngestBirthDate?.toIso8601String(),
    };
  }
}

/// 学生仓库接口
abstract class StudentRepository {
  /// 获取学生列表
  Future<ApiResponse<PaginatedResponse<Student>>> getStudents({
    String? classId,
    String? grade,
    String? searchQuery,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  });

  /// 获取单个学生
  Future<ApiResponse<Student>> getStudent(String studentId);

  /// 根据学号获取学生
  Future<ApiResponse<Student>> getStudentByNumber(String studentNumber);

  /// 创建学生
  Future<ApiResponse<Student>> createStudent(Map<String, dynamic> studentData);

  /// 批量创建学生
  Future<ApiResponse<List<Student>>> createStudentsBatch(List<Map<String, dynamic>> studentsData);

  /// 更新学生
  Future<ApiResponse<Student>> updateStudent(String studentId, Map<String, dynamic> studentData);

  /// 删除学生
  Future<ApiResponse<bool>> deleteStudent(String studentId);

  /// 批量删除学生
  Future<ApiResponse<bool>> deleteStudentsBatch(List<String> studentIds);

  /// 激活/停用学生
  Future<ApiResponse<bool>> toggleStudentStatus(String studentId, bool isActive);

  /// 获取学生统计
  Future<ApiResponse<StudentStatistics>> getStudentStatistics({
    String? classId,
    String? grade,
  });

  /// 导入学生数据
  Future<ApiResponse<Map<String, dynamic>>> importStudents(
    String filePath, {
    String? classId,
  });

  /// 导出学生数据
  Future<ApiResponse<String>> exportStudents({
    String? classId,
    String? grade,
    String format = 'excel',
  });

  /// 搜索学生
  Future<ApiResponse<List<Student>>> searchStudents(String query, {
    String? classId,
    String? grade,
    int limit = 10,
  });
}

/// 学生仓库实现类
class StudentRepositoryImpl extends BaseRepository implements StudentRepository {
  static const String _cacheKeyPrefix = 'students_';
  static const String _statisticsCacheKey = 'student_statistics';
  static const Duration _cacheExpiry = Duration(minutes: 30);

  StudentRepositoryImpl({
    required RemoteDataSource remoteDataSource,
    required LocalDataSource localDataSource,
    required ConnectivityService connectivityService,
  }) : super(
          remoteDataSource: remoteDataSource,
          localDataSource: localDataSource,
          connectivityService: connectivityService,
        );

  @override
  Future<ApiResponse<PaginatedResponse<Student>>> getStudents({
    String? classId,
    String? grade,
    String? searchQuery,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  }) async {
    final cacheKey = _buildStudentsCacheKey(
      classId: classId,
      grade: grade,
      searchQuery: searchQuery,
      isActive: isActive,
      page: page,
      pageSize: pageSize,
    );

    return fetchData<PaginatedResponse<Student>>(
      remoteCall: () => _fetchStudentsFromRemote(
        classId: classId,
        grade: grade,
        searchQuery: searchQuery,
        isActive: isActive,
        page: page,
        pageSize: pageSize,
      ),
      localCall: () => _fetchStudentsFromLocal(cacheKey),
      cacheKey: cacheKey,
      forceRefresh: forceRefresh,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<Student>> getStudent(String studentId) async {
    final cacheKey = '${_cacheKeyPrefix}single_$studentId';

    return fetchData<Student>(
      remoteCall: () => _fetchStudentFromRemote(studentId),
      localCall: () => _fetchStudentFromLocal(studentId),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<Student>> getStudentByNumber(String studentNumber) async {
    final cacheKey = '${_cacheKeyPrefix}number_$studentNumber';

    return fetchData<Student>(
      remoteCall: () => _fetchStudentByNumberFromRemote(studentNumber),
      localCall: () => _fetchStudentByNumberFromLocal(studentNumber),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<Student>> createStudent(Map<String, dynamic> studentData) async {
    return syncToServer<Map<String, dynamic>>(
      data: studentData,
      uploadCall: (data) => _createStudentRemote(data),
      syncKey: 'create_student_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success && response.data == true) {
        // 清除相关缓存
        _clearRelatedCache();
        // 返回创建的Student对象
        return ApiResponse.success(
          data: Student.fromJson(studentData..['id'] = 'temp_${DateTime.now().millisecondsSinceEpoch}'),
          message: response.message,
        );
      }
      return ApiResponse<Student>.error(message: response.message);
    });
  }

  @override
  Future<ApiResponse<List<Student>>> createStudentsBatch(List<Map<String, dynamic>> studentsData) async {
    return syncToServer<List<Map<String, dynamic>>>(
      data: studentsData,
      uploadCall: (data) => _createStudentsBatchRemote(data),
      syncKey: 'create_students_batch_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success && response.data == true) {
        // 清除相关缓存
        _clearRelatedCache();
        // 返回创建的Student对象列表
        final students = studentsData.map((data) => 
          Student.fromJson(data..['id'] = 'temp_${DateTime.now().millisecondsSinceEpoch}')
        ).toList();
        return ApiResponse.success(
          data: students,
          message: response.message,
        );
      }
      return ApiResponse<List<Student>>.error(message: response.message);
    });
  }

  @override
  Future<ApiResponse<Student>> updateStudent(String studentId, Map<String, dynamic> studentData) async {
    return syncToServer<Map<String, dynamic>>(
      data: studentData,
      uploadCall: (data) => _updateStudentRemote(studentId, data),
      syncKey: 'update_student_$studentId',
    ).then((response) {
      if (response.success && response.data == true) {
        // 清除相关缓存
        _clearRelatedCache();
        clearCache('${_cacheKeyPrefix}single_$studentId');
        // 返回更新的Student对象
        return ApiResponse.success(
          data: Student.fromJson(studentData..['id'] = studentId),
          message: response.message,
        );
      }
      return ApiResponse<Student>.error(message: response.message);
    });
  }

  @override
  Future<ApiResponse<bool>> deleteStudent(String studentId) async {
    return syncToServer<String>(
      data: studentId,
      uploadCall: (id) => _deleteStudentRemote(id),
      syncKey: 'delete_student_$studentId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        clearCache('${_cacheKeyPrefix}single_$studentId');
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> deleteStudentsBatch(List<String> studentIds) async {
    return syncToServer<List<String>>(
      data: studentIds,
      uploadCall: (ids) => _deleteStudentsBatchRemote(ids),
      syncKey: 'delete_students_batch_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        for (final studentId in studentIds) {
          clearCache('${_cacheKeyPrefix}single_$studentId');
        }
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> toggleStudentStatus(String studentId, bool isActive) async {
    return syncToServer<Map<String, dynamic>>(
      data: {'is_active': isActive},
      uploadCall: (data) => _updateStudentRemote(studentId, data),
      syncKey: 'toggle_student_status_$studentId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        clearCache('${_cacheKeyPrefix}single_$studentId');
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<StudentStatistics>> getStudentStatistics({
    String? classId,
    String? grade,
  }) async {
    final cacheKey = _buildStatisticsCacheKey(
      classId: classId,
      grade: grade,
    );

    return fetchData<StudentStatistics>(
      remoteCall: () => _fetchStatisticsFromRemote(
        classId: classId,
        grade: grade,
      ),
      localCall: () => _fetchStatisticsFromLocal(cacheKey),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<Map<String, dynamic>>> importStudents(
    String filePath, {
    String? classId,
  }) async {
    try {
      final response = await remoteDataSource.uploadFile<Map<String, dynamic>>(
        '/api/v1/students/import',
        File(filePath),
        fields: {
          if (classId != null) 'class_id': classId,
        },
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success) {
        // 导入成功，清除相关缓存
        _clearRelatedCache();
        AppLogger.info('StudentRepository: 学生导入成功', {
          'filePath': filePath,
          'classId': classId,
        });
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('StudentRepository: 学生导入失败', e, stackTrace);
      return ApiResponse.error(message: '学生导入失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<String>> exportStudents({
    String? classId,
    String? grade,
    String format = 'excel',
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'format': format,
        if (classId != null) 'class_id': classId,
        if (grade != null) 'grade': grade,
      };

      final response = await remoteDataSource.get<String>(
        '/api/v1/students/export',
        queryParameters: queryParams,
        fromJson: (data) => data as String,
      );

      if (response.success) {
        AppLogger.info('StudentRepository: 学生导出成功', {
          'classId': classId,
          'grade': grade,
          'format': format,
        });
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('StudentRepository: 学生导出失败', e, stackTrace);
      return ApiResponse.error(message: '学生导出失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<List<Student>>> searchStudents(String query, {
    String? classId,
    String? grade,
    int limit = 10,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'q': query,
        'limit': limit,
        if (classId != null) 'class_id': classId,
        if (grade != null) 'grade': grade,
      };

      final response = await remoteDataSource.get<List<Student>>(
        '/api/v1/students/search',
        queryParameters: queryParams,
        fromJson: (data) => (data as List)
            .map((item) => Student.fromJson(item as Map<String, dynamic>))
            .toList(),
      );

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('StudentRepository: 学生搜索失败', e, stackTrace);
      return ApiResponse.error(message: '学生搜索失败: ${e.toString()}');
    }
  }

  // 私有方法实现

  /// 从远程获取学生列表
  Future<ApiResponse<PaginatedResponse<Student>>> _fetchStudentsFromRemote({
    String? classId,
    String? grade,
    String? searchQuery,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
      if (classId != null) 'class_id': classId,
      if (grade != null) 'grade': grade,
      if (searchQuery != null) 'search': searchQuery,
      if (isActive != null) 'is_active': isActive,
    };

    return remoteDataSource.get<PaginatedResponse<Student>>(
      '/api/v1/students/',
      queryParameters: queryParams,
      fromJson: (data) => PaginatedResponse.fromJson(
        data as Map<String, dynamic>,
        (item) => Student.fromJson(item as Map<String, dynamic>),
      ),
    );
  }

  /// 从本地获取学生列表
  Future<PaginatedResponse<Student>?> _fetchStudentsFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>(cacheKey);
    if (cachedData != null) {
      return PaginatedResponse.fromJson(
        cachedData,
        (item) => Student.fromJson(item as Map<String, dynamic>),
      );
    }

    // 如果没有缓存，尝试获取默认数据
    final defaultData = await localDataSource.getDefaultData<List<dynamic>>('students');
    if (defaultData != null) {
      final students = defaultData
          .map((item) => Student.fromJson(item as Map<String, dynamic>))
          .toList();
      return PaginatedResponse<Student>(
        items: students,
        total: students.length,
        page: 1,
        pageSize: students.length,
        totalPages: 1,
        hasNext: false,
        hasPrevious: false,
      );
    }

    return null;
  }

  /// 从远程获取单个学生
  Future<ApiResponse<Student>> _fetchStudentFromRemote(String studentId) async {
    return remoteDataSource.get<Student>(
      '/api/v1/students/$studentId',
      fromJson: (data) => Student.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取单个学生
  Future<Student?> _fetchStudentFromLocal(String studentId) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>('${_cacheKeyPrefix}single_$studentId');
    if (cachedData != null) {
      return Student.fromJson(cachedData);
    }
    return null;
  }

  /// 从远程根据学号获取学生
  Future<ApiResponse<Student>> _fetchStudentByNumberFromRemote(String studentNumber) async {
    return remoteDataSource.get<Student>(
      '/api/v1/students/by-number/$studentNumber',
      fromJson: (data) => Student.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地根据学号获取学生
  Future<Student?> _fetchStudentByNumberFromLocal(String studentNumber) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>('${_cacheKeyPrefix}number_$studentNumber');
    if (cachedData != null) {
      return Student.fromJson(cachedData);
    }
    return null;
  }

  /// 远程创建学生
  Future<ApiResponse<bool>> _createStudentRemote(Map<String, dynamic> studentData) async {
    final response = await remoteDataSource.post<Map<String, dynamic>>(
      '/api/v1/students/',
      body: studentData,
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程批量创建学生
  Future<ApiResponse<bool>> _createStudentsBatchRemote(List<Map<String, dynamic>> studentsData) async {
    final response = await remoteDataSource.post<List<dynamic>>(
      '/api/v1/students/batch',
      body: {'students': studentsData},
      fromJson: (data) => data as List<dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程更新学生
  Future<ApiResponse<bool>> _updateStudentRemote(String studentId, Map<String, dynamic> studentData) async {
    final response = await remoteDataSource.put<Map<String, dynamic>>(
      '/api/v1/students/$studentId',
      body: studentData,
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程删除学生
  Future<ApiResponse<bool>> _deleteStudentRemote(String studentId) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/students/$studentId',
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程批量删除学生
  Future<ApiResponse<bool>> _deleteStudentsBatchRemote(List<String> studentIds) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/students/batch',
      headers: {'Content-Type': 'application/json'},
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 从远程获取统计数据
  Future<ApiResponse<StudentStatistics>> _fetchStatisticsFromRemote({
    String? classId,
    String? grade,
  }) async {
    final queryParams = <String, dynamic>{
      if (classId != null) 'class_id': classId,
      if (grade != null) 'grade': grade,
    };

    return remoteDataSource.get<StudentStatistics>(
      '/api/v1/students/statistics',
      queryParameters: queryParams,
      fromJson: (data) => StudentStatistics.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取统计数据
  Future<StudentStatistics?> _fetchStatisticsFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>(cacheKey);
    if (cachedData != null) {
      return StudentStatistics.fromJson(cachedData);
    }
    return null;
  }

  /// 构建学生缓存键
  String _buildStudentsCacheKey({
    String? classId,
    String? grade,
    String? searchQuery,
    bool? isActive,
    int page = 1,
    int pageSize = 20,
  }) {
    final parts = <String>[
      _cacheKeyPrefix,
      'list',
      if (classId != null) 'class_$classId',
      if (grade != null) 'grade_$grade',
      if (searchQuery != null) 'search_${searchQuery.hashCode}',
      if (isActive != null) 'active_$isActive',
      'page_$page',
      'size_$pageSize',
    ];
    return parts.join('_');
  }

  /// 构建统计缓存键
  String _buildStatisticsCacheKey({
    String? classId,
    String? grade,
  }) {
    final parts = <String>[
      _statisticsCacheKey,
      if (classId != null) 'class_$classId',
      if (grade != null) 'grade_$grade',
    ];
    return parts.join('_');
  }

  /// 清除相关缓存
  Future<void> _clearRelatedCache() async {
    try {
      // 这里应该清除所有相关的学生缓存
      // 在实际实现中，可以维护一个缓存键列表
      await clearAllCache();
      AppLogger.debug('StudentRepository: 已清除相关缓存');
    } catch (e) {
      AppLogger.warning('StudentRepository: 清除缓存失败', {'error': e.toString()});
    }
  }

  @override
  Future<void> _syncSingleItem(Map<String, dynamic> item) async {
    final syncKey = item['syncKey'] as String;
    final data = item['data'];
    
    try {
      if (syncKey.startsWith('create_student_')) {
        await _createStudentRemote(data as Map<String, dynamic>);
      } else if (syncKey.startsWith('create_students_batch_')) {
        await _createStudentsBatchRemote(data as List<Map<String, dynamic>>);
      } else if (syncKey.startsWith('update_student_')) {
        final studentId = syncKey.split('_').last;
        await _updateStudentRemote(studentId, data as Map<String, dynamic>);
      } else if (syncKey.startsWith('delete_student_')) {
        await _deleteStudentRemote(data as String);
      } else if (syncKey.startsWith('delete_students_batch_')) {
        await _deleteStudentsBatchRemote(data as List<String>);
      } else if (syncKey.startsWith('toggle_student_status_')) {
        final studentId = syncKey.split('_').last;
        await _updateStudentRemote(studentId, data as Map<String, dynamic>);
      }
      
      // 同步成功，清除标记
      await localDataSource.clearSyncMark(syncKey);
      AppLogger.info('StudentRepository: 单项同步成功', {'syncKey': syncKey});
    } catch (e, stackTrace) {
      AppLogger.error('StudentRepository: 单项同步失败', e, stackTrace);
      rethrow;
    }
  }
}