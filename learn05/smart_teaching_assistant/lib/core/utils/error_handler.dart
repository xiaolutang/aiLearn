import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'app_logger.dart';

/// 应用异常基类
abstract class AppException implements Exception {
  final String message;
  final String? code;
  final dynamic originalError;
  final StackTrace? stackTrace;

  const AppException({
    required this.message,
    this.code,
    this.originalError,
    this.stackTrace,
  });

  @override
  String toString() => 'AppException: $message';
}

/// 网络异常
class NetworkException extends AppException {
  const NetworkException({
    required String message,
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
          message: message,
          code: code,
          originalError: originalError,
          stackTrace: stackTrace,
        );
}

/// 服务器异常
class ServerException extends AppException {
  final int? statusCode;
  final Map<String, dynamic>? errorData;

  const ServerException({
    required String message,
    String? code,
    this.statusCode,
    this.errorData,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
          message: message,
          code: code,
          originalError: originalError,
          stackTrace: stackTrace,
        );
}

/// 认证异常
class AuthException extends AppException {
  const AuthException({
    required String message,
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
          message: message,
          code: code,
          originalError: originalError,
          stackTrace: stackTrace,
        );
}

/// 业务逻辑异常
class BusinessException extends AppException {
  final Map<String, dynamic>? details;

  const BusinessException({
    required String message,
    String? code,
    this.details,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
          message: message,
          code: code,
          originalError: originalError,
          stackTrace: stackTrace,
        );
}

/// 验证异常
class ValidationException extends AppException {
  final Map<String, List<String>>? fieldErrors;

  const ValidationException({
    required String message,
    String? code,
    this.fieldErrors,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
          message: message,
          code: code,
          originalError: originalError,
          stackTrace: stackTrace,
        );
}

/// 缓存异常
class CacheException extends AppException {
  const CacheException({
    required String message,
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
          message: message,
          code: code,
          originalError: originalError,
          stackTrace: stackTrace,
        );
}

/// 文件操作异常
class FileException extends AppException {
  const FileException({
    required String message,
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
          message: message,
          code: code,
          originalError: originalError,
          stackTrace: stackTrace,
        );
}

/// 错误处理器
class ErrorHandler {
  /// 处理异常并转换为AppException
  static AppException handleError(dynamic error, [StackTrace? stackTrace]) {
    AppLogger.debug('ErrorHandler: 开始处理异常', {
      'errorType': error.runtimeType.toString(),
      'errorMessage': error.toString(),
      'hasStackTrace': stackTrace != null
    });

    if (error is AppException) {
      AppLogger.debug('ErrorHandler: 异常已是AppException类型', {
        'code': error.code,
        'message': error.message
      });
      return error;
    }

    if (error is DioError) {
      AppLogger.info('ErrorHandler: 处理Dio网络异常', {
        'dioErrorType': error.type.toString(),
        'statusCode': error.response?.statusCode,
        'requestPath': error.requestOptions.path
      });
      return _handleDioError(error, stackTrace);
    }

    if (error is SocketException) {
      AppLogger.warning('ErrorHandler: 处理Socket网络异常', {
        'address': error.address?.toString(),
        'port': error.port,
        'osError': error.osError?.toString()
      });
      return NetworkException(
        message: '网络连接失败，请检查网络设置',
        code: 'NETWORK_ERROR',
        originalError: error,
        stackTrace: stackTrace,
      );
    }

    if (error is HttpException) {
      AppLogger.warning('ErrorHandler: 处理HTTP异常', {
        'message': error.message,
        'uri': error.uri?.toString()
      });
      return NetworkException(
        message: 'HTTP请求失败: ${error.message}',
        code: 'HTTP_ERROR',
        originalError: error,
        stackTrace: stackTrace,
      );
    }

    if (error is FormatException) {
      AppLogger.warning('ErrorHandler: 处理数据格式异常', {
        'message': error.message,
        'source': error.source,
        'offset': error.offset
      });
      return BusinessException(
        message: '数据格式错误: ${error.message}',
        code: 'FORMAT_ERROR',
        originalError: error,
        stackTrace: stackTrace,
      );
    }

    // 未知错误
    AppLogger.error('ErrorHandler: 处理未知类型异常', error, stackTrace);
    return BusinessException(
      message: '发生未知错误: ${error.toString()}',
      code: 'UNKNOWN_ERROR',
      originalError: error,
      stackTrace: stackTrace,
    );
  }

