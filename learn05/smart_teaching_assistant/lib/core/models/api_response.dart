/// 统一API响应格式
class ApiResponse<T> {
  final bool success;
  final int code;
  final String message;
  final T? data;
  final Map<String, dynamic>? error;
  final Map<String, dynamic>? metadata;
  final DateTime timestamp;

  ApiResponse({
    required this.success,
    required this.code,
    required this.message,
    this.data,
    this.error,
    this.metadata,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  /// 成功响应构造函数
  factory ApiResponse.success({
    T? data,
    String message = '操作成功',
    int code = 200,
    Map<String, dynamic>? metadata,
  }) {
    return ApiResponse<T>(
      success: true,
      code: code,
      message: message,
      data: data,
      metadata: metadata,
    );
  }

  /// 错误响应构造函数
  factory ApiResponse.error({
    required String message,
    int code = 400,
    Map<String, dynamic>? error,
    Map<String, dynamic>? metadata,
  }) {
    return ApiResponse<T>(
      success: false,
      code: code,
      message: message,
      error: error,
      metadata: metadata,
    );
  }

  /// 网络错误响应构造函数
  factory ApiResponse.networkError({
    String message = '网络连接失败',
  }) {
    return ApiResponse<T>(
      success: false,
      code: -1,
      message: message,
      error: {'type': 'network_error'},
    );
  }

  /// 服务器错误响应构造函数
  factory ApiResponse.serverError({
    String message = '服务器内部错误',
    int code = 500,
  }) {
    return ApiResponse<T>(
      success: false,
      code: code,
      message: message,
      error: {'type': 'server_error'},
    );
  }

  /// 认证错误响应构造函数
  factory ApiResponse.authError({
    String message = '认证失败',
    int code = 401,
  }) {
    return ApiResponse<T>(
      success: false,
      code: code,
      message: message,
      error: {'type': 'auth_error'},
    );
  }

  /// 验证错误响应构造函数
  factory ApiResponse.validationError({
    String message = '数据验证失败',
    Map<String, dynamic>? error,
  }) {
    return ApiResponse<T>(
      success: false,
      code: 422,
      message: message,
      error: error ?? {'type': 'validation_error'},
    );
  }

  /// 从JSON创建响应对象
  factory ApiResponse.fromJson(
    Map<String, dynamic> json, 
    T? Function(dynamic)? fromJsonT,
  ) {
    return ApiResponse<T>(
      success: json['success'] ?? false,
      code: json['code'] ?? 0,
      message: json['message'] ?? '',
      data: json['data'] != null && fromJsonT != null 
          ? fromJsonT(json['data']) 
          : json['data'],
      error: json['error'],
      metadata: json['metadata'],
      timestamp: json['timestamp'] != null 
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson([Map<String, dynamic>? Function(T)? toJsonT]) {
    return {
      'success': success,
      'code': code,
      'message': message,
      'data': data != null && toJsonT != null ? toJsonT(data as T) : data,
      'error': error,
      'metadata': metadata,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  /// 错误类型判断
  bool get isNetworkError => code == -1;
  bool get isServerError => code >= 500;
  bool get isClientError => code >= 400 && code < 500;
  bool get isAuthError => code == 401 || code == 403;
  bool get isValidationError => code == 422;
  bool get isNotFound => code == 404;
  bool get isForbidden => code == 403;
  bool get isUnauthorized => code == 401;
  bool get isBadRequest => code == 400;

  /// 复制并修改响应
  ApiResponse<R> copyWith<R>({
    bool? success,
    int? code,
    String? message,
    R? data,
    Map<String, dynamic>? error,
    Map<String, dynamic>? metadata,
    DateTime? timestamp,
  }) {
    return ApiResponse<R>(
      success: success ?? this.success,
      code: code ?? this.code,
      message: message ?? this.message,
      data: data ?? (this.data as R?),
      error: error ?? this.error,
      metadata: metadata ?? this.metadata,
      timestamp: timestamp ?? this.timestamp,
    );
  }

  /// 转换数据类型
  ApiResponse<R> transform<R>(R? Function(T?) transformer) {
    return ApiResponse<R>(
      success: success,
      code: code,
      message: message,
      data: transformer(data),
      error: error,
      metadata: metadata,
      timestamp: timestamp,
    );
  }

  /// 获取错误详情
  String get errorDetail {
    if (error != null) {
      if (error!['detail'] != null) {
        return error!['detail'].toString();
      }
      if (error!['message'] != null) {
        return error!['message'].toString();
      }
      return error.toString();
    }
    return message;
  }

  /// 获取用户友好的错误信息
  String get userFriendlyMessage {
    if (isNetworkError) {
      return '网络连接失败，请检查网络设置';
    }
    if (isServerError) {
      return '服务器暂时不可用，请稍后重试';
    }
    if (isAuthError) {
      return '登录已过期，请重新登录';
    }
    if (isValidationError) {
      return '输入信息有误，请检查后重试';
    }
    if (isNotFound) {
      return '请求的资源不存在';
    }
    if (isForbidden) {
      return '没有权限执行此操作';
    }
    return message.isNotEmpty ? message : '操作失败，请重试';
  }

  @override
  String toString() {
    return 'ApiResponse{success: $success, code: $code, message: $message, data: $data, error: $error}';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ApiResponse<T> &&
        other.success == success &&
        other.code == code &&
        other.message == message &&
        other.data == data;
  }

  @override
  int get hashCode {
    return success.hashCode ^
        code.hashCode ^
        message.hashCode ^
        data.hashCode;
  }
}

/// 分页响应模型
class PaginatedResponse<T> {
  final List<T> items;
  final int total;
  final int page;
  final int pageSize;
  final int totalPages;
  final bool hasNext;
  final bool hasPrevious;

  /// 数据列表的别名，与items相同
  List<T> get data => items;

  PaginatedResponse({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.totalPages,
    required this.hasNext,
    required this.hasPrevious,
  });

  factory PaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) fromJsonT,
  ) {
    final itemsList = json['items'] as List? ?? [];
    return PaginatedResponse<T>(
      items: itemsList.map((item) => fromJsonT(item as Map<String, dynamic>)).toList(),
      total: json['total'] ?? 0,
      page: json['page'] ?? 1,
      pageSize: json['page_size'] ?? 10,
      totalPages: json['total_pages'] ?? 0,
      hasNext: json['has_next'] ?? false,
      hasPrevious: json['has_previous'] ?? false,
    );
  }

  Map<String, dynamic> toJson(Map<String, dynamic> Function(T) toJsonT) {
    return {
      'items': items.map((item) => toJsonT(item)).toList(),
      'total': total,
      'page': page,
      'page_size': pageSize,
      'total_pages': totalPages,
      'has_next': hasNext,
      'has_previous': hasPrevious,
    };
  }

  /// 是否为空
  bool get isEmpty => items.isEmpty;

  /// 是否不为空
  bool get isNotEmpty => items.isNotEmpty;

  /// 获取分页信息文本
  String get paginationInfo {
    final start = (page - 1) * pageSize + 1;
    final end = (start + items.length - 1).clamp(start, total);
    return '第 $start-$end 项，共 $total 项';
  }

  @override
  String toString() {
    return 'PaginatedResponse{items: ${items.length}, total: $total, page: $page, pageSize: $pageSize}';
  }
}