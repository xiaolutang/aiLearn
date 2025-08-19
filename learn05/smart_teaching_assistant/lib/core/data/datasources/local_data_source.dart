import 'dart:convert';
import 'dart:io';
import 'package:path/path.dart' as path;
import 'package:shared_preferences/shared_preferences.dart';
import '../../utils/app_logger.dart';

/// 本地数据源抽象类
abstract class LocalDataSource {
  /// 获取缓存数据
  Future<T?> getCachedData<T>(String key);
  
  /// 缓存数据
  Future<void> cacheData<T>(String key, T data);
  
  /// 获取缓存信息（时间戳等）
  Future<Map<String, dynamic>?> getCacheInfo(String key);
  
  /// 清除指定缓存
  Future<void> clearCache(String key);
  
  /// 清除所有缓存
  Future<void> clearAllCache();
  
  /// 根据前缀清除缓存
  Future<void> clearCacheByPrefix(String prefix);
  
  /// 标记数据为待同步
  Future<void> markForSync<T>(String syncKey, T data);
  
  /// 清除同步标记
  Future<void> clearSyncMark(String syncKey);
  
  /// 获取待同步数据
  Future<List<Map<String, dynamic>>> getPendingSyncData();
  
  /// 获取默认数据
  Future<T?> getDefaultData<T>(String key);
}

/// 本地数据源实现类
class LocalDataSourceImpl implements LocalDataSource {
  static const String _cachePrefix = 'cache_';
  static const String _cacheInfoPrefix = 'cache_info_';
  static const String _syncPrefix = 'sync_';
  static const String _defaultDataPath = 'assets/data/default';
  
  late SharedPreferences _prefs;
  late String _documentsPath;
  
  /// 初始化
  Future<void> initialize() async {
    try {
      _prefs = await SharedPreferences.getInstance();
      
      // 获取文档目录路径
      final directory = Directory.systemTemp; // 在实际应用中应使用 path_provider
      _documentsPath = directory.path;
      
      AppLogger.info('LocalDataSource: 初始化完成', {
        'documentsPath': _documentsPath,
      });
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 初始化失败', e, stackTrace);
      rethrow;
    }
  }

  @override
  Future<T?> getCachedData<T>(String key) async {
    try {
      final cacheKey = _cachePrefix + key;
      final jsonString = _prefs.getString(cacheKey);
      
      if (jsonString != null) {
        final data = jsonDecode(jsonString);
        AppLogger.debug('LocalDataSource: 获取缓存数据成功', {
          'key': key,
          'dataType': T.toString(),
        });
        return data as T;
      }
      
      AppLogger.debug('LocalDataSource: 缓存数据不存在', {'key': key});
      return null;
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 获取缓存数据失败', e, stackTrace);
      return null;
    }
  }

  @override
  Future<void> cacheData<T>(String key, T data) async {
    try {
      final cacheKey = _cachePrefix + key;
      final cacheInfoKey = _cacheInfoPrefix + key;
      
      // 保存数据
      final jsonString = jsonEncode(data);
      await _prefs.setString(cacheKey, jsonString);
      
      // 保存缓存信息
      final cacheInfo = {
        'timestamp': DateTime.now().toIso8601String(),
        'dataType': T.toString(),
        'size': jsonString.length,
      };
      await _prefs.setString(cacheInfoKey, jsonEncode(cacheInfo));
      
      AppLogger.debug('LocalDataSource: 缓存数据成功', {
        'key': key,
        'dataType': T.toString(),
        'size': jsonString.length,
      });
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 缓存数据失败', e, stackTrace);
      rethrow;
    }
  }

  @override
  Future<Map<String, dynamic>?> getCacheInfo(String key) async {
    try {
      final cacheInfoKey = _cacheInfoPrefix + key;
      final jsonString = _prefs.getString(cacheInfoKey);
      
      if (jsonString != null) {
        return jsonDecode(jsonString) as Map<String, dynamic>;
      }
      
      return null;
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 获取缓存信息失败', e, stackTrace);
      return null;
    }
  }

