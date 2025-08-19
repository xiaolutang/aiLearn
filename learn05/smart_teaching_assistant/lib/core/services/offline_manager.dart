import 'dart:async';
import '../utils/app_logger.dart';
import '../utils/api_client.dart';
import '../models/student_model.dart';
import 'database_service.dart';
import 'sync_service.dart';
import 'cache_service.dart';
import 'connectivity_service.dart';
import 'grade_service.dart';

class OfflineManager {
  static final OfflineManager _instance = OfflineManager._internal();
  factory OfflineManager() => _instance;
  OfflineManager._internal();
  
  /// 获取单例实例
  static OfflineManager get instance => _instance;

  // 服务实例
  DatabaseService? _databaseService;
  SyncService? _syncService;
  CacheService? _cacheService;
  ApiClient? _apiService;
  GradeService? _gradeService;
  
  // 初始化状态
  bool _isInitialized = false;
  
  // 离线模式状态
  bool _isOfflineMode = false;
  
  // 状态监听器
  final List<Function(bool)> _offlineModeListeners = [];
  
  /// 获取初始化状态
  bool get isInitialized => _isInitialized;
  
  /// 获取离线模式状态
  bool get isOfflineMode => _isOfflineMode;
  
  /// 获取数据库服务实例
  DatabaseService get databaseService {
    if (_databaseService == null) {
      throw Exception('OfflineManager not initialized. Call init() first.');
    }
    return _databaseService!;
  }
  
  /// 初始化离线管理器
  Future<void> init() async {
    if (_isInitialized) {
      AppLogger.warning('OfflineManager already initialized');
      return;
    }
    
    try {
      AppLogger.info('开始初始化离线管理器');
      
      // 初始化连接服务
      AppLogger.debug('初始化连接服务');
      await ConnectivityService.instance.init();
      AppLogger.debug('连接服务初始化完成');
      
      // 初始化API客户端
      AppLogger.debug('初始化API客户端');
      _apiService = ApiClient();
      _apiService!.initialize();
      AppLogger.debug('API客户端初始化完成');
      
      // 初始化成绩服务
      AppLogger.debug('初始化成绩服务');
      _gradeService = GradeService(_apiService!);
      AppLogger.debug('成绩服务初始化完成');
      
      // 初始化缓存服务
      AppLogger.debug('初始化缓存服务');
      await CacheService.init();
      _cacheService = CacheService();
      AppLogger.debug('缓存服务初始化完成');
      
      // 初始化数据库服务
      AppLogger.debug('初始化数据库服务');
      _databaseService = DatabaseService();
      AppLogger.debug('数据库服务初始化完成');
      
      // 初始化同步服务
      AppLogger.debug('初始化同步服务');
      _syncService = SyncService(_apiService!, _gradeService!);
      AppLogger.debug('同步服务初始化完成');
      
      // 监听网络状态变化
      AppLogger.debug('设置网络状态监听器');
      ConnectivityService.instance.addListener(_onNetworkStatusChanged);
      
      // 检查初始网络状态
      final isConnected = ConnectivityService.instance.isConnected;
      AppLogger.info('初始网络状态检查', {
        'isConnected': isConnected,
        'willSetOfflineMode': !isConnected,
      });
      _updateOfflineMode(!isConnected);
      
      _isInitialized = true;
      AppLogger.info('离线管理器初始化完成', {
        'isOfflineMode': _isOfflineMode,
        'isConnected': isConnected,
      });
    } catch (e, stackTrace) {
      AppLogger.error('离线管理器初始化失败', e, stackTrace);
      rethrow;
    }
  }
  
  /// 网络状态变化处理
  void _onNetworkStatusChanged(bool isConnected) {
    AppLogger.info('网络状态变化', {
      'isConnected': isConnected,
      'previousOfflineMode': _isOfflineMode,
      'newOfflineMode': !isConnected,
    });
    _updateOfflineMode(!isConnected);
    
    if (isConnected) {
      _handleBackOnline();
    }
  }
  
