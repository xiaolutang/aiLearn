import 'package:dio/dio.dart';
import '../../models/auth_dto.dart';
import '../../models/user_model.dart';

/// 认证数据源抽象接口
abstract class AuthDataSource {
  /// 用户登录
  Future<LoginResponseDto> login(LoginRequestDto request);
  
  /// 用户注册
  Future<RegisterResponseDto> register(RegisterRequestDto request);
  
  /// 刷新访问令牌
  Future<RefreshTokenResponseDto> refreshToken(RefreshTokenRequestDto request);
  
  /// 用户登出
  Future<void> logout(String accessToken);
  
  /// 获取当前用户信息
  Future<UserModel> getCurrentUser(String accessToken);
  
  /// 更新用户信息
  Future<UserModel> updateUser(String accessToken, Map<String, dynamic> userData);
  
  /// 发送密码重置邮件
  Future<void> sendPasswordResetEmail(PasswordResetRequestDto request);
  
  /// 确认密码重置
  Future<void> confirmPasswordReset(PasswordResetConfirmDto request);
  
  /// 发送验证码
  Future<void> sendVerificationCode(String identifier, VerificationType type, VerificationPurpose purpose);
  
  /// 验证验证码
  Future<bool> verifyCode(VerificationCodeDto request);
  
  /// 第三方登录
  Future<LoginResponseDto> thirdPartyLogin(ThirdPartyLoginDto request);
  
  /// 检查用户名是否可用
  Future<bool> checkUsernameAvailability(String username);
  
  /// 检查邮箱是否可用
  Future<bool> checkEmailAvailability(String email);
  
  /// 获取用户权限列表
  Future<List<String>> getUserPermissions(String accessToken);
  
  /// 更新用户密码
  Future<void> updatePassword(String accessToken, String oldPassword, String newPassword);
}

/// 远程认证数据源实现
class RemoteAuthDataSource implements AuthDataSource {
  final Dio _dio;
  final String _baseUrl;

  RemoteAuthDataSource({
    required Dio dio,
    required String baseUrl,
  }) : _dio = dio, _baseUrl = baseUrl;