  /// 处理Dio异常
  static AppException _handleDioError(DioError error, [StackTrace? stackTrace]) {
    final requestInfo = {
      'method': error.requestOptions.method,
      'path': error.requestOptions.path,
      'baseUrl': error.requestOptions.baseUrl,
      'connectTimeout': error.requestOptions.connectTimeout,
      'receiveTimeout': error.requestOptions.receiveTimeout,
      'sendTimeout': error.requestOptions.sendTimeout
    };

    switch (error.type) {
      case DioErrorType.connectTimeout:
        AppLogger.warning('ErrorHandler: 连接超时异常', requestInfo);
        return NetworkException(
          message: '连接超时，请检查网络连接',
          code: 'CONNECTION_TIMEOUT',
          originalError: error,
          stackTrace: stackTrace,
        );

      case DioErrorType.sendTimeout:
        AppLogger.warning('ErrorHandler: 发送超时异常', requestInfo);
        return NetworkException(
          message: '请求发送超时',
          code: 'SEND_TIMEOUT',
          originalError: error,
          stackTrace: stackTrace,
        );

      case DioErrorType.receiveTimeout:
        AppLogger.warning('ErrorHandler: 接收超时异常', requestInfo);
        return NetworkException(
          message: '响应接收超时',
          code: 'RECEIVE_TIMEOUT',
          originalError: error,
          stackTrace: stackTrace,
        );

      case DioErrorType.response:
        AppLogger.warning('ErrorHandler: HTTP响应异常', {
          ...requestInfo,
          'statusCode': error.response?.statusCode,
          'statusMessage': error.response?.statusMessage,
          'responseHeaders': error.response?.headers.map.toString(),
          'responseData': error.response?.data.toString()
        });
        return _handleResponseError(error, stackTrace);

      case DioErrorType.cancel:
        AppLogger.debug('ErrorHandler: 请求取消异常', requestInfo);
        return NetworkException(
          message: '请求已取消',
          code: 'REQUEST_CANCELLED',
          originalError: error,
          stackTrace: stackTrace,
        );

      case DioErrorType.other:
      default:
        AppLogger.error('ErrorHandler: 其他Dio异常', error, stackTrace);
        if (error.error is SocketException) {
          return NetworkException(
            message: '网络连接错误，请检查网络设置',
            code: 'CONNECTION_ERROR',
            originalError: error,
            stackTrace: stackTrace,
          );
        } else if (error.message?.contains('certificate') == true) {
          return NetworkException(
            message: 'SSL证书验证失败',
            code: 'BAD_CERTIFICATE',
            originalError: error,
            stackTrace: stackTrace,
          );
        } else {
          return NetworkException(
            message: '网络请求失败: ${error.message}',
            code: 'UNKNOWN_NETWORK_ERROR',
            originalError: error,
            stackTrace: stackTrace,
          );
        }
    }
  }

