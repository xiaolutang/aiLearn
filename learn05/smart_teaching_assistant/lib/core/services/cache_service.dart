import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

class CacheService {
  static SharedPreferences? _prefs;
  static const String _keyPrefix = 'smart_teaching_';
  
  // 缓存键名常量
  static const String _userProfileKey = '${_keyPrefix}user_profile';
  static const String _appSettingsKey = '${_keyPrefix}app_settings';
  static const String _recentSearchesKey = '${_keyPrefix}recent_searches';
  static const String _offlineDataKey = '${_keyPrefix}offline_data';
  static const String _cacheMetadataKey = '${_keyPrefix}cache_metadata';
  
  /// 初始化缓存服务
  static Future<void> init() async {
    try {
      AppLogger.debug('缓存服务初始化开始');
      _prefs = await SharedPreferences.getInstance();
      AppLogger.info('缓存服务初始化成功');
    } catch (e, stackTrace) {
      AppLogger.error('缓存服务初始化失败 [${e.runtimeType}]', e, stackTrace);
      rethrow;
    }
  }
  
  /// 获取SharedPreferences实例
  static SharedPreferences get _preferences {
    if (_prefs == null) {
      throw Exception('Cache service not initialized. Call CacheService.init() first.');
    }
    return _prefs!;
  }
  
  // ==================== 基础缓存操作 ====================
  
  /// 存储字符串
  static Future<bool> setString(String key, String value) async {
    try {
      AppLogger.debug('存储字符串缓存开始: $key', {
        'valueLength': value.length,
        'fullKey': _keyPrefix + key,
      });
      
      final result = await _preferences.setString(_keyPrefix + key, value);
      
      AppLogger.debug('字符串缓存存储${result ? "成功" : "失败"}: $key');
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('存储字符串缓存失败 [${e.runtimeType}] Key: $key, ValueLength: ${value.length}', e, stackTrace);
      return false;
    }
  }
  
  /// 获取字符串
  static String? getString(String key) {
    try {
      AppLogger.debug('获取字符串缓存: $key');
      final value = _preferences.getString(_keyPrefix + key);
      AppLogger.debug('字符串缓存获取${value != null ? "成功" : "失败"}: $key', {
        'hasValue': value != null,
        'valueLength': value?.length,
      });
      return value;
    } catch (e, stackTrace) {
      AppLogger.error('获取字符串缓存失败 [${e.runtimeType}] Key: $key', e, stackTrace);
      return null;
    }
  }
  
  /// 存储整数
  static Future<bool> setInt(String key, int value) async {
    try {
      AppLogger.debug('存储整数缓存: $key = $value');
      final result = await _preferences.setInt(_keyPrefix + key, value);
      AppLogger.debug('整数缓存存储${result ? "成功" : "失败"}: $key = $value');
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('存储整数缓存失败 [${e.runtimeType}] Key: $key, Value: $value', e, stackTrace);
      return false;
    }
  }
  
  /// 获取整数
  static int? getInt(String key) {
    try {
      AppLogger.debug('获取整数缓存: $key');
      final value = _preferences.getInt(_keyPrefix + key);
      AppLogger.debug('整数缓存获取${value != null ? "成功" : "失败"}: $key = $value');
      return value;
    } catch (e, stackTrace) {
      AppLogger.error('获取整数缓存失败 [${e.runtimeType}] Key: $key', e, stackTrace);
      return null;
    }
  }
  
  /// 存储布尔值
  static Future<bool> setBool(String key, bool value) async {
    try {
      AppLogger.debug('存储布尔缓存: $key = $value');
      final result = await _preferences.setBool(_keyPrefix + key, value);
      AppLogger.debug('布尔缓存存储${result ? "成功" : "失败"}: $key = $value');
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('存储布尔缓存失败 [${e.runtimeType}] Key: $key, Value: $value', e, stackTrace);
      return false;
    }
  }
  
  /// 获取布尔值
  static bool? getBool(String key) {
    try {
      AppLogger.debug('获取布尔缓存: $key');
      final value = _preferences.getBool(_keyPrefix + key);
      AppLogger.debug('布尔缓存获取${value != null ? "成功" : "失败"}: $key = $value');
      return value;
    } catch (e, stackTrace) {
      AppLogger.error('获取布尔缓存失败 [${e.runtimeType}] Key: $key', e, stackTrace);
      return null;
    }
  }
  
  /// 存储双精度浮点数
  static Future<bool> setDouble(String key, double value) async {
    try {
      AppLogger.debug('存储浮点数缓存: $key = $value');
      final result = await _preferences.setDouble(_keyPrefix + key, value);
      AppLogger.debug('浮点数缓存存储${result ? "成功" : "失败"}: $key = $value');
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('存储浮点数缓存失败 [${e.runtimeType}] Key: $key, Value: $value', e, stackTrace);
      return false;
    }
  }
  
