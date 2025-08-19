import 'package:flutter/foundation.dart';
import '../../models/user_model.dart';
import '../../models/auth_dto.dart';

/// 认证状态
class AuthState {
  final UserModel? user;
  final bool isLoading;
  final bool isLoggedIn;
  final String? error;
  final List<String> permissions;
  
  const AuthState({
    this.user,
    this.isLoading = false,
    this.isLoggedIn = false,
    this.error,
    this.permissions = const [],
  });
  
  AuthState copyWith({
    UserModel? user,
    bool? isLoading,
    bool? isLoggedIn,
    String? error,
    List<String>? permissions,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      error: error,
      permissions: permissions ?? this.permissions,
    );
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AuthState &&
        other.user == user &&
        other.isLoading == isLoading &&
        other.isLoggedIn == isLoggedIn &&
        other.error == error &&
        _listEquals(other.permissions, permissions);
  }
  
  @override
  int get hashCode {
    return user.hashCode ^
        isLoading.hashCode ^
        isLoggedIn.hashCode ^
        error.hashCode ^
        permissions.hashCode;
  }
  
  bool _listEquals<T>(List<T>? a, List<T>? b) {
    if (a == null) return b == null;
    if (b == null || a.length != b.length) return false;
    for (int index = 0; index < a.length; index += 1) {
      if (a[index] != b[index]) return false;
    }
    return true;
  }
}

/// 认证状态管理器
class AuthProvider extends ChangeNotifier {
  AuthState _state = const AuthState();
  
  AuthState get state => _state;
  
  bool get isLoggedIn => _state.isLoggedIn;
  UserModel? get currentUser => _state.user;
  List<String> get permissions => _state.permissions;
  bool get isLoading => _state.isLoading;
  String? get error => _state.error;
  
  void _setState(AuthState newState) {
    _state = newState;
    notifyListeners();
  }
  
  /// 模拟登录
  Future<bool> login({
    required String username,
    required String password,
    bool rememberMe = false,
  }) async {
    try {
      _setState(_state.copyWith(isLoading: true, error: null));
      
      // 模拟网络延迟
      await Future.delayed(const Duration(seconds: 1));
      
      // 模拟登录验证
      if (username.isEmpty || password.isEmpty) {
        throw Exception('用户名和密码不能为空');
      }
      
      if (password.length < 6) {
        throw Exception('密码长度不能少于6位');
      }
      
      // 创建模拟用户
       final user = UserModel(
         id: 1,
         username: username,
         email: '$username@example.com',
         fullName: '测试用户',
         role: UserRole.teacher,
         isActive: true,
         createdAt: DateTime.now(),
         updatedAt: DateTime.now(),
         profile: UserProfile(
           bio: '这是一个测试用户',
           preferences: const {},
         ),
       );
      
      final permissions = ['read', 'write', 'manage_students', 'view_analytics'];
      
      _setState(_state.copyWith(
        user: user,
        isLoggedIn: true,
        permissions: permissions,
        isLoading: false,
      ));
      
      return true;
    } catch (e) {
      _setState(_state.copyWith(
        isLoading: false,
        error: e.toString(),
      ));
      return false;
    }
  }
  
  /// 模拟注册
  Future<bool> register({
    required String username,
    required String email,
    required String password,
    required String fullName,
    required UserRole role,
  }) async {
    try {
      _setState(_state.copyWith(isLoading: true, error: null));
      
      // 模拟网络延迟
      await Future.delayed(const Duration(seconds: 1));
      
      // 模拟注册验证
      if (username.isEmpty || email.isEmpty || password.isEmpty || fullName.isEmpty) {
        throw Exception('所有字段都不能为空');
      }
      
      if (password.length < 6) {
        throw Exception('密码长度不能少于6位');
      }
      
      if (!email.contains('@')) {
        throw Exception('邮箱格式不正确');
      }
      
      // 创建新用户
       final user = UserModel(
         id: DateTime.now().millisecondsSinceEpoch,
         username: username,
         email: email,
         fullName: fullName,
         role: role,
         isActive: true,
         createdAt: DateTime.now(),
         updatedAt: DateTime.now(),
         profile: UserProfile(
           bio: '',
           preferences: const {},
         ),
       );
      
      final permissions = _getPermissionsByRole(role);
      
      _setState(_state.copyWith(
        user: user,
        isLoggedIn: true,
        permissions: permissions,
        isLoading: false,
      ));
      
      return true;
    } catch (e) {
      _setState(_state.copyWith(
        isLoading: false,
        error: e.toString(),
      ));
      return false;
    }
  }
  
  /// 登出
  Future<void> logout() async {
    try {
      _setState(_state.copyWith(isLoading: true, error: null));
      
      // 模拟网络延迟
      await Future.delayed(const Duration(milliseconds: 500));
      
      _setState(const AuthState());
    } catch (e) {
      _setState(_state.copyWith(
        isLoading: false,
        error: e.toString(),
      ));
    }
  }
  
