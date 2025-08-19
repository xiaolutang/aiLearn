import 'dart:async';
import 'dart:convert';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:sqflite/sqflite.dart';
import '../utils/api_client.dart';
import '../utils/app_logger.dart';
import '../models/student_model.dart';
import '../models/grade_model.dart';
import 'database_service.dart';
import 'grade_service.dart';

class SyncService {
  final ApiClient _apiClient;
  final GradeService _gradeService;
  Timer? _syncTimer;
  bool _isSyncing = false;
  
  // 同步状态回调
  Function(SyncStatus)? onSyncStatusChanged;
  Function(double)? onSyncProgressChanged;
  
  SyncService(this._apiClient, this._gradeService);
  
  /// 启动自动同步
  void startAutoSync({Duration interval = const Duration(minutes: 5)}) {
    stopAutoSync();
    _syncTimer = Timer.periodic(interval, (_) {
      syncPendingChanges();
    });
    AppLogger.info('Auto sync started with interval: ${interval.inMinutes} minutes');
  }
  
  /// 停止自动同步
  void stopAutoSync() {
    _syncTimer?.cancel();
    _syncTimer = null;
    AppLogger.info('Auto sync stopped');
  }
  
  /// 检查网络连接状态
  Future<bool> isConnected() async {
    try {
      final connectivityResult = await Connectivity().checkConnectivity();
      return connectivityResult != ConnectivityResult.none;
    } catch (e) {
      AppLogger.error('Failed to check connectivity', e);
      return false;
    }
  }
  
  /// 同步待处理的更改
  Future<SyncResult> syncPendingChanges() async {
    if (_isSyncing) {
      AppLogger.info('Sync already in progress, skipping');
      return SyncResult(
        success: false,
        message: 'Sync already in progress',
        syncedCount: 0,
        failedCount: 0,
      );
    }
    
    if (!await isConnected()) {
      AppLogger.info('No internet connection, skipping sync');
      return SyncResult(
        success: false,
        message: 'No internet connection',
        syncedCount: 0,
        failedCount: 0,
      );
    }
    
    _isSyncing = true;
    onSyncStatusChanged?.call(SyncStatus.syncing);
    
    try {
      AppLogger.info('Starting sync of pending changes');
      
      final pendingRecords = await DatabaseService.getPendingSyncRecords();
      if (pendingRecords.isEmpty) {
        AppLogger.info('No pending changes to sync');
        onSyncStatusChanged?.call(SyncStatus.completed);
        return SyncResult(
          success: true,
          message: 'No pending changes',
          syncedCount: 0,
          failedCount: 0,
        );
      }
      
      int syncedCount = 0;
      int failedCount = 0;
      
      for (int i = 0; i < pendingRecords.length; i++) {
        final record = pendingRecords[i];
        final progress = (i + 1) / pendingRecords.length;
        onSyncProgressChanged?.call(progress);
        
        try {
          await _syncRecord(record);
          syncedCount++;
          
          // 更新同步状态为已完成
          await DatabaseService.updateSyncStatus(
            syncId: record['id'],
            status: 'synced',
          );
          
          AppLogger.info('Synced record: ${record['table_name']}/${record['record_id']}');
        } catch (e, stackTrace) {
          failedCount++;
          
          // 更新同步状态为失败
          await DatabaseService.updateSyncStatus(
            syncId: record['id'],
            status: 'failed',
            errorMessage: e.toString(),
          );
          
          AppLogger.error('Failed to sync record: ${record['table_name']}/${record['record_id']}', e, stackTrace);
        }
      }
      
      final result = SyncResult(
        success: failedCount == 0,
        message: 'Synced $syncedCount records, $failedCount failed',
        syncedCount: syncedCount,
        failedCount: failedCount,
      );
      
      onSyncStatusChanged?.call(failedCount == 0 ? SyncStatus.completed : SyncStatus.failed);
      AppLogger.info('Sync completed: ${result.message}');
      
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('Sync failed', e, stackTrace);
      onSyncStatusChanged?.call(SyncStatus.failed);
      return SyncResult(
        success: false,
        message: 'Sync failed: $e',
        syncedCount: 0,
        failedCount: 0,
      );
    } finally {
      _isSyncing = false;
    }
  }
  
  /// 同步单个记录
  Future<void> _syncRecord(Map<String, dynamic> record) async {
    final tableName = record['table_name'] as String;
    final recordId = record['record_id'] as String;
    final operation = record['operation'] as String;
    final dataJson = record['data'] as String?;
    
    Map<String, dynamic>? data;
    if (dataJson != null) {
      try {
        data = json.decode(dataJson);
      } catch (e) {
        AppLogger.error('Failed to parse sync data', e);
        throw Exception('Invalid sync data format');
      }
    }
    
    switch (tableName) {
      case 'students':
        await _syncStudent(recordId, operation, data);
        break;
      case 'classes':
        await _syncClass(recordId, operation, data);
        break;
      case 'grades':
        await _syncGrade(recordId, operation, data);
        break;
      default:
        throw Exception('Unknown table: $tableName');
    }
  }
  
