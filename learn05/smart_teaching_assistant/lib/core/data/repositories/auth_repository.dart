import '../datasources/local_data_source.dart';
import '../datasources/remote_data_source.dart';
import '../../models/api_response.dart';
import '../../services/connectivity_service.dart';
import '../../utils/app_logger.dart';
import 'base_repository.dart';

/// 用户数据模型
class User {
  final String id;
  final String username;
  final String email;
  final String? phone;
  final String role;
  final String? avatar;
  final String? realName;
  final String? school;
  final String? department;
  final String? title;
  final Map<String, dynamic>? profile;
  final List<String> permissions;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final DateTime? lastLoginAt;
  final bool isActive;
  final bool isVerified;

  User({
    required this.id,
    required this.username,
    required this.email,
    this.phone,
    required this.role,
    this.avatar,
    this.realName,
    this.school,
    this.department,
    this.title,
    this.profile,
    required this.permissions,
    required this.createdAt,
    this.updatedAt,
    this.lastLoginAt,
    this.isActive = true,
    this.isVerified = false,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'],
      role: json['role'] ?? 'student',
      avatar: json['avatar'],
      realName: json['real_name'],
      school: json['school'],
      department: json['department'],
      title: json['title'],
      profile: json['profile'] as Map<String, dynamic>?,
      permissions: List<String>.from(json['permissions'] ?? []),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      lastLoginAt: json['last_login_at'] != null ? DateTime.parse(json['last_login_at']) : null,
      isActive: json['is_active'] ?? true,
      isVerified: json['is_verified'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'phone': phone,
      'role': role,
      'avatar': avatar,
      'real_name': realName,
      'school': school,
      'department': department,
      'title': title,
      'profile': profile,
      'permissions': permissions,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'last_login_at': lastLoginAt?.toIso8601String(),
      'is_active': isActive,
      'is_verified': isVerified,
    };
  }

  User copyWith({
    String? id,
    String? username,
    String? email,
    String? phone,
    String? role,
    String? avatar,
    String? realName,
    String? school,
    String? department,
    String? title,
    Map<String, dynamic>? profile,
    List<String>? permissions,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? lastLoginAt,
    bool? isActive,
    bool? isVerified,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      role: role ?? this.role,
      avatar: avatar ?? this.avatar,
      realName: realName ?? this.realName,
      school: school ?? this.school,
      department: department ?? this.department,
      title: title ?? this.title,
      profile: profile ?? this.profile,
      permissions: permissions ?? this.permissions,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
    );
  }

  /// 检查是否有指定权限
  bool hasPermission(String permission) {
    return permissions.contains(permission) || permissions.contains('*');
  }

  /// 检查是否是教师
  bool get isTeacher => role == 'teacher' || role == 'admin';

  /// 检查是否是学生
  bool get isStudent => role == 'student';

  /// 检查是否是管理员
  bool get isAdmin => role == 'admin';

  @override
  String toString() {
    return 'User{id: $id, username: $username, role: $role, isActive: $isActive}';
  }
}

/// 登录请求数据模型
class LoginRequest {
  final String identifier; // 用户名、邮箱或手机号
  final String password;
  final String? captcha;
  final String? captchaKey;
  final bool rememberMe;
  final String? deviceId;
  final String? deviceInfo;

  LoginRequest({
    required this.identifier,
    required this.password,
    this.captcha,
    this.captchaKey,
    this.rememberMe = false,
    this.deviceId,
    this.deviceInfo,
  });

  Map<String, dynamic> toJson() {
    return {
      'identifier': identifier,
      'password': password,
      if (captcha != null) 'captcha': captcha,
      if (captchaKey != null) 'captcha_key': captchaKey,
      'remember_me': rememberMe,
      if (deviceId != null) 'device_id': deviceId,
      if (deviceInfo != null) 'device_info': deviceInfo,
    };
  }
}

/// 注册请求数据模型
class RegisterRequest {
  final String username;
  final String email;
  final String password;
  final String confirmPassword;
  final String? phone;
  final String role;
  final String? realName;
  final String? school;
  final String? department;
  final String? inviteCode;
  final String? captcha;
  final String? captchaKey;

