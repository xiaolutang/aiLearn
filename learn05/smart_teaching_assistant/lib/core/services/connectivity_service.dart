import 'dart:async';
import 'dart:io';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../utils/app_logger.dart';

class ConnectivityService {
  static ConnectivityService? _instance;
  static ConnectivityService get instance => _instance ??= ConnectivityService._();
  
  ConnectivityService._();
  
  final Connectivity _connectivity = Connectivity();
  StreamSubscription<ConnectivityResult>? _connectivitySubscription;
  
  // 网络状态流控制器
  final StreamController<bool> _networkStatusController = StreamController<bool>.broadcast();
  
  // 当前网络状态
  bool _isConnected = false;
  ConnectivityResult _currentConnectivity = ConnectivityResult.none;
  
  // 网络状态监听器列表
  final List<Function(bool)> _listeners = [];
  
  /// 获取网络状态流
  Stream<bool> get networkStatusStream => _networkStatusController.stream;
  
  /// 获取当前网络连接状态
  bool get isConnected => _isConnected;
  
  /// 获取当前连接类型
  ConnectivityResult get currentConnectivity => _currentConnectivity;
  
  /// 初始化连接服务
  Future<void> init() async {
    try {
      AppLogger.info('Initializing connectivity service');
      
      // 获取初始连接状态
      await _updateConnectivityStatus();
      
      // 监听连接状态变化
      _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
        _onConnectivityChanged,
        onError: (error, stackTrace) {
          AppLogger.error('Connectivity stream error', error, stackTrace);
        },
      );
      
      AppLogger.info('Connectivity service initialized. Current status: $_isConnected');
    } catch (e, stackTrace) {
      AppLogger.error('Failed to initialize connectivity service', e, stackTrace);
      rethrow;
    }
  }
  
  /// 处理连接状态变化
  void _onConnectivityChanged(ConnectivityResult result) async {
    AppLogger.debug('Connectivity changed: $result');
    _currentConnectivity = result;
    await _updateConnectivityStatus();
  }
  
  /// 更新连接状态
  Future<void> _updateConnectivityStatus() async {
    try {
      final previousStatus = _isConnected;
      
      // 首先检查连接类型
      if (_currentConnectivity == ConnectivityResult.none) {
        _isConnected = false;
      } else {
        // 即使有连接类型，也需要验证实际的网络可达性
        _isConnected = await _checkInternetConnection();
      }
      
      // 如果状态发生变化，通知监听器
      if (previousStatus != _isConnected) {
        AppLogger.info('Network status changed: $_isConnected');
        _notifyListeners(_isConnected);
        _networkStatusController.add(_isConnected);
      }
    } catch (e, stackTrace) {
      AppLogger.error('Failed to update connectivity status', e, stackTrace);
      _isConnected = false;
    }
  }
  
  /// 检查实际的互联网连接
  Future<bool> _checkInternetConnection() async {
    try {
      // 尝试连接到可靠的服务器
      final result = await InternetAddress.lookup('google.com')
          .timeout(const Duration(seconds: 5));
      
      if (result.isNotEmpty && result[0].rawAddress.isNotEmpty) {
        return true;
      }
      return false;
    } catch (e) {
      // 如果连接失败，尝试备用服务器
      try {
        final result = await InternetAddress.lookup('baidu.com')
            .timeout(const Duration(seconds: 5));
        
        if (result.isNotEmpty && result[0].rawAddress.isNotEmpty) {
          return true;
        }
        return false;
      } catch (e) {
        AppLogger.debug('Internet connection check failed: $e');
        return false;
      }
    }
  }
  
  /// 添加网络状态监听器
  void addListener(Function(bool) listener) {
    _listeners.add(listener);
    AppLogger.debug('Added network status listener. Total: ${_listeners.length}');
  }
  
  /// 移除网络状态监听器
  void removeListener(Function(bool) listener) {
    _listeners.remove(listener);
    AppLogger.debug('Removed network status listener. Total: ${_listeners.length}');
  }
  
  /// 通知所有监听器
  void _notifyListeners(bool isConnected) {
    for (final listener in _listeners) {
      try {
        listener(isConnected);
      } catch (e, stackTrace) {
        AppLogger.error('Error in network status listener', e, stackTrace);
      }
    }
  }
  
  /// 手动检查网络状态
  Future<bool> checkConnectivity() async {
    try {
      AppLogger.debug('Manual connectivity check requested');
      
      // 获取当前连接类型
      _currentConnectivity = await _connectivity.checkConnectivity();
      
      // 更新状态
      await _updateConnectivityStatus();
      
      return _isConnected;
    } catch (e, stackTrace) {
      AppLogger.error('Failed to check connectivity', e, stackTrace);
      return false;
    }
  }
  
  /// 等待网络连接
  Future<bool> waitForConnection({Duration timeout = const Duration(seconds: 30)}) async {
    try {
      AppLogger.debug('Waiting for network connection (timeout: ${timeout.inSeconds}s)');
      
      if (_isConnected) {
        return true;
      }
      
      final completer = Completer<bool>();
      late StreamSubscription subscription;
      
      // 设置超时
      final timeoutTimer = Timer(timeout, () {
        if (!completer.isCompleted) {
          completer.complete(false);
        }
      });
      
      // 监听网络状态变化
      subscription = networkStatusStream.listen((isConnected) {
        if (isConnected && !completer.isCompleted) {
          completer.complete(true);
        }
      });
      
      final result = await completer.future;
      
      // 清理资源
      timeoutTimer.cancel();
      subscription.cancel();
      
      AppLogger.debug('Wait for connection result: $result');
      return result;
    } catch (e, stackTrace) {
      AppLogger.error('Failed to wait for connection', e, stackTrace);
      return false;
    }
  }
  
  /// 获取连接类型描述
  String getConnectivityDescription() {
    switch (_currentConnectivity) {
      case ConnectivityResult.wifi:
        return 'WiFi';
      case ConnectivityResult.mobile:
        return '移动网络';
      case ConnectivityResult.ethernet:
        return '以太网';
      case ConnectivityResult.bluetooth:
        return '蓝牙';
      case ConnectivityResult.vpn:
        return 'VPN';
      case ConnectivityResult.other:
        return '其他';
      case ConnectivityResult.none:
      default:
        return '无连接';
    }
  }
  
  /// 获取网络质量评估
  Future<NetworkQuality> assessNetworkQuality() async {
    try {
      if (!_isConnected) {
        return NetworkQuality.none;
      }
      
      AppLogger.debug('Assessing network quality');
      
      final stopwatch = Stopwatch()..start();
      
      // 测试网络延迟
      try {
        await InternetAddress.lookup('google.com')
            .timeout(const Duration(seconds: 3));
        stopwatch.stop();
        
        final latency = stopwatch.elapsedMilliseconds;
        
        if (latency < 100) {
          return NetworkQuality.excellent;
        } else if (latency < 300) {
          return NetworkQuality.good;
        } else if (latency < 1000) {
          return NetworkQuality.fair;
        } else {
          return NetworkQuality.poor;
        }
      } catch (e) {
        return NetworkQuality.poor;
      }
    } catch (e, stackTrace) {
      AppLogger.error('Failed to assess network quality', e, stackTrace);
      return NetworkQuality.unknown;
    }
  }
  
  /// 获取网络信息
  Map<String, dynamic> getNetworkInfo() {
    return {
      'isConnected': _isConnected,
      'connectivityType': _currentConnectivity.toString(),
      'connectivityDescription': getConnectivityDescription(),
      'timestamp': DateTime.now().toIso8601String(),
    };
  }
  
  /// 重置连接状态（用于测试）
  void resetConnectionStatus() {
    AppLogger.debug('Resetting connection status');
    _isConnected = false;
    _currentConnectivity = ConnectivityResult.none;
    _notifyListeners(_isConnected);
    _networkStatusController.add(_isConnected);
  }
  
  /// 模拟网络状态（用于测试）
  void simulateNetworkStatus(bool isConnected, [ConnectivityResult? connectivity]) {
    AppLogger.debug('Simulating network status: $isConnected');
    _isConnected = isConnected;
    _currentConnectivity = connectivity ?? 
        (isConnected ? ConnectivityResult.wifi : ConnectivityResult.none);
    _notifyListeners(_isConnected);
    _networkStatusController.add(_isConnected);
  }
  
  /// 释放资源
  void dispose() {
    try {
      AppLogger.info('Disposing connectivity service');
      
      _connectivitySubscription?.cancel();
      _connectivitySubscription = null;
      
      _networkStatusController.close();
      _listeners.clear();
      
      AppLogger.info('Connectivity service disposed');
    } catch (e, stackTrace) {
      AppLogger.error('Error disposing connectivity service', e, stackTrace);
    }
  }
}

/// 网络质量枚举
enum NetworkQuality {
  none,      // 无网络
  poor,      // 网络质量差
  fair,      // 网络质量一般
  good,      // 网络质量良好
  excellent, // 网络质量优秀
  unknown,   // 未知
}

/// 网络质量扩展方法
extension NetworkQualityExtension on NetworkQuality {
  String get description {
    switch (this) {
      case NetworkQuality.none:
        return '无网络';
      case NetworkQuality.poor:
        return '网络较差';
      case NetworkQuality.fair:
        return '网络一般';
      case NetworkQuality.good:
        return '网络良好';
      case NetworkQuality.excellent:
        return '网络优秀';
      case NetworkQuality.unknown:
        return '网络状态未知';
    }
  }
  
  double get score {
    switch (this) {
      case NetworkQuality.none:
        return 0.0;
      case NetworkQuality.poor:
        return 0.2;
      case NetworkQuality.fair:
        return 0.5;
      case NetworkQuality.good:
        return 0.8;
      case NetworkQuality.excellent:
        return 1.0;
      case NetworkQuality.unknown:
        return 0.0;
    }
  }
}