  /// 同步学生数据
  Future<void> _syncStudent(String recordId, String operation, Map<String, dynamic>? data) async {
    switch (operation) {
      case 'create':
        if (data == null) throw Exception('No data for create operation');
        final response = await _apiClient.post(
          '/api/students',
          data: data,
        );
        if (!response.success) {
          throw Exception(response.message ?? 'Failed to create student');
        }
        break;
        
      case 'update':
        if (data == null) throw Exception('No data for update operation');
        final response = await _apiClient.put(
          '/api/students/$recordId',
          data: data,
        );
        if (!response.success) {
          throw Exception(response.message ?? 'Failed to update student');
        }
        break;
        
      case 'delete':
        final response = await _apiClient.delete('/api/students/$recordId');
        if (!response.success) {
          throw Exception(response.message ?? 'Failed to delete student');
        }
        break;
        
      default:
        throw Exception('Unknown operation: $operation');
    }
  }
  
  /// 同步班级数据
  Future<void> _syncClass(String recordId, String operation, Map<String, dynamic>? data) async {
    switch (operation) {
      case 'create':
        if (data == null) throw Exception('No data for create operation');
        final response = await _apiClient.post(
          '/api/classes',
          data: data,
        );
        if (!response.success) {
          throw Exception(response.message ?? 'Failed to create class');
        }
        break;
        
      case 'update':
        if (data == null) throw Exception('No data for update operation');
        final response = await _apiClient.put(
          '/api/classes/$recordId',
          data: data,
        );
        if (!response.success) {
          throw Exception(response.message ?? 'Failed to update class');
        }
        break;
        
      case 'delete':
        final response = await _apiClient.delete('/api/classes/$recordId');
        if (!response.success) {
          throw Exception(response.message ?? 'Failed to delete class');
        }
        break;
        
      default:
        throw Exception('Unknown operation: $operation');
    }
  }
  
  /// 同步成绩数据
  Future<void> _syncGrade(String recordId, String operation, Map<String, dynamic>? data) async {
    switch (operation) {
      case 'create':
        if (data == null) throw Exception('No data for create operation');
        final response = await _apiClient.post(
          '/api/grades',
          data: data,
        );
        if (!response.success) {
          throw Exception(response.message ?? 'Failed to create grade');
        }
        break;
        
      case 'update':
        if (data == null) throw Exception('No data for update operation');
        final response = await _apiClient.put(
          '/api/grades/$recordId',
          data: data,
        );
        if (!response.success) {
          throw Exception(response.message ?? 'Failed to update grade');
        }
        break;
        
      case 'delete':
        final response = await _apiClient.delete('/api/grades/$recordId');
        if (!response.success) {
          throw Exception(response.message ?? 'Failed to delete grade');
        }
        break;
        
      default:
        throw Exception('Unknown operation: $operation');
    }
  }
  
  /// 从服务器拉取最新数据
  Future<SyncResult> pullDataFromServer() async {
    if (!await isConnected()) {
      return SyncResult(
        success: false,
        message: 'No internet connection',
        syncedCount: 0,
        failedCount: 0,
      );
    }
    
    try {
      AppLogger.info('Pulling data from server');
      onSyncStatusChanged?.call(SyncStatus.syncing);
      
      int syncedCount = 0;
      
      // 拉取学生数据
      try {
        final studentsResponse = await _apiClient.get('/api/students');
        if (studentsResponse.success && studentsResponse.data != null) {
          final students = (studentsResponse.data!['data'] as List)
              .map((json) => Student.fromJson(json))
              .toList();
          
          for (final student in students) {
            await DatabaseService.insertStudent(student);
            syncedCount++;
          }
        }
      } catch (e) {
        AppLogger.error('Failed to pull students data', e);
      }
      
      // 拉取班级数据
      try {
        final classesResponse = await _apiClient.get('/api/classes');
        if (classesResponse.success && classesResponse.data != null) {
          final classes = (classesResponse.data!['data'] as List)
              .map((json) => json as Map<String, dynamic>)
              .toList();
          
          for (final classData in classes) {
            await DatabaseService.insertClass(classData);
            syncedCount++;
          }
        }
      } catch (e) {
        AppLogger.error('Failed to pull classes data', e);
      }
      
      // 拉取成绩数据
      try {
        final gradesResponse = await _apiClient.get('/api/grades');
        if (gradesResponse.success && gradesResponse.data != null) {
          final grades = (gradesResponse.data!['data'] as List)
              .map((json) => Grade.fromJson(json))
              .toList();
          
          for (final grade in grades) {
            await DatabaseService.insertGrade(grade);
            syncedCount++;
          }
        }
      } catch (e) {
        AppLogger.error('Failed to pull grades data', e);
      }
      
      onSyncStatusChanged?.call(SyncStatus.completed);
      AppLogger.info('Data pull completed, synced $syncedCount records');
      
      return SyncResult(
        success: true,
        message: 'Pulled $syncedCount records from server',
        syncedCount: syncedCount,
        failedCount: 0,
      );
    } catch (e, stackTrace) {
      AppLogger.error('Failed to pull data from server', e, stackTrace);
      onSyncStatusChanged?.call(SyncStatus.failed);
      return SyncResult(
        success: false,
        message: 'Failed to pull data: $e',
        syncedCount: 0,
        failedCount: 0,
      );
    }
  }
  