  /// 处理HTTP响应错误
  static AppException _handleResponseError(DioError error, [StackTrace? stackTrace]) {
    final response = error.response;
    final statusCode = response?.statusCode;
    final data = response?.data;

    AppLogger.warning('ErrorHandler: 开始处理HTTP响应错误', {
      'statusCode': statusCode,
      'requestPath': error.requestOptions.path,
      'requestMethod': error.requestOptions.method,
      'responseDataType': data.runtimeType.toString(),
      'responseSize': data.toString().length
    });

    String message = '服务器错误';
    String? code;
    Map<String, dynamic>? errorData;

    // 尝试解析错误信息
    if (data is Map<String, dynamic>) {
      message = data['message'] ?? data['error'] ?? message;
      code = data['code']?.toString();
      errorData = data;
      
      AppLogger.debug('ErrorHandler: 解析响应错误数据', {
        'parsedMessage': message,
        'parsedCode': code,
        'errorDataKeys': errorData.keys.toList()
      });
    }

    switch (statusCode) {
      case 400:
        AppLogger.warning('ErrorHandler: 400 请求参数错误', {
          'message': message,
          'code': code,
          'fieldErrors': _extractFieldErrors(data)
        });
        return ValidationException(
          message: message.isEmpty ? '请求参数错误' : message,
          code: code ?? 'BAD_REQUEST',
          fieldErrors: _extractFieldErrors(data),
          originalError: error,
          stackTrace: stackTrace,
        );

      case 401:
        AppLogger.warning('ErrorHandler: 401 认证失败', {
          'message': message,
          'code': code,
          'requestPath': error.requestOptions.path
        });
        return AuthException(
          message: message.isEmpty ? '认证失败，请重新登录' : message,
          code: code ?? 'UNAUTHORIZED',
          originalError: error,
          stackTrace: stackTrace,
        );

      case 403:
        AppLogger.warning('ErrorHandler: 403 权限不足', {
          'message': message,
          'code': code,
          'requestPath': error.requestOptions.path
        });
        return AuthException(
          message: message.isEmpty ? '权限不足，无法访问' : message,
          code: code ?? 'FORBIDDEN',
          originalError: error,
          stackTrace: stackTrace,
        );

      case 404:
        AppLogger.warning('ErrorHandler: 404 资源不存在', {
          'message': message,
          'code': code,
          'requestPath': error.requestOptions.path
        });
        return BusinessException(
          message: message.isEmpty ? '请求的资源不存在' : message,
          code: code ?? 'NOT_FOUND',
          originalError: error,
          stackTrace: stackTrace,
        );

      case 422:
        AppLogger.warning('ErrorHandler: 422 数据验证失败', {
          'message': message,
          'code': code,
          'fieldErrors': _extractFieldErrors(data)
        });
        return ValidationException(
          message: message.isEmpty ? '数据验证失败' : message,
          code: code ?? 'VALIDATION_ERROR',
          fieldErrors: _extractFieldErrors(data),
          originalError: error,
          stackTrace: stackTrace,
        );

      case 429:
        AppLogger.warning('ErrorHandler: 429 请求过于频繁', {
          'message': message,
          'code': code,
          'requestPath': error.requestOptions.path
        });
        return NetworkException(
          message: message.isEmpty ? '请求过于频繁，请稍后再试' : message,
          code: code ?? 'TOO_MANY_REQUESTS',
          originalError: error,
          stackTrace: stackTrace,
        );

      case 500:
        AppLogger.error('ErrorHandler: 500 服务器内部错误', {
          'message': message,
          'code': code,
          'statusCode': statusCode,
          'requestPath': error.requestOptions.path,
          'errorDataKeys': errorData?.keys.toList()
        });
        return ServerException(
          message: message.isEmpty ? '服务器内部错误' : message,
          code: code ?? 'INTERNAL_SERVER_ERROR',
          statusCode: statusCode,
          errorData: errorData,
          originalError: error,
          stackTrace: stackTrace,
        );

      case 502:
        AppLogger.error('ErrorHandler: 502 网关错误', {
          'message': message,
          'code': code,
          'statusCode': statusCode,
          'requestPath': error.requestOptions.path
        });
        return ServerException(
          message: message.isEmpty ? '网关错误' : message,
          code: code ?? 'BAD_GATEWAY',
          statusCode: statusCode,
          errorData: errorData,
          originalError: error,
          stackTrace: stackTrace,
        );

      case 503:
        AppLogger.error('ErrorHandler: 503 服务暂时不可用', {
          'message': message,
          'code': code,
          'statusCode': statusCode,
          'requestPath': error.requestOptions.path
        });
        return ServerException(
          message: message.isEmpty ? '服务暂时不可用' : message,
          code: code ?? 'SERVICE_UNAVAILABLE',
          statusCode: statusCode,
          errorData: errorData,
          originalError: error,
          stackTrace: stackTrace,
        );

      default:
        AppLogger.error('ErrorHandler: 未知HTTP状态码错误', {
          'message': message,
          'code': code,
          'statusCode': statusCode,
          'requestPath': error.requestOptions.path,
          'errorDataKeys': errorData?.keys.toList()
        });
        return ServerException(
          message: message.isEmpty ? '服务器错误 ($statusCode)' : message,
          code: code ?? 'SERVER_ERROR',
          statusCode: statusCode,
          errorData: errorData,
          originalError: error,
          stackTrace: stackTrace,
        );
    }
  }

