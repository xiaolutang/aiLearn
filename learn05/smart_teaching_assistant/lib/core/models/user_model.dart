/// 用户模型类
class User {
  final String id;
  final String name;
  final String email;
  final String? avatar;
  final String role; // teacher, admin
  final DateTime createdAt;
  final DateTime? updatedAt;
  final Map<String, dynamic>? profile;

  const User({
    required this.id,
    required this.name,
    required this.email,
    this.avatar,
    required this.role,
    required this.createdAt,
    this.updatedAt,
    this.profile,
  });

  /// 从JSON创建User对象
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'].toString(),
      name: json['name']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      avatar: json['avatar']?.toString(),
      role: json['role']?.toString() ?? 'teacher',
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at'].toString()) 
          : DateTime.now(),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at'].toString()) 
          : null,
      profile: json['profile'] is Map<String, dynamic> 
          ? json['profile'] as Map<String, dynamic> 
          : null,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'avatar': avatar,
      'role': role,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'profile': profile,
    };
  }

  /// 复制并更新部分字段
  User copyWith({
    String? id,
    String? name,
    String? email,
    String? avatar,
    String? role,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? profile,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      avatar: avatar ?? this.avatar,
      role: role ?? this.role,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      profile: profile ?? this.profile,
    );
  }

  /// 获取用户显示名称
  String get displayName => name.isNotEmpty ? name : email;

  /// 检查是否为管理员
  bool get isAdmin => role == 'admin';

  /// 检查是否为教师
  bool get isTeacher => role == 'teacher';

  /// 获取头像URL或默认头像
  String get avatarUrl {
    if (avatar != null && avatar!.isNotEmpty) {
      return avatar!;
    }
    // 返回默认头像URL或生成基于用户名的头像
    return 'https://ui-avatars.com/api/?name=${Uri.encodeComponent(displayName)}&background=6366f1&color=fff';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'User(id: $id, name: $name, email: $email, role: $role)';
  }
}

/// 用户登录请求模型
class LoginRequest {
  final String username;
  final String password;
  final bool? rememberMe;

  const LoginRequest({
    required this.username,
    required this.password,
    this.rememberMe,
  });

  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'password': password,
      if (rememberMe != null) 'remember_me': rememberMe,
    };
  }
}

/// 用户注册请求模型
class RegisterRequest {
  final String name;
  final String email;
  final String password;
  final String? role;

  const RegisterRequest({
    required this.name,
    required this.email,
    required this.password,
    this.role,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'email': email,
      'password': password,
      'role': role ?? 'teacher',
    };
  }
}

/// 认证响应模型
class AuthResponse {
  final bool success;
  final String? message;
  final User? user;
  final String? token;
  final Map<String, dynamic>? errors;

  const AuthResponse({
    required this.success,
    this.message,
    this.user,
    this.token,
    this.errors,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      success: json['success'] as bool? ?? false,
      message: json['message'] as String?,
      user: json['user'] != null ? User.fromJson(json['user']) : null,
      token: json['token'] as String?,
      errors: json['errors'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'message': message,
      'user': user?.toJson(),
      'token': token,
      'errors': errors,
    };
  }
}