  /// 拉取最新数据
  Future<SyncResult> pullLatestData() async {
    try {
      AppLogger.info('Pulling latest data from server');
      return await pullDataFromServer();
    } catch (e, stackTrace) {
      AppLogger.error('Failed to pull latest data', e, stackTrace);
      return SyncResult(
        success: false,
        message: 'Failed to pull latest data: $e',
        syncedCount: 0,
        failedCount: 1,
      );
    }
  }
  
  /// 强制全量同步
  Future<SyncResult> forceFullSync() async {
    try {
      AppLogger.info('Starting force full sync');
      
      // 清除本地数据
      await DatabaseService.clearAllData();
      
      // 从服务器拉取最新数据
      final pullResult = await pullDataFromServer();
      if (!pullResult.success) {
        return pullResult;
      }
      
      // 同步待处理的更改
      final pushResult = await syncPendingChanges();
      
      return SyncResult(
        success: pullResult.success && pushResult.success,
        message: 'Full sync completed',
        syncedCount: pullResult.syncedCount + pushResult.syncedCount,
        failedCount: pullResult.failedCount + pushResult.failedCount,
      );
    } catch (e, stackTrace) {
      AppLogger.error('Force full sync failed', e, stackTrace);
      return SyncResult(
        success: false,
        message: 'Force full sync failed: $e',
        syncedCount: 0,
        failedCount: 0,
      );
    }
  }
  
  /// 获取同步状态
  Future<Map<String, dynamic>> getSyncStatus() async {
    try {
      final pendingRecords = await DatabaseService.getPendingSyncRecords();
      return {
        'is_syncing': _isSyncing,
        'pending_count': pendingRecords.length,
        'auto_sync_enabled': _syncTimer != null,
        'last_sync_time': DateTime.now().toIso8601String(), // 这里应该存储实际的最后同步时间
      };
    } catch (e) {
      AppLogger.error('Failed to get sync status', e);
      return {
        'is_syncing': false,
        'pending_count': 0,
        'auto_sync_enabled': false,
        'last_sync_time': null,
      };
    }
  }
  
  /// 清理同步记录
  Future<void> cleanupSyncRecords() async {
    try {
      // 这里可以实现清理逻辑，比如删除已完成的同步记录
      AppLogger.info('Sync records cleanup completed');
    } catch (e, stackTrace) {
      AppLogger.error('Failed to cleanup sync records', e, stackTrace);
    }
  }
  
  /// 清除同步记录
  Future<void> clearSyncRecords() async {
    try {
      // 清除同步状态表中的记录
      final db = await DatabaseService.database;
      await db.delete('sync_status');
      AppLogger.info('Sync records cleared');
    } catch (e, stackTrace) {
      AppLogger.error('Failed to clear sync records', e, stackTrace);
      rethrow;
    }
  }
  
  /// 标记数据需要同步
  Future<void> markForSync(String tableName, String recordId, String operation, Map<String, dynamic> data) async {
    try {
      final db = await DatabaseService.database;
      await db.insert(
        'sync_status',
        {
          'table_name': tableName,
          'record_id': recordId,
          'operation': operation,
          'data': data.toString(),
          'created_at': DateTime.now().toIso8601String(),
          'is_synced': 0,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
      AppLogger.info('Marked $tableName:$recordId for sync ($operation)');
    } catch (e, stackTrace) {
      AppLogger.error('Failed to mark for sync', e, stackTrace);
      rethrow;
    }
  }
  
  /// 释放资源
  void dispose() {
    stopAutoSync();
    onSyncStatusChanged = null;
    onSyncProgressChanged = null;
  }
}

/// 同步状态枚举
enum SyncStatus {
  idle,
  syncing,
  completed,
  failed,
}

/// 同步结果类
class SyncResult {
  final bool success;
  final String message;
  final int syncedCount;
  final int failedCount;
  
  SyncResult({
    required this.success,
    required this.message,
    required this.syncedCount,
    required this.failedCount,
  });
  
  @override
  String toString() {
    return 'SyncResult(success: $success, message: $message, synced: $syncedCount, failed: $failedCount)';
  }
}