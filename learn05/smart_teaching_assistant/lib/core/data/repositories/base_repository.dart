import 'dart:async';
import '../datasources/local_data_source.dart';
import '../datasources/remote_data_source.dart';
import '../../models/api_response.dart';
import '../../utils/app_logger.dart';
import '../../services/connectivity_service.dart';

/// Repository基类，实现数据源管理和缓存策略
abstract class BaseRepository {
  final RemoteDataSource remoteDataSource;
  final LocalDataSource localDataSource;
  final ConnectivityService connectivityService;

  BaseRepository({
    required this.remoteDataSource,
    required this.localDataSource,
    required this.connectivityService,
  });

  /// 通用数据获取方法，实现网络降级策略
  /// [remoteCall] 网络请求方法
  /// [localCall] 本地数据获取方法
  /// [cacheKey] 缓存键
  /// [forceRefresh] 是否强制刷新
  Future<ApiResponse<T>> fetchData<T>({
    required Future<ApiResponse<T>> Function() remoteCall,
    required Future<T?> Function() localCall,
    required String cacheKey,
    bool forceRefresh = false,
    Duration? cacheExpiry,
  }) async {
    try {
      // 检查网络连接状态
      final isConnected = connectivityService.isConnected;
      
      // 如果有网络且不是强制刷新，先检查缓存是否有效
      if (isConnected && !forceRefresh) {
        final cachedData = await _getCachedData<T>(cacheKey, cacheExpiry);
        if (cachedData != null) {
          AppLogger.debug('Repository: 返回缓存数据', {'cacheKey': cacheKey});
          return ApiResponse.success(data: cachedData);
        }
      }

      // 尝试网络请求
      if (isConnected) {
        try {
          final response = await remoteCall();
          
          if (response.success && response.data != null) {
            // 成功获取数据，更新本地缓存
            await _cacheData(cacheKey, response.data!);
            AppLogger.info('Repository: 网络请求成功，已更新缓存', {
              'cacheKey': cacheKey,
              'dataType': T.toString(),
            });
            return response;
          } else {
            // 网络请求失败，尝试返回本地数据
            AppLogger.warning('Repository: 网络请求失败，尝试本地数据', {
              'cacheKey': cacheKey,
              'error': response.message,
            });
            return await _fallbackToLocal<T>(localCall, cacheKey);
          }
        } catch (e) {
          // 网络异常，降级到本地数据
          AppLogger.error('Repository: 网络异常，降级到本地数据', e, null);
          return await _fallbackToLocal<T>(localCall, cacheKey);
        }
      } else {
        // 无网络连接，直接使用本地数据
        AppLogger.info('Repository: 无网络连接，使用本地数据', {'cacheKey': cacheKey});
        return await _fallbackToLocal<T>(localCall, cacheKey);
      }
    } catch (e, stackTrace) {
      AppLogger.error('Repository: 数据获取异常', e, stackTrace);
      return ApiResponse.error(message: '数据获取失败: ${e.toString()}');
    }
  }

  /// 获取缓存数据
  Future<T?> _getCachedData<T>(String cacheKey, Duration? cacheExpiry) async {
    try {
      final cacheInfo = await localDataSource.getCacheInfo(cacheKey);
      if (cacheInfo != null && cacheExpiry != null) {
        final now = DateTime.now();
        final cacheTime = DateTime.parse(cacheInfo['timestamp']);
        if (now.difference(cacheTime) > cacheExpiry) {
          AppLogger.debug('Repository: 缓存已过期', {
            'cacheKey': cacheKey,
            'cacheTime': cacheTime.toIso8601String(),
            'expiry': cacheExpiry.toString(),
          });
          return null;
        }
      }
      return await localDataSource.getCachedData<T>(cacheKey);
    } catch (e) {
      AppLogger.warning('Repository: 获取缓存数据失败', {'error': e.toString()});
      return null;
    }
  }

  /// 缓存数据
  Future<void> _cacheData<T>(String cacheKey, T data) async {
    try {
      await localDataSource.cacheData(cacheKey, data);
    } catch (e) {
      AppLogger.warning('Repository: 缓存数据失败', {'error': e.toString()});
    }
  }