  /// 更新离线模式状态
  void _updateOfflineMode(bool isOffline) {
    if (_isOfflineMode != isOffline) {
      final previousMode = _isOfflineMode;
      _isOfflineMode = isOffline;
      
      AppLogger.info('离线模式状态变更', {
        'previousMode': previousMode ? '离线' : '在线',
        'newMode': isOffline ? '离线' : '在线',
        'listenerCount': _offlineModeListeners.length,
      });
      
      // 通知监听器
      for (int i = 0; i < _offlineModeListeners.length; i++) {
        try {
          _offlineModeListeners[i](_isOfflineMode);
          AppLogger.debug('离线模式监听器执行成功', {'listenerIndex': i});
        } catch (e, stackTrace) {
          AppLogger.error('离线模式状态监听器执行失败 - listenerIndex: $i', e, stackTrace);
        }
      }
      
      AppLogger.info('离线模式状态已更新: ${isOffline ? "离线" : "在线"}');
    } else {
      AppLogger.debug('离线模式状态无变化', {
        'currentMode': isOffline ? '离线' : '在线',
      });
    }
  }
  
  /// 处理重新上线
  Future<void> _handleBackOnline() async {
    try {
      AppLogger.info('Back online, starting sync process');
      
      // 启动自动同步
      _syncService?.startAutoSync();
      
      // 同步待处理的更改
      await _syncService?.syncPendingChanges();
      
      AppLogger.info('Online sync process completed');
    } catch (e, stackTrace) {
      AppLogger.error('Failed to handle back online', e, stackTrace);
    }
  }
  
  /// 添加离线模式监听器
  void addOfflineModeListener(Function(bool) listener) {
    _offlineModeListeners.add(listener);
  }
  
  /// 移除离线模式监听器
  void removeOfflineModeListener(Function(bool) listener) {
    _offlineModeListeners.remove(listener);
  }
  
  /// 获取学生数据（离线优先）
  Future<List<Map<String, dynamic>>> getStudents() async {
    try {
      AppLogger.info('OfflineManager: 开始获取学生数据', {
        'isOfflineMode': _isOfflineMode,
        'strategy': '离线优先'
      });
      
      // 首先尝试从缓存获取
      final cachedData = await CacheService.getOfflineData('students');
      if (cachedData != null && cachedData['items'] != null) {
        final cacheItems = List<Map<String, dynamic>>.from(cachedData['items']);
        AppLogger.info('OfflineManager: 从缓存获取学生数据成功', {
          'studentsCount': cacheItems.length,
          'dataSource': 'cache'
        });
        return cacheItems;
      }
      
      AppLogger.debug('OfflineManager: 缓存中无学生数据，尝试从数据库获取');
      
      // 尝试从数据库获取
      final students = await DatabaseService.getStudents();
      if (students.isNotEmpty) {
        final localData = students.map((student) => student.toJson()).toList();
        
        AppLogger.info('OfflineManager: 从数据库获取学生数据成功', {
          'studentsCount': localData.length,
          'dataSource': 'database'
        });
        
        // 更新缓存
        await CacheService.setOfflineData('students', {'items': localData});
        AppLogger.debug('OfflineManager: 已将数据库数据缓存');
        
        return localData;
      }
      
      AppLogger.debug('OfflineManager: 数据库中无学生数据');
      
      // 如果在线，尝试从网络获取
      if (!_isOfflineMode) {
        AppLogger.debug('OfflineManager: 在线模式，尝试从网络获取学生数据');
        return await _getStudentsFromNetwork();
      }
      
      AppLogger.warning('OfflineManager: 离线模式且无本地数据', {
        'isOfflineMode': _isOfflineMode,
        'cacheEmpty': cachedData == null,
        'databaseEmpty': students.isEmpty
      });
      return [];
    } catch (e, stackTrace) {
      AppLogger.error('OfflineManager: 获取学生数据失败', {
        'error': e.toString(),
        'stackTrace': stackTrace.toString(),
        'isOfflineMode': _isOfflineMode
      });
      return [];
    }
  }
  