  @override
  Future<void> clearCache(String key) async {
    try {
      final cacheKey = _cachePrefix + key;
      final cacheInfoKey = _cacheInfoPrefix + key;
      
      await _prefs.remove(cacheKey);
      await _prefs.remove(cacheInfoKey);
      
      AppLogger.debug('LocalDataSource: 清除缓存成功', {'key': key});
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 清除缓存失败', e, stackTrace);
      rethrow;
    }
  }

  @override
  Future<void> clearAllCache() async {
    try {
      final keys = _prefs.getKeys();
      final cacheKeys = keys.where((key) => 
          key.startsWith(_cachePrefix) || key.startsWith(_cacheInfoPrefix));
      
      for (final key in cacheKeys) {
        await _prefs.remove(key);
      }
      
      AppLogger.info('LocalDataSource: 清除所有缓存成功', {
        'clearedCount': cacheKeys.length,
      });
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 清除所有缓存失败', e, stackTrace);
      rethrow;
    }
  }

  @override
  Future<void> clearCacheByPrefix(String prefix) async {
    try {
      final keys = _prefs.getKeys();
      final targetKeys = keys.where((key) => 
          (key.startsWith(_cachePrefix + prefix) || key.startsWith(_cacheInfoPrefix + prefix)));
      
      for (final key in targetKeys) {
        await _prefs.remove(key);
      }
      
      AppLogger.info('LocalDataSource: 清除前缀缓存成功', {
        'prefix': prefix,
        'clearedCount': targetKeys.length,
      });
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 清除前缀缓存失败', e, stackTrace);
      rethrow;
    }
  }

  @override
  Future<void> markForSync<T>(String syncKey, T data) async {
    try {
      final key = _syncPrefix + syncKey;
      final syncData = {
        'syncKey': syncKey,
        'data': data,
        'dataType': T.toString(),
        'timestamp': DateTime.now().toIso8601String(),
        'retryCount': 0,
      };
      
      await _prefs.setString(key, jsonEncode(syncData));
      
      AppLogger.debug('LocalDataSource: 标记数据为待同步', {
        'syncKey': syncKey,
        'dataType': T.toString(),
      });
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 标记同步数据失败', e, stackTrace);
      rethrow;
    }
  }

  @override
  Future<void> clearSyncMark(String syncKey) async {
    try {
      final key = _syncPrefix + syncKey;
      await _prefs.remove(key);
      
      AppLogger.debug('LocalDataSource: 清除同步标记成功', {'syncKey': syncKey});
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 清除同步标记失败', e, stackTrace);
      rethrow;
    }
  }

  @override
  Future<List<Map<String, dynamic>>> getPendingSyncData() async {
    try {
      final keys = _prefs.getKeys();
      final syncKeys = keys.where((key) => key.startsWith(_syncPrefix));
      
      final pendingData = <Map<String, dynamic>>[];
      
      for (final key in syncKeys) {
        final jsonString = _prefs.getString(key);
        if (jsonString != null) {
          final data = jsonDecode(jsonString) as Map<String, dynamic>;
          pendingData.add(data);
        }
      }
      
      AppLogger.debug('LocalDataSource: 获取待同步数据', {
        'count': pendingData.length,
      });
      
      return pendingData;
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 获取待同步数据失败', e, stackTrace);
      return [];
    }
  }

  @override
  Future<T?> getDefaultData<T>(String key) async {
    try {
      // 尝试从assets加载默认数据
      final filePath = path.join(_defaultDataPath, '$key.json');
      
      // 在实际应用中，这里应该使用 rootBundle.loadString
      // 现在先返回模拟数据
      final defaultData = await _getDefaultDataFromAssets<T>(key);
      
      if (defaultData != null) {
        AppLogger.debug('LocalDataSource: 获取默认数据成功', {
          'key': key,
          'dataType': T.toString(),
        });
        return defaultData;
      }
      
      AppLogger.warning('LocalDataSource: 默认数据不存在', {'key': key});
      return null;
    } catch (e, stackTrace) {
      AppLogger.error('LocalDataSource: 获取默认数据失败', e, stackTrace);
      return null;
    }
  }