  /// 降级到本地数据
  Future<ApiResponse<T>> _fallbackToLocal<T>(
    Future<T?> Function() localCall,
    String cacheKey,
  ) async {
    try {
      final localData = await localCall();
      if (localData != null) {
        AppLogger.info('Repository: 使用本地数据', {'cacheKey': cacheKey});
        return ApiResponse.success(
          data: localData,
          message: '使用本地数据',
        );
      } else {
        AppLogger.warning('Repository: 本地数据不可用', {'cacheKey': cacheKey});
        return ApiResponse.error(message: '数据不可用，请检查网络连接');
      }
    } catch (e) {
      AppLogger.error('Repository: 本地数据获取失败', e, null);
      return ApiResponse.error(message: '本地数据获取失败');
    }
  }

  /// 清除指定缓存
  Future<void> clearCache(String cacheKey) async {
    try {
      await localDataSource.clearCache(cacheKey);
      AppLogger.info('Repository: 缓存已清除', {'cacheKey': cacheKey});
    } catch (e) {
      AppLogger.warning('Repository: 清除缓存失败', {'error': e.toString()});
    }
  }

  /// 清除所有缓存
  Future<void> clearAllCache() async {
    try {
      await localDataSource.clearAllCache();
      AppLogger.info('Repository: 所有缓存已清除');
    } catch (e) {
      AppLogger.warning('Repository: 清除所有缓存失败', {'error': e.toString()});
    }
  }

  /// 根据前缀清除缓存
  Future<void> clearCacheByPrefix(String prefix) async {
    try {
      await localDataSource.clearCacheByPrefix(prefix);
      AppLogger.info('Repository: 前缀缓存已清除', {'prefix': prefix});
    } catch (e) {
      AppLogger.warning('Repository: 清除前缀缓存失败', {'error': e.toString()});
    }
  }

  /// 同步数据到服务器
  Future<ApiResponse<bool>> syncToServer<T>({
    required T data,
    required Future<ApiResponse<bool>> Function(T) uploadCall,
    required String syncKey,
  }) async {
    try {
      final isConnected = connectivityService.isConnected;
      if (!isConnected) {
        // 无网络时，将数据标记为待同步
        await localDataSource.markForSync(syncKey, data);
        AppLogger.info('Repository: 数据已标记为待同步', {'syncKey': syncKey});
        return ApiResponse.success(
          data: true,
          message: '数据已保存，将在网络恢复后同步',
        );
      }

      // 有网络时，直接上传
      final response = await uploadCall(data);
      if (response.success) {
        // 同步成功，清除待同步标记
        await localDataSource.clearSyncMark(syncKey);
        AppLogger.info('Repository: 数据同步成功', {'syncKey': syncKey});
      } else {
        // 同步失败，标记为待同步
        await localDataSource.markForSync(syncKey, data);
        AppLogger.warning('Repository: 数据同步失败，已标记为待同步', {
          'syncKey': syncKey,
          'error': response.message,
        });
      }
      return response;
    } catch (e, stackTrace) {
      AppLogger.error('Repository: 数据同步异常', e, stackTrace);
      // 异常时也标记为待同步
      await localDataSource.markForSync(syncKey, data);
      return ApiResponse.error(message: '数据同步失败: ${e.toString()}');
    }
  }

  /// 获取待同步数据
  Future<List<Map<String, dynamic>>> getPendingSyncData() async {
    try {
      return await localDataSource.getPendingSyncData();
    } catch (e) {
      AppLogger.error('Repository: 获取待同步数据失败', e, null);
      return [];
    }
  }

  /// 执行批量同步
  Future<void> performBatchSync() async {
    try {
      final isConnected = connectivityService.isConnected;
      if (!isConnected) {
        AppLogger.info('Repository: 无网络连接，跳过批量同步');
        return;
      }

      final pendingData = await getPendingSyncData();
      if (pendingData.isEmpty) {
        AppLogger.info('Repository: 无待同步数据');
        return;
      }

      AppLogger.info('Repository: 开始批量同步', {'count': pendingData.length});
      
      for (final item in pendingData) {
        try {
          await _syncSingleItem(item);
        } catch (e) {
          AppLogger.warning('Repository: 单项同步失败', {
            'syncKey': item['syncKey'],
            'error': e.toString(),
          });
        }
      }
      
      AppLogger.info('Repository: 批量同步完成');
    } catch (e, stackTrace) {
      AppLogger.error('Repository: 批量同步异常', e, stackTrace);
    }
  }

  /// 同步单个数据项（子类需要实现）
  Future<void> _syncSingleItem(Map<String, dynamic> item) async {
    // 子类需要根据具体业务实现
    throw UnimplementedError('子类需要实现 _syncSingleItem 方法');
  }
}