  RegisterRequest({
    required this.username,
    required this.email,
    required this.password,
    required this.confirmPassword,
    this.phone,
    this.role = 'student',
    this.realName,
    this.school,
    this.department,
    this.inviteCode,
    this.captcha,
    this.captchaKey,
  });

  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
      if (phone != null) 'phone': phone,
      'role': role,
      if (realName != null) 'real_name': realName,
      if (school != null) 'school': school,
      if (department != null) 'department': department,
      if (inviteCode != null) 'invite_code': inviteCode,
      if (captcha != null) 'captcha': captcha,
      if (captchaKey != null) 'captcha_key': captchaKey,
    };
  }
}

/// 认证响应数据模型
class AuthResponse {
  final User user;
  final String accessToken;
  final String refreshToken;
  final DateTime expiresAt;
  final Map<String, dynamic>? metadata;

  AuthResponse({
    required this.user,
    required this.accessToken,
    required this.refreshToken,
    required this.expiresAt,
    this.metadata,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      user: User.fromJson(json['user'] as Map<String, dynamic>),
      accessToken: json['access_token'] ?? '',
      refreshToken: json['refresh_token'] ?? '',
      expiresAt: DateTime.parse(json['expires_at'] ?? DateTime.now().add(Duration(hours: 24)).toIso8601String()),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user': user.toJson(),
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'expires_at': expiresAt.toIso8601String(),
      'metadata': metadata,
    };
  }

  /// 检查Token是否即将过期（30分钟内）
  bool get isTokenExpiringSoon {
    final now = DateTime.now();
    final thirtyMinutesFromNow = now.add(Duration(minutes: 30));
    return expiresAt.isBefore(thirtyMinutesFromNow);
  }

  /// 检查Token是否已过期
  bool get isTokenExpired {
    return expiresAt.isBefore(DateTime.now());
  }
}

/// 密码重置请求数据模型
class PasswordResetRequest {
  final String email;
  final String? captcha;
  final String? captchaKey;

  PasswordResetRequest({
    required this.email,
    this.captcha,
    this.captchaKey,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      if (captcha != null) 'captcha': captcha,
      if (captchaKey != null) 'captcha_key': captchaKey,
    };
  }
}

/// 密码更新请求数据模型
class PasswordUpdateRequest {
  final String currentPassword;
  final String newPassword;
  final String confirmPassword;

  PasswordUpdateRequest({
    required this.currentPassword,
    required this.newPassword,
    required this.confirmPassword,
  });

  Map<String, dynamic> toJson() {
    return {
      'current_password': currentPassword,
      'new_password': newPassword,
      'confirm_password': confirmPassword,
    };
  }
}

/// 用户资料更新请求数据模型
class ProfileUpdateRequest {
  final String? realName;
  final String? phone;
  final String? avatar;
  final String? school;
  final String? department;
  final String? title;
  final Map<String, dynamic>? profile;

  ProfileUpdateRequest({
    this.realName,
    this.phone,
    this.avatar,
    this.school,
    this.department,
    this.title,
    this.profile,
  });

  Map<String, dynamic> toJson() {
    final json = <String, dynamic>{};
    if (realName != null) json['real_name'] = realName;
    if (phone != null) json['phone'] = phone;
    if (avatar != null) json['avatar'] = avatar;
    if (school != null) json['school'] = school;
    if (department != null) json['department'] = department;
    if (title != null) json['title'] = title;
    if (profile != null) json['profile'] = profile;
    return json;
  }
}

/// 认证仓库接口
abstract class AuthRepository {
  /// 用户登录
  Future<ApiResponse<AuthResponse>> login(LoginRequest request);