  /// 提取字段验证错误
  static Map<String, List<String>>? _extractFieldErrors(dynamic data) {
    AppLogger.debug('ErrorHandler: 开始提取字段验证错误', {
      'dataType': data.runtimeType.toString(),
      'dataIsMap': data is Map<String, dynamic>
    });
    
    if (data is! Map<String, dynamic>) {
      AppLogger.debug('ErrorHandler: 数据不是Map类型，无法提取字段错误');
      return null;
    }

    final errors = data['errors'] ?? data['field_errors'];
    if (errors is! Map<String, dynamic>) {
      AppLogger.debug('ErrorHandler: 未找到有效的字段错误数据', {
        'errorsType': errors.runtimeType.toString(),
        'hasErrors': data.containsKey('errors'),
        'hasFieldErrors': data.containsKey('field_errors')
      });
      return null;
    }

    final fieldErrors = <String, List<String>>{};
    errors.forEach((key, value) {
      if (value is List) {
        fieldErrors[key] = value.map((e) => e.toString()).toList();
      } else if (value is String) {
        fieldErrors[key] = [value];
      }
    });

    AppLogger.debug('ErrorHandler: 字段错误提取完成', {
      'fieldCount': fieldErrors.length,
      'fields': fieldErrors.keys.toList()
    });

    return fieldErrors.isEmpty ? null : fieldErrors;
  }

  /// 记录错误日志
  static void logError(AppException exception) {
    AppLogger.error('ErrorHandler: 应用异常详情', {
      'exceptionType': exception.runtimeType.toString(),
      'message': exception.message,
      'code': exception.code,
      'hasOriginalError': exception.originalError != null,
      'hasStackTrace': exception.stackTrace != null,
      'originalErrorType': exception.originalError?.runtimeType.toString(),
      'originalErrorMessage': exception.originalError?.toString()
    });
    
    if (kDebugMode) {
      print('=== Error Log ===');
      print('Type: ${exception.runtimeType}');
      print('Message: ${exception.message}');
      print('Code: ${exception.code}');
      if (exception.originalError != null) {
        print('Original Error: ${exception.originalError}');
      }
      if (exception.stackTrace != null) {
        print('Stack Trace: ${exception.stackTrace}');
      }
      print('================');
    }
  }

  /// 获取用户友好的错误消息
  static String getUserFriendlyMessage(AppException exception) {
    String friendlyMessage;
    
    switch (exception.runtimeType) {
      case NetworkException:
        friendlyMessage = '网络连接异常，请检查网络设置后重试';
        break;
      case AuthException:
        friendlyMessage = '登录状态已过期，请重新登录';
        break;
      case ValidationException:
        friendlyMessage = exception.message;
        break;
      case ServerException:
        friendlyMessage = '服务器暂时无法响应，请稍后重试';
        break;
      case BusinessException:
        friendlyMessage = exception.message;
        break;
      case CacheException:
        friendlyMessage = '数据缓存异常，请清除缓存后重试';
        break;
      case FileException:
        friendlyMessage = '文件操作失败，请检查存储权限';
        break;
      default:
        friendlyMessage = '操作失败，请稍后重试';
        break;
    }
    
    AppLogger.debug('ErrorHandler: 生成用户友好错误消息', {
      'exceptionType': exception.runtimeType.toString(),
      'originalMessage': exception.message,
      'friendlyMessage': friendlyMessage
    });
    
    return friendlyMessage;
  }
}

/// 错误处理结果
class ErrorResult<T> {
  final T? data;
  final AppException? error;
  final bool isSuccess;

  const ErrorResult.success(this.data)
      : error = null,
        isSuccess = true;

  const ErrorResult.failure(this.error)
      : data = null,
        isSuccess = false;

  /// 是否失败
  bool get isFailure => !isSuccess;

  /// 获取数据或抛出异常
  T get dataOrThrow {
    if (isSuccess && data != null) {
      return data!;
    }
    throw error ?? BusinessException(message: '未知错误');
  }

  /// 映射数据
  ErrorResult<R> map<R>(R Function(T data) mapper) {
    if (isSuccess && data != null) {
      try {
        return ErrorResult.success(mapper(data!));
      } catch (e, stackTrace) {
        return ErrorResult.failure(ErrorHandler.handleError(e, stackTrace));
      }
    }
    return ErrorResult.failure(error!);
  }

  /// 处理结果
  R fold<R>(
    R Function(T data) onSuccess,
    R Function(AppException error) onFailure,
  ) {
    if (isSuccess && data != null) {
      return onSuccess(data!);
    }
    return onFailure(error!);
  }
}