  @override
  Future<LoginResponseDto> login(LoginRequestDto request) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/api/v1/auth/login',
        data: request.toJson(),
      );
      
      return LoginResponseDto.fromJson(response.data);
    } catch (e) {
      throw _handleException(e, '登录失败');
    }
  }

  @override
  Future<RegisterResponseDto> register(RegisterRequestDto request) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/api/v1/auth/register',
        data: request.toJson(),
      );
      
      return RegisterResponseDto.fromJson(response.data);
    } catch (e) {
      throw _handleException(e, '注册失败');
    }
  }

  @override
  Future<RefreshTokenResponseDto> refreshToken(RefreshTokenRequestDto request) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/api/v1/auth/refresh',
        data: request.toJson(),
      );
      
      return RefreshTokenResponseDto.fromJson(response.data);
    } catch (e) {
      throw _handleException(e, '令牌刷新失败');
    }
  }

  @override
  Future<void> logout(String accessToken) async {
    try {
      await _dio.post(
        '$_baseUrl/api/v1/auth/logout',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );
    } catch (e) {
      throw _handleException(e, '登出失败');
    }
  }

  @override
  Future<UserModel> getCurrentUser(String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/api/v1/auth/me',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );
      
      return UserModel.fromJson(response.data);
    } catch (e) {
      throw _handleException(e, '获取用户信息失败');
    }
  }

  @override
  Future<UserModel> updateUser(String accessToken, Map<String, dynamic> userData) async {
    try {
      final response = await _dio.put(
        '$_baseUrl/api/v1/auth/me',
        data: userData,
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );
      
      return UserModel.fromJson(response.data);
    } catch (e) {
      throw _handleException(e, '更新用户信息失败');
    }
  }

  @override
  Future<void> sendPasswordResetEmail(PasswordResetRequestDto request) async {
    try {
      await _dio.post(
        '$_baseUrl/api/v1/auth/password-reset',
        data: request.toJson(),
      );
    } catch (e) {
      throw _handleException(e, '发送密码重置邮件失败');
    }
  }

  @override
  Future<void> confirmPasswordReset(PasswordResetConfirmDto request) async {
    try {
      await _dio.post(
        '$_baseUrl/api/v1/auth/password-reset/confirm',
        data: request.toJson(),
      );
    } catch (e) {
      throw _handleException(e, '密码重置失败');
    }
  }

  @override
  Future<void> sendVerificationCode(String identifier, VerificationType type, VerificationPurpose purpose) async {
    try {
      await _dio.post(
        '$_baseUrl/api/v1/auth/verification/send',
        data: {
          'identifier': identifier,
          'type': type.name,
          'purpose': purpose.name,
        },
      );
    } catch (e) {
      throw _handleException(e, '发送验证码失败');
    }
  }

  @override
  Future<bool> verifyCode(VerificationCodeDto request) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/api/v1/auth/verification/verify',
        data: request.toJson(),
      );
      
      return response.data['valid'] ?? false;
    } catch (e) {
      throw _handleException(e, '验证码验证失败');
    }
  }

  @override
  Future<LoginResponseDto> thirdPartyLogin(ThirdPartyLoginDto request) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/api/v1/auth/third-party/login',
        data: request.toJson(),
      );
      
      return LoginResponseDto.fromJson(response.data);
    } catch (e) {
      throw _handleException(e, '第三方登录失败');
    }
  }

  @override
  Future<bool> checkUsernameAvailability(String username) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/api/v1/auth/check/username',
        queryParameters: {'username': username},
      );
      
      return response.data['available'] ?? false;
    } catch (e) {
      throw _handleException(e, '检查用户名可用性失败');
    }
  }

  @override
  Future<bool> checkEmailAvailability(String email) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/api/v1/auth/check/email',
        queryParameters: {'email': email},
      );
      
      return response.data['available'] ?? false;
    } catch (e) {
      throw _handleException(e, '检查邮箱可用性失败');
    }
  }

  @override
  Future<List<String>> getUserPermissions(String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/api/v1/auth/permissions',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );
      
      final List<dynamic> permissions = response.data['permissions'] ?? [];
      return permissions.cast<String>();
    } catch (e) {
      throw _handleException(e, '获取用户权限失败');
    }
  }

  @override
  Future<void> updatePassword(String accessToken, String oldPassword, String newPassword) async {
    try {
      await _dio.put(
        '$_baseUrl/api/v1/auth/password',
        data: {
          'old_password': oldPassword,
          'new_password': newPassword,
        },
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );
    } catch (e) {
      throw _handleException(e, '更新密码失败');
    }
  }

  /// 统一异常处理
  Exception _handleException(dynamic error, String defaultMessage) {
    if (error is DioError) {
      switch (error.type) {
        case DioErrorType.connectTimeout:
          return Exception('连接超时，请检查网络连接');
        case DioErrorType.sendTimeout:
          return Exception('请求发送超时，请重试');
        case DioErrorType.receiveTimeout:
          return Exception('响应接收超时，请重试');
        case DioErrorType.response:
          final statusCode = error.response?.statusCode;
          final message = error.response?.data?['message'] ?? error.response?.data?['detail'];
          
          switch (statusCode) {
            case 400:
              return Exception(message ?? '请求参数错误');
            case 401:
              return Exception(message ?? '认证失败，请重新登录');
            case 403:
              return Exception(message ?? '权限不足');
            case 404:
              return Exception(message ?? '请求的资源不存在');
            case 422:
              return Exception(message ?? '数据验证失败');
            case 429:
              return Exception(message ?? '请求过于频繁，请稍后重试');
            case 500:
              return Exception(message ?? '服务器内部错误');
            case 502:
              return Exception(message ?? '网关错误');
            case 503:
              return Exception(message ?? '服务暂时不可用');
            default:
              return Exception(message ?? defaultMessage);
          }
        case DioErrorType.cancel:
          return Exception('请求已取消');
        case DioErrorType.other:
        default:
          return Exception(error.message ?? defaultMessage);
      }
    }
    
    return Exception('$defaultMessage: $error');
  }
}

/// 本地认证数据源实现（用于离线模式和默认数据）
class LocalAuthDataSource implements AuthDataSource {
  // 模拟的默认用户数据
  static const Map<String, dynamic> _defaultUser = {
    'id': 1,
    'username': 'demo_teacher',
    'email': 'teacher@example.com',
    'full_name': '演示教师',
    'role': 'teacher',
    'is_active': true,
    'created_at': '2024-01-01T00:00:00Z',
    'updated_at': '2024-01-01T00:00:00Z',
    'profile': {
      'school_name': '演示学校',
      'subject': '数学',
      'teacher_id': 'T001',
    },
  };