  /// 获取双精度浮点数
  static double? getDouble(String key) {
    try {
      AppLogger.debug('获取浮点数缓存: $key');
      final value = _preferences.getDouble(_keyPrefix + key);
      AppLogger.debug('浮点数缓存获取${value != null ? "成功" : "失败"}: $key = $value');
      return value;
    } catch (e, stackTrace) {
      AppLogger.error('获取浮点数缓存失败 [${e.runtimeType}] Key: $key', e, stackTrace);
      return null;
    }
  }
  
  /// 存储字符串列表
  static Future<bool> setStringList(String key, List<String> value) async {
    try {
      AppLogger.debug('存储字符串列表缓存: $key', {
        'itemCount': value.length,
        'totalLength': value.join('').length,
      });
      
      final result = await _preferences.setStringList(_keyPrefix + key, value);
      
      AppLogger.debug('字符串列表缓存存储${result ? "成功" : "失败"}: $key (${value.length} 项)');
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('存储字符串列表缓存失败 [${e.runtimeType}] Key: $key, ItemCount: ${value.length}', e, stackTrace);
      return false;
    }
  }
  
  /// 获取字符串列表
  static List<String>? getStringList(String key) {
    try {
      AppLogger.debug('获取字符串列表缓存: $key');
      final value = _preferences.getStringList(_keyPrefix + key);
      
      AppLogger.debug('字符串列表缓存获取${value != null ? "成功" : "失败"}: $key', {
        'hasValue': value != null,
        'itemCount': value?.length,
      });
      
      return value;
    } catch (e, stackTrace) {
      AppLogger.error('获取字符串列表缓存失败 [${e.runtimeType}] Key: $key', e, stackTrace);
      return null;
    }
  }
  
  /// 存储JSON对象
  static Future<bool> setJson(String key, Map<String, dynamic> value) async {
    try {
      AppLogger.debug('存储JSON缓存: $key', {
        'keyCount': value.keys.length,
        'hasNestedObjects': value.values.any((v) => v is Map || v is List),
      });
      
      final jsonString = json.encode(value);
      final result = await setString(key, jsonString);
      
      AppLogger.debug('JSON缓存存储${result ? "成功" : "失败"}: $key (${jsonString.length} 字符)');
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('存储JSON缓存失败 [${e.runtimeType}] Key: $key, KeyCount: ${value.keys.length}', e, stackTrace);
      return false;
    }
  }
  
  /// 获取JSON对象
  static Map<String, dynamic>? getJson(String key) {
    try {
      AppLogger.debug('获取JSON缓存: $key');
      final jsonString = getString(key);
      
      if (jsonString == null) {
        AppLogger.debug('JSON缓存不存在: $key');
        return null;
      }
      
      final value = json.decode(jsonString) as Map<String, dynamic>;
      AppLogger.debug('JSON缓存获取成功: $key', {
        'keyCount': value.keys.length,
        'jsonLength': jsonString.length,
      });
      
      return value;
    } catch (e, stackTrace) {
      AppLogger.error('获取JSON缓存失败 [${e.runtimeType}] Key: $key', e, stackTrace);
      return null;
    }
  }
  
  /// 删除缓存项
  static Future<bool> remove(String key) async {
    try {
      AppLogger.debug('删除缓存项: $key');
      final result = await _preferences.remove(_keyPrefix + key);
      
      AppLogger.debug('缓存项删除${result ? "成功" : "失败"}: $key');
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('删除缓存项失败 [${e.runtimeType}] Key: $key', e, stackTrace);
      return false;
    }
  }
  
  /// 检查缓存项是否存在
  static bool containsKey(String key) {
    try {
      AppLogger.debug('检查缓存项是否存在: $key');
      final exists = _preferences.containsKey(_keyPrefix + key);
      
      AppLogger.debug('缓存项${exists ? "存在" : "不存在"}: $key');
      return exists;
    } catch (e, stackTrace) {
      AppLogger.error('检查缓存项失败 [${e.runtimeType}] Key: $key', e, stackTrace);
      return false;
    }
  }
  
  /// 清除所有缓存
  static Future<bool> clear() async {
    try {
      AppLogger.debug('开始清除所有缓存');
      
      final keys = _preferences.getKeys()
          .where((key) => key.startsWith(_keyPrefix))
          .toList();
      
      AppLogger.debug('找到 ${keys.length} 个缓存项需要清除');
      
      for (final key in keys) {
        await _preferences.remove(key);
      }
      
      AppLogger.info('所有缓存清除成功 (${keys.length} 项)');
      return true;
    } catch (e, stackTrace) {
      AppLogger.error('清除所有缓存失败 [${e.runtimeType}]', e, stackTrace);
      return false;
    }
  }
  
