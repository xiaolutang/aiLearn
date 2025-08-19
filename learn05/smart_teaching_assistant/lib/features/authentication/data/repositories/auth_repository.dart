import 'package:connectivity_plus/connectivity_plus.dart';
import '../datasources/auth_datasource.dart';
import '../../models/auth_dto.dart';
import '../../models/user_model.dart';
import '../../../../core/storage/storage_service.dart';
import '../../../../core/network/network_info.dart';

/// 认证仓库接口
abstract class AuthRepository {
  /// 用户登录
  Future<LoginResponseDto> login(LoginRequestDto request);
  
  /// 用户注册
  Future<RegisterResponseDto> register(RegisterRequestDto request);
  
  /// 刷新访问令牌
  Future<RefreshTokenResponseDto> refreshToken(RefreshTokenRequestDto request);
  
  /// 用户登出
  Future<void> logout();
  
  /// 获取当前用户信息
  Future<UserModel> getCurrentUser();
  
  /// 更新用户信息
  Future<UserModel> updateUser(Map<String, dynamic> userData);
  
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
  Future<List<String>> getUserPermissions();
  
  /// 更新用户密码
  Future<void> updatePassword(String oldPassword, String newPassword);
  
  /// 检查登录状态
  Future<bool> isLoggedIn();
  
  /// 获取访问令牌
  Future<String?> getAccessToken();
  
  /// 获取刷新令牌
  Future<String?> getRefreshToken();
  
  /// 清除本地认证数据
  Future<void> clearAuthData();
}

/// 认证仓库实现
class AuthRepositoryImpl implements AuthRepository {
  final AuthDataSource _remoteDataSource;
  final AuthDataSource _localDataSource;
  final StorageService _storageService;
  final NetworkInfo _networkInfo;
  
  // 缓存键
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userDataKey = 'user_data';
  static const String _permissionsKey = 'user_permissions';
  static const String _loginTimeKey = 'login_time';
  
  AuthRepositoryImpl({
    required AuthDataSource remoteDataSource,
    required AuthDataSource localDataSource,
    required StorageService storageService,
    required NetworkInfo networkInfo,
  }) : _remoteDataSource = remoteDataSource,
       _localDataSource = localDataSource,
       _storageService = storageService,
       _networkInfo = networkInfo;

  @override
  Future<LoginResponseDto> login(LoginRequestDto request) async {
    try {
      LoginResponseDto response;
      
      if (await _networkInfo.isConnected) {
        // 网络可用，使用远程数据源
        response = await _remoteDataSource.login(request);
        
        // 缓存登录信息
        await _cacheAuthData(response);
      } else {
        // 网络不可用，使用本地数据源
        response = await _localDataSource.login(request);
        
        // 缓存本地登录信息
        await _cacheAuthData(response);
      }
      
      return response;
    } catch (e) {
      // 远程登录失败，尝试本地登录
      if (await _networkInfo.isConnected) {
        try {
          final response = await _localDataSource.login(request);
          await _cacheAuthData(response);
          return response;
        } catch (localError) {
          throw Exception('登录失败: $e');
        }
      } else {
        throw Exception('网络不可用且本地登录失败: $e');
      }
    }
  }

  @override
  Future<RegisterResponseDto> register(RegisterRequestDto request) async {
    try {
      if (await _networkInfo.isConnected) {
        return await _remoteDataSource.register(request);
      } else {
        // 注册通常需要网络连接，但可以提供离线模拟
        return await _localDataSource.register(request);
      }
    } catch (e) {
      // 远程注册失败，尝试本地注册（仅用于演示）
      if (await _networkInfo.isConnected) {
        return await _localDataSource.register(request);
      } else {
        throw Exception('注册失败: $e');
      }
    }
  }

