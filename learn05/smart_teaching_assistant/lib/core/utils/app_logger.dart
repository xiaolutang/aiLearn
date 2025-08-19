import 'dart:developer' as developer;
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'error_handler.dart';

/// 日志级别
enum LogLevel {
  debug,
  info,
  warning,
  error,
  fatal,
}

/// 应用日志记录器
class AppLogger {
  static const String _tag = 'SmartTeachingAssistant';
  
  /// 是否启用日志
  static bool _isEnabled = kDebugMode;
  
  /// 设置日志启用状态
  static void setEnabled(bool enabled) {
    _isEnabled = enabled;
  }
  
  /// 记录调试日志
  static void debug(String message, [dynamic error, StackTrace? stackTrace]) {
    _log(LogLevel.debug, message, error, stackTrace);
  }
  
  /// 记录信息日志
  static void info(String message, [dynamic error, StackTrace? stackTrace]) {
    _log(LogLevel.info, message, error, stackTrace);
  }
  
  /// 记录警告日志
  static void warning(String message, [dynamic error, StackTrace? stackTrace]) {
    _log(LogLevel.warning, message, error, stackTrace);
  }
  
  /// 记录错误日志
  static void error(String message, [dynamic error, StackTrace? stackTrace]) {
    _log(LogLevel.error, message, error, stackTrace);
  }
  
  /// 记录致命错误日志
  static void fatal(String message, [dynamic error, StackTrace? stackTrace]) {
    _log(LogLevel.fatal, message, error, stackTrace);
  }
  
  /// 记录API请求
  static void apiRequest(String method, String url, [Map<String, dynamic>? data]) {
    if (!_isEnabled) return;
    
    final message = 'API Request: $method $url';
    if (data != null && data.isNotEmpty) {
      debug('$message\nData: $data');
    } else {
      debug(message);
    }
  }
  
  /// 记录API响应
  static void apiResponse(String method, String url, int statusCode, [dynamic data]) {
    if (!_isEnabled) return;
    
    final message = 'API Response: $method $url [$statusCode]';
    if (data != null) {
      debug('$message\nData: $data');
    } else {
      debug(message);
    }
  }
  
  /// 记录用户操作
  static void userAction(String action, [Map<String, dynamic>? context]) {
    if (!_isEnabled) return;
    
    final message = 'User Action: $action';
    if (context != null && context.isNotEmpty) {
      info('$message\nContext: $context');
    } else {
      info(message);
    }
  }
  
  /// 记录页面导航
  static void navigation(String from, String to, [Map<String, dynamic>? arguments]) {
    if (!_isEnabled) return;
    
    final message = 'Navigation: $from -> $to';
    if (arguments != null && arguments.isNotEmpty) {
      info('$message\nArguments: $arguments');
    } else {
      info(message);
    }
  }
  
  /// 内部日志记录方法
  static void _log(LogLevel level, String message, [dynamic error, StackTrace? stackTrace]) {
    if (!_isEnabled) return;
    
    final timestamp = DateTime.now().toIso8601String();
    final levelStr = level.name.toUpperCase();
    final logMessage = '[$timestamp] [$levelStr] [$_tag] $message';
    
    // 在调试模式下打印到控制台
    if (kDebugMode) {
      // 使用print确保在终端中可见
      print(logMessage);
      if (error != null) {
        print('Error: $error');
      }
      if (stackTrace != null) {
        print('StackTrace: $stackTrace');
      }
      
      // 同时使用developer.log用于DevTools
      switch (level) {
        case LogLevel.debug:
          developer.log(logMessage, name: _tag, level: 500);
          break;
        case LogLevel.info:
          developer.log(logMessage, name: _tag, level: 800);
          break;
        case LogLevel.warning:
          developer.log(logMessage, name: _tag, level: 900);
          break;
        case LogLevel.error:
        case LogLevel.fatal:
          developer.log(
            logMessage,
            name: _tag,
            level: 1000,
            error: error,
            stackTrace: stackTrace,
          );
          break;
      }
    }
    
    // 在生产环境中可以发送到远程日志服务
    if (kReleaseMode && (level == LogLevel.error || level == LogLevel.fatal)) {
      _sendToRemoteLogging(level, message, error, stackTrace);
    }
  }
  
  /// 发送到远程日志服务（生产环境）
  static void _sendToRemoteLogging(LogLevel level, String message, dynamic error, StackTrace? stackTrace) {
    // TODO: 实现远程日志服务集成
    // 例如：Firebase Crashlytics, Sentry, 或自定义日志服务
  }
}

/// 全局错误处理器
class GlobalErrorHandler {
  static BuildContext? _context;
  
  /// 设置全局上下文
  static void setContext(BuildContext context) {
    _context = context;
  }
  
  /// 处理并显示错误
  static void handleError(dynamic error, [StackTrace? stackTrace, bool showToUser = true]) {
    final appException = ErrorHandler.handleError(error, stackTrace);
    
    // 记录错误日志
    AppLogger.error(
      'Global Error: ${appException.message}',
      appException.originalError,
      appException.stackTrace,
    );
    
    // 显示给用户
    if (showToUser) {
      showErrorToUser(appException);
    }
  }
  
