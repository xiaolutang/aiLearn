import '../models/user_model.dart';
import '../utils/api_client.dart';
import '../utils/constants.dart';
import '../utils/app_logger.dart';

/// 用户认证服务类
class AuthService {
  final ApiClient _apiClient = ApiClient();

  /// 用户登录
  Future<Map<String, dynamic>> login(String username, String password, {bool rememberMe = false}) async {
    AppLogger.info('AuthService: 开始登录请求', {'username': username});
    
    final loginRequest = LoginRequest(
      username: username.trim(),
      password: password,
      rememberMe: rememberMe,
    );

    try {
      final response = await _apiClient.post<Map<String, dynamic>>(
        '${ApiConstants.baseUrl}/api/v1/auth/login',
        data: loginRequest.toJson(),
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success) {
        AppLogger.info('AuthService: 登录API调用成功', {
          'username': username,
          'statusCode': response.code,
          'hasAccessToken': response.data?['access_token'] != null,
          'hasRefreshToken': response.data?['refresh_token'] != null,
          'hasUserData': response.data?['user'] != null,
        });
        
        // 保存Token
        if (response.data?['access_token'] != null) {
          await _apiClient.setTokens(
            response.data!['access_token'],
            response.data?['refresh_token'],
          );
          AppLogger.debug('AuthService: Token已保存到本地存储');
        }
        
        return {
          'success': true,
          'user': response.data?['user_info'],
          'token': response.data?['access_token'],
          'refresh_token': response.data?['refresh_token'],
          'message': response.message ?? '登录成功',
        };
      } else {
        AppLogger.warning('AuthService: 登录API调用失败', {
          'username': username,
          'statusCode': response.code,
          'message': response.message,
          'errors': response.data?['errors'],
        });
        
        return {
          'success': false,
          'message': response.message ?? '登录失败',
          'errors': response.data?['errors'],
        };
      }
    } catch (e, stackTrace) {
       AppLogger.error('AuthService: 登录请求异常 - username: $username', e, stackTrace);
       rethrow;
     }
  }

  /// 用户注册
  Future<Map<String, dynamic>> register(String name, String email, String password) async {
    AppLogger.info('AuthService: 开始注册请求', {'name': name, 'email': email});
    
    final registerRequest = RegisterRequest(
      name: name.trim(),
      email: email.trim(),
      password: password,
    );

    try {
      final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/auth/register',
        data: registerRequest.toJson(),
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success) {
        AppLogger.info('AuthService: 注册API调用成功', {
          'name': name,
          'email': email,
          'statusCode': response.code,
          'hasAccessToken': response.data?['access_token'] != null,
          'hasRefreshToken': response.data?['refresh_token'] != null,
          'hasUserData': response.data?['user'] != null,
        });
        
        // 保存Token
        if (response.data?['access_token'] != null) {
          await _apiClient.setTokens(
            response.data!['access_token'],
            response.data?['refresh_token'],
          );
          AppLogger.debug('AuthService: 注册后Token已保存到本地存储');
        }
        
        return {
          'success': true,
          'user': response.data?['user_info'],
          'token': response.data?['access_token'],
          'refresh_token': response.data?['refresh_token'],
          'message': response.message ?? '注册成功',
        };
      } else {
        AppLogger.warning('AuthService: 注册API调用失败', {
          'name': name,
          'email': email,
          'statusCode': response.code,
          'message': response.message,
          'errors': response.data?['errors'],
        });
        
        return {
          'success': false,
          'message': response.message ?? '注册失败',
          'errors': response.data?['errors'],
        };
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthService: 注册请求异常 - name: $name, email: $email', e, stackTrace);
      rethrow;
    }
  }

  /// 验证Token有效性
  Future<User?> validateToken(String token) async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/auth/me',
      headers: {
        'Authorization': 'Bearer $token',
      },
      fromJsonT: (json) => json as Map<String, dynamic>,
    );

    if (response.success && response.data?['user'] != null) {
      return User.fromJson(response.data!['user']);
    }
    return null;
  }

  /// 用户登出
  Future<Map<String, dynamic>> logout() async {
    AppLogger.info('AuthService: 开始登出请求');
    
    try {
      final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/auth/logout',
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      AppLogger.info('AuthService: 登出API调用完成', {
        'success': response.success,
        'statusCode': response.code,
        'message': response.message,
      });

      // 清除本地Token
      await _apiClient.clearTokens();
      AppLogger.debug('AuthService: 本地Token已清除');

      return {
        'success': response.success,
        'message': response.success ? '登出成功' : response.message ?? '登出失败',
      };
    } catch (e, stackTrace) {
      AppLogger.error('AuthService: 登出请求异常', e, stackTrace);
      // 即使API调用失败，也要清除本地Token
      await _apiClient.clearTokens();
      AppLogger.debug('AuthService: 登出异常后本地Token已清除');
      rethrow;
    }
  }

  /// 更新用户资料
  Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> userData) async {
    final response = await _apiClient.put<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/auth/profile',
      data: userData,
      fromJsonT: (json) => json as Map<String, dynamic>,
    );

    if (response.success) {
      return {
        'success': true,
        'user': response.data?['user'],
        'message': response.message ?? '更新成功',
      };
    } else {
      return {
        'success': false,
        'message': response.message ?? '更新失败',
        'errors': response.data?['errors'],
      };
    }
  }

  /// 修改密码
  Future<Map<String, dynamic>> changePassword(String oldPassword, String newPassword) async {
    final response = await _apiClient.put<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/auth/change-password',
      data: {
        'old_password': oldPassword,
        'new_password': newPassword,
      },
      fromJsonT: (json) => json as Map<String, dynamic>,
    );

    if (response.success) {
      return {
        'success': true,
        'message': response.message ?? '密码修改成功',
      };
    } else {
      return {
        'success': false,
        'message': response.message ?? '密码修改失败',
        'errors': response.data?['errors'],
      };
    }
  }

  /// 忘记密码
  Future<Map<String, dynamic>> forgotPassword(String email) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/auth/forgot-password',
      data: {'email': email.trim()},
      fromJsonT: (json) => json as Map<String, dynamic>,
    );

    if (response.success) {
      return {
        'success': true,
        'message': response.message ?? '重置密码邮件已发送',
      };
    } else {
      return {
        'success': false,
        'message': response.message ?? '发送失败',
        'errors': response.data?['errors'],
      };
    }
  }

  /// 重置密码
  Future<Map<String, dynamic>> resetPassword(String token, String newPassword) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/auth/reset-password',
      data: {
        'token': token,
        'password': newPassword,
      },
      fromJsonT: (json) => json as Map<String, dynamic>,
    );

    if (response.success) {
      return {
        'success': true,
        'message': response.message ?? '密码重置成功',
      };
    } else {
      return {
        'success': false,
        'message': response.message ?? '密码重置失败',
        'errors': response.data?['errors'],
      };
    }
  }

  /// 刷新Token
  Future<Map<String, dynamic>> refreshToken(String refreshToken) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/auth/refresh',
      data: {'refresh_token': refreshToken},
      fromJsonT: (json) => json as Map<String, dynamic>,
    );

    if (response.success) {
      // 保存新的Token
      if (response.data?['access_token'] != null) {
        await _apiClient.setTokens(
          response.data!['access_token'],
          response.data?['refresh_token'] ?? refreshToken,
        );
      }
      
      return {
        'success': true,
        'token': response.data?['access_token'],
        'refresh_token': response.data?['refresh_token'],
        'message': response.message ?? 'Token刷新成功',
      };
    } else {
      return {
        'success': false,
        'message': response.message ?? 'Token刷新失败',
      };
    }
  }
}