  @override
  Future<RefreshTokenResponseDto> refreshToken(RefreshTokenRequestDto request) async {
    try {
      RefreshTokenResponseDto response;
      
      if (await _networkInfo.isConnected) {
        response = await _remoteDataSource.refreshToken(request);
        
        // 更新缓存的令牌
        await _storageService.setString(_accessTokenKey, response.accessToken);
        await _storageService.setString(_refreshTokenKey, response.refreshToken);
      } else {
        response = await _localDataSource.refreshToken(request);
        
        // 更新本地令牌缓存
        await _storageService.setString(_accessTokenKey, response.accessToken);
        await _storageService.setString(_refreshTokenKey, response.refreshToken);
      }
      
      return response;
    } catch (e) {
      // 刷新失败，尝试本地刷新
      if (await _networkInfo.isConnected) {
        try {
          final response = await _localDataSource.refreshToken(request);
          await _storageService.setString(_accessTokenKey, response.accessToken);
          await _storageService.setString(_refreshTokenKey, response.refreshToken);
          return response;
        } catch (localError) {
          throw Exception('令牌刷新失败: $e');
        }
      } else {
        throw Exception('网络不可用且本地令牌刷新失败: $e');
      }
    }
  }

  @override
  Future<void> logout() async {
    try {
      final accessToken = await getAccessToken();
      
      if (accessToken != null) {
        if (await _networkInfo.isConnected) {
          await _remoteDataSource.logout(accessToken);
        } else {
          await _localDataSource.logout(accessToken);
        }
      }
    } catch (e) {
      // 登出失败不应该阻止清除本地数据
      print('登出请求失败: $e');
    } finally {
      // 无论如何都要清除本地认证数据
      await clearAuthData();
    }
  }

  @override
  Future<UserModel> getCurrentUser() async {
    try {
      final accessToken = await getAccessToken();
      if (accessToken == null) {
        throw Exception('用户未登录');
      }
      
      UserModel user;
      
      if (await _networkInfo.isConnected) {
        user = await _remoteDataSource.getCurrentUser(accessToken);
        
        // 缓存用户数据
        await _storageService.setString(_userDataKey, user.toJson().toString());
      } else {
        // 尝试从缓存获取用户数据
        final cachedUserData = await _storageService.getString(_userDataKey);
        if (cachedUserData != null) {
          user = UserModel.fromJson(Map<String, dynamic>.from(
            Uri.splitQueryString(cachedUserData)
          ));
        } else {
          // 使用本地数据源
          user = await _localDataSource.getCurrentUser(accessToken);
        }
      }
      
      return user;
    } catch (e) {
      // 远程获取失败，尝试本地获取
      if (await _networkInfo.isConnected) {
        try {
          final accessToken = await getAccessToken();
          if (accessToken != null) {
            return await _localDataSource.getCurrentUser(accessToken);
          }
        } catch (localError) {
          throw Exception('获取用户信息失败: $e');
        }
      }
      throw Exception('获取用户信息失败: $e');
    }
  }

  @override
  Future<UserModel> updateUser(Map<String, dynamic> userData) async {
    try {
      final accessToken = await getAccessToken();
      if (accessToken == null) {
        throw Exception('用户未登录');
      }
      
      UserModel user;
      
      if (await _networkInfo.isConnected) {
        user = await _remoteDataSource.updateUser(accessToken, userData);
        
        // 更新缓存的用户数据
        await _storageService.setString(_userDataKey, user.toJson().toString());
      } else {
        user = await _localDataSource.updateUser(accessToken, userData);
        
        // 更新本地缓存
        await _storageService.setString(_userDataKey, user.toJson().toString());
      }
      
      return user;
    } catch (e) {
      // 远程更新失败，尝试本地更新
      if (await _networkInfo.isConnected) {
        try {
          final accessToken = await getAccessToken();
          if (accessToken != null) {
            final user = await _localDataSource.updateUser(accessToken, userData);
            await _storageService.setString(_userDataKey, user.toJson().toString());
            return user;
          }
        } catch (localError) {
          throw Exception('更新用户信息失败: $e');
        }
      }
      throw Exception('更新用户信息失败: $e');
    }
  }

  @override
  Future<void> sendPasswordResetEmail(PasswordResetRequestDto request) async {
    try {
      if (await _networkInfo.isConnected) {
        await _remoteDataSource.sendPasswordResetEmail(request);
      } else {
        await _localDataSource.sendPasswordResetEmail(request);
      }
    } catch (e) {
      // 远程发送失败，尝试本地模拟
      if (await _networkInfo.isConnected) {
        await _localDataSource.sendPasswordResetEmail(request);
      } else {
        throw Exception('发送密码重置邮件失败: $e');
      }
    }
  }

