import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../models/api_response.dart';
import '../../utils/app_logger.dart';
import '../../constants/app_constants.dart';

/// 远程数据源抽象类
abstract class RemoteDataSource {
  /// GET请求
  Future<ApiResponse<T>> get<T>(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
    T? Function(dynamic)? fromJson,
  });

  /// POST请求
  Future<ApiResponse<T>> post<T>(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? body,
    T? Function(dynamic)? fromJson,
  });

  /// PUT请求
  Future<ApiResponse<T>> put<T>(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? body,
    T? Function(dynamic)? fromJson,
  });

  /// DELETE请求
  Future<ApiResponse<T>> delete<T>(
    String endpoint, {
    Map<String, String>? headers,
    T? Function(dynamic)? fromJson,
  });

  /// PATCH请求
  Future<ApiResponse<T>> patch<T>(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? body,
    T? Function(dynamic)? fromJson,
  });

  /// 上传文件
  Future<ApiResponse<T>> uploadFile<T>(
    String endpoint,
    File file, {
    Map<String, String>? headers,
    Map<String, String>? fields,
    T? Function(dynamic)? fromJson,
  });

  /// 设置认证Token
  void setAuthToken(String? token);

  /// 设置刷新Token
  void setRefreshToken(String? refreshToken);

  /// 刷新Token
  Future<ApiResponse<Map<String, dynamic>>> refreshToken();
}

/// 远程数据源实现类
class RemoteDataSourceImpl implements RemoteDataSource {
  late http.Client _client;
  String? _authToken;
  String? _refreshToken;
  final String _baseUrl;
  final Duration _timeout;
  
  // Token刷新相关
  bool _isRefreshing = false;
  final List<Completer<String?>> _tokenRefreshCompleters = [];

  RemoteDataSourceImpl({
    String? baseUrl,
    Duration? timeout,
  }) : _baseUrl = baseUrl ?? AppConstants.baseUrl,
       _timeout = timeout ?? const Duration(seconds: 30);

  /// 初始化
  void initialize() {
    _client = http.Client();
    AppLogger.info('RemoteDataSource: 初始化完成', {
      'baseUrl': _baseUrl,
      'timeout': _timeout.inSeconds,
    });
  }

  /// 释放资源
  void dispose() {
    _client.close();
    AppLogger.info('RemoteDataSource: 资源已释放');
  }

  @override
  void setAuthToken(String? token) {
    _authToken = token;
    AppLogger.debug('RemoteDataSource: 设置认证Token', {
      'hasToken': token != null,
    });
  }

  @override
  void setRefreshToken(String? refreshToken) {
    _refreshToken = refreshToken;
    AppLogger.debug('RemoteDataSource: 设置刷新Token', {
      'hasRefreshToken': refreshToken != null,
    });
  }

