import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'constants.dart';
import 'app_logger.dart';
import '../models/api_response.dart';

/// HTTP客户端封装类
class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();

  late http.Client _client;
  String? _token;
  String? _refreshToken;

  /// 初始化客户端
  void initialize() {
    _client = http.Client();
    _loadTokens();
  }

  /// 从本地存储加载Tokens
  Future<void> _loadTokens() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString('auth_token');
      _refreshToken = prefs.getString('refresh_token');
    } catch (e) {
      print('加载Tokens失败: $e');
    }
  }

  /// 保存Token到本地存储
  Future<void> setTokens(String? token, String? refreshToken) async {
    try {
      _token = token;
      _refreshToken = refreshToken;
      final prefs = await SharedPreferences.getInstance();
      if (token != null) {
        await prefs.setString('auth_token', token);
      } else {
        await prefs.remove('auth_token');
      }
      if (refreshToken != null) {
        await prefs.setString('refresh_token', refreshToken);
      } else {
        await prefs.remove('refresh_token');
      }
    } catch (e) {
      print('保存Tokens失败: $e');
    }
  }

  /// 保存单个Token（向后兼容）
  Future<void> setToken(String? token) async {
    await setTokens(token, _refreshToken);
  }

  /// 清除所有Token
  Future<void> clearTokens() async {
    await setTokens(null, null);
  }

  /// 文件上传（增强版）
  Future<ApiResponse<T>> uploadFileWithResponse<T>(
    String url,
    String filePath,
    String fieldName, {
    Map<String, String>? fields,
    Map<String, String>? headers,
    T? Function(dynamic)? fromJsonT,
  }) async {
    try {
      final response = await uploadFile(url, filePath, fieldName, fields: fields, headers: headers);
      
      if (response.statusCode >= 200 && response.statusCode < 300) {
        final responseBody = await response.stream.bytesToString();
        
        try {
          final Map<String, dynamic> jsonData = json.decode(responseBody);
          return ApiResponse<T>.fromJson(jsonData, fromJsonT);
        } catch (e) {
          return ApiResponse<T>.success(
            code: response.statusCode,
            message: '上传成功',
            data: responseBody as T?,
          );
        }
      } else {
        return ApiResponse<T>.error(
          code: response.statusCode,
          message: 'HTTP ${response.statusCode}',
        );
      }
    } catch (e) {
      return ApiResponse<T>.error(
        code: -3,
        message: '文件上传失败: ${e.toString()}',
      );
    }
  }

  /// 获取当前Token
  String? get token => _token;

  /// 构建请求头
  Map<String, String> _buildHeaders({Map<String, String>? headers}) {
    final defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (_token != null) {
      defaultHeaders['Authorization'] = 'Bearer $_token';
    }

    if (headers != null) {
      defaultHeaders.addAll(headers);
    }

    return defaultHeaders;
  }

  /// GET请求
  Future<ApiResponse<T>> get<T>(
    String url, {
    Map<String, String>? headers,
    Duration? timeout,
    T? Function(dynamic)? fromJsonT,
  }) async {
    try {
      AppLogger.debug('GET请求开始: $url', {'headers': headers, 'timeout': timeout?.inMilliseconds});
      
      final uri = Uri.parse(url);
      final requestHeaders = _buildHeaders(headers: headers);
      
      final response = await _client
          .get(
            uri,
            headers: requestHeaders,
          )
          .timeout(timeout ?? ApiConstants.defaultTimeout);
      
      AppLogger.debug('GET请求完成: $url', {
        'statusCode': response.statusCode,
        'responseLength': response.body.length,
      });
      
      return await _handleApiResponse<T>(response, fromJsonT);
    } on SocketException catch (e, stackTrace) {
      AppLogger.error('GET请求网络连接失败: $url [SocketException] Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -1,
        message: '网络连接失败，请检查网络设置',
      );
    } on HttpException catch (e, stackTrace) {
      AppLogger.error('GET请求HTTP异常: $url [HttpException] Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -2,
        message: 'HTTP请求异常',
      );
    } on TimeoutException catch (e, stackTrace) {
      final timeoutMs = timeout?.inMilliseconds ?? ApiConstants.defaultTimeout.inMilliseconds;
      AppLogger.error('GET请求超时: $url [TimeoutException] Timeout: ${timeoutMs}ms', e, stackTrace);
      return ApiResponse<T>.error(
        code: -4,
        message: '请求超时，请稍后重试',
      );
    } catch (e, stackTrace) {
      AppLogger.error('GET请求未知异常: $url [${e.runtimeType}] Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -3,
        message: '请求失败: ${e.toString()}',
      );
    }
  }

  /// POST请求
  Future<ApiResponse<T>> post<T>(
    String url, {
    Map<String, dynamic>? data,
    Map<String, String>? headers,
    Duration? timeout,
    T? Function(dynamic)? fromJsonT,
  }) async {
    try {
      AppLogger.debug('POST请求开始: $url', {'data': data, 'headers': headers, 'timeout': timeout?.inMilliseconds});
      
      final uri = Uri.parse(url);
      final body = data != null ? json.encode(data) : null;
      final requestHeaders = _buildHeaders(headers: headers);
      
      final response = await _client
          .post(
            uri,
            headers: requestHeaders,
            body: body,
          )
          .timeout(timeout ?? ApiConstants.defaultTimeout);
      
      AppLogger.debug('POST请求完成: $url', {
        'statusCode': response.statusCode,
        'responseLength': response.body.length,
      });
      
      return await _handleApiResponse<T>(response, fromJsonT);
    } on SocketException catch (e, stackTrace) {
      AppLogger.error('POST请求网络连接失败: $url [SocketException] Data: $data Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -1,
        message: '网络连接失败，请检查网络设置',
      );
    } on HttpException catch (e, stackTrace) {
      AppLogger.error('POST请求HTTP异常: $url [HttpException] Data: $data Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -2,
        message: 'HTTP请求异常',
      );
    } on TimeoutException catch (e, stackTrace) {
      final timeoutMs = timeout?.inMilliseconds ?? ApiConstants.defaultTimeout.inMilliseconds;
      AppLogger.error('POST请求超时: $url [TimeoutException] Timeout: ${timeoutMs}ms Data: $data', e, stackTrace);
      return ApiResponse<T>.error(
        code: -4,
        message: '请求超时，请稍后重试',
      );
    } catch (e, stackTrace) {
      AppLogger.error('POST请求未知异常: $url [${e.runtimeType}] Data: $data Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -3,
        message: '请求失败: ${e.toString()}',
      );
    }
  }

  /// PUT请求
  Future<ApiResponse<T>> put<T>(
    String url, {
    Map<String, dynamic>? data,
    Map<String, String>? headers,
    Duration? timeout,
    T? Function(dynamic)? fromJsonT,
  }) async {
    try {
      AppLogger.debug('PUT请求开始: $url', {'data': data, 'headers': headers, 'timeout': timeout?.inMilliseconds});
      
      final uri = Uri.parse(url);
      final body = data != null ? json.encode(data) : null;
      final requestHeaders = _buildHeaders(headers: headers);
      
      final response = await _client
          .put(
            uri,
            headers: requestHeaders,
            body: body,
          )
          .timeout(timeout ?? ApiConstants.defaultTimeout);
      
      AppLogger.debug('PUT请求完成: $url', {
        'statusCode': response.statusCode,
        'responseLength': response.body.length,
      });
      
      return await _handleApiResponse<T>(response, fromJsonT);
    } on SocketException catch (e, stackTrace) {
      AppLogger.error('PUT请求网络连接失败: $url [SocketException] Data: $data Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -1,
        message: '网络连接失败，请检查网络设置',
      );
    } on HttpException catch (e, stackTrace) {
      AppLogger.error('PUT请求HTTP异常: $url [HttpException] Data: $data Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -2,
        message: 'HTTP请求异常',
      );
    } on TimeoutException catch (e, stackTrace) {
      final timeoutMs = timeout?.inMilliseconds ?? ApiConstants.defaultTimeout.inMilliseconds;
      AppLogger.error('PUT请求超时: $url [TimeoutException] Timeout: ${timeoutMs}ms Data: $data', e, stackTrace);
      return ApiResponse<T>.error(
        code: -4,
        message: '请求超时，请稍后重试',
      );
    } catch (e, stackTrace) {
      AppLogger.error('PUT请求未知异常: $url [${e.runtimeType}] Data: $data Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -3,
        message: '请求失败: ${e.toString()}',
      );
    }
  }

  /// DELETE请求
  Future<ApiResponse<T>> delete<T>(
    String url, {
    Map<String, String>? headers,
    Duration? timeout,
    T? Function(dynamic)? fromJsonT,
  }) async {
    try {
      AppLogger.debug('DELETE请求开始: $url', {'headers': headers, 'timeout': timeout?.inMilliseconds});
      
      final uri = Uri.parse(url);
      final requestHeaders = _buildHeaders(headers: headers);
      
      final response = await _client
          .delete(
            uri,
            headers: requestHeaders,
          )
          .timeout(timeout ?? ApiConstants.defaultTimeout);
      
      AppLogger.debug('DELETE请求完成: $url', {
        'statusCode': response.statusCode,
        'responseLength': response.body.length,
      });
      
      return await _handleApiResponse<T>(response, fromJsonT);
    } on SocketException catch (e, stackTrace) {
      AppLogger.error('DELETE请求网络连接失败: $url [SocketException] Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -1,
        message: '网络连接失败，请检查网络设置',
      );
    } on HttpException catch (e, stackTrace) {
      AppLogger.error('DELETE请求HTTP异常: $url [HttpException] Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -2,
        message: 'HTTP请求异常',
      );
    } on TimeoutException catch (e, stackTrace) {
      final timeoutMs = timeout?.inMilliseconds ?? ApiConstants.defaultTimeout.inMilliseconds;
      AppLogger.error('DELETE请求超时: $url [TimeoutException] Timeout: ${timeoutMs}ms', e, stackTrace);
      return ApiResponse<T>.error(
        code: -4,
        message: '请求超时，请稍后重试',
      );
    } catch (e, stackTrace) {
      AppLogger.error('DELETE请求未知异常: $url [${e.runtimeType}] Headers: $headers', e, stackTrace);
      return ApiResponse<T>.error(
        code: -3,
        message: '请求失败: ${e.toString()}',
      );
    }
  }

  /// 处理API响应
  Future<ApiResponse<T>> _handleApiResponse<T>(
    http.Response response,
    T? Function(dynamic)? fromJsonT,
  ) async {
    try {
      AppLogger.debug('处理API响应', {
        'statusCode': response.statusCode,
        'contentLength': response.body.length,
        'contentType': response.headers['content-type'],
      });
      
      final Map<String, dynamic> jsonData = json.decode(utf8.decode(response.bodyBytes));
      
      // 记录响应数据结构
      AppLogger.debug('API响应数据结构', {
        'hasSuccess': jsonData.containsKey('success'),
        'hasData': jsonData.containsKey('data'),
        'hasMessage': jsonData.containsKey('message'),
        'hasError': jsonData.containsKey('error'),
        'dataType': jsonData['data']?.runtimeType.toString(),
      });
      
      // 处理Token过期，尝试刷新Token
      if (response.statusCode == 401 && _refreshToken != null) {
        AppLogger.warning('检测到401未授权响应，尝试刷新Token', {
          'hasRefreshToken': _refreshToken != null,
          'responseMessage': jsonData['message'],
        });
        final refreshResult = await _refreshAccessToken();
        if (refreshResult) {
          AppLogger.info('Token刷新成功，请求需要重试');
          // Token刷新成功，重新发起原请求
          // 这里需要重新构造原请求，暂时返回Token过期错误
          return ApiResponse<T>.error(
            code: 401,
            message: 'Token已刷新，请重试',
          );
        } else {
          AppLogger.error('Token刷新失败，处理Token过期');
          await _handleTokenExpired();
        }
      }
      
      final apiResponse = ApiResponse<T>.fromJson(jsonData, fromJsonT);
      
      // 记录API响应结果
      if (apiResponse.success) {
        AppLogger.info('API请求成功', {
          'statusCode': response.statusCode,
          'message': apiResponse.message,
          'hasData': apiResponse.data != null,
        });
      } else {
        AppLogger.warning('API请求业务失败', {
          'statusCode': response.statusCode,
          'message': apiResponse.message,
          'error': apiResponse.error,
          'code': apiResponse.code,
        });
      }
      
      return apiResponse;
    } catch (e, stackTrace) {
      AppLogger.warning('JSON解析失败，返回原始响应', {
        'statusCode': response.statusCode,
        'responseBody': response.body.length > 1000 ? '${response.body.substring(0, 1000)}...' : response.body,
        'error': e.toString(),
      });
      
      // JSON解析失败，返回原始响应
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return ApiResponse<T>.success(
          code: response.statusCode,
          message: '请求成功',
          data: response.body as T?,
        );
      } else {
        return ApiResponse<T>.error(
          code: response.statusCode,
          message: 'HTTP ${response.statusCode}',
        );
      }
    }
  }

  /// 刷新访问Token
  Future<bool> _refreshAccessToken() async {
    if (_refreshToken == null) {
      AppLogger.warning('刷新Token失败：refresh_token为空');
      return false;
    }
    
    try {
      AppLogger.debug('开始刷新访问Token');
      
      final response = await _client.post(
        Uri.parse('${ApiConstants.baseUrl}/api/v1/auth/refresh'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_refreshToken',
        },
        body: json.encode({'refresh_token': _refreshToken}),
      );
      
      AppLogger.debug('Token刷新响应', {
        'statusCode': response.statusCode,
        'responseLength': response.body.length,
      });
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          final newToken = data['data']['token'];
          final newRefreshToken = data['data']['refresh_token'];
          await setTokens(newToken, newRefreshToken);
          AppLogger.info('Token刷新成功');
          return true;
        } else {
           AppLogger.error('Token刷新失败：响应数据格式错误 Data: $data');
         }
       } else {
         AppLogger.error('Token刷新失败：HTTP状态码错误 StatusCode: ${response.statusCode} Body: ${response.body}');
      }
    } catch (e, stackTrace) {
      AppLogger.error('Token刷新异常', e, stackTrace);
    }
    
    return false;
  }

  /// 处理Token过期
  Future<void> _handleTokenExpired() async {
    await setTokens(null, null);
    // 这里可以添加跳转到登录页面的逻辑
    // 或者发送全局事件通知
  }

  /// 上传文件
  Future<http.StreamedResponse> uploadFile(
    String url,
    String filePath,
    String fieldName, {
    Map<String, String>? fields,
    Map<String, String>? headers,
  }) async {
    try {
      AppLogger.debug('开始上传文件: $url', {
        'filePath': filePath,
        'fieldName': fieldName,
        'fields': fields,
        'headers': headers,
      });
      
      final uri = Uri.parse(url);
      final request = http.MultipartRequest('POST', uri);
      
      // 添加请求头
      request.headers.addAll(_buildHeaders(headers: headers));
      
      // 添加文件
      final file = await http.MultipartFile.fromPath(fieldName, filePath);
      request.files.add(file);
      
      AppLogger.debug('文件信息', {
        'fileName': file.filename,
        'fileSize': file.length,
        'contentType': file.contentType?.toString(),
      });
      
      // 添加其他字段
      if (fields != null) {
        request.fields.addAll(fields);
      }
      
      final response = await request.send();
      
      AppLogger.debug('文件上传完成', {
        'statusCode': response.statusCode,
        'contentLength': response.contentLength,
      });
      
      return response;
    } on SocketException catch (e, stackTrace) {
      AppLogger.error('文件上传网络连接失败: $url [SocketException] FilePath: $filePath', e, stackTrace);
      throw Exception('网络连接失败，请检查网络设置');
    } on FileSystemException catch (e, stackTrace) {
      AppLogger.error('文件系统异常: $url [FileSystemException] FilePath: $filePath', e, stackTrace);
      throw Exception('文件访问失败: ${e.toString()}');
    } catch (e, stackTrace) {
      AppLogger.error('文件上传未知异常: $url [${e.runtimeType}] FilePath: $filePath', e, stackTrace);
      throw Exception('文件上传失败: ${e.toString()}');
    }
  }

  /// 下载文件
  Future<List<int>> downloadFile(String url) async {
    try {
      AppLogger.debug('开始下载文件: $url');
      
      final uri = Uri.parse(url);
      final response = await _client.get(
        uri,
        headers: _buildHeaders(),
      );
      
      AppLogger.debug('文件下载响应', {
        'statusCode': response.statusCode,
        'contentLength': response.contentLength,
        'contentType': response.headers['content-type'],
      });
      
      if (response.statusCode == 200) {
        AppLogger.info('文件下载成功: $url Size: ${response.bodyBytes.length} bytes');
        return response.bodyBytes;
      } else {
        AppLogger.error('文件下载失败: $url HTTP ${response.statusCode} Body: ${response.body}');
        throw Exception('下载失败: HTTP ${response.statusCode}');
      }
    } on SocketException catch (e, stackTrace) {
      AppLogger.error('文件下载网络连接失败: $url [SocketException]', e, stackTrace);
      throw Exception('网络连接失败，请检查网络设置');
    } on TimeoutException catch (e, stackTrace) {
      AppLogger.error('文件下载超时: $url [TimeoutException]', e, stackTrace);
      throw Exception('下载超时，请稍后重试');
    } catch (e, stackTrace) {
      AppLogger.error('文件下载未知异常: $url [${e.runtimeType}]', e, stackTrace);
      throw Exception('文件下载失败: ${e.toString()}');
    }
  }

  /// 释放资源
  void dispose() {
    _client.close();
  }
}