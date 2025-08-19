import 'dart:io';

import '../datasources/local_data_source.dart';
import '../datasources/remote_data_source.dart';
import '../../models/api_response.dart';
import '../../models/grade_model.dart';
import '../../services/connectivity_service.dart';
import '../../utils/app_logger.dart';
import 'base_repository.dart';





/// 成绩仓库接口
abstract class GradeRepository {
  /// 获取成绩列表
  Future<ApiResponse<PaginatedResponse<Grade>>> getGrades({
    String? classId,
    String? subjectId,
    String? studentId,
    String? examType,
    DateTime? startDate,
    DateTime? endDate,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  });

  /// 获取单个成绩
  Future<ApiResponse<Grade>> getGrade(String gradeId);

  /// 创建成绩
  Future<ApiResponse<Grade>> createGrade(Map<String, dynamic> gradeData);

  /// 批量创建成绩
  Future<ApiResponse<List<Grade>>> createGradesBatch(List<Map<String, dynamic>> gradesData);

  /// 更新成绩
  Future<ApiResponse<Grade>> updateGrade(String gradeId, Map<String, dynamic> gradeData);

  /// 删除成绩
  Future<ApiResponse<bool>> deleteGrade(String gradeId);

  /// 批量删除成绩
  Future<ApiResponse<bool>> deleteGradesBatch(List<String> gradeIds);

  /// 获取成绩统计
  Future<ApiResponse<GradeStatistics>> getGradeStatistics({
    String? classId,
    String? subjectId,
    DateTime? startDate,
    DateTime? endDate,
  });

  /// 导入成绩数据
  Future<ApiResponse<Map<String, dynamic>>> importGrades(
    String filePath, {
    String? classId,
    String? examType,
  });

  /// 导出成绩数据
  Future<ApiResponse<String>> exportGrades({
    String? classId,
    String? subjectId,
    DateTime? startDate,
    DateTime? endDate,
    String format = 'excel',
  });
}

/// 成绩仓库实现类
class GradeRepositoryImpl extends BaseRepository implements GradeRepository {
  static const String _cacheKeyPrefix = 'grades_';
  static const String _statisticsCacheKey = 'grade_statistics';
  static const Duration _cacheExpiry = Duration(minutes: 30);

  GradeRepositoryImpl({
    required RemoteDataSource remoteDataSource,
    required LocalDataSource localDataSource,
    required ConnectivityService connectivityService,
  }) : super(
          remoteDataSource: remoteDataSource,
          localDataSource: localDataSource,
          connectivityService: connectivityService,
        );

  @override
  Future<ApiResponse<PaginatedResponse<Grade>>> getGrades({
    String? classId,
    String? subjectId,
    String? studentId,
    String? examType,
    DateTime? startDate,
    DateTime? endDate,
    int page = 1,
    int pageSize = 20,
    bool forceRefresh = false,
  }) async {
    final cacheKey = _buildGradesCacheKey(
      classId: classId,
      subjectId: subjectId,
      studentId: studentId,
      examType: examType,
      startDate: startDate,
      endDate: endDate,
      page: page,
      pageSize: pageSize,
    );

    return fetchData<PaginatedResponse<Grade>>(
      remoteCall: () => _fetchGradesFromRemote(
        classId: classId,
        subjectId: subjectId,
        studentId: studentId,
        examType: examType,
        startDate: startDate,
        endDate: endDate,
        page: page,
        pageSize: pageSize,
      ),
      localCall: () => _fetchGradesFromLocal(cacheKey),
      cacheKey: cacheKey,
      forceRefresh: forceRefresh,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<Grade>> getGrade(String gradeId) async {
    final cacheKey = '${_cacheKeyPrefix}single_$gradeId';

    return fetchData<Grade>(
      remoteCall: () => _fetchGradeFromRemote(gradeId),
      localCall: () => _fetchGradeFromLocal(gradeId),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<Grade>> createGrade(Map<String, dynamic> gradeData) async {
    return syncToServer<Map<String, dynamic>>(
      data: gradeData,
      uploadCall: (data) => _createGradeRemote(data),
      syncKey: 'create_grade_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success && response.data == true) {
        // 清除相关缓存
        _clearRelatedCache();
        // 这里应该返回创建的Grade对象，简化处理
        return ApiResponse.success(
          data: Grade.fromJson(gradeData..['id'] = 'temp_${DateTime.now().millisecondsSinceEpoch}'),
          message: response.message,
        );
      }
      return ApiResponse<Grade>.error(message: response.message);
    });
  }

  @override
  Future<ApiResponse<List<Grade>>> createGradesBatch(List<Map<String, dynamic>> gradesData) async {
    return syncToServer<List<Map<String, dynamic>>>(
      data: gradesData,
      uploadCall: (data) => _createGradesBatchRemote(data),
      syncKey: 'create_grades_batch_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success && response.data == true) {
        // 清除相关缓存
        _clearRelatedCache();
        // 返回创建的Grade对象列表
        final grades = gradesData.map((data) => 
          Grade.fromJson(data..['id'] = 'temp_${DateTime.now().millisecondsSinceEpoch}')
        ).toList();
        return ApiResponse.success(
          data: grades,
          message: response.message,
        );
      }
      return ApiResponse<List<Grade>>.error(message: response.message);
    });
  }