  @override
  Future<ApiResponse<T>> get<T>(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
    T? Function(dynamic)? fromJson,
  }) async {
    return _makeRequest<T>(
      'GET',
      endpoint,
      headers: headers,
      queryParameters: queryParameters,
      fromJson: fromJson,
    );
  }

  @override
  Future<ApiResponse<T>> post<T>(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? body,
    T? Function(dynamic)? fromJson,
  }) async {
    return _makeRequest<T>(
      'POST',
      endpoint,
      headers: headers,
      body: body,
      fromJson: fromJson,
    );
  }

  @override
  Future<ApiResponse<T>> put<T>(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? body,
    T? Function(dynamic)? fromJson,
  }) async {
    return _makeRequest<T>(
      'PUT',
      endpoint,
      headers: headers,
      body: body,
      fromJson: fromJson,
    );
  }

  @override
  Future<ApiResponse<T>> delete<T>(
    String endpoint, {
    Map<String, String>? headers,
    T? Function(dynamic)? fromJson,
  }) async {
    return _makeRequest<T>(
      'DELETE',
      endpoint,
      headers: headers,
      fromJson: fromJson,
    );
  }

  @override
  Future<ApiResponse<T>> patch<T>(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? body,
    T? Function(dynamic)? fromJson,
  }) async {
    return _makeRequest<T>(
      'PATCH',
      endpoint,
      headers: headers,
      body: body,
      fromJson: fromJson,
    );
  }

  @override
  Future<ApiResponse<T>> uploadFile<T>(
    String endpoint,
    File file, {
    Map<String, String>? headers,
    Map<String, String>? fields,
    T? Function(dynamic)? fromJson,
  }) async {
    try {
      final uri = _buildUri(endpoint);
      final request = http.MultipartRequest('POST', uri);
      
      // 添加文件
      final multipartFile = await http.MultipartFile.fromPath(
        'file',
        file.path,
      );
      request.files.add(multipartFile);
      
      // 添加字段
      if (fields != null) {
        request.fields.addAll(fields);
      }
      
      // 添加请求头
      final requestHeaders = _buildHeaders(headers);
      request.headers.addAll(requestHeaders);
      
      AppLogger.debug('RemoteDataSource: 开始文件上传', {
        'endpoint': endpoint,
        'fileName': file.path.split('/').last,
        'fileSize': await file.length(),
      });
      
      final streamedResponse = await request.send().timeout(_timeout);
      final response = await http.Response.fromStream(streamedResponse);
      
      return _handleResponse<T>(response, fromJson);
    } catch (e, stackTrace) {
      AppLogger.error('RemoteDataSource: 文件上传异常', e, stackTrace);
      return _handleError<T>(e);
    }
  }

  /// 执行HTTP请求
  Future<ApiResponse<T>> _makeRequest<T>(
    String method,
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? body,
    Map<String, dynamic>? queryParameters,
    T? Function(dynamic)? fromJson,
    int retryCount = 0,
  }) async {
    try {
      final uri = _buildUri(endpoint, queryParameters);
      final requestHeaders = _buildHeaders(headers);
      
      AppLogger.debug('RemoteDataSource: 发起请求', {
        'method': method,
        'url': uri.toString(),
        'hasBody': body != null,
        'retryCount': retryCount,
      });
      
      late http.Response response;
      
      switch (method.toUpperCase()) {
        case 'GET':
          response = await _client.get(uri, headers: requestHeaders).timeout(_timeout);
          break;
        case 'POST':
          response = await _client.post(
            uri,
            headers: requestHeaders,
            body: body != null ? jsonEncode(body) : null,
          ).timeout(_timeout);
          break;
        case 'PUT':
          response = await _client.put(
            uri,
            headers: requestHeaders,
            body: body != null ? jsonEncode(body) : null,
          ).timeout(_timeout);
          break;
        case 'DELETE':
          response = await _client.delete(uri, headers: requestHeaders).timeout(_timeout);
          break;
        case 'PATCH':
          response = await _client.patch(
            uri,
            headers: requestHeaders,
            body: body != null ? jsonEncode(body) : null,
          ).timeout(_timeout);
          break;
        default:
          throw UnsupportedError('不支持的HTTP方法: $method');
      }
      
      // 处理401错误，尝试刷新Token
      if (response.statusCode == 401 && retryCount == 0 && _refreshToken != null) {
        AppLogger.info('RemoteDataSource: 检测到401错误，尝试刷新Token');
        
        final newToken = await _handleTokenRefresh();
        if (newToken != null) {
          // 使用新Token重试请求
          return _makeRequest<T>(
            method,
            endpoint,
            headers: headers,
            body: body,
            queryParameters: queryParameters,
            fromJson: fromJson,
            retryCount: retryCount + 1,
          );
        }
      }
      
      return _handleResponse<T>(response, fromJson);
    } catch (e, stackTrace) {
      AppLogger.error('RemoteDataSource: 请求异常', e, stackTrace);
      return _handleError<T>(e);
    }
  }

  /// 构建请求URI
  Uri _buildUri(String endpoint, [Map<String, dynamic>? queryParameters]) {
    final url = endpoint.startsWith('http') ? endpoint : '$_baseUrl$endpoint';
    final uri = Uri.parse(url);
    
    if (queryParameters != null && queryParameters.isNotEmpty) {
      final queryString = queryParameters.entries
          .map((e) => '${Uri.encodeComponent(e.key)}=${Uri.encodeComponent(e.value.toString())}')
          .join('&');
      return Uri.parse('${uri.toString()}?$queryString');
    }
    
    return uri;
  }

  /// 构建请求头
  Map<String, String> _buildHeaders([Map<String, String>? customHeaders]) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    // 添加认证头
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    
    // 添加自定义头
    if (customHeaders != null) {
      headers.addAll(customHeaders);
    }
    
    return headers;
  }

  /// 处理响应
  ApiResponse<T> _handleResponse<T>(
    http.Response response,
    T? Function(dynamic)? fromJson,
  ) {
    try {
      AppLogger.debug('RemoteDataSource: 收到响应', {
        'statusCode': response.statusCode,
        'contentLength': response.body.length,
      });
      
      // 解析响应体
      Map<String, dynamic> responseData;
      try {
        responseData = jsonDecode(response.body) as Map<String, dynamic>;
      } catch (e) {
        // 如果不是JSON格式，创建一个包装对象
        responseData = {
          'success': response.statusCode >= 200 && response.statusCode < 300,
          'code': response.statusCode,
          'message': response.statusCode >= 200 && response.statusCode < 300 
              ? '请求成功' 
              : '请求失败',
          'data': response.body,
        };
      }
      
      // 根据状态码判断成功或失败
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return ApiResponse<T>(
          success: responseData['success'] ?? true,
          code: responseData['code'] ?? response.statusCode,
          message: responseData['message'] ?? '请求成功',
          data: fromJson != null && responseData['data'] != null
              ? fromJson(responseData['data'])
              : responseData['data'],
          metadata: responseData['metadata'],
        );
      } else {
        return ApiResponse<T>(
          success: false,
          code: response.statusCode,
          message: responseData['message'] ?? _getStatusMessage(response.statusCode),
          error: responseData['error'] ?? {
            'statusCode': response.statusCode,
            'body': response.body,
          },
        );
      }
    } catch (e, stackTrace) {
      AppLogger.error('RemoteDataSource: 响应处理异常', e, stackTrace);
      return ApiResponse<T>(
        success: false,
        code: response.statusCode,
        message: '响应解析失败',
        error: {'parseError': e.toString()},
      );
    }
  }

  /// 处理错误
  ApiResponse<T> _handleError<T>(dynamic error) {
    if (error is TimeoutException) {
      return ApiResponse.networkError(message: '请求超时，请检查网络连接');
    }
    
    if (error is SocketException) {
      return ApiResponse.networkError(message: '网络连接失败，请检查网络设置');
    }
    
    if (error is HttpException) {
      return ApiResponse.serverError(message: '服务器错误: ${error.message}');
    }
    
    return ApiResponse.error(message: '请求失败: ${error.toString()}');
  }

  /// 获取状态码对应的消息
  String _getStatusMessage(int statusCode) {
    switch (statusCode) {
      case 400:
        return '请求参数错误';
      case 401:
        return '未授权访问';
      case 403:
        return '禁止访问';
      case 404:
        return '资源不存在';
      case 422:
        return '数据验证失败';
      case 500:
        return '服务器内部错误';
      case 502:
        return '网关错误';
      case 503:
        return '服务不可用';
      case 504:
        return '网关超时';
      default:
        return '请求失败 ($statusCode)';
    }
  }

  /// 处理Token刷新
  Future<String?> _handleTokenRefresh() async {
    // 如果已经在刷新中，等待刷新完成
    if (_isRefreshing) {
      final completer = Completer<String?>();
      _tokenRefreshCompleters.add(completer);
      return completer.future;
    }
    
    _isRefreshing = true;
    
    try {
      final response = await refreshToken();
      
      if (response.success && response.data != null) {
        final newToken = response.data!['access_token'] as String?;
        final newRefreshToken = response.data!['refresh_token'] as String?;
        
        // 更新Token
        setAuthToken(newToken);
        if (newRefreshToken != null) {
          setRefreshToken(newRefreshToken);
        }
        
        // 通知等待的请求
        for (final completer in _tokenRefreshCompleters) {
          completer.complete(newToken);
        }
        _tokenRefreshCompleters.clear();
        
        AppLogger.info('RemoteDataSource: Token刷新成功');
        return newToken;
      } else {
        AppLogger.warning('RemoteDataSource: Token刷新失败', {
          'message': response.message,
        });
        
        // 通知等待的请求刷新失败
        for (final completer in _tokenRefreshCompleters) {
          completer.complete(null);
        }
        _tokenRefreshCompleters.clear();
        
        return null;
      }
    } catch (e, stackTrace) {
      AppLogger.error('RemoteDataSource: Token刷新异常', e, stackTrace);
      
      // 通知等待的请求刷新失败
      for (final completer in _tokenRefreshCompleters) {
        completer.complete(null);
      }
      _tokenRefreshCompleters.clear();
      
      return null;
    } finally {
      _isRefreshing = false;
    }
  }

  @override
  Future<ApiResponse<Map<String, dynamic>>> refreshToken() async {
    if (_refreshToken == null) {
      return ApiResponse.authError(message: '刷新Token不存在');
    }
    
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/api/v1/auth/refresh'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_refreshToken',
        },
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse.success(data: data);
      } else {
        return ApiResponse.authError(
          message: 'Token刷新失败',
          code: response.statusCode,
        );
      }
    } catch (e, stackTrace) {
      AppLogger.error('RemoteDataSource: Token刷新请求异常', e, stackTrace);
      return ApiResponse.authError(message: 'Token刷新请求失败');
    }
  }

  /// 获取请求统计信息
  Map<String, dynamic> getRequestStats() {
    // 在实际应用中，这里应该维护请求统计信息
    return {
      'totalRequests': 0,
      'successRequests': 0,
      'failedRequests': 0,
      'averageResponseTime': 0,
    };
  }
}