import 'package:json_annotation/json_annotation.dart';

part 'auth_dto.g.dart';

/// 登录请求DTO
@JsonSerializable()
class LoginRequestDto {
  @JsonKey(name: 'username')
  final String username;
  
  @JsonKey(name: 'password')
  final String password;
  
  @JsonKey(name: 'remember_me')
  final bool rememberMe;
  
  @JsonKey(name: 'device_info')
  final DeviceInfoDto? deviceInfo;

  const LoginRequestDto({
    required this.username,
    required this.password,
    this.rememberMe = false,
    this.deviceInfo,
  });

  /// 从JSON创建登录请求
  factory LoginRequestDto.fromJson(Map<String, dynamic> json) => _$LoginRequestDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$LoginRequestDtoToJson(this);
}

/// 登录响应DTO
@JsonSerializable()
class LoginResponseDto {
  @JsonKey(name: 'access_token')
  final String accessToken;
  
  @JsonKey(name: 'refresh_token')
  final String refreshToken;
  
  @JsonKey(name: 'token_type')
  final String tokenType;
  
  @JsonKey(name: 'expires_in')
  final int expiresIn;
  
  @JsonKey(name: 'user')
  final Map<String, dynamic> user;
  
  @JsonKey(name: 'permissions')
  final List<String> permissions;
  
  @JsonKey(name: 'settings')
  final Map<String, dynamic>? settings;

  const LoginResponseDto({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
    required this.permissions,
    this.settings,
  });

  /// 从JSON创建登录响应
  factory LoginResponseDto.fromJson(Map<String, dynamic> json) => _$LoginResponseDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$LoginResponseDtoToJson(this);
}

/// 注册请求DTO
@JsonSerializable()
class RegisterRequestDto {
  @JsonKey(name: 'username')
  final String username;
  
  @JsonKey(name: 'email')
  final String email;
  
  @JsonKey(name: 'password')
  final String password;
  
  @JsonKey(name: 'confirm_password')
  final String confirmPassword;
  
  @JsonKey(name: 'full_name')
  final String fullName;
  
  @JsonKey(name: 'role')
  final String role;
  
  @JsonKey(name: 'phone')
  final String? phone;
  
  @JsonKey(name: 'school_code')
  final String? schoolCode;
  
  @JsonKey(name: 'invitation_code')
  final String? invitationCode;
  
  @JsonKey(name: 'device_info')
  final DeviceInfoDto? deviceInfo;

  const RegisterRequestDto({
    required this.username,
    required this.email,
    required this.password,
    required this.confirmPassword,
    required this.fullName,
    required this.role,
    this.phone,
    this.schoolCode,
    this.invitationCode,
    this.deviceInfo,
  });

  /// 从JSON创建注册请求
  factory RegisterRequestDto.fromJson(Map<String, dynamic> json) => _$RegisterRequestDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$RegisterRequestDtoToJson(this);
}

/// 注册响应DTO
@JsonSerializable()
class RegisterResponseDto {
  @JsonKey(name: 'user_id')
  final int userId;
  
  @JsonKey(name: 'username')
  final String username;
  
  @JsonKey(name: 'email')
  final String email;
  
  @JsonKey(name: 'message')
  final String message;
  
  @JsonKey(name: 'verification_required')
  final bool verificationRequired;
  
  @JsonKey(name: 'verification_method')
  final String? verificationMethod;

  const RegisterResponseDto({
    required this.userId,
    required this.username,
    required this.email,
    required this.message,
    required this.verificationRequired,
    this.verificationMethod,
  });

  /// 从JSON创建注册响应
  factory RegisterResponseDto.fromJson(Map<String, dynamic> json) => _$RegisterResponseDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$RegisterResponseDtoToJson(this);
}

/// 刷新令牌请求DTO
@JsonSerializable()
class RefreshTokenRequestDto {
  @JsonKey(name: 'refresh_token')
  final String refreshToken;
  
  @JsonKey(name: 'device_info')
  final DeviceInfoDto? deviceInfo;

  const RefreshTokenRequestDto({
    required this.refreshToken,
    this.deviceInfo,
  });

  /// 从JSON创建刷新令牌请求
  factory RefreshTokenRequestDto.fromJson(Map<String, dynamic> json) => _$RefreshTokenRequestDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$RefreshTokenRequestDtoToJson(this);
}

/// 刷新令牌响应DTO
@JsonSerializable()
class RefreshTokenResponseDto {
  @JsonKey(name: 'access_token')
  final String accessToken;
  
  @JsonKey(name: 'refresh_token')
  final String? refreshToken;
  
  @JsonKey(name: 'token_type')
  final String tokenType;
  
  @JsonKey(name: 'expires_in')
  final int expiresIn;

  const RefreshTokenResponseDto({
    required this.accessToken,
    this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
  });