  /// 从网络获取学生数据
  Future<List<Map<String, dynamic>>> _getStudentsFromNetwork() async {
    try {
      AppLogger.info('OfflineManager: 开始从网络获取学生数据');
      
      // 这里应该调用实际的API
      // final response = await _apiService!.get('/students');
      // final networkData = List<Map<String, dynamic>>.from(response.data);
      
      // 临时返回空数据
      final networkData = <Map<String, dynamic>>[];
      
      AppLogger.info('OfflineManager: 网络获取学生数据完成', {
        'studentsCount': networkData.length,
        'dataSource': 'network'
      });
      
      if (networkData.isNotEmpty) {
        AppLogger.debug('OfflineManager: 开始保存网络数据到本地数据库');
        
        // 保存到数据库
        int savedCount = 0;
        for (final studentData in networkData) {
          try {
            final student = Student.fromJson(studentData);
            await DatabaseService.insertStudent(student);
            savedCount++;
          } catch (e) {
            AppLogger.warning('OfflineManager: 保存学生数据失败', {
              'studentData': studentData,
              'error': e.toString()
            });
          }
        }
        
        AppLogger.info('OfflineManager: 网络数据保存到数据库完成', {
          'totalCount': networkData.length,
          'savedCount': savedCount,
          'failedCount': networkData.length - savedCount
        });
        
        // 缓存数据
        await CacheService.setOfflineData('students', {'items': networkData});
        AppLogger.debug('OfflineManager: 网络数据已缓存');
      }
      
      return networkData;
    } catch (e, stackTrace) {
      AppLogger.error('OfflineManager: 从网络获取学生数据失败', {
        'error': e.toString(),
        'stackTrace': stackTrace.toString()
      });
      rethrow;
    }
  }
  
  /// 创建学生（离线支持）
  Future<bool> createStudent(Map<String, dynamic> studentData) async {
    try {
      final studentName = studentData['name'] ?? '未知学生';
      AppLogger.info('OfflineManager: 开始创建学生', {
        'studentName': studentName,
        'isOfflineMode': _isOfflineMode,
        'inputData': studentData.keys.toList()
      });
      
      // 添加本地ID和时间戳
      final localData = Map<String, dynamic>.from(studentData);
      final localId = DateTime.now().millisecondsSinceEpoch.toString();
      final timestamp = DateTime.now().toIso8601String();
      
      localData['local_id'] = localId;
      localData['created_at'] = timestamp;
      localData['updated_at'] = timestamp;
      
      AppLogger.debug('OfflineManager: 准备本地数据', {
        'localId': localId,
        'timestamp': timestamp
      });
      
      // 保存到本地数据库
      final student = Student.fromJson(localData);
      await DatabaseService.insertStudent(student);
      
      AppLogger.debug('OfflineManager: 学生数据已保存到本地数据库');
      
      // 如果在线，尝试同步到服务器
      if (!_isOfflineMode) {
        try {
          AppLogger.debug('OfflineManager: 在线模式，尝试同步到服务器');
          // 这里应该调用实际的API服务
          AppLogger.debug('OfflineManager: 同步新学生到服务器 (占位符)');
          
          // 同步成功后，更新本地记录的服务器ID
          // await DatabaseService.updateStudent(localData['local_id'], {'server_id': serverResponse['id']});
        } catch (e) {
          AppLogger.warning('OfflineManager: 同步新学生到服务器失败，稍后重试', {
            'studentName': studentName,
            'localId': localId,
            'error': e.toString()
          });
          // 标记为待同步
          await _syncService?.markForSync('students', localId, 'create', localData);
        }
      } else {
        AppLogger.debug('OfflineManager: 离线模式，标记为待同步');
        // 离线模式，标记为待同步
        await _syncService?.markForSync('students', localId, 'create', localData);
      }
      
      // 清除相关缓存
      await CacheService.removeOfflineData('students');
      AppLogger.debug('OfflineManager: 已清除学生缓存数据');
      
      AppLogger.info('OfflineManager: 学生创建成功', {
        'studentName': studentName,
        'localId': localId,
        'isOfflineMode': _isOfflineMode
      });
      return true;
    } catch (e, stackTrace) {
      AppLogger.error('OfflineManager: 创建学生失败', {
        'error': e.toString(),
        'stackTrace': stackTrace.toString(),
        'studentData': studentData,
        'isOfflineMode': _isOfflineMode
      });
      return false;
    }
  }
  