  /// 用户注册
  Future<ApiResponse<AuthResponse>> register(RegisterRequest request);

  /// 用户登出
  Future<ApiResponse<bool>> logout();

  /// 刷新Token
  Future<ApiResponse<AuthResponse>> refreshToken();

  /// 获取当前用户信息
  Future<ApiResponse<User>> getCurrentUser({bool forceRefresh = false});

  /// 更新用户资料
  Future<ApiResponse<User>> updateProfile(ProfileUpdateRequest request);

  /// 更新密码
  Future<ApiResponse<bool>> updatePassword(PasswordUpdateRequest request);

  /// 发送密码重置邮件
  Future<ApiResponse<bool>> sendPasswordResetEmail(PasswordResetRequest request);

  /// 重置密码
  Future<ApiResponse<bool>> resetPassword(String token, String newPassword, String confirmPassword);

  /// 发送邮箱验证
  Future<ApiResponse<bool>> sendEmailVerification();

  /// 验证邮箱
  Future<ApiResponse<bool>> verifyEmail(String token);

  /// 检查用户名是否可用
  Future<ApiResponse<bool>> checkUsernameAvailability(String username);

  /// 检查邮箱是否可用
  Future<ApiResponse<bool>> checkEmailAvailability(String email);

  /// 获取验证码
  Future<ApiResponse<Map<String, dynamic>>> getCaptcha();

  /// 检查是否已登录
  Future<bool> isLoggedIn();

  /// 获取本地存储的用户信息
  Future<User?> getLocalUser();

  /// 清除本地认证数据
  Future<void> clearLocalAuth();
}

/// 认证仓库实现类
class AuthRepositoryImpl extends BaseRepository implements AuthRepository {
  static const String _userCacheKey = 'current_user';
  static const String _authCacheKey = 'auth_response';
  static const Duration _userCacheExpiry = Duration(hours: 1);
  static const Duration _authCacheExpiry = Duration(hours: 24);

  AuthRepositoryImpl({
    required RemoteDataSource remoteDataSource,
    required LocalDataSource localDataSource,
    required ConnectivityService connectivityService,
  }) : super(
          remoteDataSource: remoteDataSource,
          localDataSource: localDataSource,
          connectivityService: connectivityService,
        );