  @override
  Future<ApiResponse<Grade>> updateGrade(String gradeId, Map<String, dynamic> gradeData) async {
    return syncToServer<Map<String, dynamic>>(
      data: gradeData,
      uploadCall: (data) => _updateGradeRemote(gradeId, data),
      syncKey: 'update_grade_$gradeId',
    ).then((response) {
      if (response.success && response.data == true) {
        // 清除相关缓存
        _clearRelatedCache();
        clearCache('${_cacheKeyPrefix}single_$gradeId');
        // 返回更新的Grade对象
        return ApiResponse.success(
          data: Grade.fromJson(gradeData..['id'] = gradeId),
          message: response.message,
        );
      }
      return ApiResponse<Grade>.error(message: response.message);
    });
  }

  @override
  Future<ApiResponse<bool>> deleteGrade(String gradeId) async {
    return syncToServer<String>(
      data: gradeId,
      uploadCall: (id) => _deleteGradeRemote(id),
      syncKey: 'delete_grade_$gradeId',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        clearCache('${_cacheKeyPrefix}single_$gradeId');
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<bool>> deleteGradesBatch(List<String> gradeIds) async {
    return syncToServer<List<String>>(
      data: gradeIds,
      uploadCall: (ids) => _deleteGradesBatchRemote(ids),
      syncKey: 'delete_grades_batch_${DateTime.now().millisecondsSinceEpoch}',
    ).then((response) {
      if (response.success) {
        // 清除相关缓存
        _clearRelatedCache();
        for (final gradeId in gradeIds) {
          clearCache('${_cacheKeyPrefix}single_$gradeId');
        }
      }
      return response;
    });
  }

  @override
  Future<ApiResponse<GradeStatistics>> getGradeStatistics({
    String? classId,
    String? subjectId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final cacheKey = _buildStatisticsCacheKey(
      classId: classId,
      subjectId: subjectId,
      startDate: startDate,
      endDate: endDate,
    );

    return fetchData<GradeStatistics>(
      remoteCall: () => _fetchStatisticsFromRemote(
        classId: classId,
        subjectId: subjectId,
        startDate: startDate,
        endDate: endDate,
      ),
      localCall: () => _fetchStatisticsFromLocal(cacheKey),
      cacheKey: cacheKey,
      cacheExpiry: _cacheExpiry,
    );
  }

  @override
  Future<ApiResponse<Map<String, dynamic>>> importGrades(
    String filePath, {
    String? classId,
    String? examType,
  }) async {
    try {
      final response = await remoteDataSource.uploadFile<Map<String, dynamic>>(
        '/api/v1/grades/import',
        File(filePath),
        fields: {
          if (classId != null) 'class_id': classId,
          if (examType != null) 'exam_type': examType,
        },
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success) {
        // 导入成功，清除相关缓存
        _clearRelatedCache();
        AppLogger.info('GradeRepository: 成绩导入成功', {
          'filePath': filePath,
          'classId': classId,
          'examType': examType,
        });
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('GradeRepository: 成绩导入失败', e, stackTrace);
      return ApiResponse.error(message: '成绩导入失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<String>> exportGrades({
    String? classId,
    String? subjectId,
    DateTime? startDate,
    DateTime? endDate,
    String format = 'excel',
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'format': format,
        if (classId != null) 'class_id': classId,
        if (subjectId != null) 'subject_id': subjectId,
        if (startDate != null) 'start_date': startDate.toIso8601String(),
        if (endDate != null) 'end_date': endDate.toIso8601String(),
      };

      final response = await remoteDataSource.get<String>(
        '/api/v1/grades/export',
        queryParameters: queryParams,
        fromJson: (data) => data as String,
      );

      if (response.success) {
        AppLogger.info('GradeRepository: 成绩导出成功', {
          'classId': classId,
          'subjectId': subjectId,
          'format': format,
        });
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('GradeRepository: 成绩导出失败', e, stackTrace);
      return ApiResponse.error(message: '成绩导出失败: ${e.toString()}');
    }
  }

  // 私有方法实现

  /// 从远程获取成绩列表
  Future<ApiResponse<PaginatedResponse<Grade>>> _fetchGradesFromRemote({
    String? classId,
    String? subjectId,
    String? studentId,
    String? examType,
    DateTime? startDate,
    DateTime? endDate,
    int page = 1,
    int pageSize = 20,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
      if (classId != null) 'class_id': classId,
      if (subjectId != null) 'subject_id': subjectId,
      if (studentId != null) 'student_id': studentId,
      if (examType != null) 'exam_type': examType,
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
    };

    return remoteDataSource.get<PaginatedResponse<Grade>>(
      '/api/v1/grades/',
      queryParameters: queryParams,
      fromJson: (data) => PaginatedResponse.fromJson(
        data as Map<String, dynamic>,
        (item) => Grade.fromJson(item as Map<String, dynamic>),
      ),
    );
  }

  /// 从本地获取成绩列表
  Future<PaginatedResponse<Grade>?> _fetchGradesFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>(cacheKey);
    if (cachedData != null) {
      return PaginatedResponse.fromJson(
        cachedData,
        (item) => Grade.fromJson(item as Map<String, dynamic>),
      );
    }

    // 如果没有缓存，尝试获取默认数据
    final defaultData = await localDataSource.getDefaultData<List<dynamic>>('grades');
    if (defaultData != null) {
      final grades = defaultData
          .map((item) => Grade.fromJson(item as Map<String, dynamic>))
          .toList();
      return PaginatedResponse<Grade>(
        items: grades,
        total: grades.length,
        page: 1,
        pageSize: grades.length,
        totalPages: 1,
        hasNext: false,
        hasPrevious: false,
      );
    }

    return null;
  }

  /// 从远程获取单个成绩
  Future<ApiResponse<Grade>> _fetchGradeFromRemote(String gradeId) async {
    return remoteDataSource.get<Grade>(
      '/api/v1/grades/$gradeId',
      fromJson: (data) => Grade.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取单个成绩
  Future<Grade?> _fetchGradeFromLocal(String gradeId) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>('${_cacheKeyPrefix}single_$gradeId');
    if (cachedData != null) {
      return Grade.fromJson(cachedData);
    }
    return null;
  }

  /// 远程创建成绩
  Future<ApiResponse<bool>> _createGradeRemote(Map<String, dynamic> gradeData) async {
    final response = await remoteDataSource.post<Map<String, dynamic>>(
      '/api/v1/grades/',
      body: gradeData,
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程批量创建成绩
  Future<ApiResponse<bool>> _createGradesBatchRemote(List<Map<String, dynamic>> gradesData) async {
    final response = await remoteDataSource.post<List<dynamic>>(
      '/api/v1/grades/batch',
      body: {'grades': gradesData},
      fromJson: (data) => data as List<dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程更新成绩
  Future<ApiResponse<bool>> _updateGradeRemote(String gradeId, Map<String, dynamic> gradeData) async {
    final response = await remoteDataSource.put<Map<String, dynamic>>(
      '/api/v1/grades/$gradeId',
      body: gradeData,
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程删除成绩
  Future<ApiResponse<bool>> _deleteGradeRemote(String gradeId) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/grades/$gradeId',
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 远程批量删除成绩
  Future<ApiResponse<bool>> _deleteGradesBatchRemote(List<String> gradeIds) async {
    final response = await remoteDataSource.delete<Map<String, dynamic>>(
      '/api/v1/grades/batch',
      headers: {'Content-Type': 'application/json'},
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  /// 从远程获取统计数据
  Future<ApiResponse<GradeStatistics>> _fetchStatisticsFromRemote({
    String? classId,
    String? subjectId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = <String, dynamic>{
      if (classId != null) 'class_id': classId,
      if (subjectId != null) 'subject_id': subjectId,
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
    };

    return remoteDataSource.get<GradeStatistics>(
      '/api/v1/grades/statistics',
      queryParameters: queryParams,
      fromJson: (data) => GradeStatistics.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取统计数据
  Future<GradeStatistics?> _fetchStatisticsFromLocal(String cacheKey) async {
    final cachedData = await localDataSource.getCachedData<Map<String, dynamic>>(cacheKey);
    if (cachedData != null) {
      return GradeStatistics.fromJson(cachedData);
    }
    return null;
  }

  /// 构建成绩缓存键
  String _buildGradesCacheKey({
    String? classId,
    String? subjectId,
    String? studentId,
    String? examType,
    DateTime? startDate,
    DateTime? endDate,
    int page = 1,
    int pageSize = 20,
  }) {
    final parts = <String>[
      _cacheKeyPrefix,
      'list',
      if (classId != null) 'class_$classId',
      if (subjectId != null) 'subject_$subjectId',
      if (studentId != null) 'student_$studentId',
      if (examType != null) 'exam_$examType',
      if (startDate != null) 'start_${startDate.millisecondsSinceEpoch}',
      if (endDate != null) 'end_${endDate.millisecondsSinceEpoch}',
      'page_$page',
      'size_$pageSize',
    ];
    return parts.join('_');
  }

  /// 构建统计缓存键
  String _buildStatisticsCacheKey({
    String? classId,
    String? subjectId,
    DateTime? startDate,
    DateTime? endDate,
  }) {
    final parts = <String>[
      _statisticsCacheKey,
      if (classId != null) 'class_$classId',
      if (subjectId != null) 'subject_$subjectId',
      if (startDate != null) 'start_${startDate.millisecondsSinceEpoch}',
      if (endDate != null) 'end_${endDate.millisecondsSinceEpoch}',
    ];
    return parts.join('_');
  }

  /// 清除相关缓存
  Future<void> _clearRelatedCache() async {
    try {
      // 这里应该清除所有相关的成绩缓存
      // 在实际实现中，可以维护一个缓存键列表
      await clearAllCache();
      AppLogger.debug('GradeRepository: 已清除相关缓存');
    } catch (e) {
      AppLogger.warning('GradeRepository: 清除缓存失败', {'error': e.toString()});
    }
  }

  @override
  Future<void> _syncSingleItem(Map<String, dynamic> item) async {
    final syncKey = item['syncKey'] as String;
    final data = item['data'];
    
    try {
      if (syncKey.startsWith('create_grade_')) {
        await _createGradeRemote(data as Map<String, dynamic>);
      } else if (syncKey.startsWith('create_grades_batch_')) {
        await _createGradesBatchRemote(data as List<Map<String, dynamic>>);
      } else if (syncKey.startsWith('update_grade_')) {
        final gradeId = syncKey.split('_').last;
        await _updateGradeRemote(gradeId, data as Map<String, dynamic>);
      } else if (syncKey.startsWith('delete_grade_')) {
        await _deleteGradeRemote(data as String);
      } else if (syncKey.startsWith('delete_grades_batch_')) {
        await _deleteGradesBatchRemote(data as List<String>);
      }
      
      // 同步成功，清除标记
      await localDataSource.clearSyncMark(syncKey);
      AppLogger.info('GradeRepository: 单项同步成功', {'syncKey': syncKey});
    } catch (e, stackTrace) {
      AppLogger.error('GradeRepository: 单项同步失败', e, stackTrace);
      rethrow;
    }
  }
}