  /// 更新学生（离线支持）
  Future<bool> updateStudent(String studentId, Map<String, dynamic> updateData) async {
    try {
      AppLogger.info('OfflineManager: 开始更新学生', {
        'studentId': studentId,
        'updateFields': updateData.keys.toList(),
        'isOfflineMode': _isOfflineMode
      });
      
      // 添加更新时间戳
      final localData = Map<String, dynamic>.from(updateData);
      final timestamp = DateTime.now().toIso8601String();
      localData['updated_at'] = timestamp;
      
      AppLogger.debug('OfflineManager: 准备更新数据', {
        'timestamp': timestamp,
        'updateFieldsCount': updateData.length
      });
      
      // 更新本地数据库
      await DatabaseService.updateStudent(studentId, localData);
      AppLogger.debug('OfflineManager: 学生数据已在本地数据库更新');
      
      // 如果在线，尝试同步到服务器
      if (!_isOfflineMode) {
        try {
          AppLogger.debug('OfflineManager: 在线模式，尝试同步更新到服务器');
          // 这里应该调用实际的API服务
          AppLogger.debug('OfflineManager: 同步更新学生到服务器 (占位符)');
        } catch (e) {
          AppLogger.warning('OfflineManager: 同步更新学生到服务器失败，稍后重试', {
            'studentId': studentId,
            'error': e.toString()
          });
          // 标记为待同步
          await _syncService?.markForSync('students', studentId, 'update', localData);
        }
      } else {
        AppLogger.debug('OfflineManager: 离线模式，标记为待同步');
        // 离线模式，标记为待同步
        await _syncService?.markForSync('students', studentId, 'update', localData);
      }
      
      // 清除相关缓存
      await CacheService.removeOfflineData('students');
      AppLogger.debug('OfflineManager: 已清除学生缓存数据');
      
      AppLogger.info('OfflineManager: 学生更新成功', {
        'studentId': studentId,
        'isOfflineMode': _isOfflineMode
      });
      return true;
    } catch (e, stackTrace) {
      AppLogger.error('OfflineManager: 更新学生失败', {
        'error': e.toString(),
        'stackTrace': stackTrace.toString(),
        'studentId': studentId,
        'updateData': updateData,
        'isOfflineMode': _isOfflineMode
      });
      return false;
    }
  }
  
  /// 删除学生（离线支持）
  Future<bool> deleteStudent(String studentId) async {
    try {
      AppLogger.info('OfflineManager: 开始删除学生', {
        'studentId': studentId,
        'isOfflineMode': _isOfflineMode
      });
      
      // 从本地数据库删除
      await DatabaseService.deleteStudent(studentId);
      AppLogger.debug('OfflineManager: 学生已从本地数据库删除');
      
      // 如果在线，尝试同步到服务器
      if (!_isOfflineMode) {
        try {
          AppLogger.debug('OfflineManager: 在线模式，尝试同步删除到服务器');
          // 这里应该调用实际的API服务
          AppLogger.debug('OfflineManager: 同步删除学生到服务器 (占位符)');
        } catch (e) {
          AppLogger.warning('OfflineManager: 同步删除学生到服务器失败，稍后重试', {
            'studentId': studentId,
            'error': e.toString()
          });
          // 标记为待同步
          await _syncService?.markForSync('students', studentId, 'delete', <String, dynamic>{});
        }
      } else {
        AppLogger.debug('OfflineManager: 离线模式，标记为待同步');
        // 离线模式，标记为待同步
        await _syncService?.markForSync('students', studentId, 'delete', <String, dynamic>{});
      }
      
      // 清除相关缓存
      await CacheService.removeOfflineData('students');
      AppLogger.debug('OfflineManager: 已清除学生缓存数据');
      
      AppLogger.info('OfflineManager: 学生删除成功', {
        'studentId': studentId,
        'isOfflineMode': _isOfflineMode
      });
      return true;
    } catch (e, stackTrace) {
      AppLogger.error('OfflineManager: 删除学生失败', {
        'error': e.toString(),
        'stackTrace': stackTrace.toString(),
        'studentId': studentId,
        'isOfflineMode': _isOfflineMode
      });
      return false;
    }
  }
  