  /// 从JSON创建刷新令牌响应
  factory RefreshTokenResponseDto.fromJson(Map<String, dynamic> json) => _$RefreshTokenResponseDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$RefreshTokenResponseDtoToJson(this);
}

/// 密码重置请求DTO
@JsonSerializable()
class PasswordResetRequestDto {
  @JsonKey(name: 'email')
  final String email;
  
  @JsonKey(name: 'username')
  final String? username;
  
  @JsonKey(name: 'captcha_token')
  final String? captchaToken;

  const PasswordResetRequestDto({
    required this.email,
    this.username,
    this.captchaToken,
  });

  /// 从JSON创建密码重置请求
  factory PasswordResetRequestDto.fromJson(Map<String, dynamic> json) => _$PasswordResetRequestDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$PasswordResetRequestDtoToJson(this);
}

/// 密码重置确认DTO
@JsonSerializable()
class PasswordResetConfirmDto {
  @JsonKey(name: 'token')
  final String token;
  
  @JsonKey(name: 'new_password')
  final String newPassword;
  
  @JsonKey(name: 'confirm_password')
  final String confirmPassword;

  const PasswordResetConfirmDto({
    required this.token,
    required this.newPassword,
    required this.confirmPassword,
  });

  /// 从JSON创建密码重置确认
  factory PasswordResetConfirmDto.fromJson(Map<String, dynamic> json) => _$PasswordResetConfirmDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$PasswordResetConfirmDtoToJson(this);
}

/// 设备信息DTO
@JsonSerializable()
class DeviceInfoDto {
  @JsonKey(name: 'device_id')
  final String deviceId;
  
  @JsonKey(name: 'device_name')
  final String deviceName;
  
  @JsonKey(name: 'platform')
  final String platform;
  
  @JsonKey(name: 'os_version')
  final String osVersion;
  
  @JsonKey(name: 'app_version')
  final String appVersion;
  
  @JsonKey(name: 'screen_resolution')
  final String? screenResolution;
  
  @JsonKey(name: 'timezone')
  final String? timezone;
  
  @JsonKey(name: 'locale')
  final String? locale;

  const DeviceInfoDto({
    required this.deviceId,
    required this.deviceName,
    required this.platform,
    required this.osVersion,
    required this.appVersion,
    this.screenResolution,
    this.timezone,
    this.locale,
  });

  /// 从JSON创建设备信息
  factory DeviceInfoDto.fromJson(Map<String, dynamic> json) => _$DeviceInfoDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$DeviceInfoDtoToJson(this);
}

/// 验证码验证DTO
@JsonSerializable()
class VerificationCodeDto {
  @JsonKey(name: 'code')
  final String code;
  
  @JsonKey(name: 'type')
  final VerificationType type;
  
  @JsonKey(name: 'identifier')
  final String identifier; // 邮箱或手机号
  
  @JsonKey(name: 'purpose')
  final VerificationPurpose purpose;

  const VerificationCodeDto({
    required this.code,
    required this.type,
    required this.identifier,
    required this.purpose,
  });

  /// 从JSON创建验证码验证
  factory VerificationCodeDto.fromJson(Map<String, dynamic> json) => _$VerificationCodeDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$VerificationCodeDtoToJson(this);
}

/// 验证类型枚举
@JsonEnum()
enum VerificationType {
  @JsonValue('email')
  email,
  
  @JsonValue('sms')
  sms,
  
  @JsonValue('voice')
  voice,
}

/// 验证目的枚举
@JsonEnum()
enum VerificationPurpose {
  @JsonValue('registration')
  registration,
  
  @JsonValue('password_reset')
  passwordReset,
  
  @JsonValue('login_verification')
  loginVerification,
  
  @JsonValue('email_change')
  emailChange,
  
  @JsonValue('phone_change')
  phoneChange,
}

/// 第三方登录DTO
@JsonSerializable()
class ThirdPartyLoginDto {
  @JsonKey(name: 'provider')
  final String provider; // 'wechat', 'qq', 'dingtalk', 'google', 'apple'
  
  @JsonKey(name: 'access_token')
  final String accessToken;
  
  @JsonKey(name: 'open_id')
  final String? openId;
  
  @JsonKey(name: 'union_id')
  final String? unionId;
  
  @JsonKey(name: 'user_info')
  final Map<String, dynamic>? userInfo;
  
  @JsonKey(name: 'device_info')
  final DeviceInfoDto? deviceInfo;

  const ThirdPartyLoginDto({
    required this.provider,
    required this.accessToken,
    this.openId,
    this.unionId,
    this.userInfo,
    this.deviceInfo,
  });

  /// 从JSON创建第三方登录
  factory ThirdPartyLoginDto.fromJson(Map<String, dynamic> json) => _$ThirdPartyLoginDtoFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$ThirdPartyLoginDtoToJson(this);
}