  // ==================== 业务相关缓存操作 ====================
  
  /// 缓存用户配置信息
  static Future<bool> setUserProfile(Map<String, dynamic> profile) async {
    return await setJson('user_profile', profile);
  }
  
  /// 获取用户配置信息
  static Map<String, dynamic>? getUserProfile() {
    return getJson('user_profile');
  }
  
  /// 缓存应用设置
  static Future<bool> setAppSettings(Map<String, dynamic> settings) async {
    return await setJson('app_settings', settings);
  }
  
  /// 获取应用设置
  static Map<String, dynamic>? getAppSettings() {
    return getJson('app_settings');
  }
  
  /// 缓存最近搜索记录
  static Future<bool> addRecentSearch(String searchTerm) async {
    try {
      AppLogger.debug('添加最近搜索记录: $searchTerm');
      
      final recentSearches = getStringList('recent_searches') ?? [];
      final originalCount = recentSearches.length;
      
      // 移除重复项
      recentSearches.remove(searchTerm);
      
      // 添加到开头
      recentSearches.insert(0, searchTerm);
      
      // 限制数量（最多保存20条）
      if (recentSearches.length > 20) {
        recentSearches.removeRange(20, recentSearches.length);
      }
      
      final result = await setStringList('recent_searches', recentSearches);
      
      AppLogger.debug('最近搜索记录${result ? "添加成功" : "添加失败"}: $searchTerm', {
        'originalCount': originalCount,
        'newCount': recentSearches.length,
      });
      
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('添加最近搜索记录失败 [${e.runtimeType}] SearchTerm: $searchTerm', e, stackTrace);
      return false;
    }
  }
  
  /// 获取最近搜索记录
  static List<String> getRecentSearches() {
    return getStringList('recent_searches') ?? [];
  }
  
  /// 清除最近搜索记录
  static Future<bool> clearRecentSearches() async {
    return await remove('recent_searches');
  }
  
  /// 缓存离线数据
  static Future<bool> setOfflineData(String dataType, Map<String, dynamic> data) async {
    try {
      AppLogger.debug('缓存离线数据: $dataType', {
        'dataKeyCount': data.keys.length,
        'timestamp': DateTime.now().toIso8601String(),
      });
      
      final offlineData = getJson('offline_data') ?? <String, dynamic>{};
      offlineData[dataType] = {
        'data': data,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };
      
      final result = await setJson('offline_data', offlineData);
      
      AppLogger.debug('离线数据缓存${result ? "成功" : "失败"}: $dataType (${data.keys.length} 个键)');
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('缓存离线数据失败 [${e.runtimeType}] DataType: $dataType, KeyCount: ${data.keys.length}', e, stackTrace);
      return false;
    }
  }
  
  /// 获取离线数据
  static Map<String, dynamic>? getOfflineData(String dataType, {Duration? maxAge}) {
    try {
      AppLogger.debug('获取离线数据: $dataType', {
        'hasMaxAge': maxAge != null,
        'maxAgeMinutes': maxAge?.inMinutes,
      });
      
      final offlineData = getJson('offline_data');
      if (offlineData == null || !offlineData.containsKey(dataType)) {
        AppLogger.debug('离线数据不存在: $dataType');
        return null;
      }
      
      final cachedItem = offlineData[dataType] as Map<String, dynamic>;
      final timestamp = cachedItem['timestamp'] as int;
      final data = cachedItem['data'] as Map<String, dynamic>;
      
      // 检查数据是否过期
      if (maxAge != null) {
        final cacheTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
        final now = DateTime.now();
        final age = now.difference(cacheTime);
        
        if (age > maxAge) {
          AppLogger.debug('离线数据已过期: $dataType', {
            'ageMinutes': age.inMinutes,
            'maxAgeMinutes': maxAge.inMinutes,
          });
          return null;
        }
      }
      
      AppLogger.debug('离线数据获取成功: $dataType', {
        'dataKeyCount': data.keys.length,
        'ageMinutes': DateTime.now().difference(DateTime.fromMillisecondsSinceEpoch(timestamp)).inMinutes,
      });
      
      return data;
    } catch (e, stackTrace) {
      AppLogger.error('获取离线数据失败 [${e.runtimeType}] DataType: $dataType', e, stackTrace);
      return null;
    }
  }
  