  /// 显示错误给用户
  static void showErrorToUser(AppException exception) {
    final message = ErrorHandler.getUserFriendlyMessage(exception);
    
    // 根据错误类型选择不同的显示方式
    if (exception is AuthException) {
      _showAuthErrorDialog(message);
    } else if (exception is ValidationException) {
      _showValidationError(exception);
    } else {
      _showToast(message);
    }
  }
  
  /// 显示认证错误对话框
  static void _showAuthErrorDialog(String message) {
    if (_context == null) {
      _showToast(message);
      return;
    }
    
    showDialog(
      context: _context!,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('认证失败'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              // TODO: 导航到登录页面
            },
            child: const Text('重新登录'),
          ),
        ],
      ),
    );
  }
  
  /// 显示验证错误
  static void _showValidationError(ValidationException exception) {
    AppLogger.warning('GlobalErrorHandler: 显示验证错误', {
      'message': exception.message,
      'hasFieldErrors': exception.fieldErrors != null && exception.fieldErrors!.isNotEmpty,
      'fieldErrorCount': exception.fieldErrors?.length ?? 0,
      'fieldNames': exception.fieldErrors?.keys.toList() ?? []
    });
    
    if (exception.fieldErrors != null && exception.fieldErrors!.isNotEmpty) {
      // 如果有字段错误，显示详细信息
      final errors = exception.fieldErrors!.entries
          .map((e) => '${e.key}: ${e.value.join(', ')}')
          .join('\n');
      _showToast('验证失败:\n$errors');
    } else {
      _showToast(exception.message);
    }
  }
  
  /// 显示Toast消息
  static void _showToast(String message) {
    AppLogger.debug('GlobalErrorHandler: 显示Toast消息', {
      'message': message,
      'messageLength': message.length
    });
    
    // 使用print替代toast，在Web环境下更稳定
    print('ERROR: $message');
  }
  
  /// 显示成功消息
  static void showSuccess(String message) {
    AppLogger.info('GlobalErrorHandler: 显示成功消息', {
      'message': message
    });
    
    // 使用print替代toast，在Web环境下更稳定
    print('SUCCESS: $message');
  }
  
  /// 显示信息消息
  static void showInfo(String message) {
    AppLogger.info('GlobalErrorHandler: 显示信息消息', {
      'message': message
    });
    
    // 使用print替代toast，在Web环境下更稳定
    print('INFO: $message');
  }
  
  /// 显示警告消息
  static void showWarning(String message) {
    AppLogger.warning('GlobalErrorHandler: 显示警告消息', {
      'message': message
    });
    
    // 使用print替代toast，在Web环境下更稳定
    print('WARNING: $message');
  }
}

/// 错误边界Widget
class ErrorBoundary extends StatefulWidget {
  final Widget child;
  final Widget Function(FlutterErrorDetails details)? errorBuilder;
  final void Function(FlutterErrorDetails details)? onError;
  
  const ErrorBoundary({
    Key? key,
    required this.child,
    this.errorBuilder,
    this.onError,
  }) : super(key: key);
  
  @override
  State<ErrorBoundary> createState() => _ErrorBoundaryState();
}

class _ErrorBoundaryState extends State<ErrorBoundary> {
  FlutterErrorDetails? _errorDetails;
  
  @override
  void initState() {
    super.initState();
    
    AppLogger.info('ErrorBoundary: 初始化错误边界组件');
    
    // 设置错误处理器
    FlutterError.onError = (details) {
      AppLogger.fatal('ErrorBoundary: 捕获Flutter错误', {
        'exceptionType': details.exception.runtimeType.toString(),
        'exceptionMessage': details.exception.toString(),
        'library': details.library,
        'context': details.context?.toString(),
        'hasStack': details.stack != null,
        'stackLines': details.stack?.toString().split('\n').length ?? 0
      });
      
      setState(() {
        _errorDetails = details;
      });
      
      // 记录错误
      AppLogger.fatal(
        'Flutter Error: ${details.exception}',
        details.exception,
        details.stack,
      );
      
      // 调用自定义错误处理
      widget.onError?.call(details);
    };
  }
  
  @override
  Widget build(BuildContext context) {
    if (_errorDetails != null) {
      AppLogger.warning('ErrorBoundary: 渲染错误界面', {
        'hasCustomErrorBuilder': widget.errorBuilder != null,
        'exceptionType': _errorDetails!.exception.runtimeType.toString()
      });
      return widget.errorBuilder?.call(_errorDetails!) ?? _buildDefaultErrorWidget();
    }
    
    return widget.child;
  }
  
  Widget _buildDefaultErrorWidget() {
    return Scaffold(
      appBar: AppBar(
        title: const Text('出错了'),
        backgroundColor: Colors.red,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              const Text(
                '应用遇到了一个错误',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                kDebugMode ? _errorDetails!.exception.toString() : '请重启应用或联系技术支持',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 14),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  AppLogger.info('ErrorBoundary: 用户点击重试按钮');
                  setState(() {
                    _errorDetails = null;
                  });
                },
                child: const Text('重试'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}