  /// 强制同步所有数据
  Future<void> forceSync() async {
    try {
      AppLogger.info('OfflineManager: 开始强制同步所有数据', {
        'isOfflineMode': _isOfflineMode
      });
      
      if (_isOfflineMode) {
        AppLogger.error('OfflineManager: 无法在离线模式下进行同步', {
          'isOfflineMode': _isOfflineMode
        });
        throw Exception('Cannot sync while offline');
      }
      
      AppLogger.debug('OfflineManager: 调用同步服务进行完整同步');
      await _syncService?.forceFullSync();
      
      AppLogger.debug('OfflineManager: 清除所有缓存数据');
      // 清除所有缓存
      await CacheService.clear();
      
      AppLogger.info('OfflineManager: 强制同步完成');
    } catch (e, stackTrace) {
      AppLogger.error('OfflineManager: 强制同步失败', {
        'error': e.toString(),
        'stackTrace': stackTrace.toString(),
        'isOfflineMode': _isOfflineMode
      });
      rethrow;
    }
  }
  
  /// 获取离线数据统计
  Future<Map<String, dynamic>> getOfflineStats() async {
    try {
      AppLogger.debug('OfflineManager: 开始获取离线数据统计');
      
      final pendingSync = await DatabaseService.getPendingSyncRecords();
      final dbSize = await DatabaseService.getDatabaseSize();
      
      final stats = {
        'pending_sync_count': pendingSync.length,
        'database_size_bytes': dbSize,
        'is_offline_mode': _isOfflineMode,
        'last_sync_time': null, // 可以从同步服务获取
      };
      
      AppLogger.info('OfflineManager: 离线数据统计获取完成', {
        'pendingSyncCount': pendingSync.length,
        'databaseSizeBytes': dbSize,
        'isOfflineMode': _isOfflineMode
      });
      
      return stats;
    } catch (e, stackTrace) {
      AppLogger.error('OfflineManager: 获取离线数据统计失败', {
        'error': e.toString(),
        'stackTrace': stackTrace.toString()
      });
      return {};
    }
  }
  
  /// 清除所有离线数据
  Future<void> clearAllData() async {
    try {
      AppLogger.info('Clearing all offline data');
      
      await DatabaseService.clearAllData();
      await CacheService.clear();
      await _syncService?.clearSyncRecords();
      
      AppLogger.info('All offline data cleared');
    } catch (e, stackTrace) {
      AppLogger.error('Failed to clear all data', e, stackTrace);
      rethrow;
    }
  }
  
  /// 释放资源
  Future<void> dispose() async {
    try {
      AppLogger.info('Disposing OfflineManager');
      
      // 停止监听网络状态
      ConnectivityService.instance.removeListener(_onNetworkStatusChanged);
      
      // 停止同步服务
      _syncService?.stopAutoSync();
      
      // 释放数据库资源
      await DatabaseService.dispose();
      
      // 清空监听器
      _offlineModeListeners.clear();
      
      _isInitialized = false;
      AppLogger.info('OfflineManager disposed');
    } catch (e, stackTrace) {
      AppLogger.error('Failed to dispose OfflineManager', e, stackTrace);
    }
  }
}