  /// 移除离线数据
  static Future<bool> removeOfflineData(String dataType) async {
    try {
      AppLogger.debug('移除离线数据: $dataType');
      
      final offlineData = getJson('offline_data') ?? <String, dynamic>{};
      final hadData = offlineData.containsKey(dataType);
      
      offlineData.remove(dataType);
      final result = await setJson('offline_data', offlineData);
      
      AppLogger.debug('离线数据移除${result ? "成功" : "失败"}: $dataType', {
        'hadData': hadData,
        'remainingCount': offlineData.keys.length,
      });
      
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('移除离线数据失败 [${e.runtimeType}] DataType: $dataType', e, stackTrace);
      return false;
    }
  }
  
  /// 获取缓存大小信息
  static Map<String, dynamic> getCacheInfo() {
    try {
      AppLogger.debug('开始获取缓存大小信息');
      
      final keys = _preferences.getKeys()
          .where((key) => key.startsWith(_keyPrefix))
          .toList();
      
      AppLogger.debug('找到 ${keys.length} 个缓存项');
      
      int totalSize = 0;
      final categories = <String, int>{};
      
      for (final key in keys) {
        final value = _preferences.get(key);
        int size = 0;
        
        if (value is String) {
          size = value.length;
        } else if (value is List<String>) {
          size = value.join().length;
        } else {
          size = value.toString().length;
        }
        
        totalSize += size;
        
        // 按类别统计
        final category = key.replaceFirst(_keyPrefix, '').split('_').first;
        categories[category] = (categories[category] ?? 0) + size;
      }
      
      final result = {
        'total_items': keys.length,
        'total_size_bytes': totalSize,
        'categories': categories,
        'last_updated': DateTime.now().toIso8601String(),
      };
      
      AppLogger.debug('缓存信息获取成功', {
        'totalItems': keys.length,
        'totalSizeKB': (totalSize / 1024).round(),
        'categoryCount': categories.keys.length,
      });
      
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('获取缓存信息失败 [${e.runtimeType}]', e, stackTrace);
      return {
        'total_items': 0,
        'total_size_bytes': 0,
        'categories': <String, int>{},
        'last_updated': DateTime.now().toIso8601String(),
      };
    }
  }
  
  /// 清理过期缓存
  static Future<int> cleanupExpiredCache({Duration maxAge = const Duration(days: 7)}) async {
    try {
      AppLogger.debug('开始清理过期缓存', {
        'maxAgeDays': maxAge.inDays,
        'maxAgeHours': maxAge.inHours,
      });
      
      int cleanedCount = 0;
      final offlineData = getJson('offline_data') ?? <String, dynamic>{};
      final now = DateTime.now();
      
      AppLogger.debug('检查 ${offlineData.keys.length} 个离线数据项');
      
      final keysToRemove = <String>[];
      
      for (final entry in offlineData.entries) {
        final cachedItem = entry.value as Map<String, dynamic>;
        final timestamp = cachedItem['timestamp'] as int;
        final cacheTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
        final age = now.difference(cacheTime);
        
        if (age > maxAge) {
          keysToRemove.add(entry.key);
          AppLogger.debug('发现过期缓存项: ${entry.key}', {
            'ageHours': age.inHours,
            'maxAgeHours': maxAge.inHours,
          });
        }
      }
      
      for (final key in keysToRemove) {
        offlineData.remove(key);
        cleanedCount++;
      }
      
      if (cleanedCount > 0) {
        await setJson('offline_data', offlineData);
        AppLogger.info('过期缓存清理完成: $cleanedCount 项', {
          'remainingItems': offlineData.keys.length,
        });
      } else {
        AppLogger.debug('没有发现过期缓存项');
      }
      
      return cleanedCount;
    } catch (e, stackTrace) {
      AppLogger.error('清理过期缓存失败 [${e.runtimeType}] MaxAge: ${maxAge.inDays} 天', e, stackTrace);
      return 0;
    }
  }
  
  /// 预加载常用数据
  static Future<void> preloadCommonData() async {
    try {
      AppLogger.info('开始预加载常用数据到缓存');
      
      // 这里可以预加载一些常用的数据，比如：
      // - 用户偏好设置
      // - 常用的班级列表
      // - 科目信息等
      
      // 示例：预加载默认设置
      final defaultSettings = {
        'theme': 'light',
        'language': 'zh_CN',
        'auto_sync': true,
        'notification_enabled': true,
      };
      
      if (getAppSettings() == null) {
        AppLogger.debug('应用设置不存在，预加载默认设置');
        await setAppSettings(defaultSettings);
        AppLogger.debug('默认应用设置预加载完成');
      } else {
        AppLogger.debug('应用设置已存在，跳过预加载');
      }
      
      AppLogger.info('常用数据预加载成功完成');
    } catch (e, stackTrace) {
      AppLogger.error('预加载常用数据失败 [${e.runtimeType}]', e, stackTrace);
    }
  }
}