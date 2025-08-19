import '../../../authentication/data/repositories/auth_repository.dart';
import '../../../authentication/models/auth_dto.dart';
import '../../../authentication/models/user_model.dart';

/// 登录用例
class LoginUseCase {
  final AuthRepository _repository;
  
  LoginUseCase(this._repository);
  
  Future<LoginResponseDto> call({
    required String username,
    required String password,
    String? deviceId,
    String? deviceName,
    bool rememberMe = false,
  }) async {
    final request = LoginRequestDto(
      username: username,
      password: password,
      deviceInfo: deviceId != null ? DeviceInfoDto(
        deviceId: deviceId,
        deviceName: deviceName ?? 'Unknown Device',
        platform: 'flutter',
        osVersion: '1.0.0',
        appVersion: '1.0.0',
      ) : null,
      rememberMe: rememberMe,
    );
    
    return await _repository.login(request);
  }
}

/// 注册用例
class RegisterUseCase {
  final AuthRepository _repository;
  
  RegisterUseCase(this._repository);
  
  Future<RegisterResponseDto> call({
    required String username,
    required String email,
    required String password,
    required String fullName,
    required UserRole role,
    Map<String, dynamic>? profile,
  }) async {
    final request = RegisterRequestDto(
      username: username,
      email: email,
      password: password,
      confirmPassword: password, // 确认密码与密码相同
      fullName: fullName,
      role: role.toString().split('.').last, // 将枚举转换为字符串
    );
    
    return await _repository.register(request);
  }
}

/// 登出用例
class LogoutUseCase {
  final AuthRepository _repository;
  
  LogoutUseCase(this._repository);
  
  Future<void> call() async {
    await _repository.logout();
  }
}

/// 获取当前用户用例
class GetCurrentUserUseCase {
  final AuthRepository _repository;
  
  GetCurrentUserUseCase(this._repository);
  
  Future<UserModel> call() async {
    return await _repository.getCurrentUser();
  }
}

/// 更新用户信息用例
class UpdateUserUseCase {
  final AuthRepository _repository;
  
  UpdateUserUseCase(this._repository);
  
  Future<UserModel> call({
    String? fullName,
    String? email,
    Map<String, dynamic>? profile,
  }) async {
    final userData = <String, dynamic>{};
    
    if (fullName != null) userData['full_name'] = fullName;
    if (email != null) userData['email'] = email;
    if (profile != null) userData['profile'] = profile;
    
    return await _repository.updateUser(userData);
  }
}

/// 刷新令牌用例
class RefreshTokenUseCase {
  final AuthRepository _repository;
  
  RefreshTokenUseCase(this._repository);
  
  Future<RefreshTokenResponseDto> call() async {
    final refreshToken = await _repository.getRefreshToken();
    if (refreshToken == null) {
      throw Exception('刷新令牌不存在');
    }
    
    final request = RefreshTokenRequestDto(refreshToken: refreshToken);
    return await _repository.refreshToken(request);
  }
}

/// 发送密码重置邮件用例
class SendPasswordResetEmailUseCase {
  final AuthRepository _repository;
  
  SendPasswordResetEmailUseCase(this._repository);
  
  Future<void> call(String email) async {
    final request = PasswordResetRequestDto(email: email);
    await _repository.sendPasswordResetEmail(request);
  }
}

/// 确认密码重置用例
class ConfirmPasswordResetUseCase {
  final AuthRepository _repository;
  
  ConfirmPasswordResetUseCase(this._repository);
  
  Future<void> call({
    required String token,
    required String newPassword,
  }) async {
    final request = PasswordResetConfirmDto(
      token: token,
      newPassword: newPassword,
      confirmPassword: newPassword, // 确认密码与新密码相同
    );
    await _repository.confirmPasswordReset(request);
  }
}

/// 发送验证码用例
class SendVerificationCodeUseCase {
  final AuthRepository _repository;
  
  SendVerificationCodeUseCase(this._repository);
  
  Future<void> call({
    required String identifier,
    required VerificationType type,
    required VerificationPurpose purpose,
  }) async {
    await _repository.sendVerificationCode(identifier, type, purpose);
  }
}

/// 验证验证码用例
class VerifyCodeUseCase {
  final AuthRepository _repository;
  
  VerifyCodeUseCase(this._repository);
  
  Future<bool> call({
    required String identifier,
    required String code,
    required VerificationType type,
    required VerificationPurpose purpose,
  }) async {
    final request = VerificationCodeDto(
      identifier: identifier,
      code: code,
      type: type,
      purpose: purpose,
    );
    return await _repository.verifyCode(request);
  }
}

/// 第三方登录用例
class ThirdPartyLoginUseCase {
  final AuthRepository _repository;
  
  ThirdPartyLoginUseCase(this._repository);
  
  Future<LoginResponseDto> call({
    required String provider,
    required String accessToken,
    String? openId,
    Map<String, dynamic>? userInfo,
  }) async {
    final request = ThirdPartyLoginDto(
      provider: provider,
      accessToken: accessToken,
      openId: openId,
      userInfo: userInfo,
    );
    return await _repository.thirdPartyLogin(request);
  }
}

/// 检查用户名可用性用例
class CheckUsernameAvailabilityUseCase {
  final AuthRepository _repository;
  