  static const Map<String, dynamic> _defaultLoginResponse = {
    'access_token': 'demo_access_token',
    'refresh_token': 'demo_refresh_token',
    'token_type': 'Bearer',
    'expires_in': 3600,
    'user': _defaultUser,
    'permissions': ['read:grades', 'write:grades', 'read:students', 'write:students'],
  };

  @override
  Future<LoginResponseDto> login(LoginRequestDto request) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 500));
    
    // 简单的用户名密码验证
    if (request.username == 'demo' && request.password == 'demo123') {
      return LoginResponseDto.fromJson(_defaultLoginResponse);
    } else {
      throw Exception('用户名或密码错误');
    }
  }

  @override
  Future<RegisterResponseDto> register(RegisterRequestDto request) async {
    await Future.delayed(const Duration(milliseconds: 500));
    
    return const RegisterResponseDto(
      userId: 1,
      username: 'demo_user',
      email: 'demo@example.com',
      message: '注册成功',
      verificationRequired: false,
    );
  }

  @override
  Future<RefreshTokenResponseDto> refreshToken(RefreshTokenRequestDto request) async {
    await Future.delayed(const Duration(milliseconds: 300));
    
    return const RefreshTokenResponseDto(
      accessToken: 'new_demo_access_token',
      refreshToken: 'new_demo_refresh_token',
      tokenType: 'Bearer',
      expiresIn: 3600,
    );
  }

  @override
  Future<void> logout(String accessToken) async {
    await Future.delayed(const Duration(milliseconds: 200));
    // 本地登出不需要实际操作
  }

  @override
  Future<UserModel> getCurrentUser(String accessToken) async {
    await Future.delayed(const Duration(milliseconds: 300));
    return UserModel.fromJson(_defaultUser);
  }

  @override
  Future<UserModel> updateUser(String accessToken, Map<String, dynamic> userData) async {
    await Future.delayed(const Duration(milliseconds: 400));
    
    final updatedUser = Map<String, dynamic>.from(_defaultUser);
    updatedUser.addAll(userData);
    
    return UserModel.fromJson(updatedUser);
  }

  @override
  Future<void> sendPasswordResetEmail(PasswordResetRequestDto request) async {
    await Future.delayed(const Duration(milliseconds: 500));
    // 模拟发送成功
  }

  @override
  Future<void> confirmPasswordReset(PasswordResetConfirmDto request) async {
    await Future.delayed(const Duration(milliseconds: 400));
    // 模拟重置成功
  }

  @override
  Future<void> sendVerificationCode(String identifier, VerificationType type, VerificationPurpose purpose) async {
    await Future.delayed(const Duration(milliseconds: 300));
    // 模拟发送成功
  }

  @override
  Future<bool> verifyCode(VerificationCodeDto request) async {
    await Future.delayed(const Duration(milliseconds: 300));
    // 模拟验证成功（验证码为 123456）
    return request.code == '123456';
  }

  @override
  Future<LoginResponseDto> thirdPartyLogin(ThirdPartyLoginDto request) async {
    await Future.delayed(const Duration(milliseconds: 600));
    return LoginResponseDto.fromJson(_defaultLoginResponse);
  }

  @override
  Future<bool> checkUsernameAvailability(String username) async {
    await Future.delayed(const Duration(milliseconds: 200));
    // 模拟用户名可用性检查
    return username != 'admin' && username != 'demo';
  }

  @override
  Future<bool> checkEmailAvailability(String email) async {
    await Future.delayed(const Duration(milliseconds: 200));
    // 模拟邮箱可用性检查
    return email != 'admin@example.com' && email != 'demo@example.com';
  }

  @override
  Future<List<String>> getUserPermissions(String accessToken) async {
    await Future.delayed(const Duration(milliseconds: 200));
    return const ['read:grades', 'write:grades', 'read:students', 'write:students'];
  }

  @override
  Future<void> updatePassword(String accessToken, String oldPassword, String newPassword) async {
    await Future.delayed(const Duration(milliseconds: 400));
    // 模拟密码更新成功
  }
}