  /// 从assets获取默认数据（模拟实现）
  Future<T?> _getDefaultDataFromAssets<T>(String key) async {
    try {
      // 这里应该根据具体的数据类型返回默认数据
      // 在实际应用中，应该从assets/data/default/目录加载JSON文件
      
      switch (key) {
        case 'classes':
          return _getDefaultClasses() as T?;
        case 'subjects':
          return _getDefaultSubjects() as T?;
        case 'students':
          return _getDefaultStudents() as T?;
        case 'grades':
          return _getDefaultGrades() as T?;
        default:
          return null;
      }
    } catch (e) {
      AppLogger.warning('LocalDataSource: 获取默认数据异常', {
        'key': key,
        'error': e.toString(),
      });
      return null;
    }
  }

  /// 获取默认班级数据
  List<Map<String, dynamic>> _getDefaultClasses() {
    return [
      {
        'id': 'class_001',
        'name': '高一(1)班',
        'grade': '高一',
        'teacher_id': 'teacher_001',
        'teacher_name': '张老师',
        'student_count': 45,
        'subjects': ['语文', '数学', '英语', '物理', '化学', '生物'],
        'created_at': '2024-01-01T00:00:00Z',
      },
      {
        'id': 'class_002',
        'name': '高一(2)班',
        'grade': '高一',
        'teacher_id': 'teacher_002',
        'teacher_name': '李老师',
        'student_count': 43,
        'subjects': ['语文', '数学', '英语', '物理', '化学', '生物'],
        'created_at': '2024-01-01T00:00:00Z',
      },
    ];
  }

  /// 获取默认科目数据
  List<Map<String, dynamic>> _getDefaultSubjects() {
    return [
      {'id': 'subject_001', 'name': '语文', 'code': 'chinese'},
      {'id': 'subject_002', 'name': '数学', 'code': 'math'},
      {'id': 'subject_003', 'name': '英语', 'code': 'english'},
      {'id': 'subject_004', 'name': '物理', 'code': 'physics'},
      {'id': 'subject_005', 'name': '化学', 'code': 'chemistry'},
      {'id': 'subject_006', 'name': '生物', 'code': 'biology'},
    ];
  }

  /// 获取默认学生数据
  List<Map<String, dynamic>> _getDefaultStudents() {
    return [
      {
        'id': 'student_001',
        'name': '张三',
        'class_id': 'class_001',
        'student_number': '2024001',
        'gender': '男',
        'created_at': '2024-01-01T00:00:00Z',
      },
      {
        'id': 'student_002',
        'name': '李四',
        'class_id': 'class_001',
        'student_number': '2024002',
        'gender': '女',
        'created_at': '2024-01-01T00:00:00Z',
      },
    ];
  }

  /// 获取默认成绩数据
  List<Map<String, dynamic>> _getDefaultGrades() {
    return [
      {
        'id': 'grade_001',
        'student_id': 'student_001',
        'subject_id': 'subject_002',
        'score': 85.5,
        'exam_type': '期中考试',
        'exam_date': '2024-01-15T00:00:00Z',
        'created_at': '2024-01-16T00:00:00Z',
      },
      {
        'id': 'grade_002',
        'student_id': 'student_002',
        'subject_id': 'subject_002',
        'score': 92.0,
        'exam_type': '期中考试',
        'exam_date': '2024-01-15T00:00:00Z',
        'created_at': '2024-01-16T00:00:00Z',
      },
    ];
  }

  /// 获取缓存统计信息
  Future<Map<String, dynamic>> getCacheStats() async {
    try {
      final keys = _prefs.getKeys();
      final cacheKeys = keys.where((key) => key.startsWith(_cachePrefix));
      final syncKeys = keys.where((key) => key.startsWith(_syncPrefix));
      
      int totalSize = 0;
      for (final key in cacheKeys) {
        final data = _prefs.getString(key);
        if (data != null) {
          totalSize += data.length;
        }
      }
      
      return {
        'cacheCount': cacheKeys.length,
        'syncCount': syncKeys.length,
        'totalSize': totalSize,
        'totalSizeFormatted': _formatBytes(totalSize),
      };
    } catch (e) {
      AppLogger.error('LocalDataSource: 获取缓存统计失败', e, null);
      return {
        'cacheCount': 0,
        'syncCount': 0,
        'totalSize': 0,
        'totalSizeFormatted': '0 B',
      };
    }
  }

  /// 格式化字节数
  String _formatBytes(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024) return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
  }
}