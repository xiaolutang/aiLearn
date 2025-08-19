import 'package:connectivity_plus/connectivity_plus.dart';

/// 网络信息接口
abstract class NetworkInfo {
  /// 检查是否有网络连接
  Future<bool> get isConnected;
  
  /// 获取当前连接类型
  Future<ConnectivityResult> get connectionType;
  
  /// 监听网络状态变化
  Stream<ConnectivityResult> get onConnectivityChanged;
}

/// 基于connectivity_plus的网络信息实现
class ConnectivityNetworkInfo implements NetworkInfo {
  final Connectivity _connectivity;
  
  ConnectivityNetworkInfo(this._connectivity);

  @override
  Future<bool> get isConnected async {
    final result = await _connectivity.checkConnectivity();
    return result != ConnectivityResult.none;
  }

  @override
  Future<ConnectivityResult> get connectionType async {
    return await _connectivity.checkConnectivity();
  }

  @override
  Stream<ConnectivityResult> get onConnectivityChanged {
    return _connectivity.onConnectivityChanged;
  }
}

/// 模拟网络信息（用于测试）
class MockNetworkInfo implements NetworkInfo {
  bool _isConnected;
  ConnectivityResult _connectionType;
  
  MockNetworkInfo({
    bool isConnected = true,
    ConnectivityResult connectionType = ConnectivityResult.wifi,
  }) : _isConnected = isConnected,
       _connectionType = connectionType;

  @override
  Future<bool> get isConnected async => _isConnected;

  @override
  Future<ConnectivityResult> get connectionType async => _connectionType;

  @override
  Stream<ConnectivityResult> get onConnectivityChanged {
    return Stream.value(_connectionType);
  }
  
  /// 设置网络连接状态（用于测试）
  void setConnected(bool connected) {
    _isConnected = connected;
    _connectionType = connected ? ConnectivityResult.wifi : ConnectivityResult.none;
  }
  
  /// 设置连接类型（用于测试）
  void setConnectionType(ConnectivityResult type) {
    _connectionType = type;
    _isConnected = type != ConnectivityResult.none;
  }
}