  @override
  Future<void> confirmPasswordReset(PasswordResetConfirmDto request) async {
    try {
      if (await _networkInfo.isConnected) {
        await _remoteDataSource.confirmPasswordReset(request);
      } else {
        await _localDataSource.confirmPasswordReset(request);
      }
    } catch (e) {
      // 远程确认失败，尝试本地模拟
      if (await _networkInfo.isConnected) {
        await _localDataSource.confirmPasswordReset(request);
      } else {
        throw Exception('密码重置失败: $e');
      }
    }
  }

  @override
  Future<void> sendVerificationCode(String identifier, VerificationType type, VerificationPurpose purpose) async {
    try {
      if (await _networkInfo.isConnected) {
        await _remoteDataSource.sendVerificationCode(identifier, type, purpose);
      } else {
        await _localDataSource.sendVerificationCode(identifier, type, purpose);
      }
    } catch (e) {
      // 远程发送失败，尝试本地模拟
      if (await _networkInfo.isConnected) {
        await _localDataSource.sendVerificationCode(identifier, type, purpose);
      } else {
        throw Exception('发送验证码失败: $e');
      }
    }
  }

  @override
  Future<bool> verifyCode(VerificationCodeDto request) async {
    try {
      if (await _networkInfo.isConnected) {
        return await _remoteDataSource.verifyCode(request);
      } else {
        return await _localDataSource.verifyCode(request);
      }
    } catch (e) {
      // 远程验证失败，尝试本地验证
      if (await _networkInfo.isConnected) {
        return await _localDataSource.verifyCode(request);
      } else {
        throw Exception('验证码验证失败: $e');
      }
    }
  }

  @override
  Future<LoginResponseDto> thirdPartyLogin(ThirdPartyLoginDto request) async {
    try {
      LoginResponseDto response;
      
      if (await _networkInfo.isConnected) {
        response = await _remoteDataSource.thirdPartyLogin(request);
        
        // 缓存登录信息
        await _cacheAuthData(response);
      } else {
        response = await _localDataSource.thirdPartyLogin(request);
        
        // 缓存本地登录信息
        await _cacheAuthData(response);
      }
      
      return response;
    } catch (e) {
      // 远程第三方登录失败，尝试本地模拟
      if (await _networkInfo.isConnected) {
        try {
          final response = await _localDataSource.thirdPartyLogin(request);
          await _cacheAuthData(response);
          return response;
        } catch (localError) {
          throw Exception('第三方登录失败: $e');
        }
      } else {
        throw Exception('网络不可用且第三方登录失败: $e');
      }
    }
  }

  @override
  Future<bool> checkUsernameAvailability(String username) async {
    try {
      if (await _networkInfo.isConnected) {
        return await _remoteDataSource.checkUsernameAvailability(username);
      } else {
        return await _localDataSource.checkUsernameAvailability(username);
      }
    } catch (e) {
      // 远程检查失败，尝试本地检查
      if (await _networkInfo.isConnected) {
        return await _localDataSource.checkUsernameAvailability(username);
      } else {
        throw Exception('检查用户名可用性失败: $e');
      }
    }
  }

  @override
  Future<bool> checkEmailAvailability(String email) async {
    try {
      if (await _networkInfo.isConnected) {
        return await _remoteDataSource.checkEmailAvailability(email);
      } else {
        return await _localDataSource.checkEmailAvailability(email);
      }
    } catch (e) {
      // 远程检查失败，尝试本地检查
      if (await _networkInfo.isConnected) {
        return await _localDataSource.checkEmailAvailability(email);
      } else {
        throw Exception('检查邮箱可用性失败: $e');
      }
    }
  }

