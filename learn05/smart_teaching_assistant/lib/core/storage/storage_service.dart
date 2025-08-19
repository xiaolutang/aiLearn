import 'package:shared_preferences/shared_preferences.dart';

/// 本地存储服务接口
abstract class StorageService {
  /// 存储字符串
  Future<bool> setString(String key, String value);
  
  /// 获取字符串
  Future<String?> getString(String key);
  
  /// 存储整数
  Future<bool> setInt(String key, int value);
  
  /// 获取整数
  Future<int?> getInt(String key);
  
  /// 存储布尔值
  Future<bool> setBool(String key, bool value);
  
  /// 获取布尔值
  Future<bool?> getBool(String key);
  
  /// 存储双精度浮点数
  Future<bool> setDouble(String key, double value);
  
  /// 获取双精度浮点数
  Future<double?> getDouble(String key);
  
  /// 存储字符串列表
  Future<bool> setStringList(String key, List<String> value);
  
  /// 获取字符串列表
  Future<List<String>?> getStringList(String key);
  
  /// 删除指定键的数据
  Future<bool> remove(String key);
  
  /// 清除所有数据
  Future<bool> clear();
  
  /// 检查是否包含指定键
  Future<bool> containsKey(String key);
  
  /// 获取所有键
  Future<Set<String>> getKeys();
}

/// SharedPreferences实现的存储服务
class SharedPreferencesStorageService implements StorageService {
  SharedPreferences? _prefs;
  
  /// 初始化SharedPreferences
  Future<void> init() async {
    _prefs ??= await SharedPreferences.getInstance();
  }
  
  /// 确保SharedPreferences已初始化
  Future<SharedPreferences> get _preferences async {
    if (_prefs == null) {
      await init();
    }
    return _prefs!;
  }

  @override
  Future<bool> setString(String key, String value) async {
    final prefs = await _preferences;
    return await prefs.setString(key, value);
  }

  @override
  Future<String?> getString(String key) async {
    final prefs = await _preferences;
    return prefs.getString(key);
  }

  @override
  Future<bool> setInt(String key, int value) async {
    final prefs = await _preferences;
    return await prefs.setInt(key, value);
  }

  @override
  Future<int?> getInt(String key) async {
    final prefs = await _preferences;
    return prefs.getInt(key);
  }

  @override
  Future<bool> setBool(String key, bool value) async {
    final prefs = await _preferences;
    return await prefs.setBool(key, value);
  }

  @override
  Future<bool?> getBool(String key) async {
    final prefs = await _preferences;
    return prefs.getBool(key);
  }

  @override
  Future<bool> setDouble(String key, double value) async {
    final prefs = await _preferences;
    return await prefs.setDouble(key, value);
  }

  @override
  Future<double?> getDouble(String key) async {
    final prefs = await _preferences;
    return prefs.getDouble(key);
  }

  @override
  Future<bool> setStringList(String key, List<String> value) async {
    final prefs = await _preferences;
    return await prefs.setStringList(key, value);
  }

  @override
  Future<List<String>?> getStringList(String key) async {
    final prefs = await _preferences;
    return prefs.getStringList(key);
  }

  @override
  Future<bool> remove(String key) async {
    final prefs = await _preferences;
    return await prefs.remove(key);
  }

  @override
  Future<bool> clear() async {
    final prefs = await _preferences;
    return await prefs.clear();
  }

  @override
  Future<bool> containsKey(String key) async {
    final prefs = await _preferences;
    return prefs.containsKey(key);
  }

  @override
  Future<Set<String>> getKeys() async {
    final prefs = await _preferences;
    return prefs.getKeys();
  }
}

/// 内存存储服务（用于测试）
class MemoryStorageService implements StorageService {
  final Map<String, dynamic> _storage = {};

  @override
  Future<bool> setString(String key, String value) async {
    _storage[key] = value;
    return true;
  }

  @override
  Future<String?> getString(String key) async {
    final value = _storage[key];
    return value is String ? value : null;
  }

  @override
  Future<bool> setInt(String key, int value) async {
    _storage[key] = value;
    return true;
  }

  @override
  Future<int?> getInt(String key) async {
    final value = _storage[key];
    return value is int ? value : null;
  }

  @override
  Future<bool> setBool(String key, bool value) async {
    _storage[key] = value;
    return true;
  }

  @override
  Future<bool?> getBool(String key) async {
    final value = _storage[key];
    return value is bool ? value : null;
  }

  @override
  Future<bool> setDouble(String key, double value) async {
    _storage[key] = value;
    return true;
  }

  @override
  Future<double?> getDouble(String key) async {
    final value = _storage[key];
    return value is double ? value : null;
  }

  @override
  Future<bool> setStringList(String key, List<String> value) async {
    _storage[key] = List<String>.from(value);
    return true;
  }

  @override
  Future<List<String>?> getStringList(String key) async {
    final value = _storage[key];
    if (value is List) {
      return value.cast<String>();
    }
    return null;
  }

  @override
  Future<bool> remove(String key) async {
    _storage.remove(key);
    return true;
  }

  @override
  Future<bool> clear() async {
    _storage.clear();
    return true;
  }

  @override
  Future<bool> containsKey(String key) async {
    return _storage.containsKey(key);
  }

  @override
  Future<Set<String>> getKeys() async {
    return _storage.keys.toSet();
  }
}