  CheckUsernameAvailabilityUseCase(this._repository);
  
  Future<bool> call(String username) async {
    // 基本验证
    if (username.isEmpty || username.length < 3) {
      return false;
    }
    
    // 检查用户名格式（只允许字母、数字、下划线）
    final usernameRegex = RegExp(r'^[a-zA-Z0-9_]+$');
    if (!usernameRegex.hasMatch(username)) {
      return false;
    }
    
    return await _repository.checkUsernameAvailability(username);
  }
}

/// 检查邮箱可用性用例
class CheckEmailAvailabilityUseCase {
  final AuthRepository _repository;
  
  CheckEmailAvailabilityUseCase(this._repository);
  
  Future<bool> call(String email) async {
    // 基本邮箱格式验证
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(email)) {
      return false;
    }
    
    return await _repository.checkEmailAvailability(email);
  }
}

/// 获取用户权限用例
class GetUserPermissionsUseCase {
  final AuthRepository _repository;
  
  GetUserPermissionsUseCase(this._repository);
  
  Future<List<String>> call() async {
    return await _repository.getUserPermissions();
  }
}

/// 更新密码用例
class UpdatePasswordUseCase {
  final AuthRepository _repository;
  
  UpdatePasswordUseCase(this._repository);
  
  Future<void> call({
    required String oldPassword,
    required String newPassword,
  }) async {
    // 密码强度验证
    if (!_isPasswordStrong(newPassword)) {
      throw Exception('密码强度不足，请使用至少8位字符，包含大小写字母、数字和特殊字符');
    }
    
    await _repository.updatePassword(oldPassword, newPassword);
  }
  
  /// 检查密码强度
  bool _isPasswordStrong(String password) {
    if (password.length < 8) return false;
    
    // 至少包含一个大写字母
    if (!password.contains(RegExp(r'[A-Z]'))) return false;
    
    // 至少包含一个小写字母
    if (!password.contains(RegExp(r'[a-z]'))) return false;
    
    // 至少包含一个数字
    if (!password.contains(RegExp(r'[0-9]'))) return false;
    
    // 至少包含一个特殊字符
    if (!password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) return false;
    
    return true;
  }
}

/// 检查登录状态用例
class CheckLoginStatusUseCase {
  final AuthRepository _repository;
  
  CheckLoginStatusUseCase(this._repository);
  
  Future<bool> call() async {
    return await _repository.isLoggedIn();
  }
}

/// 获取访问令牌用例
class GetAccessTokenUseCase {
  final AuthRepository _repository;
  
  GetAccessTokenUseCase(this._repository);
  
  Future<String?> call() async {
    return await _repository.getAccessToken();
  }
}

/// 清除认证数据用例
class ClearAuthDataUseCase {
  final AuthRepository _repository;
  
  ClearAuthDataUseCase(this._repository);
  
  Future<void> call() async {
    await _repository.clearAuthData();
  }
}

/// 认证用例集合（便于依赖注入）
class AuthUseCases {
  final LoginUseCase login;
  final RegisterUseCase register;
  final LogoutUseCase logout;
  final GetCurrentUserUseCase getCurrentUser;
  final UpdateUserUseCase updateUser;
  final RefreshTokenUseCase refreshToken;
  final SendPasswordResetEmailUseCase sendPasswordResetEmail;
  final ConfirmPasswordResetUseCase confirmPasswordReset;
  final SendVerificationCodeUseCase sendVerificationCode;
  final VerifyCodeUseCase verifyCode;
  final ThirdPartyLoginUseCase thirdPartyLogin;
  final CheckUsernameAvailabilityUseCase checkUsernameAvailability;
  final CheckEmailAvailabilityUseCase checkEmailAvailability;
  final GetUserPermissionsUseCase getUserPermissions;
  final UpdatePasswordUseCase updatePassword;
  final CheckLoginStatusUseCase checkLoginStatus;
  final GetAccessTokenUseCase getAccessToken;
  final ClearAuthDataUseCase clearAuthData;
  
  AuthUseCases(AuthRepository repository)
    : login = LoginUseCase(repository),
      register = RegisterUseCase(repository),
      logout = LogoutUseCase(repository),
      getCurrentUser = GetCurrentUserUseCase(repository),
      updateUser = UpdateUserUseCase(repository),
      refreshToken = RefreshTokenUseCase(repository),
      sendPasswordResetEmail = SendPasswordResetEmailUseCase(repository),
      confirmPasswordReset = ConfirmPasswordResetUseCase(repository),
      sendVerificationCode = SendVerificationCodeUseCase(repository),
      verifyCode = VerifyCodeUseCase(repository),
      thirdPartyLogin = ThirdPartyLoginUseCase(repository),
      checkUsernameAvailability = CheckUsernameAvailabilityUseCase(repository),
      checkEmailAvailability = CheckEmailAvailabilityUseCase(repository),
      getUserPermissions = GetUserPermissionsUseCase(repository),
      updatePassword = UpdatePasswordUseCase(repository),
      checkLoginStatus = CheckLoginStatusUseCase(repository),
      getAccessToken = GetAccessTokenUseCase(repository),
      clearAuthData = ClearAuthDataUseCase(repository);
}