  @override
  Future<List<String>> getUserPermissions() async {
    try {
      final accessToken = await getAccessToken();
      if (accessToken == null) {
        throw Exception('用户未登录');
      }
      
      List<String> permissions;
      
      if (await _networkInfo.isConnected) {
        permissions = await _remoteDataSource.getUserPermissions(accessToken);
        
        // 缓存权限数据
        await _storageService.setStringList(_permissionsKey, permissions);
      } else {
        // 尝试从缓存获取权限数据
        final cachedPermissions = await _storageService.getStringList(_permissionsKey);
        if (cachedPermissions != null && cachedPermissions.isNotEmpty) {
          permissions = cachedPermissions;
        } else {
          // 使用本地数据源
          permissions = await _localDataSource.getUserPermissions(accessToken);
        }
      }
      
      return permissions;
    } catch (e) {
      // 远程获取失败，尝试本地获取
      if (await _networkInfo.isConnected) {
        try {
          final accessToken = await getAccessToken();
          if (accessToken != null) {
            return await _localDataSource.getUserPermissions(accessToken);
          }
        } catch (localError) {
          throw Exception('获取用户权限失败: $e');
        }
      }
      throw Exception('获取用户权限失败: $e');
    }
  }

  @override
  Future<void> updatePassword(String oldPassword, String newPassword) async {
    try {
      final accessToken = await getAccessToken();
      if (accessToken == null) {
        throw Exception('用户未登录');
      }
      
      if (await _networkInfo.isConnected) {
        await _remoteDataSource.updatePassword(accessToken, oldPassword, newPassword);
      } else {
        await _localDataSource.updatePassword(accessToken, oldPassword, newPassword);
      }
    } catch (e) {
      // 远程更新失败，尝试本地更新
      if (await _networkInfo.isConnected) {
        try {
          final accessToken = await getAccessToken();
          if (accessToken != null) {
            await _localDataSource.updatePassword(accessToken, oldPassword, newPassword);
          }
        } catch (localError) {
          throw Exception('更新密码失败: $e');
        }
      } else {
        throw Exception('更新密码失败: $e');
      }
    }
  }

  @override
  Future<bool> isLoggedIn() async {
    try {
      final accessToken = await getAccessToken();
      final loginTime = await _storageService.getInt(_loginTimeKey);
      
      if (accessToken == null || loginTime == null) {
        return false;
      }
      
      // 检查令牌是否过期（假设令牌有效期为1小时）
      final now = DateTime.now().millisecondsSinceEpoch;
      final tokenAge = now - loginTime;
      const tokenValidDuration = 60 * 60 * 1000; // 1小时（毫秒）
      
      if (tokenAge > tokenValidDuration) {
        // 令牌可能已过期，尝试刷新
        final refreshToken = await getRefreshToken();
        if (refreshToken != null) {
          try {
            await this.refreshToken(RefreshTokenRequestDto(
              refreshToken: refreshToken,
            ));
            return true;
          } catch (e) {
            // 刷新失败，清除认证数据
            await clearAuthData();
            return false;
          }
        } else {
          await clearAuthData();
          return false;
        }
      }
      
      return true;
    } catch (e) {
      return false;
    }
  }

  @override
  Future<String?> getAccessToken() async {
    return await _storageService.getString(_accessTokenKey);
  }

  @override
  Future<String?> getRefreshToken() async {
    return await _storageService.getString(_refreshTokenKey);
  }

  @override
  Future<void> clearAuthData() async {
    await Future.wait<bool>([
      _storageService.remove(_accessTokenKey),
      _storageService.remove(_refreshTokenKey),
      _storageService.remove(_userDataKey),
      _storageService.remove(_permissionsKey),
      _storageService.remove(_loginTimeKey),
    ]);
  }

  /// 缓存认证数据
  Future<void> _cacheAuthData(LoginResponseDto response) async {
    await Future.wait<bool>([
      _storageService.setString(_accessTokenKey, response.accessToken),
      _storageService.setString(_refreshTokenKey, response.refreshToken),
      _storageService.setString(_userDataKey, response.user.toJson().toString()),
      _storageService.setStringList(_permissionsKey, response.permissions),
      _storageService.setInt(_loginTimeKey, DateTime.now().millisecondsSinceEpoch),
    ]);
  }
}