  @override
  Future<ApiResponse<AuthResponse>> login(LoginRequest request) async {
    try {
      // 使用后端实际的登录端点 /api/v1/auth/login
      // 后端期望 JSON 格式
      final loginData = {
        'username': request.identifier, // 使用identifier作为username
        'password': request.password,
      };
      
      final response = await remoteDataSource.post<Map<String, dynamic>>(
        '/api/v1/auth/login',
        body: loginData,
        fromJson: (data) => data as Map<String, dynamic>,
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.success && response.data != null) {
        final tokenData = response.data!;
        final accessToken = tokenData['access_token'] as String?;
        
        if (accessToken == null) {
          return ApiResponse<AuthResponse>.error(message: '登录响应格式错误');
        }
        
        // 设置认证Token以便后续请求使用
        remoteDataSource.setAuthToken(accessToken);
        
        // 获取用户信息 - 使用默认用户信息，因为后端token接口不返回用户详情
         final user = User(
           id: '1', // 临时ID，实际应该从其他接口获取
           username: request.identifier,
           email: request.identifier.contains('@') ? request.identifier : '${request.identifier}@example.com',
           role: 'teacher', // 默认角色
           createdAt: DateTime.now(),
           isActive: true,
           isVerified: true,
           permissions: ['read', 'write'],
         );
        
        // 构建 AuthResponse
        final authResponse = AuthResponse(
          user: user,
          accessToken: accessToken,
          refreshToken: '', // 后端暂不支持refresh token
          expiresAt: DateTime.now().add(Duration(hours: 24)), // 默认24小时过期
        );
        
        // 缓存认证信息
        await localDataSource.cacheData(_authCacheKey, authResponse.toJson());
        await localDataSource.cacheData(_userCacheKey, user.toJson());
        
        AppLogger.info('AuthRepository: 用户登录成功', {
          'username': user.username,
          'role': user.role,
        });
        
        return ApiResponse<AuthResponse>.success(
          data: authResponse,
          message: '登录成功',
        );
      } else {
        return ApiResponse<AuthResponse>.error(message: response.message ?? '登录失败');
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 用户登录失败', e, stackTrace);
      return ApiResponse.error(message: '登录失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<AuthResponse>> register(RegisterRequest request) async {
    try {
      // 使用后端实际的注册端点 /api/v1/auth/register
      final response = await remoteDataSource.post<Map<String, dynamic>>(
        '/api/v1/auth/register',
        body: {
           'username': request.username,
           'email': request.email,
           'password': request.password,
           'full_name': request.realName ?? request.username,
           'role': 'teacher', // 默认角色
         },
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        // 注册成功后需要登录获取token
        final loginRequest = LoginRequest(
          identifier: request.username,
          password: request.password,
        );
        
        // 调用登录方法获取完整的认证信息
        final loginResponse = await login(loginRequest);
        
        if (loginResponse.success && loginResponse.data != null) {
          AppLogger.info('AuthRepository: 用户注册并登录成功', {
            'username': loginResponse.data!.user.username,
            'role': loginResponse.data!.user.role,
          });
          
          return loginResponse;
        } else {
          return ApiResponse<AuthResponse>.error(message: '注册成功但登录失败，请手动登录');
        }
      } else {
        return ApiResponse<AuthResponse>.error(message: response.message ?? '注册失败');
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 用户注册失败', e, stackTrace);
      return ApiResponse<AuthResponse>.error(message: '注册失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> logout() async {
    try {
      final response = await remoteDataSource.post<Map<String, dynamic>>(
        '/api/v1/auth/logout',
        fromJson: (data) => data as Map<String, dynamic>,
      );

      // 无论远程登出是否成功，都清除本地认证数据
      await clearLocalAuth();
      
      AppLogger.info('AuthRepository: 用户登出成功');
      return response.transform<bool>((data) => true);
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 用户登出失败', e, stackTrace);
      
      // 即使远程登出失败，也清除本地数据
      await clearLocalAuth();
      return ApiResponse.success(data: true, message: '已清除本地登录状态');
    }
  }

  @override
  Future<ApiResponse<AuthResponse>> refreshToken() async {
    try {
      final response = await remoteDataSource.post<AuthResponse>(
        '/api/v1/auth/refresh',
        fromJson: (data) => AuthResponse.fromJson(data as Map<String, dynamic>),
      );

      if (response.success && response.data != null) {
        // 更新缓存的认证信息
        await localDataSource.cacheData(_authCacheKey, response.data!.toJson());
        await localDataSource.cacheData(_userCacheKey, response.data!.user.toJson());
        
        // 更新认证Token
        remoteDataSource.setAuthToken(response.data!.accessToken);
        
        AppLogger.info('AuthRepository: Token刷新成功', {
          'userId': response.data!.user.id,
        });
      }

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: Token刷新失败', e, stackTrace);
      return ApiResponse.error(message: 'Token刷新失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<User>> getCurrentUser({bool forceRefresh = false}) async {
    return fetchData<User>(
      remoteCall: () => _fetchUserFromRemote(),
      localCall: () => _fetchUserFromLocal(),
      cacheKey: _userCacheKey,
      forceRefresh: forceRefresh,
      cacheExpiry: _userCacheExpiry,
    );
  }

  @override
  Future<ApiResponse<User>> updateProfile(ProfileUpdateRequest request) async {
    try {
      final isConnected = connectivityService.isConnected;
      if (isConnected) {
        final response = await _updateProfileRemote(request);
        if (response.success) {
          // 清除用户缓存，强制下次获取最新数据
          clearCache(_userCacheKey);
        }
        return response;
      } else {
        // 离线时保存到本地待同步
        await localDataSource.markForSync(
          'update_profile_${DateTime.now().millisecondsSinceEpoch}',
          request.toJson(),
        );
        return ApiResponse.error(message: '网络不可用，已保存到本地待同步');
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 更新用户资料失败', e, stackTrace);
      return ApiResponse.error(message: '更新用户资料失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> updatePassword(PasswordUpdateRequest request) async {
    return syncToServer<PasswordUpdateRequest>(
      data: request,
      uploadCall: (data) => _updatePasswordRemote(data),
      syncKey: 'update_password_${DateTime.now().millisecondsSinceEpoch}',
    );
  }

  @override
  Future<ApiResponse<bool>> sendPasswordResetEmail(PasswordResetRequest request) async {
    try {
      final response = await remoteDataSource.post<Map<String, dynamic>>(
        '/api/v1/auth/password-reset/send',
        body: request.toJson(),
        fromJson: (data) => data as Map<String, dynamic>,
      );

      return response.transform<bool>((data) => response.success);
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 发送密码重置邮件失败', e, stackTrace);
      return ApiResponse.error(message: '发送密码重置邮件失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> resetPassword(String token, String newPassword, String confirmPassword) async {
    try {
      final response = await remoteDataSource.post<Map<String, dynamic>>(
        '/api/v1/auth/password-reset/confirm',
        body: {
          'token': token,
          'new_password': newPassword,
          'confirm_password': confirmPassword,
        },
        fromJson: (data) => data as Map<String, dynamic>,
      );

      return response.transform<bool>((data) => response.success);
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 重置密码失败', e, stackTrace);
      return ApiResponse.error(message: '重置密码失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> sendEmailVerification() async {
    try {
      final response = await remoteDataSource.post<Map<String, dynamic>>(
        '/api/v1/auth/email-verification/send',
        fromJson: (data) => data as Map<String, dynamic>,
      );

      return response.transform<bool>((data) => response.success);
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 发送邮箱验证失败', e, stackTrace);
      return ApiResponse.error(message: '发送邮箱验证失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> verifyEmail(String token) async {
    try {
      final response = await remoteDataSource.post<Map<String, dynamic>>(
        '/api/v1/auth/email-verification/confirm',
        body: {'token': token},
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success) {
        // 清除用户缓存，强制获取最新验证状态
        await clearCache(_userCacheKey);
      }

      return response.transform<bool>((data) => response.success);
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 邮箱验证失败', e, stackTrace);
      return ApiResponse.error(message: '邮箱验证失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> checkUsernameAvailability(String username) async {
    try {
      final response = await remoteDataSource.get<Map<String, dynamic>>(
        '/api/v1/auth/check-username',
        queryParameters: {'username': username},
        fromJson: (data) => data as Map<String, dynamic>,
      );

      return response.transform<bool>((data) => data?['available'] == true);
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 检查用户名可用性失败', e, stackTrace);
      return ApiResponse.error(message: '检查用户名可用性失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<bool>> checkEmailAvailability(String email) async {
    try {
      final response = await remoteDataSource.get<Map<String, dynamic>>(
        '/api/v1/auth/check-email',
        queryParameters: {'email': email},
        fromJson: (data) => data as Map<String, dynamic>,
      );

      return response.transform<bool>((data) => data?['available'] == true);
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 检查邮箱可用性失败', e, stackTrace);
      return ApiResponse.error(message: '检查邮箱可用性失败: ${e.toString()}');
    }
  }

  @override
  Future<ApiResponse<Map<String, dynamic>>> getCaptcha() async {
    try {
      final response = await remoteDataSource.get<Map<String, dynamic>>(
        '/api/v1/auth/captcha',
        fromJson: (data) => data as Map<String, dynamic>,
      );

      return response;
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 获取验证码失败', e, stackTrace);
      return ApiResponse.error(message: '获取验证码失败: ${e.toString()}');
    }
  }

  @override
  Future<bool> isLoggedIn() async {
    try {
      final authData = await localDataSource.getCachedData<Map<String, dynamic>>(_authCacheKey);
      if (authData != null) {
        final authResponse = AuthResponse.fromJson(authData);
        return !authResponse.isTokenExpired;
      }
      return false;
    } catch (e) {
      AppLogger.warning('AuthRepository: 检查登录状态失败', {'error': e.toString()});
      return false;
    }
  }

  @override
  Future<User?> getLocalUser() async {
    try {
      final userData = await localDataSource.getCachedData<Map<String, dynamic>>(_userCacheKey);
      if (userData != null) {
        return User.fromJson(userData);
      }
      return null;
    } catch (e) {
      AppLogger.warning('AuthRepository: 获取本地用户信息失败', {'error': e.toString()});
      return null;
    }
  }

  @override
  Future<void> clearLocalAuth() async {
    try {
      await clearCache(_authCacheKey);
      await clearCache(_userCacheKey);
      remoteDataSource.setAuthToken(null);
      AppLogger.info('AuthRepository: 本地认证数据已清除');
    } catch (e) {
      AppLogger.warning('AuthRepository: 清除本地认证数据失败', {'error': e.toString()});
    }
  }

  // 私有方法实现

  /// 从远程获取用户信息
  Future<ApiResponse<User>> _fetchUserFromRemote() async {
    return remoteDataSource.get<User>(
      '/api/v1/auth/me',
      fromJson: (data) => User.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 从本地获取用户信息
  Future<User?> _fetchUserFromLocal() async {
    final userData = await localDataSource.getCachedData<Map<String, dynamic>>(_userCacheKey);
    if (userData != null) {
      return User.fromJson(userData);
    }
    return null;
  }

  /// 远程更新用户资料
  Future<ApiResponse<User>> _updateProfileRemote(ProfileUpdateRequest request) async {
    final response = await remoteDataSource.put<User>(
      '/api/v1/auth/profile',
      body: request.toJson(),
      fromJson: (data) => User.fromJson(data as Map<String, dynamic>),
    );
    
    if (response.success && response.data != null) {
      // 更新本地用户缓存
      await localDataSource.cacheData(_userCacheKey, response.data!.toJson());
    }
    
    return response;
  }

  /// 远程更新密码
  Future<ApiResponse<bool>> _updatePasswordRemote(PasswordUpdateRequest request) async {
    final response = await remoteDataSource.put<Map<String, dynamic>>(
      '/api/v1/auth/password',
      body: request.toJson(),
      fromJson: (data) => data as Map<String, dynamic>,
    );
    return response.transform<bool>((data) => response.success);
  }

  @override
  Future<void> _syncSingleItem(Map<String, dynamic> item) async {
    final syncKey = item['syncKey'] as String;
    final data = item['data'];
    
    try {
      if (syncKey.startsWith('update_profile_')) {
        final request = ProfileUpdateRequest(
          realName: data['real_name'],
          phone: data['phone'],
          avatar: data['avatar'],
          school: data['school'],
          department: data['department'],
          title: data['title'],
          profile: data['profile'] as Map<String, dynamic>?,
        );
        await _updateProfileRemote(request);
      } else if (syncKey.startsWith('update_password_')) {
        final request = PasswordUpdateRequest(
          currentPassword: data['current_password'],
          newPassword: data['new_password'],
          confirmPassword: data['confirm_password'],
        );
        await _updatePasswordRemote(request);
      }
      
      // 同步成功，清除标记
      await localDataSource.clearSyncMark(syncKey);
      AppLogger.info('AuthRepository: 单项同步成功', {'syncKey': syncKey});
    } catch (e, stackTrace) {
      AppLogger.error('AuthRepository: 单项同步失败', e, stackTrace);
      rethrow;
    }
  }
}