  /// 更新用户信息
  Future<bool> updateUser({
    String? fullName,
    String? email,
    String? bio,
    Map<String, dynamic>? preferences,
  }) async {
    try {
      if (_state.user == null) {
        throw Exception('用户未登录');
      }
      
      _setState(_state.copyWith(isLoading: true, error: null));
      
      // 模拟网络延迟
      await Future.delayed(const Duration(milliseconds: 800));
      
      final updatedUser = _state.user!.copyWith(
        fullName: fullName ?? _state.user!.fullName,
        email: email ?? _state.user!.email,
        updatedAt: DateTime.now(),
        profile: _state.user!.profile?.copyWith(
          bio: bio ?? _state.user!.profile?.bio,
          preferences: preferences ?? _state.user!.profile?.preferences,
        ),
      );
      
      _setState(_state.copyWith(
        user: updatedUser,
        isLoading: false,
      ));
      
      return true;
    } catch (e) {
      _setState(_state.copyWith(
        isLoading: false,
        error: e.toString(),
      ));
      return false;
    }
  }
  
  /// 检查用户名可用性
  Future<bool> checkUsernameAvailability(String username) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 300));
    
    // 基本验证
    if (username.isEmpty || username.length < 3) {
      return false;
    }
    
    // 检查用户名格式（只允许字母、数字、下划线）
    final usernameRegex = RegExp(r'^[a-zA-Z0-9_]+$');
    if (!usernameRegex.hasMatch(username)) {
      return false;
    }
    
    // 模拟已存在的用户名
    final existingUsernames = ['admin', 'test', 'user', 'teacher', 'student'];
    return !existingUsernames.contains(username.toLowerCase());
  }
  
  /// 检查邮箱可用性
  Future<bool> checkEmailAvailability(String email) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 300));
    
    // 基本邮箱格式验证
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(email)) {
      return false;
    }
    
    // 模拟已存在的邮箱
    final existingEmails = [
      'admin@example.com',
      'test@example.com',
      'user@example.com'
    ];
    return !existingEmails.contains(email.toLowerCase());
  }
  
  /// 发送密码重置邮件
  Future<bool> sendPasswordResetEmail(String email) async {
    try {
      _setState(_state.copyWith(isLoading: true, error: null));
      
      // 模拟网络延迟
      await Future.delayed(const Duration(seconds: 1));
      
      // 基本邮箱格式验证
      final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
      if (!emailRegex.hasMatch(email)) {
        throw Exception('邮箱格式不正确');
      }
      
      _setState(_state.copyWith(isLoading: false));
      return true;
    } catch (e) {
      _setState(_state.copyWith(
        isLoading: false,
        error: e.toString(),
      ));
      return false;
    }
  }
  
  /// 发送验证码
  Future<bool> sendVerificationCode({
    required String identifier,
    required VerificationType type,
    required VerificationPurpose purpose,
  }) async {
    try {
      _setState(_state.copyWith(isLoading: true, error: null));
      
      // 模拟网络延迟
      await Future.delayed(const Duration(milliseconds: 800));
      
      // 基本验证
      if (identifier.isEmpty) {
        throw Exception('标识符不能为空');
      }
      
      if (type == VerificationType.email) {
        final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
        if (!emailRegex.hasMatch(identifier)) {
          throw Exception('邮箱格式不正确');
        }
      } else if (type == VerificationType.sms) {
         final phoneRegex = RegExp(r'^1[3-9]\d{9}$');
         if (!phoneRegex.hasMatch(identifier)) {
           throw Exception('手机号格式不正确');
         }
       }
      
      _setState(_state.copyWith(isLoading: false));
      return true;
    } catch (e) {
      _setState(_state.copyWith(
        isLoading: false,
        error: e.toString(),
      ));
      return false;
    }
  }
  
  /// 验证验证码
  Future<bool> verifyCode({
    required String identifier,
    required String code,
    required VerificationType type,
    required VerificationPurpose purpose,
  }) async {
    try {
      _setState(_state.copyWith(isLoading: true, error: null));
      
      // 模拟网络延迟
      await Future.delayed(const Duration(milliseconds: 600));
      
      // 基本验证
      if (code.isEmpty || code.length != 6) {
        throw Exception('验证码必须是6位数字');
      }
      
      if (!RegExp(r'^\d{6}$').hasMatch(code)) {
        throw Exception('验证码只能包含数字');
      }
      
      // 模拟验证码验证（测试用验证码：123456）
      final isValid = code == '123456';
      
      _setState(_state.copyWith(isLoading: false));
      return isValid;
    } catch (e) {
      _setState(_state.copyWith(
        isLoading: false,
        error: e.toString(),
      ));
      return false;
    }
  }
  
  /// 检查权限
  bool hasPermission(String permission) {
    return _state.permissions.contains(permission);
  }
  
  /// 检查角色
  bool hasRole(UserRole role) {
    return _state.user?.role == role;
  }
  
  /// 清除错误信息
  void clearError() {
    _setState(_state.copyWith(error: null));
  }
  
  /// 根据角色获取权限
  List<String> _getPermissionsByRole(UserRole role) {
    switch (role) {
      case UserRole.admin:
        return [
          'read', 'write', 'delete',
          'manage_users', 'manage_classes', 'manage_students',
          'view_analytics', 'export_data', 'system_settings'
        ];
      case UserRole.teacher:
        return [
          'read', 'write',
          'manage_classes', 'manage_students',
          'view_analytics', 'export_data'
        ];
      case UserRole.student:
        return ['read', 'view_own_data'];
      case UserRole.parent:
        return ['read', 'view_child_data'];
    }
  }
}

/// 全局认证提供者实例
final authProvider = AuthProvider();